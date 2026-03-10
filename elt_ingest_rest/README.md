# ELT Ingest REST

A flexible Python library for ingesting data from REST APIs with support for various pagination strategies and automatic saving to disk.

See:

- [ARCHITECTURE.md](file:///Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_rest/ARCHITECTURE.md)
- [SOLUTION_OVERVIEW.md](file:///Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_rest/SOLUTION_OVERVIEW.md)

## Features

- **Multiple Pagination Types Supported:**
  - No pagination (single request)
  - Offset/Limit pagination
  - Page number pagination
  - Cursor-based pagination
  - Next URL pagination
  - Link header pagination (RFC 5988)

- **Flexible Configuration:**
  - Custom headers and authentication
  - Query parameters support
  - GET/POST/PUT/PATCH/DELETE methods
  - Request timeout and retry configuration
  - SSL verification control

- **Data Extraction:**
  - JSONPath-like nested data extraction
  - Configurable data path in response
  - Custom stop conditions

- **Output Options:**
  - Save as single JSON file
  - Save in batches (multiple files)
  - Custom output directory and filename
  - Pretty-printed JSON output

- **Robust Error Handling:**
  - Automatic retry with exponential backoff
  - Configurable retry status codes
  - Session management with connection pooling

## Installation

```bash
uv pip install -e .
```

## Quick Start

### Run From Config (Recommended)

Configs live under `config/ingest/`.

```bash
uv run --project . python examples/run_from_json.py config/ingest/pokeapi_offset.json -v
```

### Non-Paginated API

```python
from pathlib import Path
from elt_ingest_rest import IngestConfig, PaginationConfig, PaginationType, RestApiIngester

config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/users/123",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    pagination=PaginationConfig(type=PaginationType.NONE),
    output_dir=Path("./output"),
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
print(f"Saved {len(data)} records to {output_path}")
```

### Offset/Limit Pagination

```python
config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/api/v1/products",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    pagination=PaginationConfig(
        type=PaginationType.OFFSET_LIMIT,
        page_size=100,
        offset_param="offset",
        limit_param="limit",
        data_path="results",  # Extract from response.results
        max_records=1000,  # Limit to 1000 records
    ),
    output_dir=Path("./output/products"),
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
```

### Page Number Pagination

```python
config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/api/v1/users",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    pagination=PaginationConfig(
        type=PaginationType.PAGE_NUMBER,
        page_size=50,
        page_param="page",
        page_size_param="per_page",
        data_path="data",
        max_pages=10,  # Limit to 10 pages
    ),
    output_dir=Path("./output/users"),
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
```

### Cursor-Based Pagination

```python
config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/api/v1/events",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    pagination=PaginationConfig(
        type=PaginationType.CURSOR,
        page_size=100,
        cursor_param="cursor",
        cursor_path="pagination.next_cursor",  # Nested path
        data_path="data",
    ),
    output_dir=Path("./output/events"),
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
```

### Next URL Pagination

```python
config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/api/orders",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    pagination=PaginationConfig(
        type=PaginationType.NEXT_URL,
        next_url_path="next",  # Response: {"data": [...], "next": "url"}
        data_path="data",
    ),
    output_dir=Path("./output/orders"),
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
```

### Link Header Pagination

```python
config = IngestConfig(
    base_url="https://api.github.com",
    endpoint="/users/octocat/repos",
    headers={"Accept": "application/vnd.github.v3+json"},
    pagination=PaginationConfig(
        type=PaginationType.LINK_HEADER,
        link_header_name="Link",
        data_path="",  # Data at root level
    ),
    output_dir=Path("./output/repos"),
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
```

## Advanced Usage

### Batch Saving

Save data in multiple files:

```python
config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/api/v1/transactions",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    pagination=PaginationConfig(
        type=PaginationType.PAGE_NUMBER,
        page_size=500,
        data_path="transactions",
    ),
    output_dir=Path("./output/transactions"),
    save_mode="batch",  # Save in batches
    batch_size=1000,  # 1000 records per file
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
```

### Custom Stop Condition

```python
def stop_when_date_reached(response: dict) -> bool:
    """Stop if we've reached data before 2024."""
    data = response.get("data", [])
    if not data:
        return False
    last_record = data[-1]
    return last_record.get("year", 9999) < 2024

config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/api/v1/historical_data",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    pagination=PaginationConfig(
        type=PaginationType.PAGE_NUMBER,
        page_size=100,
        data_path="data",
        stop_condition=stop_when_date_reached,
    ),
    output_dir=Path("./output/historical"),
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
```

### POST Requests

```python
config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/api/v1/query",
    method="POST",
    headers={
        "Authorization": "Bearer YOUR_TOKEN",
        "Content-Type": "application/json",
    },
    body={
        "query": "SELECT * FROM users WHERE active = true",
        "format": "json",
    },
    pagination=PaginationConfig(
        type=PaginationType.NONE,
        data_path="results",
    ),
    output_dir=Path("./output/query_results"),
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
```

### Basic Authentication

```python
config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/api/v1/protected/data",
    auth=("username", "password"),  # Basic auth
    pagination=PaginationConfig(type=PaginationType.NONE),
    output_dir=Path("./output/protected"),
)

ingester = RestApiIngester(config)
data, output_path = ingester.ingest()
```

## License

MIT
