"""
BCE-4X — Bridge Meteo V3
=========================
Fournit les fonctions legacy (fetch_current_weather, compute_weather_influence)
en redirigeant vers le service meteo V3 (Open-Meteo).
Ce module remplace weather_service_v1.py (PURGE).
"""

import httpx
import logging

logger = logging.getLogger("bionic.weather_bridge_v3")

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


async def fetch_current_weather(lat: float, lng: float) -> dict:
    """Recupere les donnees meteo actuelles via Open-Meteo V3."""
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": ",".join([
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "precipitation", "weather_code", "cloud_cover", "surface_pressure",
            "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
        ]),
        "timezone": "America/Toronto",
        "forecast_days": 1,
    }
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.get(OPEN_METEO_URL, params=params)
        resp.raise_for_status()
        raw = resp.json()

    c = raw.get("current", {})
    return {
        "temperature": c.get("temperature_2m"),
        "humidity": c.get("relative_humidity_2m"),
        "pressure_hpa": c.get("surface_pressure"),
        "wind_speed_kmh": c.get("wind_speed_10m"),
        "wind_direction": c.get("wind_direction_10m"),
        "wind_gusts_kmh": c.get("wind_gusts_10m"),
        "precipitation_1h_mm": c.get("precipitation"),
        "cloud_cover": c.get("cloud_cover"),
        "weather_code": c.get("weather_code"),
        "source": "open-meteo-v3",
    }


def compute_weather_influence(weather_snapshot: dict) -> dict:
    """Calcule les multiplicateurs d'influence meteo par categorie."""
    if not weather_snapshot:
        return None

    temp = weather_snapshot.get("temperature", 10)
    wind = weather_snapshot.get("wind_speed_kmh", 0)
    precip = weather_snapshot.get("precipitation_1h_mm", 0)
    humidity = weather_snapshot.get("humidity", 50)

    # Multiplicateurs base sur les conditions
    temp_factor = 1.0
    if -5 <= temp <= 5:
        temp_factor = 1.15
    elif temp < -15 or temp > 30:
        temp_factor = 0.7

    wind_factor = 1.0
    if 5 <= wind <= 20:
        wind_factor = 1.1
    elif wind > 35:
        wind_factor = 0.6

    precip_factor = 1.0
    if 0.5 <= precip <= 3:
        precip_factor = 1.05
    elif precip > 10:
        precip_factor = 0.65

    return {
        "alimentation": round(temp_factor * precip_factor, 3),
        "corridors": round(wind_factor * precip_factor, 3),
        "repos": round(temp_factor * 0.95, 3),
        "reproduction": round(temp_factor * humidity / 100, 3),
        "global": round((temp_factor + wind_factor + precip_factor) / 3, 3),
    }
