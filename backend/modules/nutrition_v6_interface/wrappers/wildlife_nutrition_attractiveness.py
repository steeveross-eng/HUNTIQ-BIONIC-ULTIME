"""
Nutrition V6 — Wildlife Nutrition Attractiveness (Wrapper V5)
==============================================================
Directive x6800-A STEEVE-MAX — WRAPPERS V6 IMMEDIATS
BCE-4X GOLDEN V6+

Encapsule : wildlife_nutritional_engine (N3) + seasonal_metabolism_engine (N6)
            + nutrient_deficiency_engine (N2)
Interface V6 canonique pour attractivite nutritionnelle gibier.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

from modules.saline_engine.engines.wildlife_nutritional_engine import (
    get_daily_needs as _v5_get_daily_needs
)
from modules.saline_engine.engines.seasonal_metabolism_engine import (
    get_metabolic_state as _v5_get_metabolic_state
)
from modules.saline_engine.engines.nutrient_deficiency_engine import (
    analyze_deficiencies as _v5_analyze_deficiencies
)
from modules.saline_engine.engines.hydrology_leaching_engine import (
    analyze_hydrology as _v5_analyze_hydrology
)


def get_species_nutritional_needs(species: str, season: str = "automne",
                                  sex: str = "male",
                                  age: str = "adult") -> Dict[str, Any]:
    """V6 API: Besoins nutritionnels journaliers par espece."""
    raw = _v5_get_daily_needs(species, season, sex, age)
    return {
        "version": "v6",
        "source_engine": "wildlife_nutritional_engine_v5_wrapped",
        "species": species,
        "season": season,
        "sex": sex,
        "age": age,
        "daily_needs": raw.get("daily_needs", {}),
        "priority_minerals": raw.get("priority_minerals", []),
        "total_minerals_mg": raw.get("total_daily_mg", 0)
    }


def get_metabolic_state(month: int, species: str = "orignal",
                        sex: str = "male") -> Dict[str, Any]:
    """V6 API: Etat metabolique saisonnier."""
    raw = _v5_get_metabolic_state(month, species, sex)
    return {
        "version": "v6",
        "source_engine": "seasonal_metabolism_engine_v5_wrapped",
        "species": species,
        "month": month,
        "metabolic_phase": raw.get("phase", "unknown"),
        "activity_level": raw.get("activity", "unknown"),
        "priority_minerals": raw.get("priority_minerals", []),
        "visit_probability": raw.get("visit_probability", {}),
        "peak_hours": raw.get("peak_hours", []),
        "recommendations": raw.get("recommendations", [])
    }


def compute_wildlife_food_attractiveness(
        lat: float, lng: float, species: str,
        season: str = "automne", month: int = 10) -> Dict[str, Any]:
    """V6 API: Score d'attractivite alimentaire pour une espece a un point."""
    from modules.saline_engine.engines.soil_composition_engine import analyze_soil
    from modules.saline_engine.engines.vegetation_forage_engine import analyze_vegetation

    soil = analyze_soil(lat, lng, season)
    needs = _v5_get_daily_needs(species, season)
    deficits = _v5_analyze_deficiencies(soil, needs)
    hydro = _v5_analyze_hydrology(lat, lng, season)
    vegetation = analyze_vegetation(lat, lng, month)
    metabolism = _v5_get_metabolic_state(month, species)

    # Score d'attractivite base sur les deficits et la vegetation
    deficit_score = deficits.get("coverage_score", 50) / 100.0
    forage_score = vegetation.get("forage_quality", 50) / 100.0
    hydro_score = hydro.get("water_score", 50) / 100.0

    attractiveness = round(
        (deficit_score * 0.4 + forage_score * 0.35 + hydro_score * 0.25), 4
    )

    return {
        "version": "v6",
        "source_engine": "wildlife_nutrition_attractiveness_v5_wrapped",
        "location": {"lat": lat, "lng": lng},
        "species": species,
        "season": season,
        "attractiveness_score": attractiveness,
        "components": {
            "deficit_coverage": deficit_score,
            "forage_quality": forage_score,
            "water_access": hydro_score
        },
        "metabolic_phase": metabolism.get("phase", "unknown"),
        "priority_minerals": metabolism.get("priority_minerals", []),
        "deficit_details": deficits.get("deficits", [])
    }


def get_species_list() -> List[str]:
    """V6 API: Liste des especes supportees."""
    return ["orignal", "chevreuil", "ours_noir", "dindon_sauvage"]
