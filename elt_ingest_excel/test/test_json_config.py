"""Tests for JSON configuration parsing."""

import json
import tempfile
from pathlib import Path

import pytest

from elt_ingest_excel import (
    JsonConfigParser,
    ExcelIngestConfig,
    WorkbookConfig,
    SheetConfig,
)


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestJsonConfigParser:
    """Tests for JsonConfigParser."""

    def test_from_json_file_single_workbook(self):
        """Test loading config from a JSON file with single workbook."""
        config = JsonConfigParser.from_json(
            FIXTURES_DIR / "single_workbook.json",
            database_path="/path/to/db.duckdb",
        )

        assert isinstance(config, ExcelIngestConfig)
        assert config.database_path == Path("/path/to/db.duckdb")
        assert len(config.workbooks) == 1
        assert config.workbooks[0].workbook_file_name == "/path/to/workbook.xlsx"
        assert len(config.workbooks[0].sheets) == 1
        assert config.workbooks[0].sheets[0].sheet_name == "Sheet1"
        assert config.workbooks[0].sheets[0].target_table_name == "table1"

    def test_from_json_file_multiple_workbooks(self):
        """Test loading config from a JSON file with multiple workbooks."""
        config = JsonConfigParser.from_json(
            FIXTURES_DIR / "multiple_workbooks.json",
            database_path="/path/to/db.duckdb",
        )

        assert len(config.workbooks) == 2
        assert config.workbooks[0].workbook_file_name == "/path/to/workbook1.xlsx"
        assert config.workbooks[1].workbook_file_name == "/path/to/workbook2.xlsx"

    def test_from_json_string_path(self):
        """Test loading config using string path."""
        config = JsonConfigParser.from_json(
            str(FIXTURES_DIR / "single_workbook.json"),
            database_path="/path/to/db.duckdb",
        )

        assert len(config.workbooks) == 1
        assert config.workbooks[0].workbook_file_name == "/path/to/workbook.xlsx"

    def test_sheet_optional_fields_defaults(self):
        """Test that sheet optional fields have correct defaults."""
        config = JsonConfigParser.from_json(
            FIXTURES_DIR / "single_workbook.json",
            database_path="/path/to/db.duckdb",
        )

        sheet = config.workbooks[0].sheets[0]
        assert sheet.header_row == 1
        assert sheet.skip_rows == 0

    def test_sheet_custom_header_row(self):
        """Test loading sheet with custom header row settings."""
        config = JsonConfigParser.from_json(
            FIXTURES_DIR / "custom_header_row.json",
            database_path="/path/to/db.duckdb",
        )

        sheet = config.workbooks[0].sheets[0]
        assert sheet.header_row == 3
        assert sheet.skip_rows == 2

    def test_config_defaults(self):
        """Test that config has correct default values."""
        config = JsonConfigParser.from_json(
            FIXTURES_DIR / "single_workbook.json",
            database_path="/path/to/db.duckdb",
        )

        assert config.create_tables is True
        assert config.replace_data is True

    def test_config_custom_flags(self):
        """Test setting custom create_tables and replace_data flags."""
        config = JsonConfigParser.from_json(
            FIXTURES_DIR / "single_workbook.json",
            database_path="/path/to/db.duckdb",
            create_tables=False,
            replace_data=False,
        )

        assert config.create_tables is False
        assert config.replace_data is False

    def test_to_json(self):
        """Test serializing config to JSON."""
        config = ExcelIngestConfig(
            database_path=Path("/path/to/db.duckdb"),
            workbooks=[
                WorkbookConfig(
                    workbook_file_name="/path/to/workbook.xlsx",
                    sheets=[
                        SheetConfig(
                            sheet_name="Sheet1",
                            target_table_name="table1",
                            header_row=2,
                            skip_rows=1,
                        )
                    ],
                )
            ],
        )

        json_str = JsonConfigParser.to_json(config)
        data = json.loads(json_str)

        assert len(data) == 1
        assert data[0]["workbookFileName"] == "/path/to/workbook.xlsx"
        assert data[0]["sheets"][0]["sheetName"] == "Sheet1"
        assert data[0]["sheets"][0]["targetTableName"] == "table1"
        assert data[0]["sheets"][0]["headerRow"] == 2
        assert data[0]["sheets"][0]["skipRows"] == 1

    def test_to_json_file(self):
        """Test serializing config to a JSON file."""
        config = ExcelIngestConfig(
            database_path=Path("/path/to/db.duckdb"),
            workbooks=[
                WorkbookConfig(
                    workbook_file_name="/path/to/workbook.xlsx",
                    sheets=[
                        SheetConfig(
                            sheet_name="Sheet1",
                            target_table_name="table1",
                        )
                    ],
                )
            ],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            JsonConfigParser.to_json(config, filepath=temp_path)

            # Read back and verify
            with open(temp_path) as f:
                data = json.load(f)

            assert len(data) == 1
            assert data[0]["workbookFileName"] == "/path/to/workbook.xlsx"
        finally:
            Path(temp_path).unlink()

    def test_roundtrip_json(self):
        """Test that config can be serialized and deserialized."""
        # Load original config
        original_config = JsonConfigParser.from_json(
            FIXTURES_DIR / "custom_header_row.json",
            database_path="/path/to/db.duckdb",
        )

        # Serialize to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            JsonConfigParser.to_json(original_config, filepath=temp_path)

            # Deserialize back
            reloaded_config = JsonConfigParser.from_json(
                temp_path,
                database_path="/path/to/db.duckdb",
            )

            # Verify roundtrip
            assert len(reloaded_config.workbooks) == len(original_config.workbooks)
            assert (
                reloaded_config.workbooks[0].workbook_file_name
                == original_config.workbooks[0].workbook_file_name
            )
            assert (
                reloaded_config.workbooks[0].sheets[0].header_row
                == original_config.workbooks[0].sheets[0].header_row
            )
        finally:
            Path(temp_path).unlink()

    def test_missing_workbook_filename(self):
        """Test error when workbookFileName is missing."""
        with pytest.raises(ValueError, match="Missing required field: workbookFileName"):
            JsonConfigParser.from_json(
                FIXTURES_DIR / "missing_workbook_filename.json",
                database_path="/path/to/db.duckdb",
            )

    def test_missing_sheet_name(self):
        """Test error when sheetName is missing."""
        with pytest.raises(ValueError, match="Missing required field: sheetName"):
            JsonConfigParser.from_json(
                FIXTURES_DIR / "missing_sheet_name.json",
                database_path="/path/to/db.duckdb",
            )

    def test_missing_target_table_name(self):
        """Test error when targetTableName is missing."""
        with pytest.raises(ValueError, match="Missing required field: targetTableName"):
            JsonConfigParser.from_json(
                FIXTURES_DIR / "missing_target_table_name.json",
                database_path="/path/to/db.duckdb",
            )

    def test_file_not_found(self):
        """Test error when config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            JsonConfigParser.from_json(
                Path("/nonexistent/config.json"),
                database_path="/path/to/db.duckdb",
            )

    def test_invalid_json_file(self):
        """Test error when JSON file contains invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                JsonConfigParser.from_json(
                    temp_path,
                    database_path="/path/to/db.duckdb",
                )
        finally:
            Path(temp_path).unlink()
