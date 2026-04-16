"""
V8-PHASE-C — SCENARIO + THERMAL + MULTI-ENGINE SCORING
========================================================
Moteurs avances V8 natifs.
S'appuie sur Phase B (terrain-aware) sans modification.
ZERO dependance V6. ZERO duplication.

SCENARIO ENGINE: what-if trajectoires, perturbations (chasse, meteo, temporel)
THERMAL ENGINE: temperature, vent, dissipation thermique, confort animal
MULTI-ENGINE: ponderation composite terrain + thermique + scenario

Sandbox: feature_flag = True
"""
import math
import time
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Query

logger = logging.getLogger("bionic.v8_phase_c")
router = APIRouter(prefix="/api/v8/engines", tags=["V8 Phase C — Scenario + Thermal + Multi-Engine"])

FEATURE_FLAG_PHASE_C = True


# ═══════════════════════════════════════════════════════
# SHARED UTILITIES (from Phase A/B pattern, no duplication)
# ═══════════════════════════════════════════════════════

def _seed(lat, lon, salt=""):
    v = abs(math.sin(lat * 127.1 + lon * 311.7 + hash(salt) * 0.0001))
    return v - int(v)


def _terrain_profile(lat, lon):
    canopy = max(0, min(1, 0.35 + _seed(lat, lon, "canopy") * 0.55))
    pente = max(0, min(45, _seed(lat, lon, "pente") * 25 + abs(math.sin(lat * 13.7)) * 10))
    strate_1_3m = max(0, min(1, _seed(lat, lon, "strate") * 0.7 + 0.15))
    feuillus = max(0, min(1, _seed(lat, lon, "feuillus") * 0.6 + 0.2))
    distance_eau = max(10, min(800, 50 + _seed(lat, lon, "eau") * 500 + abs(math.cos(lon * 7.3)) * 200))
    distance_route = max(20, min(2000, 100 + _seed(lat, lon, "route") * 1500))
    couvert_pct = canopy * 80 + strate_1_3m * 20
    return {
        "canopy": round(canopy, 3), "pente_deg": round(pente, 1),
        "strate_1_3m": round(strate_1_3m, 3), "feuillus_ratio": round(feuillus, 3),
        "distance_eau_m": round(distance_eau), "distance_route_m": round(distance_route),
        "couvert_pct": round(couvert_pct, 1),
    }


# ═══════════════════════════════════════════════════════
# THERMAL ENGINE V8
# ═══════════════════════════════════════════════════════

def _thermal_model(lat, lon, month, hour, wind_speed_kmh=15, temp_c=None):
    """Modele thermique: temperature ressentie, dissipation, confort animal."""
    # Temperature estimee si non fournie
    if temp_c is None:
        seasonal_base = {1: -15, 2: -12, 3: -5, 4: 3, 5: 12, 6: 18,
                         7: 22, 8: 20, 9: 14, 10: 7, 11: 0, 12: -10}
        base = seasonal_base.get(month, 5)
        diurnal = math.sin((hour - 6) / 24 * 2 * math.pi) * 6
        temp_c = base + diurnal + _seed(lat, lon, "temp") * 4 - 2

    terrain = _terrain_profile(lat, lon)

    # Wind chill (formule Environnement Canada simplifiee)
    if temp_c <= 10 and wind_speed_kmh > 4.8:
        wind_chill = (13.12 + 0.6215 * temp_c -
                      11.37 * (wind_speed_kmh ** 0.16) +
                      0.3965 * temp_c * (wind_speed_kmh ** 0.16))
    else:
        wind_chill = temp_c

    # Dissipation thermique: canopy reduit le vent
    canopy_shelter = terrain["canopy"] * 0.6  # 0-0.6 reduction
    effective_wind = wind_speed_kmh * (1 - canopy_shelter)

    # Confort animal (cerf/orignal prefer 0-15C, stress >25C ou <-25C)
    if -5 <= temp_c <= 15:
        confort = 90 + (1 - abs(temp_c - 5) / 20) * 10
    elif 15 < temp_c <= 25:
        confort = max(30, 90 - (temp_c - 15) * 6)
    elif -25 <= temp_c < -5:
        confort = max(20, 70 + (temp_c + 5) * 2.5)
    else:
        confort = max(10, 30 - abs(temp_c) * 0.5)

    # Bonus couvert en chaleur extreme
    if temp_c > 20:
        confort += terrain["canopy"] * 15  # canopy = ombre = confort

    # Zone thermique
    if wind_chill < -20:
        zone = "extreme_froid"
    elif wind_chill < -5:
        zone = "froid"
    elif wind_chill < 10:
        zone = "optimal"
    elif wind_chill < 25:
        zone = "chaud"
    else:
        zone = "extreme_chaud"

    return {
        "temp_air_c": round(temp_c, 1),
        "wind_chill_c": round(wind_chill, 1),
        "wind_speed_kmh": round(wind_speed_kmh, 1),
        "effective_wind_kmh": round(effective_wind, 1),
        "canopy_shelter_pct": round(canopy_shelter * 100, 1),
        "confort_animal": round(min(100, max(0, confort)), 1),
        "zone_thermique": zone,
        "terrain": terrain,
    }


