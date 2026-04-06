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
    ORDONNANCE STEEVE-MAX 2026-04-07: MODE OFF — DESACTIVE.
    Archive: /app/LEGACY_ACCESS_AFFUTS/
    """
    return {
        "status": "disabled", "mode": "OFF",
        "ordonnance": "STEEVE-MAX 2026-04-07 — DESACTIVATION SECURISEE",
    }


@router.post("/score", summary="Calculer TCS seul")
async def compute_score_only(request: TCSScoreRequest):
    """
    ORDONNANCE STEEVE-MAX 2026-04-07: MODE OFF — DESACTIVE.
    """
    return {
        "status": "disabled", "mode": "OFF",
        "ordonnance": "STEEVE-MAX 2026-04-07 — DESACTIVATION SECURISEE",
    }


@router.get("/status", summary="Statut du moteur Clarity v7")
async def clarity_status():
    """Statut du moteur."""
    return {
        "engine": "access_clarity_engine_v7",
        "status": "disabled_by_ordonnance",
        "ordonnance": "STEEVE-MAX 2026-04-07 — DESACTIVATION SECURISEE",
        "archive": "/LEGACY_ACCESS_AFFUTS/",
    }
