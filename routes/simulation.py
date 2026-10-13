from flask import Blueprint, jsonify, request

bp = Blueprint("simulation", __name__)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


@bp.route("/api/simulation", methods=["POST"])
def simulation():
    data = request.get_json(force=True) or {}
    traffic = float(data.get("traffic", 0))     # % increase
    temperature = float(data.get("temperature", 0))  # degrees increase
    rainfall = float(data.get("rainfall", 0))    # % increase
    population = float(data.get("population", 0))  # % increase

    traffic_load = _clamp(40 + traffic * 0.6 + population * 0.5, 0, 100)
    air_quality_risk = _clamp(20 + traffic * 0.35 + temperature * 4 + population * 0.3, 0, 100)
    energy_demand = _clamp(35 + temperature * 6 + population * 0.6 + traffic * 0.1, 0, 100)
    flood_risk = _clamp(rainfall * 0.55 + population * 0.2, 0, 100)

    narrative = []
    if traffic_load > 75:
        narrative.append("Road network would approach gridlock in peak zones.")
    if air_quality_risk > 70:
        narrative.append("Air quality would likely breach safe thresholds citywide.")
    if energy_demand > 70:
        narrative.append("Grid demand would strain existing capacity.")
    if flood_risk > 60:
        narrative.append("Low-lying zones face material flood exposure.")
    if not narrative:
        narrative.append("Conditions remain within manageable operating range.")

    return jsonify({
        "traffic_load": round(traffic_load, 1),
        "air_quality_risk": round(air_quality_risk, 1),
        "energy_demand": round(energy_demand, 1),
        "flood_risk": round(flood_risk, 1),
        "narrative": " ".join(narrative),
    })
