import json
import threading
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen


_CACHE_SECONDS = 600
_FAILURE_CACHE_SECONDS = 30
_cache = {}
_cache_lock = threading.Lock()


def _get_json(url, params):
    request = Request(
        f"{url}?{urlencode(params)}",
        headers={"User-Agent": "SmartCityDashboard/1.0"},
    )
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read())


def _cached(key):
    with _cache_lock:
        entry = _cache.get(key)
        if entry and time.monotonic() - entry[0] < entry[1]:
            return entry[2]
    return None


def _store(key, value, ttl=_CACHE_SECONDS):
    with _cache_lock:
        _cache[key] = (time.monotonic(), ttl, value)


def current_temperatures_for_locations(locations):
    locations = [location for location in locations if location.latitude is not None and location.longitude is not None]
    cache_key = ("dashboard", tuple(
        (location.location_id, round(location.latitude, 4), round(location.longitude, 4))
        for location in locations
    ))
    cached = _cached(cache_key)
    if cached is not None:
        return cached

    weather_data = {location.location_id: None for location in locations}
    if not locations:
        return weather_data

    try:
        data = _get_json(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": ",".join(str(location.latitude) for location in locations),
                "longitude": ",".join(str(location.longitude) for location in locations),
                "current": "temperature_2m,relative_humidity_2m",
                "timezone": "Asia/Kolkata",
            },
        )
        aqi_response = _get_json(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            {
                "latitude": ",".join(str(location.latitude) for location in locations),
                "longitude": ",".join(str(location.longitude) for location in locations),
                "current": "european_aqi",
                "timezone": "Asia/Kolkata",
            },
        )
        
        responses = data if isinstance(data, list) else [data]
        aqi_responses = aqi_response if isinstance(aqi_response, list) else [aqi_response]
        
        for location, response, aqi_res in zip(locations, responses, aqi_responses):
            current = response.get("current") or {}
            aqi_current = aqi_res.get("current") or {}
            temp = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            aqi = aqi_current.get("european_aqi")
            
            if temp is not None:
                weather_data[location.location_id] = {
                    "temperature": float(temp),
                    "humidity": humidity,
                    "aqi": aqi,
                    "time": current.get("time"),
                }
    except Exception as e:
        print(f"Weather API error: {e}")

    ttl = _CACHE_SECONDS if all(weather_data.values()) else _FAILURE_CACHE_SECONDS
    _store(cache_key, weather_data, ttl)
    return weather_data


def current_temperature_for_place(place):
    query = " ".join(place.strip().split())
    cache_key = ("place", query.casefold())
    cached = _cached(cache_key)
    if cached is not None:
        return cached

    data = _get_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": query, "count": 10, "language": "en", "format": "json", "countryCode": "IN"},
    )
    places = data.get("results") or []
    place_data = next((item for item in places if
        item.get("country_code") == "IN"
        and item.get("admin1", "").casefold() == "karnataka"
        and any(city in item.get("admin2", "").casefold() for city in ("bengaluru", "bangalore"))
    ), None)
    if not place_data:
        raise LookupError("That place could not be matched to Bengaluru, Karnataka.")

    current = _get_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": place_data["latitude"],
            "longitude": place_data["longitude"],
            "current": "temperature_2m",
            "timezone": "Asia/Kolkata",
        },
    ).get("current") or {}
    temperature = current.get("temperature_2m")
    if temperature is None:
        raise RuntimeError("The weather provider returned no current temperature.")

    result = {
        "place": place_data.get("name", query),
        "temperature": float(temperature),
        "time": current.get("time"),
    }
    _store(cache_key, result)
    return result