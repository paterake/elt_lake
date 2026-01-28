"""JSON configuration parser for publish/output configuration."""

import json
from pathlib import Path
from typing import Union

from ..models import PublishConfig, PublishWorkbookConfig, PublishSheetConfig


class PublishConfigParser:
    """Parser for publish JSON configuration files.

    JSON format:
    [
        {
            "srcWorkbookPathName": "/path/to/templates",
            "srcWorkbookFileName": "template.xlsm",
            "tgtWorkbookPathName": "/path/to/output",
            "tgtWorkbookFileName": "output_name",
            "sheets": [
                {
                    "srcTableName": "table_name",
                    "sheetName": "Sheet Name",
                    "headerRow": "3",
                    "dataRow": "4"
                }
            ]
        }
    ]
    """

    @staticmethod
    def from_json(
        json_data: Union[str, Path, dict, list],
    ) -> PublishConfig:
        """Load publish configuration from JSON.

        Args:
            json_data: JSON file path, JSON string, dict, or list of workbook configs.

        Returns:
            PublishConfig instance.

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
        workbooks = PublishConfigParser._parse_workbooks(data)

        return PublishConfig(workbooks=workbooks)

    @staticmethod
    def _parse_workbooks(data: list) -> list[PublishWorkbookConfig]:
        """Parse list of publish workbook configurations.

        Args:
            data: List of workbook config dictionaries.

        Returns:
            List of PublishWorkbookConfig instances.
        """
        workbooks = []
        for wb_data in data:
            required_fields = [
                "srcWorkbookPathName",
                "srcWorkbookFileName",
                "tgtWorkbookPathName",
                "tgtWorkbookFileName",
            ]
            for field in required_fields:
                if field not in wb_data:
                    raise ValueError(f"Missing required field: {field}")

            sheets = PublishConfigParser._parse_sheets(wb_data.get("sheets", []))

            workbook = PublishWorkbookConfig(
                src_workbook_path=wb_data["srcWorkbookPathName"],
                src_workbook_file_name=wb_data["srcWorkbookFileName"],
                tgt_workbook_path=wb_data["tgtWorkbookPathName"],
                tgt_workbook_file_name=wb_data["tgtWorkbookFileName"],
                sheets=sheets,
            )
            workbooks.append(workbook)

        return workbooks

    @staticmethod
    def _parse_sheets(sheets_data: list) -> list[PublishSheetConfig]:
        """Parse list of publish sheet configurations.

        Args:
            sheets_data: List of sheet config dictionaries.

        Returns:
            List of PublishSheetConfig instances.
        """
        sheets = []
        for sheet_data in sheets_data:
            if "srcTableName" not in sheet_data:
                raise ValueError("Missing required field: srcTableName")
            if "sheetName" not in sheet_data:
                raise ValueError("Missing required field: sheetName")

            # Parse headerRow (handle string or int)
            header_row_raw = sheet_data.get("headerRow", 1)
            header_row = int(header_row_raw) if header_row_raw is not None else 1

            # Parse dataRow (handle string or int)
            data_row_raw = sheet_data.get("dataRow", 2)
            data_row = int(data_row_raw) if data_row_raw is not None else 2

            sheet = PublishSheetConfig(
                src_table_name=sheet_data["srcTableName"],
                sheet_name=sheet_data["sheetName"],
                header_row=header_row,
                data_row=data_row,
            )
            sheets.append(sheet)

        return sheets
