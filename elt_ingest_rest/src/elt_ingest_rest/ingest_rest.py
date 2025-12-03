"""REST API ingestion module for paginated and non-paginated endpoints."""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class PaginationType(Enum):
    """Supported pagination types."""

    NONE = "none"
    OFFSET_LIMIT = "offset_limit"
    PAGE_NUMBER = "page_number"
    CURSOR = "cursor"
    LINK_HEADER = "link_header"
    NEXT_URL = "next_url"


@dataclass
class PaginationConfig:
    """Configuration for API pagination."""

    type: PaginationType = PaginationType.NONE
    page_size: int = 100

    # For OFFSET_LIMIT pagination
    offset_param: str = "offset"
    limit_param: str = "limit"

    # For PAGE_NUMBER pagination
    page_param: str = "page"
    page_size_param: str = "per_page"

    # For CURSOR pagination
    cursor_param: str = "cursor"
    cursor_path: str = "next_cursor"  # JSONPath to extract cursor from response

    # For NEXT_URL pagination
    next_url_path: str = "next"  # JSONPath to extract next URL from response

    # For LINK_HEADER pagination
    link_header_name: str = "Link"

    # Response data extraction
    data_path: str = "data"  # JSONPath to extract data array from response

    # Maximum pages/records to fetch (0 = unlimited)
    max_pages: int = 0
    max_records: int = 0

    # Stop condition callback
    stop_condition: Optional[Callable[[dict], bool]] = None


@dataclass
class IngestConfig:
    """Configuration for REST API ingestion."""

    base_url: str
    endpoint: str = ""
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    body: Optional[dict[str, Any]] = None
    auth: Optional[tuple[str, str]] = None
    timeout: int = 30
    verify_ssl: bool = True

    # Pagination configuration
    pagination: PaginationConfig = field(default_factory=PaginationConfig)

    # Output configuration
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    output_filename: Optional[str] = None
    save_mode: str = "single"  # "single" or "batch"
    batch_size: int = 1000

    # Retry configuration
    max_retries: int = 3
    backoff_factor: float = 0.3
    retry_status_codes: list[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])


