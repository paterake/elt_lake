#!/usr/bin/env python3
"""
Example: Analyze VBA macros in an Excel workbook.

This script demonstrates how to use the VbaMacroAnalyzer to extract
and document VBA macros from Excel workbooks.

Usage:
    cd elt_ingest_excel
    uv run python examples/analyze_vba_macros.py \
        --workbook /path/to/workbook.xlsm \
        [--output /path/to/report.txt]
"""

import argparse
import sys
from pathlib import Path

from elt_ingest_excel.macro.vba_analyzer import (
    VbaMacroAnalyzer,
    analyze_workbook_macros,
)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze VBA macros in Excel workbooks"
    )
    parser.add_argument(
        "--workbook",
        required=True,
        help="Path to the Excel workbook (.xlsm, .xlam, .xlsb)",
    )
    parser.add_argument(
        "--output",
        help="Optional path to save the analysis report (txt file)",
    )
    parser.add_argument(
        "--list-macros",
        action="store_true",
        help="Only list macro names (one per line)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    workbook_path = Path(args.workbook).expanduser().resolve()
    if not workbook_path.exists():
        print(f"Error: Workbook not found: {workbook_path}", file=sys.stderr)
        return 1

    try:
        analyzer = VbaMacroAnalyzer(workbook_path)
        result = analyzer.analyze()

        if args.list_macros:
            # Simple list of macro names
            for macro in result.macros:
                print(macro.name)
            return 0

        if args.json:
            # JSON output
            import json

            output = {
                "workbook": str(result.workbook_path),
                "macros": [
                    {
                        "name": m.name,
                        "type": m.macro_type,
                    }
                    for m in result.macros
                ],
                "sheet_count": len(result.sheet_names),
                "named_range_count": len(result.named_ranges),
                "validation_sheets": result.validation_sheets,
            }
            print(json.dumps(output, indent=2))
            return 0

        # Default: human-readable report
        report = analyzer.generate_report(result)
        print(report)

        # Save report if output path specified
        if args.output:
            output_file = Path(args.output).expanduser().resolve()
            output_file.write_text(report, encoding="utf-8")
            print(f"\nReport saved to: {output_file}", file=sys.stderr)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
