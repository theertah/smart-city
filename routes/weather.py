import json
import urllib.request
from flask import Blueprint, jsonify

bp = Blueprint("weather", __name__)

@bp.route("/api/weather")
def current_weather():
    # Bangalore coordinates
    weather_url = "https://api.open-meteo.com/v1/forecast?latitude=12.9716&longitude=77.5946&current=temperature_2m,relative_humidity_2m,wind_speed_10m,is_day&hourly=temperature_2m&forecast_days=1&timezone=Asia%2FKolkata"
    aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=12.9716&longitude=77.5946&current=european_aqi&timezone=Asia%2FKolkata"
    try:
        req1 = urllib.request.Request(weather_url, headers={'User-Agent': 'SmartCityBot'})
        with urllib.request.urlopen(req1) as response1:
            data1 = json.loads(response1.read().decode())
            weather = data1.get("current", {})
            hourly = data1.get("hourly", {})
        
        req2 = urllib.request.Request(aqi_url, headers={'User-Agent': 'SmartCityBot'})
        with urllib.request.urlopen(req2) as response2:
            data2 = json.loads(response2.read().decode())
            aqi_data = data2.get("current", {})

        today = (weather.get("time") or "")[:10]
        forecast = [
            {"time": hour, "temperature": temperature}
            for hour, temperature in zip(hourly.get("time", []), hourly.get("temperature_2m", []))
            if hour.startswith(today) and 6 <= int(hour[11:13]) <= 23
        ]

        return jsonify({
            "temperature": weather.get("temperature_2m"),
            "humidity": weather.get("relative_humidity_2m"),
            "windspeed": weather.get("wind_speed_10m"),
            "is_day": weather.get("is_day"),
            "time": weather.get("time"),
            "aqi": aqi_data.get("european_aqi"),
            "forecast": forecast
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
