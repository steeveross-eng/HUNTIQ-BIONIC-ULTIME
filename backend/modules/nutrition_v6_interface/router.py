"""
Nutrition V6 Interface — Router API canonique
================================================
Directive x6800-A STEEVE-MAX — WRAPPERS V6 IMMEDIATS
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

Source UNIQUE officielle pour :
  - soil_nutrients_layer
  - forage_quality_model
  - wildlife_nutrition_attractiveness
  - cross_layer_integration
  - nutrition_score
  - forage_quality_map
  - wildlife_food_attractiveness

VERROUILLAGE :
  Les moteurs V5 sous-jacents restent INCHANGES et fonctionnels
  mais NE SONT PLUS accessibles directement au niveau API V6.
  Toute consommation DOIT passer par cette interface.

Modules V5 encapsules (13 moteurs) :
  N1: soil_composition_engine
  N2: nutrient_deficiency_engine
  N3: wildlife_nutritional_engine
  N4: vegetation_forage_engine
  N5: hydrology_leaching_engine
  N6: seasonal_metabolism_engine
  N7: saline_recommendation_engine
  N8: bionic_engine_p0/nutrition_engine
  N9: bionic_engine_p0/phenology_engine
  N10: soil_engine
  N11: nutrition_engine/v1
  N12: bionic_ecological_engine/intelligence_core
  N13: bionic_ecological_engine/behavior_pipeline
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, Dict, List

from .wrappers import soil_nutrients_layer as snl
from .wrappers import forage_quality_model as fqm
from .wrappers import wildlife_nutrition_attractiveness as wna
from .wrappers import cross_layer_integration as cli

router = APIRouter(prefix="/api/v1/nutrition-v6", tags=["Nutrition V6 Interface"])


# ==============================================
# HEALTH + META
# ==============================================

@router.get("/health")
async def health():
    return {
        "status": "operational",
        "engine": "nutrition_v6_interface",
        "version": "6.0.0",
        "type": "wrapper_v5_encapsulation",
        "directive": "x6800-A",
        "v5_engines_wrapped": 13,
        "v5_engines_status": "locked_read_only",
        "modules": [
            "soil_nutrients_layer",
            "forage_quality_model",
            "wildlife_nutrition_attractiveness",
            "cross_layer_integration"
        ]
    }


@router.get("/lockout-status")
async def lockout_status():
    """Statut de verrouillage V5 → V6."""
    return {
        "v6_active": True,
        "v5_locked": True,
        "v5_engines_count": 13,
        "redirect_active": True,
        "directive": "x6800-A",
        "policy": "Toute consommation nutritionnelle DOIT passer par /api/v1/nutrition-v6/*"
    }


# ==============================================
# SOIL NUTRIENTS LAYER
# ==============================================

@router.get("/soil/analyze/{lat}/{lng}")
async def analyze_soil(lat: float, lng: float,
                       season: str = Query("automne")):
    """V6 API: Analyse sol et nutriments."""
    return snl.analyze_soil_nutrients(lat, lng, season)


@router.get("/soil/ecozone/{lat}/{lng}")
async def get_ecozone(lat: float, lng: float):
    """V6 API: Ecozone a une position."""
    return {"version": "v6", "ecozone": snl.get_ecozone(lat, lng)}


@router.get("/soil/minerals/{lat}/{lng}")
async def get_minerals(lat: float, lng: float,
                       season: str = Query("automne")):
    """V6 API: Profil mineralogique normalise."""
    return {"version": "v6", "minerals": snl.get_mineral_profile(lat, lng, season)}


# ==============================================
# FORAGE QUALITY MODEL
# ==============================================

@router.get("/forage/analyze/{lat}/{lng}")
async def analyze_forage(lat: float, lng: float,
                         month: int = Query(10)):
    """V6 API: Qualite fourrage a une position."""
    return fqm.analyze_forage_quality(lat, lng, month)


@router.get("/forage/map/{lat}/{lng}")
async def forage_quality_map(lat: float, lng: float,
                             radius_km: float = Query(5.0),
                             month: int = Query(10)):
    """V6 API: Carte de qualite fourrage."""
    return fqm.get_forage_quality_map(lat, lng, radius_km, month)


# ==============================================
# WILDLIFE NUTRITION ATTRACTIVENESS
# ==============================================

@router.get("/wildlife/needs/{species}")
async def species_needs(species: str,
                        season: str = Query("automne"),
                        sex: str = Query("male"),
                        age: str = Query("adult")):
    """V6 API: Besoins nutritionnels d'une espece."""
    return wna.get_species_nutritional_needs(species, season, sex, age)


@router.get("/wildlife/metabolism/{species}/{month}")
async def metabolic_state(species: str, month: int,
                          sex: str = Query("male")):
    """V6 API: Etat metabolique saisonnier."""
    return wna.get_metabolic_state(month, species, sex)


@router.get("/wildlife/attractiveness/{lat}/{lng}/{species}")
async def food_attractiveness(lat: float, lng: float, species: str,
                              season: str = Query("automne"),
                              month: int = Query(10)):
    """V6 API: Score d'attractivite alimentaire."""
    return wna.compute_wildlife_food_attractiveness(
        lat, lng, species, season, month)


@router.get("/wildlife/species")
async def list_species():
    """V6 API: Especes supportees."""
    return {"version": "v6", "species": wna.get_species_list()}


# ==============================================
# CROSS LAYER INTEGRATION
# ==============================================

@router.get("/cross-layer/{lat}/{lng}")
async def cross_layer(lat: float, lng: float,
                      species: str = Query("orignal"),
                      season: str = Query("automne"),
                      month: int = Query(10)):
    """V6 API: Analyse croisee complete Sol → Fourrage → Gibier."""
    return cli.compute_cross_layer_analysis(lat, lng, species, season, month)


@router.get("/nutrition-score/{lat}/{lng}")
async def nutrition_score(lat: float, lng: float,
                          species: str = Query("orignal"),
                          season: str = Query("automne"),
                          month: int = Query(10)):
    """V6 API: Score nutritionnel unifie."""
    return cli.get_nutrition_score(lat, lng, species, season, month)


@router.get("/layer-summary/{lat}/{lng}")
async def layer_summary(lat: float, lng: float,
                        species: str = Query("orignal")):
    """V6 API: Resume rapide des couches nutritionnelles."""
    return cli.get_layer_summary(lat, lng, species)
