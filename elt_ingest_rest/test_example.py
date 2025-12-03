"""Simple test example to verify the REST API ingester works."""

from pathlib import Path
from elt_ingest_rest import IngestConfig, PaginationConfig, PaginationType, RestApiIngester


def test_github_api():
    """Test with GitHub's public API (no auth required)."""
    print("Testing REST API Ingester with GitHub API...")

    config = IngestConfig(
        base_url="https://api.github.com",
        endpoint="/users/octocat/repos",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Python-REST-Ingester"
        },
        pagination=PaginationConfig(
            type=PaginationType.PAGE_NUMBER,
            page_size=10,
            page_param="page",
            page_size_param="per_page",
            data_path="",  # Data is at root level (array)
            max_pages=1,  # Just fetch 1 page for testing
        ),
        output_dir=Path("./output/github_test"),
    )

    ingester = RestApiIngester(config)
    data, output_path = ingester.ingest()

    print(f"\n✓ Success!")
    print(f"  - Fetched {len(data)} repositories")
    print(f"  - Saved to: {output_path}")
    print(f"\nFirst repo name: {data[0]['name'] if data else 'N/A'}")


if __name__ == "__main__":
    test_github_api()
