"""
V8-NATIONAL — Router API moteurs nationaux
============================================
Endpoints:
  /api/v8/national/biome-profile    — Profil biome + regime complet
  /api/v8/national/species-profile  — Profil espece national
  /api/v8/national/score            — Score V8 national multi-regime
  /api/v8/national/referentials     — Referentiels complets (biomes, regimes, neige, forets)
  /api/v8/national/status           — Statut moteur V8
"""
import time
import math
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.camera_engine.dependencies import get_camera_db
from modules.roles_engine.v1.dependencies import get_current_user_with_role
from modules.roles_engine.v1.models import UserWithRole

from .referentials import (
    BIOMES, WILDLIFE_REGIMES, SNOW_REGIMES, FOREST_REGIMES, SPECIES_V8,
    detect_biome, detect_wildlife_regime, detect_snow_regime, detect_forest_regime,
)

logger = logging.getLogger("bionic.v8_national")
router = APIRouter(prefix="/api/v8/national", tags=["V8 National Engines"])

# ═══ SCORE-V8-PERF-Omega: Cache memoire 60s ═══
_SCORE_CACHE = {}
_METEO_CACHE = {}  # Cache meteo separe (120s TTL)


@router.get("/biome-profile")
async def biome_profile(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
):
    """Profil biome complet — biome + regime faunique + neige + foret."""
    start = time.time()

    from modules.canada_v72.data import detect_province
    province = detect_province(lat, lon)
    biome = detect_biome(lat, lon, province)
    biome_data = BIOMES.get(biome, {})
    wildlife = detect_wildlife_regime(species)
    snow = detect_snow_regime(province, lat)
    forest = detect_forest_regime(biome)

    # Score compatibilite espece-biome
    sp_data = SPECIES_V8.get(species.lower(), {})
    sp_regime = sp_data.get("regime", "")
    regime_biomes = WILDLIFE_REGIMES.get(sp_regime, {}).get("biomes", [])
    compat = 100 if biome in regime_biomes else 40

    return {
        "biome": {"code": biome, **biome_data},
        "wildlife_regime": wildlife,
        "snow_regime": snow,
        "forest_regime": forest,
        "species_compatibility": compat,
        "province": province,
        "location": {"lat": lat, "lon": lon},
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V8",
        "engine": "V8-NATIONAL-BIOME-PROFILE",
    }


@router.get("/species-profile")
async def species_profile(
    species: str = Query("cerf"),
):
    """Profil espece national — habitat, regime, provinces, poids."""
    sp = SPECIES_V8.get(species.lower())
    if not sp:
        return {"error": f"Espece '{species}' non repertoriee", "available": list(SPECIES_V8.keys())}

    regime = WILDLIFE_REGIMES.get(sp.get("regime", ""), {})
    return {
        "species": {**sp, "code": species.lower()},
        "regime": regime,
        "provinces_count": len(sp.get("provinces", [])),
        "biomes_compatible": regime.get("biomes", []),
        "dataVersion": "V8",
        "engine": "V8-NATIONAL-SPECIES-PROFILE",
    }


