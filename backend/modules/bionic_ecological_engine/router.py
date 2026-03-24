"""
BIONIC Ecological Intelligence Engine — API Router
STEEVE-MAX x2000 / Phase A

Endpoints /api/v1/ecological-intelligence/*

Moteur ecologique unifie intégrant:
- Sol, hydrologie, vegetation, mineraux, carences
- Meteo, solunar, pression humaine
- Hotspots, zones, corridors
- Predictions multi-especes
- Scoring consolide
- Recommandations ecologiques
- Resumes executifs

Master Switch: guard("saline_intelligence") + guard("predictions") + guard("territory")
NOTE: En mode LOCKED, tous les endpoints retournent 503.
"""
import logging
from fastapi import APIRouter, Query, Depends
from typing import Optional

from .models import (
    AnalysisScale, SpeciesType, EcologicalQueryRequest,
    EcologicalIntelligenceResponse,
)
from .intelligence_core import run_ecological_analysis
from .behavior_pipeline import run_behavior_pipeline
from .species_profiles import get_all_species, get_species_profile, SPECIES_PROFILES
from .biogeography import (
    filter_species_for_coordinates, get_jurisdiction_info,
    get_species_status, is_species_present, is_species_huntable,
)

logger = logging.getLogger("bionic.ecological.router")

router = APIRouter(
    prefix="/api/v1/ecological-intelligence",
    tags=["BIONIC ECOLOGICAL INTELLIGENCE"],
)


# ═══════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════

@router.get("/health")
async def health():
    return {
        "status": "operational",
        "engine": "bionic_ecological_intelligence",
        "version": "2.0.0",
        "directive": "STEEVE-MAX x2250",
        "master_switch": "LOCKED",
        "species_count": len(SPECIES_PROFILES),
        "species_ids": list(SPECIES_PROFILES.keys()),
        "sub_engines": [
            "soil_composition", "hydrology_leaching", "vegetation_forage",
            "mineral_analysis", "weather_integration", "solunar_integration",
            "human_pressure", "hotspot_analysis", "corridor_analysis",
            "predictive_multi_species", "consolidated_scoring",
            "ecological_recommendations", "executive_summary",
            "species_profiles", "behavior_correlation_pipeline",
        ],
        "switches_required": [
            "saline_intelligence", "predictions", "territory", "weather", "scoring"
        ],
    }


# ═══════════════════════════════════════════════
# SPECIES REFERENCE API
# ═══════════════════════════════════════════════

@router.get("/species")
async def list_species():
    """Liste complete des especes integrees dans BIONIC"""
    return {
        "status": "success",
        "total": len(SPECIES_PROFILES),
        "species": get_all_species(),
    }


@router.get("/species/{species_id}")
async def species_detail(species_id: str):
    """Profil complet d'une espece (ecologie, alimentation, comportement, chasse, predictions)"""
    profile = get_species_profile(species_id)
    if not profile or profile["id"] != species_id:
        return {"status": "error", "message": f"Espece '{species_id}' non trouvee"}
    # Remove _id if present (MongoDB safety)
    return {
        "status": "success",
        "species": profile,
    }


@router.get("/species/{species_id}/ecology")
async def species_ecology(species_id: str):
    """Profil ecologique d'une espece"""
    profile = get_species_profile(species_id)
    return {
        "status": "success",
        "species_id": species_id,
        "name_fr": profile.get("name_fr", ""),
        "ecology": profile.get("ecology", {}),
        "diet": profile.get("diet", {}),
    }


@router.get("/species/{species_id}/hunting")
async def species_hunting(species_id: str):
    """Informations de chasse et reglementation d'une espece"""
    profile = get_species_profile(species_id)
    return {
        "status": "success",
        "species_id": species_id,
        "name_fr": profile.get("name_fr", ""),
        "hunting": profile.get("hunting", {}),
    }


# ═══════════════════════════════════════════════
# BIOGEOGRAPHY API (x2260)
# ═══════════════════════════════════════════════

