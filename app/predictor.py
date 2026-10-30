import joblib
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

from .data_service import hourly_demand, ZONE_COORDS

MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "demand_model.joblib"
FEATURES = ["zone_id", "hour", "day_of_week"]


def train_model():
    """Train on the first 23 days, test on the last 7, then retrain on all data."""
    table = hourly_demand()
    table["date"] = pd.to_datetime(table["date"])

    cutoff = table["date"].max() - pd.Timedelta(days=6)
    train = table[table["date"] < cutoff]
    test = table[table["date"] >= cutoff]

    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(train[FEATURES], train["rides"])

    pred = model.predict(test[FEATURES])
    metrics = {
        "mae": round(mean_absolute_error(test["rides"], pred), 2),
        "r2": round(r2_score(test["rides"], pred), 3),
        "train_rows": len(train),
        "test_rows": len(test),
    }

    # final model uses all the data
    model.fit(table[FEATURES], table["rides"])
    joblib.dump(model, MODEL_PATH)
    return metrics


def load_model():
    if not MODEL_PATH.exists():
        train_model()
    return joblib.load(MODEL_PATH)


def predict_all_zones(hour, day_of_week):
    """Predicted rides for every zone at a given hour and weekday (0=Mon)."""
    model = load_model()
    rows = pd.DataFrame({
        "zone_id": list(ZONE_COORDS.keys()),
        "hour": hour,
        "day_of_week": day_of_week,
    })
    rows["predicted_rides"] = model.predict(rows[FEATURES]).round(1)
    rows["zone_name"] = rows["zone_id"].map(lambda z: ZONE_COORDS[z][0])
    rows["lat"] = rows["zone_id"].map(lambda z: ZONE_COORDS[z][1])
    rows["lon"] = rows["zone_id"].map(lambda z: ZONE_COORDS[z][2])
    return rows.sort_values("predicted_rides", ascending=False).reset_index(drop=True)