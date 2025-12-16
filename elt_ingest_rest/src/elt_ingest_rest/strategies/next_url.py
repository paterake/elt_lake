"""Next URL pagination strategy."""

import logging
from urllib.parse import urljoin
from .base import BasePaginationStrategy

logger = logging.getLogger(__name__)


class NextUrlStrategy(BasePaginationStrategy):
    """Strategy for next URL pagination.

    API returns full or relative URL for next page in response body.

    Example response:
    {
      "data": [...],
      "next": "https://api.example.com/items?page=2"
    }

    Or relative URL:
    {
      "results": [...],
      "next": "/api/items?page=2"
    }

    Common in REST APIs (PokeAPI, many others)
    """

    def fetch(self) -> list[dict]:
        """Fetch data using next URL pagination.

        Algorithm:
        1. Start with initial URL
        2. Extract data from response
        3. Extract next URL from response.next_url_path
        4. Continue following next URLs until none or limits reached

        Returns:
            List of all records fetched
        """
        all_data = []
        url = self._build_url()
        page_count = 0

        config = self.config.pagination

        while url:
            # Make request
            # Skip params on subsequent requests (already in next URL)
            response = self._make_request(url, params={} if page_count > 0 else None)
            data = self._extract_data(response)

            # No more data - stop
            if not data:
                break

            all_data.extend(data)
            page_count += 1

            # Check stop conditions
            if self._should_stop(response, page_count, len(all_data)):
                break

            # Extract next URL
            next_url = self._get_nested_value(response, config.next_url_path)
            if not next_url:
                break

            # Handle relative URLs
            if next_url.startswith("http"):
                url = next_url  # Absolute URL
            else:
                url = urljoin(self.config.base_url, next_url)  # Relative URL

        return all_data
