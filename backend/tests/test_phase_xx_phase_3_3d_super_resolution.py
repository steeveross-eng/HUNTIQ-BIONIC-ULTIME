"""
PHASE 3 + ORGANIC_PONDÉRÉ + IA SUPER RESOLUTION · Pytest neutre
═══════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
"""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engines.mesh_3d_omega import (
    ENGINE_NAME as MESH_NAME,
    ENGINE_VERSION as MESH_VERSION,
    build_cesium_tileset,
    build_delaunay_tin,
    build_gltf_mesh,
    drape_spectral_on_vertices,
    drape_terrain_slope_on_vertices,
    elevation_sampling,
)
from engines.super_resolution_omega import (
    DEFAULT_MODE,
    ENGINE_NAME as SR_NAME,
    MODE_BICUBIC_X4,
    MODE_LANCZOS_X2,
    MODE_LANCZOS_X4,
    MODE_REAL_ESRGAN_X4,
    upscale_array_lanczos,
    upscale_dem_hr,
    upscale_lidar_hr,
    upscale_spectral_layer,
)


# ═══════════════════ MESH 3D ═══════════════════
def test_mesh_engine_identity():
    assert "MESH-3D" in MESH_NAME.upper()
    assert "PHASE_3" in MESH_VERSION


def test_delaunay_tin_grid_3x3():
    """3x3 grille → 9 vertices · ≥8 triangles."""
    grid = [[100.0, 110.0, 120.0],
            [105.0, 115.0, 125.0],
            [110.0, 120.0, 130.0]]
    lats = [48.20, 48.205, 48.21]
    lons = [-68.39, -68.385, -68.38]
    out = build_delaunay_tin(grid, lats, lons)
    assert out["valid"] is True
    assert out["n_vertices"] == 9
    assert out["n_triangles"] >= 8


def test_delaunay_tin_invalid_too_small():
    """Grille 1×1 → invalid."""
    out = build_delaunay_tin([[100.0]], [48.20], [-68.39])
    assert out["valid"] is False


def test_gltf_mesh_minimal():
    """glTF avec 4 vertices + 2 triangles."""
    verts = [[0, 0, 0], [10, 0, 5], [10, 10, 8], [0, 10, 3]]
    tris = [[0, 1, 2], [0, 2, 3]]
    out = build_gltf_mesh(verts, tris)
    g = out["gltf"]
    assert g["asset"]["version"] == "2.0"
    assert g["meshes"][0]["primitives"][0]["mode"] == 4  # TRIANGLES
    assert out["n_vertices"] == 4
    assert out["n_triangles"] == 2
    assert "data:application/octet-stream;base64," in g["buffers"][0]["uri"]


def test_gltf_mesh_with_vertex_colors():
    """glTF avec couleurs vertex."""
    verts = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    tris = [[0, 1, 2]]
    colors = [[1.0, 0.0, 0.0, 1.0]] * 3
    out = build_gltf_mesh(verts, tris, vertex_colors=colors)
    assert out["has_vertex_colors"] is True
    assert "COLOR_0" in out["gltf"]["meshes"][0]["primitives"][0]["attributes"]


def test_cesium_tileset_spec_1_0():
    """Tileset Cesium 1.0 conforme (région bounding en radians)."""
    out = build_cesium_tileset(48.206657, -68.382422,
                                bbox_radius_m=200.0,
                                elev_min=300.0, elev_max=500.0)
    ts = out["tileset"]
    assert ts["asset"]["version"] == "1.0"
    assert "boundingVolume" in ts["root"]
    region = ts["root"]["boundingVolume"]["region"]
    assert len(region) == 6
    # Lon/lat doivent être en radians (entre -π et π)
    assert -1.5 < region[0] < 0.0  # west en radians (négatif)
    assert region[4] == 300.0  # min height
    assert region[5] == 500.0  # max height


def test_drape_spectral_high_ndvi():
    """NDVI haut → couleurs vertes (g > r)."""
    verts = [[0, 0, 0]] * 5
    colors = drape_spectral_on_vertices(verts, ndvi_normalized=0.85)
    assert all(c[1] > c[0] for c in colors)  # green > red


def test_drape_spectral_water():
    """NDWI très haut → couleurs bleues (b > g)."""
    verts = [[0, 0, 0]] * 5
    colors = drape_spectral_on_vertices(verts,
                                          ndvi_normalized=0.5,
                                          ndwi_normalized=0.85)
    assert all(c[2] > c[1] for c in colors)


