# elt-ingest-excel Architecture

ELT pipeline that extracts data from Excel workbooks, loads it into DuckDB, applies SQL
transformations, and publishes results back to Excel. All behaviour is driven by config files
under `config/` — no operational values are hardcoded in Python.

## Pipeline phases

Three cumulative phases, controlled at runtime via `--run-to-phase`:

```
INGEST → TRANSFORM → PUBLISH
```

| Phase | What runs |
|---|---|
| `INGEST` | Read source Excel sheets → DuckDB tables |
| `TRANSFORM` | Execute SQL files in order → derived/cleaned tables |
| `PUBLISH` | Write DuckDB query results → target Excel workbook sheets |

Each phase includes all preceding phases.

---

## Module layout

```
elt_ingest_excel/
├── config/                  # All operational config (see Config layout below)
├── examples/                # One script per pipeline — the only entry points
│   ├── base_runner.py       # Shared argparse + FileIngestor wiring
│   ├── fin_supplier_creditor.py
│   ├── fin_customer_debtor.py
│   └── hcm_contingent_worker.py
├── src/elt_ingest_excel/
│   ├── elt_pipeline.py      # FileIngestor orchestrator + PipelinePhase enum
│   ├── loaders/             # ExcelReader, SheetProcessor
│   ├── parsers/             # JsonConfigParser, PublishConfigParser
│   ├── transform/           # SqlExecutor, SqlFileExecutor, UDFs
│   ├── writers/             # DuckDBWriter, SaveMode
│   ├── publish/             # ExcelPublisherXlwings, ExcelPublisherOpenpyxl
│   ├── models/              # Dataclass config models and result types
│   └── reporting/           # PipelineReporter (console output)
├── test/                    # pytest test suite
└── pyproject.toml           # Dependencies and Python version requirement
```

---

## Config layout

```
config/
├── ingest/                  # Ingest JSON configs — one per pipeline
│   ├── finance/
│   │   ├── supplier.json
│   │   └── customer.json
│   └── hcm/
│       └── contingent_worker.json
├── transform/
│   └── sql/                 # SQL files + order.txt — one directory per pipeline
│       ├── finance/
│       │   ├── supplier/
│       │   └── customer/
│       ├── hcm/
│       │   └── contingent_worker/
│       └── ref/             # Reference data load SQL (shared across pipelines)
├── validate/                # Post-transform validation SQL
│   └── finance/
│       └── supplier/
├── publish/                 # Publish JSON configs — one per pipeline
│   ├── finance/
│   │   ├── publish_supplier.json
│   │   └── publish_customer.json
│   └── hcm/
│       └── publish_contingent_worker.json
└── data/                    # Static reference data (JSON/CSV) read by SQL transforms
    ├── ref_country.json
    ├── ref_post_code_county.json
    └── ...
```

---

## Ingest config

Each pipeline has one ingest JSON file listing one or more source workbooks and their sheets.
See [`config/ingest/finance/supplier.json`](config/ingest/finance/supplier.json) for a live example.

**Schema:**

```json
[
  {
    "workbookFileName": "<source Excel filename>",
    "fileType": "EXCEL",
    "sheets": [
      {
        "sheetName": "<worksheet name>",
        "targetTableName": "<DuckDB table name>",
        "headerRow": 1,
        "dataRow": 2
      }
    ]
  }
]
```

| Field | Required | Default | Description |
|---|---|---|---|
| `workbookFileName` | Yes | — | Source Excel filename (relative to `data_path`) |
| `fileType` | No | `EXCEL` | File type (`EXCEL` only currently) |
| `sheetName` | Yes | — | Worksheet name in the workbook |
| `targetTableName` | Yes | — | DuckDB table to create |
| `headerRow` | No | `1` | Row containing column headers (1-indexed) |
| `dataRow` | No | `2` | First row of data (1-indexed) |

All source columns are read as strings (`dtype=str`). Type conversion is done in SQL during TRANSFORM.

---

## Transform config

Each pipeline's transform directory contains:

- **`order.txt`** — lists SQL filenames to execute, one per line, in order. Lines starting with `#` are comments.
- **`*.sql`** — one file per transformation step.

