import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.ensemble import IsolationForest
from datetime import timedelta
import os

# --- CONFIGURATION ---
TARGET_FILENAME = 'AstraZeneca_Cleaned_Processed_Data.csv'
FORECAST_FILE = 'Final_Forecast_Submission.csv'
ANOMALY_FILE = 'Anomaly_Risk_Report.csv'
IMG_FORECAST = 'forecast_chart.png'

def find_the_file():
    """ Hunts for the file in current and sub-folders """
    print(f">>> SEARCHING for '{TARGET_FILENAME}'...")
    
    # 1. Check right here
    if os.path.exists(TARGET_FILENAME):
        return TARGET_FILENAME
    
    # 2. Walk through all sub-folders
    for root, dirs, files in os.walk("."):
        if TARGET_FILENAME in files:
            found_path = os.path.join(root, TARGET_FILENAME)
            print(f">>> FOUND IT AT: {found_path}")
            return found_path
            
    # 3. Fail gracefully
    print("\n!!! ERROR: I searched everywhere but could not find the file.")
    print(f"I am currently looking in this folder: {os.getcwd()}")
    print("Please make sure the file is inside this folder or a sub-folder.")
    return None

def master_quant_engine():
    # --- STEP 1: FIND DATA ---
    file_path = find_the_file()
    if file_path is None:
        return # Stop if no file

    print(">>> [1/5] LOADING DATA...")
    df = pd.read_csv(file_path)
    df['week'] = pd.to_datetime(df['week'])
    
    # --- STEP 2: FORECASTING ---
    print(">>> [2/5] RUNNING FORECAST (Holt-Winters)...")
    weekly = df.groupby(['week', 'cash_flow_direction'])['Amount in USD'].sum().unstack(fill_value=0)
    weekly = weekly.resample('W-MON').sum().fillna(0)
    
    if 'Inflow' not in weekly.columns: weekly['Inflow'] = 0.0
    if 'Outflow' not in weekly.columns: weekly['Outflow'] = 0.0
    
    try:
        model_in = ExponentialSmoothing(weekly['Inflow'], trend='add', seasonal=None).fit()
        future_in = model_in.forecast(26)
        model_out = ExponentialSmoothing(weekly['Outflow'], trend='add', seasonal=None).fit()
        future_out = model_out.forecast(26)
    except Exception as e:
        print(f"Warning: Model had a hiccup ({e}), using simple average instead.")
        future_in = [weekly['Inflow'].mean()] * 26
        future_out = [weekly['Outflow'].mean()] * 26
    
    # Build Forecast Data
    future_dates = [weekly.index[-1] + timedelta(weeks=x) for x in range(1, 27)]
    forecast_df = pd.DataFrame({
        'week': future_dates,
        'Inflow': future_in if isinstance(future_in, list) else future_in.values,
        'Outflow': future_out if isinstance(future_out, list) else future_out.values,
        'Type': 'Forecast'
    })
    
    history_df = pd.DataFrame({
        'week': weekly.index,
        'Inflow': weekly['Inflow'].values,
        'Outflow': weekly['Outflow'].values,
        'Type': 'History'
    })
    
    full_df = pd.concat([history_df, forecast_df])
    full_df['Net_Cash_Flow'] = full_df['Inflow'] + full_df['Outflow']
    full_df['Ending_Balance'] = full_df['Net_Cash_Flow'].cumsum()
    
    full_df.to_csv(FORECAST_FILE, index=False)
    
    plt.figure(figsize=(10, 5))
    plt.plot(full_df['week'], full_df['Ending_Balance'], label='Cash Balance', color='#830051')
    plt.axvline(x=weekly.index[-1], color='black', linestyle='--', label='Forecast Start')
    plt.title("6-Month Cash Flow Forecast")
    plt.legend()
    plt.savefig(IMG_FORECAST)
    print(f"   Saved Forecast to: {FORECAST_FILE}")

    # --- STEP 3: ANOMALY DETECTION ---
    print(">>> [3/5] DETECTING FRAUD (Isolation Forest)...")
    df_ml = df.copy()
    df_ml['Cat_Code'] = df_ml['Category'].astype('category').cat.codes
    X = df_ml[['Amount in USD', 'Cat_Code']].fillna(0)
    
    iso = IsolationForest(contamination=0.01, random_state=42)
    df_ml['Anomaly'] = iso.fit_predict(X)
    anomalies = df_ml[df_ml['Anomaly'] == -1]
    
    cols_to_save = [c for c in ['week', 'Name', 'Category', 'Amount in USD'] if c in df.columns]
    anomalies[cols_to_save].to_csv(ANOMALY_FILE, index=False)
    print(f"   Saved Risk Report to: {ANOMALY_FILE}")
    
    print(">>> [5/5] SUCCESS! FILES GENERATED.")

if __name__ == "__main__":
    master_quant_engine()