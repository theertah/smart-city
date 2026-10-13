"""Forecasts a bin's fill level a few hours ahead using linear regression
over its recent fill-rate trend."""
from database.models import Waste

MIN_ROWS_TO_TRAIN = 6
FORECAST_HOURS = 5


def predict_fill(location_id, reading_interval_minutes=5):
    rows = (
        Waste.query.filter_by(location_id=location_id)
        .order_by(Waste.timestamp.desc())
        .limit(24)
        .all()
    )
    rows = list(reversed(rows))  # oldest -> newest
    current_fill = rows[-1].fill_percentage if rows else 0

    if len(rows) < MIN_ROWS_TO_TRAIN:
        # heuristic: assume ~1.2%/reading fill rate
        predicted = min(100, current_fill + 1.2 * (FORECAST_HOURS * 60 / reading_interval_minutes))
        return {"current": round(current_fill, 1), "predicted": round(predicted, 1), "model": "heuristic"}

    import numpy as np
    from sklearn.linear_model import LinearRegression

    X = np.array(range(len(rows))).reshape(-1, 1)
    y = np.array([r.fill_percentage for r in rows])

    model = LinearRegression()
    model.fit(X, y)

    steps_ahead = int(FORECAST_HOURS * 60 / reading_interval_minutes)
    future_x = np.array([[len(rows) - 1 + steps_ahead]])
    predicted = float(model.predict(future_x)[0])

    # if the trend implies a collection would happen before the forecast point, cap sensibly
    predicted = max(0, min(100, predicted))
    return {"current": round(current_fill, 1), "predicted": round(predicted, 1), "model": "linear_regression"}
