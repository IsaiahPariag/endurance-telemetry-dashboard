import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)
os.makedirs("data/raw", exist_ok=True)

start_date = datetime.now() - timedelta(days=180)
dates = [start_date + timedelta(days=i) for i in range(180)]

records = []
for d in dates:
    if np.random.rand() > 0.45:
        activity_type = np.random.choice(
            ["Intervals (400m)", "Tempo Run", "Long Run", "Recovery Run"],
            p=[0.25, 0.35, 0.20, 0.20]
        )
        
        if activity_type == "Intervals (400m)":
            dist = round(np.random.uniform(3.0, 5.0), 2)
            pace_sec = int(np.random.uniform(350, 400)) # 5:50 - 6:40 /mi
            hr = int(np.random.uniform(168, 185))
        elif activity_type == "Tempo Run":
            dist = round(np.random.uniform(4.0, 7.0), 2)
            pace_sec = int(np.random.uniform(410, 460)) # 6:50 - 7:40 /mi
            hr = int(np.random.uniform(155, 172))
        elif activity_type == "Long Run":
            dist = round(np.random.uniform(7.0, 13.0), 2)
            pace_sec = int(np.random.uniform(470, 530)) # 7:50 - 8:50 /mi
            hr = int(np.random.uniform(142, 160))
        else:
            dist = round(np.random.uniform(2.5, 4.0), 2)
            pace_sec = int(np.random.uniform(530, 600)) # 8:50 - 10:00 /mi
            hr = int(np.random.uniform(130, 145))
            
        dur_min = round((dist * pace_sec) / 60, 2)
        elev = int(dist * np.random.uniform(15, 40))
        
        records.append({
            "activity_id": f"ACT_{len(records)+1:04d}",
            "date": d.strftime("%Y-%m-%d"),
            "type": activity_type,
            "distance_miles": dist,
            "duration_minutes": dur_min,
            "pace_seconds_per_mile": pace_sec,
            "avg_heart_rate": hr,
            "max_heart_rate": hr + int(np.random.uniform(8, 18)),
            "elevation_gain_ft": elev,
            "rpe_perceived_exertion": int(np.random.uniform(4, 10))
        })

df = pd.DataFrame(records)
df.to_csv("data/raw/running_logs.csv", index=False)
print(f"Generated {len(df)} telemetry logs in data/raw/running_logs.csv")
