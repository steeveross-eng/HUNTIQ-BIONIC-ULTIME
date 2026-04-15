"""
NUTRITION-ENGINE-V7 — Router API institutionnel
=================================================
Endpoints centraux:
  /api/v7/nutrition/soil-layer       — Couche Sol
  /api/v7/nutrition/nutrients        — Couche Nutriments/Deficiences
  /api/v7/nutrition/forage           — Couche Fourrage/Vegetation
  /api/v7/nutrition/water            — Couche Hydrologie
  /api/v7/nutrition/metabolism       — Couche Metabolisme
  /api/v7/nutrition/attractiveness   — Score composite V7 (pipeline complet)
  /api/v7/nutrition/full-pipeline    — Pipeline complet en une requete
  /api/v7/nutrition/status           — Statut du moteur

Consommateurs: TERRITOIRE, INTELLIGENCE, SUPRA, CARTE-2027
Hierarchie: NUTRITION-ENGINE-V7 = source unique nutritionnelle V7
"""
import time
import logging
from fastapi import APIRouter, Query
from typing import Optional

from .pipeline import (
    compute_soil_layer,
    compute_nutrient_layer,
    compute_forage_layer,
    compute_water_layer,
    compute_metabolism_layer,
    compute_attractiveness_v7,
    run_full_pipeline,
    SPECIES_MAP,
    V7_WEIGHTS,
)

logger = logging.getLogger("bionic.nutrition_engine_v7")
router = APIRouter(prefix="/api/v7/nutrition", tags=["Nutrition Engine V7"])


@router.get("/soil-layer")
async def soil_layer(
    lat: float = Query(...), lng: float = Query(...),
    season: str = Query("automne"),
):
    """Couche Sol V7: Analyse pedologique + profil mineral + proprietes."""
    start = time.time()
    result = compute_soil_layer(lat, lng, season)
    result["compute_ms"] = round((time.time() - start) * 1000)
    return result


@router.get("/nutrients")
async def nutrients(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("chevreuil"),
    season: str = Query("automne"),
    sex: str = Query("male"), age: str = Query("adult"),
):
    """Couche Nutriments V7: Besoins espece + deficiences + couverture."""
    start = time.time()
    result = compute_nutrient_layer(lat, lng, species, season, sex, age)
    result["compute_ms"] = round((time.time() - start) * 1000)
    return result


@router.get("/forage")
async def forage(
    lat: float = Query(...), lng: float = Query(...),
    month: int = Query(10), species: str = Query("chevreuil"),
):
    """Couche Fourrage V7: Qualite vegetation + phenologie + NDVI."""
    start = time.time()
    result = compute_forage_layer(lat, lng, month, species)
    result["compute_ms"] = round((time.time() - start) * 1000)
    return result


@router.get("/water")
async def water(
    lat: float = Query(...), lng: float = Query(...),
    season: str = Query("automne"),
):
    """Couche Hydrologie V7: Acces eau + drainage + lessivage."""
    start = time.time()
    result = compute_water_layer(lat, lng, season)
    result["compute_ms"] = round((time.time() - start) * 1000)
    return result


@router.get("/metabolism")
async def metabolism(
    month: int = Query(10), species: str = Query("chevreuil"),
    sex: str = Query("male"),
):
    """Couche Metabolisme V7: Phase + demande energetique + heures pic."""
    start = time.time()
    result = compute_metabolism_layer(month, species, sex)
    result["compute_ms"] = round((time.time() - start) * 1000)
    return result


@router.get("/attractiveness")
async def attractiveness(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("chevreuil"),
    season: str = Query("automne"), month: int = Query(10),
    sex: str = Query("male"), age: str = Query("adult"),
):
    """Score d'attractivite V7 — Pipeline complet Sol→Nutriments→Fourrage→Gibier."""
    start = time.time()
    result = compute_attractiveness_v7(lat, lng, species, season, month, sex, age)
    result["compute_ms"] = round((time.time() - start) * 1000)
    return result


@router.get("/full-pipeline")
async def full_pipeline(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("chevreuil"),
    season: str = Query("automne"), month: int = Query(10),
    sex: str = Query("male"), age: str = Query("adult"),
):
    """Pipeline complet V7 en une seule requete — identique a /attractiveness."""
    start = time.time()
    result = run_full_pipeline(lat, lng, species, season, month, sex, age)
    result["compute_ms"] = round((time.time() - start) * 1000)
    return result


@router.get("/status")
async def status():
    """Statut du moteur NUTRITION-ENGINE-V7."""
    return {
        "engine": "NUTRITION-ENGINE-V7",
        "version": "7.0.0",
        "status": "OPERATIONNEL",
        "pipeline": "Sol → Nutriments → Plantes → Fourrage → Attractivite → Gibier",
        "layers": [
            {"name": "Soil Layer", "endpoint": "/soil-layer", "source": "soil_composition_engine_v5"},
            {"name": "Nutrient Layer", "endpoint": "/nutrients", "source": "nutrient_deficiency_engine_v5 + wildlife_nutritional_engine_v5"},
            {"name": "Forage Layer", "endpoint": "/forage", "source": "vegetation_forage_engine_v5 + NDVI_simulated"},
            {"name": "Water Layer", "endpoint": "/water", "source": "hydrology_leaching_engine_v5"},
            {"name": "Metabolism Layer", "endpoint": "/metabolism", "source": "seasonal_metabolism_engine_v5"},
            {"name": "Attractiveness V7", "endpoint": "/attractiveness", "source": "composite_v7_pipeline"},
        ],
        "weights": V7_WEIGHTS,
        "species_supported": list(set(SPECIES_MAP.values())),
        "v5_engines_encapsulated": 7,
        "consumers": ["TERRITOIRE", "INTELLIGENCE-V7", "SUPRA", "CARTE-2027"],
        "planned_v71": ["SoilGrids_real", "Sentinel-2_NDVI", "RNCan_pedology", "IRDA_Quebec"],
    }
