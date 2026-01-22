import pandas as pd
from pathlib import Path

class ExcelReader:
    """
    A class to load and clean Excel files with customizable header and cleaning options.
    """

    def __init__(
        self,
        file_path: str,
        sheet_name: str | int = 0,
        header_row: int = 0,  # 0-based index; e.g., 2 means row 3
        dtype=str,
        drop_empty_rows: bool = True,
        drop_empty_cols: bool = True
    ):
        self.file_path = Path(file_path).expanduser()
        self.sheet_name = sheet_name
        self.header_row = header_row
        self.dtype = dtype
        self.drop_empty_rows = drop_empty_rows
        self.drop_empty_cols = drop_empty_cols
        self.df: pd.DataFrame | None = None

    def load(self) -> pd.DataFrame:
        """Load and clean the Excel sheet, returning a pandas DataFrame."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        # Load with specified header row
        self.df = pd.read_excel(
            self.file_path,
            sheet_name=self.sheet_name,
            header=self.header_row,
            dtype=self.dtype
        )

        # print(self.df.dtypes)

        # Clean empty columns
        if self.drop_empty_cols:
            self.df = self.df.dropna(how='all', axis=1)

        # Clean empty rows
        if self.drop_empty_rows:
            self.df = self.df.dropna(how='all', axis=0)

        return self.df

    def preview(self, n: int = 5):
        if self.df is None:
            print("No data loaded. Call .load() first.")
            return
        
        # Temporarily show all columns
        with pd.option_context(
            'display.max_columns', None,
            'display.width', None,
            'display.max_colwidth', 50
        ):
            print(self.df.head(n))