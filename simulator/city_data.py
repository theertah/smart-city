import random
import math
from datetime import datetime

from database.db import db
from database.models import Location, Traffic, Environment, Waste

# in-memory running state per zone so readings drift realistically
# instead of being independently random every tick
_state = {}


def _time_of_day_factor():
    hour = datetime.now().hour + datetime.now().minute / 60
    rush = math.exp(-((hour - 9) ** 2) / 8) + math.exp(-((hour - 18) ** 2) / 8)
    return max(0, min(rush, 1.4))


def _init_state(location_id):
    _state[location_id] = {
        "vehicle_count": random.uniform(400, 700),
        "average_speed": random.uniform(28, 45),
        "temperature": random.uniform(27, 33),
        "humidity": random.uniform(40, 70),
        "air_quality": random.uniform(35, 65),
        "noise_level": random.uniform(45, 70),
        "waste_fill": random.uniform(20, 55),
    }


def generate_tick():
    """Advance every zone's simulated state by one step and persist rows.
    Call this from the scheduler (see app.py) inside an app context."""
    locations = Location.query.all()
    tod = _time_of_day_factor()

    for loc in locations:
        if loc.location_id not in _state:
            _init_state(loc.location_id)
        s = _state[loc.location_id]

        traffic_factor = 0.8 + loc.population / 3000
        target_vehicles = (500 + tod * 380) * traffic_factor
        target_speed = 48 - tod * 11 - max(0, traffic_factor - 1) * 8
        s["vehicle_count"] = _clamp(
            s["vehicle_count"] + (target_vehicles - s["vehicle_count"]) * 0.18 + random.uniform(-25, 25),
            150, 2200,
        )
        s["average_speed"] = _clamp(
            s["average_speed"] + (target_speed - s["average_speed"]) * 0.18 + random.uniform(-1.8, 1.8),
            8, 60,
        )
        congestion = _clamp((s["vehicle_count"] / 1400) * 60 + (55 - s["average_speed"]) * 0.6 + random.uniform(-4, 4), 2, 100)

        s["temperature"] = _clamp(s["temperature"] + random.uniform(-0.4, 0.5), 20, 42)
        s["humidity"] = _clamp(s["humidity"] + random.uniform(-2, 2), 20, 95)
        target_air_quality = 42 + congestion * 0.18
        s["air_quality"] = _clamp(
            s["air_quality"] + (target_air_quality - s["air_quality"]) * 0.12 + random.uniform(-2, 2),
            8, 100,
        )
        s["noise_level"] = _clamp(s["noise_level"] + random.uniform(-2, 2) + tod * 4, 30, 100)

        s["waste_fill"] = s["waste_fill"] + random.uniform(0.3, 2.2)
        if s["waste_fill"] >= 98:
            s["waste_fill"] = random.uniform(5, 15)  # simulated collection
        s["waste_fill"] = _clamp(s["waste_fill"], 0, 100)

        db.session.add(Traffic(location_id=loc.location_id, vehicle_count=int(s["vehicle_count"]),
                                average_speed=s["average_speed"], congestion_level=congestion))
        db.session.add(Environment(location_id=loc.location_id, temperature=s["temperature"],
                                    humidity=s["humidity"], air_quality=s["air_quality"], noise_level=s["noise_level"]))
        db.session.add(Waste(location_id=loc.location_id, fill_percentage=s["waste_fill"]))

    db.session.commit()


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))
