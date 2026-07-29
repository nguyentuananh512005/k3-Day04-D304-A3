from __future__ import annotations

from typing import Any
import requests

from tools._shared import TIMEOUT, err


def get_weather(city: str = "", days: int = 1) -> dict[str, Any]:
    """Fetch current weather and forecast for a given city using Open-Meteo API."""
    try:
        if not city:
            return err("weather", "City parameter is required")
        
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=TIMEOUT)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        
        results = geo_data.get("results")
        if not results:
            return {"tool": "weather", "city": city, "error": "city_not_found", "message": f"City '{city}' not found."}
            
        location = results[0]
        lat, lon = location["latitude"], location["longitude"]
        country = location.get("country", "")
        
        # 2. Weather forecast
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode&forecast_days={days}&timezone=auto"
        w_resp = requests.get(weather_url, timeout=TIMEOUT)
        w_resp.raise_for_status()
        w_data = w_resp.json()
        
        current = w_data.get("current_weather", {})
        return {
            "tool": "weather",
            "city": location.get("name", city),
            "country": country,
            "temperature_celsius": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "weather_code": current.get("weathercode"),
            "is_day": current.get("is_day") == 1,
        }
    except Exception as exc:
        return err("weather", exc)
