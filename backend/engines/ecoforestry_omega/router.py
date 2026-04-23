"""
ENGINE_ECOFORESTRY_Ω — Router FastAPI — X199 ACTIVÉ
====================================================
Phase : PHASE_X199_ACTIVATION_Ω — moteur #1 (racine)
Commandant STEEVE-MAX

Rôle : Classification forestière d'un waypoint (essences, canopée, stades
successionnels, lisières, mosaïques) à partir de lat/lng + saison.

Activation : triple verrou X199 (flag + env + token `STEEVE-MAX-X199-EXPLICIT`).
V30 INTANGIBLE. Aucun import sous engines.v8_institutional.*.
"""
from __future__ import annotations

import math
from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from engines.x199_commons import is_x199_authorized, unauthorized_response

# ═══════════════════════════════════════════════════════════════════════
# FEATURE FLAG — ACTIVÉ (ORDRE COMMANDANT — PHASE X199-ACTIVATION-Ω #1)
# ═══════════════════════════════════════════════════════════════════════
FEATURE_FLAG_ACTIVE: bool = True

ENGINE_ID = "ENGINE_ECOFORESTRY_Ω"
CATEGORY = "etendu"
ROLE = "Essences, canopy, stades successionnels, lisières, mosaïques forestières"
MAX_KB_TARGET = 80

# Catalogue institutionnel Bas-Saint-Laurent / Témiscouata (waypoint officiel)
FOREST_TYPES = [
    "coniferous_boreal", "mixed_boreal", "deciduous_temperate",
    "regeneration_5_15y", "mature_50_plus", "clearing_wet",
    "wetland_forested", "edge_ecotone",
]
SUCCESSION_STAGES = ["pioneer", "intermediate", "mature", "climax"]

# ═══════════════════════════════════════════════════════════════════════
# LOGIQUE INSTITUTIONNELLE — CLASSIFICATION FORESTIÈRE
# ═══════════════════════════════════════════════════════════════════════
def _base_forest_type(lat: float, lng: float) -> str:
    """Classification territoriale déterministe (reproductible, testable)."""
    # Heuristique Bas-Saint-Laurent : latitude ≥ 48° → dominance boréale mixte,
    # sauf bordures humides (signature lng centrée -68.35 à -68.45).
    if 48.10 <= lat <= 48.30:
        if -68.45 <= lng <= -68.30:
            return "mixed_boreal"
        if -68.50 <= lng < -68.45:
            return "wetland_forested"
    if lat >= 48.30:
        return "coniferous_boreal"
    return "deciduous_temperate"


def _canopy_fraction(lat: float, lng: float, month: int) -> float:
    """Fraction de canopée (0-1) selon type et saison."""
    t = _base_forest_type(lat, lng)
    base = {
        "coniferous_boreal":   0.82,
        "mixed_boreal":        0.75,
        "deciduous_temperate": 0.70,
        "wetland_forested":    0.55,
    }.get(t, 0.65)
    # Feuillus en feuille : mai-octobre bonus, hiver malus
    if t in ("deciduous_temperate", "mixed_boreal") and month in (11, 12, 1, 2, 3, 4):
        base -= 0.15
    return max(0.0, min(1.0, round(base, 3)))


def _succession_stage(lat: float, lng: float) -> str:
    """Stade successionnel déterministe depuis une signature spatiale."""
    # Signature : utilise les décimales lat/lng pour indexer le catalogue
    h = int(abs((lat * 1000 + lng * 1000)) * 1000) % len(SUCCESSION_STAGES)
    return SUCCESSION_STAGES[h]


def _edge_proximity_m(lat: float, lng: float) -> float:
    """Estimation déterministe de proximité à une lisière (mètres)."""
    # Proximité lisière : modulo pseudo-cyclique borné à 200 m
    sig = abs(math.sin(lat * 17.0) * math.cos(lng * 23.0))
    return round(sig * 200.0, 1)


def compute_ecoforestry(lat: float, lng: float, month: int = 10) -> Dict[str, Any]:
    month = max(1, min(12, int(month)))
    ftype = _base_forest_type(lat, lng)
    return {
        "engine_id": ENGINE_ID,
        "lat": lat, "lng": lng, "month": month,
        "forest_type": ftype,
        "canopy_fraction": _canopy_fraction(lat, lng, month),
        "succession_stage": _succession_stage(lat, lng),
        "edge_proximity_m": _edge_proximity_m(lat, lng),
        "mosaic_diversity_index": round(
            (0.4 if "mixed" in ftype else 0.25)
            + (0.25 if "wetland" in ftype else 0.0), 3,
        ),
        "v30_engine_touched": False,
    }


router = APIRouter(
    prefix="/api/v7-ultime/ecoforestry/compute",
    tags=["ENGINE_ECOFORESTRY_Ω_X199_ACTIVE"],
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
        "forest_types_catalogue": FOREST_TYPES,
        "succession_stages": SUCCESSION_STAGES,
    })


@router.post("")
@router.post("/")
async def engine_compute(payload: dict = None):
    if not is_x199_authorized(FEATURE_FLAG_ACTIVE)["authorized"]:
        raise unauthorized_response(ENGINE_ID, FEATURE_FLAG_ACTIVE)
    p = payload or {}
    return JSONResponse(compute_ecoforestry(
        lat=float(p.get("lat", 48.206657)),
        lng=float(p.get("lng", p.get("lon", -68.382422))),
        month=int(p.get("month", 10)),
    ))
