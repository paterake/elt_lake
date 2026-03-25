# elt-ingest-excel

ELT module that ingests Excel workbooks into DuckDB, runs SQL transformations, and publishes results back to Excel.

For full architectural detail see [ARCHITECTURE.md](ARCHITECTURE.md).

## Prerequisites

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) package manager
- Excel (macOS/Windows) — required only for the `xlwings` publisher (default)

## Setup

```bash
cd elt_ingest_excel
uv sync
```

## Running

All pipelines accept `--run-to-phase INGEST|TRANSFORM|PUBLISH` (default: `PUBLISH`).

```bash
# Finance – Supplier/Creditor
uv run python examples/fin_supplier_creditor.py [--run-to-phase INGEST|TRANSFORM|PUBLISH]

# Finance – Customer/Debtor
uv run python examples/fin_customer_debtor.py [--run-to-phase INGEST|TRANSFORM|PUBLISH]

# HCM – Contingent Worker
uv run python examples/hcm_contingent_worker.py [--run-to-phase INGEST|TRANSFORM|PUBLISH]
```

## Examples:
```bash
cd elt_ingest_excel
uv sync
uv run python examples/fin_supplier_creditor.py --run-to-phase PUBLISH
uv run python examples/hcm_contingent_worker.py --run-to-phase PUBLISH
uv run python examples/fin_customer_debtor.py   --run-to-phase PUBLISH
uv run python examples/fin_workday_ref.py

```

## Running Excel VBA validations (macOS)

This runs the validation macros inside the generated .xlsm workbook and unhides the Validation Results sheet.

Prerequisites:
- Microsoft Excel installed (macOS)
- Macros enabled for the workbook (Excel may prompt you the first time you open it)

List available VBA entry points offline (best-effort, no Excel required):

```bash
cd elt_ingest_excel
uv run python -m elt_ingest_excel.macro.excel_macro_runner \
  --workbook /Users/rpatel/Documents/workday_fin_creditor_supplier_active_v1.xlsm \
  --list-macros
```

List macros via Excel (recommended, accurate):

```bash
cd elt_ingest_excel
uv run python -m elt_ingest_excel.macro.excel_macro_runner \
  --workbook /Users/rpatel/Documents/workday_fin_creditor_supplier_active_v1.xlsm \
  --list-macros-excel \
  --excel-visible
```

Run the validation macro and unhide Validation Results:

```bash
cd elt_ingest_excel
uv run python -m elt_ingest_excel.macro.excel_macro_runner \
  --workbook /Users/rpatel/Documents/workday_fin_creditor_supplier_active_v1.xlsm \
  --macro 'workday_fin_creditor_supplier_active_v1.xlsm!runSpecificValidationsFromSheet' \
  --unhide-sheet "Validation Results" \
  --excel-visible
```


## Tests

```bash
uv run pytest test/ -v
```
