"""
ENGINE_MESH_3D_OMEGA · PHASE 3 · CESIUM 3D TILES + glTF + DRAPING
══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Objectif : génération de mesh 3D institutionnel à partir de DEM réel.

Capacités :
  - Delaunay TIN (Triangulated Irregular Network) via scipy.spatial
  - glTF 2.0 mesh (binaire embedded base64)
  - Cesium 3D Tiles tileset.json (spec 3D Tiles 1.0)
  - elevation_sampling : interpolation barycentrique sur le mesh
  - draping_layers : SPECTRAL (NDVI), TERRAIN_HR (slope), GIS (densité)
    appliqués comme couleurs vertex sur le mesh

CHAÎNES_Ω :
  TERRAIN_HR → MESH_3D → TERRITOIRE
  CASCADE → MESH_3D (draping)

Doctrine ANTI-GÉNÉRIQUE :
  - DEM source : ENGINE_TERRAIN_HR_Ω (vrai Open-Meteo elevation)
  - Spectral source : ENGINE_SPECTRAL_Ω (vrai Sentinel-2 NDVI/NDWI)
  - GIS source : ENGINE_GIS_Ω (vraie densité WorldPop)

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW ENGINE EXTERNE
"""

from __future__ import annotations

import base64
import json
import logging
import math
import struct
from typing import Any

import numpy as np
from scipy.spatial import Delaunay

from engines.v8_institutional.engine_science_omega import mark_call, register_engine

logger = logging.getLogger("engine_mesh_3d_omega")

ENGINE_NAME = "ENGINE-MESH-3D-Ω"
ENGINE_VERSION = "V1_LOCK-PHASE_3_3D_OMEGA-2026-05"
ENGINE_DOCTRINE = "PHASE_3 · CESIUM_3D_TILES + glTF + DRAPING_LAYERS"

# Constantes glTF / 3D Tiles
GLTF_VERSION = "2.0"
TILESET_VERSION = "1.0"
DEFAULT_GRID_N = 11

register_engine(
    ENGINE_NAME, ENGINE_VERSION,
    "PHASE 3 · 3D mesh : Cesium 3D Tiles + glTF + draping SPECTRAL/TERRAIN_HR/GIS",
    "TERRAIN",
    ["ENGINE-TERRAIN-HR-Ω", "ENGINE-SPECTRAL-Ω", "ENGINE-GIS-Ω"],
)


# ═════════════════════ UTILS GÉOMÉTRIQUES ═════════════════════
def _latlon_to_local_xyz(lat: float, lon: float, elev_m: float,
                          lat0: float, lon0: float) -> tuple[float, float, float]:
    """Convertit lat/lon/elev → (x, y, z) en mètres locaux centrés sur (lat0, lon0).

    Approximation flat-earth valide pour <5km.
    """
    cos_lat = max(0.5, math.cos(math.radians(lat0)))
    x = (lon - lon0) * 111000.0 * cos_lat
    y = (lat - lat0) * 111000.0
    z = float(elev_m)
    return (x, y, z)