class RestApiIngester:
    """Ingest data from REST APIs with support for various pagination types."""

    def __init__(self, config: IngestConfig):
        """Initialize the ingester with configuration.

        Args:
            config: IngestConfig object with API and output settings
        """
        self.config = config
        self.session = self._create_session()
        self.total_records = 0
        self.total_pages = 0

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=self.config.retry_status_codes,
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        if self.config.auth:
            session.auth = self.config.auth

        session.headers.update(self.config.headers)
        session.verify = self.config.verify_ssl

        return session

    def _get_nested_value(self, data: dict, path: str) -> Any:
        """Extract nested value from dict using dot notation path.

        Args:
            data: Dictionary to extract from
            path: Dot-separated path (e.g., "meta.pagination.next")

        Returns:
            Extracted value or None
        """
        if not path:
            return data

        keys = path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

        return value

    def _make_request(self, url: str, params: Optional[dict] = None) -> dict:
        """Make HTTP request to the API.

        Args:
            url: URL to request
            params: Query parameters

        Returns:
            Response JSON data
        """
        request_params = {**self.config.params, **(params or {})}

        logger.info(f"Making {self.config.method} request to {url}")
        logger.debug(f"Parameters: {request_params}")

        response = self.session.request(
            method=self.config.method,
            url=url,
            params=request_params,
            json=self.config.body,
            timeout=self.config.timeout
        )

        response.raise_for_status()
        return response.json()

    def _extract_data(self, response: dict) -> list[dict]:
        """Extract data array from response.

        Args:
            response: API response dictionary

        Returns:
            List of data records
        """
        data = self._get_nested_value(response, self.config.pagination.data_path)

        # If data_path is empty or data is already a list at root
        if data is None:
            if isinstance(response, list):
                return response
            return [response]

        if isinstance(data, list):
            return data

        return [data]

    def _should_stop(self, response: dict, page_count: int, record_count: int) -> bool:
        """Check if pagination should stop.

        Args:
            response: Current response data
            page_count: Number of pages fetched
            record_count: Number of records fetched

        Returns:
            True if should stop, False otherwise
        """
        config = self.config.pagination

        # Check max limits
        if config.max_pages > 0 and page_count >= config.max_pages:
            logger.info(f"Reached max pages limit: {config.max_pages}")
            return True

        if config.max_records > 0 and record_count >= config.max_records:
            logger.info(f"Reached max records limit: {config.max_records}")
            return True

        # Check custom stop condition
        if config.stop_condition and config.stop_condition(response):
            logger.info("Stop condition met")
            return True

        return False

    def _fetch_no_pagination(self) -> list[dict]:
        """Fetch data from non-paginated endpoint."""
        url = urljoin(self.config.base_url, self.config.endpoint)
        response = self._make_request(url)
        return self._extract_data(response)

    def _fetch_offset_limit(self) -> list[dict]:
        """Fetch data using offset/limit pagination."""
        all_data = []
        offset = 0
        page_count = 0

        config = self.config.pagination
        url = urljoin(self.config.base_url, self.config.endpoint)

        while True:
            params = {
                config.offset_param: offset,
                config.limit_param: config.page_size
            }

            response = self._make_request(url, params)
            data = self._extract_data(response)

            if not data:
                break

            all_data.extend(data)
            page_count += 1

            if self._should_stop(response, page_count, len(all_data)):
                break

            if len(data) < config.page_size:
                break

            offset += config.page_size

        return all_data

    def _fetch_page_number(self) -> list[dict]:
        """Fetch data using page number pagination."""
        all_data = []
        page = 1

        config = self.config.pagination
        url = urljoin(self.config.base_url, self.config.endpoint)

        while True:
            params = {
                config.page_param: page,
                config.page_size_param: config.page_size
            }

            response = self._make_request(url, params)
            data = self._extract_data(response)

            if not data:
                break

            all_data.extend(data)

            if self._should_stop(response, page, len(all_data)):
                break

            if len(data) < config.page_size:
                break

            page += 1

        return all_data

    def _fetch_cursor(self) -> list[dict]:
        """Fetch data using cursor-based pagination."""
        all_data = []
        cursor = None
        page_count = 0

        config = self.config.pagination
        url = urljoin(self.config.base_url, self.config.endpoint)

        while True:
            params = {}
            if cursor:
                params[config.cursor_param] = cursor
            else:
                params[config.cursor_param] = ""

            response = self._make_request(url, params)
            data = self._extract_data(response)

            if not data:
                break

            all_data.extend(data)
            page_count += 1

            if self._should_stop(response, page_count, len(all_data)):
                break

            # Extract next cursor
            cursor = self._get_nested_value(response, config.cursor_path)
            if not cursor:
                break

        return all_data

    def _fetch_next_url(self) -> list[dict]:
        """Fetch data using next URL pagination."""
        all_data = []
        url = urljoin(self.config.base_url, self.config.endpoint)
        page_count = 0

        config = self.config.pagination

        while url:
            response = self._make_request(url, params={} if page_count > 0 else None)
            data = self._extract_data(response)

            if not data:
                break

            all_data.extend(data)
            page_count += 1

            if self._should_stop(response, page_count, len(all_data)):
                break

            # Extract next URL
            next_url = self._get_nested_value(response, config.next_url_path)
            if not next_url:
                break

            # Handle relative URLs
            if next_url.startswith("http"):
                url = next_url
            else:
                url = urljoin(self.config.base_url, next_url)

        return all_data

    def _fetch_link_header(self) -> list[dict]:
        """Fetch data using Link header pagination."""
        all_data = []
        url = urljoin(self.config.base_url, self.config.endpoint)
        page_count = 0

        while url:
            response = self.session.request(
                method=self.config.method,
                url=url,
                params=self.config.params if page_count == 0 else {},
                json=self.config.body,
                timeout=self.config.timeout
            )

            response.raise_for_status()
            data_json = response.json()
            data = self._extract_data(data_json)

            if not data:
                break

            all_data.extend(data)
            page_count += 1

            if self._should_stop(data_json, page_count, len(all_data)):
                break

            # Parse Link header
            link_header = response.headers.get(self.config.pagination.link_header_name, "")
            url = self._parse_link_header(link_header)

        return all_data

    def _parse_link_header(self, link_header: str) -> Optional[str]:
        """Parse Link header to extract next URL.

        Args:
            link_header: Link header value

        Returns:
            Next URL or None
        """
        if not link_header:
            return None

        links = link_header.split(",")
        for link in links:
            parts = link.split(";")
            if len(parts) < 2:
                continue

            url = parts[0].strip()[1:-1]  # Remove < and >
            rel = parts[1].strip()

            if 'rel="next"' in rel or "rel='next'" in rel:
                return url

        return None

    def fetch(self) -> list[dict]:
        """Fetch all data from the API based on pagination type.

        Returns:
            List of all fetched records
        """
        logger.info(f"Starting ingestion from {self.config.base_url}{self.config.endpoint}")
        logger.info(f"Pagination type: {self.config.pagination.type.value}")

        pagination_handlers = {
            PaginationType.NONE: self._fetch_no_pagination,
            PaginationType.OFFSET_LIMIT: self._fetch_offset_limit,
            PaginationType.PAGE_NUMBER: self._fetch_page_number,
            PaginationType.CURSOR: self._fetch_cursor,
            PaginationType.NEXT_URL: self._fetch_next_url,
            PaginationType.LINK_HEADER: self._fetch_link_header,
        }

        handler = pagination_handlers.get(self.config.pagination.type)
        if not handler:
            raise ValueError(f"Unsupported pagination type: {self.config.pagination.type}")

        data = handler()
        self.total_records = len(data)

        logger.info(f"Fetched {self.total_records} total records")
        return data

    def _get_output_filename(self) -> str:
        """Generate output filename."""
        if self.config.output_filename:
            return self.config.output_filename

        # Generate filename from endpoint and timestamp
        endpoint_name = self.config.endpoint.strip("/").replace("/", "_") or "api_data"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{endpoint_name}_{timestamp}.json"

    def save(self, data: list[dict]) -> Path:
        """Save fetched data to disk.

        Args:
            data: Data to save

        Returns:
            Path to saved file
        """
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        if self.config.save_mode == "single":
            return self._save_single(data)
        elif self.config.save_mode == "batch":
            return self._save_batch(data)
        else:
            raise ValueError(f"Unsupported save mode: {self.config.save_mode}")

    def _save_single(self, data: list[dict]) -> Path:
        """Save all data to a single file.

        Args:
            data: Data to save

        Returns:
            Path to saved file
        """
        filename = self._get_output_filename()
        filepath = self.config.output_dir / filename

        logger.info(f"Saving {len(data)} records to {filepath}")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully saved data to {filepath}")
        return filepath

    def _save_batch(self, data: list[dict]) -> Path:
        """Save data in multiple batch files.

        Args:
            data: Data to save

        Returns:
            Path to output directory
        """
        base_filename = self._get_output_filename().replace(".json", "")
        batch_size = self.config.batch_size

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_num = i // batch_size + 1
            filename = f"{base_filename}_batch_{batch_num:04d}.json"
            filepath = self.config.output_dir / filename

            logger.info(f"Saving batch {batch_num} ({len(batch)} records) to {filepath}")

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(batch, f, indent=2, ensure_ascii=False)

        logger.info(f"Successfully saved {len(data)} records in batches to {self.config.output_dir}")
        return self.config.output_dir

    def ingest(self) -> tuple[list[dict], Path]:
        """Fetch and save data from the API.

        Returns:
            Tuple of (fetched data, output path)
        """
        data = self.fetch()
        output_path = self.save(data)
        return data, output_path
