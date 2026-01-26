"""JSON configuration parser for Excel ingestion."""

import json
from pathlib import Path
from typing import Union

from ..models import ExcelIngestConfig, WorkbookConfig, SheetConfig


class JsonConfigParser:
    """Parser for JSON configuration files.

    Supports loading configuration from:
    - File path (str or Path)
    - JSON string
    - Python dict/list

    JSON format:
    [
        {
            "workbookFileName": "/path/to/workbook.xlsx",
            "sheets": [
                {
                    "sheetName": "Sheet1",
                    "targetTableName": "my_table",
                    "headerRow": 1,
                    "dataRow": 2
                }
            ]
        }
    ]
    """

    @staticmethod
    def from_json(
        json_data: Union[str, Path, dict, list],
        database_path: Union[str, Path],
        create_tables: bool = True,
        replace_data: bool = True,
    ) -> ExcelIngestConfig:
        """Load configuration from JSON.

        Args:
            json_data: JSON file path, JSON string, dict, or list of workbook configs.
            database_path: Path to the DuckDB database file.
            create_tables: Whether to create tables if they don't exist.
            replace_data: Whether to replace existing data or append.

        Returns:
            ExcelIngestConfig instance.

        Raises:
            FileNotFoundError: If json_data is a path that doesn't exist.
            json.JSONDecodeError: If JSON parsing fails.
            ValueError: If configuration is invalid.
        """
        # Parse JSON data based on type
        if isinstance(json_data, Path):
            if not json_data.exists():
                raise FileNotFoundError(f"Config file not found: {json_data}")
            data = json.loads(json_data.read_text())
        elif isinstance(json_data, str):
            # Check if it's a file path or JSON string
            path = Path(json_data)
            if path.exists():
                data = json.loads(path.read_text())
            else:
                data = json.loads(json_data)
        elif isinstance(json_data, (dict, list)):
            data = json_data
        else:
            raise ValueError(f"Unsupported json_data type: {type(json_data)}")

        # Ensure data is a list
        if isinstance(data, dict):
            data = [data]

        # Parse workbook configurations
        workbooks = JsonConfigParser._parse_workbooks(data)

        # Convert database_path to Path
        db_path = Path(database_path) if isinstance(database_path, str) else database_path

        return ExcelIngestConfig(
            database_path=db_path,
            workbooks=workbooks,
            create_tables=create_tables,
            replace_data=replace_data,
        )

    @staticmethod
    def _parse_workbooks(data: list) -> list[WorkbookConfig]:
        """Parse list of workbook configurations.

        Args:
            data: List of workbook config dictionaries.

        Returns:
            List of WorkbookConfig instances.
        """
        workbooks = []
        for wb_data in data:
            if "workbookFileName" not in wb_data:
                raise ValueError("Missing required field: workbookFileName")

            sheets = JsonConfigParser._parse_sheets(wb_data.get("sheets", []))

            workbook = WorkbookConfig(
                workbook_file_name=wb_data["workbookFileName"],
                sheets=sheets,
            )
            workbooks.append(workbook)

        return workbooks

    @staticmethod
    def _parse_sheets(sheets_data: list) -> list[SheetConfig]:
        """Parse list of sheet configurations.

        Args:
            sheets_data: List of sheet config dictionaries.

        Returns:
            List of SheetConfig instances.
        """
        sheets = []
        for sheet_data in sheets_data:
            if "sheetName" not in sheet_data:
                raise ValueError("Missing required field: sheetName")
            if "targetTableName" not in sheet_data:
                raise ValueError("Missing required field: targetTableName")

            # Parse headerRow (handle string or int)
            header_row_raw = sheet_data.get("headerRow", 1)
            header_row = int(header_row_raw) if header_row_raw is not None else 1

            # Parse dataRow (handle string or int, None means default)
            data_row_raw = sheet_data.get("dataRow")
            data_row = int(data_row_raw) if data_row_raw is not None else None

            sheet = SheetConfig(
                sheet_name=sheet_data["sheetName"],
                target_table_name=sheet_data["targetTableName"],
                header_row=header_row,
                data_row=data_row,
            )
            sheets.append(sheet)

        return sheets

    @staticmethod
    def to_json(
        config: ExcelIngestConfig,
        filepath: Union[str, Path, None] = None,
    ) -> str:
        """Serialize configuration to JSON.

        Args:
            config: ExcelIngestConfig instance to serialize.
            filepath: Optional file path to write JSON to.

        Returns:
            JSON string representation.
        """
        data = []
        for workbook in config.workbooks:
            wb_data = {
                "workbookFileName": workbook.workbook_file_name,
                "sheets": [
                    {
                        "sheetName": sheet.sheet_name,
                        "targetTableName": sheet.target_table_name,
                        "headerRow": sheet.header_row,
                        "dataRow": sheet.data_row,
                    }
                    for sheet in workbook.sheets
                ],
            }
            data.append(wb_data)

        json_str = json.dumps(data, indent=2)

        if filepath:
            path = Path(filepath) if isinstance(filepath, str) else filepath
            path.write_text(json_str)

        return json_str

    @staticmethod
    def find_workbook(
        config: ExcelIngestConfig,
        file_name: str,
    ) -> WorkbookConfig | None:
        """Find a workbook configuration by file name.

        Args:
            config: ExcelIngestConfig containing workbook definitions.
            file_name: Workbook file name to match (supports ~ expansion).

        Returns:
            WorkbookConfig if found, None otherwise.
        """
        file_name_expanded = str(Path(file_name).expanduser())

        for workbook in config.workbooks:
            workbook_path_expanded = str(Path(workbook.workbook_file_name).expanduser())
            if workbook_path_expanded == file_name_expanded:
                return workbook

        return None

    @staticmethod
    def get_sheets(
        workbook: WorkbookConfig,
        sheet_filter: str = "*",
    ) -> list[SheetConfig]:
        """Get sheets from a workbook with optional filtering.

        Args:
            workbook: WorkbookConfig containing sheet definitions.
            sheet_filter: Sheet name to filter on, or "*" for all sheets.

        Returns:
            List of SheetConfig matching the filter.
        """
        if sheet_filter == "*":
            return workbook.sheets

        return [
            sheet for sheet in workbook.sheets
            if sheet.sheet_name == sheet_filter
        ]
