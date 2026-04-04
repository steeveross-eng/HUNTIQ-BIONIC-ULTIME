"""
Nutrition V6 — Forage Quality Model (Wrapper V5)
==================================================
Directive x6800-A STEEVE-MAX — WRAPPERS V6 IMMEDIATS
BCE-4X GOLDEN V6+

Encapsule : vegetation_forage_engine (N4) + phenology_engine (N9)
Interface V6 canonique pour qualite fourrage et phenologie.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

from modules.saline_engine.engines.vegetation_forage_engine import (
    analyze_vegetation as _v5_analyze_vegetation
)


def analyze_forage_quality(lat: float, lng: float,
                           month: int = 10,
                           terrain: Dict = None) -> Dict[str, Any]:
    """V6 API: Analyse qualite fourrage a une position."""
    raw = _v5_analyze_vegetation(lat, lng, month, terrain)

    return {
        "version": "v6",
        "source_engine": "vegetation_forage_engine_v5_wrapped",
        "location": {"lat": lat, "lng": lng},
        "month": month,
        "dominant_type": raw.get("dominant_type", "unknown"),
        "canopy_density": raw.get("canopy_density", 0.0),
        "forage_quality_index": raw.get("forage_quality", 0.0),
        "mineral_content": raw.get("mineral_content", {}),
        "phenology_stage": raw.get("phenology_stage", "unknown"),
        "browse_availability": raw.get("browse_availability", 0.0),
        "species_attractiveness": raw.get("species_attractiveness", {}),
        "normalized_score": _normalize(raw.get("forage_quality", 0.0))
    }


def get_forage_quality_map(lat: float, lng: float,
                           radius_km: float = 5.0,
                           month: int = 10) -> Dict[str, Any]:
    """V6 API: Carte de qualite fourrage dans un rayon."""
    center = analyze_forage_quality(lat, lng, month)
    offsets = [
        (lat + 0.01, lng), (lat - 0.01, lng),
        (lat, lng + 0.01), (lat, lng - 0.01)
    ]
    samples = [analyze_forage_quality(la, ln, month) for la, ln in offsets]
    scores = [center["forage_quality_index"]] + [s["forage_quality_index"] for s in samples]

    return {
        "version": "v6",
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "avg_forage_quality": round(sum(scores) / len(scores), 2),
        "max_forage_quality": max(scores),
        "min_forage_quality": min(scores),
        "sample_count": len(scores),
        "center_analysis": center
    }


def _normalize(score: float) -> float:
    return round(min(max(score / 100.0, 0.0), 1.0), 4)
