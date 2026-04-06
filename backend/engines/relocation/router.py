"""
BCE-4X BLOC 3 — RELOCALISATION AUTOMATIQUE API
=================================================
ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0

Endpoints:
- POST /api/v1/relocation/evaluate  — Evaluer la necessite de relocalisation
- GET  /api/v1/relocation/status    — Statut du module
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic.relocation.router")

router = APIRouter(prefix="/api/v1/relocation", tags=["Relocalisation Automatique"])


class CurrentSaline(BaseModel):
    id: Optional[str] = "SAL-CURRENT"
    lat: float
    lng: float
    score: float = Field(..., ge=0, le=100)


class CurrentAffut(BaseModel):
    lat: float
    lng: float
    score: float = Field(..., ge=0, le=100)
    classification: str = Field("unknown", description="rejected/a_eviter/recommended")
    factors: Optional[dict] = None


class RelocationRequest(BaseModel):
    center_lat: float
    center_lng: float
    current_saline: CurrentSaline
    current_affut: CurrentAffut
    wind_direction_deg: float = Field(..., ge=0, lt=360)
    wind_speed_kmh: float = Field(..., ge=0)
    session: str = Field("matin")
    species: str = Field("ORIGNAL")
    month: int = Field(10, ge=1, le=12)
    terrain: Optional[dict] = None


@router.post("/evaluate")
async def evaluate_relocation(req: RelocationRequest):
    """
    Evaluer si une relocalisation est necessaire.

    Declencheur: saline >= 50 + affut impossible.
    Retourne le diagnostic du site actuel + alternative proposee.
    """
    try:
        # Phase 0: Construire les corridors UNIFIED pour la zone
        corridors = []
        try:
            from engines.corridor_unified.corridor_builder import build_unified_corridors
            corridors = build_unified_corridors(
                center_lat=req.center_lat,
                center_lng=req.center_lng,
                radius_m=600,
                species=req.species,
            )
        except Exception as e:
            logger.warning(f"[RELOCATION] Corridors indisponibles: {e}")

        # Phase 1-6: Evaluation relocalisation
        from engines.relocation.relocation_engine import evaluate_relocation

        terrain = req.terrain or _default_terrain()

        result = evaluate_relocation(
            current_saline={
                "id": req.current_saline.id,
                "lat": req.current_saline.lat,
                "lng": req.current_saline.lng,
                "score": req.current_saline.score,
            },
            current_affut={
                "lat": req.current_affut.lat,
                "lng": req.current_affut.lng,
                "score": req.current_affut.score,
                "classification": req.current_affut.classification,
                "factors": req.current_affut.factors or {},
            },
            center_lat=req.center_lat,
            center_lng=req.center_lng,
            terrain=terrain,
            wind_direction_deg=req.wind_direction_deg,
            wind_speed_kmh=req.wind_speed_kmh,
            session=req.session,
            species=req.species,
            month=req.month,
            corridors=corridors,
        )

        result["version"] = "RELOCATION_V1"
        result["governance"] = "BCE-4X GOLDEN V6+ — STEEVE-MAX"
        return result

    except Exception as e:
        logger.error(f"[RELOCATION] Erreur evaluation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def relocation_status():
    """Statut du module de relocalisation."""
    return {
        "engine": "relocation_automatique",
        "version": "1.0.0",
        "status": "active",
        "trigger": "saline >= 50 + affut impossible",
        "species_radius": {"CERF": 200, "ORIGNAL": 300, "WAPITI": 400},
        "composite_weights": {"saline": 0.40, "affut": 0.35, "bdre": 0.25},
        "governance": "BCE-4X GOLDEN V6+ — STEEVE-MAX",
    }


def _default_terrain():
    """Terrain par defaut pour les evaluations."""
    return {
        "foret": {"couvert_pct": 60, "strate_arbustive_pct": 30, "essences": ["SAPIN", "EPINETTE", "BOULEAU"]},
        "relief": {"pente_moyenne_pct": 8},
        "eau": {"distance_eau_m": 200},
        "nutriments_sol": {"NA": 80, "CA": 200, "MG": 50, "K": 100, "P": 15, "S": 10, "FE": 30, "ZN": 5, "MN": 20},
    }
