"""
NUTRITION-ENGINE-V7 — Pipeline central
========================================
Pipeline institutionnel:
  Sol → Nutriments → Plantes → Fourrage → Attractivite → Gibier

Consolide et remplace les logiques nutritionnelles dispersees:
  - soil_composition_engine (N1)
  - nutrient_deficiency_engine (N2)
  - wildlife_nutritional_engine (N3)
  - vegetation_forage_engine (N4)
  - hydrology_leaching_engine (N5)
  - seasonal_metabolism_engine (N6)
  - soil_engine (N10)
  - nutrition_v6_interface wrappers

Sorties normalisees 0-100 + metadonnees V7.
"""
import math
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("bionic.nutrition_engine_v7")

# ═══════════════════════════════════════════════════════
# IMPORTS V5 SOURCES (lecture seule — encapsulation V7)
# ═══════════════════════════════════════════════════════
from modules.saline_engine.engines.soil_composition_engine import (
    analyze_soil as _v5_soil, get_ecozone as _v5_ecozone
)
from modules.saline_engine.engines.nutrient_deficiency_engine import (
    analyze_deficiencies as _v5_deficiencies
)
from modules.saline_engine.engines.wildlife_nutritional_engine import (
    get_daily_needs as _v5_needs
)
from modules.saline_engine.engines.vegetation_forage_engine import (
    analyze_vegetation as _v5_vegetation
)
from modules.saline_engine.engines.hydrology_leaching_engine import (
    analyze_hydrology as _v5_hydrology
)
from modules.saline_engine.engines.seasonal_metabolism_engine import (
    get_metabolic_state as _v5_metabolism
)


# ═══════════════════════════════════════════════════════
# CONSTANTES V7
# ═══════════════════════════════════════════════════════

SPECIES_MAP = {
    "chevreuil": "chevreuil", "cerf": "chevreuil", "orignal": "orignal",
    "ours_noir": "ours_noir", "ours": "ours_noir",
    "dindon_sauvage": "dindon_sauvage", "dindon": "dindon_sauvage",
    "wapiti": "wapiti", "caribou": "caribou",
}

SENTINEL2_NDVI_BANDS = {"red": "B04", "nir": "B08"}

SOILGRIDS_LAYERS = ["nitrogen", "phh2o", "soc", "clay", "sand", "silt", "cec", "ocd"]

V7_WEIGHTS = {
    "soil_quality": 0.20,
    "nutrient_coverage": 0.25,
    "forage_quality": 0.20,
    "water_access": 0.10,
    "metabolic_demand": 0.15,
    "temporal_v7": 0.10,
}


# ═══════════════════════════════════════════════════════
# ETAPE 1 — SOIL LAYER (Sol)
# ═══════════════════════════════════════════════════════

def compute_soil_layer(lat: float, lng: float, season: str = "automne") -> Dict[str, Any]:
    """
    Couche Sol V7: Analyse pedologique + profil mineralogique.
    Sources: soil_composition_engine + soil_engine.
    Sortie: score 0-100, profil mineral, proprietes physiques.
    """
    raw = _v5_soil(lat, lng, season)
    ecozone = _v5_ecozone(lat, lng)

    minerals = raw.get("minerals", {})
    soil_quality = raw.get("soil_quality", 50)

    # Profil mineral normalise 0-100
    mineral_profile = {}
    for k, v in minerals.items():
        raw_val = v if isinstance(v, (int, float)) else v.get("score", v.get("value", 50)) if isinstance(v, dict) else 50
        mineral_profile[k] = {
            "raw_value": raw_val,
            "normalized": round(min(max(raw_val, 0), 100), 1),
        }

    return {
        "score": round(min(100, max(0, soil_quality)), 1),
        "ecozone": ecozone,
        "ph": raw.get("ph", 6.0),
        "texture": raw.get("texture", "inconnu"),
        "drainage": raw.get("drainage", "moyen"),
        "mineral_profile": mineral_profile,
        "seasonal_factors": raw.get("seasonal_factors", {}),
        "properties": {
            "retention": raw.get("retention", 50),
            "leaching_risk": raw.get("leaching_risk", 50),
            "organic_matter": raw.get("organic_matter", 3.0),
        },
        "data_sources": ["soil_composition_engine_v5", "SoilGrids_simulated"],
        "engine": "NUTRITION-ENGINE-V7-SOIL",
    }


