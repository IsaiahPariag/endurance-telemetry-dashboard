import pandas as pd
import numpy as np

def format_pace(seconds):
    minutes = int(seconds // 60)
    rem_seconds = int(seconds % 60)
    return f"{minutes}:{rem_seconds:02d} /mi"

def run_pipeline():
    # 1. Extract
    df = pd.read_csv("data/raw/running_logs.csv")
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    # 2. Transform: Pace Formatting
    df['pace_formatted'] = df['pace_seconds_per_mile'].apply(format_pace)
    
    # Workload Proxy: Training Load = duration * RPE
    df['training_load'] = df['duration_minutes'] * df['rpe_perceived_exertion']
    
    # Create complete date range to properly compute rolling window metrics
    full_dates = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
    daily_df = pd.DataFrame({'date': full_dates})
    
    # Aggregate daily metrics
    daily_agg = df.groupby('date').agg({
        'training_load': 'sum',
        'distance_miles': 'sum'
    }).reset_index()
    
    daily_merged = pd.merge(daily_df, daily_agg, on='date', how='left').fillna(0)
    
    # Rolling 7-day Acute Load vs 28-day Chronic Load
    daily_merged['acute_load_7d'] = daily_merged['training_load'].rolling(window=7, min_periods=1).mean()
    daily_merged['chronic_load_28d'] = daily_merged['training_load'].rolling(window=28, min_periods=1).mean()
    
    # Acute:Chronic Workload Ratio (ACWR)
    # ACWR between 0.8 and 1.3 is considered the sweet spot for athletic progression
    daily_merged['acwr'] = (daily_merged['acute_load_7d'] / (daily_merged['chronic_load_28d'] + 1e-5)).round(2)
    
    # Merge ACWR metrics back to activity records
    final_df = pd.merge(df, daily_merged[['date', 'acute_load_7d', 'chronic_load_28d', 'acwr']], on='date', how='left')
    
    # 3. Load
    final_df.to_csv("data/processed/clean_telemetry.csv", index=False)
    print("ETL complete: Clean telemetry saved to data/processed/clean_telemetry.csv")

if __name__ == "__main__":
    run_pipeline()
