import numpy as np
import pandas as pd

np.random.seed(42)

# 10 zones with a base popularity and map coordinates (NYC-like area)
zones = {
    0: ("Downtown",   40.7128, -74.0060, 1.0),
    1: ("Airport",    40.6413, -73.7781, 0.8),
    2: ("University", 40.8075, -73.9626, 0.7),
    3: ("Mall",       40.7580, -73.9855, 0.9),
    4: ("Station",    40.7527, -73.9772, 1.1),
    5: ("Hospital",   40.7420, -73.9540, 0.5),
    6: ("Suburb A",   40.6782, -73.9442, 0.4),
    7: ("Suburb B",   40.7282, -73.7949, 0.3),
    8: ("Tech Park",  40.7061, -74.0087, 0.6),
    9: ("Beach",      40.5795, -73.8372, 0.3),
}

rows = []
start = pd.Timestamp("2026-09-01")
for day in range(30):
    for hour in range(24):
        for zid, (name, lat, lon, base) in zones.items():
            # rush hours: 8-10 and 17-20 get more demand
            peak = 2.5 if hour in (8, 9, 17, 18, 19) else 1.0
            night = 0.3 if hour < 5 else 1.0
            weekend = 1.3 if (day % 7) in (5, 6) else 1.0
            lam = 20 * base * peak * night * weekend
            n = np.random.poisson(lam)
            for _ in range(n):
                t = start + pd.Timedelta(days=day, hours=hour,
                                         minutes=int(np.random.randint(0, 60)))
                rows.append((t, zid, name,
                             lat + np.random.normal(0, 0.005),
                             lon + np.random.normal(0, 0.005)))

df = pd.DataFrame(rows, columns=["timestamp", "zone_id", "zone_name", "lat", "lon"])
df.to_csv("data/ride_requests.csv", index=False)
print("Rows:", len(df))
print(df.head())