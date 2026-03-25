"""
CORE Scoring Pipeline — Generateur de grille partage
========================================================
Directive x3205. Elimine la duplication entre alimentation_v1 et repos_v1.
Implementation identique a l'originale (alimentation_v1/grid_generator.py).
BCE-4X: ZERO changement fonctionnel.
"""
import math

from .constants import METERS_PER_DEG_LAT


def meters_per_deg_lng(lat: float) -> float:
    """Metres par degre de longitude a une latitude donnee."""
    return 111320.0 * math.cos(math.radians(lat))


def generate_grid(
    center_lat: float,
    center_lng: float,
    side_m: float = 2000.0,
    cell_m: float = 10.0,
) -> dict:
    """
    Genere une grille de cellules carrees sur un territoire.

    Args:
        center_lat/lng: Centre de la zone
        side_m: Cote du carre en metres
        cell_m: Taille d'une cellule en metres

    Returns:
        {center, side_m, cell_m, n_cells_per_side, total_cells, cells: [{row, col, lat, lng}]}
    """
    half_side = side_m / 2.0
    n_cells = int(side_m / cell_m)
    m_per_lng = meters_per_deg_lng(center_lat)

    lat_start = center_lat - (half_side / METERS_PER_DEG_LAT)
    lng_start = center_lng - (half_side / m_per_lng)

    d_lat = cell_m / METERS_PER_DEG_LAT
    d_lng = cell_m / m_per_lng

    cells = []
    for row in range(n_cells):
        for col in range(n_cells):
            cell_lat = lat_start + (row + 0.5) * d_lat
            cell_lng = lng_start + (col + 0.5) * d_lng
            cells.append({
                "row": row,
                "col": col,
                "lat": round(cell_lat, 7),
                "lng": round(cell_lng, 7),
            })

    return {
        "center": {"lat": center_lat, "lng": center_lng},
        "side_m": side_m,
        "cell_m": cell_m,
        "n_cells_per_side": n_cells,
        "total_cells": len(cells),
        "cells": cells,
    }