See [`config/transform/sql/finance/supplier/order.txt`](config/transform/sql/finance/supplier/order.txt) for a live example.

SQL files are restricted to their own pipeline directory — path traversal is enforced at runtime
(any entry in `order.txt` that resolves outside the configured transform path is rejected).

### Reference data

Static lookup tables in `config/data/` are loaded into DuckDB by SQL files in
[`config/transform/sql/ref/`](config/transform/sql/ref/). These are shared across pipelines.

### Validation SQL

Post-transform data quality checks live in [`config/validate/`](config/validate/). These are
run separately from the main transform phase.

---

## Publish config

Each pipeline has one publish JSON file mapping DuckDB query results to target Excel sheets.
See [`config/publish/finance/publish_customer.json`](config/publish/finance/publish_customer.json) for a live example.

**Schema:**

```json
[
  {
    "srcWorkbookPathName": "<path to source template workbook>",
    "srcWorkbookFileName": "<source workbook filename>",
    "tgtWorkbookPathName": "<path to write output workbook>",
    "tgtWorkbookFileName": "<output filename (without extension)>",
    "sheets": [
      {
        "srcTableName": "<DuckDB table or view to read>",
        "sheetName": "<target worksheet name>",
        "headerRow": 3,
        "dataRow": 4
      }
    ]
  }
]
```

---

## Adding a new pipeline

1. Create an ingest config under `config/ingest/<domain>/<name>.json`
2. Create a transform directory `config/transform/sql/<domain>/<name>/` with `order.txt` and SQL files
3. Create a publish config under `config/publish/<domain>/publish_<name>.json`
4. Add an example script under `examples/<name>.py` following the pattern in `examples/base_runner.py`

No Python source changes are required.

---

## Publisher types

Two Excel publisher backends are available, selected via `publisher_type` in `base_runner.py`:

| Type | Requires Excel | Preserves shapes/macros | Use when |
|---|---|---|---|
| `xlwings` (default) | Yes (macOS/Windows) | Yes | Target is `.xlsm` with drawings/macros |
| `openpyxl` | No | Partial | No Excel installed, or `.xlsx` targets |

---

## SaveMode

Controls how the DuckDB writer handles existing tables during INGEST:

| Mode | Behaviour |
|---|---|
| `RECREATE` (default) | Drop and recreate table from source data |
| `OVERWRITE` | Delete all rows, insert new rows (preserves schema) |
| `APPEND` | Insert new rows without touching existing data |
| `DROP` | Drop the table only; no data written |

---

## SQL path hardening

`SqlFileExecutor` resolves all SQL file paths at construction time. Before executing any file,
it verifies the resolved path is inside the configured transform directory. Any entry in
`order.txt` that escapes the directory (e.g. via `../`) is rejected with an error and the
pipeline halts. Only SQL files committed under `config/` can be executed.

---

## Phone normalisation UDF

Three DuckDB UDFs are registered by `src/elt_ingest_excel/transform/udf/phone.py`:

| UDF | Inputs | Returns | Purpose |
|---|---|---|---|
| `udf_parse_phone` | `international_code, number` | `STRUCT` | Full parse: intl code, area code, local number, device type |
| `get_phone_type` | `number, country_code` | `VARCHAR` | `Mobile`, `Landline`, or `NULL` |
| `get_area_code` | `number, country_code` | `VARCHAR` | Geographic area code or `NULL` |

Parsing uses the `phonenumbers` library (ITU-T E.164). The UDFs are called from SQL files in
`config/transform/sql/` — the invocation is config-driven; the parsing logic is standard-defined.

---

## Dependencies

See [`pyproject.toml`](pyproject.toml) for pinned versions.

| Package | Purpose |
|---|---|
| `pandas` | DataFrame reading and manipulation |
| `openpyxl` | Excel reading (ingest) and writing (openpyxl publisher) |
| `duckdb` | Local columnar database — storage, transforms, UDFs |
| `xlwings` | Excel automation publisher (requires Excel installed) |
| `phonenumbers` | ITU-T phone number parsing for UDFs |
