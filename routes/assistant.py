import json
import re
from urllib.parse import quote

from flask import Blueprint, current_app, jsonify, request
from database.models import Location, Traffic, Environment, Waste, Complaint
import city_brain
from weather import current_temperature_for_place, current_temperatures_for_locations

bp = Blueprint("assistant", __name__)


def _latest_map(model):
    """location_id -> latest row, in one pass."""
    out = {}
    for row in model.query.order_by(model.timestamp.asc()).all():
        out[row.location_id] = row
    return out


def _canonical_place(value):
    return " ".join(value.strip(" ,.?").split())


def _city_context(locations, traffic, environment, waste):
    areas = []
    for location in locations:
        traffic_reading = traffic.get(location.location_id)
        environment_reading = environment.get(location.location_id)
        waste_reading = waste.get(location.location_id)
        areas.append({
            "area": location.name,
            "zone": location.zone,
            "traffic": ({
                "congestion_percent": round(traffic_reading.congestion_level, 1),
                "vehicles": traffic_reading.vehicle_count,
                "average_speed_kmh": round(traffic_reading.average_speed, 1),
                "recorded_at": traffic_reading.timestamp.isoformat(),
            } if traffic_reading else None),
            "environment": ({
                "aqi": round(environment_reading.air_quality, 1),
                "temperature_c": round(environment_reading.temperature, 1),
                "humidity_percent": round(environment_reading.humidity, 1),
                "noise_db": round(environment_reading.noise_level, 1),
                "recorded_at": environment_reading.timestamp.isoformat(),
            } if environment_reading else None),
            "waste": ({
                "bin_fill_percent": round(waste_reading.fill_percentage, 1),
                "recorded_at": waste_reading.timestamp.isoformat(),
            } if waste_reading else None),
        })
    return json.dumps({"data_type": "simulated demo sensor readings", "areas": areas})


def _model_answer(question, conversation, city_context):
    from google import genai
    from google.genai import types

    instructions = (
        "You are the conversational assistant for a Bengaluru smart-city dashboard. "
        "Answer the user's actual question directly and naturally, including general questions outside the dashboard. "
        "The attached city readings are simulated demo data, not real-world traffic, pollution, or waste measurements. "
        "Use them only for questions about this dashboard and never describe them as actual live city data. "
        "Use Google Search when current facts, recent events, or reliable sources would improve the answer. "
        "Never invent citations, current facts, route distances, journey times, fares, or transit operations. "
        "Be explicit about uncertainty, ask a concise follow-up if a place or "
        "request is ambiguous, and keep the response useful rather than replying with a generic capabilities list."
    )
    valid_messages = []
    if isinstance(conversation, list):
        for message in conversation[-12:]:
            if not isinstance(message, dict):
                continue
            role = message.get("role")
            content = message.get("content")
            if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                valid_messages.append({"role": role, "content": content.strip()[:3000]})
    if valid_messages and valid_messages[0]["role"] == "assistant":
        valid_messages.pop(0)
    if not valid_messages or valid_messages[-1] != {"role": "user", "content": question}:
        valid_messages.append({"role": "user", "content": question})

    contents = [
        {
            "role": "user" if message["role"] == "user" else "model",
            "parts": [{"text": message["content"]}],
        }
        for message in valid_messages
    ]
    client = genai.Client(api_key=current_app.config["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=current_app.config["GEMINI_MODEL"],
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=instructions + "\nDashboard readings:\n" + city_context,
            max_output_tokens=700,
            temperature=0.2,
            tools=(
                [types.Tool(google_search=types.GoogleSearch())]
                if current_app.config["GEMINI_SEARCH_ENABLED"] else None
            ),
        ),
    )
    answer = response.text
    if not answer or not answer.strip():
        raise RuntimeError("The AI provider returned an empty response.")
    sources = []
    seen_urls = set()
    for candidate in response.candidates or []:
        metadata = getattr(candidate, "grounding_metadata", None)
        for chunk in getattr(metadata, "grounding_chunks", None) or []:
            web_source = getattr(chunk, "web", None)
            url = getattr(web_source, "uri", None)
            if isinstance(url, str) and url.startswith("https://") and url not in seen_urls:
                seen_urls.add(url)
                sources.append({"label": getattr(web_source, "title", None) or url, "url": url})
    return answer.strip(), sources


@bp.route("/api/assistant/status", methods=["GET"])
def assistant_status():
    return jsonify({
        "ai_enabled": bool(current_app.config["GEMINI_API_KEY"]),
        "search_enabled": bool(current_app.config["GEMINI_SEARCH_ENABLED"]),
    })


