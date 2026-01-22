# src/elt_ingest_excel/excel_reader.py
import pandas as pd
from pathlib import Path

class ExcelReader:
    def __init__(self, file_path, sheet_name=0, header_row=0, dtype=str):
        self.file_path = Path(file_path).expanduser()
        self.sheet_name = sheet_name
        self.header_row = header_row
        self.dtype = dtype
        self.df = None

    def load(self):
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        self.df = pd.read_excel(
            self.file_path,
            sheet_name=self.sheet_name,
            header=self.header_row,
            dtype=self.dtype
        )
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
