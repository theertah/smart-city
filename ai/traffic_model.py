"""Predicts congestion 30 minutes ahead from recent traffic history.

Trains a RandomForestRegressor on-the-fly from whatever history the
simulator has accumulated in the database. Falls back to a simple
heuristic until enough rows exist to train on.
"""
from database.models import Traffic

MIN_ROWS_TO_TRAIN = 30


def _build_training_set(location_id):
    rows = (
        Traffic.query.filter_by(location_id=location_id)
        .order_by(Traffic.timestamp.asc())
        .all()
    )
    if len(rows) < MIN_ROWS_TO_TRAIN:
        return None, None

    import numpy as np

    X, y = [], []
    for i in range(len(rows) - 1):
        r = rows[i]
        nxt = rows[i + 1]
        X.append([r.vehicle_count, r.average_speed, r.congestion_level])
        y.append(nxt.congestion_level)
    return np.array(X), np.array(y)


def predict_congestion(location_id, latest_reading):
    """latest_reading: dict with vehicle_count, average_speed, congestion_level"""
    X, y = _build_training_set(location_id)

    if X is None:
        # heuristic fallback: recent trend + light mean reversion
        base = latest_reading["congestion_level"]
        predicted = max(0, min(100, base + (base - 50) * 0.15))
        return {"prediction": round(predicted, 1), "confidence": 0.4, "model": "heuristic"}

    import numpy as np
    from sklearn.ensemble import RandomForestRegressor

    model = RandomForestRegressor(n_estimators=80, max_depth=6, random_state=42)
    model.fit(X, y)
    features = np.array([[latest_reading["vehicle_count"], latest_reading["average_speed"], latest_reading["congestion_level"]]])
    predicted = float(model.predict(features)[0])

    # crude confidence proxy: agreement across the forest's trees
    tree_preds = [t.predict(features)[0] for t in model.estimators_]
    spread = float(np.std(tree_preds))
    confidence = max(0.4, min(0.95, 1 - spread / 50))

    return {"prediction": round(max(0, min(100, predicted)), 1), "confidence": round(confidence, 2), "model": "random_forest"}
