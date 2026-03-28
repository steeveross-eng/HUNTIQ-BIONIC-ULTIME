"""
Weather Engine V9 — BCE-4X UNIFIED v3.0 (Open-Meteo UNIQUE)
================================================================
BCE-4X P0 FIX: OWM NEUTRALISE — Source unique Open-Meteo (identique a V3)
Autorise par STEEVE-MAX — 28 Mars 2026

Regles officielles:
  - Frequence standard: 60 minutes
  - Frequence fallback: 60 minutes
  - Interdiction BCE-4X: mise a jour < 60 minutes
  - Cache obligatoire 60 minutes
  - Source: Open-Meteo UNIQUEMENT (alignement V3)
  - OWM: NEUTRALISE DEFINITIVEMENT

Integration: Open-Meteo API (identique a /api/v3/weather) + fallback algorithmique.
"""

import time
import logging
import httpx
from datetime import datetime, timezone
from .base import BionicEngine, EngineResult

logger = logging.getLogger("bionic.engines.weather_v9")

# BCE-4X P0: OWM NEUTRALISE — Source unique Open-Meteo
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
V9_CACHE_TTL_S = 3600  # 60 minutes — REGLE OFFICIELLE BCE-4X
V9_MIN_INTERVAL_S = 3600  # Interdiction < 60 min

# Cache global V9 (anciennement OWM, maintenant Open-Meteo)
_v9_cache = {
    "data": None,
    "fetched_at": 0,
    "lat": None,
    "lng": None,
    "source": "none",
}

# Impact meteo sur les deplacements
WIND_IMPACT = {
    "calm": {"score_mod": 10, "desc": "Calme - deplacement libre"},
    "light": {"score_mod": 5, "desc": "Vent leger - faible influence"},
    "moderate": {"score_mod": -5, "desc": "Vent modere - deplacement sous couvert prefere"},
    "strong": {"score_mod": -20, "desc": "Vent fort - deplacement reduit, couvert obligatoire"},
    "storm": {"score_mod": -40, "desc": "Tempete - repos force"},
}

TEMP_COMFORT = {
    "moose": {"optimal_min": -10, "optimal_max": 15, "stress_heat": 25, "stress_cold": -35},
    "deer": {"optimal_min": -5, "optimal_max": 20, "stress_heat": 30, "stress_cold": -25},
    "bear": {"optimal_min": 5, "optimal_max": 25, "stress_heat": 35, "stress_cold": -10},
}

# Precipitation types and their ecological impact
PRECIP_IMPACT = {
    "rain_light": {"mod": -3, "desc": "Pluie legere"},
    "rain_moderate": {"mod": -8, "desc": "Pluie moderee"},
    "rain_heavy": {"mod": -15, "desc": "Forte pluie"},
    "snow_light": {"mod": -5, "desc": "Neige legere"},
    "snow_moderate": {"mod": -12, "desc": "Neige moderee"},
    "snow_heavy": {"mod": -25, "desc": "Forte neige - deplacement difficile"},
}

# Moon phase influence on nocturnal activity
MOON_PHASES = {
    "new_moon": {"activity_mod": -10, "desc": "Nouvelle lune - activite nocturne reduite"},
    "waxing": {"activity_mod": 0, "desc": "Lune croissante"},
    "full_moon": {"activity_mod": 15, "desc": "Pleine lune - activite nocturne accrue"},
    "waning": {"activity_mod": 5, "desc": "Lune decroissante"},
}


