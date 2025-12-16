"""Pagination configuration models."""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


class PaginationType(Enum):
    """Supported pagination types for REST APIs.

    Each type represents a different strategy for fetching paginated data:
    - NONE: Single request, no pagination
    - OFFSET_LIMIT: Skip N records, fetch M records (e.g., ?offset=100&limit=50)
    - PAGE_NUMBER: Fetch page N with M records per page (e.g., ?page=2&per_page=50)
    - CURSOR: Use opaque cursor token for next page (e.g., ?cursor=abc123)
    - LINK_HEADER: Follow RFC 5988 Link header with rel="next"
    - NEXT_URL: Follow URL in response body (e.g., {"next": "https://..."})
    """

    NONE = "none"
    OFFSET_LIMIT = "offset_limit"
    PAGE_NUMBER = "page_number"
    CURSOR = "cursor"
    LINK_HEADER = "link_header"
    NEXT_URL = "next_url"


@dataclass
class PaginationConfig:
    """Configuration for API pagination strategy.

    This class defines all parameters needed for different pagination types.
    Not all parameters are used by all pagination types - see PaginationType
    for which parameters apply to which strategy.
    """

    # Core pagination settings
    type: PaginationType = PaginationType.NONE
    page_size: int = 100

    # OFFSET_LIMIT pagination parameters
    offset_param: str = "offset"
    limit_param: str = "limit"

    # PAGE_NUMBER pagination parameters
    page_param: str = "page"
    page_size_param: str = "per_page"

    # CURSOR pagination parameters
    cursor_param: str = "cursor"
    cursor_path: str = "next_cursor"  # JSONPath to extract cursor from response

    # NEXT_URL pagination parameters
    next_url_path: str = "next"  # JSONPath to extract next URL from response

    # LINK_HEADER pagination parameters
    link_header_name: str = "Link"

    # Response data extraction
    data_path: str = "data"  # JSONPath to extract data array from response

    # Limits (0 = unlimited)
    max_pages: int = 0
    max_records: int = 0

    # Custom stop condition callback
    stop_condition: Optional[Callable[[dict], bool]] = None
