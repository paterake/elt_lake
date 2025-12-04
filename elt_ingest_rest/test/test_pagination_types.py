"""Comprehensive tests for all pagination types using real public APIs."""

import pytest
from pathlib import Path
from elt_ingest_rest.ingest_rest import (
    IngestConfig,
    PaginationConfig,
    PaginationType,
    RestApiIngester,
)


class TestNoPagination:
    """Test non-paginated API endpoints."""

    def test_jsonplaceholder_single_post(self):
        """Test fetching a single post (no pagination)."""
        config = IngestConfig(
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="/posts/1",
            pagination=PaginationConfig(
                type=PaginationType.NONE,
                data_path="",  # Single object at root
            ),
            output_dir=Path("./output/test/no_pagination"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 1
        assert data[0]["id"] == 1
        assert "title" in data[0]
        assert output_path.exists()

    def test_jsonplaceholder_all_posts(self):
        """Test fetching all posts at once (no pagination)."""
        config = IngestConfig(
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="/posts",
            pagination=PaginationConfig(
                type=PaginationType.NONE,
                data_path="",  # Array at root
            ),
            output_dir=Path("./output/test/no_pagination"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 100  # jsonplaceholder has 100 posts
        assert data[0]["id"] == 1
        assert output_path.exists()


class TestOffsetLimitPagination:
    """Test offset/limit pagination."""

    def test_jsonplaceholder_offset_limit(self):
        """Test JSONPlaceholder with offset/limit using _start and _limit."""
        config = IngestConfig(
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="/posts",
            pagination=PaginationConfig(
                type=PaginationType.OFFSET_LIMIT,
                page_size=10,
                offset_param="_start",
                limit_param="_limit",
                data_path="",  # Array at root
                max_pages=3,  # Fetch only 3 pages
            ),
            output_dir=Path("./output/test/offset_limit"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 30  # 3 pages × 10 records
        assert data[0]["id"] == 1
        assert data[10]["id"] == 11  # Second page starts at ID 11
        assert output_path.exists()

    def test_pokeapi_offset_limit(self):
        """Test PokeAPI with offset/limit pagination."""
        config = IngestConfig(
            base_url="https://pokeapi.co",
            endpoint="/api/v2/pokemon",
            pagination=PaginationConfig(
                type=PaginationType.OFFSET_LIMIT,
                page_size=20,
                offset_param="offset",
                limit_param="limit",
                data_path="results",  # Data is in results array
                max_pages=2,  # Fetch only 2 pages
            ),
            output_dir=Path("./output/test/offset_limit"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 40  # 2 pages × 20 records
        assert "name" in data[0]
        assert "url" in data[0]
        assert output_path.exists()

    def test_offset_limit_with_max_records(self):
        """Test offset/limit with max_records limit."""
        config = IngestConfig(
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="/posts",
            pagination=PaginationConfig(
                type=PaginationType.OFFSET_LIMIT,
                page_size=10,
                offset_param="_start",
                limit_param="_limit",
                data_path="",
                max_records=25,  # Stop after 25 records
            ),
            output_dir=Path("./output/test/offset_limit"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 30  # Will fetch 3 pages (30 records) to reach 25+
        assert output_path.exists()


class TestPageNumberPagination:
    """Test page number pagination."""

    def test_github_page_number(self):
        """Test GitHub API with page number pagination."""
        config = IngestConfig(
            base_url="https://api.github.com",
            endpoint="/users/octocat/repos",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Python-REST-Ingester-Test",
            },
            pagination=PaginationConfig(
                type=PaginationType.PAGE_NUMBER,
                page_size=10,
                page_param="page",
                page_size_param="per_page",
                data_path="",  # Array at root
                max_pages=2,  # Fetch only 2 pages
            ),
            output_dir=Path("./output/test/page_number"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) >= 8  # octocat has at least 8 repos
        assert "name" in data[0]
        assert "full_name" in data[0]
        assert output_path.exists()

    def test_github_search_page_number(self):
        """Test GitHub search API with page number pagination."""
        config = IngestConfig(
            base_url="https://api.github.com",
            endpoint="/search/repositories",
            params={"q": "language:python", "sort": "stars"},
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Python-REST-Ingester-Test",
            },
            pagination=PaginationConfig(
                type=PaginationType.PAGE_NUMBER,
                page_size=10,
                page_param="page",
                page_size_param="per_page",
                data_path="items",  # Results are in items array
                max_pages=2,
            ),
            output_dir=Path("./output/test/page_number"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 20  # 2 pages × 10 items
        assert "name" in data[0]
        assert "stargazers_count" in data[0]
        assert output_path.exists()

    def test_openlibrary_page_number(self):
        """Test Open Library API with page number pagination."""
        config = IngestConfig(
            base_url="https://openlibrary.org",
            endpoint="/search.json",
            params={"q": "python programming"},
            pagination=PaginationConfig(
                type=PaginationType.PAGE_NUMBER,
                page_size=10,
                page_param="page",
                page_size_param="limit",  # Open Library uses 'limit' not 'per_page'
                data_path="docs",  # Results are in docs array
                max_pages=2,
            ),
            output_dir=Path("./output/test/page_number"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) >= 10  # Should get at least 10 results
        assert output_path.exists()


class TestLinkHeaderPagination:
    """Test Link header pagination (RFC 5988)."""

    def test_github_link_header(self):
        """Test GitHub API with Link header pagination."""
        config = IngestConfig(
            base_url="https://api.github.com",
            endpoint="/users/torvalds/repos",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Python-REST-Ingester-Test",
            },
            params={"per_page": "10"},  # Small page size to ensure pagination
            pagination=PaginationConfig(
                type=PaginationType.LINK_HEADER,
                link_header_name="Link",
                data_path="",  # Array at root
                max_pages=2,
            ),
            output_dir=Path("./output/test/link_header"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) >= 10  # Should get at least 10 repos
        assert "name" in data[0]
        assert output_path.exists()


class TestCursorPagination:
    """Test cursor-based pagination."""

    def test_github_graphql_style_cursor(self):
        """
        Test cursor pagination pattern.
        Note: Most public APIs with cursor pagination require authentication.
        This test demonstrates the configuration pattern.
        """
        # This is a configuration example - would need auth token for real test
        config = IngestConfig(
            base_url="https://api.example.com",  # Placeholder
            endpoint="/items",
            pagination=PaginationConfig(
                type=PaginationType.CURSOR,
                page_size=50,
                cursor_param="cursor",
                cursor_path="pagination.next_cursor",
                data_path="data",
            ),
            output_dir=Path("./output/test/cursor"),
        )

        # This test is skipped because most cursor APIs need auth
        pytest.skip("Cursor pagination APIs typically require authentication")


class TestNextUrlPagination:
    """Test next URL pagination."""

    def test_pokeapi_next_url(self):
        """Test PokeAPI with next URL pagination."""
        config = IngestConfig(
            base_url="https://pokeapi.co",
            endpoint="/api/v2/pokemon?limit=20",
            pagination=PaginationConfig(
                type=PaginationType.NEXT_URL,
                next_url_path="next",  # API returns {"next": "url", "results": [...]}
                data_path="results",
                max_pages=3,
            ),
            output_dir=Path("./output/test/next_url"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 60  # 3 pages × 20 records
        assert "name" in data[0]
        assert output_path.exists()


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_results(self):
        """Test handling of empty result set."""
        config = IngestConfig(
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="/posts",
            params={"userId": 99999},  # Non-existent user
            pagination=PaginationConfig(
                type=PaginationType.NONE,
                data_path="",
            ),
            output_dir=Path("./output/test/edge_cases"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 0
        assert output_path.exists()

    def test_single_page_pagination(self):
        """Test pagination when results fit in single page."""
        config = IngestConfig(
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="/posts",
            params={"userId": 1},  # User 1 has 10 posts
            pagination=PaginationConfig(
                type=PaginationType.PAGE_NUMBER,
                page_size=20,  # Larger than result set
                page_param="page",
                page_size_param="per_page",
                data_path="",
            ),
            output_dir=Path("./output/test/edge_cases"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 10  # All results in one page
        assert output_path.exists()

    def test_custom_headers(self):
        """Test with custom headers."""
        config = IngestConfig(
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="/posts/1",
            headers={
                "Accept": "application/json",
                "Custom-Header": "test-value",
            },
            pagination=PaginationConfig(type=PaginationType.NONE),
            output_dir=Path("./output/test/edge_cases"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 1
        assert output_path.exists()


class TestBatchSaving:
    """Test batch save functionality."""

    def test_batch_save_mode(self):
        """Test saving data in multiple batch files."""
        config = IngestConfig(
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="/posts",
            pagination=PaginationConfig(
                type=PaginationType.OFFSET_LIMIT,
                page_size=10,
                offset_param="_start",
                limit_param="_limit",
                data_path="",
                max_pages=5,  # 50 records total
            ),
            output_dir=Path("./output/test/batch_save"),
            save_mode="batch",
            batch_size=20,  # 20 records per file
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 50
        assert output_path.is_dir()

        # Check that batch files were created
        batch_files = list(output_path.glob("*_batch_*.json"))
        assert len(batch_files) == 3  # 50 records / 20 per batch = 3 files


class TestDataExtraction:
    """Test data extraction from various response formats."""

    def test_nested_data_path(self):
        """Test extracting data from nested response structure."""
        config = IngestConfig(
            base_url="https://api.github.com",
            endpoint="/search/repositories",
            params={"q": "language:rust", "sort": "stars"},
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Python-REST-Ingester-Test",
            },
            pagination=PaginationConfig(
                type=PaginationType.PAGE_NUMBER,
                page_size=5,
                page_param="page",
                page_size_param="per_page",
                data_path="items",  # Nested under items
                max_pages=1,
            ),
            output_dir=Path("./output/test/data_extraction"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 5
        assert "name" in data[0]
        assert output_path.exists()

    def test_root_array_data(self):
        """Test when data is array at root level."""
        config = IngestConfig(
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="/users",
            pagination=PaginationConfig(
                type=PaginationType.NONE,
                data_path="",  # Empty path means root level
            ),
            output_dir=Path("./output/test/data_extraction"),
        )

        ingester = RestApiIngester(config)
        data, output_path = ingester.ingest()

        assert len(data) == 10  # jsonplaceholder has 10 users
        assert "name" in data[0]
        assert "email" in data[0]
        assert output_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
