"""ENGINE_MESH_3D_Ω · Router FastAPI · PHASE 3."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from engines.spectral_omega import compute_spectral_at_point
from engines.terrain_hr_omega import (
    compute_slope_aspect,
    fetch_elevation_grid_open_meteo,
)

from . import (
    ENGINE_DOCTRINE,
    ENGINE_NAME,
    ENGINE_VERSION,
    build_cesium_tileset,
    build_delaunay_tin,
    build_gltf_mesh,
    drape_spectral_on_vertices,
    drape_terrain_slope_on_vertices,
    elevation_sampling,
)

router = APIRouter(prefix="/api/v20/mesh-3d", tags=["ENGINE_MESH_3D_Ω_PHASE_3"])


class PointBody(BaseModel):
    lat: float
    lon: float
    halo_m: float = 200.0
    grid_n: int = 11
    drape_spectral: bool = False
    drape_slope: bool = False


class SampleBody(BaseModel):
    vertices: list[list[float]]
    triangles: list[list[int]]
    sample_x: float
    sample_y: float


@router.get("/status")
async def m3d_status() -> dict[str, Any]:
    return {
        "engine_name": ENGINE_NAME, "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "capabilities": ["DELAUNAY_TIN", "glTF_2.0_BINARY",
                          "CESIUM_3D_TILES_1.0", "DRAPING_LAYERS",
                          "ELEVATION_SAMPLING"],
        "draping_layers_supported": ["SPECTRAL", "TERRAIN_HR", "GIS"],
        "active": True, "priority": 0,
    }


@router.post("/build")
async def m3d_build(body: PointBody) -> dict[str, Any]:
    """Construit un mesh 3D complet (TIN + glTF + tileset Cesium) au point."""
    # 1) Récupérer le DEM grid réel
    dem = fetch_elevation_grid_open_meteo(
        body.lat, body.lon, grid_n=body.grid_n, halo_m=body.halo_m)
    if not dem.get("available"):
        return {"ok": False, "error": "DEM unavailable", "dem": dem}

    elev_grid = dem["elevation_grid_m"]
    lats = dem["lats"]
    lons = dem["lons"]

    # 2) Construire le TIN Delaunay
    tin = build_delaunay_tin(elev_grid, lats, lons)
    if not tin.get("valid"):
        return {"ok": False, "error": "Delaunay TIN failed", "tin": tin}

    # 3) Optionnel : draping spectral / slope
    vertex_colors = None
    drape_info: dict[str, Any] = {}
    if body.drape_spectral:
        spec = compute_spectral_at_point(
            body.lat, body.lon, halo_m=body.halo_m,
            include_landsat_lst=False)
        vertex_colors = drape_spectral_on_vertices(
            tin["vertices"],
            float(spec.get("ndvi_normalized", 0.5)),
            float(spec.get("ndwi_normalized", 0.5)),
        )
        drape_info["spectral"] = {
            "ndvi_normalized": spec.get("ndvi_normalized"),
            "ndwi_normalized": spec.get("ndwi_normalized"),
        }
    if body.drape_slope and not vertex_colors:
        sa = compute_slope_aspect(elev_grid, cell_size_m=10.0)
        if sa.get("valid"):
            vertex_colors = drape_terrain_slope_on_vertices(
                tin["vertices"], sa["slope_pct"], body.grid_n)
            drape_info["slope"] = sa.get("stats", {})

    # 4) Générer le glTF
    gltf = build_gltf_mesh(tin["vertices"], tin["triangles"], vertex_colors)

    # 5) Générer le tileset Cesium
    tileset = build_cesium_tileset(
        body.lat, body.lon, bbox_radius_m=body.halo_m,
        elev_min=dem["stats"]["min_m"], elev_max=dem["stats"]["max_m"],
    )

    return {
        "ok": True,
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "lat": body.lat, "lon": body.lon, "halo_m": body.halo_m,
        "tin": {
            "n_vertices": tin["n_vertices"],
            "n_triangles": tin["n_triangles"],
        },
        "gltf": {
            "size_bytes": gltf["size_bytes"],
            "n_vertices": gltf["n_vertices"],
            "n_triangles": gltf["n_triangles"],
            "has_vertex_colors": gltf["has_vertex_colors"],
            "doc": gltf["gltf"],  # full glTF JSON pour Cesium
        },
        "tileset": tileset["tileset"],
        "tileset_meta": {
            "bounding_region_deg": tileset["bounding_region_deg"],
            "geometric_error": tileset["geometric_error"],
        },
        "draping": drape_info,
    }


@router.post("/tin")
async def m3d_tin(body: PointBody) -> dict[str, Any]:
    """Construit uniquement le TIN Delaunay (sans glTF)."""
    dem = fetch_elevation_grid_open_meteo(
        body.lat, body.lon, grid_n=body.grid_n, halo_m=body.halo_m)
    if not dem.get("available"):
        return {"ok": False, "error": "DEM unavailable"}
    return build_delaunay_tin(dem["elevation_grid_m"], dem["lats"], dem["lons"])


@router.post("/elevation-sample")
async def m3d_sample(body: SampleBody) -> dict[str, Any]:
    """Échantillonne l'élévation sur un mesh à un point local (x, y)."""
    return elevation_sampling(body.vertices, body.triangles,
                                body.sample_x, body.sample_y)
