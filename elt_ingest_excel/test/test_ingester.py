"""Tests for Excel ingestion into DuckDB."""

import json
import tempfile
from pathlib import Path

import duckdb
import pytest
from openpyxl import Workbook

from elt_ingest_excel import (
    ExcelIngester,
    JsonConfigParser,
    ExcelLoader,
    SheetConfig,
)


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_config_with_substitution(
    fixture_name: str,
    database_path: str,
    workbook_path: str | None = None,
) -> dict:
    """Load a JSON fixture file and substitute placeholder values.

    Args:
        fixture_name: Name of the fixture file (without .json extension).
        database_path: Path to the DuckDB database.
        workbook_path: Path to the Excel workbook (substitutes ${WORKBOOK_PATH}).

    Returns:
        ExcelIngestConfig loaded from the fixture with substitutions applied.
    """
    fixture_path = FIXTURES_DIR / f"{fixture_name}.json"
    content = fixture_path.read_text()

    # Substitute placeholders
    if workbook_path:
        content = content.replace("${WORKBOOK_PATH}", workbook_path)

    config_data = json.loads(content)

    return JsonConfigParser.from_json(
        config_data,
        database_path=database_path,
    )


@pytest.fixture
def sample_workbook():
    """Create a sample Excel workbook for testing."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        workbook_path = f.name

    wb = Workbook()

    # Sheet1 - simple data
    ws1 = wb.active
    ws1.title = "Sheet1"
    ws1["A1"] = "Name"
    ws1["B1"] = "Age"
    ws1["C1"] = "City"
    ws1["A2"] = "Alice"
    ws1["B2"] = 30
    ws1["C2"] = "New York"
    ws1["A3"] = "Bob"
    ws1["B3"] = 25
    ws1["C3"] = "Los Angeles"
    ws1["A4"] = "Charlie"
    ws1["B4"] = 35
    ws1["C4"] = "Chicago"

    # Sheet2 - different data
    ws2 = wb.create_sheet("Sheet2")
    ws2["A1"] = "Product"
    ws2["B1"] = "Price"
    ws2["C1"] = "Quantity"
    ws2["A2"] = "Widget"
    ws2["B2"] = 9.99
    ws2["C2"] = 100
    ws2["A3"] = "Gadget"
    ws2["B3"] = 19.99
    ws2["C3"] = 50

    # Sheet3 - with header on row 3
    ws3 = wb.create_sheet("Sheet3")
    ws3["A1"] = "Report Title"
    ws3["A2"] = "Generated: 2024-01-01"
    ws3["A3"] = "ID"
    ws3["B3"] = "Value"
    ws3["A4"] = 1
    ws3["B4"] = 100
    ws3["A5"] = 2
    ws3["B5"] = 200

    wb.save(workbook_path)
    wb.close()

    yield workbook_path

    # Cleanup
    Path(workbook_path).unlink(missing_ok=True)


@pytest.fixture
def temp_database():
    """Create a temporary DuckDB database path."""
    # Use a temp directory and generate a path (don't create the file)
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.duckdb"

    yield str(db_path)

    # Cleanup
    db_path.unlink(missing_ok=True)
    Path(temp_dir).rmdir()


class TestExcelLoader:
    """Tests for ExcelLoader."""

    def test_load_simple_sheet(self, sample_workbook):
        """Test loading a simple sheet."""
        config = load_config_with_substitution(
            "ingest_single_sheet",
            database_path="/tmp/test.duckdb",
            workbook_path=sample_workbook,
        )
        sheet_config = config.workbooks[0].sheets[0]

        with ExcelLoader(sample_workbook) as loader:
            data = loader.load_sheet(sheet_config)

        assert len(data) == 3
        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == 30
        assert data[0]["city"] == "New York"
        assert data[2]["name"] == "Charlie"

    def test_load_sheet_with_custom_header(self, sample_workbook):
        """Test loading a sheet with custom header row."""
        config = load_config_with_substitution(
            "ingest_custom_header",
            database_path="/tmp/test.duckdb",
            workbook_path=sample_workbook,
        )
        sheet_config = config.workbooks[0].sheets[0]

        with ExcelLoader(sample_workbook) as loader:
            data = loader.load_sheet(sheet_config)

        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[0]["value"] == 100
        assert data[1]["id"] == 2
        assert data[1]["value"] == 200

    def test_get_sheet_names(self, sample_workbook):
        """Test getting sheet names from workbook."""
        with ExcelLoader(sample_workbook) as loader:
            names = loader.get_sheet_names()

        assert "Sheet1" in names
        assert "Sheet2" in names
        assert "Sheet3" in names

    def test_sheet_not_found(self, sample_workbook):
        """Test error when sheet doesn't exist."""
        sheet_config = SheetConfig(
            sheet_name="NonexistentSheet",
            target_table_name="test_table",
        )

        with pytest.raises(ValueError, match="Sheet 'NonexistentSheet' not found"):
            with ExcelLoader(sample_workbook) as loader:
                loader.load_sheet(sheet_config)

    def test_workbook_not_found(self):
        """Test error when workbook doesn't exist."""
        with pytest.raises(FileNotFoundError):
            ExcelLoader("/nonexistent/workbook.xlsx")


