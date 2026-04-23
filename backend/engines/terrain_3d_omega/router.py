"""
ENGINE_3D_TERRAIN_Ω — Router FastAPI — X199 ACTIVÉ
===================================================
Phase : PHASE_X199_ACTIVATION_Ω — moteur #3 (dépend advanced_geospatial)
Commandant STEEVE-MAX

Rôle : DEM 1m/5m/10m, relief 3D, pente, exposition, microrelief vectoriel.
Implémentation institutionnelle : calcul pente / exposition à partir d'un
triangle DEM (3 altitudes en 3 points voisins).

Activation : triple verrou X199. V30 INTANGIBLE.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from engines.x199_commons import is_x199_authorized, unauthorized_response

FEATURE_FLAG_ACTIVE: bool = True

ENGINE_ID = "ENGINE_3D_TERRAIN_Ω"
CATEGORY = "etendu"
ROLE = "DEM 1m/5m/10m, relief 3D, exposition, microrelief vectoriel"
MAX_KB_TARGET = 100

SLOPE_CLASSES = [
    {"label": "flat",          "min_deg": 0,   "max_deg": 3},
    {"label": "gentle",        "min_deg": 3,   "max_deg": 10},
    {"label": "moderate",      "min_deg": 10,  "max_deg": 20},
    {"label": "steep",         "min_deg": 20,  "max_deg": 35},
    {"label": "very_steep",    "min_deg": 35,  "max_deg": 90},
]

ASPECT_CARDINALS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def slope_aspect_from_triangle(
    p0: List[float], p1: List[float], p2: List[float],
) -> Dict[str, Any]:
    """Calcule pente (deg) et exposition (aspect) depuis 3 points (lat, lng, alt_m).

    Hypothèse locale (petit voisinage < 500 m) : projection plane (équirectangulaire).
    """
    def to_xy(a: List[float]) -> List[float]:
        lat0 = p0[0]
        dlat_m = (a[0] - lat0) * 111320.0
        dlng_m = (a[1] - p0[1]) * 111320.0 * math.cos(math.radians(lat0))
        return [dlng_m, dlat_m, a[2]]
    v0 = to_xy(p0); v1 = to_xy(p1); v2 = to_xy(p2)
    u = [v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]]
    w = [v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]]
    # Normale = u × w
    nx = u[1]*w[2] - u[2]*w[1]
    ny = u[2]*w[0] - u[0]*w[2]
    nz = u[0]*w[1] - u[1]*w[0]
    # Normaliser vers le haut (nz > 0)
    if nz < 0:
        nx, ny, nz = -nx, -ny, -nz
    norm = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
    # Pente = angle entre normale et Z
    slope_rad = math.acos(max(-1.0, min(1.0, nz / norm)))
    slope_deg = math.degrees(slope_rad)
    # Aspect = direction de plus grande pente (projection XY)
    aspect_rad = math.atan2(ny, nx)  # mathématique (E=0, N=π/2)
    aspect_bearing = (90.0 - math.degrees(aspect_rad)) % 360.0  # bearing cartographique
    idx = int(round(aspect_bearing / 45.0)) % 8
    return {
        "slope_deg": round(slope_deg, 2),
        "aspect_bearing_deg": round(aspect_bearing, 2),
        "aspect_cardinal": ASPECT_CARDINALS[idx],
    }


def classify_slope(slope_deg: float) -> str:
    for c in SLOPE_CLASSES:
        if c["min_deg"] <= slope_deg < c["max_deg"]:
            return c["label"]
    return "very_steep"


def microrelief_index(slope_deg: float, aspect_cardinal: str) -> float:
    """Indice 0-1 d'hétérogénéité microrelief (signature Ω)."""
    base = min(1.0, slope_deg / 35.0)
    # Aspects N/NE/NW favorisent microrelief mousseux boréal (+bonus)
    if aspect_cardinal in ("N", "NE", "NW"):
        base = min(1.0, base + 0.15)
    return round(base, 3)


def compute_terrain_3d(triangle: List[List[float]]) -> Dict[str, Any]:
    if not triangle or len(triangle) < 3:
        # Fallback : simulation DEM plat autour du waypoint officiel
        lat0, lng0 = 48.206657, -68.382422
        triangle = [
            [lat0,           lng0,           220.0],
            [lat0 + 0.001,   lng0,           225.0],
            [lat0,           lng0 + 0.001,   222.0],
        ]
    sa = slope_aspect_from_triangle(triangle[0], triangle[1], triangle[2])
    return {
        "engine_id": ENGINE_ID,
        "triangle_input": triangle,
        "slope_deg": sa["slope_deg"],
        "slope_class": classify_slope(sa["slope_deg"]),
        "aspect_bearing_deg": sa["aspect_bearing_deg"],
        "aspect_cardinal": sa["aspect_cardinal"],
        "microrelief_index": microrelief_index(sa["slope_deg"], sa["aspect_cardinal"]),
        "dem_resolution_m": 1,
        "v30_engine_touched": False,
    }


router = APIRouter(
    prefix="/api/v7-ultime/terrain-3d/compute",
    tags=["ENGINE_3D_TERRAIN_Ω_X199_ACTIVE"],
)


@router.get("/status")
async def engine_status():
    auth = is_x199_authorized(FEATURE_FLAG_ACTIVE)
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "category": CATEGORY,
        "role": ROLE,
        "max_kb_target": MAX_KB_TARGET,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "phase": "X199-ACTIVATION",
        "ready": auth["authorized"],
        "authorization": auth,
        "v30_modified": False,
        "diagnostic_panel_active": False,
        "slope_classes": SLOPE_CLASSES,
        "aspect_cardinals": ASPECT_CARDINALS,
    })


@router.post("")
@router.post("/")
async def engine_compute(payload: dict = None):
    if not is_x199_authorized(FEATURE_FLAG_ACTIVE)["authorized"]:
        raise unauthorized_response(ENGINE_ID, FEATURE_FLAG_ACTIVE)
    p = payload or {}
    return JSONResponse(compute_terrain_3d(triangle=p.get("triangle") or []))
