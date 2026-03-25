"""Tests for VBA macro analyzer."""

import zipfile
import pytest
from pathlib import Path

from elt_ingest_excel.macro.vba_analyzer import (
    VbaMacroAnalyzer,
    VbaAnalysisResult,
    VbaMacro,
    list_vba_entry_points,
    analyze_workbook_macros,
)


class TestVbaMacroAnalyzer:
    """Test cases for VbaMacroAnalyzer."""

    def test_init_with_valid_path(self, tmp_path: Path) -> None:
        """Test initialization with a valid workbook path."""
        # Create a minimal fake workbook for testing
        workbook = tmp_path / "test.xlsm"
        workbook.touch()

        # Should not raise
        analyzer = VbaMacroAnalyzer(str(workbook))
        assert analyzer.workbook_path == workbook.resolve()

    def test_init_with_invalid_path(self) -> None:
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            VbaMacroAnalyzer("/nonexistent/path.xlsm")

    def test_init_with_wrong_suffix(self, tmp_path: Path) -> None:
        """Test initialization with non-Excel file."""
        txt_file = tmp_path / "test.txt"
        txt_file.touch()

        with pytest.raises(ValueError, match="Expected workbook"):
            VbaMacroAnalyzer(str(txt_file))

    def test_list_vba_entry_points_empty(self, tmp_path: Path) -> None:
        """Test listing macros from a file without VBA."""
        workbook = tmp_path / "empty.xlsm"
        workbook.touch()

        # Should handle non-zip files gracefully
        with pytest.raises(zipfile.BadZipFile):
            list_vba_entry_points(str(workbook))

    def test_analyze_workbook_macros(self, tmp_path: Path) -> None:
        """Test analyzing a workbook."""
        workbook = tmp_path / "test.xlsm"
        workbook.touch()

        # Should handle non-zip files gracefully
        with pytest.raises(zipfile.BadZipFile):
            analyze_workbook_macros(str(workbook))


class TestVbaMacro:
    """Test cases for VbaMacro dataclass."""

    def test_create_macro(self) -> None:
        """Test creating a VbaMacro instance."""
        macro = VbaMacro(name="TestMacro", macro_type="Sub")
        assert macro.name == "TestMacro"
        assert macro.macro_type == "Sub"
        assert macro.module_name is None
        assert macro.parameters == []

    def test_create_macro_with_all_fields(self) -> None:
        """Test creating a VbaMacro with all fields."""
        macro = VbaMacro(
            name="TestFunc",
            macro_type="Function",
            module_name="Module1",
            parameters=["arg1", "arg2"],
            description="Test function",
            line_number=10,
        )
        assert macro.name == "TestFunc"
        assert macro.macro_type == "Function"
        assert macro.module_name == "Module1"
        assert macro.parameters == ["arg1", "arg2"]
        assert macro.description == "Test function"
        assert macro.line_number == 10


class TestVbaAnalysisResult:
    """Test cases for VbaAnalysisResult dataclass."""

    def test_create_result(self) -> None:
        """Test creating a VbaAnalysisResult instance."""
        result = VbaAnalysisResult(workbook_path="/path/to/workbook.xlsm")
        assert result.workbook_path == "/path/to/workbook.xlsm"
        assert result.macros == []
        assert result.sheet_names == []
        assert result.named_ranges == []
        assert result.validation_sheets == []
