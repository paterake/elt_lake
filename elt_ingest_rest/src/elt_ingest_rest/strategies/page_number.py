"""Page number pagination strategy."""

import logging
from .base import BasePaginationStrategy

logger = logging.getLogger(__name__)


class PageNumberStrategy(BasePaginationStrategy):
    """Strategy for page number pagination.

    Example: ?page=2&per_page=50
    - page: Page number (usually 1-indexed)
    - per_page: Records per page

    Common in REST APIs (GitHub, many others)
    """

    def fetch(self) -> list[dict]:
        """Fetch data using page number pagination.

        Algorithm:
        1. Start with page=1
        2. Request: ?page=1&per_page=page_size
        3. Increment page by 1
        4. Continue until no more data or limits reached

        Returns:
            List of all records fetched
        """
        all_data = []
        page = 1

        config = self.config.pagination
        url = self._build_url()

        while True:
            # Build pagination parameters
            params = {
                config.page_param: page,
                config.page_size_param: config.page_size,
            }

            # Make request
            response = self._make_request(url, params)
            data = self._extract_data(response)

            # No more data - stop
            if not data:
                break

            all_data.extend(data)

            # Check stop conditions
            if self._should_stop(response, page, len(all_data)):
                break

            # Partial page indicates last page
            if len(data) < config.page_size:
                break

            # Move to next page
            page += 1

        return all_data