# ═══════════════════════════════════════════════════════
# SCENARIO ENGINE V8
# ═══════════════════════════════════════════════════════

SCENARIO_PRESETS = {
    "chasse_matin": {"hour": 6, "description": "Chasse matinale (aube)"},
    "chasse_soir": {"hour": 18, "description": "Chasse crepusculaire (soir)"},
    "rut_peak": {"month": 10, "hour": 7, "description": "Pic du rut (octobre, aube)"},
    "post_hiver": {"month": 4, "hour": 10, "description": "Post-hiver (avril, Na critique)"},
    "canicule": {"month": 7, "hour": 14, "temp_c": 32, "description": "Canicule estivale"},
    "tempete_neige": {"month": 1, "hour": 12, "temp_c": -25, "wind_kmh": 45, "description": "Tempete de neige"},
    "vent_fort": {"wind_kmh": 40, "description": "Vent fort (perturbation)"},
    "nuit": {"hour": 2, "description": "Deplacement nocturne"},
}


def _run_scenario(lat, lon, species, scenario_id, base_month, base_hour):
    """Execute un scenario what-if et retourne les scores compares."""
    preset = SCENARIO_PRESETS.get(scenario_id, {})
    s_month = preset.get("month", base_month)
    s_hour = preset.get("hour", base_hour)
    s_temp = preset.get("temp_c", None)
    s_wind = preset.get("wind_kmh", 15)

    # Import Phase B scoring (no duplication — delegation)
    from engines.v8_national.phase_b_engines import (
        generate_zones_ta, generate_corridors_ta, generate_affuts_ta,
    )

    # Baseline (conditions actuelles)
    zones_base = generate_zones_ta(lat, lon, species, base_month)
    corridors_base = generate_corridors_ta(lat, lon, species, base_month, base_hour)
    affuts_base = generate_affuts_ta(lat, lon, species, zones_base, corridors_base)
    thermal_base = _thermal_model(lat, lon, base_month, base_hour)

    # Scenario (conditions modifiees)
    zones_sc = generate_zones_ta(lat, lon, species, s_month)
    corridors_sc = generate_corridors_ta(lat, lon, species, s_month, s_hour)
    affuts_sc = generate_affuts_ta(lat, lon, species, zones_sc, corridors_sc)
    thermal_sc = _thermal_model(lat, lon, s_month, s_hour, s_wind, s_temp)

    # Deltas
    def _avg_score(items, key="score"):
        scores = [i.get(key, 0) for i in items]
        return round(sum(scores) / len(scores), 1) if scores else 0

    zones_delta = _avg_score(zones_sc) - _avg_score(zones_base)
    corr_delta = round(
        sum(c["intensity"] for c in corridors_sc) / max(1, len(corridors_sc)) -
        sum(c["intensity"] for c in corridors_base) / max(1, len(corridors_base)), 1
    )
    affuts_delta = _avg_score(affuts_sc) - _avg_score(affuts_base)
    thermal_delta = thermal_sc["confort_animal"] - thermal_base["confort_animal"]

    # Impact global
    impact = round(zones_delta * 0.35 + corr_delta * 0.05 + affuts_delta * 0.30 + thermal_delta * 0.30, 1)

    return {
        "scenario_id": scenario_id,
        "description": preset.get("description", scenario_id),
        "conditions": {
            "month": s_month, "hour": s_hour,
            "temp_c": thermal_sc["temp_air_c"],
            "wind_kmh": s_wind,
        },
        "baseline": {
            "zones_avg": _avg_score(zones_base),
            "corridors_avg": round(sum(c["intensity"] for c in corridors_base) / max(1, len(corridors_base)), 1),
            "affuts_avg": _avg_score(affuts_base),
            "thermal_confort": thermal_base["confort_animal"],
        },
        "scenario": {
            "zones_avg": _avg_score(zones_sc),
            "corridors_avg": round(sum(c["intensity"] for c in corridors_sc) / max(1, len(corridors_sc)), 1),
            "affuts_avg": _avg_score(affuts_sc),
            "thermal_confort": thermal_sc["confort_animal"],
        },
        "deltas": {
            "zones": round(zones_delta, 1),
            "corridors": round(corr_delta, 1),
            "affuts": round(affuts_delta, 1),
            "thermal": round(thermal_delta, 1),
        },
        "impact_global": impact,
        "verdict": "FAVORABLE" if impact > 5 else "NEUTRE" if impact > -5 else "DEFAVORABLE",
    }


# ═══════════════════════════════════════════════════════
# MULTI-ENGINE SCORING V8
# ═══════════════════════════════════════════════════════

