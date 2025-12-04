# REST API Ingester Test Suite

Comprehensive test suite covering all pagination types and edge cases using real public APIs.

## Test Coverage

### 1. No Pagination (`TestNoPagination`)
- **Single resource**: `https://jsonplaceholder.typicode.com/posts/1`
- **Multiple resources**: `https://jsonplaceholder.typicode.com/posts`

### 2. Offset/Limit Pagination (`TestOffsetLimitPagination`)
- **JSONPlaceholder**: `https://jsonplaceholder.typicode.com/posts?_start=0&_limit=10`
- **PokeAPI**: `https://pokeapi.co/api/v2/pokemon?offset=20&limit=20`
- Tests with `max_pages` and `max_records` limits

### 3. Page Number Pagination (`TestPageNumberPagination`)
- **GitHub repos**: `https://api.github.com/users/octocat/repos?page=1&per_page=10`
- **GitHub search**: `https://api.github.com/search/repositories?q=javascript&per_page=10&page=2`
- **Open Library**: `https://openlibrary.org/search.json?q=javascript&page=1`

### 4. Link Header Pagination (`TestLinkHeaderPagination`)
- **GitHub**: Uses RFC 5988 Link headers for pagination
- Parses `Link` header to find next page

### 5. Next URL Pagination (`TestNextUrlPagination`)
- **PokeAPI**: Response includes `"next": "url"` field
- Handles both absolute and relative URLs

### 6. Cursor Pagination (`TestCursorPagination`)
- Configuration example provided
- Most cursor APIs require authentication (test skipped)

### 7. Edge Cases (`TestEdgeCases`)
- Empty result sets
- Single page results
- Custom headers

### 8. Batch Saving (`TestBatchSaving`)
- Multiple output files
- Configurable batch size

### 9. Data Extraction (`TestDataExtraction`)
- Nested data paths (`items`, `results`, `docs`)
- Root-level arrays
- Root-level objects

## Running Tests

### Run all tests:
```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_rest
pytest test/test_pagination_types.py -v
```

### Run specific test class:
```bash
pytest test/test_pagination_types.py::TestOffsetLimitPagination -v
```

### Run specific test:
```bash
pytest test/test_pagination_types.py::TestPageNumberPagination::test_github_page_number -v
```

### Run with output:
```bash
pytest test/test_pagination_types.py -v -s
```

### Run with coverage:
```bash
pytest test/test_pagination_types.py --cov=elt_ingest_rest --cov-report=html
```

## Test Output

All test output files are saved to `./output/test/` with subdirectories:
- `no_pagination/`
- `offset_limit/`
- `page_number/`
- `link_header/`
- `next_url/`
- `cursor/`
- `edge_cases/`
- `batch_save/`
- `data_extraction/`

## API Rate Limits

Some tests use public APIs with rate limits:

- **GitHub API**: 60 requests/hour (unauthenticated)
  - To increase: Add authentication token in headers
- **PokeAPI**: No rate limit but fair use policy
- **JSONPlaceholder**: No rate limit
- **Open Library**: Rate limited, but generous

## Adding New Tests

To add tests for a new API:

1. Identify the pagination type
2. Create a new test method in the appropriate test class
3. Configure `IngestConfig` and `PaginationConfig`
4. Assert expected results

Example:
```python
def test_new_api(self):
    """Test description."""
    config = IngestConfig(
        base_url="https://api.example.com",
        endpoint="/data",
        pagination=PaginationConfig(
            type=PaginationType.OFFSET_LIMIT,
            page_size=10,
            offset_param="offset",
            limit_param="limit",
            data_path="results",
            max_pages=2,
        ),
        output_dir=Path("./output/test/offset_limit"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()

    assert len(data) > 0
    assert output_path.exists()
```

## Dependencies

```bash
pip install pytest
pip install pytest-cov  # For coverage reports
```

## Notes

- Tests use real public APIs - require internet connection
- Some tests are skipped if they require authentication
- Tests are designed to be non-destructive (read-only)
- Rate limiting may cause intermittent failures
