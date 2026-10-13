from flask import Blueprint, jsonify
from database.models import Location, Traffic

bp = Blueprint("traffic", __name__)


@bp.route("/api/traffic")
def traffic():
    result = []
    for loc in Location.query.all():
        latest = Traffic.query.filter_by(location_id=loc.location_id).order_by(Traffic.timestamp.desc()).first()
        if latest:
            row = latest.to_dict()
            row["zone"] = loc.zone
            row["name"] = loc.name
            row["latitude"] = loc.latitude
            row["longitude"] = loc.longitude
            result.append(row)
    return jsonify(result)
