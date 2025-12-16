"""Main ingestion configuration model."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .pagination import PaginationConfig


@dataclass
class IngestConfig:
    """Configuration for REST API ingestion.

    This is the main configuration object that defines:
    - HTTP request parameters (URL, headers, auth, etc.)
    - Pagination strategy (via PaginationConfig)
    - Output settings (where and how to save data)
    - Retry/timeout settings
    """

    # Required: API endpoint
    base_url: str

    # HTTP request configuration
    endpoint: str = ""
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    body: Optional[dict[str, Any]] = None
    auth: Optional[tuple[str, str]] = None
    timeout: int = 30
    verify_ssl: bool = True

    # Pagination strategy
    pagination: PaginationConfig = field(default_factory=PaginationConfig)

    # Output configuration
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    output_filename: Optional[str] = None
    save_mode: str = "single"  # "single" or "batch"
    batch_size: int = 1000

    # Retry configuration
    max_retries: int = 3
    backoff_factor: float = 0.3
    retry_status_codes: list[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )
