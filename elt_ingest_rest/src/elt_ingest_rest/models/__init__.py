"""Data models for REST API ingestion configuration."""

from .pagination import PaginationConfig, PaginationType
from .config import IngestConfig

__all__ = [
    "PaginationType",
    "PaginationConfig",
    "IngestConfig",
]
