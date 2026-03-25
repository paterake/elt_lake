# VBA Macro Analyzer - Quick Start Guide

## Overview

This module provides Python tools to analyze and document VBA macros in Excel workbooks (`.xlsm`, `.xlam`, `.xlsb`).

## What Was Created

```
elt_ingest_excel/src/elt_ingest_excel/macro/
├── __init__.py                    # Module exports
├── excel_macro_runner.py          # Existing: Execute VBA macros
├── vba_analyzer.py                # NEW: Analyze VBA macros
└── README.md                      # NEW: Module documentation

elt_ingest_excel/examples/
├── analyze_vba_macros.py          # NEW: Command-line analyzer
└── document_validation_macros.py  # NEW: Validation macro documentation

elt_ingest_excel/test/
└── test_vba_analyzer.py           # NEW: Unit tests
```

## Quick Start

### 1. Analyze a Workbook

```bash
cd elt_ingest_excel

# List all macros
uv run python examples/analyze_vba_macros.py \
  --workbook ../.tmp/workday_fin_creditor_supplier_active_v1.xlsm \
  --list-macros

# Full analysis report
uv run python examples/analyze_vba_macros.py \
  --workbook ../.tmp/workday_fin_creditor_supplier_active_v1.xlsm
```

### 2. Document Validation Macros

```bash
uv run python examples/document_validation_macros.py
```

This generates detailed documentation about the validation macros in your Workday Supplier/Creditor workbook.

### 3. Use in Python Code

```python
from elt_ingest_excel.macro import VbaMacroAnalyzer

# Analyze a workbook
analyzer = VbaMacroAnalyzer("path/to/workbook.xlsm")
result = analyzer.analyze()

# Get all macros
for macro in result.macros:
    print(f"{macro.macro_type} {macro.name}")

# Categorize macros
categorized = analyzer.get_macros_by_category(result.macros)
print(f"Validation macros: {[m.name for m in categorized['Validation']]}")

# Generate report
report = analyzer.generate_report(result)
print(report)
```

### 4. Run VBA Macros (Existing Functionality)

```bash
# Run a specific validation macro
uv run python -m elt_ingest_excel.macro.excel_macro_runner \
  --workbook path/to/workbook.xlsm \
  --macro 'runSpecificValidationsFromSheet' \
  --unhide-sheet "Validation Results" \
  --excel-visible
```

## Key Macros in Your Workbook

### Primary Validation Macros

| Macro | Purpose |
|-------|---------|
| `runSpecificValidationsFromSheet` | Validate the current sheet only |
| `runAllValidationsFromSheet` | Validate all sheets in the workbook |
| `runValidationsFromRibbon` | Entry point for Excel ribbon button |

### Supporting Macros

| Macro | Purpose |
|-------|---------|
| `deleteValidationSheet` | Clear the Validation Results sheet |
| `clearSheetValidations` | Clear validation flags for a sheet |
| `populateResultSheetHeaders` | Set up validation result headers |
| `removeDuplicatesEntireSheet` | Remove duplicate rows |
| `Worksheet_Change` | Real-time validation on cell edits |

## Example Output

```
================================================================================
VBA MACRO ANALYSIS REPORT
================================================================================

Workbook: /path/to/workbook.xlsm

Total Macros Found: 40
Total Sheets: 124
Total Named Ranges: 573

--------------------------------------------------------------------------------
MACROS BY CATEGORY
--------------------------------------------------------------------------------

Validation (8):
  • checkNamedRangeExists
  • clearSheetValidations
  • deleteValidationSheet
  • getSelectedValidationSheetList
  • populateResultSheetHeaders
  • runAllValidationsFromSheet
  • runSpecificValidationsFromSheet
  • runValidationsFromRibbon

Sheet Operations (11):
  • addAdditionalSheetRows
  • clearSheetExistingFormat
  • deleteVa
  • DELETEVALUES
  • populateSheetDropDown
  • removeDuplicatesEntireSheet
  • Unhide_Multiple_Sheets
  • UpdateExistingSheetRows
  • Worksheet_Activate
  • Worksheet_Change
  • Worksheet_SelectionChange
...
```

## How the Validation Works

1. **Data Entry**: Users enter supplier/creditor data in Excel sheets
2. **Validation Trigger**: 
   - Manual: Click ribbon button or run macro
   - Automatic: `Worksheet_Change` event on cell edits
3. **Validation Rules**: Check against named ranges and predefined values
4. **Results**: Issues written to "Validation Results" sheet with:
   - Sheet name, rule type, column, supplier ID, details, error message

## Integration with ELT Pipeline

The validation macros complement the SQL-based validations in your ELT pipeline:

```
Source Excel → DuckDB (INGEST) → SQL Transforms (TRANSFORM) 
→ Output Workbook (.xlsm) → VBA Validation → Validation Results
```

SQL validations are in: `config/validate/finance/supplier/*.sql`

## Running Tests

```bash
cd elt_ingest_excel
uv run pytest test/test_vba_analyzer.py -v
```

## Limitations

- VBA code is compiled (in `vbaProject.bin`), so we can only extract macro **names**, not the actual source code
- For full VBA decompilation, use external tools like:
  - [runvba](https://github.com/DissectMalware/runvba)
  - [oledump.py](https://github.com/DidierStevens/DidierStevensSuite)

## Next Steps

1. **Review the documentation**: Run `document_validation_macros.py` for detailed macro docs
2. **Integrate with your workflow**: Use the analyzer to document other workbooks
3. **Extend the analyzer**: Add more pattern matching for your specific macros
