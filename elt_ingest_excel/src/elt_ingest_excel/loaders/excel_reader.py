# src/elt_ingest_excel/loader/excel_reader.py
import re
import pandas as pd
from pathlib import Path


class ExcelReader:
    def __init__(self, file_path, sheet_name=0, header_row=0, dtype=str):
        self.file_path = Path(file_path).expanduser()
        self.sheet_name = sheet_name
        self.header_row = header_row
        self.dtype = dtype
        self.df = None

    @staticmethod
    def clean_column_name(name: str) -> str:
        """Clean a column name for database compatibility.

        Args:
            name: Original column name.

        Returns:
            Cleaned column name:
            - Lowercased
            - Trimmed (leading/trailing spaces removed)
            - Non-alphanumeric characters replaced with underscore
            - Multiple consecutive underscores collapsed to single
            - Leading/trailing underscores removed
        """
        if not isinstance(name, str):
            name = str(name)
        # Lowercase and trim
        cleaned = name.lower().strip()
        # Replace non-alphanumeric with underscore
        cleaned = re.sub(r'[^a-z0-9]', '_', cleaned)
        # Collapse multiple underscores to single
        cleaned = re.sub(r'_+', '_', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        return cleaned

    @staticmethod
    def _normalize_sheet_name(name: str) -> str:
        return re.sub(r"\s+", " ", str(name)).strip().casefold()

    def _load_with_xlwings(self) -> pd.DataFrame:
        import xlwings as xw

        app = xw.App(visible=False, add_book=False)
        book = None
        try:
            book = app.books.open(str(self.file_path))
            sheet = None

            if isinstance(self.sheet_name, int):
                sheet = book.sheets[self.sheet_name]
            elif isinstance(self.sheet_name, str):
                try:
                    sheet = book.sheets[self.sheet_name]
                except Exception:
                    normalized_target = self._normalize_sheet_name(self.sheet_name)
                    normalized_matches = [
                        s
                        for s in book.sheets
                        if self._normalize_sheet_name(s.name) == normalized_target
                    ]
                    if len(normalized_matches) == 1:
                        sheet = normalized_matches[0]
                    elif len(book.sheets) == 1:
                        sheet = book.sheets[0]
                    else:
                        raise ValueError(
                            f"Worksheet named '{self.sheet_name}' not found. Available worksheets: {[s.name for s in book.sheets]}"
                        )
            else:
                raise TypeError(f"Unsupported sheet_name type: {type(self.sheet_name)}")

            values = sheet.used_range.value
            if values is None:
                return pd.DataFrame()
            if not isinstance(values, list):
                values = [[values]]
            elif values and not isinstance(values[0], list):
                values = [values]

            header_row = int(self.header_row)
            if header_row < 0 or header_row >= len(values):
                raise ValueError(
                    f"header_row={self.header_row} is out of bounds for worksheet '{sheet.name}'"
                )

            headers = values[header_row]
            data = values[header_row + 1 :]
            df = pd.DataFrame(data, columns=headers)
            df = df.where(df.notna(), "")
            df = df.astype(str)
            return df
        finally:
            if book is not None:
                book.close()
            app.quit()

    def load(self):
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        try:
            self.df = pd.read_excel(
                self.file_path,
                sheet_name=self.sheet_name,
                header=self.header_row,
                dtype=str,
                na_filter=False,
            )
        except ValueError as e:
            msg = str(e)
            if (
                "Worksheet named" in msg
                or "Worksheet index" in msg
                or "0 worksheets found" in msg
            ):
                if isinstance(self.sheet_name, str):
                    try:
                        import openpyxl

                        wb = openpyxl.load_workbook(
                            self.file_path, read_only=True, data_only=True
                        )
                        available = list(wb.sheetnames)
                        wb.close()
                        if available and self.sheet_name not in available:
                            normalized_target = self._normalize_sheet_name(self.sheet_name)
                            normalized_matches = [
                                n
                                for n in available
                                if self._normalize_sheet_name(n) == normalized_target
                            ]
                            if len(normalized_matches) == 1:
                                self.df = pd.read_excel(
                                    self.file_path,
                                    sheet_name=normalized_matches[0],
                                    header=self.header_row,
                                    dtype=str,
                                    na_filter=False,
                                )
                            else:
                                self.df = self._load_with_xlwings()
                        else:
                            self.df = self._load_with_xlwings()
                    except Exception:
                        self.df = self._load_with_xlwings()
                else:
                    self.df = self._load_with_xlwings()
            else:
                raise
        # Clean up column names for database compatibility
        self.df.columns = [self.clean_column_name(col) for col in self.df.columns]
        if "department" in self.df.columns and "department_1" not in self.df.columns:
            self.df["department_1"] = self.df["department"]
        # self.df.dropna(how='all', axis=1, inplace=True)
        self.df.dropna(how='all', axis=0, inplace=True)
        return self.df

    def preview(self, n=5, full=True):
        if self.df is None:
            print("No data loaded.")
            return
        if full:
            # Show all columns without truncation
            with pd.option_context(
                'display.max_columns', None,
                'display.width', 10000,
                'display.max_colwidth', 100
            ):
                print(self.df.head(n))
        else:
            print(self.df.head(n))
