from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

_BENGALURU_LOCATIONS = [
    {"name": "Yalahanka", "latitude": 13.1007, "longitude": 77.5963, "zone": "North Bengaluru", "population": 500},
    {"name": "K. R. Puram", "latitude": 13.0050, "longitude": 77.6950, "zone": "East Bengaluru", "population": 500},
    {"name": "Byatarayanapura", "latitude": 13.0683, "longitude": 77.591, "zone": "North Bengaluru", "population": 500},
    {"name": "Yeshwanthpura", "latitude": 13.0236, "longitude": 77.5542, "zone": "West Bengaluru", "population": 500},
    {"name": "Rajarajeshwarinagar", "latitude": 12.9061, "longitude": 77.5196, "zone": "South Bengaluru", "population": 500},
    {"name": "Dasarahalli", "latitude": 13.0433, "longitude": 77.5126, "zone": "West Bengaluru", "population": 500},
    {"name": "Mahalakshmi Layout", "latitude": 13.0113, "longitude": 77.5447, "zone": "West Bengaluru", "population": 500},
    {"name": "Malleshwaram", "latitude": 13.0027, "longitude": 77.5703, "zone": "West Bengaluru", "population": 500},
    {"name": "Hebbal", "latitude": 13.0382, "longitude": 77.5919, "zone": "North Bengaluru", "population": 500},
    {"name": "Pulakeshinagar", "latitude": 12.9982, "longitude": 77.6133, "zone": "East Bengaluru", "population": 500},
    {"name": "Sarvagnanagar", "latitude": 12.9955, "longitude": 77.6239, "zone": "East Bengaluru", "population": 500},
    {"name": "C. V. Raman Nagar", "latitude": 12.9856, "longitude": 77.665, "zone": "East Bengaluru", "population": 500},
    {"name": "Shivajinagar", "latitude": 12.9855, "longitude": 77.6054, "zone": "Central Bengaluru", "population": 500},
    {"name": "Shanti Nagar", "latitude": 12.9555, "longitude": 77.5924, "zone": "Central Bengaluru", "population": 500},
    {"name": "Gandhi Nagar", "latitude": 12.9772, "longitude": 77.58, "zone": "Central Bengaluru", "population": 500},
    {"name": "Rajaji Nagar", "latitude": 12.9945, "longitude": 77.5543, "zone": "West Bengaluru", "population": 500},
    {"name": "Govindaraja Nagara", "latitude": 12.9777, "longitude": 77.5407, "zone": "West Bengaluru", "population": 500},
    {"name": "Vijayanagar", "latitude": 12.971, "longitude": 77.5374, "zone": "West Bengaluru", "population": 500},
    {"name": "Chamrajpet", "latitude": 12.9584, "longitude": 77.5629, "zone": "Central Bengaluru", "population": 500},
    {"name": "Chickpete", "latitude": 12.9698, "longitude": 77.5757, "zone": "Central Bengaluru", "population": 500},
    {"name": "Basavanagudi", "latitude": 12.9417, "longitude": 77.5755, "zone": "South Bengaluru", "population": 500},
    {"name": "Padmanabhanagar", "latitude": 12.9181, "longitude": 77.5577, "zone": "South Bengaluru", "population": 500},
    {"name": "BTM Layout", "latitude": 12.914, "longitude": 77.6103, "zone": "South Bengaluru", "population": 500},
    {"name": "Jayanagar", "latitude": 12.9293, "longitude": 77.5824, "zone": "South Bengaluru", "population": 500},
    {"name": "Mahadevapura", "latitude": 12.9965, "longitude": 77.6927, "zone": "East Bengaluru", "population": 500},
    {"name": "Bommanahalli", "latitude": 12.9035, "longitude": 77.623, "zone": "South Bengaluru", "population": 500},
    {"name": "Bangalore South", "latitude": 12.8592, "longitude": 77.6628, "zone": "South Bengaluru", "population": 500},
    {"name": "Anekal", "latitude": 12.8482, "longitude": 77.6921, "zone": "South Bengaluru", "population": 500}
]

_LEGACY_LOCATION_NAMES = {
    "Residential North": "Hebbal",
    "Commercial Core": "Majestic",
    "Industrial Belt": "Whitefield",
    "Tech Park": "Electronic City",
    "Riverside": "Jayanagar",
}


def init_db(app):
    """Attach SQLAlchemy, migrate demo zones and seed an empty database."""
    db.init_app(app)
    with app.app_context():
        from database.models import Location
        db.create_all()

        if Location.query.count() == 0:
            db.session.add_all(Location(**location) for location in _BENGALURU_LOCATIONS)
            db.session.commit()
            return

        locations_by_name = {location["name"]: location for location in _BENGALURU_LOCATIONS}
        migrated = False
        for location in Location.query.all():
            new_name = _LEGACY_LOCATION_NAMES.get(location.name)
            if new_name:
                location.name = new_name
                location.zone = locations_by_name[new_name]["zone"]
                location.latitude = locations_by_name[new_name]["latitude"]
                location.longitude = locations_by_name[new_name]["longitude"]
                migrated = True
        if migrated:
            db.session.commit()
