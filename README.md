# AI Smart City — Backend (Flask + MySQL + scikit-learn)

A software-only smart city platform: a background simulator generates
realistic city sensor data, stores it in a database, trains/uses scikit-learn
models to predict and detect anomalies, and a rule-based "City Brain" combines
everything into alerts. No hardware required.

## Folder structure

```
smart-city-backend/
│
├── app.py                  # Flask app factory, starts the simulator thread
├── config.py                # Reads DB + app config from environment
├── city_brain.py             # Cross-module rule engine (combines all modules)
├── requirements.txt
├── schema.sql                # MySQL schema (optional — SQLite works out of the box)
├── .env.example             # local configuration template; never put API keys in Git
│
├── database/
│   ├── db.py                 # SQLAlchemy engine/session setup
│   └── models.py              # Location, Traffic, Environment, Waste, Complaint, Prediction
│
├── routes/
│   ├── traffic.py
│   ├── waste.py
│   ├── environment.py
│   ├── complaints.py
│   ├── predictions.py         # /api/alerts, /api/predictions
│   └── assistant.py           # /api/assistant (NL question answering)
│
├── ai/
│   ├── traffic_model.py       # RandomForestRegressor — congestion prediction
│   ├── waste_model.py         # Linear regression — bin fill forecasting
│   ├── anomaly.py             # IsolationForest — anomaly detection
│   └── complaint_classifier.py# Keyword-based category + priority scoring
│
├── simulator/
│   └── city_data.py           # Generates fake-but-realistic sensor readings
│
├── templates/
│   ├── index.html             # Dashboard shell
│   └── chatbot/panel.html     # Chatbot panel
│
└── static/
   ├── css/
   └── js/                     # Dashboard, map, and chatbot scripts
```

## Quick start (SQLite — zero setup)

```bash
cd smart-city-backend
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env             # defaults to SQLite, no edits needed
python app.py
```

Open **http://localhost:5000**. The simulator starts automatically and
writes a new reading for every zone every 5 seconds; the ML models train
themselves on the first batch of simulated history (takes a few seconds).
The Environment dashboard's outdoor temperatures come from Open-Meteo current
weather data; humidity, AQI, noise, traffic, and waste remain simulated.
The assistant can look up temperatures for Bengaluru localities and list the
dashboard areas. Weather responses are cached briefly and include the provider
update time.

### Enable Gemini Chat

The assistant uses Google Gemini for general questions when an API key is
configured. Add your key to `GEMINI_API_KEY` in your local `.env` file.
Never commit `.env` or paste the key into chat. `GEMINI_MODEL` defaults to
`gemini-3.8-flash` and can be changed to another model available to your
account. Install dependencies with `pip install -r requirements.txt`, then
restart the app after changing `.env`. Google Search grounding is enabled by
default for current questions; it can consume additional API quota and may be
billable. The chat displays source links when Gemini returns citations.

Without a key, the chatbot stays in demo mode and only answers the dashboard's
local Bengaluru questions. With a key, the model receives the recent chat and
the app's sensor readings; those readings are simulated except for the separate
live temperature lookup.

## Switching to real MySQL (as in the original roadmap)

1. Create the database:
   ```bash
   mysql -u root -p < schema.sql
   ```
2. In `.env`, set:
   ```
   DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost:3306/smart_city
   ```
3. `pip install -r requirements.txt` already includes `PyMySQL`.
4. Run `python app.py` as above — SQLAlchemy will create any tables that
   `schema.sql` didn't, and the app behaves identically.

## API overview

```
GET  /api/traffic            GET  /api/environment
GET  /api/waste
GET  /api/alerts              GET  /api/predictions
GET  /api/complaints          POST /api/complaints
POST /api/assistant
```

## Notes for your project report

- The **AI layer** is real, trained scikit-learn models (`RandomForestRegressor`
   for traffic, `IsolationForest` for anomalies), not hardcoded numbers —
  they retrain periodically on accumulated simulator history.
- The **City Brain** (`city_brain.py`) is a rule engine that reads the latest
  reading from every module and raises cross-module alerts (e.g. high traffic
  + poor air quality together), which is what makes the system feel like one
  coherent platform rather than five unrelated pages.
- Swap `simulator/city_data.py` for real sensor input later without changing
  any other file — it only needs to keep writing rows into the same tables.
