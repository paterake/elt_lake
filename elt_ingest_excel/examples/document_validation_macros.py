#!/usr/bin/env python3
"""
Document validation macros for the Workday Supplier/Creditor workbook.

This script generates detailed documentation about the validation macros
in the workday_fin_creditor_supplier_active_v1.xlsm workbook.
"""

from pathlib import Path

from elt_ingest_excel.macro import VbaMacroAnalyzer


def main() -> None:
    """Generate validation macro documentation."""
    workbook_path = Path(
        "~/Documents/__code/git/emailrak/elt_lake/.tmp/"
        "workday_fin_creditor_supplier_active_v1.xlsm"
    ).expanduser()

    if not workbook_path.exists():
        print(f"Workbook not found: {workbook_path}")
        return

    analyzer = VbaMacroAnalyzer(workbook_path)
    result = analyzer.analyze()

    print("=" * 80)
    print("VALIDATION MACRO DOCUMENTATION")
    print("workday_fin_creditor_supplier_active_v1.xlsm")
    print("=" * 80)

    # Validation macros
    print("\n1. PRIMARY VALIDATION MACROS")
    print("-" * 80)

    validation_macros = {
        "runSpecificValidationsFromSheet": (
            "Run validations for the currently selected sheet only.",
            "Use this when you want to validate data in a specific sheet",
            "without running all validations across the entire workbook.",
        ),
        "runAllValidationsFromSheet": (
            "Run all validations across all data sheets in the workbook.",
            "This is the comprehensive validation that checks all sheets",
            "and populates the 'Validation Results' sheet with any issues found.",
        ),
        "runValidationsFromRibbon": (
            "Entry point for running validations from the Excel ribbon.",
            "This macro is typically bound to a ribbon button for user access.",
        ),
    }

    for name, description in validation_macros.items():
        print(f"\n  {name}")
        for line in description:
            print(f"    {line}")

    # Supporting validation macros
    print("\n2. SUPPORTING VALIDATION MACROS")
    print("-" * 80)

    supporting_macros = {
        "deleteValidationSheet": (
            "Clear all content from the Validation Results sheet.",
            "Used to reset the validation results before running new validations.",
        ),
        "clearSheetValidations": (
            "Clear validation flags/markers for a specific sheet.",
            "Removes validation highlighting or comments from the active sheet.",
        ),
        "populateResultSheetHeaders": (
            "Set up column headers in the Validation Results sheet.",
            "Headers typically include: sheet, rule_type, col, supplier_id, detail, message",
        ),
        "getSelectedValidationSheetList": (
            "Get list of sheets to validate based on user selection.",
            "Used by runSpecificValidationsFromSheet to determine scope.",
        ),
        "checkNamedRangeExists": (
            "Verify that a named range exists in the workbook.",
            "Used to validate configuration before running validations.",
        ),
    }

    for name, description in supporting_macros.items():
        print(f"\n  {name}")
        for line in description:
            print(f"    {line}")

    # Data operation macros
    print("\n3. DATA OPERATION MACROS")
    print("-" * 80)

    data_macros = {
        "removeDuplicatesEntireSheet": (
            "Remove duplicate rows from the entire active sheet.",
            "Uses Excel's built-in duplicate removal functionality.",
        ),
        "UpdateExistingSheetRows": (
            "Update existing rows in a sheet with new data.",
            "Matches on primary key and updates changed values.",
        ),
        "addAdditionalSheetRows": (
            "Add new rows to a sheet for additional data entry.",
            "Extends the data entry area while preserving existing data.",
        ),
        "populateSheetDropDown": (
            "Populate drop-down lists for data validation in a sheet.",
            "Sets up Excel data validation with allowed values from named ranges.",
        ),
    }

    for name, description in data_macros.items():
        print(f"\n  {name}")
        for line in description:
            print(f"    {line}")

    # Event handlers
    print("\n4. EVENT HANDLERS")
    print("-" * 80)

    event_handlers = {
        "Worksheet_Change": (
            "Triggered when a user edits a cell in the worksheet.",
            "Monitors column D (rows 4-99999) for changes.",
            "Likely validates Alternate Name Usage in real-time.",
        ),
        "Worksheet_Activate": (
            "Triggered when a worksheet is activated/selected.",
            "May be used to set up sheet-specific configuration.",
        ),
        "Worksheet_SelectionChange": (
            "Triggered when the user changes cell selection.",
            "May be used for context-sensitive help or validation hints.",
        ),
    }

    for name, description in event_handlers.items():
        print(f"\n  {name}")
        for line in description:
            print(f"    {line}")

    # Validation sheets
    print("\n5. VALIDATION-RELATED SHEETS")
    print("-" * 80)

    for sheet in result.validation_sheets:
        print(f"  • {sheet}")

    # Key data sheets
    print("\n6. KEY DATA SHEETS (Sample)")
    print("-" * 80)

    key_sheets = [
        "Supplier Name",
        "Supplier Groups",
        "Supplier Alternate Name",
        "Supplier Currencies",
        "Supplier Tax",
        "Supplier Payment",
        "Supplier Procurement",
        "Supplier Company Restrictions",
        "Supplier Settlement Account",
        "Supplier Intermediary Account",
        "Supplier Address",
        "Supplier Phone",
        "Supplier Email",
        "Validation Results",
    ]

    for sheet in key_sheets:
        if sheet in result.sheet_names:
            print(f"  ✓ {sheet}")
        else:
            print(f"  ✗ {sheet} (not found)")

    # Usage examples
    print("\n7. USAGE EXAMPLES")
    print("-" * 80)

    print("""
From Python:
  # Run specific validations
  from elt_ingest_excel.macro.excel_macro_runner import run_excel_vba_macro
  
  run_excel_vba_macro(
      workbook_path="workday_fin_creditor_supplier_active_v1.xlsm",
      macro_name="runSpecificValidationsFromSheet",
      unhide_sheets=["Validation Results"],
      save=True,
      close=False,
  )

From Command Line:
  uv run python -m elt_ingest_excel.macro.excel_macro_runner \\
    --workbook workday_fin_creditor_supplier_active_v1.xlsm \\
    --macro 'runSpecificValidationsFromSheet' \\
    --unhide-sheet "Validation Results" \\
    --excel-visible

From Excel:
  1. Open the workbook
  2. Enable macros when prompted
  3. Click the "Run Validations" button on the ribbon
  4. Or press Alt+F8 and select a macro to run
""")

    print("\n" + "=" * 80)
    print(f"Total macros found: {len(result.macros)}")
    print(f"Total sheets: {len(result.sheet_names)}")
    print(f"Total named ranges: {len(result.named_ranges)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
