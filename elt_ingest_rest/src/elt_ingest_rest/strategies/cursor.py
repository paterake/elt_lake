"""Cursor-based pagination strategy."""

import logging
from .base import BasePaginationStrategy

logger = logging.getLogger(__name__)


class CursorStrategy(BasePaginationStrategy):
    """Strategy for cursor-based pagination.

    Example: ?cursor=eyJpZCI6MTIzfQ
    - cursor: Opaque token representing position in dataset

    Common in:
    - Facebook Graph API
    - Twitter API
    - GraphQL APIs
    - Large datasets where offset is inefficient

    Response typically contains:
    {
      "data": [...],
      "pagination": {
        "next_cursor": "eyJpZCI6NDU2fQ"
      }
    }
    """

    def fetch(self) -> list[dict]:
        """Fetch data using cursor-based pagination.

        Algorithm:
        1. First request: ?cursor="" (or no cursor param)
        2. Extract next_cursor from response
        3. Next request: ?cursor=<next_cursor>
        4. Continue until no next_cursor or limits reached

        Returns:
            List of all records fetched
        """
        all_data = []
        cursor = None
        page_count = 0

        config = self.config.pagination
        url = self._build_url()

        while True:
            # Build pagination parameters
            params = {}
            if cursor:
                params[config.cursor_param] = cursor
            else:
                # First request - some APIs need empty cursor
                params[config.cursor_param] = ""

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

            # Extract next cursor
            cursor = self._get_nested_value(response, config.cursor_path)
            if not cursor:
                break

        return all_data
