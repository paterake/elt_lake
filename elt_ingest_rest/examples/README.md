# JSON Configuration Examples

This directory contains example JSON configuration files for the REST API Ingester.

## Benefits of JSON Configuration

✅ **Separation of Concerns**: Configuration separate from code
✅ **Version Control**: Track API configurations in git
✅ **Portability**: Easy to share and deploy
✅ **No Code Changes**: Modify API settings without changing Python code
✅ **CI/CD Friendly**: Load different configs for dev/staging/prod

---

## Quick Start

### 1. Using Python Code

```python
from pathlib import Path
from elt_ingest_rest import IngestConfigJson, RestApiIngester

# Load configuration from JSON file
config = IngestConfigJson.from_json(Path("examples/github_repos.json"))

# Run ingestion
ingester = RestApiIngester(config)
data, output_path = ingester.ingest()

print(f"Fetched {len(data)} records, saved to {output_path}")
```

### 2. Using CLI Script

```bash
# Run ingestion from JSON config
python examples/run_from_json.py examples/github_repos.json

# With verbose logging
python examples/run_from_json.py examples/pokeapi_offset.json --verbose
```

---

## Example Configuration Files

### 1. [github_repos.json](github_repos.json) - Page Number Pagination

Fetches GitHub user repositories using page-based pagination.

```json
{
  "base_url": "https://api.github.com",
  "endpoint": "/users/octocat/repos",
  "pagination": {
    "type": "page_number",
    "page_size": 30,
    "page_param": "page",
    "page_size_param": "per_page"
  }
}
```

**Run it:**
```bash
python examples/run_from_json.py examples/github_repos.json
```

---

### 2. [pokeapi_offset.json](pokeapi_offset.json) - Offset/Limit Pagination

Fetches Pokemon data using offset/limit pagination, limited to 5 pages.

```json
{
  "base_url": "https://pokeapi.co",
  "endpoint": "/api/v2/pokemon",
  "pagination": {
    "type": "offset_limit",
    "page_size": 20,
    "offset_param": "offset",
    "limit_param": "limit",
    "data_path": "results",
    "max_pages": 5
  }
}
```

**Run it:**
```bash
python examples/run_from_json.py examples/pokeapi_offset.json
```

---

### 3. [jsonplaceholder_posts.json](jsonplaceholder_posts.json) - Batch Save Mode

Fetches posts with batch saving (multiple output files).

```json
{
  "base_url": "https://jsonplaceholder.typicode.com",
  "endpoint": "/posts",
  "pagination": {
    "type": "offset_limit",
    "offset_param": "_start",
    "limit_param": "_limit",
    "max_pages": 3
  },
  "save_mode": "batch",
  "batch_size": 15
}
```

**Run it:**
```bash
python examples/run_from_json.py examples/jsonplaceholder_posts.json
```

---

## JSON Configuration Reference

### Complete Configuration Structure

```json
{
  "base_url": "https://api.example.com",
  "endpoint": "/api/v1/data",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
  },
  "params": {
    "filter": "active",
    "sort": "created_at"
  },
  "body": null,
  "auth": ["username", "password"],
  "timeout": 30,
  "verify_ssl": true,
  "pagination": {
    "type": "page_number",
    "page_size": 100,
    "offset_param": "offset",
    "limit_param": "limit",
    "page_param": "page",
    "page_size_param": "per_page",
    "cursor_param": "cursor",
    "cursor_path": "next_cursor",
    "next_url_path": "next",
    "link_header_name": "Link",
    "data_path": "data",
    "max_pages": 10,
    "max_records": 1000
  },
  "output_dir": "./output/data",
  "output_filename": "custom_name.json",
  "save_mode": "single",
  "batch_size": 1000,
  "max_retries": 3,
  "backoff_factor": 0.3,
  "retry_status_codes": [429, 500, 502, 503, 504]
}
```

---

## Field Descriptions

### Core Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `base_url` | string | **Yes** | - | Base URL of the API |
| `endpoint` | string | No | `""` | API endpoint path |
| `method` | string | No | `"GET"` | HTTP method (GET, POST, PUT, etc.) |
| `headers` | object | No | `{}` | HTTP headers |
| `params` | object | No | `{}` | Query parameters |
| `body` | object | No | `null` | Request body (for POST/PUT) |
| `auth` | array | No | `null` | Basic auth `["username", "password"]` |
| `timeout` | number | No | `30` | Request timeout in seconds |
| `verify_ssl` | boolean | No | `true` | Verify SSL certificates |

### Pagination Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `type` | string | No | `"none"` | Pagination type: `none`, `offset_limit`, `page_number`, `cursor`, `link_header`, `next_url` |
| `page_size` | number | No | `100` | Records per page |
| `offset_param` | string | No | `"offset"` | Offset parameter name |
| `limit_param` | string | No | `"limit"` | Limit parameter name |
| `page_param` | string | No | `"page"` | Page number parameter name |
| `page_size_param` | string | No | `"per_page"` | Page size parameter name |
| `cursor_param` | string | No | `"cursor"` | Cursor parameter name |
| `cursor_path` | string | No | `"next_cursor"` | JSON path to extract cursor |
| `next_url_path` | string | No | `"next"` | JSON path to extract next URL |
| `link_header_name` | string | No | `"Link"` | Link header name |
| `data_path` | string | No | `"data"` | JSON path to data array (empty for root) |
| `max_pages` | number | No | `0` | Maximum pages (0 = unlimited) |
| `max_records` | number | No | `0` | Maximum records (0 = unlimited) |