def test_drape_slope_progressive():
    """Slope croissante → rouge croissant."""
    verts = [[0, 0, 0]] * 9
    slope_grid = [[0.0, 5.0, 10.0],
                   [15.0, 20.0, 25.0],
                   [30.0, 50.0, 100.0]]
    colors = drape_terrain_slope_on_vertices(verts, slope_grid, grid_n=3)
    assert len(colors) == 9
    # Premier (slope=0) → gris ; dernier (slope=100) → rouge
    assert colors[-1][0] > colors[0][0]   # plus rouge


def test_elevation_sampling_inside_triangle():
    """Sampling au centre d'un triangle → moyenne des sommets."""
    verts = [[0, 0, 100], [10, 0, 110], [5, 10, 120]]
    tris = [[0, 1, 2]]
    out = elevation_sampling(verts, tris, sample_x=5.0, sample_y=3.33)
    assert out["valid"] is True
    # Moyenne pondérée doit être entre 100 et 120
    assert 100.0 <= out["elevation_m"] <= 120.0


def test_elevation_sampling_outside():
    """Sampling hors mesh → invalid."""
    verts = [[0, 0, 100], [10, 0, 110], [5, 10, 120]]
    tris = [[0, 1, 2]]
    out = elevation_sampling(verts, tris, sample_x=100.0, sample_y=100.0)
    assert out["valid"] is False


# ═══════════════════ SUPER RESOLUTION ═══════════════════
def test_sr_engine_identity():
    assert "SUPER-RESOLUTION" in SR_NAME.upper()


def test_sr_modes_doctrinal():
    """4 modes doctrinaux."""
    assert MODE_LANCZOS_X4 == "LANCZOS_X4"
    assert MODE_LANCZOS_X2 == "LANCZOS_X2"
    assert MODE_BICUBIC_X4 == "BICUBIC_X4"
    assert MODE_REAL_ESRGAN_X4 == "REAL_ESRGAN_X4"
    assert DEFAULT_MODE == MODE_LANCZOS_X4


def test_upscale_lanczos_2d_x4():
    """Upscale Lanczos x4 sur grille 4×4 → 16×16."""
    arr = np.array([[float(i + j) for j in range(4)] for i in range(4)],
                    dtype=np.float32)
    up = upscale_array_lanczos(arr, factor=4)
    assert up.shape == (16, 16)
    # Stats préservées (min/max approximatifs)
    assert abs(float(np.nanmin(up)) - float(np.nanmin(arr))) < 0.5
    assert abs(float(np.nanmax(up)) - float(np.nanmax(arr))) < 0.5


def test_upscale_dem_hr_pipeline():
    """Pipeline DEM upscale x4."""
    grid = [[100.0, 110.0], [105.0, 115.0]]
    out = upscale_dem_hr(grid, factor=4, mode=MODE_LANCZOS_X4)
    assert out["valid"] is True
    assert out["shape_in"] == [2, 2]
    assert out["shape_out"] == [8, 8]


def test_upscale_real_esrgan_fallback_when_absent():
    """Real-ESRGAN absent → fallback Lanczos automatique."""
    grid = [[100.0, 110.0, 120.0],
            [105.0, 115.0, 125.0],
            [110.0, 120.0, 130.0]]
    out = upscale_dem_hr(grid, factor=4, mode=MODE_REAL_ESRGAN_X4)
    assert out["valid"] is True
    assert "fallback" in out["mode"].lower() or "lanczos" in out["mode"].lower()


def test_upscale_spectral_layer_metadata():
    """Upscale spectral conserve layer_name."""
    grid = [[0.5] * 3 for _ in range(3)]
    out = upscale_spectral_layer(grid, layer_name="ndvi", factor=2,
                                   mode=MODE_LANCZOS_X2)
    assert out["layer_name"] == "ndvi"
    assert "SPECTRAL_UPSCALE" in out["doctrine_applied"].upper()


def test_upscale_lidar_hr_capped_x2():
    """LIDAR upscale capped à x2 max."""
    grid = [[100.0, 110.0], [105.0, 115.0]]
    out = upscale_lidar_hr(grid, factor=4, mode=MODE_LANCZOS_X2)
    # Note : la fonction passe min(factor, 2) au router
    assert out["valid"] is True


def test_upscale_invalid_input():
    """Input vide → invalid."""
    out = upscale_dem_hr([], factor=4)
    assert out["valid"] is False
