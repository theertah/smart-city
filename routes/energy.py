from flask import Blueprint, jsonify
from database.models import Location, Energy

bp = Blueprint("energy", __name__)


@bp.route("/api/energy")
def energy():
    result = []
    for loc in Location.query.all():
        latest = Energy.query.filter_by(location_id=loc.location_id).order_by(Energy.timestamp.desc()).first()
        if latest:
            row = latest.to_dict()
            row["zone"] = loc.zone
            row["name"] = loc.name
            result.append(row)
    return jsonify(result)
