"""Base classes and types for Excel publishers."""

import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

import duckdb

from ..models import PublishConfig, PublishWorkbookConfig, PublishSheetConfig

if TYPE_CHECKING:
    from ..reporting import PipelineReporter


@dataclass
class PublishResult:
    """Result of publishing data to a sheet.

    Attributes:
        sheet_name: Name of the sheet written to.
        table_name: Source DuckDB table.
        rows_written: Number of rows written.
        success: Whether the publish succeeded.
        error: Error message if failed, None otherwise.
    """
    sheet_name: str
    table_name: str
    rows_written: int
    success: bool
    error: str | None = None


class BaseExcelPublisher(ABC):
    """Base class for Excel publishers.

    Handles common operations:
    - DuckDB connection management
    - Workbook cloning
    - Query execution
    - Result creation

    Subclasses implement library-specific workbook and sheet operations.
    """

    def __init__(
        self,
        database_path: Union[str, Path],
        reporter: "PipelineReporter | None" = None,
    ):
        """Initialize the publisher.

        Args:
            database_path: Path to the DuckDB database file.
            reporter: Optional reporter for output messages.
        """
        self.database_path = Path(database_path).expanduser()
        self.connection: duckdb.DuckDBPyConnection | None = None
        self.reporter = reporter

    def __enter__(self):
        """Context manager entry."""
        self.connection = duckdb.connect(str(self.database_path), read_only=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def publish(
        self,
        config: PublishConfig,
    ) -> list[PublishResult]:
        """Publish data to all configured workbooks.

        Args:
            config: PublishConfig with workbook configurations.

        Returns:
            List of PublishResult for each sheet processed.
        """
        all_results = []

        for workbook_config in config.workbooks:
            results = self._publish_workbook(workbook_config)
            all_results.extend(results)

        return all_results

    def _publish_workbook(
        self,
        workbook_config: PublishWorkbookConfig,
    ) -> list[PublishResult]:
        """Publish data to a single workbook.

        Args:
            workbook_config: Configuration for the workbook.

        Returns:
            List of PublishResult for each sheet processed.
        """
        results = []

        # Clone template workbook to target
        src_path = workbook_config.src_workbook_full_path
        tgt_path = workbook_config.tgt_workbook_full_path

        if self.reporter:
            self.reporter.print_workbook_source(src_path)
            self.reporter.print_workbook_target(tgt_path)

        # Delete existing target if it exists
        if tgt_path.exists():
            if self.reporter:
                self.reporter.print_workbook_deleting_existing(tgt_path)
            tgt_path.unlink()

        # Clone the template
        if self.reporter:
            self.reporter.print_workbook_cloning()
        shutil.copy2(src_path, tgt_path)

        # Open and process workbook using library-specific implementation
        results = self._open_and_process_workbook(workbook_config, tgt_path)

        return results

    @abstractmethod
    def _open_and_process_workbook(
        self,
        workbook_config: PublishWorkbookConfig,
        tgt_path: Path,
    ) -> list[PublishResult]:
        """Open workbook and process all sheets.

        Library-specific implementation for opening the workbook,
        processing sheets, and saving.

        Args:
            workbook_config: Configuration for the workbook.
            tgt_path: Path to the target workbook file.

        Returns:
            List of PublishResult for each sheet processed.
        """
        pass

    def _process_sheets(
        self,
        workbook: Any,
        workbook_config: PublishWorkbookConfig,
    ) -> list[PublishResult]:
        """Process all sheets in the workbook.

        Args:
            workbook: Library-specific workbook object.
            workbook_config: Configuration for the workbook.

        Returns:
            List of PublishResult for each sheet processed.
        """
        results = []
        for sheet_config in workbook_config.sheets:
            result = self._publish_sheet(workbook, sheet_config)
            results.append(result)
        return results

    def _publish_sheet(
        self,
        workbook: Any,
        sheet_config: PublishSheetConfig,
    ) -> PublishResult:
        """Publish data to a single sheet.

        Args:
            workbook: Library-specific workbook object.
            sheet_config: Configuration for the sheet.

        Returns:
            PublishResult with details of the operation.
        """
        sheet_name = sheet_config.sheet_name
        table_name = sheet_config.src_table_name
        data_row = sheet_config.data_row

        if self.reporter:
            self.reporter.print_publish_sheet_start(sheet_name, table_name)

        try:
            # Check if sheet exists
            if not self._sheet_exists(workbook, sheet_name):
                error = f"Sheet '{sheet_name}' not found in workbook"
                if self.reporter:
                    self.reporter.print_publish_sheet_error(error)
                return PublishResult(
                    sheet_name=sheet_name,
                    table_name=table_name,
                    rows_written=0,
                    success=False,
                    error=error,
                )

            # Get the sheet
            ws = self._get_sheet(workbook, sheet_name)

            # Query DuckDB table
            query = f"SELECT * FROM {table_name}"
            result = self.connection.execute(query)
            rows = result.fetchall()

            if self.reporter:
                self.reporter.print_publish_rows_from_table(len(rows))

            # Write data using library-specific implementation
            self._write_data_to_sheet(ws, rows, data_row)

            if self.reporter:
                self.reporter.print_publish_rows_written(len(rows))

            return PublishResult(
                sheet_name=sheet_name,
                table_name=table_name,
                rows_written=len(rows),
                success=True,
            )

        except Exception as e:
            error = str(e)
            if self.reporter:
                self.reporter.print_publish_sheet_error(error)
            return PublishResult(
                sheet_name=sheet_name,
                table_name=table_name,
                rows_written=0,
                success=False,
                error=error,
            )

    @abstractmethod
    def _sheet_exists(self, workbook: Any, sheet_name: str) -> bool:
        """Check if a sheet exists in the workbook.

        Args:
            workbook: Library-specific workbook object.
            sheet_name: Name of the sheet to check.

        Returns:
            True if sheet exists, False otherwise.
        """
        pass

    @abstractmethod
    def _get_sheet(self, workbook: Any, sheet_name: str) -> Any:
        """Get a sheet from the workbook.

        Args:
            workbook: Library-specific workbook object.
            sheet_name: Name of the sheet to get.

        Returns:
            Library-specific sheet object.
        """
        pass

    @abstractmethod
    def _write_data_to_sheet(
        self,
        sheet: Any,
        rows: list[tuple],
        start_row: int,
    ) -> None:
        """Write data to the sheet.

        Args:
            sheet: Library-specific sheet object.
            rows: Data rows to write.
            start_row: Starting row number (1-indexed).
        """
        pass

    def _report_saving(self, tgt_path: Path) -> None:
        """Report that workbook is being saved.

        Args:
            tgt_path: Path to the target workbook.
        """
        if self.reporter:
            self.reporter.print_workbook_saving()

    def _report_saved(self, tgt_path: Path) -> None:
        """Report that workbook was saved.

        Args:
            tgt_path: Path to the target workbook.
        """
        if self.reporter:
            self.reporter.print_workbook_saved(tgt_path)
