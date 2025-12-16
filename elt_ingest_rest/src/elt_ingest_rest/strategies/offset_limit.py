"""Offset/limit pagination strategy."""

import logging
from .base import BasePaginationStrategy

logger = logging.getLogger(__name__)


class OffsetLimitStrategy(BasePaginationStrategy):
    """Strategy for offset/limit pagination.

    Example: ?offset=100&limit=50
    - offset: Number of records to skip
    - limit: Number of records to return

    Common in REST APIs, databases (SQL OFFSET/LIMIT)
    """

    def fetch(self) -> list[dict]:
        """Fetch data using offset/limit pagination.

        Algorithm:
        1. Start with offset=0
        2. Request: ?offset=0&limit=page_size
        3. Increment offset by page_size
        4. Continue until no more data or limits reached

        Returns:
            List of all records fetched
        """
        all_data = []
        offset = 0
        page_count = 0

        config = self.config.pagination
        url = self._build_url()

        while True:
            # Build pagination parameters
            params = {
                config.offset_param: offset,
                config.limit_param: config.page_size,
            }

            # Make request
            response = self._make_request(url, params)
            data = self._extract_data(response)

            # No more data - stop
            if not data:
                break

            all_data.extend(data)
            page_count += 1

            # Check stop conditions
            if self._should_stop(response, page_count, len(all_data)):
                break

            # Partial page indicates last page
            if len(data) < config.page_size:
                break

            # Move to next page
            offset += config.page_size

        return all_data
