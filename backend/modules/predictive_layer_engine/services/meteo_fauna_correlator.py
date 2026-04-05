"""
M3 — Meteo Fauna Correlator : Correlations meteo ↔ activite faunique
======================================================================
Directive x7000-M3 — Phase M3-B MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : weather_fauna_simulation_engine consomme en LECTURE.
NE recree PAS les simulations meteo. AGREGE avec solunar et historique.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None

SPECIES_MAP = {
    "orignal": "moose",
    "chevreuil": "deer",
    "ours_noir": "bear",
    "dindon_sauvage": "wild_turkey"
}


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


def _get_optimal_conditions(species_key: str) -> Dict[str, Any]:
    """PF3-MET1 : Conditions optimales depuis weather_fauna_simulation (LECTURE SEULE)."""
    try:
        from modules.weather_fauna_simulation_engine.v1.service import WeatherFaunaSimulationService
        svc = WeatherFaunaSimulationService()
        optimal = svc.optimal_conditions.get(species_key)
        if optimal:
            return {
                "optimal_temp_min": optimal.optimal_temp_min,
                "optimal_temp_max": optimal.optimal_temp_max,
                "max_wind_speed": optimal.max_wind_speed,
                "pressure_trend": optimal.pressure_trend or "falling",
                "source": "weather_fauna_simulation_engine"
            }
    except Exception:
        pass

    defaults = {
        "moose": {"optimal_temp_min": -5, "optimal_temp_max": 10, "max_wind_speed": 30},
        "deer": {"optimal_temp_min": 2, "optimal_temp_max": 15, "max_wind_speed": 25},
        "bear": {"optimal_temp_min": 10, "optimal_temp_max": 25, "max_wind_speed": 35},
        "wild_turkey": {"optimal_temp_min": 5, "optimal_temp_max": 20, "max_wind_speed": 20}
    }
    d = defaults.get(species_key, defaults["deer"])
    return {**d, "pressure_trend": "falling", "source": "fallback"}


def _get_solunar_context(lat: float, lng: float, date_str: str) -> Dict[str, Any]:
    """PF3-LUN1/LUN3 : Contexte solunaire (LECTURE SEULE)."""
    try:
        from modules.solunar.engine import compute_solunar
        data = compute_solunar(lat, lng, date_str)
        return {
            "solunar_score": data.get("solunar_score", 50),
            "lunar_intensity": data.get("lunar_intensity", 0.5),
            "phase_name": data.get("moon", {}).get("phase_name", "unknown"),
            "hunting_windows_count": len(data.get("hunting_windows", [])),
            "source": "solunar_engine"
        }
    except Exception:
        return {
            "solunar_score": 50,
            "lunar_intensity": 0.5,
            "phase_name": "unknown",
            "hunting_windows_count": 0,
            "source": "fallback"
        }


async def correlate_zone(zone_id: str, species: str,
                         lat: float = 46.85, lng: float = -71.25) -> Dict[str, Any]:
    """Matrice de correlation meteo-faune pour une zone/espece."""
    species_key = SPECIES_MAP.get(species, "deer")
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    optimal = _get_optimal_conditions(species_key)
    solunar = _get_solunar_context(lat, lng, date_str)

    correlation_factors = {
        "temperature": {
            "correlation_strength": 0.75,
            "optimal_range": {
                "min": optimal["optimal_temp_min"],
                "max": optimal["optimal_temp_max"]
            },
            "impact": "primary",
            "description": f"Activite maximale entre {optimal['optimal_temp_min']}C et {optimal['optimal_temp_max']}C"
        },
        "barometric_pressure": {
            "correlation_strength": 0.82,
            "optimal_trend": optimal["pressure_trend"],
            "impact": "primary",
            "description": "Activite accrue lors de chutes de pression"
        },
        "wind_speed": {
            "correlation_strength": -0.65,
            "optimal_range": {"min": 0, "max": optimal["max_wind_speed"]},
            "impact": "secondary",
            "description": f"Activite reduite au-dela de {optimal['max_wind_speed']} km/h"
        },
        "precipitation": {
            "correlation_strength": -0.45,
            "optimal_range": {"min": 0, "max": 5},
            "impact": "secondary",
            "description": "Activite moderement reduite par precipitations"
        },
        "lunar_phase": {
            "correlation_strength": 0.55,
            "current_score": solunar["solunar_score"],
            "current_phase": solunar["phase_name"],
            "impact": "tertiary",
            "description": f"Phase actuelle : {solunar['phase_name']}, score {solunar['solunar_score']}"
        },
        "humidity": {
            "correlation_strength": 0.30,
            "optimal_range": {"min": 40, "max": 80},
            "impact": "tertiary",
            "description": "Impact faible, humidite moderee favorable"
        }
    }

    db = _get_db()
    ts_count = await db.timeseries_data.count_documents(
        {"zone_id": zone_id, "species": species}
    )
    data_richness = min(1.0, ts_count / 4.0)

    return {
        "zone_id": zone_id,
        "species": species,
        "species_key": species_key,
        "correlation_matrix": correlation_factors,
        "optimal_conditions": optimal,
        "solunar_context": solunar,
        "data_richness": round(data_richness, 2),
        "confidence": round(0.6 + data_richness * 0.3, 2),
        "sources": ["weather_fauna_simulation_engine", "solunar", "timeseries_data"],
        "computed_at": now.isoformat()
    }
