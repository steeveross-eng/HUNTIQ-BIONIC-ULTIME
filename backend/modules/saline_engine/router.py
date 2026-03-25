"""
SALINE INTELLIGENCE ULTRA — API Router
Endpoints /api/v1/saline/*
Orchestre les 7 moteurs scientifiques pour analyse saline complete.

Interconnecte:
- soil_composition_engine
- nutrient_deficiency_engine
- wildlife_nutritional_engine
- vegetation_forage_engine
- hydrology_leaching_engine
- seasonal_metabolism_engine
- saline_recommendation_engine (maitre)

Services BIONIC reutilises:
- alimentation_v2/terrain (terrain analysis)
- solunar/engine (solunar data)
- weather_engine (meteo)

Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x1000
"""
import logging
from fastapi import APIRouter, Query
from typing import Optional

from .models import (
    SalineAnalysisRequest, SoilRequest, NutrientRequest,
    VegetationRequest, HydrologyRequest, MetabolismRequest,
    HealthResponse,
)
from .engines.soil_composition_engine import analyze_soil
from .engines.nutrient_deficiency_engine import analyze_deficiencies
from .engines.wildlife_nutritional_engine import get_daily_needs
from .engines.vegetation_forage_engine import analyze_vegetation
from .engines.hydrology_leaching_engine import analyze_hydrology
from .engines.seasonal_metabolism_engine import get_metabolic_state
from .engines.saline_recommendation_engine import generate_full_analysis

logger = logging.getLogger("saline.router")

router = APIRouter(
    prefix="/api/v1/saline",
    tags=["SALINE INTELLIGENCE ULTRA"],
)


# ═══════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="operational",
        engine="saline_intelligence_ultra",
        version="1.0.0",
        engines_count=7,
        message="SALINE INTELLIGENCE ULTRA — 7 moteurs scientifiques actifs | GOLDEN-BCE-4X",
    )


# ═══════════════════════════════════════════════
# ANALYSE COMPLETE (MOTEUR MAITRE)
# ═══════════════════════════════════════════════

@router.post("/analyze")
async def full_analysis(request: SalineAnalysisRequest):
    """
    Analyse COMPLETE Saline Intelligence Ultra.
    Orchestre les 7 sous-moteurs et produit la recommandation finale.
    Interconnecte: alimentation_v2/terrain, solunar/engine, weather.
    """
    # Fetch terrain data from alimentation_v2
    terrain = _get_terrain_data(request.lat, request.lng)

    # Fetch solunar data
    solunar_data = _get_solunar_data(request.lat, request.lng)

    result = generate_full_analysis(
        lat=request.lat,
        lng=request.lng,
        species=request.species.value,
        sex=request.sex.value,
        age=request.age.value,
        month=request.month,
        season=request.season.value,
        terrain=terrain,
        solunar_data=solunar_data,
        weather_data=None,
    )
    return result


@router.get("/analyze/quick")
async def quick_analysis(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    species: str = Query("orignal"),
    month: int = Query(10, ge=1, le=12),
    season: str = Query("automne"),
):
    """Analyse rapide GET — parametres minimaux."""
    terrain = _get_terrain_data(lat, lng)
    solunar_data = _get_solunar_data(lat, lng)

    result = generate_full_analysis(
        lat=lat, lng=lng,
        species=species, sex="male", age="adult",
        month=month, season=season,
        terrain=terrain, solunar_data=solunar_data,
    )
    return result


# ═══════════════════════════════════════════════
# SOUS-MOTEURS INDIVIDUELS
# ═══════════════════════════════════════════════

@router.post("/soil")
async def soil_analysis(request: SoilRequest):
    """Analyse sol uniquement (soil_composition_engine)."""
    return analyze_soil(request.lat, request.lng, request.season.value)


@router.get("/soil")
async def soil_analysis_get(
    lat: float = Query(...), lng: float = Query(...),
    season: str = Query("automne"),
):
    return analyze_soil(lat, lng, season)


@router.post("/nutrients")
async def nutrient_analysis(request: NutrientRequest):
    """Analyse deficiences nutritives (nutrient_deficiency_engine + wildlife_nutritional_engine)."""
    soil = analyze_soil(request.lat, request.lng, request.season.value)
    needs = get_daily_needs(request.species.value, request.season.value, request.sex.value, request.age.value)
    deficiency = analyze_deficiencies(soil, needs)
    return {
        "soil": soil,
        "needs": needs,
        "deficiency": deficiency,
    }


@router.get("/nutrients")
async def nutrient_analysis_get(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("orignal"), season: str = Query("automne"),
    sex: str = Query("male"), age: str = Query("adult"),
):
    soil = analyze_soil(lat, lng, season)
    needs = get_daily_needs(species, season, sex, age)
    deficiency = analyze_deficiencies(soil, needs)
    return {"soil": soil, "needs": needs, "deficiency": deficiency}