def _fetch_open_meteo_v3(lat: float, lng: float) -> dict:
    """
    BCE-4X P0: Fetch meteo depuis Open-Meteo (source UNIQUE, identique a V3).
    Respecte la regle BCE-4X des 60 minutes.
    """
    global _v9_cache
    now = time.time()
    elapsed = now - _v9_cache["fetched_at"]

    # BCE-4X: Interdiction de mise a jour < 60 minutes
    if elapsed < V9_MIN_INTERVAL_S and _v9_cache["data"] is not None:
        logger.info(
            f"[WeatherV9-BCE4X] Cache actif ({elapsed:.0f}s/{V9_MIN_INTERVAL_S}s). "
            f"Mise a jour BLOQUEE par regle 60 min."
        )
        return _v9_cache["data"]

    try:
        resp = httpx.get(
            OPEN_METEO_URL,
            params={
                "latitude": round(lat, 4),
                "longitude": round(lng, 4),
                "current": ",".join([
                    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                    "precipitation", "weather_code", "cloud_cover", "surface_pressure",
                    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
                    "visibility",
                ]),
                "timezone": "America/Toronto",
            },
            timeout=5,
        )
        if resp.status_code == 200:
            raw = resp.json()
            weather = _parse_open_meteo_response(raw)
            _v9_cache = {
                "data": weather,
                "fetched_at": now,
                "lat": lat,
                "lng": lng,
                "source": "open-meteo-v3",
            }
            logger.info(f"[WeatherV9] Open-Meteo OK: T={weather['temperature_c']}C, vent={weather['wind_speed_kmh']}km/h")
            return weather
        else:
            logger.warning(f"[WeatherV9] Open-Meteo HTTP {resp.status_code}")
    except Exception as e:
        logger.warning(f"[WeatherV9] Open-Meteo request failed: {e}")

    # Fallback: cache expire ou algorithmique
    if _v9_cache["data"] is not None:
        logger.info("[WeatherV9] Utilisation du cache Open-Meteo expire (fallback)")
        return _v9_cache["data"]

    return _generate_fallback_weather(lat, lng)


