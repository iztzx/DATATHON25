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
            
            # --- 3a. CATEGORY MAPPING (Inferred Activity) ---
            print("Applying Rule-Based Activity Logic...")
            
            # Default to Operating
            df['Activity'] = 'Operating'
            
            # Identify Column for Rules (Category or Category Names)
            rule_col = 'Category' # Default
            
            # Define Keywords
            investing_kw = ['Capex', 'Asset', 'Invest', 'Acquisition']
            financing_kw = ['Intercompany', 'Dividend', 'Equity', 'Loan', 'Interest', 'Financing', 'Treasury']
            
            for keyword in investing_kw:
                mask = df[rule_col].astype(str).str.contains(keyword, case=False, na=False)
                df.loc[mask, 'Activity'] = 'Investing'
                
            for keyword in financing_kw:
                mask = df[rule_col].astype(str).str.contains(keyword, case=False, na=False)
                df.loc[mask, 'Activity'] = 'Financing'
            
            # RULE: "Non Netting AP" -> Operating Outflow (Manual Override)
            mask_nn_ap = df['Category'].astype(str).str.contains("Non Netting AP", case=False, na=False)
            if mask_nn_ap.any():
                print(f"  • Fixing {mask_nn_ap.sum()} 'Non Netting AP' entries -> Operating")
                # Fallback if Activity column is empty or mismatch
                if 'Activity' in df.columns:
                    df['Activity'] = df['Activity'].astype(object) # Fix FutureWarning
                    df.loc[mask_nn_ap, 'Activity'] = 'Operating' # Simplification
            
            # RULE: "Other" Logic (Sign-based)
            mask_other = df['Category'].astype(str).str.contains("Other", case=False, na=False)
            if mask_other.any():
                print(f"  • Logic check on {mask_other.sum()} 'Other' entries")
                # Inflow if Amount > 0, Outflow if < 0. 
                # Already handled by cash_flow_direction, but let's ensure Activity is valid
                if 'Activity' in df.columns:
                     # If mapped activity is missing for Other, fill it?
                     # Usually 'Other' is Operating unless specified.
                     df.loc[mask_other & df['Activity'].isna(), 'Activity'] = 'Operating'

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
        subset_cols = ['Amount in USD', 'posting_date', 'Category']
        # NOTE: We intentionally PRESERVE duplicates here so the Anomaly Detection module
        # in the main analysis can flag them for review.
        print("  • NOTE: Duplicates are PRESERVED for anomaly detection.")
        df['is_potential_duplicate'] = df.duplicated(subset=subset_cols, keep=False)
        
        # C. CURRENCY CHECK (The "Korea Check")
        # Load Exchange Rates to verify impact
        df_fx = all_sheets.get('Others - Exchange Rate')
        if df_fx is not None:
             print("Performing Currency Impact Analysis...")
             # Cleaning FX sheet (Header detection usually row 0, but check)
             # Assumption: Columns are "Code" (Currency Code), "Rate (USD)"
             # Main data has 'Curr.'
             
             if 'Code' in df_fx.columns and 'Rate (USD)' in df_fx.columns and 'Curr.' in df.columns:
                 print("  • Merging Provided Exchange Rates (from Excel)...")
                 # Rename for clarity before merge
                 df_fx_clean = df_fx[['Code', 'Rate (USD)']].rename(columns={'Rate (USD)': 'Sheet_Rate_USD'})
                 
                 df = pd.merge(df, df_fx_clean, left_on='Curr.', right_on='Code', how='left')
                 
                 # Calculate Implied Rate from Data
                 # Implied Rate = Amount USD / Amount Doc
                 # Handle div/0
                 df['implied_fx_rate'] = df.apply(lambda row: abs(row['Amount in USD'] / row['Amount in doc. curr.']) if row['Amount in doc. curr.'] != 0 else 0, axis=1)
                 
                 # Calculate Variance % (Official vs Implied)
                 # If Implied < Official, implies devaluation or bad conversion?
                 # Actually, usually 'Amount in USD' IS calculated by 'Rate (USD)' in the source.
                 # This check verifies if the SOURCE system used the SAME rate as the provided TABLE.
                 df['fx_rate_variance'] = df['implied_fx_rate'] - df['Sheet_Rate_USD']
                 
                 print("  • Calculated 'fx_rate_variance' for General Currency Volatility Analysis")
             else:
                 print("  • Warning: Could not map Exchange Rate columns (Missing 'Code' or 'Rate (USD)').")

        # 6b. TIME SERIES FEATURES (ESS Ready)
        print("Adding Time Series Intelligence...")
        if 'posting_date' in df.columns:
            df['Year'] = df['posting_date'].dt.year
            df['Quarter'] = df['posting_date'].dt.quarter
            df['Month'] = df['posting_date'].dt.month
            df['Week_Num'] = df['posting_date'].dt.isocalendar().week
            # Create a clean 'YYYY-WW' string for categorical sorting
            df['Fiscal_Week'] = df['Year'].astype(str) + "-W" + df['Week_Num'].astype(str).str.zfill(2)
        
        # 6c. NET AMOUNT STANDARDIZATION
        # Ensure we have a clear 'Net_Amount_USD' signed column for summation
        # (Handling cases where Amount in USD might be positive only - though usually it tracks Doc Curr sign)
        # Trusting Doc Curr Sign as source of truth
        if 'Amount in doc. curr.' in df.columns and 'Amount in USD' in df.columns:
             # Force sign consistency
             df['Net_Amount_USD'] = np.where(df['Amount in doc. curr.'] < 0, 
                                             -1 * df['Amount in USD'].abs(), 
                                             df['Amount in USD'].abs())

        # 7. Export
        print(f"\nSaving processed data to: {output_path}")
        export_cols = [c for c in df.columns if c in [
            'Name', 'Country', 'DocumentNo', 'posting_date', 'week', 
            'Year', 'Quarter', 'Month', 'Fiscal_Week',
            'Category', 'Activity', 
            'Amount in doc. curr.', 'Amount in USD', 'Net_Amount_USD',
            'cash_flow_direction', 'is_weekend', 'is_potential_duplicate',
            'Curr.', 'implied_fx_rate', 'Sheet_Rate_USD', 'fx_rate_variance'
        ]]
        
        # If Activity missing, export what we have
        df.to_csv(output_path, columns=export_cols, index=False)
        print("Done! Data cleaning separation successful.")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")

if __name__ == "__main__":
    clean_and_export_data()