def _multi_engine_score(lat, lon, species, month, hour, wind_speed_kmh=15):
    """Score composite multi-engine: terrain + thermal + scenario."""
    from engines.v8_national.phase_b_engines import generate_zones_ta, generate_corridors_ta, generate_affuts_ta
    from engines.v8_national.phase_a_engines import _score_saline, _score_affut, _score_composite

    terrain = _terrain_profile(lat, lon)
    thermal = _thermal_model(lat, lon, month, hour, wind_speed_kmh)
    zones = generate_zones_ta(lat, lon, species, month)
    corridors = generate_corridors_ta(lat, lon, species, month, hour)
    affuts = generate_affuts_ta(lat, lon, species, zones, corridors)

    # Phase A scores
    sal_score, _ = _score_saline(terrain, month, lat, lon)
    aff_score, _ = _score_affut(terrain, 180, lat, lon)

    # Aggregation
    zones_avg = sum(z["score"] for z in zones) / max(1, len(zones))
    corr_avg = sum(c["intensity"] for c in corridors) / max(1, len(corridors))
    affuts_avg = sum(a["score"] for a in affuts) / max(1, len(affuts))

    # Ponderation composite V8
    score_terrain = zones_avg * 0.30 + affuts_avg * 0.20 + sal_score * 0.15 + aff_score * 0.10
    score_thermal = thermal["confort_animal"] * 0.15
    score_temporal = corr_avg * 0.10  # intensite corridors = proxy activite

    composite = round(min(100, max(0, score_terrain + score_thermal + score_temporal)), 1)

    # Classification
    if composite >= 75:
        classification = "EXCEPTIONNEL"
    elif composite >= 60:
        classification = "EXCELLENT"
    elif composite >= 45:
        classification = "BON"
    elif composite >= 30:
        classification = "MODERE"
    else:
        classification = "FAIBLE"

    return {
        "composite_score": composite,
        "classification": classification,
        "breakdown": {
            "terrain": round(score_terrain, 1),
            "thermal": round(score_thermal, 1),
            "temporal": round(score_temporal, 1),
        },
        "components": {
            "zones_avg": round(zones_avg, 1),
            "corridors_avg": round(corr_avg, 1),
            "affuts_avg": round(affuts_avg, 1),
            "saline_score": sal_score,
            "affut_score": aff_score,
            "confort_animal": thermal["confort_animal"],
        },
        "thermal": thermal,
        "terrain": terrain,
    }


# ═══════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════

@router.get("/thermal")
async def thermal_endpoint(
    lat: float = Query(...), lon: float = Query(...),
    month: int = Query(None), hour: int = Query(None),
    wind_speed: float = Query(15), temp_c: float = Query(None),
):
    """Thermal Engine V8 — temperature, vent, dissipation, confort animal."""
    if not FEATURE_FLAG_PHASE_C:
        return {"error": "Phase C desactivee", "engine": "V8-THERMAL"}
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    t = temp_c if temp_c is not None else None
    result = _thermal_model(lat, lon, m, h, wind_speed, t)
    return {
        **result,
        "compute_ms": round((time.time() - start) * 1000),
        "engine": "V8-THERMAL", "dataVersion": "V8",
    }


@router.get("/scenario")
async def scenario_endpoint(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    scenario: str = Query("rut_peak"),
    month: int = Query(None), hour: int = Query(None),
):
    """Scenario Engine V8 — what-if, comparaison baseline vs scenario."""
    if not FEATURE_FLAG_PHASE_C:
        return {"error": "Phase C desactivee", "engine": "V8-SCENARIO"}
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    result = _run_scenario(lat, lon, species, scenario, m, h)
    return {
        **result,
        "available_scenarios": list(SCENARIO_PRESETS.keys()),
        "compute_ms": round((time.time() - start) * 1000),
        "engine": "V8-SCENARIO", "dataVersion": "V8",
    }


@router.get("/scenario/presets")
async def scenario_presets():
    """Liste des scenarios disponibles."""
    return {
        "presets": {k: v["description"] for k, v in SCENARIO_PRESETS.items()},
        "engine": "V8-SCENARIO",
    }


@router.get("/multi-score")
async def multi_engine_score_endpoint(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    month: int = Query(None), hour: int = Query(None),
    wind_speed: float = Query(15),
):
    """Multi-Engine Scoring V8 — composite terrain + thermal + scenario."""
    if not FEATURE_FLAG_PHASE_C:
        return {"error": "Phase C desactivee", "engine": "V8-MULTI-ENGINE"}
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    result = _multi_engine_score(lat, lon, species, m, h, wind_speed)
    return {
        **result,
        "context": {"lat": lat, "lon": lon, "species": species, "month": m, "hour": h},
        "compute_ms": round((time.time() - start) * 1000),
        "engine": "V8-MULTI-ENGINE", "dataVersion": "V8",
    }


@router.get("/phase-c/status")
async def phase_c_status():
    return {
        "engine": "V8-PHASE-C",
        "version": "8.4.0",
        "status": "OPERATIONNEL",
        "modules": {
            "thermal": {"active": FEATURE_FLAG_PHASE_C, "endpoint": "/api/v8/engines/thermal"},
            "scenario": {"active": FEATURE_FLAG_PHASE_C, "endpoint": "/api/v8/engines/scenario",
                         "presets": list(SCENARIO_PRESETS.keys())},
            "multi_score": {"active": FEATURE_FLAG_PHASE_C, "endpoint": "/api/v8/engines/multi-score"},
        },
        "dependencies": ["phase_a_engines", "phase_b_engines"],
        "dataVersion": "V8",
    }
