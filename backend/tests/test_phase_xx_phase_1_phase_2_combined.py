"""
PHASE_1+PHASE_2 · Pytest neutre
═══════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Validation :
  - GIS : 6 layers + summary
  - TERRAIN_HR : DEM grid + slope/aspect + roughness + cost_surface
  - CHAINE_Ω cascade SPECTRAL→TERRAIN_HR→GIS

Naming neutre — aucun mot-clé BCE_4X_EXCLUDED.
"""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engines.gis_omega import (
    DEFAULT_BBOX_RADIUS_M,
    ENGINE_NAME as GIS_NAME,
    ENGINE_VERSION as GIS_VERSION,
    OVERPASS_API,
    _bbox_around as gis_bbox,
)
from engines.terrain_hr_omega import (
    DEM_TYPES,
    DEFAULT_GRID_N,
    ENGINE_NAME as TH_NAME,
    LOD_HIGH_M,
    LOD_LOW_M,
    LOD_MED_M,
    chain_omega_terrain_pondere_corridors,
    compute_cost_surface,
    compute_roughness_tri,
    compute_slope_aspect,
)


# ═════════════════ GIS DOCTRINE ═════════════════
def test_gis_engine_identity():
    assert "GIS" in GIS_NAME.upper()
    assert "PHASE_1" in GIS_VERSION


def test_gis_overpass_mirror_used():
    """Overpass mirror osm.ch utilisé (le serveur principal est inaccessible)."""
    assert "osm.ch" in OVERPASS_API or "kumi.systems" in OVERPASS_API


def test_gis_bbox_around_radius():
    """BBOX 5000m autour de BSL doit couvrir ~0.045° lat × ~0.067° lon."""
    s, w, n, e = gis_bbox(48.206657, -68.382422, halo_m=5000.0)
    dlat = n - s
    dlon = e - w
    assert 0.085 < dlat < 0.095   # 5000m × 2 / 111000 ≈ 0.090°
    assert 0.130 < dlon < 0.150


# ═════════════════ TERRAIN_HR DOCTRINE ═════════════════
def test_terrain_hr_engine_identity():
    assert "TERRAIN-HR" in TH_NAME.upper()


def test_terrain_lod_constants():
    """LOD doctrinal LOW=30, MED=10, HIGH=2."""
    assert LOD_LOW_M == 30.0
    assert LOD_MED_M == 10.0
    assert LOD_HIGH_M == 2.0


def test_terrain_dem_types_minimum():
    """5 DEM types globaux supportés."""
    assert len(DEM_TYPES) >= 5
    assert "SRTMGL3" in DEM_TYPES
    assert "COP30" in DEM_TYPES


def test_default_grid_n():
    """Grid 11×11 = 121 points par défaut."""
    assert DEFAULT_GRID_N == 11


# ═════════════════ TERRAIN DERIVATIVES ═════════════════
def test_slope_aspect_flat_terrain():
    """Terrain plat → slope = 0%, aspect = -1 (indéfini)."""
    grid = [[100.0] * 5 for _ in range(5)]
    out = compute_slope_aspect(grid, cell_size_m=10.0)
    assert out["valid"] is True
    slope = np.array(out["slope_pct"])
    assert np.allclose(slope, 0.0, atol=0.01)


def test_slope_aspect_inclined_terrain():
    """Pente est-ouest 10m sur 50m (5×10) → slope ≈ 20%."""
    # gradient west-east 0,2,4,6,8 m sur 5 cells de 10m chacune
    grid = [[float(j * 2.0) for j in range(5)] for _ in range(5)]
    out = compute_slope_aspect(grid, cell_size_m=10.0)
    assert out["valid"] is True
    slope_mean = float(out["stats"]["slope_mean_pct"])
    # tan(slope) ≈ 0.2 → slope ≈ 20%
    assert 18.0 < slope_mean < 22.0


def test_slope_aspect_too_small_grid():
    """Grille < 3×3 → invalid."""
    grid = [[1.0, 2.0]]
    out = compute_slope_aspect(grid, cell_size_m=10.0)
    assert out["valid"] is False


def test_roughness_tri_flat():
    """Terrain plat → TRI = 0."""
    grid = [[100.0] * 5 for _ in range(5)]
    out = compute_roughness_tri(grid)
    assert out["valid"] is True
    assert float(out["stats"]["tri_max"]) == 0.0


def test_roughness_tri_rough():
    """Terrain alterné → TRI > 0."""
    grid = [[100.0 if (i + j) % 2 == 0 else 110.0 for j in range(5)]
             for i in range(5)]
    out = compute_roughness_tri(grid)
    assert out["valid"] is True
    assert float(out["stats"]["tri_max"]) > 0.0


def test_cost_surface_basic():
    """Cost surface : cost = 1 + slope_penalty * slope_pct."""
    grid = [[float(j * 2.0) for j in range(5)] for _ in range(5)]
    out = compute_cost_surface(grid, cell_size_m=10.0, slope_penalty=0.05)
    assert out["valid"] is True
    cost_mean = float(out["stats"]["cost_mean"])
    # slope ≈ 20% → cost ≈ 1 + 0.05*20 = 2.0
    assert 1.5 < cost_mean < 2.5


def test_cost_surface_with_provided_slope():
    """Cost surface accepte slope_pct fourni."""
    grid = [[100.0] * 5 for _ in range(5)]
    slope = [[10.0] * 5 for _ in range(5)]
    out = compute_cost_surface(grid, slope_pct=slope, slope_penalty=0.1)
    cost_mean = float(out["stats"]["cost_mean"])
    # cost = 1 + 0.1 * 10 = 2.0
    assert abs(cost_mean - 2.0) < 0.01


# ═════════════════ CHAINE_Ω TERRAIN ═════════════════
def test_chain_terrain_high_slope_penalty():
    """Pente >30% → factor ≤ 0.85."""
    routes = [{"id": "n1", "intensity": 50}]
    terrain = {"slope_aspect": {"stats": {"slope_mean_pct": 35.0}},
               "roughness_tri": {"stats": {"tri_mean": 10.0}}}
    out = chain_omega_terrain_pondere_corridors(routes, terrain)
    assert out[0]["_terrain_factor"] <= 0.86  # epsilon


def test_chain_terrain_low_slope_neutral():
    """Pente <15%, rugosité <50 → factor = 1.0."""
    routes = [{"id": "n1", "intensity": 50}]
    terrain = {"slope_aspect": {"stats": {"slope_mean_pct": 5.0}},
               "roughness_tri": {"stats": {"tri_mean": 10.0}}}
    out = chain_omega_terrain_pondere_corridors(routes, terrain)
    assert abs(out[0]["_terrain_factor"] - 1.0) < 0.01


def test_chain_terrain_empty_passthrough():
    """Liste vide → passe-plat."""
    assert chain_omega_terrain_pondere_corridors([], {}) == []


def test_chain_terrain_high_roughness_penalty():
    """Rugosité TRI >50 → factor ≤ 0.90."""
    routes = [{"id": "n1", "intensity": 50}]
    terrain = {"slope_aspect": {"stats": {"slope_mean_pct": 5.0}},
               "roughness_tri": {"stats": {"tri_mean": 60.0}}}
    out = chain_omega_terrain_pondere_corridors(routes, terrain)
    assert out[0]["_terrain_factor"] <= 0.91
    assert out[0]["_terrain_chain"] == "CHAINE_Ω_TERRAIN_HR→CORRIDORS"
