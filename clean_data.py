import pandas as pd
import numpy as np
import os

def clean_and_export_data():
    """
    Standalone script to clean AstraZeneca dataset and export to CSV.
    Implements robust multi-sheet loading, whitespace handling, and currency checks.
    """
    input_path = 'MATERIALS/Datathon Dataset.xlsx'
    output_path = 'AstraZeneca_Cleaned_Processed_Data.csv'
    
    print(f"=== ASTRAZENECA DATA CLEANING UTILITY ===")
    print(f"Input: {input_path}")
    
    try:
        # 1. Load All Sheets
        print("Loading Excel sheets...")
        all_sheets = pd.read_excel(input_path, sheet_name=None)
        
        df = all_sheets.get('Data - Main')
        df_link = all_sheets.get('Others - Category Linkage')
        
        if df is None:
            print("Error: 'Data - Main' sheet not found.")
            return
            
        print(f"  • Main Data: {df.shape} rows")
        
        # 2. Quality Check: Missing USD
        missing_usd = df['Amount in USD'].isnull().sum()
        print(f"  • Missing USD Amounts: {missing_usd}")
        
        if missing_usd > 0 and 'Amount in doc. curr.' in df.columns and 'Rate (USD)' in df.columns:
            print("    -> Filling missing USD from Rate...")
            df['Amount in USD'] = df['Amount in USD'].fillna(df['Amount in doc. curr.'] * df['Rate (USD)'])
            
        # 3. Standardization & Merging
        if df_link is not None and 'Category' in df.columns and 'Category' in df_link.columns:
            print("Merging Category Linkage...")
            # Robust Merge: Strip whitespace
            df['Category_Clean'] = df['Category'].astype(str).str.strip()
            df_link['Category_Clean'] = df_link['Category'].astype(str).str.strip()
            
            # Merge to get Activity (Operating/Investing/Financing)
            df = pd.merge(df, df_link, left_on='Category_Clean', right_on='Category_Clean', how='left', suffixes=('', '_link'))
            
            # Identify new column (Activity)
            new_cols = [c for c in df.columns if c not in df_link.columns or c == 'Category_Clean']
            potential_activity = [c for c in df.columns if c not in new_cols] # Columns solely from link
            
            # Fallback logic to find the 'Activity' column if name varies
            if 'Activity' in df.columns:
                print("  • Activity column mapped.")
            elif len(potential_activity) > 0:
                # Assume the first new meaningful column is Activity
                act_col = potential_activity[0] 
                df['Activity'] = df[act_col]
                print(f"  • Mapped Activity from column: {act_col}")
        
        # 3b. Merge Country Mapping
        df_country = all_sheets.get('Others - Country Mapping')
        if df_country is not None:
             print("Merging Country Mapping...")
             # Check columns. Snapshot showed 'Code', 'Country', 'Currency'
             # Main data 'Name' likely matches 'Code'
             if 'Code' in df_country.columns and 'Name' in df.columns:
                 df = pd.merge(df, df_country, left_on='Name', right_on='Code', how='left')
                 print(f"  • Added Country info. Columns: {list(df_country.columns)}")
             else:
                 print("  • Warning: Could not map Country (Columns mismatch)")

        # 4. Standardize Dates
        if 'Pstng Date' in df.columns:
            df['posting_date'] = pd.to_datetime(df['Pstng Date'], errors='coerce')
            df['week'] = df['posting_date'].dt.to_period('W').dt.start_time
            
        # 5. Determine Cash Flow Direction
        if 'Amount in doc. curr.' in df.columns:
            df['cash_flow_direction'] = np.where(df['Amount in doc. curr.'] > 0, 'Inflow', 'Outflow')
            
        # 6. ENHANCED QUALITY FLAGS (Comprehensiveness Upgrade)
        print("Adding Data Quality Flags...")
        
        # A. Weekend Postings (Saturday=5, Sunday=6)
        df['is_weekend'] = df['posting_date'].dt.dayofweek.isin([5, 6])
        
        # B. Potential Duplicates (Same Amount, Date, Category - regardless of Docs)
        # Marking instances that appear more than once
        subset_cols = ['Amount in USD', 'posting_date', 'Category']
        df['is_potential_duplicate'] = df.duplicated(subset=subset_cols, keep=False)
        
        # 7. Export
        print(f"\nSaving processed data to: {output_path}")
        export_cols = [c for c in df.columns if c in [
            'Name', 'Country', 'DocumentNo', 'posting_date', 'week', 'Category', 
            'Activity', 'Amount in doc. curr.', 'Amount in USD', 
            'cash_flow_direction', 'is_weekend', 'is_potential_duplicate'
        ]]
        
        # If Activity missing, export what we have
        df.to_csv(output_path, columns=export_cols, index=False)
        print("Done! Data cleaning separation successful.")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")

if __name__ == "__main__":
    clean_and_export_data()
