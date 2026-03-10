"""Base pagination strategy interface.

All pagination strategies inherit from this base class and implement
the fetch() method with their specific pagination logic.
"""

import csv
import logging
from abc import ABC, abstractmethod
from io import StringIO
from typing import Any, Optional
from urllib.parse import urljoin
from xml.etree import ElementTree

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

    def _make_request(self, url: str, params: Optional[dict] = None) -> Any:
        """Make HTTP request to the API.

        Args:
            url: URL to request
            params: Query parameters (merged with config.params)

        Returns:
            Parsed response content

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
        return self._parse_response(response)

    def _parse_response(self, response: requests.Response) -> Any:
        response_format = self.config.response_format.lower().strip()

        if response_format == "json":
            return response.json()

        if response_format == "csv":
            lines = response.text.splitlines()
            if self.config.csv_skip_rows:
                lines = lines[self.config.csv_skip_rows :]

            lines = [line for line in lines if line.strip()]
            if not lines:
                return []

            reader = csv.DictReader(
                StringIO("\n".join(lines)),
                delimiter=self.config.csv_delimiter,
            )
            return [dict(row) for row in reader]

        if response_format == "xml":
            return self._parse_xml(response.text)

        raise ValueError(f"Unsupported response_format: {self.config.response_format}")

    def _parse_xml(self, xml_text: str) -> list[dict]:
        def local_name(tag: str) -> str:
            if "}" in tag:
                return tag.split("}", 1)[1]
            return tag

        def element_to_record(element: ElementTree.Element) -> dict:
            record: dict[str, Any] = dict(element.attrib)

            for child in list(element):
                child_key = local_name(child.tag)
                child_text = (child.text or "").strip()

                if child_text:
                    if child_key in record:
                        existing = record[child_key]
                        if isinstance(existing, list):
                            existing.append(child_text)
                        else:
                            record[child_key] = [existing, child_text]
                    else:
                        record[child_key] = child_text
                elif child.attrib:
                    for attr_key, attr_value in child.attrib.items():
                        record[f"{child_key}.{attr_key}"] = attr_value

            return record

        root = ElementTree.fromstring(xml_text)

        boe_series = [
            element
            for element in root.iter()
            if local_name(element.tag) == "Cube" and "SCODE" in element.attrib
        ]
        if boe_series:
            records: list[dict] = []
            for series_element in boe_series:
                series_code = series_element.attrib.get("SCODE")
                series_description = series_element.attrib.get("DESC")

                for cube in series_element:
                    if local_name(cube.tag) != "Cube":
                        continue
                    if "TIME" not in cube.attrib or "OBS_VALUE" not in cube.attrib:
                        continue

                    record: dict[str, Any] = {
                        "series_code": series_code,
                        "series_description": series_description,
                        "time": cube.attrib.get("TIME"),
                        "value": cube.attrib.get("OBS_VALUE"),
                    }
                    if "OBS_CONF" in cube.attrib:
                        record["obs_conf"] = cube.attrib.get("OBS_CONF")
                    if "LAST_UPDATED" in cube.attrib:
                        record["last_updated"] = cube.attrib.get("LAST_UPDATED")

                    records.append(record)

            return records

        record_tag = self.config.xml_record_tag.strip()
        if record_tag:
            elements = [
                element
                for element in root.iter()
                if local_name(element.tag) == record_tag
            ]
            return [element_to_record(element) for element in elements]

        children = list(root)
        if not children:
            return [element_to_record(root)]

        return [element_to_record(child) for child in children]

    def _extract_data(self, response: Any) -> list[dict]:
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
            if response is None:
                return []
            if isinstance(response, dict):
                return [response]
            return [{"value": response}]

        # Extract nested data
        if not isinstance(response, dict):
            return []

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

    def _should_stop(self, response: Any, page_count: int, total_records: int) -> bool:
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
        if (
            config.stop_condition
            and isinstance(response, dict)
            and config.stop_condition(response)
        ):
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
