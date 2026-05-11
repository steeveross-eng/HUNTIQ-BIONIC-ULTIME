"""ENGINE_MESH_3D_Ω · Router FastAPI · PHASE 3."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
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
    pack_glb_binary,
)
from .gltf_store import get_gltf, make_cache_key, stats as store_stats, store_gltf

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

    # 6) ENDPOINT_GLTF_NATIF_Ω — Cache key + GLB packing + store
    cache_key = make_cache_key(
        body.lat, body.lon, body.halo_m, body.grid_n,
        body.drape_spectral, body.drape_slope,
    )
    # On stocke le glTF JSON avec uri EXTERNE pointant vers /gltf-binary/{cache_key}.bin
    gltf_external = gltf.get("gltf_external_buffer", gltf["gltf"])
    binary_buffer: bytes = gltf.get("binary_buffer", b"")
    glb_bytes = pack_glb_binary(gltf["gltf"], binary_buffer)
    store_gltf(cache_key, gltf_external, binary_buffer, glb_bytes, metadata={
        "lat": body.lat, "lon": body.lon, "halo_m": body.halo_m,
        "grid_n": body.grid_n,
        "drape_spectral": body.drape_spectral,
        "drape_slope": body.drape_slope,
        "n_vertices": gltf["n_vertices"],
        "n_triangles": gltf["n_triangles"],
    })

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
            "doc": gltf["gltf"],  # full glTF JSON pour Cesium (backcompat)
        },
        "tileset": tileset["tileset"],
        "tileset_meta": {
            "bounding_region_deg": tileset["bounding_region_deg"],
            "geometric_error": tileset["geometric_error"],
        },
        "draping": drape_info,
        # ENDPOINT_GLTF_NATIF_Ω — URLs natives à utiliser côté frontend
        "cache_key": cache_key,
        "glb_url": f"/api/v20/mesh-3d/gltf-binary/{cache_key}.glb",
        "gltf_url": f"/api/v20/mesh-3d/gltf/{cache_key}.gltf",
        "glb_size_bytes": len(glb_bytes),
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


# ═════════════════════ ENDPOINT_GLTF_NATIF_Ω ═════════════════════
# COMMANDE_INSTITUTIONNELLE_Ω · VERSION_ULTIME_ABSOLUE_X8
# Sert le glTF JSON et le GLB binaire pré-cachés en mémoire, avec
# Cache-Control public 1h + support ETag (If-None-Match → 304).

_CACHE_CONTROL = "public, max-age=3600"


def _etag_match(request: Request, etag: str) -> bool:
    """Vérifie If-None-Match. Supporte weak ETags (préfixe W/) — RFC 7232."""
    inm = request.headers.get("if-none-match", "").strip()
    if not inm:
        return False
    # Support quoted etag + comma-separated list + weak prefix W/
    for tag in inm.split(","):
        clean = tag.strip()
        if clean.startswith("W/"):
            clean = clean[2:]
        clean = clean.strip('"')
        if clean == etag:
            return True
    return False


@router.get("/gltf/{cache_key}.gltf")
async def m3d_gltf_native(cache_key: str, request: Request):
    """Sert le JSON glTF 2.0 (avec buffer.uri externe vers /gltf-binary).

    Headers : Cache-Control 1h, ETag SHA1 du GLB, support 304.
    """
    entry = get_gltf(cache_key)
    if entry is None:
        raise HTTPException(status_code=404,
                            detail=f"cache_key not found: {cache_key}")
    etag = entry["etag"]
    if _etag_match(request, etag):
        return Response(status_code=304, headers={
            "ETag": f'"{etag}"', "Cache-Control": _CACHE_CONTROL,
        })

    # On reconstruit le doc avec buffer.uri pointant vers l'endpoint binaire
    gltf_doc = json.loads(json.dumps(entry["gltf_json"]))  # deep copy
    if gltf_doc.get("buffers"):
        for buf in gltf_doc["buffers"]:
            # URI relatif autorisé par la spec glTF — le client Cesium
            # résoudra contre l'URL parent de la requête.
            buf["uri"] = f"./{cache_key}.bin"
            buf["byteLength"] = entry["size_bin"]
    return JSONResponse(content=gltf_doc, headers={
        "ETag": f'"{etag}"',
        "Cache-Control": _CACHE_CONTROL,
        "Content-Type": "model/gltf+json",
    })


@router.get("/gltf-binary/{cache_key}.glb")
async def m3d_glb_native(cache_key: str, request: Request):
    """Sert le glTF binaire (.glb) pré-packé du cache mémoire.

    Format conforme Khronos glTF 2.0 binary (magic 'glTF', version 2).
    Headers : Cache-Control 1h, ETag SHA1, support 304.
    Content-Type : model/gltf-binary
    """
    entry = get_gltf(cache_key)
    if entry is None:
        raise HTTPException(status_code=404,
                            detail=f"cache_key not found: {cache_key}")
    etag = entry["etag"]
    if _etag_match(request, etag):
        return Response(status_code=304, headers={
            "ETag": f'"{etag}"', "Cache-Control": _CACHE_CONTROL,
        })
    return Response(
        content=entry["glb_bytes"],
        media_type="model/gltf-binary",
        headers={
            "ETag": f'"{etag}"',
            "Cache-Control": _CACHE_CONTROL,
            "Content-Length": str(entry["size_glb"]),
        },
    )


@router.get("/gltf-binary/{cache_key}.bin")
async def m3d_bin_native(cache_key: str, request: Request):
    """Sert le buffer binaire brut (référencé par le glTF JSON via buffer.uri).

    Permet à Cesium de charger le glTF JSON externalisé sans re-télécharger
    le tileset complet. Cache-Control 1h + ETag.
    """
    entry = get_gltf(cache_key)
    if entry is None:
        raise HTTPException(status_code=404,
                            detail=f"cache_key not found: {cache_key}")
    etag = entry["etag"]
    if _etag_match(request, etag):
        return Response(status_code=304, headers={
            "ETag": f'"{etag}"', "Cache-Control": _CACHE_CONTROL,
        })
    return Response(
        content=entry["binary_buffer"],
        media_type="application/octet-stream",
        headers={
            "ETag": f'"{etag}"',
            "Cache-Control": _CACHE_CONTROL,
            "Content-Length": str(entry["size_bin"]),
        },
    )


@router.get("/gltf-cache/stats")
async def m3d_gltf_cache_stats() -> dict[str, Any]:
    """Statistiques du cache glTF (LRU mémoire)."""
    return {"ok": True, **store_stats()}
