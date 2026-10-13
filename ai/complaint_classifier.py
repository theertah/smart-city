"""Keyword-based NLP classification for citizen complaints. Swap this for
a trained text classifier (e.g. TF-IDF + LogisticRegression) later without
changing the routes that call it."""

CATEGORY_RULES = [
    ("ROAD DAMAGE", "Road Maintenance", ["pothole", "road", "crack", "pavement", "sidewalk", "footpath"]),
    ("WASTE", "Sanitation", ["garbage", "waste", "bin", "trash", "overflow", "dump"]),
    ("ENERGY", "Electrical Dept.", ["streetlight", "light", "power", "electric", "transformer", "outage"]),
    ("WATER", "Water Board", ["water", "leak", "pipe", "drain", "sewage", "flood"]),
    ("NOISE", "Enforcement", ["noise", "loud", "construction at night", "horn"]),
    ("TRAFFIC", "Traffic Police", ["traffic", "signal", "jam", "parking", "congestion", "accident",""]),
]

SEVERITY_WORDS = {
    "urgent": 3, "dangerous": 4, "huge": 2, "severe": 4, "broken": 2,
    "unsafe": 3, "immediately": 2, "flood": 3, "fire": 4, "collapsed": 3,
}


def classify(text):
    lower = text.lower()
    category, department = "GENERAL", "Municipal Corporation"
    for cat, dept, keywords in CATEGORY_RULES:
        if any(k in lower for k in keywords):
            category, department = cat, dept
            break

    severity = 3
    for word, weight in SEVERITY_WORDS.items():
        if word in lower:
            severity += weight
    severity = max(1, min(10, severity))

    return {"category": category, "department": department, "severity": severity}


def priority_score(severity, same_category_reports_in_zone, population_weight):
    return severity + same_category_reports_in_zone * 2 + population_weight


def priority_label(score):
    if score >= 16:
        return "HIGH"
    if score >= 9:
        return "MEDIUM"
    return "LOW"
