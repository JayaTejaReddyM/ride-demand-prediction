from flask import Blueprint, render_template, request, jsonify
from .auth import role_required
from .recommender import recommend
from .predictor import predict_all_zones
from .data_service import ZONE_COORDS
from .live_ingest import get_snapshot

main_bp = Blueprint("main", __name__)

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@main_bp.route("/recommend", methods=["GET", "POST"])
@role_required("admin", "driver")
def recommend_page():
    result = None
    if request.method == "POST":
        zone = int(request.form["zone"])
        hour = int(request.form["hour"])
        day = int(request.form["day"])
        result = recommend(zone, hour, day)
    return render_template("recommend.html", result=result,
                           zones=ZONE_COORDS, days=DAYS)


@main_bp.route("/api/demand")
@role_required("admin", "planner")
def api_demand():
    hour = int(request.args.get("hour", 18))
    day = int(request.args.get("day", 2))
    data = predict_all_zones(hour, day)
    return jsonify(data[["zone_id", "zone_name", "lat", "lon",
                         "predicted_rides"]].to_dict(orient="records"))


@main_bp.route("/heatmap")
@role_required("admin", "planner")
def heatmap_page():
    return render_template("heatmap.html", days=DAYS)


@main_bp.route("/api/live")
@role_required("admin", "planner")
def api_live():
    return jsonify(get_snapshot())