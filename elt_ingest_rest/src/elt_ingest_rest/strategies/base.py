"""Base pagination strategy interface.

All pagination strategies inherit from this base class and implement
the fetch() method with their specific pagination logic.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
from urllib.parse import urljoin

import requests

from ..models import IngestConfig

logger = logging.getLogger(__name__)


class BasePaginationStrategy(ABC):
    """Abstract base class for pagination strategies.

    Each strategy implements the fetch() method which:
    1. Makes HTTP requests to the API
    2. Extracts data from responses
    3. Handles pagination logic
    4. Returns all collected data
    """

    def __init__(self, config: IngestConfig, session: requests.Session):
        """Initialize strategy with configuration and HTTP session.

        Args:
            config: Ingestion configuration
            session: Configured requests session with retry logic
        """
        self.config = config
        self.session = session

    @abstractmethod
    def fetch(self) -> list[dict]:
        """Fetch all data using this pagination strategy.

        Returns:
            List of all records fetched from the API

        Raises:
            requests.HTTPError: If API request fails
        """
        pass

    # --- Helper Methods ---

    def _make_request(self, url: str, params: Optional[dict] = None) -> dict:
        """Make HTTP request to the API.

        Args:
            url: URL to request
            params: Query parameters (merged with config.params)

        Returns:
            Response JSON data

        Raises:
            requests.HTTPError: If request fails
        """
        request_params = {**self.config.params, **(params or {})}

        logger.info(f"Making {self.config.method} request to {url}")
        logger.debug(f"Parameters: {request_params}")

        response = self.session.request(
            method=self.config.method,
            url=url,
            params=request_params,
            json=self.config.body,
            timeout=self.config.timeout,
        )

        response.raise_for_status()
        return response.json()

    def _extract_data(self, response: dict) -> list[dict]:
        """Extract data array from API response.

        Handles both:
        - Array at root level (data_path="")
        - Nested array (data_path="data.items")
        - Single object responses (wraps in list)

        Args:
            response: API response JSON

        Returns:
            List of data records
        """
        data_path = self.config.pagination.data_path

        if not data_path:
            # Data is at root level
            if isinstance(response, list):
                return response
            else:
                return [response]  # Wrap single object

        # Extract nested data
        data = self._get_nested_value(response, data_path)

        if data is None:
            return []
        elif isinstance(data, list):
            return data
        else:
            return [data]  # Wrap single object

    def _get_nested_value(self, data: dict, path: str) -> Any:
        """Extract nested value from dict using dot notation.

        Args:
            data: Dictionary to extract from
            path: Dot-separated path (e.g., "meta.pagination.next")

        Returns:
            Extracted value or None

        Example:
            data = {"meta": {"pagination": {"next": "url"}}}
            _get_nested_value(data, "meta.pagination.next")  # Returns "url"
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

    def _should_stop(
        self, response: dict, page_count: int, total_records: int
    ) -> bool:
        """Check if pagination should stop.

        Checks:
        1. max_pages limit reached
        2. max_records limit reached
        3. Custom stop_condition callback

        Args:
            response: Current API response
            page_count: Number of pages fetched so far
            total_records: Total records fetched so far

        Returns:
            True if should stop pagination
        """
        config = self.config.pagination

        # Check max_pages limit
        if config.max_pages > 0 and page_count >= config.max_pages:
            logger.info(f"Reached max pages limit: {config.max_pages}")
            return True

        # Check max_records limit
        if config.max_records > 0 and total_records >= config.max_records:
            logger.info(f"Reached max records limit: {config.max_records}")
            return True

        # Check custom stop condition
        if config.stop_condition and config.stop_condition(response):
            logger.info("Custom stop condition met")
            return True

        return False

    def _build_url(self, endpoint: str = "") -> str:
        """Build full URL from base_url and endpoint.

        Args:
            endpoint: API endpoint (uses config.endpoint if not provided)

        Returns:
            Full URL
        """
        endpoint = endpoint or self.config.endpoint
        return urljoin(self.config.base_url, endpoint)