def _parse_open_meteo_response(raw: dict) -> dict:
    """Parse la reponse Open-Meteo en format unifie (identique a V3)."""
    c = raw.get("current", {})

    # WMO weather code → condition text
    wmo_code = c.get("weather_code", 0)
    condition = "Clear"
    condition_desc = "Ciel degage"
    if wmo_code == 0:
        condition, condition_desc = "Clear", "Ciel degage"
    elif wmo_code <= 3:
        condition, condition_desc = "Clouds", "Partiellement nuageux"
    elif wmo_code <= 48:
        condition, condition_desc = "Fog", "Brouillard"
    elif wmo_code <= 57:
        condition, condition_desc = "Drizzle", "Bruine"
    elif wmo_code <= 67:
        condition, condition_desc = "Rain", "Pluie"
    elif wmo_code <= 77:
        condition, condition_desc = "Snow", "Neige"
    elif wmo_code <= 82:
        condition, condition_desc = "Rain", "Averses"
    elif wmo_code >= 95:
        condition, condition_desc = "Thunderstorm", "Orage"

    precip = c.get("precipitation", 0) or 0
    # Estimate rain/snow split based on temperature
    temp = c.get("temperature_2m", 10)
    rain_mm = precip if temp > 2 else 0
    snow_mm = precip if temp <= 2 else 0

    return {
        "temperature_c": round(c.get("temperature_2m", 10), 1),
        "feels_like_c": round(c.get("apparent_temperature", 10), 1),
        "humidity_pct": c.get("relative_humidity_2m", 50),
        "pressure_hpa": round(c.get("surface_pressure", 1013), 1),
        "wind_speed_kmh": round(c.get("wind_speed_10m", 0), 1),
        "wind_deg": round(c.get("wind_direction_10m", 0)),
        "wind_gust_kmh": round(c.get("wind_gusts_10m", 0), 1),
        "cloud_cover_pct": c.get("cloud_cover", 0),
        "precipitation_mm": round(precip, 1),
        "rain_mm": round(rain_mm, 1),
        "snow_mm": round(snow_mm, 1),
        "visibility_m": c.get("visibility", 10000),
        "condition": condition,
        "condition_desc": condition_desc,
        "source": "open-meteo-v3",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _generate_fallback_weather(lat: float, lng: float) -> dict:
    """Modele meteorologique algorithmique Quebec (fallback sans API)."""
    month = datetime.now(timezone.utc).month
    hour = datetime.now(timezone.utc).hour

    # Temperature saisonniere Quebec
    seasonal_temp = {
        1: -15, 2: -13, 3: -5, 4: 5, 5: 12, 6: 18,
        7: 22, 8: 20, 9: 14, 10: 7, 11: 0, 12: -10,
    }
    base_temp = seasonal_temp.get(month, 10)
    # Variation diurne
    if 6 <= hour <= 14:
        base_temp += 3
    elif 22 <= hour or hour <= 4:
        base_temp -= 4

    # Altitude effect
    alt_factor = max(0, (lat - 46.0)) * 2
    base_temp -= alt_factor

    return {
        "temperature_c": round(base_temp, 1),
        "feels_like_c": round(base_temp - 2, 1),
        "humidity_pct": 65,
        "pressure_hpa": 1015,
        "wind_speed_kmh": 12,
        "wind_deg": 270,
        "wind_gust_kmh": 20,
        "cloud_cover_pct": 40,
        "precipitation_mm": 0,
        "rain_mm": 0,
        "snow_mm": 0,
        "visibility_m": 10000,
        "condition": "Clear",
        "condition_desc": "modele algorithmique",
        "source": "fallback_algorithmic",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def get_v9_cache_status() -> dict:
    """Retourne le statut du cache V9 Open-Meteo pour BCE-4X."""
    now = time.time()
    elapsed = now - _v9_cache["fetched_at"]
    return {
        "cache_active": _v9_cache["data"] is not None,
        "source": _v9_cache.get("source", "none"),
        "elapsed_s": round(elapsed, 0),
        "ttl_remaining_s": max(0, round(V9_CACHE_TTL_S - elapsed, 0)),
        "update_blocked": elapsed < V9_MIN_INTERVAL_S and _v9_cache["data"] is not None,
        "next_update_in_s": max(0, round(V9_MIN_INTERVAL_S - elapsed, 0)),
        "bce_compliant": True,
        "owm_neutralized": True,
    }


class WeatherEngineV9(BionicEngine):
    ENGINE_ID = "weather"
    ENGINE_NAME = "Weather Engine V9"
    DEFAULT_WEIGHT = 0.10

    def evaluate(self, context):
        lat = context.get("lat", 46.8)
        lng = context.get("lng", -71.2)
        species = context.get("species", "moose")

        # Fetch live weather (respects 60-min BCE-4X rule)
        # BCE-4X P0: Source UNIQUE Open-Meteo (identique a V3)
        weather = context.get("weather", {})
        if not weather or not weather.get("source"):
            weather = _fetch_open_meteo_v3(lat, lng)

        temp = weather.get("temperature_c", 10)
        wind_kmh = weather.get("wind_speed_kmh", 10)
        precip = weather.get("precipitation_mm", 0)
        pressure = weather.get("pressure_hpa", 1013)
        humidity = weather.get("humidity_pct", 50)
        cloud_cover = weather.get("cloud_cover_pct", 40)
        snow_mm = weather.get("snow_mm", 0)
        visibility = weather.get("visibility_m", 10000)
        source = weather.get("source", "unknown")

        # Wind category
        if wind_kmh < 5:
            wind_cat = "calm"
        elif wind_kmh < 15:
            wind_cat = "light"
        elif wind_kmh < 30:
            wind_cat = "moderate"
        elif wind_kmh < 50:
            wind_cat = "strong"
        else:
            wind_cat = "storm"

        wind_mod = WIND_IMPACT[wind_cat]["score_mod"]

        # Temperature comfort (species-specific)
        comfort = TEMP_COMFORT.get(species, TEMP_COMFORT["moose"])
        if comfort["optimal_min"] <= temp <= comfort["optimal_max"]:
            temp_score = 80
        elif temp > comfort["stress_heat"]:
            temp_score = max(10, 80 - (temp - comfort["stress_heat"]) * 5)
        elif temp < comfort["stress_cold"]:
            temp_score = max(10, 80 - (comfort["stress_cold"] - temp) * 3)
        else:
            temp_score = 60

        # Precipitation impact (type-aware)
        precip_mod = 0
        precip_type = "none"
        if snow_mm > 0:
            if snow_mm > 5:
                precip_mod = PRECIP_IMPACT["snow_heavy"]["mod"]
                precip_type = "snow_heavy"
            elif snow_mm > 2:
                precip_mod = PRECIP_IMPACT["snow_moderate"]["mod"]
                precip_type = "snow_moderate"
            else:
                precip_mod = PRECIP_IMPACT["snow_light"]["mod"]
                precip_type = "snow_light"
        elif precip > 0:
            if precip > 10:
                precip_mod = PRECIP_IMPACT["rain_heavy"]["mod"]
                precip_type = "rain_heavy"
            elif precip > 5:
                precip_mod = PRECIP_IMPACT["rain_moderate"]["mod"]
                precip_type = "rain_moderate"
            elif precip > 1:
                precip_mod = PRECIP_IMPACT["rain_light"]["mod"]
                precip_type = "rain_light"

        # Barometric pressure (animals sense pressure changes)
        pressure_mod = 0
        pressure_trend = "stable"
        if pressure < 1000:
            pressure_mod = -10
            pressure_trend = "low_storm"
        elif pressure < 1008:
            pressure_mod = -5
            pressure_trend = "dropping"
        elif pressure > 1025:
            pressure_mod = 8
            pressure_trend = "high_stable"
        elif pressure > 1020:
            pressure_mod = 5
            pressure_trend = "stable_good"

        # Humidity effect (high humidity + heat = stress for moose)
        humidity_mod = 0
        if humidity > 85 and temp > 15:
            humidity_mod = -8
        elif humidity > 90:
            humidity_mod = -5

        # Visibility (fog reduces movement confidence)
        visibility_mod = 0
        if visibility < 500:
            visibility_mod = -10
        elif visibility < 1000:
            visibility_mod = -5

        # Cloud cover effect on thermoregulation
        cloud_mod = 0
        if cloud_cover > 80 and temp < 0:
            cloud_mod = 3  # Insulation effect in cold
        elif cloud_cover < 20 and temp > 20:
            cloud_mod = -5  # Sun exposure stress

        score = max(5, min(100, temp_score + wind_mod + precip_mod + pressure_mod + humidity_mod + visibility_mod + cloud_mod))
        impact = 2 if score > 80 else 1 if score > 65 else 0 if score > 40 else -1 if score > 20 else -2
        certainty = 0.90 if source == "open-meteo-v3" else 0.60 if source == "fallback_algorithmic" else 0.50

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=certainty,
            justification=(
                f"T={temp}C, Vent={wind_kmh}km/h ({wind_cat}), "
                f"Precip={precip}mm ({precip_type}), P={pressure}hPa ({pressure_trend}), "
                f"Source={source}"
            ),
            classification_impact=impact,
            details={
                "temperature_c": temp,
                "feels_like_c": weather.get("feels_like_c", temp),
                "wind_kmh": wind_kmh,
                "wind_category": wind_cat,
                "wind_deg": weather.get("wind_deg", 0),
                "precipitation_mm": precip,
                "precipitation_type": precip_type,
                "snow_mm": snow_mm,
                "pressure_hpa": pressure,
                "pressure_trend": pressure_trend,
                "humidity_pct": humidity,
                "cloud_cover_pct": cloud_cover,
                "visibility_m": visibility,
                "temp_score": round(temp_score, 1),
                "wind_mod": wind_mod,
                "precip_mod": precip_mod,
                "pressure_mod": pressure_mod,
                "humidity_mod": humidity_mod,
                "visibility_mod": visibility_mod,
                "cloud_mod": cloud_mod,
                "source": source,
                "owm_neutralized": True,
                "v9_cache": get_v9_cache_status(),
            },
        )