# ═══════════════════════════════════════════════════════
# ETAPE 2 — NUTRIENT LAYER (Nutriments / Deficiences)
# ═══════════════════════════════════════════════════════

def compute_nutrient_layer(lat: float, lng: float, species: str,
                           season: str = "automne", sex: str = "male",
                           age: str = "adult") -> Dict[str, Any]:
    """
    Couche Nutriments V7: Besoins espece + deficiences terrain.
    Pipeline: Sol → Besoins espece → Deficiences.
    """
    sp = SPECIES_MAP.get(species.lower(), species)
    soil = _v5_soil(lat, lng, season)
    needs = _v5_needs(sp, season, sex, age)
    deficits = _v5_deficiencies(soil, needs)

    coverage = deficits.get("coverage_score", 50)
    critical = deficits.get("critical_deficits", [])
    all_deficits = deficits.get("deficits", [])

    return {
        "score": round(min(100, max(0, coverage)), 1),
        "species": sp,
        "daily_needs": needs.get("daily_needs", {}),
        "priority_minerals": needs.get("priority_minerals", []),
        "coverage_score": coverage,
        "deficits": all_deficits,
        "critical_count": len(critical),
        "critical_minerals": critical,
        "interactions": deficits.get("interactions", []),
        "data_sources": ["wildlife_nutritional_engine_v5", "nutrient_deficiency_engine_v5"],
        "engine": "NUTRITION-ENGINE-V7-NUTRIENTS",
    }


# ═══════════════════════════════════════════════════════
# ETAPE 3 — FORAGE LAYER (Fourrage / Vegetation)
# ═══════════════════════════════════════════════════════

def compute_forage_layer(lat: float, lng: float, month: int = 10,
                         species: str = "chevreuil") -> Dict[str, Any]:
    """
    Couche Fourrage V7: Qualite vegetation + phenologie + browse.
    Sources: vegetation_forage_engine + NDVI simule.
    """
    raw = _v5_vegetation(lat, lng, month)

    forage_quality = raw.get("forage_quality", 50)
    canopy = raw.get("canopy_density", 50)

    # NDVI simule (V7 — a remplacer par Sentinel-2 reel en V7.1)
    ndvi_simulated = round(0.3 + math.sin(math.radians(month * 30)) * 0.3, 2)
    ndvi_quality_boost = max(0, (ndvi_simulated - 0.3) * 50)

    return {
        "score": round(min(100, max(0, forage_quality + ndvi_quality_boost * 0.3)), 1),
        "forage_quality_base": forage_quality,
        "canopy_density": canopy,
        "phenology_stage": raw.get("phenology_stage", "inconnu"),
        "browse_availability": raw.get("browse_availability", 50),
        "mineral_content": raw.get("mineral_content", {}),
        "species_attractiveness": raw.get("species_attractiveness", {}),
        "ndvi": {
            "value": ndvi_simulated,
            "source": "simulated_seasonal_model",
            "sentinel2_integration": "planned_v7.1",
        },
        "data_sources": ["vegetation_forage_engine_v5", "NDVI_simulated"],
        "engine": "NUTRITION-ENGINE-V7-FORAGE",
    }


# ═══════════════════════════════════════════════════════
# ETAPE 4 — WATER LAYER (Hydrologie)
# ═══════════════════════════════════════════════════════

def compute_water_layer(lat: float, lng: float,
                        season: str = "automne") -> Dict[str, Any]:
    """
    Couche Hydrologie V7: Acces eau + drainage + lessivage.
    """
    raw = _v5_hydrology(lat, lng, season)

    return {
        "score": round(min(100, max(0, raw.get("water_score", 50))), 1),
        "drainage": raw.get("drainage", "moyen"),
        "leaching_risk": raw.get("leaching_risk", "moyen"),
        "distance_eau_m": raw.get("distance_eau_m", 500),
        "water_bodies_nearby": raw.get("water_bodies", 0),
        "saturation_risk": raw.get("saturation_risk", "faible"),
        "data_sources": ["hydrology_leaching_engine_v5"],
        "engine": "NUTRITION-ENGINE-V7-WATER",
    }


# ═══════════════════════════════════════════════════════
# ETAPE 5 — METABOLISM LAYER (Etat metabolique)
# ═══════════════════════════════════════════════════════

