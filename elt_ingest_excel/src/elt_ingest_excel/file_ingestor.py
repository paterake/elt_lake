"""Main workflow module for file ingestion."""

from pathlib import Path
from typing import Union

import pandas as pd

from .loaders import ExcelReader
from .models import FileType, SheetConfig, WorkbookConfig
from .parsers import JsonConfigParser


class FileIngestor:
    """Main file ingestion workflow.

    This class orchestrates the file ingestion process:
    1. Load configuration from JSON
    2. Find workbook by file name
    3. Filter sheets as needed
    4. Process each sheet (currently just preview)

    Supports multiple file types (EXCEL, DELIMITED), though
    currently only EXCEL is implemented.
    """

    def __init__(
        self,
        config_path: Union[str, Path],
        workbook_file_name: str,
        sheet_filter: str = "*",
        database_path: str = "/tmp/unused.duckdb",
    ):
        """Initialize the file ingestor.

        Args:
            config_path: Path to JSON configuration file.
            workbook_file_name: File name of the workbook to process.
            sheet_filter: Sheet name to filter on, or "*" for all sheets.
            database_path: Path to DuckDB database (placeholder for now).
        """
        self.config_path = Path(config_path)
        self.workbook_file_name = workbook_file_name
        self.sheet_filter = sheet_filter
        self.database_path = database_path

        # Configure pandas display
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 50)

        # Load configuration
        self.config = JsonConfigParser.from_json(
            self.config_path,
            database_path=self.database_path,
        )

        # Find workbook
        self.workbook = JsonConfigParser.find_workbook(
            self.config,
            self.workbook_file_name,
        )

        if self.workbook is None:
            raise ValueError(f"No workbook config found for: {workbook_file_name}")

        # Get sheets (filtered)
        self.sheets = JsonConfigParser.get_sheets(self.workbook, self.sheet_filter)

    def process(self) -> None:
        """Process all sheets in the workbook.

        For EXCEL files, reads each sheet and calls preview().
        Other file types will be supported in future versions.
        """
        print(f"Loaded config for: {self.workbook.workbook_file_name}")
        print(f"File type: {self.workbook.file_type.value}")
        print(f"Processing {len(self.sheets)} sheet(s)")

        for sheet_config in self.sheets:
            self._process_sheet(sheet_config)

    def _process_sheet(self, sheet_config: SheetConfig) -> None:
        """Process a single sheet.

        Args:
            sheet_config: Configuration for the sheet to process.
        """
        print(f"\n{'='*60}")
        print(f"Sheet: {sheet_config.sheet_name}")
        print(f"  Target table: {sheet_config.target_table_name}")
        print(f"  Header row: {sheet_config.header_row}")
        print(f"  Data row: {sheet_config.data_row}")
        print(f"{'='*60}")

        if self.workbook.file_type == FileType.EXCEL:
            self._process_excel_sheet(sheet_config)
        elif self.workbook.file_type == FileType.DELIMITED:
            self._process_delimited_file(sheet_config)
        else:
            raise ValueError(f"Unsupported file type: {self.workbook.file_type}")

    def _process_excel_sheet(self, sheet_config: SheetConfig) -> None:
        """Process an Excel sheet.

        Args:
            sheet_config: Configuration for the sheet to process.
        """
        reader = ExcelReader(
            file_path=self.workbook.workbook_file_name,
            sheet_name=sheet_config.sheet_name,
            header_row=sheet_config.header_row - 1,  # pandas uses 0-indexed
            dtype=str,
        )
        df = reader.load()
        reader.preview()

        print(f"\nFirst row as dict:")
        print(df.iloc[0].to_dict())
        print(f"\nTotal rows: {len(df)}")

    def _process_delimited_file(self, sheet_config: SheetConfig) -> None:
        """Process a delimited file (CSV, TSV, etc.).

        Args:
            sheet_config: Configuration for the file to process.

        Note:
            Not yet implemented. Will be added in future version.
        """
        raise NotImplementedError("DELIMITED file type not yet supported")
