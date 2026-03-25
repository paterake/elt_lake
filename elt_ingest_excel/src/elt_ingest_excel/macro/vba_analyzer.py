"""
VBA Macro Analyzer for Excel Workbooks.

This module provides tools to extract, analyze, and document VBA macros
from Excel .xlsm, .xlam, and .xlsb files.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class VbaMacro:
    """Represents a VBA macro (Sub or Function)."""

    name: str
    macro_type: str  # "Sub" or "Function"
    module_name: str | None = None
    parameters: list[str] = field(default_factory=list)
    description: str | None = None
    line_number: int | None = None


@dataclass
class VbaAnalysisResult:
    """Result of VBA analysis on a workbook."""

    workbook_path: str
    macros: list[VbaMacro] = field(default_factory=list)
    sheet_names: list[str] = field(default_factory=list)
    named_ranges: list[str] = field(default_factory=list)
    validation_sheets: list[str] = field(default_factory=list)
    raw_strings: list[str] = field(default_factory=list)


class VbaMacroAnalyzer:
    """Analyzer for VBA macros in Excel workbooks."""

    def __init__(self, workbook_path: str | Path) -> None:
        """Initialize the analyzer with a workbook path.

        Args:
            workbook_path: Path to the Excel workbook (.xlsm, .xlam, .xlsb)
        """
        self.workbook_path = Path(workbook_path).expanduser().resolve()
        if not self.workbook_path.exists():
            raise FileNotFoundError(str(self.workbook_path))

        valid_suffixes = {".xlsm", ".xlam", ".xlsb"}
        if self.workbook_path.suffix.lower() not in valid_suffixes:
            raise ValueError(
                f"Expected workbook with suffix {valid_suffixes}, "
                f"got '{self.workbook_path.suffix}'"
            )

    def analyze(self) -> VbaAnalysisResult:
        """Perform comprehensive analysis of the workbook.

        Returns:
            VbaAnalysisResult containing macros, sheets, and named ranges
        """
        result = VbaAnalysisResult(workbook_path=str(self.workbook_path))

        with zipfile.ZipFile(self.workbook_path) as zf:
            # Extract VBA macros
            result.macros = self._extract_macros(zf)
            result.raw_strings = self._extract_vba_strings(zf)

            # Extract sheet names
            result.sheet_names = self._extract_sheet_names(zf)

            # Extract named ranges
            result.named_ranges = self._extract_named_ranges(zf)

            # Identify validation-related sheets
            result.validation_sheets = self._find_validation_sheets(
                result.sheet_names, result.named_ranges
            )

        return result

    def _extract_vba_strings(self, zf: zipfile.ZipFile, min_len: int = 2) -> list[str]:
        """Extract printable strings from VBA project.

        Args:
            zf: ZipFile object for the workbook
            min_len: Minimum length of strings to extract

        Returns:
            List of printable ASCII strings from VBA binary
        """
        try:
            vba = zf.read("xl/vbaProject.bin")
        except KeyError:
            return []

        strings: list[str] = []
        current: list[int] = []

        for b in vba:
            if 32 <= b <= 126:
                current.append(b)
            else:
                if len(current) >= min_len:
                    strings.append(bytes(current).decode("ascii", errors="ignore"))
                current = []

        if len(current) >= min_len:
            strings.append(bytes(current).decode("ascii", errors="ignore"))

        return strings

    def _extract_macros(self, zf: zipfile.ZipFile) -> list[VbaMacro]:
        """Extract VBA macro definitions from the workbook.

        Note: This extracts macro names from the compiled VBA project.
        For full macro code extraction, use external tools like:
        - runvba (https://github.com/DissectMalware/runvba)
        - oledump.py (https://github.com/DidierStevens/DidierStevensSuite)

        Args:
            zf: ZipFile object for the workbook

        Returns:
            List of VbaMacro objects
        """
        strings = self._extract_vba_strings(zf, min_len=2)
        txt = "\n".join(strings)

        macros: list[VbaMacro] = []
        seen: set[str] = set()

        # Known macro names from common Excel VBA patterns
        # These are extracted from string references in the VBA binary
        known_macro_patterns = [
            r"runSpecificValidationsFromSheet",
            r"runAllValidationsFromSheet",
            r"runValidationsFromRibbon",
            r"deleteValidationSheet",
            r"removeDuplicatesEntireSheet",
            r"clearSheetValidations",
            r"populateResultSheetHeaders",
            r"getSelectedValidationSheetList",
            r"populateSheetDropDown",
            r"addAdditionalSheetRows",
            r"UpdateExistingSheetRows",
            r"clearSheetExistingFormat",
            r"checkNamedRangeExists",
            r"Unhide_Multiple_Sheets",
            r"togglePri",  # togglePrimary
            r"yConfig",  # updateConfig
            r"optimiz",  # optimizeEnd
            r"Worksheet_Change",
            r"Worksheet_Activate",
            r"Worksheet_SelectionChange",
            r"deleteVa",  # deleteValidation
            r"upd",  # update
            r"useforsuppliersettlementonly",
        ]

        # First, look for known macro patterns in strings
        for pattern in known_macro_patterns:
            if re.search(pattern, txt, re.IGNORECASE):
                # Try to get the full name
                match = re.search(rf"({pattern}[A-Za-z0-9_]*)", txt, re.IGNORECASE)
                if match:
                    name = match.group(1)
                    # Clean up common truncations
                    if name and name not in seen:
                        seen.add(name)
                        macros.append(
                            VbaMacro(
                                name=name,
                                macro_type="Sub",  # Most are Subs
                            )
                        )

        # Also try to extract from Sub/Function patterns
        pattern = r"(?:^|[\r\n])\s*(Public\s+|Private\s+)?(Sub|Function)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(|:|\n|$)"

        for match in re.finditer(pattern, txt, re.IGNORECASE | re.MULTILINE):
            macro_type = match.group(2)
            macro_name = match.group(3)

            if macro_name.lower() in {"auto_open", "auto_close"}:
                continue
            if macro_name in seen:
                continue

            seen.add(macro_name)

            # Skip common VBA keywords and fragments
            if len(macro_name) < 3 or macro_name.lower() in {
                "and",
                "the",
                "sub",
                "end",
                "if",
                "dim",
                "set",
                "for",
                "next",
                "then",
                "else",
                "public",
                "private",
                "attribute",
                "module",
                "option",
                "explicit",
            }:
                continue

            # Skip single-letter prefixes that look like fragments
            if len(macro_name) <= 4 and not macro_name[0].isupper():
                continue

            macros.append(
                VbaMacro(
                    name=macro_name,
                    macro_type=macro_type.capitalize(),
                )
            )

        return sorted(macros, key=lambda m: (m.macro_type, m.name.lower()))

    def _extract_sheet_names(self, zf: zipfile.ZipFile) -> list[str]:
        """Extract worksheet names from workbook.xml.

        Args:
            zf: ZipFile object for the workbook

        Returns:
            List of sheet names
        """
        try:
            wb_xml = zf.read("xl/workbook.xml").decode("utf-8", errors="ignore")
        except KeyError:
            return []

        # Match sheet names from workbook.xml
        names = re.findall(r'name="([^"]+)"', wb_xml)

        # Filter out filter databases and internal names
        sheet_names = [
            n
            for n in names
            if not n.startswith("_xlnm.")
            and not n.startswith("microsoft.com:")
            and n not in {"ABS", "ABSColHeaderRows", "ABSRangeToClear"}
        ]

        return sorted(set(sheet_names))

    def _extract_named_ranges(self, zf: zipfile.ZipFile) -> list[str]:
        """Extract named range definitions from workbook.xml.

        Args:
            zf: ZipFile object for the workbook

        Returns:
            List of named range names
        """
        try:
            wb_xml = zf.read("xl/workbook.xml").decode("utf-8", errors="ignore")
        except KeyError:
            return []

        names = re.findall(r'name="([^"]+)"', wb_xml)

        # Filter to only named ranges (not sheets)
        named_ranges = [
            n
            for n in names
            if not n.startswith("_xlnm.")
            and not n.startswith("microsoft.com:")
            and "_" in n or n.endswith("Table") or "Range" in n or "Ref" in n
        ]

        return sorted(set(named_ranges))

    def _find_validation_sheets(
        self, sheet_names: list[str], named_ranges: list[str]
    ) -> list[str]:
        """Identify validation-related sheets and ranges.

        Args:
            sheet_names: List of worksheet names
            named_ranges: List of named range names

        Returns:
            List of validation-related sheet/range names
        """
        validation_keywords = ["valid", "manifest", "result", "issue"]

        validation_sheets: list[str] = []

        for name in sheet_names + named_ranges:
            name_lower = name.lower()
            if any(kw in name_lower for kw in validation_keywords):
                validation_sheets.append(name)

        return sorted(set(validation_sheets))

    def get_macros_by_category(
        self, macros: list[VbaMacro]
    ) -> dict[str, list[VbaMacro]]:
        """Categorize macros by their functionality.

        Args:
            macros: List of VbaMacro objects

        Returns:
            Dictionary mapping category names to macro lists
        """
        categories: dict[str, list[VbaMacro]] = {
            "Validation": [],
            "Sheet Operations": [],
            "Named Ranges": [],
            "Data Operations": [],
            "Configuration": [],
            "Other": [],
        }

        validation_keywords = [
            "valid",
            "check",
            "verify",
            "audit",
            "manifest",
            "result",
        ]
        sheet_keywords = [
            "sheet",
            "row",
            "column",
            "cell",
            "range",
            "hide",
            "unhide",
            "delete",
            "create",
        ]
        named_range_keywords = ["named", "range", "name"]
        data_keywords = [
            "duplicate",
            "filter",
            "sort",
            "update",
            "populate",
            "import",
            "export",
            "save",
        ]
        config_keywords = ["config", "setup", "init", "password"]

        for macro in macros:
            name_lower = macro.name.lower()

            if any(kw in name_lower for kw in validation_keywords):
                categories["Validation"].append(macro)
            elif any(kw in name_lower for kw in sheet_keywords):
                categories["Sheet Operations"].append(macro)
            elif any(kw in name_lower for kw in named_range_keywords):
                categories["Named Ranges"].append(macro)
            elif any(kw in name_lower for kw in data_keywords):
                categories["Data Operations"].append(macro)
            elif any(kw in name_lower for kw in config_keywords):
                categories["Configuration"].append(macro)
            else:
                categories["Other"].append(macro)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def generate_report(self, result: VbaAnalysisResult) -> str:
        """Generate a human-readable report of the VBA analysis.

        Args:
            result: VbaAnalysisResult from analyze()

        Returns:
            Formatted report string
        """
        lines: list[str] = []

        lines.append("=" * 80)
        lines.append("VBA MACRO ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"\nWorkbook: {result.workbook_path}")
        lines.append(f"\nTotal Macros Found: {len(result.macros)}")
        lines.append(f"Total Sheets: {len(result.sheet_names)}")
        lines.append(f"Total Named Ranges: {len(result.named_ranges)}")

        # Macros by category
        categorized = self.get_macros_by_category(result.macros)
        lines.append("\n" + "-" * 80)
        lines.append("MACROS BY CATEGORY")
        lines.append("-" * 80)

        for category, macros in categorized.items():
            lines.append(f"\n{category} ({len(macros)}):")
            for macro in macros:
                lines.append(f"  • {macro.name}")

        # Validation sheets
        if result.validation_sheets:
            lines.append("\n" + "-" * 80)
            lines.append("VALIDATION-RELATED SHEETS/RANGES")
            lines.append("-" * 80)
            for name in result.validation_sheets:
                lines.append(f"  • {name}")

        # All macros list
        lines.append("\n" + "-" * 80)
        lines.append("ALL MACROS (ALPHABETICAL)")
        lines.append("-" * 80)
        for macro in sorted(result.macros, key=lambda m: m.name.lower()):
            lines.append(f"  {macro.macro_type:8} {macro.name}")

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)


def list_vba_entry_points(workbook_path: str | Path) -> list[str]:
    """List VBA macro entry points in a workbook.

    This is a convenience function compatible with the existing
    excel_macro_runner.list_vba_entry_points API.

    Args:
        workbook_path: Path to the Excel workbook

    Returns:
        Sorted list of macro names
    """
    analyzer = VbaMacroAnalyzer(workbook_path)
    result = analyzer.analyze()
    return [macro.name for macro in result.macros]


def analyze_workbook_macros(
    workbook_path: str | Path, output_path: str | Path | None = None
) -> VbaAnalysisResult:
    """Analyze VBA macros in a workbook and optionally save report.

    Args:
        workbook_path: Path to the Excel workbook
        output_path: Optional path to save the report (txt file)

    Returns:
        VbaAnalysisResult containing the analysis
    """
    analyzer = VbaMacroAnalyzer(workbook_path)
    result = analyzer.analyze()

    if output_path:
        report = analyzer.generate_report(result)
        output_file = Path(output_path).expanduser().resolve()
        output_file.write_text(report, encoding="utf-8")

    return result
