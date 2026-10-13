from flask import Blueprint, jsonify
from database.models import Location, Waste
from ai import waste_model

bp = Blueprint("waste", __name__)


@bp.route("/api/waste")
def waste():
    result = []
    for loc in Location.query.all():
        latest = Waste.query.filter_by(location_id=loc.location_id).order_by(Waste.timestamp.desc()).first()
        if latest:
            row = latest.to_dict()
            row["zone"] = loc.zone
            row["name"] = loc.name
            forecast = waste_model.predict_fill(loc.location_id)
            row["predicted_fill_5h"] = forecast["predicted"]
            row["forecast_model"] = forecast["model"]
            result.append(row)
    return jsonify(result)
