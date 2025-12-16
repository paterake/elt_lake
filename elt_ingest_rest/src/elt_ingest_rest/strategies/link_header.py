"""Link header pagination strategy (RFC 5988)."""

import logging
import re
from typing import Optional
from .base import BasePaginationStrategy

logger = logging.getLogger(__name__)


class LinkHeaderStrategy(BasePaginationStrategy):
    """Strategy for Link header pagination (RFC 5988).

    API returns pagination links in HTTP Link header.

    Example header:
    Link: <https://api.example.com/items?page=2>; rel="next",
          <https://api.example.com/items?page=5>; rel="last"

    Common in:
    - GitHub API
    - GitLab API
    - Many RESTful APIs following RFC 5988

    RFC 5988: https://tools.ietf.org/html/rfc5988
    """

    def fetch(self) -> list[dict]:
        """Fetch data using Link header pagination.

        Algorithm:
        1. Make request and check Link header
        2. Parse Link header for rel="next"
        3. Follow next URL
        4. Continue until no next link or limits reached

        Returns:
            List of all records fetched
        """
        all_data = []
        url = self._build_url()
        page_count = 0

        while url:
            # Make request (need full response for headers)
            response = self.session.request(
                method=self.config.method,
                url=url,
                params=self.config.params if page_count == 0 else {},
                json=self.config.body,
                timeout=self.config.timeout,
            )

            response.raise_for_status()
            data_json = response.json()
            data = self._extract_data(data_json)

            # No more data - stop
            if not data:
                break

            all_data.extend(data)
            page_count += 1

            # Check stop conditions
            if self._should_stop(data_json, page_count, len(all_data)):
                break

            # Parse Link header for next URL
            link_header = response.headers.get(
                self.config.pagination.link_header_name, ""
            )
            url = self._parse_link_header(link_header)

        return all_data

    def _parse_link_header(self, link_header: str) -> Optional[str]:
        """Parse Link header to extract next URL.

        Parses RFC 5988 format:
        <url>; rel="next", <url>; rel="last"

        Args:
            link_header: Value of Link header

        Returns:
            Next URL if found, None otherwise

        Example:
            >>> header = '<https://api.example.com/page2>; rel="next"'
            >>> self._parse_link_header(header)
            'https://api.example.com/page2'
        """
        if not link_header:
            return None

        # Split by comma to get individual links
        links = link_header.split(",")

        for link in links:
            # Match pattern: <url>; rel="next"
            match = re.match(r'<([^>]+)>;\s*rel="next"', link.strip())
            if match:
                return match.group(1)

        return None
