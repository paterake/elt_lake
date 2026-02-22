# elt-ingest-excel

ELT module for ingesting Excel workbooks into DuckDB with transformation and publishing capabilities.

## Setup

### Quick Run

```bash
cd elt_ingest_excel
uv sync --reinstall
```

```bash
cd elt_ingest_excel
uv sync
uv run --active python examples/fin_customer_debtor.py   --run-to-phase PUBLISH
uv run --active python examples/fin_supplier_creditor.py --run-to-phase PUBLISH
uv run python examples/hcm_contingent_worker.py
```


### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager

### Create and sync the virtual environment

```bash
cd elt_ingest_excel
uv sync
```

This creates a `.venv/` directory and installs all dependencies.

### Running code

Use `uv run` to execute Python scripts within the virtual environment:

```bash
# Run a script
uv run python examples/fin_supplier_creditor.py

# Run tests
uv run pytest test/ -v

# Start a Python REPL with dependencies available
uv run python
```

### Adding dependencies

```bash
# Add a runtime dependency
uv add requests

# Add a dev dependency
uv add --group dev black
```

## Features

- Load Excel workbooks (.xlsx) into DuckDB tables
- JSON-based configuration for workbook/sheet mappings
- SQL-based transformations
- Publish transformed data to Excel workbooks
- Support for custom header rows and row skipping

## Quick Start

### Using FileIngestor (ELT Pipeline)

```python
from elt_ingest_excel import FileIngestor, PipelinePhase

# Create pipeline
pipeline = FileIngestor(
    config_base_path="~/config",
    cfg_ingest_path="ingest/finance",
    cfg_ingest_name="supplier.json",
    cfg_transform_path="transform/finance",
    cfg_publish_path="publish/finance",
    cfg_publish_name="supplier_publish.json",
    data_path="~/data",
    data_file_name="suppliers.xlsx",
    database_path="~/output/data.duckdb",
)

# Run full ELT pipeline (ingest -> transform -> publish)
load_results, transform_results, publish_results = pipeline.process()

# Or run up to a specific phase
load_results, _, _ = pipeline.process(run_to_phase=PipelinePhase.INGEST)
load_results, transform_results, _ = pipeline.process(run_to_phase=PipelinePhase.TRANSFORM)
```

## Configuration

### Ingest JSON Config Format

```json
{
  "workbooks": [
    {
      "workbookFileName": "suppliers.xlsx",
      "fileType": "EXCEL",
      "sheets": [
        {
          "sheetName": "Sheet1",
          "targetTableName": "raw_suppliers",
          "headerRow": 1,
          "dataRow": 2
        }
      ]
    }
  ]
}
```

### Sheet Configuration Options

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `sheetName` | Yes | - | Name of the worksheet in Excel |
| `targetTableName` | Yes | - | Name of the DuckDB table to create |
| `headerRow` | No | 1 | Row number containing column headers (1-indexed) |
| `dataRow` | No | 2 | Row number where data starts (1-indexed) |

### Transform Configuration

Create an `order.txt` file in the transform config path listing SQL files to execute:

```
01_clean_data.sql
02_transform.sql
03_aggregate.sql
```

## Testing

```bash
uv run pytest test/ -v
```

## Dependencies

- `openpyxl>=3.1.0` - Excel file reading
- `duckdb>=1.0.0` - Database storage
- `pandas>=2.0.0` - Data manipulation
