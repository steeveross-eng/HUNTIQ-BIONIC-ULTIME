"""ENGINE_TERRAIN_HR_OMEGA · Router FastAPI institutionnel · ORDRE N°50 PHASE 2."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from . import (
    DEM_TYPES,
    ENGINE_DOCTRINE,
    ENGINE_NAME,
    ENGINE_VERSION,
    chain_omega_terrain_pondere_corridors,
    compute_cost_surface,
    compute_roughness_tri,
    compute_slope_aspect,
    compute_terrain_hr_at_point,
    fetch_dem_opentopo_metadata,
    fetch_elevation_grid_open_meteo,
)

router = APIRouter(prefix="/api/v20/terrain-hr",
                    tags=["ENGINE_TERRAIN_HR_Ω_PHASE_2"])


class PointBody(BaseModel):
    lat: float
    lon: float
    halo_m: float = 200.0
    grid_n: int = 11
    lod: str = "MED"


class GridBody(BaseModel):
    elevation_grid_m: list[list[float]]
    cell_size_m: float = 30.0
    slope_penalty: float | None = 0.05


class ChainBody(BaseModel):
    terrain_hr: dict[str, Any]
    corridors: list[dict[str, Any]]


@router.get("/status")
async def th_status() -> dict[str, Any]:
    return {
        "engine_name": ENGINE_NAME, "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "dem_types_supported": DEM_TYPES,
        "lod": ["LOW", "MED", "HIGH"],
        "derivatives": ["slope_pct", "aspect_deg", "roughness_tri", "cost_surface"],
        "active": True, "priority": 0,
    }


@router.post("/compute")
async def th_compute(body: PointBody) -> dict[str, Any]:
    return compute_terrain_hr_at_point(
        body.lat, body.lon, halo_m=body.halo_m,
        grid_n=body.grid_n, lod=body.lod)


@router.post("/elevation-grid")
async def th_elev(body: PointBody) -> dict[str, Any]:
    return fetch_elevation_grid_open_meteo(
        body.lat, body.lon, grid_n=body.grid_n, halo_m=body.halo_m)


@router.post("/opentopo-metadata")
async def th_meta(body: PointBody) -> dict[str, Any]:
    return fetch_dem_opentopo_metadata(body.lat, body.lon, halo_m=body.halo_m)


@router.post("/derivatives/slope-aspect")
async def th_sa(body: GridBody) -> dict[str, Any]:
    return compute_slope_aspect(body.elevation_grid_m, body.cell_size_m)


@router.post("/derivatives/roughness")
async def th_tri(body: GridBody) -> dict[str, Any]:
    return compute_roughness_tri(body.elevation_grid_m)


@router.post("/derivatives/cost-surface")
async def th_cost(body: GridBody) -> dict[str, Any]:
    return compute_cost_surface(body.elevation_grid_m,
                                  cell_size_m=body.cell_size_m,
                                  slope_penalty=body.slope_penalty or 0.05)


@router.post("/chain-corridors")
async def th_chain(body: ChainBody) -> dict[str, Any]:
    out = chain_omega_terrain_pondere_corridors(body.corridors, body.terrain_hr)
    return {"ok": True, "n_corridors": len(out), "corridors": out}
