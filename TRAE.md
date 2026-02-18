# TRAE Project Rules

This file captures the core conventions and rules for the `elt_lake` project.

## SQL Formatting

- All SQL should follow the formatting rules in `TRAE_SQL.md`.
- Use the house formatter (or the `sql-format-3space` skill) when reformatting SQL.

## Excel Column / Cell Values

- For Excel-related introspection (drop-downs or distinct values), use the `excel-column-values` skill, which invokes `elt_ingest_excel/elt_skill_excel_utility.py`.
- Modes:
  - `filter` / `auto`: Return the Data Validation / drop-down list for a column or specific cell, if available.
  - `distinct`: Return unique non-blank values actually present in the column.
- When you need the allowed values for a specific cell (for example `Supplier Tax!E4`), call the skill with:
  - `--mode auto` or `--mode filter`
  - `--column <col>`
  - `--cell <cell_ref>` (preferred for cell-level validation)
- When you only care about what appears in the data (not the drop-down definition), use `--mode distinct` without a cell target.