### Output Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `output_dir` | string | No | `"./output"` | Output directory path |
| `output_filename` | string | No | `null` | Custom output filename |
| `save_mode` | string | No | `"single"` | Save mode: `single` or `batch` |
| `batch_size` | number | No | `1000` | Records per batch file |

### Retry Configuration

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `max_retries` | number | No | `3` | Maximum retry attempts |
| `backoff_factor` | number | No | `0.3` | Exponential backoff factor |
| `retry_status_codes` | array | No | `[429, 500, 502, 503, 504]` | HTTP codes to retry |

---

## Pagination Type Examples

### No Pagination
```json
{
  "base_url": "https://api.example.com",
  "endpoint": "/users/123",
  "pagination": {
    "type": "none"
  }
}
```

### Offset/Limit
```json
{
  "pagination": {
    "type": "offset_limit",
    "page_size": 100,
    "offset_param": "offset",
    "limit_param": "limit",
    "data_path": "results"
  }
}
```

### Page Number
```json
{
  "pagination": {
    "type": "page_number",
    "page_size": 50,
    "page_param": "page",
    "page_size_param": "per_page",
    "data_path": "items"
  }
}
```

### Cursor-Based
```json
{
  "pagination": {
    "type": "cursor",
    "cursor_param": "cursor",
    "cursor_path": "pagination.next_cursor",
    "data_path": "data"
  }
}
```

### Link Header
```json
{
  "pagination": {
    "type": "link_header",
    "link_header_name": "Link",
    "data_path": ""
  }
}
```

### Next URL
```json
{
  "pagination": {
    "type": "next_url",
    "next_url_path": "next",
    "data_path": "results"
  }
}
```

---

## Creating Your Own Configuration

### 1. Start with a Template

Copy an existing example:
```bash
cp examples/github_repos.json my_api_config.json
```

### 2. Modify for Your API

Edit the JSON file:
```json
{
  "base_url": "https://your-api.com",
  "endpoint": "/api/v1/your-endpoint",
  "headers": {
    "Authorization": "Bearer YOUR_API_TOKEN"
  },
  "pagination": {
    "type": "page_number",
    "page_size": 100,
    "data_path": "data.results"
  },
  "output_dir": "./output/your_data"
}
```

### 3. Test Your Configuration

```bash
python examples/run_from_json.py my_api_config.json --verbose
```

---

## Exporting Configuration from Code

You can also generate JSON configs from Python code:

```python
from pathlib import Path
from elt_ingest_rest import IngestConfig, IngestConfigJson, PaginationConfig, PaginationType

# Create config in Python
config = IngestConfig(
    base_url="https://api.example.com",
    endpoint="/data",
    pagination=PaginationConfig(
        type=PaginationType.PAGE_NUMBER,
        page_size=50,
    )
)

# Export to JSON file
IngestConfigJson.to_json(config, Path("my_config.json"))

# Or get JSON string
json_str = IngestConfigJson.to_json(config)
print(json_str)
```

---

## Loading from Different Sources

### From File
```python
config = IngestConfigJson.from_json(Path("config.json"))
```

### From JSON String
```python
json_str = '{"base_url": "https://api.example.com"}'
config = IngestConfigJson.from_json(json_str)
```

### From Dict
```python
config_dict = {"base_url": "https://api.example.com"}
config = IngestConfigJson.from_json(config_dict)
```

---

## Environment Variables

For sensitive data like API tokens, use environment variables:

**config.json:**
```json
{
  "base_url": "https://api.example.com",
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

**Python code:**
```python
import os
import json
from pathlib import Path
from elt_ingest_rest import IngestConfig

# Load JSON
with open("config.json") as f:
    config_data = json.load(f)

# Replace environment variables
config_data["headers"]["Authorization"] = f"Bearer {os.getenv('API_TOKEN')}"

# Create config
config = IngestConfigJson.from_json(config_data)
```

---

## Best Practices

1. **Version Control**: Store JSON configs in git (exclude sensitive data)
2. **Sensitive Data**: Use environment variables for tokens/passwords
3. **Validation**: Test configs with `--verbose` flag first
4. **Documentation**: Add comments in a separate README
5. **Organization**: Group configs by API or project
6. **Naming**: Use descriptive filenames: `github_repos.json`, `api_users_prod.json`

---

## Troubleshooting

### Config file not found
```bash
Error: Config file not found: config.json
```
**Solution**: Check the file path is correct

### Invalid JSON syntax
```bash
Error: Expecting property name enclosed in double quotes
```
**Solution**: Validate JSON at [jsonlint.com](https://jsonlint.com/)

### Invalid pagination type
```bash
Error: 'invalid_type' is not a valid PaginationType
```
**Solution**: Use one of: `none`, `offset_limit`, `page_number`, `cursor`, `link_header`, `next_url`

---

## See Also

- [Main README](../README.md) - Project documentation
- [Test Examples](../test/test_json_config.py) - JSON config tests
- [Usage Examples](../test/usage_examples.py) - Python code examples
