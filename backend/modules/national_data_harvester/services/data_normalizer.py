"""
M1 — Data Normalizer : Normalisation multi-format
====================================================
Directive x6800-A — Phase M1 MAP Intelligence
BCE-4X GOLDEN V6+

ANTI-DOUBLON NUTRITIONNEL : Consomme soil_nutrients_layer V6
pour enrichissement nutritionnel des boundaries.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def normalize_boundary(raw_data: Dict, source_format: str = "geojson") -> Dict[str, Any]:
    """Normalise une limite dans le format BIONIC standard."""
    return {
        "boundary_id": raw_data.get("id", ""),
        "type": raw_data.get("type", "unknown"),
        "name": raw_data.get("name", raw_data.get("properties", {}).get("name", "")),
        "code": raw_data.get("code", ""),
        "geometry": raw_data.get("geometry", {}),
        "properties": raw_data.get("properties", {}),
        "source": raw_data.get("source", ""),
        "source_format": source_format,
        "normalized": True
    }


def enrich_with_nutrition(boundary: Dict, nutrition_data: Dict) -> Dict[str, Any]:
    """Enrichit une limite avec les donnees nutritionnelles V6."""
    boundary["nutrition_profile"] = {
        "soil_quality_index": nutrition_data.get("soil_quality_index", 0.0),
        "dominant_minerals": list(nutrition_data.get("minerals", {}).keys())[:3],
        "deficiency_risk": _compute_deficiency_risk(nutrition_data),
        "ecozone": nutrition_data.get("ecozone", "unknown"),
        "source": "nutrition_v6_interface"
    }
    return boundary


def _compute_deficiency_risk(nutrition: Dict) -> str:
    """Calcule le niveau de risque de deficit."""
    score = nutrition.get("soil_quality_index", 0)
    if isinstance(score, (int, float)):
        if score > 70:
            return "low"
        elif score > 40:
            return "moderate"
    return "high"
