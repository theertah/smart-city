from flask import Blueprint, jsonify
from database.models import Location, Traffic
from ai import traffic_model
import city_brain

bp = Blueprint("predictions", __name__)


@bp.route("/api/alerts")
def alerts():
    return jsonify(city_brain.evaluate())


@bp.route("/api/predictions")
def predictions():
    result = []
    for loc in Location.query.all():
        latest = Traffic.query.filter_by(location_id=loc.location_id).order_by(Traffic.timestamp.desc()).first()
        if not latest:
            continue
        forecast = traffic_model.predict_congestion(loc.location_id, {
            "vehicle_count": latest.vehicle_count,
            "average_speed": latest.average_speed,
            "congestion_level": latest.congestion_level,
        })
        result.append({
            "zone": loc.zone, "name": loc.name,
            "prediction_type": "congestion_30min",
            "current": latest.congestion_level,
            "prediction": forecast["prediction"],
            "confidence": forecast["confidence"],
            "model": forecast["model"],
        })
    return jsonify(result)
