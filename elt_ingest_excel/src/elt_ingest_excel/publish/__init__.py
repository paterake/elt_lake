"""Publish module for writing data to Excel workbooks."""

from .base import PublishResult
from .excel_publisher_openpyxl import ExcelPublisherOpenpyxl
from .excel_publisher_xlwings import ExcelPublisherXlwings

# Default publisher (xlwings - requires Excel, preserves all features)
ExcelPublisher = ExcelPublisherXlwings

__all__ = [
    "PublishResult",
    "ExcelPublisher",
    "ExcelPublisherOpenpyxl",
    "ExcelPublisherXlwings",
]
