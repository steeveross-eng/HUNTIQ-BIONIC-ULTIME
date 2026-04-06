"""
BCE-4X BLOC 1 — CORRIDOR_UNIFIED API
=======================================
ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0

Endpoints:
- POST /api/v1/corridor-unified/build    — Construire les corridors unifies
- GET  /api/v1/corridor-unified/status   — Statut du module
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic.corridor_unified.router")

router = APIRouter(prefix="/api/v1/corridor-unified", tags=["Corridor Unified"])


class CorridorBuildRequest(BaseModel):
    center_lat: float = Field(..., description="Latitude du centre")
    center_lng: float = Field(..., description="Longitude du centre")
    radius_m: float = Field(600, ge=200, le=2000, description="Rayon en metres")
    species: str = Field("ORIGNAL", description="Espece ciblee")
    season: str = Field("automne", description="Saison")


@router.post("/build")
async def build_corridors(req: CorridorBuildRequest):
    """
    Construire et retourner les corridors UNIFIED pour une zone donnee.
    Fusion trail_graph OSM + BDRE interne.
    """
    try:
        from engines.corridor_unified.corridor_builder import build_unified_corridors

        corridors = build_unified_corridors(
            center_lat=req.center_lat,
            center_lng=req.center_lng,
            radius_m=req.radius_m,
            species=req.species,
            season=req.season,
        )

        n_critique = sum(1 for c in corridors if c["type"] == "CRITIQUE")
        n_majeur = sum(1 for c in corridors if c["type"] == "MAJEUR")
        n_mineur = sum(1 for c in corridors if c["type"] == "MINEUR")

        return {
            "corridors": corridors,
            "summary": {
                "total": len(corridors),
                "critique": n_critique,
                "majeur": n_majeur,
                "mineur": n_mineur,
            },
            "water_exclusion": {
                "active": True,
                "buffer_min_m": 30,
                "checks": ["is_water", "distance_eau_m", "midpoint", "25pct", "75pct"],
            },
            "center": {"lat": req.center_lat, "lng": req.center_lng},
            "radius_m": req.radius_m,
            "species": req.species,
            "season": req.season,
            "version": "CORRIDOR_UNIFIED_V1.1_HYDRO",
            "governance": "BCE-4X GOLDEN V6+ — STEEVE-MAX — MASQUE EAU ACTIF",
        }
    except Exception as e:
        logger.error(f"[CORRIDOR-UNIFIED] Erreur build: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def corridor_unified_status():
    """Statut du module CORRIDOR_UNIFIED."""
    return {
        "engine": "corridor_unified",
        "version": "1.0.0",
        "status": "active",
        "classification": {
            "CRITIQUE": "Sentier OSM + BDRE > 80 + connectivity >= 3",
            "MAJEUR": "Sentier OSM OU BDRE > 50",
            "MINEUR": "BDRE < 50 OU segment isole",
        },
        "attributs": [
            "intensite", "direction", "saisonnalite", "espece",
            "largeur", "zone_tampon", "risque",
        ],
        "consommateurs": [
            "SALINES_V4", "AFFUTS_V2", "BDRE", "SUPRA",
            "RELOCALISATION", "CONTAMINATION", "DIAGNOSTIC",
        ],
        "governance": "BCE-4X GOLDEN V6+ — STEEVE-MAX",
    }
