from datetime import datetime
from database.db import db


class Location(db.Model):
    __tablename__ = "locations"
    location_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    zone = db.Column(db.String(50), nullable=False)
    population = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "location_id": self.location_id, "name": self.name,
            "zone": self.zone, "latitude": self.latitude,
            "longitude": self.longitude, "population": self.population,
        }


class Traffic(db.Model):
    __tablename__ = "traffic"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    vehicle_count = db.Column(db.Integer)
    average_speed = db.Column(db.Float)
    congestion_level = db.Column(db.Float)

    def to_dict(self):
        return {
            "location_id": self.location_id, "timestamp": self.timestamp.isoformat(),
            "vehicle_count": self.vehicle_count, "average_speed": self.average_speed,
            "congestion_level": self.congestion_level,
        }


class Environment(db.Model):
    __tablename__ = "environment"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    air_quality = db.Column(db.Float)
    noise_level = db.Column(db.Float)

    def to_dict(self):
        return {
            "location_id": self.location_id, "timestamp": self.timestamp.isoformat(),
            "temperature": self.temperature, "humidity": self.humidity,
            "air_quality": self.air_quality, "noise_level": self.noise_level,
        }


class Waste(db.Model):
    __tablename__ = "waste"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    fill_percentage = db.Column(db.Float)

    def to_dict(self):
        return {
            "location_id": self.location_id, "timestamp": self.timestamp.isoformat(),
            "fill_percentage": self.fill_percentage,
        }


class Energy(db.Model):
    __tablename__ = "energy"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    consumption = db.Column(db.Float)

    def to_dict(self):
        return {
            "location_id": self.location_id, "timestamp": self.timestamp.isoformat(),
            "consumption": self.consumption,
        }


class Complaint(db.Model):
    __tablename__ = "complaints"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"))
    category = db.Column(db.String(50))
    department = db.Column(db.String(100))
    description = db.Column(db.Text)
    severity = db.Column(db.Integer)
    priority_score = db.Column(db.Integer)
    status = db.Column(db.String(20), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "location_id": self.location_id, "category": self.category,
            "department": self.department, "description": self.description,
            "severity": self.severity, "priority_score": self.priority_score,
            "status": self.status, "created_at": self.created_at.isoformat(),
        }


class Prediction(db.Model):
    __tablename__ = "predictions"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"))
    prediction_type = db.Column(db.String(50))
    prediction = db.Column(db.Float)
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "location_id": self.location_id, "prediction_type": self.prediction_type,
            "prediction": self.prediction, "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }
