import argparse
import sys
import pandas as pd
from pathlib import Path

# Add the src directory to the path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from elt_ingest_excel import ExcelReader

# Configure pandas to show everything
pd.set_option('display.max_columns', None)        # Show all columns
pd.set_option('display.width', None)              # Don't wrap lines
pd.set_option('display.max_colwidth', 50)         # Show more text per cell

# Create an instance
loader = ExcelReader(
    file_path="~/Documents/__data/excel/FIN_Supplier.xlsm",
    sheet_name="Supplier Name",
    header_row=2,  # because your header is on row 3 (0-based index = 2)
    dtype=str
)

# Load and get the cleaned DataFrame
df = loader.load()

# Preview
loader.preview()