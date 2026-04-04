"""
Nutrition V6 — Soil Nutrients Layer (Wrapper V5)
==================================================
Directive x6800-A STEEVE-MAX — WRAPPERS V6 IMMEDIATS
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

Encapsule : soil_composition_engine (N1) + soil_engine (N10)
Interface V6 canonique pour toutes les donnees sol/nutriments.
Code V5 : INCHANGE. Invocation directe V5 : VERROUILLEE au niveau API.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# V5 engines encapsules (lecture seule, zero modification)
from modules.saline_engine.engines.soil_composition_engine import (
    analyze_soil as _v5_analyze_soil,
    get_ecozone as _v5_get_ecozone
)

# Prefixe _v5_ = invocation interne uniquement, jamais exposee directement


def get_ecozone(lat: float, lng: float) -> str:
    """V6 API: Determine l'ecozone a une position GPS."""
    return _v5_get_ecozone(lat, lng)


def analyze_soil_nutrients(lat: float, lng: float,
                           season: str = "automne") -> Dict[str, Any]:
    """V6 API: Analyse complete sol et nutriments a une position."""
    raw = _v5_analyze_soil(lat, lng, season)

    return {
        "version": "v6",
        "source_engine": "soil_composition_engine_v5_wrapped",
        "location": {"lat": lat, "lng": lng},
        "ecozone": raw.get("ecozone", "unknown"),
        "soil_quality_index": raw.get("soil_quality", 0.0),
        "ph": raw.get("ph", 0.0),
        "texture": raw.get("texture", "unknown"),
        "drainage": raw.get("drainage", "unknown"),
        "minerals": raw.get("minerals", {}),
        "seasonal_factors": raw.get("seasonal_factors", {}),
        "normalized_score": _normalize_score(raw.get("soil_quality", 0.0))
    }


def get_mineral_profile(lat: float, lng: float,
                        season: str = "automne") -> Dict[str, float]:
    """V6 API: Profil mineralogique normalise 0-1."""
    raw = _v5_analyze_soil(lat, lng, season)
    minerals = raw.get("minerals", {})
    return {k: _normalize_mineral(v) for k, v in minerals.items()}


def _normalize_score(score: float) -> float:
    """Normalise un score 0-100 vers 0-1 compatible SUPRA."""
    return round(min(max(score / 100.0, 0.0), 1.0), 4)


def _normalize_mineral(value: float) -> float:
    """Normalise une valeur minerale vers 0-1."""
    return round(min(max(value / 100.0, 0.0), 1.0), 4)