@router.post("/vegetation")
async def vegetation_analysis(request: VegetationRequest):
    """Analyse vegetation et fourrage (vegetation_forage_engine)."""
    terrain = _get_terrain_data(request.lat, request.lng)
    return analyze_vegetation(request.lat, request.lng, request.month, terrain)


@router.get("/vegetation")
async def vegetation_analysis_get(
    lat: float = Query(...), lng: float = Query(...),
    month: int = Query(10, ge=1, le=12),
):
    terrain = _get_terrain_data(lat, lng)
    return analyze_vegetation(lat, lng, month, terrain)


@router.post("/hydrology")
async def hydrology_analysis(request: HydrologyRequest):
    """Analyse hydrologique et lessivage (hydrology_leaching_engine)."""
    terrain = _get_terrain_data(request.lat, request.lng)
    soil = analyze_soil(request.lat, request.lng, request.season.value)
    return analyze_hydrology(request.lat, request.lng, request.season.value, terrain, soil)


@router.get("/hydrology")
async def hydrology_analysis_get(
    lat: float = Query(...), lng: float = Query(...),
    season: str = Query("automne"),
):
    terrain = _get_terrain_data(lat, lng)
    soil = analyze_soil(lat, lng, season)
    return analyze_hydrology(lat, lng, season, terrain, soil)


@router.post("/metabolism")
async def metabolism_analysis(request: MetabolismRequest):
    """Analyse metabolique saisonniere (seasonal_metabolism_engine + solunar)."""
    solunar_data = _get_solunar_data(46.8, -71.2)  # Default Quebec
    return get_metabolic_state(
        request.month, request.species.value, request.sex.value,
        solunar_data=solunar_data,
    )


@router.get("/metabolism")
async def metabolism_analysis_get(
    month: int = Query(10, ge=1, le=12),
    species: str = Query("orignal"),
    sex: str = Query("male"),
):
    solunar_data = _get_solunar_data(46.8, -71.2)
    return get_metabolic_state(month, species, sex, solunar_data=solunar_data)


@router.get("/species")
async def list_species():
    """Liste des especes supportees avec besoins de base."""
    from .engines.wildlife_nutritional_engine import SPECIES_NEEDS
    species_list = []
    for sp_key, sp_data in SPECIES_NEEDS.items():
        species_list.append({
            "id": sp_key,
            "base_weight_kg": sp_data["base_weight_kg"],
            "minerals_count": len(sp_data["minerals"]),
        })
    return {"species": species_list}


@router.get("/formulas")
async def list_formulas():
    """Liste des formules de produits salines disponibles."""
    from .engines.saline_recommendation_engine import PRODUCT_FORMULAS
    formulas = []
    for fid, f in PRODUCT_FORMULAS.items():
        formulas.append({
            "id": fid,
            "name": f["name"],
            "format": f["format"],
            "description": f["description"],
            "target_deficit": f["target_deficit"],
            "minerals": list(f["minerals"].keys()),
        })
    return {"formulas": formulas}


# ═══════════════════════════════════════════════
# COUCHES GEOSPATIALES (Phase B)
# ═══════════════════════════════════════════════

@router.get("/layers")
async def list_layers():
    """Liste des couches geospatiales disponibles."""
    from .layers.geospatial_layers import SALINE_LAYERS
    return {
        "layers": [
            {"id": lid, "name": layer.name, "source": layer.source}
            for lid, layer in SALINE_LAYERS.items()
        ]
    }


@router.get("/layers/all")
async def all_layers(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    """Recupere toutes les couches geospatiales pour un point."""
    from .layers.geospatial_layers import get_all_layers
    return {"lat": lat, "lng": lng, "layers": get_all_layers(lat, lng)}


@router.get("/layers/{layer_id}")
async def single_layer(
    layer_id: str,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    """Recupere une couche geospatiale specifique."""
    from .layers.geospatial_layers import get_layer
    return get_layer(layer_id, lat, lng)


@router.get("/suitability")
async def suitability_analysis(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    """Score d'aptitude saline base sur les couches geospatiales."""
    from .layers.geospatial_layers import compute_saline_suitability
    return compute_saline_suitability(lat, lng)


# ═══════════════════════════════════════════════
# HELPERS — Interconnexion BIONIC
# ═══════════════════════════════════════════════

def _get_terrain_data(lat: float, lng: float) -> Optional[dict]:
    """Recupere les donnees terrain via alimentation_v2."""
    try:
        from core.scoring_pipeline.alimentation_v2.terrain import analyze_terrain
        return analyze_terrain(lat, lng)
    except ImportError:
        logger.warning("alimentation_v2/terrain not available, using defaults")
        return None
    except Exception as e:
        logger.warning(f"Terrain analysis failed: {e}")
        return None


def _get_solunar_data(lat: float, lng: float) -> Optional[dict]:
    """Recupere les donnees solunaires via solunar/engine."""
    try:
        from modules.solunar.engine import compute_solunar
        return compute_solunar(lat, lng)
    except ImportError:
        logger.warning("solunar/engine not available")
        return None
    except Exception as e:
        logger.warning(f"Solunar computation failed: {e}")
        return None
