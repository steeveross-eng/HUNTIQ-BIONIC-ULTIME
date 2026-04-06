"""
access_clarity_engine_v7 — Router API
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
Branche: STEEVE-MAX-x3200-V6-CORE

Endpoints:
  POST /api/v7/clarity/compute   — Calculer un chemin clair + TCS
  POST /api/v7/clarity/score     — Calculer TCS seul sur des coords existantes
  GET  /api/v7/clarity/status    — Statut du moteur
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from .clarity_engine import apply_clarity, CLARITY_RENDER
from .scorer import compute_tcs, TCS_WEIGHTS

logger = logging.getLogger("access_clarity_engine_v7.router")

router = APIRouter(
    prefix="/api/v7/clarity",
    tags=["ACCESS CLARITY V7"],
)


class CoordsInput(BaseModel):
    lat: float
    lng: float


class ClarityComputeRequest(BaseModel):
    coords: List[CoordsInput]
    distance_m: float = 0
    trail_type: str = "terrain_aware"
    routing_algo: str = "terrain_grid_astar"
    trail_percentage: float = 0
    phase1_distance_m: float = 0
    phase2_distance_m: float = 0
    terrain_types: List[str] = []


class TCSScoreRequest(BaseModel):
    coords: List[CoordsInput]
    distance_m: float = 0
    trail_type: str = ""
    routing_algo: str = ""
    trail_percentage: float = 0
    terrain_context: Dict[str, Any] = {}


@router.post("/compute", summary="Calculer chemin clair + TCS")
async def compute_clarity(request: ClarityComputeRequest):
    """
    Applique le pipeline de clarte v7:
    1. Suppression zigzags
    2. Lissage Douglas-Peucker
    3. Interpolation Catmull-Rom
    4. Score TCS complet
    5. Metadonnees de rendu visuel
    """
    coords_dicts = [{"lat": c.lat, "lng": c.lng} for c in request.coords]

    if len(coords_dicts) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 coordonnees requises")

    access_data = {
        "coords": coords_dicts,
        "distance_m": request.distance_m,
        "trail_type": request.trail_type,
        "routing_algo": request.routing_algo,
        "trail_percentage": request.trail_percentage,
        "phase1_distance_m": request.phase1_distance_m,
        "phase2_distance_m": request.phase2_distance_m,
        "terrain_types": request.terrain_types,
    }

    result = apply_clarity(access_data)
    return result


@router.post("/score", summary="Calculer TCS seul")
async def compute_score_only(request: TCSScoreRequest):
    """Calcule le Terrain Clarity Score sans lissage."""
    coords_dicts = [{"lat": c.lat, "lng": c.lng} for c in request.coords]

    route_data = {
        "coords": coords_dicts,
        "distance_m": request.distance_m,
        "trail_type": request.trail_type,
        "routing_algo": request.routing_algo,
        "trail_percentage": request.trail_percentage,
    }

    tcs = compute_tcs(route_data, request.terrain_context)
    return tcs


@router.get("/status", summary="Statut du moteur Clarity v7")
async def clarity_status():
    """Retourne le statut et la configuration du moteur."""
    return {
        "engine": "access_clarity_engine_v7",
        "status": "OPERATIONAL",
        "protocol": "BCE-4X GOLDEN",
        "tcs_weights": TCS_WEIGHTS,
        "render_config": CLARITY_RENDER,
        "pipeline": [
            "1. Suppression zigzags",
            "2. Douglas-Peucker",
            "3. Catmull-Rom interpolation",
            "4. TCS scoring (6 composantes)",
            "5. Auto-correction",
            "6. Rendu visuel bleu-clair",
        ],
        "grades": {
            "S": "95-100 (Exceptionnel)",
            "A": "80-94 (Excellent)",
            "B": "60-79 (Bon)",
            "C": "40-59 (Modere)",
            "D": "20-39 (Faible)",
            "F": "0-19 (Insuffisant)",
        },
    }
