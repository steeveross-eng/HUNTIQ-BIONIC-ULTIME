"""
Vegetation Analyzer — Analyse vegetation pour segments hors-sentier
PROTOCOLE BIONIC GOLDEN — Pipeline unique acces aux affuts V6
"""
import math
import logging

logger = logging.getLogger("access_engine_v6.vegetation")


def analyze_vegetation_corridor(
    path_coords: list,
    grid: dict,
    grid_size: int,
    resolution_m: int,
    center_lat: float,
    center_lng: float,
) -> dict:
    """
    Analyse la vegetation le long d'un chemin hors-sentier.
    Retourne les metriques: essences, maturite, couvert, encombrement.
    """
    half = grid_size // 2
    canopy_values = []
    slope_values = []
    favorable_cells = 0
    unfavorable_cells = 0
    total_cells = 0

    for coord in path_coords:
        lng, lat = coord[0], coord[1]
        gx = int((lng - center_lng) * 111320 * math.cos(math.radians(center_lat)) / resolution_m) + half
        gy = int((lat - center_lat) * 111320 / resolution_m) + half

        cell = grid.get((gx, gy))
        if cell:
            total_cells += 1
            canopy_values.append(cell.get("canopy", 0.5))
            slope_values.append(cell.get("slope_deg", 0))

            if cell.get("canopy", 0.5) < 0.6 and cell.get("slope_deg", 0) < 15:
                favorable_cells += 1
            else:
                unfavorable_cells += 1

    if not canopy_values:
        return _default_analysis()

    avg_canopy = sum(canopy_values) / len(canopy_values)
    max_slope = max(slope_values) if slope_values else 0
    avg_slope = sum(slope_values) / len(slope_values) if slope_values else 0

    # Classification maturite
    if avg_canopy < 0.3:
        maturity = "clairiere"
        encumbrance = "minimal"
        dominant_species = "graminee"
    elif avg_canopy < 0.5:
        maturity = "mature_open"
        encumbrance = "low"
        dominant_species = "sapin_baumier"
    elif avg_canopy < 0.7:
        maturity = "mature_dense"
        encumbrance = "moderate"
        dominant_species = "epinette_noire"
    else:
        maturity = "dense_young"
        encumbrance = "high"
        dominant_species = "regeneration_mixte"

    # Strategie d'acces
    if favorable_cells > unfavorable_cells:
        strategy = f"Foret {maturity.replace('_', ' ')}, sous-bois degage — passage favorable"
    elif favorable_cells > 0:
        strategy = f"Alternance zones ouvertes et denses — contournement partiel recommande"
    else:
        strategy = "Vegetation dense sur la totalite du segment — effort eleve"

    return {
        "canopy_avg": round(avg_canopy, 2),
        "slope_avg_deg": round(avg_slope, 1),
        "slope_max_deg": round(max_slope, 1),
        "encumbrance": encumbrance,
        "dominant_species": dominant_species,
        "maturity": maturity,
        "favorable_ratio": round(favorable_cells / max(total_cells, 1), 2),
        "strategy": strategy,
        "total_cells_analyzed": total_cells,
    }


def _default_analysis():
    return {
        "canopy_avg": 0.5,
        "slope_avg_deg": 5.0,
        "slope_max_deg": 10.0,
        "encumbrance": "moderate",
        "dominant_species": "mixte",
        "maturity": "mature_dense",
        "favorable_ratio": 0.5,
        "strategy": "Donnees insuffisantes — analyse par defaut",
        "total_cells_analyzed": 0,
    }
