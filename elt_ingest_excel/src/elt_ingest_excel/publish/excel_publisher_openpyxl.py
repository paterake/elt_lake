"""Excel publisher using openpyxl for writing DuckDB data to Excel workbooks.

Note: openpyxl may not fully preserve drawing shapes in .xlsm files.
Use ExcelPublisherXlwings if you need to preserve all Excel features.
"""

import shutil
from pathlib import Path
from typing import Union

import duckdb
from openpyxl import load_workbook

from ..models import PublishConfig, PublishWorkbookConfig, PublishSheetConfig
from .base import PublishResult


class ExcelPublisherOpenpyxl:
    """Publisher for writing DuckDB data to Excel workbooks.

    This class handles:
    1. Cloning a template workbook to target location
    2. Querying DuckDB tables for data
    3. Writing data to specific sheets in the workbook
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

        # Clone the template
        print(f"  Cloning template to target...")
        shutil.copy2(src_path, tgt_path)

        # Open the target workbook
        wb = load_workbook(tgt_path, keep_vba=True)  # keep_vba for .xlsm files

        try:
            # Process each sheet
            for sheet_config in workbook_config.sheets:
                result = self._publish_sheet(wb, sheet_config)
                results.append(result)

            # Save the workbook
            print(f"  Saving workbook...")
            wb.save(tgt_path)
            print(f"  Workbook saved: {tgt_path}")

        finally:
            wb.close()

        return results

    def _publish_sheet(
        self,
        workbook,
        sheet_config: PublishSheetConfig,
    ) -> PublishResult:
        """Publish data to a single sheet.

        Args:
            workbook: openpyxl Workbook object.
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
            if sheet_name not in workbook.sheetnames:
                error = f"Sheet '{sheet_name}' not found in workbook"
                print(f"    ERROR: {error}")
                return PublishResult(
                    sheet_name=sheet_name,
                    table_name=table_name,
                    rows_written=0,
                    success=False,
                    error=error,
                )

            ws = workbook[sheet_name]

            # Query DuckDB table
            query = f"SELECT * FROM {table_name}"
            result = self.connection.execute(query)
            rows = result.fetchall()

            print(f"    Rows from table: {len(rows)}")

            # Write data to sheet starting at data_row
            for row_idx, row_data in enumerate(rows):
                excel_row = data_row + row_idx
                for col_idx, value in enumerate(row_data):
                    col = col_idx + 1  # Excel columns are 1-indexed
                    ws.cell(row=excel_row, column=col, value=value)

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