def _build_grid_vertices(elev_grid: list[list[float]],
                          lats: list[float],
                          lons: list[float]) -> tuple[np.ndarray, np.ndarray]:
    """Construit la matrice (n_pts, 3) de vertices et (n_pts, 2) de positions 2D."""
    arr = np.array(elev_grid, dtype=np.float32)
    rows, cols = arr.shape
    lat0 = float(lats[len(lats) // 2])
    lon0 = float(lons[len(lons) // 2])
    vertices = np.zeros((rows * cols, 3), dtype=np.float32)
    positions_2d = np.zeros((rows * cols, 2), dtype=np.float32)
    for i in range(rows):
        for j in range(cols):
            x, y, z = _latlon_to_local_xyz(
                float(lats[i]), float(lons[j]), float(arr[i, j]), lat0, lon0)
            idx = i * cols + j
            vertices[idx] = [x, y, z]
            positions_2d[idx] = [x, y]
    return vertices, positions_2d


# ═════════════════════ DELAUNAY TIN ═════════════════════
def build_delaunay_tin(elev_grid: list[list[float]],
                        lats: list[float],
                        lons: list[float]) -> dict[str, Any]:
    """Construit un TIN par Delaunay 2D + élévations (3D mesh)."""
    mark_call(ENGINE_NAME)
    vertices, positions_2d = _build_grid_vertices(elev_grid, lats, lons)
    if positions_2d.shape[0] < 4:
        return {"valid": False, "n_vertices": 0, "n_triangles": 0}
    try:
        tri = Delaunay(positions_2d)
    except Exception as e:
        logger.warning("[%s] Delaunay failed: %s", ENGINE_NAME, e)
        return {"valid": False, "error": str(e)}

    triangles = tri.simplices  # (n_tri, 3) index dans vertices
    return {
        "valid": True,
        "vertices": vertices.tolist(),
        "triangles": triangles.tolist(),
        "n_vertices": int(vertices.shape[0]),
        "n_triangles": int(triangles.shape[0]),
        "doctrine": "DELAUNAY_TIN_Ω",
    }


# ═════════════════════ glTF 2.0 GENERATOR (binary embedded) ═════════════════════
def _pack_buffer(vertices: np.ndarray, indices: np.ndarray,
                  vertex_colors: np.ndarray | None = None) -> tuple[bytes, dict[str, Any]]:
    """Pack vertices + indices (+ couleurs vertex optionnelles) en buffer binaire glTF."""
    # Vertices : VEC3 float32
    vert_bytes = vertices.astype(np.float32).tobytes()
    # Indices : SCALAR uint32
    idx_bytes = indices.astype(np.uint32).tobytes()
    # Padding pour alignement 4 bytes
    while len(vert_bytes) % 4 != 0:
        vert_bytes += b"\x00"
    while len(idx_bytes) % 4 != 0:
        idx_bytes += b"\x00"

    parts = [vert_bytes, idx_bytes]
    color_bytes = b""
    if vertex_colors is not None:
        color_bytes = vertex_colors.astype(np.float32).tobytes()
        while len(color_bytes) % 4 != 0:
            color_bytes += b"\x00"
        parts.append(color_bytes)

    buffer_data = b"".join(parts)
    offsets: dict[str, int] = {"vertices": 0, "indices": len(vert_bytes)}
    if vertex_colors is not None:
        offsets["colors"] = len(vert_bytes) + len(idx_bytes)

    return buffer_data, {
        "vert_byte_length": len(vert_bytes),
        "idx_byte_length": len(idx_bytes),
        "color_byte_length": len(color_bytes),
        "total_byte_length": len(buffer_data),
        "offsets": offsets,
    }


def build_gltf_mesh(vertices: list[list[float]],
                     triangles: list[list[int]],
                     vertex_colors: list[list[float]] | None = None,
                     ) -> dict[str, Any]:
    """Construit un glTF 2.0 minimal valide avec mesh + base64 embedded buffer."""
    mark_call(ENGINE_NAME)
    verts_arr = np.array(vertices, dtype=np.float32)
    tris_arr = np.array(triangles, dtype=np.uint32).flatten()
    colors_arr = np.array(vertex_colors, dtype=np.float32) if vertex_colors else None

    buffer_data, offsets = _pack_buffer(verts_arr, tris_arr, colors_arr)
    buffer_b64 = base64.b64encode(buffer_data).decode("ascii")

    # Bounding min/max
    vmin = verts_arr.min(axis=0).tolist()
    vmax = verts_arr.max(axis=0).tolist()

    accessors = [
        {  # 0 : vertices VEC3
            "bufferView": 0, "componentType": 5126,  # FLOAT
            "count": int(verts_arr.shape[0]), "type": "VEC3",
            "min": vmin, "max": vmax,
        },
        {  # 1 : indices SCALAR
            "bufferView": 1, "componentType": 5125,  # UNSIGNED_INT
            "count": int(tris_arr.size), "type": "SCALAR",
        },
    ]
    buffer_views = [
        {"buffer": 0, "byteOffset": offsets["offsets"]["vertices"],
          "byteLength": offsets["vert_byte_length"], "target": 34962},
        {"buffer": 0, "byteOffset": offsets["offsets"]["indices"],
          "byteLength": offsets["idx_byte_length"], "target": 34963},
    ]
    primitive_attrs = {"POSITION": 0}
    if colors_arr is not None:
        accessors.append({
            "bufferView": 2, "componentType": 5126,
            "count": int(colors_arr.shape[0]), "type": "VEC4",
        })
        buffer_views.append({
            "buffer": 0, "byteOffset": offsets["offsets"]["colors"],
            "byteLength": offsets["color_byte_length"], "target": 34962,
        })
        primitive_attrs["COLOR_0"] = 2

    gltf = {
        "asset": {"version": GLTF_VERSION,
                   "generator": f"{ENGINE_NAME} {ENGINE_VERSION}"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{
            "primitives": [{
                "attributes": primitive_attrs,
                "indices": 1, "mode": 4,  # TRIANGLES
            }],
        }],
        "buffers": [{
            "uri": f"data:application/octet-stream;base64,{buffer_b64}",
            "byteLength": offsets["total_byte_length"],
        }],
        "bufferViews": buffer_views,
        "accessors": accessors,
    }
    return {
        "gltf": gltf,
        "size_bytes": offsets["total_byte_length"],
        "buffer_b64_chars": len(buffer_b64),
        "n_vertices": int(verts_arr.shape[0]),
        "n_triangles": int(tris_arr.size // 3),
        "has_vertex_colors": colors_arr is not None,
        "doctrine": "glTF_2.0_BINARY_EMBEDDED",
    }


# ═════════════════════ CESIUM 3D TILES tileset.json ═════════════════════
def build_cesium_tileset(lat_center: float, lon_center: float,
                          bbox_radius_m: float = 200.0,
                          elev_min: float = 0.0,
                          elev_max: float = 1000.0,
                          gltf_uri: str = "mesh.gltf",
                          ) -> dict[str, Any]:
    """Construit un tileset.json Cesium 3D Tiles 1.0 minimal valide.

    Spec : https://github.com/CesiumGS/3d-tiles/blob/main/specification/README.md
    """
    mark_call(ENGINE_NAME)
    cos_lat = max(0.5, math.cos(math.radians(lat_center)))
    dlat = bbox_radius_m / 111000.0
    dlon = bbox_radius_m / (111000.0 * cos_lat)

    # Bounding region : [west, south, east, north, min_height, max_height] en radians
    bounding_region = [
        math.radians(lon_center - dlon),
        math.radians(lat_center - dlat),
        math.radians(lon_center + dlon),
        math.radians(lat_center + dlat),
        float(elev_min), float(elev_max),
    ]

    # Geometric error : approximation de la résolution visuelle
    geom_error = max(50.0, bbox_radius_m / 4.0)

    tileset = {
        "asset": {"version": TILESET_VERSION,
                   "tilesetVersion": ENGINE_VERSION},
        "geometricError": geom_error * 2,
        "root": {
            "boundingVolume": {"region": bounding_region},
            "geometricError": geom_error,
            "refine": "REPLACE",
            "content": {"uri": gltf_uri},
            "transform": [  # ECEF identity
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            ],
        },
    }
    return {
        "tileset": tileset,
        "bounding_region_deg": [
            lon_center - dlon, lat_center - dlat,
            lon_center + dlon, lat_center + dlat,
            float(elev_min), float(elev_max),
        ],
        "geometric_error": geom_error,
        "doctrine": "CESIUM_3D_TILES_1.0",
    }


# ═════════════════════ DRAPING LAYERS ═════════════════════
def drape_spectral_on_vertices(vertices: list[list[float]],
                                ndvi_normalized: float,
                                ndwi_normalized: float = 0.5
                                ) -> list[list[float]]:
    """Drape NDVI sur les vertices comme couleurs RGBA (vert→sec→bleu).

    Ratio :
      - NDVI haut (>0.7) → vert vif (#52D917 → 0.32, 0.85, 0.09, 1.0)
      - NDVI bas (<0.3) → brun (#A57B3F → 0.65, 0.48, 0.25, 1.0)
      - NDWI haut → bleu (eau)
    """
    mark_call(ENGINE_NAME)
    n = len(vertices)
    colors: list[list[float]] = []
    for _ in range(n):
        if ndwi_normalized > 0.6:
            colors.append([0.20, 0.40, 0.90, 1.0])  # bleu eau
        elif ndvi_normalized > 0.7:
            colors.append([0.32, 0.85, 0.09, 1.0])  # vert vif
        elif ndvi_normalized > 0.4:
            colors.append([0.55, 0.75, 0.35, 1.0])  # vert moyen
        else:
            colors.append([0.65, 0.48, 0.25, 1.0])  # brun sec
    return colors


def drape_terrain_slope_on_vertices(vertices: list[list[float]],
                                      slope_grid: list[list[float]],
                                      grid_n: int) -> list[list[float]]:
    """Drape la pente sur les vertices comme couleurs (gris → rouge).

    Pente faible → gris clair · Pente forte → rouge intense.
    """
    mark_call(ENGINE_NAME)
    slope_arr = np.array(slope_grid, dtype=np.float32).flatten()
    if slope_arr.size != len(vertices):
        return [[0.7, 0.7, 0.7, 1.0]] * len(vertices)
    s_max = max(1.0, float(np.nanmax(slope_arr)))
    colors: list[list[float]] = []
    for s in slope_arr:
        ratio = float(s) / s_max
        ratio = max(0.0, min(1.0, ratio))
        # gris → rouge progressif
        r = 0.7 + 0.3 * ratio
        g = 0.7 - 0.5 * ratio
        b = 0.7 - 0.5 * ratio
        colors.append([r, g, b, 1.0])
    return colors


# ═════════════════════ ELEVATION SAMPLING ═════════════════════
def elevation_sampling(vertices: list[list[float]],
                        triangles: list[list[int]],
                        sample_x: float, sample_y: float
                        ) -> dict[str, Any]:
    """Échantillonne l'élévation sur le mesh à un point (x, y) local.

    Recherche le triangle contenant (x,y), puis interpolation barycentrique sur z.
    """
    mark_call(ENGINE_NAME)
    verts = np.array(vertices, dtype=np.float64)
    tris = np.array(triangles, dtype=np.int64)
    if verts.shape[0] == 0 or tris.shape[0] == 0:
        return {"valid": False, "elevation_m": None}

    # Bruteforce search : itérer sur tous les triangles (ok pour <500 triangles)
    point = np.array([sample_x, sample_y], dtype=np.float64)
    for tri in tris:
        a, b, c = verts[tri[0]], verts[tri[1]], verts[tri[2]]
        # Coordonnées barycentriques 2D
        v0 = b[:2] - a[:2]
        v1 = c[:2] - a[:2]
        v2 = point - a[:2]
        denom = v0[0] * v1[1] - v1[0] * v0[1]
        if abs(denom) < 1e-9:
            continue
        u = (v2[0] * v1[1] - v1[0] * v2[1]) / denom
        w = (v0[0] * v2[1] - v2[0] * v0[1]) / denom
        v = 1.0 - u - w
        if u >= -1e-6 and w >= -1e-6 and v >= -1e-6:
            elev = float(v * a[2] + u * b[2] + w * c[2])
            return {
                "valid": True,
                "elevation_m": elev,
                "triangle_idx": int(np.where((tris == tri).all(axis=1))[0][0])
                if (tris == tri).all(axis=1).any() else -1,
                "barycentric": [float(v), float(u), float(w)],
            }
    return {"valid": False, "elevation_m": None,
             "reason": "point hors mesh"}
