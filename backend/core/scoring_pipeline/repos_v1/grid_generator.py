"""
REPOS-V1 — Générateur de grille 10m×10m
==========================================
x3205: Delegue a common/grid.py (elimination duplication).
BCE-4X: Implementation identique, zero changement fonctionnel.
"""
from core.scoring_pipeline.common.grid import generate_grid as _generate_grid
from core.scoring_pipeline.common.grid import meters_per_deg_lng  # noqa: F401
from core.scoring_pipeline.common.constants import METERS_PER_DEG_LAT  # noqa: F401


def generate_grid_10m(center_lat: float, center_lng: float, side_m: float = 2000.0, cell_m: float = 10.0):
    """Proxy vers common/grid.generate_grid. Signature preservee."""
    return _generate_grid(center_lat, center_lng, side_m, cell_m)
