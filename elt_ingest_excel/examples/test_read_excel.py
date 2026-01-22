# examples/test_read_excel.py
import pandas as pd
from elt_ingest_excel import ExcelReader

# Configure pandas display
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

if __name__ == "__main__":
    loader = ExcelReader(
        file_path="~/Documents/__data/excel/FIN_Supplier.xlsm",
        sheet_name="Supplier Name",
        header_row=2,
        dtype=str
    )
    df = loader.load()
    loader.preview()
    print(df.iloc[0].to_dict())