def compute_metabolism_layer(month: int, species: str = "chevreuil",
                             sex: str = "male") -> Dict[str, Any]:
    """
    Couche Metabolisme V7: Phase metabolique + besoins energetiques.
    """
    sp = SPECIES_MAP.get(species.lower(), species)
    raw = _v5_metabolism(month, sp, sex)

    phase = raw.get("phase", "inconnu")
    demand_map = {
        "hibernation_preparation": 60, "winter_conservation": 30,
        "spring_recovery": 75, "antler_growth": 90,
        "pre_rut_buildup": 85, "rut_peak": 95,
        "post_rut_recovery": 70, "summer_maintenance": 65,
    }
    demand_score = demand_map.get(phase, 50)

    return {
        "score": demand_score,
        "metabolic_phase": phase,
        "activity_level": raw.get("activity", "moyen"),
        "energy_demand_factor": raw.get("energy_demand_factor", 1.0),
        "priority_minerals": raw.get("priority_minerals", []),
        "visit_probability": raw.get("visit_probability", {}),
        "peak_hours": raw.get("peak_hours", []),
        "data_sources": ["seasonal_metabolism_engine_v5"],
        "engine": "NUTRITION-ENGINE-V7-METABOLISM",
    }


# ═══════════════════════════════════════════════════════
# ETAPE 6 — ATTRACTIVENESS SCORE (Score composite V7)
# ═══════════════════════════════════════════════════════

def compute_attractiveness_v7(lat: float, lng: float, species: str,
                              season: str = "automne", month: int = 10,
                              sex: str = "male", age: str = "adult",
                              include_temporal: bool = True) -> Dict[str, Any]:
    """
    Score d'attractivite nutritionnelle V7 — pipeline complet.
    Sol → Nutriments → Fourrage → Eau → Metabolisme → Temporel V7.
    Sortie: score 0-100 normalise + detail par couche.
    """
    soil = compute_soil_layer(lat, lng, season)
    nutrients = compute_nutrient_layer(lat, lng, species, season, sex, age)
    forage = compute_forage_layer(lat, lng, month, species)
    water = compute_water_layer(lat, lng, season)
    metabolism = compute_metabolism_layer(month, species, sex)

    # Temporel V7
    temporal_score = 50
    if include_temporal:
        now = datetime.now(timezone.utc)
        h = now.hour
        doy = (month - 1) * 30 + now.day
        crepuscular = species.lower() in ["chevreuil", "cerf", "orignal", "wapiti", "caribou"]
        temporal_score = 90 if (5 <= h <= 8 or 16 <= h <= 19) and crepuscular else 50
        phase = abs(((doy % 29.53) / 29.53) * 2 - 1)
        solunar_mod = 10 if phase < 0.15 else -5 if 0.4 < phase < 0.6 else 0
        temporal_score = min(100, max(0, temporal_score + solunar_mod))

    # Composite V7
    scores = {
        "soil_quality": soil["score"],
        "nutrient_coverage": nutrients["score"],
        "forage_quality": forage["score"],
        "water_access": water["score"],
        "metabolic_demand": metabolism["score"],
        "temporal_v7": temporal_score,
    }

    composite = sum(scores[k] * V7_WEIGHTS[k] for k in V7_WEIGHTS)
    composite = round(min(100, max(0, composite)), 1)

    # Rating
    if composite >= 80:
        rating = "premium"
    elif composite >= 60:
        rating = "optimal"
    elif composite >= 40:
        rating = "adequat"
    else:
        rating = "insuffisant"

    return {
        "attractiveness_score": composite,
        "rating": rating,
        "scores_detail": {k: round(v, 1) for k, v in scores.items()},
        "weights": V7_WEIGHTS,
        "layers": {
            "soil": soil,
            "nutrients": nutrients,
            "forage": forage,
            "water": water,
            "metabolism": metabolism,
        },
        "species": species,
        "season": season,
        "month": month,
        "location": {"lat": lat, "lng": lng},
        "pipeline": "Sol → Nutriments → Fourrage → Eau → Metabolisme → Temporel",
        "data_sources_count": 7,
        "engine": "NUTRITION-ENGINE-V7-ATTRACTIVENESS",
        "version": "7.0.0",
    }


# ═══════════════════════════════════════════════════════
# CONVENIENCE — Full pipeline result
# ═══════════════════════════════════════════════════════

def run_full_pipeline(lat: float, lng: float, species: str = "chevreuil",
                      season: str = "automne", month: int = 10,
                      sex: str = "male", age: str = "adult") -> Dict[str, Any]:
    """Execute le pipeline complet V7 en une seule invocation."""
    return compute_attractiveness_v7(lat, lng, species, season, month, sex, age)