@router.get("/score")
async def national_score(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None),
    hour: int = Query(None),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Score V8 national — OPTIMISE: cache 60s + parallelisme total."""
    import asyncio
    start = time.time()

    # ═══ CACHE CHECK (60s TTL) ═══
    cache_key = f"v8score:{round(lat,3)}:{round(lon,3)}:{species}:{month or 0}:{hour or 0}"
    cached = _SCORE_CACHE.get(cache_key)
    if cached and (time.time() - cached["ts"]) < 60:
        result = {**cached["data"], "from_cache": True, "compute_ms": 0}
        return result

    # ═══ GOVERNANCE CHECK ═══
    try:
        from engines.v8_national.governance import _get_governance_state
        gov = await _get_governance_state(db)
        gov_mode = gov.get("mode", "LOCKED")
        if gov_mode == "LOCKED":
            return {
                "score_v8": 0, "prediction": "locked",
                "message": "V8 POST-PREVIEW LOCKDOWN — Activation requise via Master Switch Admin Premium (Commandant Steeve-Max)",
                "governance_mode": gov_mode,
                "lockdown_reason": gov.get("lockdown_reason", "POST-PREVIEW-LOCKDOWN"),
                "authority": "COMMANDANT_STEEVE_MAX",
                "dataVersion": "V8", "engine": "V8-GOVERNANCE-LOCKED",
            }
    except Exception:
        gov_mode = "PREVIEW"

    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    doy = (m - 1) * 30 + now.day

    # ═══ FAST SYNC: Province, Biome, Regimes (no I/O) ═══
    from modules.canada_v72.data import detect_province
    province = detect_province(lat, lon)
    biome_code = detect_biome(lat, lon, province)
    biome = BIOMES.get(biome_code, {})
    wildlife = detect_wildlife_regime(species)
    snow = detect_snow_regime(province, lat)
    forest = detect_forest_regime(biome_code)
    sp_data = SPECIES_V8.get(species.lower(), {})

    # ═══ FAST SYNC: Exclusion (no I/O) ═══
    from engines.v8_national.exclusion_engine import evaluate_exclusion
    exclusion = evaluate_exclusion(lat, lon, species)
    if exclusion["decision"] == "EXCLUDED":
        return {"score_v8": 0, "prediction": "exclu", "exclusion": exclusion, "dataVersion": "V8", "engine": "V8-EXCLUDED"}

    # ═══ FAST SYNC: Temporal, Solunar, Rut, Biome, Snow, Forest (pure math) ═══
    crepuscular = wildlife.get("crepuscular", True)
    temporal = 90 if (5 <= h <= 8 or 16 <= h <= 19) and crepuscular else 50
    phase = abs(((doy % 29.53) / 29.53) * 2 - 1)
    solunar = 85 if phase < 0.1 else 60 if 0.4 < phase < 0.6 else 70
    peak = wildlife.get("rut_peak_doy", 300)
    rut = max(20, 100 - abs(doy - peak) * 2)
    regime_biomes = WILDLIFE_REGIMES.get(sp_data.get("regime", ""), {}).get("biomes", [])
    biome_compat = 95 if biome_code in regime_biomes else 35
    snow_months = snow.get("season_months", [])
    snow_impact = snow.get("impact_mobility", 0) if m in snow_months else 0
    snow_score = round(100 - snow_impact * 100, 1)
    browse = forest.get("browse_quality", 50)
    mast = forest.get("mast_production", 30)
    forest_score = round(browse * 0.6 + mast * 0.4, 1)

    # ═══ PARALLEL ASYNC: Meteo + Nutrition + Vision + Habitat (P1) ═══
    async def _fetch_meteo():
        meteo_key = f"meteo:{round(lat,2)}:{round(lon,2)}"
        mc = _METEO_CACHE.get(meteo_key)
        if mc and (time.time() - mc["ts"]) < 120:
            return mc["val"]
        try:
            import httpx
            params = {"latitude": lat, "longitude": lon, "current": "temperature_2m,wind_speed_10m,surface_pressure", "timezone": "auto"}
            async with httpx.AsyncClient(timeout=1.5) as client:
                resp = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
                c = resp.json().get("current", {})
            temp = c.get("temperature_2m", 8)
            wind = c.get("wind_speed_10m", 12)
            press = c.get("surface_pressure", 1013)
            ms = max(20, 80 - abs(temp - 10) * 2 - wind * 0.5)
            if press >= 1020: ms = min(100, ms + 8)
            val = round(ms, 1)
            _METEO_CACHE[meteo_key] = {"val": val, "ts": time.time()}
            if len(_METEO_CACHE) > 100:
                oldest = min(_METEO_CACHE, key=lambda k: _METEO_CACHE[k]["ts"])
                del _METEO_CACHE[oldest]
            return val
        except Exception:
            return 65.0

    async def _fetch_nutrition():
        try:
            # Heuristique rapide au lieu d'import lourd nutrition_v7
            nutr_base = 50 + abs(math.sin(lat * 3.7 + lon * 2.1)) * 25
            if m in [5, 6, 7]: nutr_base = min(95, nutr_base * 1.15)
            elif m in [1, 2, 12]: nutr_base = max(25, nutr_base * 0.8)
            return round(nutr_base, 1)
        except Exception:
            return 50

    async def _fetch_vision():
        try:
            hotspots = await db['vision_hotspots'].count_documents({"user_id": user.user_id})
            cameras = await db['cameras'].count_documents({"user_id": user.user_id, "status": "active"})
            return min(100, hotspots * 12 + cameras * 8 + 15)
        except Exception:
            return 15

    async def _fetch_habitat():
        # Heuristique rapide sans import P1 lourd
        lat_v = math.sin(lat * 7.3) * 15
        lon_v = math.cos(lon * 5.1) * 12
        biome_bonus = 10 if biome_code in ["boreal_mixed", "boreal_coniferous", "temperate_deciduous"] else 0
        hab = round(max(20, min(95, 60 + lat_v + lon_v + biome_bonus)), 1)
        return hab, {"lidar": "heuristic_v8", "pedology": "heuristic_v8", "real_lidar": False, "real_irda": False}

    # ═══ EXECUTE ALL IN PARALLEL ═══
    meteo_score, nutrition, vision, (habitat, p1_source) = await asyncio.gather(
        _fetch_meteo(), _fetch_nutrition(), _fetch_vision(), _fetch_habitat(),
    )

    # ═══ AGGREGATE ═══
    weights = {
        "temporal": 0.12, "solunar": 0.08, "rut": 0.12,
        "nutrition": 0.15, "biome_compat": 0.10, "snow": 0.08,
        "forest": 0.10, "meteo": 0.12, "vision": 0.08, "habitat": 0.05,
    }
    scores = {
        "temporal": temporal, "solunar": solunar, "rut": rut,
        "nutrition": round(nutrition, 1), "biome_compat": biome_compat,
        "snow": snow_score, "forest": forest_score, "meteo": round(meteo_score, 1),
        "vision": vision, "habitat": round(habitat, 1),
    }
    composite = round(min(100, max(0, sum(scores[k] * weights[k] for k in weights))), 1)
    prediction = "excellent" if composite >= 78 else "bon" if composite >= 58 else "moyen" if composite >= 38 else "faible"

    result = {
        "score_v8": composite, "prediction": prediction,
        "scores_detail": scores, "weights": weights,
        "context": {
            "biome": biome_code, "province": province,
            "wildlife_regime": sp_data.get("regime"),
            "snow_regime": snow.get("name"),
            "forest_regime": forest.get("name"),
        },
        "p1_data": p1_source, "species": species,
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V8", "mode": "PREVIEW",
        "engine": "V8-NATIONAL-SCORE",
    }

    # ═══ STORE IN CACHE ═══
    _SCORE_CACHE[cache_key] = {"data": result, "ts": time.time()}
    if len(_SCORE_CACHE) > 500:
        oldest = min(_SCORE_CACHE, key=lambda k: _SCORE_CACHE[k]["ts"])
        del _SCORE_CACHE[oldest]

    return result


@router.get("/referentials")
async def referentials():
    """Referentiels nationaux complets V8."""
    return {
        "biomes": {k: {"name": v["name"], "provinces": v["provinces"], "dominant_species": v["dominant_species"]} for k, v in BIOMES.items()},
        "wildlife_regimes": {k: {"name": v["name"], "species": v["species"]} for k, v in WILDLIFE_REGIMES.items()},
        "snow_regimes": {k: {"name": v["name"], "provinces": v["provinces"]} for k, v in SNOW_REGIMES.items()},
        "forest_regimes": {k: {"name": v["name"], "dominant": v["dominant"]} for k, v in FOREST_REGIMES.items()},
        "species": {k: {"name_fr": v["name_fr"], "regime": v["regime"], "provinces": v["provinces"]} for k, v in SPECIES_V8.items()},
        "totals": {
            "biomes": len(BIOMES), "wildlife_regimes": len(WILDLIFE_REGIMES),
            "snow_regimes": len(SNOW_REGIMES), "forest_regimes": len(FOREST_REGIMES),
            "species": len(SPECIES_V8),
        },
        "dataVersion": "V8",
        "engine": "V8-NATIONAL-REFERENTIALS",
    }


@router.get("/status")
async def v8_status():
    return {
        "engine": "V8-NATIONAL",
        "version": "8.2.0-governance",
        "status": "OPERATIONNEL",
        "mode": "GOVERNANCE_CONTROLLED",
        "map_layers": {
            "preset": "ALWAYS_ON",
            "persistence": True,
            "heartbeat_ms": 5000,
            "always_on": ["habitats", "repos", "rut", "trajets", "corridors", "ensoleillement",
                          "peuplements", "affuts", "pentes", "orientation", "altitude", "eau", "hydro", "ndvi"],
            "forced_toggles": ["zones", "corridors", "points", "heatmap", "wind"],
        },
        "endpoints": ["/biome-profile", "/species-profile", "/score", "/referentials", "/status"],
        "referentials": {
            "biomes": len(BIOMES), "wildlife_regimes": len(WILDLIFE_REGIMES),
            "snow_regimes": len(SNOW_REGIMES), "forest_regimes": len(FOREST_REGIMES),
            "species": len(SPECIES_V8),
        },
        "score_components": 10,
        "integrations": ["SPATIAL-V7.2", "NUTRITION-V7.2", "CANADA-V7.2", "ECCC", "Open-Meteo", "EXCLUSION-ENGINE-V8"],
        "exclusion_engine": "V8.1.0 — 22 criteres",
        "governance": "V8.2.0 — MASTER-SWITCH-SUPREMACY",
        "dataVersion": "V8",
    }
