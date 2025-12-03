# ELT Ingest REST

A flexible Python library for ingesting data from REST APIs with support for various pagination strategies and automatic saving to disk.

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
# Install dependencies
uv pip install -e .
```

## Quick Start

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

## Configuration Reference

### IngestConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | str | Required | Base URL of the API |
| `endpoint` | str | `""` | API endpoint path |
| `method` | str | `"GET"` | HTTP method |
| `headers` | dict | `{}` | Request headers |
| `params` | dict | `{}` | Query parameters |
| `body` | dict | `None` | Request body (for POST/PUT) |
| `auth` | tuple | `None` | Basic auth credentials |
| `timeout` | int | `30` | Request timeout in seconds |
| `verify_ssl` | bool | `True` | Verify SSL certificates |
| `pagination` | PaginationConfig | `PaginationConfig()` | Pagination settings |
| `output_dir` | Path | `./output` | Output directory |
| `output_filename` | str | `None` | Custom output filename |
| `save_mode` | str | `"single"` | Save mode: "single" or "batch" |
| `batch_size` | int | `1000` | Records per batch file |
| `max_retries` | int | `3` | Maximum retry attempts |
| `backoff_factor` | float | `0.3` | Retry backoff factor |
| `retry_status_codes` | list | `[429, 500, 502, 503, 504]` | Status codes to retry |

### PaginationConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | PaginationType | `NONE` | Pagination type |
| `page_size` | int | `100` | Records per page |
| `offset_param` | str | `"offset"` | Offset parameter name |
| `limit_param` | str | `"limit"` | Limit parameter name |
| `page_param` | str | `"page"` | Page number parameter |
| `page_size_param` | str | `"per_page"` | Page size parameter |
| `cursor_param` | str | `"cursor"` | Cursor parameter name |
| `cursor_path` | str | `"next_cursor"` | Path to cursor in response |
| `next_url_path` | str | `"next"` | Path to next URL in response |
| `link_header_name` | str | `"Link"` | Link header name |
| `data_path` | str | `"data"` | Path to data array in response |
| `max_pages` | int | `0` | Maximum pages (0 = unlimited) |
| `max_records` | int | `0` | Maximum records (0 = unlimited) |
| `stop_condition` | Callable | `None` | Custom stop condition function |

## Examples

See [examples/usage_examples.py](examples/usage_examples.py) for comprehensive examples.

## License

MIT
