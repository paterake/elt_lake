"""No pagination strategy - single request."""

import logging
from .base import BasePaginationStrategy

logger = logging.getLogger(__name__)


class NoPaginationStrategy(BasePaginationStrategy):
    """Strategy for non-paginated endpoints.

    Makes a single HTTP request and returns all data.
    Used when pagination.type = PaginationType.NONE
    """

    def fetch(self) -> list[dict]:
        """Fetch data from non-paginated endpoint.

        Returns:
            List of all records from single request
        """
        url = self._build_url()
        response = self._make_request(url)
        return self._extract_data(response)
