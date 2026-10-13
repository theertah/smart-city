from flask import Blueprint, jsonify, request
from database.db import db
from database.models import Location, Complaint
from ai import complaint_classifier

bp = Blueprint("complaints", __name__)


@bp.route("/api/complaints", methods=["GET"])
def list_complaints():
    complaints = Complaint.query.order_by(Complaint.priority_score.desc()).all()
    locations = {location.location_id: location for location in Location.query.all()}
    result = []
    for c in complaints:
        row = c.to_dict()
        location = locations.get(c.location_id)
        row["zone"] = location.zone if location else ""
        row["location_name"] = location.name if location else ""
        row["priority_label"] = complaint_classifier.priority_label(c.priority_score)
        result.append(row)
    return jsonify(result)


@bp.route("/api/complaints", methods=["POST"])
def create_complaint():
    data = request.get_json(force=True)
    text = (data.get("description") or "").strip()
    zone = data.get("zone")
    if not text or not zone:
        return jsonify({"error": "description and zone are required"}), 400

    location = Location.query.filter_by(zone=zone).first()
    if not location:
        return jsonify({"error": "unknown zone"}), 400

    classification = complaint_classifier.classify(text)
    same_category_reports = Complaint.query.filter_by(
        location_id=location.location_id, category=classification["category"]
    ).count()
    population_weight = round((location.population / 1000) * 4)
    score = complaint_classifier.priority_score(
        classification["severity"], same_category_reports, population_weight
    )

    complaint = Complaint(
        location_id=location.location_id,
        category=classification["category"],
        department=classification["department"],
        description=text,
        severity=classification["severity"],
        priority_score=score,
        status="Open",
    )
    db.session.add(complaint)
    db.session.commit()

    row = complaint.to_dict()
    row["zone"] = location.zone
    row["location_name"] = location.name
    row["priority_label"] = complaint_classifier.priority_label(score)
    return jsonify(row), 201


@bp.route("/api/complaints", methods=["DELETE"])
def delete_complaints():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids")
    if not isinstance(ids, list) or not ids:
        return jsonify({"error": "a non-empty ids list is required"}), 400
    if any(type(complaint_id) is not int or complaint_id < 1 for complaint_id in ids):
        return jsonify({"error": "ids must be positive integers"}), 400

    complaints = Complaint.query.filter(Complaint.id.in_(set(ids))).all()
    deleted_count = len(complaints)
    for complaint in complaints:
        db.session.delete(complaint)
    db.session.commit()
    return jsonify({"deleted": deleted_count})
