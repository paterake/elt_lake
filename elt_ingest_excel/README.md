# elt-ingest-excel

ELT module for ingesting Excel workbooks into DuckDB.

## Features

- Load Excel workbooks (.xlsx) into DuckDB tables
- JSON-based configuration for workbook/sheet mappings
- Automatic schema inference from Excel data
- Support for custom header rows and row skipping
- Validation of loaded data via table counts

## Installation

```bash
cd elt_ingest_excel
uv sync
```

## Quick Start

### 1. Create a JSON configuration file

```json
[
  {
    "workbookFileName": "/path/to/sales_data.xlsx",
    "sheets": [
      {
        "sheetName": "Monthly Sales",
        "targetTableName": "monthly_sales"
      },
      {
        "sheetName": "Product Catalog",
        "targetTableName": "products"
      }
    ]
  }
]
```

### 2. Run the ingestion

```python
from elt_ingest_excel import ExcelIngester, JsonConfigParser

# Load configuration
config = JsonConfigParser.from_json(
    "config.json",
    database_path="my_database.duckdb",
)

# Run ingestion
with ExcelIngester(config) as ingester:
    results = ingester.ingest()
    ingester.print_summary(results)
```

### 3. Or use the CLI

```bash
python examples/run_from_json.py config.json my_database.duckdb --verbose
```

## Configuration

### JSON Config Format

```json
[
  {
    "workbookFileName": "/path/to/workbook.xlsx",
    "sheets": [
      {
        "sheetName": "Sheet1",
        "targetTableName": "my_table",
        "headerRow": 1,
        "skipRows": 0
      }
    ]
  }
]
```

### Sheet Configuration Options

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `sheetName` | Yes | - | Name of the worksheet in Excel |
| `targetTableName` | Yes | - | Name of the DuckDB table to create |
| `headerRow` | No | 1 | Row number containing column headers (1-indexed) |
| `skipRows` | No | 0 | Number of rows to skip before the header row |

### Ingestion Options

| Option | Default | Description |
|--------|---------|-------------|
| `create_tables` | `True` | Create tables if they don't exist |
| `replace_data` | `True` | Replace existing data (vs append) |

## Programmatic Usage

### Using dataclasses directly

```python
from pathlib import Path
from elt_ingest_excel import (
    ExcelIngester,
    ExcelIngestConfig,
    WorkbookConfig,
    SheetConfig,
)

config = ExcelIngestConfig(
    database_path=Path("my_database.duckdb"),
    workbooks=[
        WorkbookConfig(
            workbook_file_name="/path/to/workbook.xlsx",
            sheets=[
                SheetConfig(
                    sheet_name="Sheet1",
                    target_table_name="my_table",
                    header_row=1,
                ),
            ],
        ),
    ],
    replace_data=True,
)

with ExcelIngester(config) as ingester:
    results = ingester.ingest()
    for result in results:
        print(f"{result.table_name}: {result.row_count} rows")
```

### Reading Excel files without DuckDB

```python
from elt_ingest_excel import ExcelLoader, SheetConfig

sheet_config = SheetConfig(
    sheet_name="Sheet1",
    target_table_name="ignored",
)

with ExcelLoader("/path/to/workbook.xlsx") as loader:
    data = loader.load_sheet(sheet_config)
    print(f"Loaded {len(data)} rows")
    print(data[0])  # First row as dict
```

## Testing

```bash
cd elt_ingest_excel
uv run pytest test/ -v
```

## Dependencies

- `openpyxl>=3.1.0` - Excel file reading
- `duckdb>=1.0.0` - Database storage
