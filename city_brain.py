"""The main coding feature of the project. Reads the latest reading from
every module for every zone and looks for relationships between them,
combining rule-based logic with the ML predictions/anomalies from ai/.
Returns a flat list of alert dicts, newest first.
"""
from database.models import Location, Traffic, Environment, Waste
from ai import anomaly

ANOMALY_METRICS = {
    "traffic": (Traffic, "congestion_level"),
    "environment": (Environment, "air_quality"),
}


def _latest(model, location_id):
    return model.query.filter_by(location_id=location_id).order_by(model.timestamp.desc()).first()


def _recent_series(model, field, location_id, limit=20):
    rows = model.query.filter_by(location_id=location_id).order_by(model.timestamp.desc()).limit(limit).all()
    rows = list(reversed(rows))
    return [getattr(r, field) for r in rows]


def evaluate():
    alerts = []
    for loc in Location.query.all():
        t = _latest(Traffic, loc.location_id)
        e = _latest(Environment, loc.location_id)
        w = _latest(Waste, loc.location_id)
        if not (t and e and w):
            continue

        # Rule: traffic-linked air stress
        if t.congestion_level > 70 and e.air_quality > 70:
            alerts.append({
                "severity": "critical", "zone": loc.zone,
                "title": f"Traffic-linked air stress — {loc.zone}",
                "detail": f"{loc.zone} · congestion {round(t.congestion_level)}%, AQI {round(e.air_quality)}",
            })

        # Rule: waste collection needed
        if w.fill_percentage > 85:
            alerts.append({
                "severity": "warning", "zone": loc.zone,
                "title": f"Waste collection needed — {loc.zone}",
                "detail": f"{loc.zone} · {round(w.fill_percentage)}% full",
            })

        # Rule: compound urban stress event
        if t.congestion_level > 65 and e.temperature > 34 and e.air_quality > 65:
            alerts.append({
                "severity": "critical", "zone": loc.zone,
                "title": f"Urban stress event — {loc.zone}",
                "detail": f"Elevated traffic, heat and pollution compounding in {loc.zone}",
            })

        # ML anomaly detection across metrics
        for label, (model, field) in ANOMALY_METRICS.items():
            series = _recent_series(model, field, loc.location_id)
            result = anomaly.detect(series)
            if result.get("is_anomaly"):
                alerts.append({
                    "severity": "critical", "zone": loc.zone,
                    "title": f"Anomaly detected — {label} in {loc.zone}",
                    "detail": f"{loc.zone} · {result['latest']} vs. typical {result['typical']}",
                })

    return alerts
