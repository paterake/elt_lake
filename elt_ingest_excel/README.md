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
uv run python examples/hcm_contingent_worker.py --run-to-phase TRANSFORM
uv run python examples/fin_customer_debtor.py   --run-to-phase PUBLISH
uv run python examples/fin_supplier_creditor.py --run-to-phase PUBLISH

```


## Tests

```bash
uv run pytest test/ -v
```
