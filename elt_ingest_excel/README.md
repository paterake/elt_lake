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

Run the validation macros that 3+ uses to validate the generated `.xlsm` workbook.
This allows you to find and fix data quality issues before sending the workbook to 3+.

**Prerequisites:**
- Microsoft Excel installed (macOS)
- Macros enabled for the workbook

**One-time setup: Unhide ValidationManifest sheet**

The ValidationManifest sheet contains the validation rules but is hidden by default.
Before running validations, unhide it and add rules for your sheets:

```bash
cd elt_ingest_excel

# Unhide ValidationManifest sheet
uv run python examples/unhide_validation_manifest.py --excel-visible
```

Then in Excel:
1. Open the `ValidationManifest` sheet (now visible at the end of sheet tabs)
2. Add validation rules for your data sheets (e.g., 'Supplier Name')
3. Save the workbook

**Run Validation:**

```bash
cd elt_ingest_excel

# Run all validations
uv run python examples/fin_supplier_creditor_validate.py

# Run specific validation macro
uv run python examples/fin_supplier_creditor_validate.py \
  --macro runSpecificValidationsFromSheet

# Run with Excel visible (to watch progress)
uv run python examples/fin_supplier_creditor_validate.py --excel-visible

# Override workbook path
uv run python examples/fin_supplier_creditor_validate.py \
  --workbook /path/to/other_workbook.xlsm
```

**Your Complete Workflow:**

```bash
# 1. Run your ETL pipeline
uv run python examples/fin_supplier_creditor.py --run-to-phase PUBLISH

# 2. Run validation (NEW - removes 3+ latency)
uv run python examples/fin_supplier_creditor_validate.py

# 3. Open workbook and review "Validation Results" sheet
#    Fix any data issues if needed, then repeat from step 1
```

For full documentation see [VBA_VALIDATION_RUNNER.md](VBA_VALIDATION_RUNNER.md).


## Creating the EIB workbook

The Supplier/Creditor `.xlsm` workbook contains an `InitiateSPECAdvanceLoad` macro that generates the EIB output (same as the "Create Specific EIBs" button on the EIB View sheet).

**One-time prerequisite:** The `TempCreator` VBA module has `Option Private Module` which blocks external calls. Remove it once:

1. Open the workbook in Excel
2. Press `Option+F11` to open the VBA Editor
3. In the Project pane: expand the workbook → **Modules → TempCreator**
4. Delete the line: `Option Private Module`
5. Save (`Cmd+S`) and close the VBA Editor

```bash
cd elt_ingest_excel

# Generate EIB workbook (saves in-place, unhides EIB View sheet)
uv run python examples/fin_supplier_creditor_create_eib.py

# Run with Excel visible (to watch progress)
uv run python examples/fin_supplier_creditor_create_eib.py --excel-visible

# Override workbook path
uv run python examples/fin_supplier_creditor_create_eib.py \
  --workbook /path/to/other_workbook.xlsm
```

After the macro completes, check the **EIB View** sheet in the workbook for the generated EIB data.

**Full workflow with EIB creation:**

```bash
# 1. Run the ETL pipeline
uv run python examples/fin_supplier_creditor.py --run-to-phase PUBLISH

# 2. Run validations
uv run python examples/fin_supplier_creditor_validate.py

# 3. Create EIB workbook
uv run python examples/fin_supplier_creditor_create_eib.py
```

## Tests

```bash
uv run pytest test/ -v
```
