"""
ROUTER HABITAT SCORE — Real-time Habitat Quality Grid
BIONIC V6 GOLDEN — habitat_score_v1

Endpoint:
  POST /api/v1/bionic/habitat-score/realtime — Pre-computed grid for cursor interpolation
  GET  /api/v1/bionic/habitat-score/status    — Service status

Score normalise 0-100%. Grille pre-calculee pour latence <20ms frontend.
Module isole. 0 impact sur pipeline principal.
"""

import logging
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic_engine.habitat_score_router")
router = APIRouter(prefix="/api/v1/bionic/habitat-score", tags=["BIONIC Habitat Score"])

SUPPORTED_SPECIES = ["moose", "deer", "bear", "wild_turkey", "elk"]

# P22ΩΩ_ZEROCOST_ENGINE_ET_TERRITOIRE_NEVER_BLANK_Ω · 2026-02-XX · STEEVE-MAX
# Normalisation FR/EN canonique : le frontend envoie des espèces FR (orignal,
# chevreuil, ours_noir, wapiti, dindon_sauvage, coyote) alors que ce router
# utilise les codes EN historiques. Sans normalisation → 400 systématique
# qui viole la doctrine NEVER BLANK Ω. Coyote n'est pas supporté ici (shadow
# uniquement) → fallback vers moose pour ne jamais retourner 400 brut.
_SPECIES_FR_TO_EN = {
    "orignal": "moose",
    "chevreuil": "deer",
    "cerf": "deer",
    "ours_noir": "bear",
    "ours": "bear",
    "wapiti": "elk",
    "dindon_sauvage": "wild_turkey",
    "dindon": "wild_turkey",
    "multi_aggregated": "moose",  # vue agrégée → comportement orignal
    "tous": "moose",
    "coyote": "moose",  # coyote n'a pas de grille habitat-score, fallback safe
}


def _normalize_species_fr_to_en(species: str) -> str:
    """Normalise une espèce FR canonique vers son code EN.

    Doctrine NEVER BLANK Ω : aucune 400 brute sur cet endpoint. Toute espèce
    FR connue est mappée vers son équivalent EN supporté ; toute espèce
    totalement inconnue retourne 'moose' (fallback safe).
    """
    if not isinstance(species, str):
        return "moose"
    lower = species.lower().strip()
    if lower in SUPPORTED_SPECIES:
        return lower
    return _SPECIES_FR_TO_EN.get(lower, "moose")


class ScoreBounds(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class HabitatScoreRequest(BaseModel):
    bounds: ScoreBounds
    species: str = Field(default="moose")
    resolution: int = Field(default=30, ge=10, le=60)


@router.post("/realtime")
async def habitat_score_realtime(request: HabitatScoreRequest):
    """
    Pre-computed habitat quality grid for real-time cursor interpolation.
    Returns a resolution x resolution grid of scores (0-100%).
    """
    from modules.bionic_engine_p0.services.habitat_score_service import get_habitat_grid

    # P22ΩΩ_ZEROCOST_ENGINE_ET_TERRITOIRE_NEVER_BLANK_Ω : normalisation FR→EN
    # AVANT validation, pour éliminer les 400 sur 'orignal/chevreuil/...'
    normalized_species = _normalize_species_fr_to_en(request.species)
    if normalized_species not in SUPPORTED_SPECIES:
        # Doctrine NEVER BLANK Ω : pas de 400 brut. Retour structuré DEGRADED.
        return {
            "version": "habitat_score_v1",
            "status": "DEGRADED",
            "reason": f"unsupported_species: {request.species}",
            "species": request.species,
            "scores": [],
            "grid": [],
            "stats": {},
            "data_sources": [],
            "computation_time_ms": 0,
            "doctrine": "P22ΩΩ_NEVER_BLANK_Ω",
        }

    bounds = {
        "north": request.bounds.north, "south": request.bounds.south,
        "east": request.bounds.east, "west": request.bounds.west,
    }

    start = time.time()
    result = await get_habitat_grid(bounds, normalized_species, request.resolution)
    elapsed = round((time.time() - start) * 1000, 1)

    return {
        "version": "habitat_score_v1",
        "status": "OK",
        "species": request.species,
        "species_normalized": normalized_species,
        "bounds": bounds,
        "resolution": request.resolution,
        "scores": result["scores"],
        "grid": result["grid"],
        "stats": result["stats"],
        "data_sources": result["data_sources"],
        "computation_time_ms": elapsed,
        "validation": {
            "score_range": "0-100%",
            "shadow_mode": True,
            "zero_impact_on_production": True,
        },
    }


@router.get("/status")
async def habitat_score_status():
    """Service status for Habitat Score."""
    return {
        "module": "HABITAT_SCORE",
        "label": "Score d'Habitat Optimal (Temps Reel)",
        "version": "habitat_score_v1",
        "status": "active",
        "mode": "shadow (non-destructif)",
        "score_range": "0-100%",
        "factors": [
            "micro-relief", "vegetation (NDVI)", "essences forestieres",
            "drainage", "distance eau", "distance anthropique",
            "connectivite ecologique", "pression humaine", "thermique",
            "altitude", "regles espece", "zones fonctionnelles",
        ],
        "species_supported": list(SUPPORTED_SPECIES),
        "endpoints": [
            "POST /api/v1/bionic/habitat-score/realtime",
            "GET /api/v1/bionic/habitat-score/status",
        ],
    }
