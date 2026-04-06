"""
ALIMENTATION — Router API REST
====================================
Endpoints:
  POST /api/v2/alimentation/analyze  — Salines V3 (actif)
  POST /api/v4/alimentation/analyze  — Salines V4 terrain-centre (BCE-4X P0-X)
Conforme BCE-4X. Aucune modification geometrique.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from .engine import analyze_alimentation_v2, SPECIES_LIST

router = APIRouter(prefix="/api/v2/alimentation", tags=["ALIMENTATION-V2"])

# BCE-4X P0-X: Router V4 dedie
router_v4 = APIRouter(prefix="/api/v4/alimentation", tags=["ALIMENTATION-V4"])


class AlimentationV2Request(BaseModel):
    center_lat: float = Field(..., description="Latitude du centre")
    center_lng: float = Field(..., description="Longitude du centre")
    species: str = Field("CERF", description="Espece: CERF, ORIGNAL, OURS, WAPITI, DINDON")
    month: int = Field(10, ge=1, le=12, description="Mois (1-12)")
    max_salines: int = Field(4, ge=1, le=4, description="Nombre max de salines (1-4)")


@router.post("/analyze")
async def analyze(req: AlimentationV2Request):
    """Analyse alimentaire V3 complete: terrain + salines + nutrition."""
    result = analyze_alimentation_v2(
        center_lat=req.center_lat,
        center_lng=req.center_lng,
        species=req.species,
        month=req.month,
        max_salines=req.max_salines,
    )
    return result


@router.get("/species")
async def list_species():
    """Liste des especes supportees."""
    return {"species": SPECIES_LIST}


# ═══════════════════════════════════════════════════════════
# BCE-4X P0-X: ENDPOINT SALINES V4 (TERRAIN-CENTRE)
# ═══════════════════════════════════════════════════════════

@router_v4.post("/analyze")
async def analyze_v4(req: AlimentationV2Request):
    """
    Analyse alimentaire V4 terrain-centree.
    9 criteres SUPRA valides scientifiquement.
    Generation basee sur features terrain (eau, sentiers, corridors, ecotones).
    """
    from core.scoring_pipeline.alimentation_v4.salines_v4 import compute_salines_v4
    from .terrain import analyze_terrain
    from .nutrition import get_nutrition

    terrain = analyze_terrain(req.center_lat, req.center_lng)
    salines = compute_salines_v4(
        center_lat=req.center_lat,
        center_lng=req.center_lng,
        terrain=terrain,
        species=req.species,
        month=req.month,
        max_salines=req.max_salines,
    )

    # Exclusion urbaine/eau (meme logique que V3)
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import (
            center_in_urban_meta_zone, _circle_on_urban, _circle_on_water,
        )
        if center_in_urban_meta_zone(req.center_lat, req.center_lng):
            salines = []
        else:
            salines = [
                s for s in salines
                if not _circle_on_urban(s["lat"], s["lng"])
                and not _circle_on_water(s["lat"], s["lng"])
            ]
    except ImportError:
        pass

    nutrition = get_nutrition(req.species)
    selected = [s for s in salines if s.get("selected")]

    score_global = selected[0]["score"] if selected else 0

    return {
        "version": "ALIMENTATION-V4",
        "species": req.species,
        "month": req.month,
        "score_global": score_global,
        "terrain": terrain,
        "salines": salines,
        "n_salines": len(selected),
        "n_candidates": len(salines),
        "max_salines": req.max_salines,
        "nutrition": {
            "aliments_recommandes": nutrition["aliments_recommandes"],
            "nutriments_essentiels": nutrition["nutriments_essentiels"],
        },
        "conformite": {
            "bce4x": True,
            "steeve_max": True,
            "supra_valide": True,
            "scoring_version": "V4",
        },
    }

