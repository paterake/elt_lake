"""Excel publisher using xlwings for writing DuckDB data to Excel workbooks.

This implementation uses xlwings which controls Excel directly via COM (Windows)
or AppleScript (Mac). This preserves all Excel features including:
- Drawing shapes
- VBA macros
- Charts
- Formatting

Requires Excel to be installed on the machine.
"""

import shutil
from pathlib import Path
from typing import Union

import duckdb
import xlwings as xw

from ..models import PublishConfig, PublishWorkbookConfig, PublishSheetConfig
from .base import PublishResult


class ExcelPublisherXlwings:
    """Publisher for writing DuckDB data to Excel workbooks using xlwings.

    This class handles:
    1. Cloning a template workbook to target location
    2. Querying DuckDB tables for data
    3. Writing data to specific sheets in the workbook

    Uses xlwings to control Excel directly, preserving all features.
    """

    def __init__(
        self,
        database_path: Union[str, Path],
    ):
        """Initialize the publisher.

        Args:
            database_path: Path to the DuckDB database file.
        """
        self.database_path = Path(database_path).expanduser()
        self.connection: duckdb.DuckDBPyConnection | None = None

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

        print(f"\n  Source template: {src_path}")
        print(f"  Target workbook: {tgt_path}")

        # Delete existing target if it exists
        if tgt_path.exists():
            print(f"  Deleting existing target: {tgt_path}")
            tgt_path.unlink()

        # Clone the template (preserves everything at filesystem level)
        print(f"  Cloning template to target...")
        shutil.copy2(src_path, tgt_path)

        # Open Excel in background (not visible)
        app = xw.App(visible=False)

        try:
            # Open the target workbook
            wb = app.books.open(str(tgt_path))

            try:
                # Process each sheet
                for sheet_config in workbook_config.sheets:
                    result = self._publish_sheet(wb, sheet_config)
                    results.append(result)

                # Save the workbook
                print(f"  Saving workbook...")
                wb.save()
                print(f"  Workbook saved: {tgt_path}")

            finally:
                wb.close()

        finally:
            app.quit()

        return results

    def _publish_sheet(
        self,
        workbook,
        sheet_config: PublishSheetConfig,
    ) -> PublishResult:
        """Publish data to a single sheet.

        Args:
            workbook: xlwings Book object.
            sheet_config: Configuration for the sheet.

        Returns:
            PublishResult with details of the operation.
        """
        sheet_name = sheet_config.sheet_name
        table_name = sheet_config.src_table_name
        data_row = sheet_config.data_row

        print(f"\n    Sheet: {sheet_name}")
        print(f"    Source table: {table_name}")

        try:
            # Check if sheet exists
            sheet_names = [s.name for s in workbook.sheets]
            if sheet_name not in sheet_names:
                error = f"Sheet '{sheet_name}' not found in workbook"
                print(f"    ERROR: {error}")
                return PublishResult(
                    sheet_name=sheet_name,
                    table_name=table_name,
                    rows_written=0,
                    success=False,
                    error=error,
                )

            ws = workbook.sheets[sheet_name]

            # Query DuckDB table
            query = f"SELECT * FROM {table_name}"
            result = self.connection.execute(query)
            rows = result.fetchall()

            print(f"    Rows from table: {len(rows)}")

            if rows:
                # Write all data at once using xlwings range
                # xlwings uses 1-indexed rows/columns
                ws.range((data_row, 1)).value = rows

            print(f"    Rows written: {len(rows)}")

            return PublishResult(
                sheet_name=sheet_name,
                table_name=table_name,
                rows_written=len(rows),
                success=True,
            )

        except Exception as e:
            error = str(e)
            print(f"    ERROR: {error}")
            return PublishResult(
                sheet_name=sheet_name,
                table_name=table_name,
                rows_written=0,
                success=False,
                error=error,
            )
