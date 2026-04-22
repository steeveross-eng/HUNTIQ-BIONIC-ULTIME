"""
ENGINE_HYDRO_TOPO_Ω — Implémentation X200 P0
==============================================
Phase     : X200-P0-ACTIVATION
Priorité  : P0 #3 (INVERSION SÉMANTIQUE HYDRO corrigée)

RESTAURATION V7 ULTIME :
- Inversion hydro corrigée : V7 attire (< 150 m bonus) vs V20-X180 qui repoussait
- Porte terrainBoosts frontend → backend (slope_high 0.20, valley 0.30, wet 0.25, transition 0.15)
- Fusion multi-échelles DEM 1m/5m/10m
- Respect `affinite_hydro` par espèce (CERF 0.60, ORIGNAL 0.85, OURS 0.50, DINDON 0.40)
"""
from __future__ import annotations

import math
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse

FEATURE_FLAG_ACTIVE: bool = True
ENGINE_ID = "ENGINE_HYDRO_TOPO_Ω"
PHASE = "X200-P0-ACTIVATION"

# Terrain-aware boosts V7 (portés en backend depuis renduOmegaStore.js)
TERRAIN_BOOSTS = {
    "slope_high":  0.20,
    "valley":      0.30,  # dominant — vallons favorisés
    "wet":         0.25,  # humides favorisés
    "transition":  0.15,  # lisières / tampons
}
BOOST_CAP = 1.95
BOOST_FLOOR = 1.0

# Bonus hydro V7 : attraction si < 150m (au lieu de répulsion X180)
HYDRO_BONUS_RADIUS_M = 150.0
HYDRO_BONUS_MAX = 0.35


def _haversine_m(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return float("inf")
    R = 6371000.0
    lat1 = math.radians(a[0]); lat2 = math.radians(b[0])
    dlat = math.radians(b[0] - a[0])
    dlon = math.radians(b[1] - a[1])
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(h))


def hydro_attraction_bonus(point: List[float], water_points: List[List[float]],
                           affinity_hydro: float = 0.6) -> float:
    """INVERSION CORRIGÉE : proximité eau devient un BONUS pondéré par affinité espèce.

    Remplace le `water_tolerance_m` répulsif de X180 par un attracteur V7.
    """
    if not water_points:
        return 0.0
    min_d = min(_haversine_m(point, w) for w in water_points)
    if min_d >= HYDRO_BONUS_RADIUS_M:
        return 0.0
    # Bonus linéaire décroissant avec la distance, modulé par affinité espèce
    raw = (HYDRO_BONUS_RADIUS_M - min_d) / HYDRO_BONUS_RADIUS_M
    return raw * HYDRO_BONUS_MAX * max(0.0, min(1.0, affinity_hydro))


def compute_terrain_aware_boost(signals: Dict[str, bool]) -> float:
    """Calcule le boost terrain-aware V7 (cap 1.95, floor 1.0)."""
    boost = 1.0
    for k, weight in TERRAIN_BOOSTS.items():
        if signals.get(k, False):
            boost += weight
    return max(BOOST_FLOOR, min(BOOST_CAP, boost))


def fuse_multiscale_dem(values: Dict[str, float]) -> float:
    """Fusion cross-scale DEM 1m/5m/10m (priorité fine > moyenne > grossière)."""
    weights = {"1m": 0.55, "5m": 0.30, "10m": 0.15}
    total_w = 0.0
    total_v = 0.0
    for scale, w in weights.items():
        if scale in values and values[scale] is not None:
            total_v += values[scale] * w
            total_w += w
    return total_v / total_w if total_w > 0 else 0.0


router = APIRouter(prefix="/api/v7-ultime/hydro-topo", tags=["ENGINE_HYDRO_TOPO_Ω_X200_P0"])


@router.get("/status")
async def status():
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "phase": PHASE,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "inversion_hydro_corrected": True,
        "hydro_semantics": "ATTRACTIVE (V7) — corrected from X180 REPULSIVE",
        "hydro_bonus_radius_m": HYDRO_BONUS_RADIUS_M,
        "hydro_bonus_max": HYDRO_BONUS_MAX,
        "terrain_boosts": TERRAIN_BOOSTS,
        "boost_cap": BOOST_CAP,
        "boost_floor": BOOST_FLOOR,
        "multiscale_dem": ["1m", "5m", "10m"],
    })


@router.post("/compute")
async def compute(payload: dict = None):
    payload = payload or {}
    point = payload.get("point", [48.206657, -68.382422])
    water_points = payload.get("water_points", [])
    affinity = float(payload.get("affinity_hydro", 0.6))
    terrain_signals = payload.get("terrain_signals", {})
    dem_values = payload.get("dem_multiscale", {})

    hydro_bonus = hydro_attraction_bonus(point, water_points, affinity)
    terrain_boost = compute_terrain_aware_boost(terrain_signals)
    dem_fused = fuse_multiscale_dem(dem_values)

    return JSONResponse({
        "engine_id": ENGINE_ID,
        "phase": PHASE,
        "point": point,
        "hydro_attraction_bonus": round(hydro_bonus, 4),
        "terrain_aware_boost": round(terrain_boost, 4),
        "dem_fused_multiscale": round(dem_fused, 2),
        "inversion_corrected": True,
    })
