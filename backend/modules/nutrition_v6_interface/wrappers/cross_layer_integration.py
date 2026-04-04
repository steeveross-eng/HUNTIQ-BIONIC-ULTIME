"""
Nutrition V6 — Cross Layer Integration (Wrapper V5)
=====================================================
Directive x6800-A STEEVE-MAX — WRAPPERS V6 IMMEDIATS
BCE-4X GOLDEN V6+

Encapsule : saline_recommendation_engine (N7) + bionic_ecological_engine (N12)
Interface V6 canonique pour integration croisee de toutes les couches.
Source unique officielle pour nutrition_score, cross_layer_integration.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

from modules.saline_engine.engines.saline_recommendation_engine import (
    generate_full_analysis as _v5_full_analysis
)


def compute_cross_layer_analysis(lat: float, lng: float,
                                 species: str = "orignal",
                                 season: str = "automne",
                                 month: int = 10) -> Dict[str, Any]:
    """V6 API: Analyse croisee complete Sol → Nutriments → Fourrage → Gibier."""
    raw = _v5_full_analysis(lat, lng, species, season, month)

    return {
        "version": "v6",
        "source_engine": "cross_layer_integration_v5_wrapped",
        "location": {"lat": lat, "lng": lng},
        "species": species,
        "season": season,
        "month": month,
        "nutrition_score": raw.get("intelligence_score", {}).get("global_score", 0.0),
        "layers": {
            "soil": raw.get("soil_analysis", {}),
            "deficiency": raw.get("deficiency_analysis", {}),
            "vegetation": raw.get("vegetation_analysis", {}),
            "hydrology": raw.get("hydrology_analysis", {}),
            "metabolism": raw.get("metabolism_analysis", {})
        },
        "placement": raw.get("placement", {}),
        "products": raw.get("recommended_products", []),
        "custom_recipe": raw.get("custom_recipe", {}),
        "intelligence_score": raw.get("intelligence_score", {}),
        "recommendations": raw.get("recommendations", [])
    }


def get_nutrition_score(lat: float, lng: float,
                        species: str = "orignal",
                        season: str = "automne",
                        month: int = 10) -> Dict[str, Any]:
    """V6 API: Score nutritionnel unifie a un point GPS."""
    result = compute_cross_layer_analysis(lat, lng, species, season, month)
    return {
        "version": "v6",
        "location": {"lat": lat, "lng": lng},
        "species": species,
        "nutrition_score": result["nutrition_score"],
        "intelligence_score": result["intelligence_score"],
        "normalized_score": _normalize(result["nutrition_score"])
    }


def get_layer_summary(lat: float, lng: float,
                      species: str = "orignal") -> Dict[str, float]:
    """V6 API: Resume rapide de toutes les couches nutritionnelles."""
    result = compute_cross_layer_analysis(lat, lng, species)
    layers = result.get("layers", {})
    return {
        "version": "v6",
        "soil_quality": layers.get("soil", {}).get("soil_quality", 0),
        "deficiency_coverage": layers.get("deficiency", {}).get("coverage_score", 0),
        "forage_quality": layers.get("vegetation", {}).get("forage_quality", 0),
        "water_access": layers.get("hydrology", {}).get("water_score", 0),
        "metabolic_demand": 1.0,
        "overall_score": result["nutrition_score"]
    }


def _normalize(score: float) -> float:
    return round(min(max(score / 100.0, 0.0), 1.0), 4)