@bp.route("/api/assistant", methods=["POST"])
def assistant():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    lower = question.lower()

    route_question = re.split(r"[?.!]", question, maxsplit=1)[0].strip()
    route_match = re.search(
        r"\b(?:how\s+(?:do i|can i|to)\s+(?:get|go)\s+from|directions?\s+from|route\s+from|navigate\s+from)\s+(.+?)\s+to\s+(.+)$",
        route_question,
        re.IGNORECASE,
    )
    if route_match:
        origin = _canonical_place(route_match.group(1))
        destination = _canonical_place(route_match.group(2))
        directions_base = (
            "https://www.google.com/maps/dir/?api=1"
            f"&origin={quote(origin + ', Bengaluru, India')}"
            f"&destination={quote(destination + ', Bengaluru, India')}"
        )
        asks_fare = bool(re.search(r"\b(how much|fare|cost|price|bmtc|bus|auto|metro)\b", question, re.IGNORECASE))
        if asks_fare:
            auto_estimate = (
                "Auto: the daytime meter rate is ₹36 for the first 2 km, then ₹18 per additional km; "
                "a 50% night surcharge applies from 10 pm to 5 am. Distance depends on the route."
            )
            metro_note = "Metro: Fares depend on the operating stations and route; use the Metro options link to check this trip."
            return jsonify({
                "answer": (
                    f"For {origin} to {destination}:\n"
                    "BMTC: The ticket depends on the service and stages travelled. Check the official fare calculator.\n"
                    f"{auto_estimate}\n"
                    f"{metro_note}"
                ),
                "links": [
                    {"label": "BMTC fare calculator", "url": "https://nammabmtcapp.karnataka.gov.in/commuter/fare-calculator"},
                    {"label": "Bus options in Google Maps", "url": directions_base + "&travelmode=transit&transit_mode=bus"},
                    {"label": "Metro Timings","url": "https://www.bmrc.co.in/metro-timings"},
                    {"label": "Metro route map", "url": "https://www.bmrc.co.in/metro-route-map"},
                    {"label": "Metro fare calculator", "url": "https://www.bmrc.co.in/metro-fare-calculator"},
                    {"label": "Metro station list", "url": "https://www.bmrc.co.in/metro-station-list"},
                    {"label": "Metro options in Google Maps", "url": directions_base + "&travelmode=transit&transit_mode=subway"},
                    {"label": "Road route in Google Maps", "url": directions_base + "&travelmode=driving"},
                ],
            })

        maps_url = directions_base + "&travelmode=driving"
        return jsonify({
            "answer": f"Here are driving directions from {origin} to {destination} in Bengaluru.",
            "maps_url": maps_url,
            "maps_label": "Open driving directions in Google Maps",
        })

    locations = Location.query.all()
    traffic = _latest_map(Traffic)
    environment = _latest_map(Environment)
    waste = _latest_map(Waste)

    area = next((location for location in sorted(locations, key=lambda item: len(item.name), reverse=True)
                 if location.name.lower() in lower or location.zone.lower() in lower), None)

    if re.fullmatch(r"(?:hello|hi|hey|good morning|good afternoon|good evening)[!.?,\s]*", lower):
        return jsonify({"answer": "Hi! I can check Bengaluru traffic, compare areas, and summarize air quality, waste, and alerts. What would you like to know?"})

    if re.search(r"\b(?:temperatures?|temps?|weather)\b", lower):
        asks_for_all_areas = bool(re.search(r"\b(?:all|every|each|across|citywide)\b", lower))
        if asks_for_all_areas:
            live_temperatures = current_temperatures_for_locations(locations)
            readings = [
                f"{location.name}: {value['temperature']:.1f}°C"
                for location in locations
                if (value := live_temperatures.get(location.location_id))
            ]
            if readings:
                updated_at = next((
                    value["time"] for location in locations
                    if (value := live_temperatures.get(location.location_id))
                ), None)
                return jsonify({
                    "answer": "Current outdoor temperatures for the dashboard's Bengaluru areas: "
                              + "; ".join(readings)
                              + (f". Updated {updated_at} IST." if updated_at else "."),
                    "links": [{"label": "Weather data by Open-Meteo", "url": "https://open-meteo.com/"}],
                })

        place = area.name if area else None
        if not place:
            place_match = re.search(
                r"\b(?:in|at|near|around|for)\s+(.+?)(?:[?.!,]|$)",
                question,
                re.IGNORECASE,
            )
            if place_match:
                place = re.sub(
                    r"\b(?:right now|currently|today|please|area)\b",
                    "",
                    place_match.group(1),
                    flags=re.IGNORECASE,
                ).strip(" ,.")
        if not place:
            place = "Bengaluru"
        try:
            reading = current_temperature_for_place(place)
        except LookupError:
            return jsonify({"answer": f"I couldn't match {place} to Bengaluru, Karnataka. Try a Bengaluru neighborhood or locality name."}), 404
        except Exception:
            current_app.logger.exception("The live weather lookup failed")
            return jsonify({"error": "Live temperature is temporarily unavailable. Please try again shortly."}), 503
        return jsonify({
            "answer": (
                f"The current outdoor temperature in {reading['place']}, Bengaluru is "
                f"{reading['temperature']:.1f}°C"
                + (f" as of {reading['time']} IST." if reading.get("time") else ".")
            ),
            "links": [{"label": "Weather data by Open-Meteo", "url": "https://open-meteo.com/"}],
        })

    if current_app.config["GEMINI_API_KEY"]:
        try:
            answer, sources = _model_answer(
                question,
                data.get("messages"),
                _city_context(locations, traffic, environment, waste),
            )
            response = {"answer": answer}
            if sources:
                response["links"] = sources
            return jsonify(response)
        except Exception as error:
            current_app.logger.exception("The configured AI assistant request failed")
            status_code = getattr(error, "status_code", None)
            if status_code == 429 or "RESOURCE_EXHAUSTED" in str(error):
                message = "Gemini's API quota is exhausted. Check your Google AI Studio usage or billing, then try again."
            elif status_code == 503 or "UNAVAILABLE" in str(error):
                message = "Gemini is temporarily at capacity. Please try again shortly."
            elif status_code == 403 or "PERMISSION_DENIED" in str(error):
                message = "Gemini rejected this API key. Check that the key is valid and Gemini API access is enabled."
            else:
                message = "Gemini could not answer this request right now. Check the server log for details and try again."
            return jsonify({
                "error": message
            }), 503

    asks_traffic = any(word in lower for word in ("traffic", "congestion", "vehicle", "vehicles", "speed", "commute", "jam"))
    asks_waste = any(word in lower for word in ("waste", "garbage", "bin", "bins", "overflow"))
    asks_air = any(word in lower for word in ("air quality", "aqi", "pollution", "air pollution"))
    asks_environment = asks_air or any(word in lower for word in ("temperature", "humidity", "noise"))
    asks_highest = any(word in lower for word in ("highest", "most", "worst", "busiest", "heaviest"))

    if asks_traffic:
        available = [location for location in locations if location.location_id in traffic]
        if asks_highest or ("which" in lower and not area):
            worst = max(available, key=lambda location: traffic[location.location_id].congestion_level, default=None)
            if not worst:
                return jsonify({"answer": "Traffic readings are not available yet. Please try again in a few seconds."})
            reading = traffic[worst.location_id]
            answer = (f"{worst.name} ({worst.zone}) is busiest right now: "
                      f"{round(reading.congestion_level)}% congestion, {round(reading.vehicle_count)} vehicles, "
                      f"and an average speed of {round(reading.average_speed, 1)} km/h.")
            return jsonify({"answer": answer})

        if area:
            reading = traffic.get(area.location_id)
            if not reading:
                return jsonify({"answer": f"I don't have a current traffic reading for {area.name} yet."})
            answer = (f"In {area.name} ({area.zone}), traffic is at {round(reading.congestion_level)}% congestion. "
                      f"There are about {round(reading.vehicle_count)} vehicles, moving at an average "
                      f"of {round(reading.average_speed, 1)} km/h.")
            return jsonify({"answer": answer})

        place_match = re.search(
            r"\b(?:traffic|congestion|road conditions?)\s+(?:at|in|near|around)\s+(.+?)[?.!]*$",
            question,
            re.IGNORECASE,
        )
        if place_match:
            place = place_match.group(1).strip(" ,.")
            maps_url = (
                "https://www.google.com/maps/search/?api=1"
                f"&query={quote(place + ', Bengaluru, India')}"
            )
            monitored = ", ".join(location.name for location in locations)
            return jsonify({
                "answer": (f"{place} is not one of this dashboard's monitored sensor areas, so I can't give a live reading there. "
                           f"I currently track {monitored}. You can check the requested place on Google Maps."),
                "maps_url": maps_url,
                "maps_label": f"Open {place} in Google Maps",
            })

        if any(word in lower for word in ("areas", "which zones", "where", "across", "citywide")):
            busy = sorted(available, key=lambda location: traffic[location.location_id].congestion_level, reverse=True)
            summary = ", ".join(f"{location.name} {round(traffic[location.location_id].congestion_level)}%" for location in busy)
            return jsonify({"answer": "Current Bengaluru congestion by area: " + summary + "."})

    if "high-risk" in lower or "high risk" in lower:
        risky = [f"{l.name} ({l.zone})" for l in locations if (
            (l.location_id in traffic and traffic[l.location_id].congestion_level > 65) or
            (l.location_id in environment and environment[l.location_id].air_quality > 70) or
            (l.location_id in waste and waste[l.location_id].fill_percentage > 85)
        )]
        answer = ("Flagged zones: " + ", ".join(risky) + " — elevated traffic, air quality, or waste levels."
                   ) if risky else "No zones currently exceed the risk thresholds."
        return jsonify({"answer": answer, "highlight_zones": risky})

    if asks_waste:
        if area:
            reading = waste.get(area.location_id)
            if not reading:
                return jsonify({"answer": f"I don't have a current waste reading for {area.name} yet."})
            answer = f"Waste bins in {area.name} ({area.zone}) are {round(reading.fill_percentage)}% full."
            if reading.fill_percentage + 25 > 90:
                answer += " They may need collection soon."
            return jsonify({"answer": answer})

        overflow = [f"{l.name} ({l.zone})" for l in locations if l.location_id in waste and waste[l.location_id].fill_percentage + 25 > 90]
        answer = ("Bins likely to overflow today: " + ", ".join(overflow) + "."
                   ) if overflow else "No bins are projected to overflow within the next few hours."
        return jsonify({"answer": answer})

    if "alert" in lower or "incident" in lower:
        alerts = city_brain.evaluate()
        answer = (f"{len(alerts)} active alert(s). Most recent: \"{alerts[0]['title']}\" — {alerts[0]['detail']}"
                   ) if alerts else "No active alerts right now — all systems nominal."
        return jsonify({"answer": answer, "alerts": alerts[:5]})

    if asks_environment:
        if area:
            reading = environment.get(area.location_id)
            if not reading:
                return jsonify({"answer": f"I don't have a current environment reading for {area.name} yet."})
            if asks_air:
                answer = f"The latest air-quality reading for {area.name} ({area.zone}) is AQI {round(reading.air_quality)}."
            else:
                answer = (f"In {area.name} ({area.zone}), the latest readings are "
                          f"{round(reading.temperature, 1)}°C, {round(reading.humidity)}% humidity, "
                          f"AQI {round(reading.air_quality)}, and {round(reading.noise_level)} dB noise.")
            return jsonify({"answer": answer})

        values = [e.air_quality for e in environment.values()]
        avg = sum(values) / len(values) if values else 0
        answer = (f"Citywide average AQI is {round(avg)}. " +
                  ("Several zones are trending toward poor air quality." if avg > 65 else "Air quality is within an acceptable range overall."))
        return jsonify({"answer": answer})

    if any(word in lower for word in ("city status", "citywide status", "how is bengaluru", "how's bengaluru", "summary", "overview")):
        traffic_values = [row.congestion_level for row in traffic.values()]
        aqi_values = [row.air_quality for row in environment.values()]
        waste_values = [row.fill_percentage for row in waste.values()]
        if not traffic_values:
            return jsonify({"answer": "Bengaluru readings are still being collected. Please try again shortly."})
        answer = (f"Bengaluru update: average congestion is {round(sum(traffic_values) / len(traffic_values))}%, "
                  f"average AQI is {round(sum(aqi_values) / len(aqi_values)) if aqi_values else 'unavailable'}, "
                  f"and average bin fill is {round(sum(waste_values) / len(waste_values)) if waste_values else 'unavailable'}%.")
        return jsonify({"answer": answer})

    if "complaint" in lower:
        count = Complaint.query.count()
        return jsonify({"answer": f"There are {count} complaint(s) currently recorded in the Bengaluru dashboard."})

    if re.search(r"\b(how much|fare|cost|price|bmtc|bus|auto|metro)\b", lower):
        return jsonify({
            "answer": "Tell me your start and destination, and I can open the route options. BMTC fares depend on the service and stages; Bengaluru auto meter fare is ₹36 for the first 2 km and ₹18 per additional km (daytime)."
        })

    return jsonify({"answer": "This is demo mode, so open-ended AI answers are not enabled yet. Add a Gemini API key to your local .env file to enable general questions. I can still answer about dashboard traffic, air quality, waste, complaints, and alerts for all 28 monitored areas in Bengaluru."})
