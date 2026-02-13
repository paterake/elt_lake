import pandas as pd
import sys

def inspect_excel(path):
    try:
        df = pd.read_excel(path)
        print("Columns:", df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head())
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    inspect_excel(sys.argv[1])
