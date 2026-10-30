import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "ride_requests.csv"

ZONE_COORDS = {
    0: ("Downtown",   40.7128, -74.0060),
    1: ("Airport",    40.6413, -73.7781),
    2: ("University", 40.8075, -73.9626),
    3: ("Mall",       40.7580, -73.9855),
    4: ("Station",    40.7527, -73.9772),
    5: ("Hospital",   40.7420, -73.9540),
    6: ("Suburb A",   40.6782, -73.9442),
    7: ("Suburb B",   40.7282, -73.7949),
    8: ("Tech Park",  40.7061, -74.0087),
    9: ("Beach",      40.5795, -73.8372),
}


def load_rides():
    """Load the raw ride request log and clean it."""
    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    df = df.dropna()
    df = df.drop_duplicates()
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek   # 0 = Monday
    df["date"] = df["timestamp"].dt.date
    return df


def hourly_demand(df=None):
    """Count rides per zone, per date, per hour (includes zero-ride hours)."""
    if df is None:
        df = load_rides()
    counts = df.groupby(["zone_id", "date", "hour"]).size()
    zones = sorted(df["zone_id"].unique())
    dates = sorted(df["date"].unique())
    full_index = pd.MultiIndex.from_product(
        [zones, dates, range(24)], names=["zone_id", "date", "hour"])
    table = counts.reindex(full_index, fill_value=0).reset_index(name="rides")
    table["day_of_week"] = pd.to_datetime(table["date"]).dt.dayofweek
    return table


def zone_summary(df=None):
    """Total rides per zone, highest first."""
    if df is None:
        df = load_rides()
    s = (df.groupby(["zone_id", "zone_name"]).size()
           .reset_index(name="total_rides")
           .sort_values("total_rides", ascending=False))
    return s


def peak_hours(df=None):
    """Average rides per hour of day across all zones."""
    if df is None:
        df = load_rides()
    return df.groupby("hour").size().div(df["date"].nunique())