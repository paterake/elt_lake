# VBA Macro Analyzer

This module provides tools to analyze and document VBA macros in Excel workbooks (`.xlsm`, `.xlam`, `.xlsb`).

## Features

- **Extract macro names** from compiled VBA projects
- **Identify validation-related** sheets and named ranges
- **Categorize macros** by functionality (Validation, Sheet Operations, Data Operations, etc.)
- **Generate reports** in human-readable or JSON format
- **List all worksheets** and named ranges in the workbook

## Limitations

The VBA code in Excel workbooks is stored in a compiled binary format (`vbaProject.bin`). This module extracts macro names and metadata from the binary, but **cannot decompile the actual VBA source code**.

For full VBA code extraction, consider using external tools:
- [runvba](https://github.com/DissectMalware/runvba)
- [oledump.py](https://github.com/DidierStevens/DidierStevensSuite)

## Usage

### Command Line

```bash
cd elt_ingest_excel

# List all macros
uv run python examples/analyze_vba_macros.py \
  --workbook /path/to/workbook.xlsm \
  --list-macros

# Generate full analysis report
uv run python examples/analyze_vba_macros.py \
  --workbook /path/to/workbook.xlsm

# Save report to file
uv run python examples/analyze_vba_macros.py \
  --workbook /path/to/workbook.xlsm \
  --output /path/to/report.txt

# JSON output for programmatic use
uv run python examples/analyze_vba_macros.py \
  --workbook /path/to/workbook.xlsm \
  --json
```

### Python API

```python
from elt_ingest_excel.macro import VbaMacroAnalyzer, analyze_workbook_macros

# Analyze a workbook
analyzer = VbaMacroAnalyzer("/path/to/workbook.xlsm")
result = analyzer.analyze()

# Access macros
for macro in result.macros:
    print(f"{macro.macro_type} {macro.name}")

# Categorize macros
categorized = analyzer.get_macros_by_category(result.macros)
print(f"Validation macros: {[m.name for m in categorized['Validation']]}")

# Generate report
report = analyzer.generate_report(result)
print(report)

# Or use the convenience function
result = analyze_workbook_macros(
    "/path/to/workbook.xlsm",
    output_path="/path/to/report.txt"
)
```

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

## Integration with Excel Macro Runner

This module complements the existing `excel_macro_runner` module:

- **`excel_macro_runner`**: Executes VBA macros in Excel (macOS only)
- **`vba_analyzer`**: Analyzes and documents VBA macros (cross-platform)

Example workflow:

```bash
# 1. Analyze the workbook to see available macros
uv run python examples/analyze_vba_macros.py \
  --workbook workbook.xlsm \
  --list-macros

# 2. Run a specific macro
uv run python -m elt_ingest_excel.macro.excel_macro_runner \
  --workbook workbook.xlsm \
  --macro 'runSpecificValidationsFromSheet' \
  --unhide-sheet "Validation Results"
```

## Module Structure

```
elt_ingest_excel/src/elt_ingest_excel/macro/
├── __init__.py              # Module exports
├── excel_macro_runner.py    # Macro execution (existing)
└── vba_analyzer.py          # Macro analysis (new)
```

## Data Classes

### `VbaMacro`
Represents a VBA macro (Sub or Function).

```python
@dataclass
class VbaMacro:
    name: str                # Macro name
    macro_type: str          # "Sub" or "Function"
    module_name: str | None  # Module containing the macro
    parameters: list[str]    # Parameter list
    description: str | None  # Description/comment
    line_number: int | None  # Line number in module
```

### `VbaAnalysisResult`
Result of analyzing a workbook.

```python
@dataclass
class VbaAnalysisResult:
    workbook_path: str       # Path to analyzed workbook
    macros: list[VbaMacro]   # List of discovered macros
    sheet_names: list[str]   # All worksheet names
    named_ranges: list[str]  # All named range names
    validation_sheets: list[str]  # Validation-related sheets
    raw_strings: list[str]   # Raw strings from VBA binary
```
