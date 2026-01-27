"""Main workflow module for file ingestion."""

from pathlib import Path
from typing import Union

import pandas as pd

from .loaders import ExcelReader
from .models import FileType, SheetConfig
from .parsers import JsonConfigParser
from .writers import SaveMode, DuckDBWriter, WriteResult


class FileIngestor:
    """Main file ingestion workflow.

    This class orchestrates the file ingestion process:
    1. Load configuration from JSON
    2. Find workbook by file name
    3. Filter sheets as needed
    4. Read each sheet and write to DuckDB

    Supports multiple file types (EXCEL, DELIMITED), though
    currently only EXCEL is implemented.
    """

    def __init__(
        self,
        config_path: Union[str, Path],
        data_path_name: str,
        data_file_name: str,
        database_path: Union[str, Path],
        sheet_filter: str = "*",
        save_mode: SaveMode = SaveMode.RECREATE,
    ):
        """Initialize the file ingestor.

        Args:
            config_path: Path to JSON configuration file.
            data_path_name: Path name of the data to process.
            data_file_name: File name of the data to process.
            database_path: Path to DuckDB database file.
            sheet_filter: Sheet name to filter on, or "*" for all sheets.
            save_mode: How to handle existing tables (DROP, RECREATE, OVERWRITE, APPEND).
        """
        self.config_path = Path(config_path)
        self.data_path_name = data_path_name
        self.data_file_name = data_file_name
        self.database_path = Path(database_path).expanduser()
        self.sheet_filter = sheet_filter
        self.save_mode = save_mode

        # Configure pandas display
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 50)

        # Load configuration
        self.config = JsonConfigParser.from_json(
            self.config_path,
            database_path=str(self.database_path),
        )

        # Find workbook
        self.workbook = JsonConfigParser.find_workbook(
            self.config,
            self.data_file_name,
        )

        if self.workbook is None:
            raise ValueError(f"No workbook config found for: {data_file_name}")

        # Get sheets (filtered)
        self.sheets = JsonConfigParser.get_sheets(self.workbook, self.sheet_filter)

        # Store results
        self.results: list[WriteResult] = []

    def process(self) -> list[WriteResult]:
        """Process all sheets in the workbook.

        For EXCEL files, reads each sheet and writes to DuckDB.
        Other file types will be supported in future versions.

        Returns:
            List of WriteResult objects for each sheet processed.
        """
        print(f"Loaded config for: {self.workbook.workbook_file_name}")
        print(f"File type: {self.workbook.file_type.value}")
        print(f"Database: {self.database_path}")
        print(f"Save mode: {self.save_mode.value}")
        print(f"Processing {len(self.sheets)} sheet(s)")

        self.results = []

        with DuckDBWriter(self.database_path) as writer:
            for sheet_config in self.sheets:
                result = self._process_sheet(sheet_config, writer)
                if result:
                    self.results.append(result)

        self._print_summary()
        return self.results

    def _process_sheet(
        self,
        sheet_config: SheetConfig,
        writer: DuckDBWriter,
    ) -> WriteResult | None:
        """Process a single sheet.

        Args:
            sheet_config: Configuration for the sheet to process.
            writer: DuckDBWriter instance for database operations.

        Returns:
            WriteResult if data was written, None otherwise.
        """
        print(f"\n{'='*60}")
        print(f"Sheet: {sheet_config.sheet_name}")
        print(f"  Target table: {sheet_config.target_table_name}")
        print(f"  Header row: {sheet_config.header_row}")
        print(f"  Data row: {sheet_config.data_row}")
        print(f"{'='*60}")

        if self.workbook.file_type == FileType.EXCEL:
            return self._process_excel_sheet(sheet_config, writer)
        elif self.workbook.file_type == FileType.DELIMITED:
            return self._process_delimited_file(sheet_config, writer)
        else:
            raise ValueError(f"Unsupported file type: {self.workbook.file_type}")

    def _process_excel_sheet(
        self,
        sheet_config: SheetConfig,
        writer: DuckDBWriter,
    ) -> WriteResult:
        """Process an Excel sheet.

        Args:
            sheet_config: Configuration for the sheet to process.
            writer: DuckDBWriter instance for database operations.

        Returns:
            WriteResult with details of the write operation.
        """
        reader = ExcelReader(
            file_path=Path(self.data_path_name) / self.data_file_name,
            sheet_name=sheet_config.sheet_name,
            header_row=sheet_config.header_row - 1,  # pandas uses 0-indexed
            dtype=str,
        )
        df = reader.load()

        # Preview the data
        reader.preview()

        if not df.empty:
            print(f"\nFirst row as dict:")
            print(df.iloc[0].to_dict())

        print(f"\nTotal rows read: {len(df)}")

        # Write to DuckDB
        result = writer.write(df, sheet_config.target_table_name, self.save_mode)

        print(f"Rows written: {result.rows_written}")
        print(f"Table row count: {result.row_count}")

        return result

    def _process_delimited_file(
        self,
        sheet_config: SheetConfig,
        writer: DuckDBWriter,
    ) -> WriteResult:
        """Process a delimited file (CSV, TSV, etc.).

        Args:
            sheet_config: Configuration for the file to process.
            writer: DuckDBWriter instance for database operations.

        Returns:
            WriteResult with details of the write operation.

        Note:
            Not yet implemented. Will be added in future version.
        """
        raise NotImplementedError("DELIMITED file type not yet supported")

    def _print_summary(self) -> None:
        """Print a summary of the ingestion results."""
        print("\n" + "=" * 60)
        print("INGESTION SUMMARY")
        print("=" * 60)

        total_rows = 0
        for result in self.results:
            print(f"\n  Table: {result.table_name}")
            print(f"    Save mode: {result.save_mode.value}")
            print(f"    Rows written: {result.rows_written}")
            print(f"    Table count: {result.row_count}")

            if result.rows_written != result.row_count and result.save_mode != SaveMode.APPEND:
                print(f"    WARNING: Row count mismatch!")

            total_rows += result.row_count

        print("\n" + "-" * 60)
        print(f"Total tables processed: {len(self.results)}")
        print(f"Total rows: {total_rows}")
        print("=" * 60 + "\n")
