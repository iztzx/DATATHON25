import pandas as pd
import os
import numpy as np

def generate_powerbi_files():
    print("=== PREPARING DATA FOR POWER BI (STAR SCHEMA) ===")
    
    # Create Output Directory
    output_dir = 'PowerBI_Data'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. LOAD DATA
    try:
        df = pd.read_csv('AstraZeneca_Cleaned_Processed_Data.csv')
        fc = pd.read_csv('AstraZeneca_Forecast_Results.csv')
        print("Data Loaded Successfully.")
    except Exception as e:
        print(f"Error loading source data: {e}")
        return

    # 2. DIM_DATE (Calendar)
    # Combine date ranges
    df['date'] = pd.to_datetime(df['posting_date'])
    fc['Date'] = pd.to_datetime(fc['Date'])
    
    min_date = min(df['date'].min(), fc['Date'].min())
    max_date = max(df['date'].max(), fc['Date'].max())
    
    dates = pd.date_range(start=min_date, end=max_date, freq='D')
    dim_date = pd.DataFrame({'Date': dates})
    dim_date['Year'] = dim_date['Date'].dt.year
    dim_date['Quarter'] = dim_date['Date'].dt.quarter
    dim_date['Month'] = dim_date['Date'].dt.month
    dim_date['Week'] = dim_date['Date'].dt.isocalendar().week
    dim_date['Month_Name'] = dim_date['Date'].dt.month_name()
    dim_date['Day_Name'] = dim_date['Date'].dt.day_name()
    # Weekly Key (Monday)
    dim_date['Week_Start_Date'] = dim_date['Date'].dt.to_period('W').dt.start_time
    
    dim_date.to_csv(f'{output_dir}/Dim_Date.csv', index=False)
    print(f"Generated {output_dir}/Dim_Date.csv")

    # 3. DIM_CATEGORY (Hierarchy)
    # Unique combinations of Activity and Category
    cat_cols = ['Activity', 'Category']
    if set(cat_cols).issubset(df.columns):
        dim_cat = df[cat_cols].drop_duplicates().sort_values('Activity')
        dim_cat['ID'] = range(1, len(dim_cat) + 1)
        dim_cat.to_csv(f'{output_dir}/Dim_Category.csv', index=False)
        print(f"Generated {output_dir}/Dim_Category.csv")
    
    # 4. DIM_ENTITY (Geography/Org)
    ent_cols = ['Name', 'Country', 'Curr.']
    existing_ent_cols = [c for c in ent_cols if c in df.columns]
    if existing_ent_cols:
        dim_ent = df[existing_ent_cols].drop_duplicates()
        dim_ent.to_csv(f'{output_dir}/Dim_Entity.csv', index=False)
        print(f"Generated {output_dir}/Dim_Entity.csv")

    # 5. FACT_ACTUALS (Transactions)
    # Simplify for Performance
    fact_cols = ['posting_date', 'Name', 'Category', 'Activity', 'Amount in USD', 'Net_Amount_USD', 'fx_rate_variance']
    fact_cols = [c for c in fact_cols if c in df.columns]
    fact_actuals = df[fact_cols].copy()
    fact_actuals['Type'] = 'Actual'
    fact_actuals.to_csv(f'{output_dir}/Fact_Actuals.csv', index=False)
    print(f"Generated {output_dir}/Fact_Actuals.csv")

    # 6. FACT_FORECASTS (Projections)
    # Ensure standard columns
    fc['Type'] = 'Forecast'
    fc.to_csv(f'{output_dir}/Fact_Forecasts.csv', index=False)
    print(f"Generated {output_dir}/Fact_Forecasts.csv")

    # 7. FACT_BUDGET (Simulated for Bullet Chart)
    # Rationale: User wants to see "Burn vs Budget". We simulate Budget = Actual * random split.
    # Group by Key Dimensions (Category, Activity, Name, Quarter)
    # Using 'fact_actuals' as base
    
    print("Generating Simulated Budget Data for PowerBI Bullet Charts...")
    fact_budget = fact_actuals.copy()
    
    # Simulate Budget Logic:
    # If Outflow (negative), Budget might be slightly less negative (Target) or more (Allowance).
    # Let's assume Budget is usually 90% to 110% of Actuals.
    np.random.seed(42) # Consistent simulation
    noise = np.random.uniform(0.9, 1.1, size=len(fact_budget))
    
    # We only care about budget for Amounts really
    if 'Amount in USD' in fact_budget.columns:
        fact_budget['Budget_Amount_USD'] = fact_budget['Amount in USD'] * noise
        
    # Rename for clarity in PowerBI
    fact_budget = fact_budget[['posting_date', 'Name', 'Category', 'Activity', 'Budget_Amount_USD']]
    fact_budget.to_csv(f'{output_dir}/Fact_Budget.csv', index=False)
    print(f"Generated {output_dir}/Fact_Budget.csv (Simulated)")
    
    print("\nREADY FOR POWER BI:")
    print("1. Open Power BI")
    print("2. Get Data -> Folder -> Select 'PowerBI_Data'")
    print("3. Load and Link tables via Date/Category/Name keys.")

if __name__ == "__main__":
    generate_powerbi_files()
