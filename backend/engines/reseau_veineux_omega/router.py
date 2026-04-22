"""
ENGINE_RESEAU_VEINEUX_Ω — Implémentation X200 P0 (support)
============================================================
Phase    : X200-P0-ACTIVATION — support orchestration corridors
Activé comme SUPPORT des 3 engines P0 pour :
  - hiérarchie 5 niveaux CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE (restauration V7)
  - convergence 600 m ± 30 % (420-780 m)
  - règle « ≥ 2 zones vitales » enforçable

SOURCE V7 : core/scoring_pipeline/corridors_v10/classifier.py
"""
from __future__ import annotations

from typing import Dict, Any, List
from fastapi import APIRouter
from fastapi.responses import JSONResponse

FEATURE_FLAG_ACTIVE: bool = True
ENGINE_ID = "ENGINE_RESEAU_VEINEUX_Ω"
PHASE = "X200-P0-ACTIVATION"

# Hiérarchie 5 niveaux V7 canonique (restauration corridors_v10.classifier)
CORRIDOR_LEVELS_V7 = [
    {"level": "CRITIQUE", "score_min": 85, "score_max": 100, "color": "#CC0000",
     "weight_px": 3.0, "largeur_m": 4, "dash_array": "10,4"},
    {"level": "MAJEUR",   "score_min": 70, "score_max": 84,  "color": "#FF0000",
     "weight_px": 2.5, "largeur_m": 6, "dash_array": None},
    {"level": "FORT",     "score_min": 50, "score_max": 69,  "color": "#FF8C00",
     "weight_px": 2.0, "largeur_m": 11, "dash_array": None},
    {"level": "MODERE",   "score_min": 30, "score_max": 49,  "color": "#FFD700",
     "weight_px": 1.5, "largeur_m": 17, "dash_array": None},
    {"level": "FAIBLE",   "score_min": 0,  "score_max": 29,  "color": "#BFBFBF",
     "weight_px": 1.2, "largeur_m": 26, "dash_array": None},
]

# Rayon fonctionnel 600 m ± 30 %
FUNCTIONAL_RADIUS_NOMINAL_M = 600
FUNCTIONAL_RADIUS_MIN_M = 420
FUNCTIONAL_RADIUS_MAX_M = 780
MAIN_VEIN_CONVERGENCE_M = 15


def classify_corridor(score: float) -> Dict[str, Any]:
    """Classification 5 niveaux V7 par score 0-100."""
    for lvl in CORRIDOR_LEVELS_V7:
        if lvl["score_min"] <= score <= lvl["score_max"]:
            return {**lvl, "score": score}
    return {**CORRIDOR_LEVELS_V7[-1], "score": score}


def validate_functional_radius(radius_m: float) -> Dict[str, Any]:
    """Valide que le rayon fonctionnel respecte 600m ± 30%."""
    ok = FUNCTIONAL_RADIUS_MIN_M <= radius_m <= FUNCTIONAL_RADIUS_MAX_M
    return {
        "radius_m": radius_m,
        "conforme_600m_30pct": ok,
        "min": FUNCTIONAL_RADIUS_MIN_M,
        "max": FUNCTIONAL_RADIUS_MAX_M,
        "nominal": FUNCTIONAL_RADIUS_NOMINAL_M,
    }


def enforce_vital_zone_rule(connections: List[Dict]) -> Dict[str, Any]:
    """Règle V7 : corridor ≥ 2 zones vitales. Enforce mode."""
    count = len(connections or [])
    return {
        "connections_count": count,
        "min_required": 2,
        "corridor_valid": count >= 2,
        "rejection_reason": None if count >= 2 else "vital_zone_connections_insufficient",
    }


router = APIRouter(prefix="/api/v7-ultime/reseau-veineux", tags=["ENGINE_RESEAU_VEINEUX_Ω_X200_P0"])


@router.get("/status")
async def status():
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "phase": PHASE,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "levels_5_restored": [l["level"] for l in CORRIDOR_LEVELS_V7],
        "functional_radius_600_30pct": [FUNCTIONAL_RADIUS_MIN_M, FUNCTIONAL_RADIUS_MAX_M],
        "main_vein_convergence_m": MAIN_VEIN_CONVERGENCE_M,
        "v7_source": "core/scoring_pipeline/corridors_v10/classifier.py",
    })


@router.get("/levels")
async def levels():
    return JSONResponse({"levels": CORRIDOR_LEVELS_V7})


@router.post("/compute")
async def compute(payload: dict = None):
    payload = payload or {}
    score = float(payload.get("score", 0))
    radius = float(payload.get("radius_m", 600))
    connections = payload.get("vital_connections", [])
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "classification": classify_corridor(score),
        "functional_radius": validate_functional_radius(radius),
        "vital_zone_rule": enforce_vital_zone_rule(connections),
    })
