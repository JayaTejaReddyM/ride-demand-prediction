import math
from .predictor import predict_all_zones
from .data_service import ZONE_COORDS


def haversine_km(lat1, lon1, lat2, lon2):
    """Straight-line distance between two coordinates in km."""
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def recommend(current_zone, hour, day_of_week, top_n=3, km_penalty=0.5):
    """Score = predicted rides - km_penalty * distance. Highest score wins."""
    demand = predict_all_zones(hour, day_of_week)
    _, clat, clon = ZONE_COORDS[current_zone]

    demand["distance_km"] = demand.apply(
        lambda r: round(haversine_km(clat, clon, r["lat"], r["lon"]), 1), axis=1)
    demand["score"] = (demand["predicted_rides"]
                       - km_penalty * demand["distance_km"]).round(1)

    ranked = demand.sort_values("score", ascending=False).head(top_n)
    best = ranked.iloc[0]
    current_name = ZONE_COORDS[current_zone][0]

    if int(best["zone_id"]) == current_zone:
        message = f"Stay in {current_name}: demand here is already the best option."
    else:
        message = (f"Move from {current_name} to {best['zone_name']} "
                   f"({best['distance_km']} km away, ~{best['predicted_rides']} rides expected).")

    options = [{
        "zone_id": int(r["zone_id"]),
        "zone_name": r["zone_name"],
        "predicted_rides": float(r["predicted_rides"]),
        "distance_km": float(r["distance_km"]),
        "score": float(r["score"]),
    } for _, r in ranked.iterrows()]

    return {"message": message, "options": options}