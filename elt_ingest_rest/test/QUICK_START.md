# Quick Start - Running Tests

## Step 1: Install Test Dependencies

```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_rest
python3 -m pip install -r test/requirements-test.txt
```

Or install individually:
```bash
python3 -m pip install pytest pytest-cov
```

## Step 2: Run Tests

### Option A: Using pytest directly

```bash
# Run all tests
python3 -m pytest test/test_pagination_types.py -v

# Run specific test class
python3 -m pytest test/test_pagination_types.py::TestOffsetLimitPagination -v

# Run single test
python3 -m pytest test/test_pagination_types.py::TestNoPagination::test_jsonplaceholder_single_post -v

# Run with coverage
python3 -m pytest test/test_pagination_types.py --cov=elt_ingest_rest --cov-report=html
```

### Option B: Using the test runner script

```bash
# Make executable (first time only)
chmod +x test/run_tests.sh

# Run all tests
./test/run_tests.sh all

# Run specific pagination type tests
./test/run_tests.sh offset-limit
./test/run_tests.sh page-number
./test/run_tests.sh link-header

# Run with coverage
./test/run_tests.sh coverage

# Quick smoke test
./test/run_tests.sh quick
```

## Step 3: View Results

Test output will be displayed in the terminal with:
- ✅ Green checkmarks for passed tests
- ❌ Red X for failed tests
- ⚠️ Yellow for skipped tests

Output files are saved to: `./output/test/`

## Expected Results

With all dependencies installed and internet connection active:

```
test_pagination_types.py::TestNoPagination::test_jsonplaceholder_single_post PASSED
test_pagination_types.py::TestNoPagination::test_jsonplaceholder_all_posts PASSED
test_pagination_types.py::TestOffsetLimitPagination::test_jsonplaceholder_offset_limit PASSED
test_pagination_types.py::TestOffsetLimitPagination::test_pokeapi_offset_limit PASSED
test_pagination_types.py::TestOffsetLimitPagination::test_offset_limit_with_max_records PASSED
test_pagination_types.py::TestPageNumberPagination::test_github_page_number PASSED
test_pagination_types.py::TestPageNumberPagination::test_github_search_page_number PASSED
test_pagination_types.py::TestPageNumberPagination::test_openlibrary_page_number PASSED
test_pagination_types.py::TestLinkHeaderPagination::test_github_link_header PASSED
test_pagination_types.py::TestCursorPagination::test_github_graphql_style_cursor SKIPPED
test_pagination_types.py::TestNextUrlPagination::test_pokeapi_next_url PASSED
test_pagination_types.py::TestEdgeCases::test_empty_results PASSED
test_pagination_types.py::TestEdgeCases::test_single_page_pagination PASSED
test_pagination_types.py::TestEdgeCases::test_custom_headers PASSED
test_pagination_types.py::TestBatchSaving::test_batch_save_mode PASSED
test_pagination_types.py::TestDataExtraction::test_nested_data_path PASSED
test_pagination_types.py::TestDataExtraction::test_root_array_data PASSED

===================== 16 passed, 1 skipped in 15.23s ======================
```

## Troubleshooting

### Error: "pytest not found"
```bash
python3 -m pip install pytest
```

### Error: "ModuleNotFoundError: No module named 'elt_ingest_rest'"
Make sure you're in the project root and the package is installed:
```bash
cd /Users/rpatel/Documents/__code/git/emailrak/elt_lake/elt_ingest_rest
python3 -m pip install -e .
```

### Error: "Connection refused" or "Timeout"
- Check your internet connection
- Some APIs have rate limits (wait a few minutes and retry)

### GitHub API Rate Limit
If you hit GitHub's rate limit (60 requests/hour):
- Wait an hour, or
- Add authentication token to increase limit to 5000/hour:
  ```python
  headers={"Authorization": "token YOUR_GITHUB_TOKEN"}
  ```

## Coverage Report

After running tests with coverage:
```bash
python3 -m pytest test/test_pagination_types.py --cov=elt_ingest_rest --cov-report=html
```

Open the coverage report:
```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Run quick test: `./test/run_tests.sh quick`
3. ✅ Run all tests: `./test/run_tests.sh all`
4. ✅ Review coverage: `./test/run_tests.sh coverage`
5. ✅ Check [TEST_COVERAGE_MATRIX.md](TEST_COVERAGE_MATRIX.md) for detailed API coverage

## Test Data

All test output is saved to `./output/test/` directory structure:
```
output/test/
├── no_pagination/
├── offset_limit/
├── page_number/
├── link_header/
├── next_url/
├── edge_cases/
├── batch_save/
└── data_extraction/
```

You can inspect the downloaded JSON files to verify the ingestion worked correctly.
