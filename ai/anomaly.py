"""One general-purpose anomaly engine reused across traffic, energy,
waste and environment — trains an IsolationForest per zone on its own
recent history for each metric."""
MIN_ROWS = 15


def detect(values):
    """values: list of floats, oldest -> newest. Returns dict describing
    whether the latest point is anomalous."""
    if len(values) < MIN_ROWS:
        return {"is_anomaly": False, "reason": "insufficient_history"}

    import numpy as np
    from sklearn.ensemble import IsolationForest

    X = np.array(values).reshape(-1, 1)
    model = IsolationForest(contamination=0.08, random_state=42)
    model.fit(X[:-1])  # train on history excluding the latest point
    latest = X[-1].reshape(1, -1)
    pred = model.predict(latest)[0]  # -1 = anomaly, 1 = normal
    score = float(model.decision_function(latest)[0])

    mean = float(np.mean(values[:-1]))
    return {
        "is_anomaly": pred == -1,
        "score": round(score, 3),
        "latest": round(values[-1], 2),
        "typical": round(mean, 2),
    }