@router.get("/biogeography/jurisdiction")
async def jurisdiction_info(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    """
    Determine la juridiction et les especes presentes a des coordonnees donnees.
    Retourne pays, province, especes presentes et chassables.
    """
    info = get_jurisdiction_info(lat, lng)
    return {"status": "success", **info}


@router.get("/biogeography/filter")
async def filter_species(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    only_huntable: bool = Query(False),
):
    """
    Filtre les especes disponibles selon les coordonnees.
    Aucune espece n'apparait dans une region ou elle n'existe pas.
    """
    species = filter_species_for_coordinates(lat, lng, only_huntable)
    from .biogeography import resolve_location
    country, province = resolve_location(lat, lng)
    return {
        "status": "success",
        "country": country,
        "province": province,
        "species_count": len(species),
        "species": species,
        "only_huntable": only_huntable,
    }


@router.get("/biogeography/species/{species_id}")
async def species_biogeography(
    species_id: str,
    lat: float = Query(None, ge=-90, le=90),
    lng: float = Query(None, ge=-180, le=180),
    country: str = Query(None),
    province: str = Query(None),
):
    """
    Statut biogeographique d'une espece dans une juridiction.
    Accepte soit lat/lng soit country/province.
    """
    if lat is not None and lng is not None:
        from .biogeography import resolve_location
        country, province = resolve_location(lat, lng)
    elif not country or not province:
        return {"status": "error", "message": "Fournir lat/lng ou country/province"}

    status = get_species_status(species_id, country, province)
    profile = get_species_profile(species_id)
    return {
        "status": "success",
        "species_id": species_id,
        "name_fr": profile.get("name_fr", ""),
        "country": country,
        "province": province,
        "biogeography": status,
        "present": is_species_present(species_id, country, province),
        "huntable": is_species_huntable(species_id, country, province),
    }


# ═══════════════════════════════════════════════
# FULL ANALYSIS
# ═══════════════════════════════════════════════

@router.get("/analyze", response_model=EcologicalIntelligenceResponse)
async def full_ecological_analysis(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_m: int = Query(600, ge=100, le=50000, description="Rayon en metres"),
    species: Optional[SpeciesType] = Query(None, description="Espece cible"),
    scale: AnalysisScale = Query(AnalysisScale.ZONE, description="Echelle d'analyse"),
):
    """
    Analyse ecologique complete.
    Orchestre tous les sous-moteurs et retourne une reponse unifiee.
    """
    req = EcologicalQueryRequest(
        lat=lat, lng=lng, radius_m=radius_m,
        species=species, scale=scale,
    )
    return run_ecological_analysis(req)


# ═══════════════════════════════════════════════
# PARTIAL ANALYSES
# ═══════════════════════════════════════════════

@router.get("/soil")
async def soil_analysis(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_m: int = Query(600, ge=100, le=50000),
):
    """Analyse du sol uniquement"""
    req = EcologicalQueryRequest(
        lat=lat, lng=lng, radius_m=radius_m,
        include_hydrology=False, include_vegetation=False,
        include_weather=False, include_solunar=False,
        include_pressure=False, include_predictions=False, include_scoring=False,
    )
    result = run_ecological_analysis(req)
    return {"status": "success", "soil": result.soil, "minerals": result.minerals}


@router.get("/habitat")
async def habitat_analysis(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_m: int = Query(600, ge=100, le=50000),
):
    """Carte d'habitat et corridors"""
    req = EcologicalQueryRequest(
        lat=lat, lng=lng, radius_m=radius_m,
        include_weather=False, include_solunar=False,
        include_predictions=False,
    )
    result = run_ecological_analysis(req)
    return {
        "status": "success",
        "vegetation": result.vegetation,
        "hotspots": [h.dict() for h in result.hotspots],
        "corridors": [c.dict() for c in result.corridors],
        "habitat_map": result.habitat_map.dict() if result.habitat_map else None,
        "scoring": result.scoring.dict() if result.scoring else None,
    }


@router.get("/predictions")
async def prediction_analysis(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    species: Optional[SpeciesType] = Query(None),
):
    """Predictions multi-especes"""
    req = EcologicalQueryRequest(
        lat=lat, lng=lng, species=species,
        include_soil=False, include_hydrology=False, include_vegetation=False,
        include_scoring=False,
    )
    result = run_ecological_analysis(req)
    return {
        "status": "success",
        "predictions": [p.dict() for p in result.predictions],
        "weather": result.weather.dict() if result.weather else None,
        "solunar": result.solunar.dict() if result.solunar else None,
    }


@router.get("/scoring")
async def territory_scoring(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_m: int = Query(600, ge=100, le=50000),
):
    """Score territoire consolide"""
    req = EcologicalQueryRequest(
        lat=lat, lng=lng, radius_m=radius_m,
        include_weather=False, include_solunar=False,
        include_predictions=False,
    )
    result = run_ecological_analysis(req)
    return {
        "status": "success",
        "scoring": result.scoring.dict() if result.scoring else None,
        "recommendations": [r.dict() for r in result.recommendations],
    }


@router.get("/executive-summary")
async def executive_summary(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_m: int = Query(600, ge=100, le=50000),
    species: Optional[SpeciesType] = Query(None),
):
    """Resume executif complet"""
    req = EcologicalQueryRequest(
        lat=lat, lng=lng, radius_m=radius_m, species=species,
    )
    result = run_ecological_analysis(req)
    return {
        "status": "success",
        "executive_summary": result.executive_summary.dict() if result.executive_summary else None,
        "scoring": result.scoring.dict() if result.scoring else None,
        "top_predictions": [p.dict() for p in result.predictions[:3]],
        "top_recommendations": [r.dict() for r in result.recommendations[:3]],
    }


@router.get("/behavioral-map")
async def behavioral_map(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_m: int = Query(1000, ge=100, le=50000),
):
    """Carte comportementale dynamique"""
    req = EcologicalQueryRequest(
        lat=lat, lng=lng, radius_m=radius_m,
        include_weather=False, include_solunar=False,
        include_predictions=False, include_scoring=False,
    )
    result = run_ecological_analysis(req)
    return {
        "status": "success",
        "hotspots": [h.dict() for h in result.hotspots],
        "corridors": [c.dict() for c in result.corridors],
        "habitat_map": result.habitat_map.dict() if result.habitat_map else None,
    }


# ═══════════════════════════════════════════════
# BEHAVIOR CORRELATION PIPELINE
# ═══════════════════════════════════════════════

@router.get("/behavior-pipeline")
async def behavior_correlation(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    species: str = Query("orignal", description="Espece cible"),
):
    """
    Pipeline comportemental global.
    Correle: deplacements x meteo x solunar x habitats x zones x
    corridors x hotspots x pression humaine.
    """
    result = run_behavior_pipeline(lat, lng, species)
    return {
        "status": result.status,
        "pipeline_id": result.pipeline_id,
        "species": result.species,
        "timestamp": result.timestamp,
        "correlation_matrix": [c.dict() for c in result.correlation_matrix],
        "behavior_patterns": [p.dict() for p in result.behavior_patterns],
        "temporal_analysis": result.temporal_analysis.dict() if result.temporal_analysis else None,
        "spatial_analysis": result.spatial_analysis.dict() if result.spatial_analysis else None,
        "pressure_impact": result.pressure_impact.dict() if result.pressure_impact else None,
        "key_insights": result.key_insights,
        "recommendations": result.recommendations,
    }


logger.info("BIONIC Ecological Intelligence Engine loaded — 16 endpoints, 8 species, biogeography active")
