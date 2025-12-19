import pandas as pd

try:
    path = "c:/DATATHON25/MATERIALS/Datathon Dataset.xlsx"
    xl = pd.ExcelFile(path)
    
    print(f"File: {path}")
    print(f"Sheets found: {len(xl.sheet_names)}")
    
    for sheet in xl.sheet_names:
        print(f"\n--- SHEET: {sheet} ---")
        df = pd.read_excel(xl, sheet, nrows=2)
        print(f"Columns: {list(df.columns)}")
        print(f"First Row Data: {df.iloc[0].values if not df.empty else 'EMPTY'}")

except Exception as e:
    print(f"Error: {e}")
