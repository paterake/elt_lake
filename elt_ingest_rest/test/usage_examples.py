"""Example usage of the RestApiIngester class."""

from pathlib import Path
from elt_ingest_rest.ingest_rest import (
    IngestConfig,
    PaginationConfig,
    PaginationType,
    RestApiIngester,
)


def example_no_pagination():
    """Example: Fetch data from non-paginated API."""
    config = IngestConfig(
        base_url="https://api.example.com",
        endpoint="/users/123",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        pagination=PaginationConfig(type=PaginationType.NONE),
        output_dir=Path("./output/users"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()
    print(f"Fetched {len(data)} records, saved to {output_path}")


def example_offset_limit_pagination():
    """Example: Fetch data with offset/limit pagination."""
    config = IngestConfig(
        base_url="https://api.example.com",
        endpoint="/api/v1/products",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        pagination=PaginationConfig(
            type=PaginationType.OFFSET_LIMIT,
            page_size=100,
            offset_param="offset",
            limit_param="limit",
            data_path="results",  # Extract data from response.results
            max_records=1000,  # Limit to 1000 records
        ),
        output_dir=Path("./output/products"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()
    print(f"Fetched {len(data)} records, saved to {output_path}")


def example_page_number_pagination():
    """Example: Fetch data with page number pagination."""
    config = IngestConfig(
        base_url="https://api.github.com",
        endpoint="/users/octocat/repos",
        headers={"Accept": "application/vnd.github.v3+json"},
        pagination=PaginationConfig(
            type=PaginationType.PAGE_NUMBER,
            page_size=30,
            page_param="page",
            page_size_param="per_page",
            data_path="",  # Data is at root level (array)
            max_pages=5,
        ),
        output_dir=Path("./output/github"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()
    print(f"Fetched {len(data)} records, saved to {output_path}")


def example_cursor_pagination():
    """Example: Fetch data with cursor-based pagination."""
    config = IngestConfig(
        base_url="https://api.example.com",
        endpoint="/api/v1/events",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        pagination=PaginationConfig(
            type=PaginationType.CURSOR,
            page_size=100,
            cursor_param="cursor",
            cursor_path="pagination.next_cursor",  # Nested path to cursor
            data_path="data",
        ),
        output_dir=Path("./output/events"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()
    print(f"Fetched {len(data)} records, saved to {output_path}")


def example_next_url_pagination():
    """Example: Fetch data with next URL pagination."""
    config = IngestConfig(
        base_url="https://api.example.com",
        endpoint="/api/orders",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        pagination=PaginationConfig(
            type=PaginationType.NEXT_URL,
            next_url_path="next",  # Response contains {"data": [...], "next": "url"}
            data_path="data",
        ),
        output_dir=Path("./output/orders"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()
    print(f"Fetched {len(data)} records, saved to {output_path}")


def example_link_header_pagination():
    """Example: Fetch data with Link header pagination (RFC 5988)."""
    config = IngestConfig(
        base_url="https://api.example.com",
        endpoint="/api/v2/customers",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        pagination=PaginationConfig(
            type=PaginationType.LINK_HEADER,
            link_header_name="Link",
            data_path="",  # Data at root
        ),
        output_dir=Path("./output/customers"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()
    print(f"Fetched {len(data)} records, saved to {output_path}")


def example_batch_save():
    """Example: Save data in multiple batch files."""
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
    print(f"Fetched {len(data)} records, saved in batches to {output_path}")


def example_with_query_params():
    """Example: Include query parameters in requests."""
    config = IngestConfig(
        base_url="https://api.example.com",
        endpoint="/api/v1/sales",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "status": "completed",
        },
        pagination=PaginationConfig(
            type=PaginationType.OFFSET_LIMIT,
            page_size=100,
            data_path="results",
        ),
        output_dir=Path("./output/sales"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()
    print(f"Fetched {len(data)} records, saved to {output_path}")


def example_with_stop_condition():
    """Example: Use custom stop condition."""

    def stop_when_date_reached(response: dict) -> bool:
        """Stop if we've reached data before 2024."""
        data = response.get("data", [])
        if not data:
            return False
        # Check if last record is before 2024
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
    print(f"Fetched {len(data)} records, saved to {output_path}")


def example_post_request():
    """Example: Use POST request to fetch data."""
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
    print(f"Fetched {len(data)} records, saved to {output_path}")


def example_basic_auth():
    """Example: Use basic authentication."""
    config = IngestConfig(
        base_url="https://api.example.com",
        endpoint="/api/v1/protected/data",
        auth=("username", "password"),  # Basic auth
        pagination=PaginationConfig(type=PaginationType.NONE),
        output_dir=Path("./output/protected"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()
    print(f"Fetched {len(data)} records, saved to {output_path}")


if __name__ == "__main__":
    # Uncomment the example you want to run
    # example_no_pagination()
    # example_offset_limit_pagination()
    # example_page_number_pagination()
    # example_cursor_pagination()
    # example_next_url_pagination()
    # example_link_header_pagination()
    # example_batch_save()
    # example_with_query_params()
    # example_with_stop_condition()
    # example_post_request()
    # example_basic_auth()
    pass
