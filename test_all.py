from app.data_service import load_rides, hourly_demand
from app.predictor import predict_all_zones
from app.recommender import recommend
from app.auth import USERS
from werkzeug.security import check_password_hash
from app import create_app

results = []

def check(name, condition):
    results.append((name, "PASS" if condition else "FAIL"))

# Module 2: Authentication
check("Admin login password valid", check_password_hash(USERS["admin"]["password"], "admin123"))
check("Wrong password rejected", not check_password_hash(USERS["admin"]["password"], "wrong"))
check("Three roles exist", {u["role"] for u in USERS.values()} == {"admin", "planner", "driver"})

# Module 3: Data service
df = load_rides()
check("Dataset loaded (>100000 rows)", len(df) > 100000)
check("No missing values", df.isna().sum().sum() == 0)
check("Training table complete (7200 rows)", len(hourly_demand(df)) == 7200)

# Module 4: Prediction
rush = predict_all_zones(18, 2)["predicted_rides"].sum()
night = predict_all_zones(3, 2)["predicted_rides"].sum()
check("Rush-hour demand > night demand", rush > night)
check("Top zone at 6 PM is Station", predict_all_zones(18, 2).iloc[0]["zone_name"] == "Station")

# Module 5: Recommendation
check("Station driver told to stay", recommend(4, 18, 2)["message"].startswith("Stay"))
check("Suburb A driver told to move", recommend(6, 18, 2)["message"].startswith("Move"))

# Web routes and role protection
app = create_app()
client = app.test_client()
check("Dashboard needs login", client.get("/dashboard").status_code == 302)

client.post("/login", data={"username": "driver", "password": "driver123"})
check("Driver can open /recommend", client.get("/recommend").status_code == 200)
check("Driver blocked from /heatmap (403)", client.get("/heatmap").status_code == 403)
client.get("/logout")

client.post("/login", data={"username": "planner", "password": "planner123"})
check("Planner can open /heatmap", client.get("/heatmap").status_code == 200)
check("Planner blocked from /recommend (403)", client.get("/recommend").status_code == 403)
check("Live API returns data", client.get("/api/live").status_code == 200)

print(f"{'Test':45} Result")
print("-" * 55)
for name, status in results:
    print(f"{name:45} {status}")
print(f"\n{sum(r[1] == 'PASS' for r in results)}/{len(results)} tests passed")