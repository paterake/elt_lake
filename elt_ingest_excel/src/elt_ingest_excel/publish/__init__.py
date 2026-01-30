"""Publish module for writing data to Excel workbooks."""

from .base import BaseExcelPublisher, PublishResult
from .excel_publisher_openpyxl import ExcelPublisherOpenpyxl
from .excel_publisher_xlwings import ExcelPublisherXlwings

# Default publisher (xlwings - requires Excel, preserves all features)
ExcelPublisher = ExcelPublisherXlwings

__all__ = [
    "BaseExcelPublisher",
    "PublishResult",
    "ExcelPublisher",
    "ExcelPublisherOpenpyxl",
    "ExcelPublisherXlwings",
]
