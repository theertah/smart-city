from flask import Blueprint, jsonify
from database.models import Location, Environment
from weather import current_temperatures_for_locations

bp = Blueprint("environment", __name__)


@bp.route("/api/environment")
def environment():
    result = []
    locations = Location.query.all()
    live_temperatures = current_temperatures_for_locations(locations)
    for loc in locations:
        latest = Environment.query.filter_by(location_id=loc.location_id).order_by(Environment.timestamp.desc()).first()
        if latest:
            row = latest.to_dict()
            row["zone"] = loc.zone
            row["name"] = loc.name
            live_data = live_temperatures.get(loc.location_id)
            if live_data:
                row["live_temperature_c"] = live_data.get("temperature")
                row["humidity"] = live_data.get("humidity") or row["humidity"]
                row["air_quality"] = live_data.get("aqi") or row["air_quality"]
                row["weather_time"] = live_data.get("time")
            else:
                row["live_temperature_c"] = None
                row["weather_time"] = None
            result.append(row)
    return jsonify(result)
