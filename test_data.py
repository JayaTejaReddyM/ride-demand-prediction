from app.data_service import load_rides, hourly_demand, zone_summary, peak_hours

df = load_rides()
print("Total rides:", len(df))

print("\n--- Rides per zone ---")
print(zone_summary(df))

print("\n--- Avg rides per hour of day ---")
print(peak_hours(df).round(0))

print("\n--- Training table (first 5 rows) ---")
h = hourly_demand(df)
print(h.head())
print("Training table rows:", len(h))