class TestExcelIngester:
    """Tests for ExcelIngester."""

    def test_ingest_single_sheet(self, sample_workbook, temp_database):
        """Test ingesting a single sheet."""
        config = load_config_with_substitution(
            "ingest_single_sheet",
            database_path=temp_database,
            workbook_path=sample_workbook,
        )

        with ExcelIngester(config) as ingester:
            results = ingester.ingest()

        assert len(results) == 1
        assert results[0].table_name == "people"
        assert results[0].rows_loaded == 3
        assert results[0].row_count == 3

        # Verify data in DuckDB
        conn = duckdb.connect(temp_database)
        data = conn.execute("SELECT * FROM people ORDER BY name").fetchall()
        conn.close()

        assert len(data) == 3
        assert data[0][0] == "Alice"  # name column

    def test_ingest_multiple_sheets(self, sample_workbook, temp_database):
        """Test ingesting multiple sheets from one workbook."""
        config = load_config_with_substitution(
            "ingest_multiple_sheets",
            database_path=temp_database,
            workbook_path=sample_workbook,
        )

        with ExcelIngester(config) as ingester:
            results = ingester.ingest()

        assert len(results) == 2
        assert results[0].table_name == "people"
        assert results[0].row_count == 3
        assert results[1].table_name == "products"
        assert results[1].row_count == 2

    def test_ingest_from_json_config(self, sample_workbook, temp_database):
        """Test ingesting using JSON configuration file."""
        config = load_config_with_substitution(
            "ingest_multiple_sheets",
            database_path=temp_database,
            workbook_path=sample_workbook,
        )

        with ExcelIngester(config) as ingester:
            results = ingester.ingest()

        assert len(results) == 2

        # Verify both tables exist and have correct data
        conn = duckdb.connect(temp_database)
        people_count = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]
        products_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        conn.close()

        assert people_count == 3
        assert products_count == 2

    def test_ingest_with_custom_header_row(self, sample_workbook, temp_database):
        """Test ingesting sheet with custom header row."""
        config = load_config_with_substitution(
            "ingest_custom_header",
            database_path=temp_database,
            workbook_path=sample_workbook,
        )

        with ExcelIngester(config) as ingester:
            results = ingester.ingest()

        assert results[0].row_count == 2

        # Verify data
        conn = duckdb.connect(temp_database)
        data = conn.execute("SELECT * FROM report_data ORDER BY id").fetchall()
        conn.close()

        assert len(data) == 2
        assert data[0][0] == 1
        assert data[0][1] == 100

    def test_replace_data(self, sample_workbook, temp_database):
        """Test that replace_data=True replaces existing data."""
        config = load_config_with_substitution(
            "ingest_single_sheet",
            database_path=temp_database,
            workbook_path=sample_workbook,
        )

        # Run twice
        with ExcelIngester(config) as ingester:
            ingester.ingest()

        with ExcelIngester(config) as ingester:
            results = ingester.ingest()

        # Should still have only 3 rows (replaced, not appended)
        assert results[0].row_count == 3

    def test_print_summary(self, sample_workbook, temp_database, capsys):
        """Test that print_summary outputs correctly."""
        config = load_config_with_substitution(
            "ingest_single_sheet",
            database_path=temp_database,
            workbook_path=sample_workbook,
        )

        with ExcelIngester(config) as ingester:
            results = ingester.ingest()
            ingester.print_summary(results)

        captured = capsys.readouterr()
        assert "INGESTION SUMMARY" in captured.out
        assert "people" in captured.out
        assert "Sheet1" in captured.out
        assert "Rows loaded: 3" in captured.out
        assert "Table count: 3" in captured.out
