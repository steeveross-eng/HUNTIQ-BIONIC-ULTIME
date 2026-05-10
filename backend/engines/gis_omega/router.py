"""ENGINE_GIS_OMEGA · Router FastAPI institutionnel · ORDRE N°50 PHASE 1."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from . import (
    ENGINE_DOCTRINE,
    ENGINE_NAME,
    ENGINE_VERSION,
    compute_corridors_gis,
    fetch_foret_mffp,
    fetch_limites,
    fetch_pression_humaine,
    fetch_routes_mtq,
    fetch_sol_irda,
    fetch_zec_sepaq,
    gis_layers_summary,
)

router = APIRouter(prefix="/api/v20/gis", tags=["ENGINE_GIS_Ω_PHASE_1"])


class PointBody(BaseModel):
    lat: float
    lon: float
    halo_m: float = 5000.0


class MaskBody(BaseModel):
    lat: float
    lon: float
    halo_m: float = 5000.0
    corridors: list[dict[str, Any]]


@router.get("/status")
async def gis_status() -> dict[str, Any]:
    return {
        "engine_name": ENGINE_NAME, "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "layers": ["FORET_MFFP", "SOL_IRDA", "ROUTES_MTQ",
                    "ZEC_SEPAQ", "LIMITES", "PRESSION_HUMAINE"],
        "p22n_absorbed": True,
        "active": True, "priority": 0,
    }


@router.post("/summary")
async def gis_summary(body: PointBody) -> dict[str, Any]:
    return gis_layers_summary(body.lat, body.lon, body.halo_m)


@router.post("/foret-mffp")
async def gis_foret(body: PointBody) -> dict[str, Any]:
    return fetch_foret_mffp(body.lat, body.lon, body.halo_m)


@router.post("/sol-irda")
async def gis_sol(body: PointBody) -> dict[str, Any]:
    return fetch_sol_irda(body.lat, body.lon, body.halo_m)


@router.post("/routes-mtq")
async def gis_routes(body: PointBody) -> dict[str, Any]:
    return fetch_routes_mtq(body.lat, body.lon, body.halo_m)


@router.post("/zec-sepaq")
async def gis_zec(body: PointBody) -> dict[str, Any]:
    return fetch_zec_sepaq(body.lat, body.lon, body.halo_m)


@router.post("/limites")
async def gis_limites(body: PointBody) -> dict[str, Any]:
    return fetch_limites(body.lat, body.lon, body.halo_m)


@router.post("/pression-humaine")
async def gis_pression(body: PointBody) -> dict[str, Any]:
    return fetch_pression_humaine(body.lat, body.lon, body.halo_m)


@router.post("/mask-corridors")
async def gis_mask(body: MaskBody) -> dict[str, Any]:
    return compute_corridors_gis(body.corridors, body.lat, body.lon, body.halo_m)
