"""
ENGINE_SPECTRAL_OMEGA · Router FastAPI institutionnel
══════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Endpoints exposés :
  - GET  /api/v20/spectral/status       → identité + version + sources
  - POST /api/v20/spectral/compute      → pipeline complet point unique
  - POST /api/v20/spectral/indices      → NDVI/NDWI/EVI à un point (rapide, sans LST)
  - POST /api/v20/spectral/fusion       → fusion multi-source 0-1
  - POST /api/v20/spectral/chain        → ponderation chaîne_Ω corridors

V30_LOCK INVIOLÉ · FUSION ADD-ONLY
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from . import (
    ENGINE_DOCTRINE,
    ENGINE_NAME,
    ENGINE_VERSION,
    STAC_LANDSAT_PC,
    STAC_LANDSAT_USGS,
    STAC_SENTINEL2,
    chain_omega_hydro_pondere,
    chain_omega_pondere_corridors,
    chain_omega_pressure_humaine_pondere,
    compute_spectral_at_point,
    fetch_landsat_l2_stac,
    fetch_sentinel2_stac,
    fusion_spectral_multisource,
)

router = APIRouter(prefix="/api/v20/spectral",
                    tags=["ENGINE_SPECTRAL_Ω_NEW_ENGINE_1"])


# ═══════════════════════════════════════════════════════════════════
# MODÈLES
# ═══════════════════════════════════════════════════════════════════
class ComputeBody(BaseModel):
    lat: float
    lon: float
    days_window: int = 45
    include_landsat_lst: bool = True
    halo_m: float = 200.0


class IndicesBody(BaseModel):
    lat: float
    lon: float
    days_window: int = 45
    halo_m: float = 200.0


class FusionBody(BaseModel):
    spectral_payload: dict[str, Any]


class ChainBody(BaseModel):
    chain_target: str  # "corridors" | "hydro" | "pressure_humaine"
    spectral_at_anchor: dict[str, Any]
    corridors: list[dict[str, Any]] | None = None
    hydro_score: float | None = None
    pressure_score: float | None = None


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════
@router.get("/status")
async def spectral_status() -> dict[str, Any]:
    """Identité institutionnelle de l'engine spectral."""
    return {
        "engine_name": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "sources": {
            "sentinel2_stac": STAC_SENTINEL2,
            "landsat_pc_stac": STAC_LANDSAT_PC,
            "landsat_usgs_stac": STAC_LANDSAT_USGS,
            "nasa_earthdata": True,
        },
        "indices": ["NDVI", "NDWI", "EVI", "LST"],
        "normalisation": "0_1",
        "cloud_mask": "s2cloudless_via_SCL",
        "fallback_value": 0.5,
        "integration": {
            "corridors": True,
            "terrain_hr": True,
            "hydro": True,
            "pressure_humaine": True,
        },
        "active": True,
        "priority": 0,
    }


@router.post("/compute")
async def spectral_compute(body: ComputeBody) -> dict[str, Any]:
    """Pipeline spectral complet sur un point WGS84.

    Retourne NDVI/NDWI/EVI/LST + métadonnées + fusion multi-source.
    """
    payload = compute_spectral_at_point(
        lat=body.lat, lon=body.lon,
        days_window=body.days_window,
        include_landsat_lst=body.include_landsat_lst,
        halo_m=body.halo_m,
    )
    payload["fused"] = fusion_spectral_multisource(payload)
    return payload


@router.post("/indices")
async def spectral_indices(body: IndicesBody) -> dict[str, Any]:
    """NDVI/NDWI/EVI Sentinel-2 uniquement (sans LST Landsat — ~3× plus rapide)."""
    return compute_spectral_at_point(
        lat=body.lat, lon=body.lon,
        days_window=body.days_window,
        include_landsat_lst=False,
        halo_m=body.halo_m,
    )


@router.post("/fusion")
async def spectral_fusion(body: FusionBody) -> dict[str, Any]:
    """Fusion multi-source institutionnelle (NDVI 40% · NDWI 20% · EVI 30% · LST_inv 10%)."""
    return fusion_spectral_multisource(body.spectral_payload)


@router.post("/chain")
async def spectral_chain(body: ChainBody) -> dict[str, Any]:
    """Hook chaîne_Ω vers corridors / hydro / pressure_humaine."""
    target = body.chain_target.lower()
    if target == "corridors":
        if not body.corridors:
            return {"error": "corridors required for chain_target=corridors", "ok": False}
        result = chain_omega_pondere_corridors(body.corridors, body.spectral_at_anchor)
        return {"chain_target": "corridors", "ok": True,
                "n_corridors": len(result), "corridors": result}
    elif target == "hydro":
        if body.hydro_score is None:
            return {"error": "hydro_score required for chain_target=hydro", "ok": False}
        weighted = chain_omega_hydro_pondere(body.hydro_score, body.spectral_at_anchor)
        return {"chain_target": "hydro", "ok": True,
                "hydro_score_input": body.hydro_score,
                "hydro_score_weighted": weighted}
    elif target == "pressure_humaine":
        if body.pressure_score is None:
            return {"error": "pressure_score required", "ok": False}
        weighted = chain_omega_pressure_humaine_pondere(
            body.pressure_score, body.spectral_at_anchor)
        return {"chain_target": "pressure_humaine", "ok": True,
                "pressure_score_input": body.pressure_score,
                "pressure_score_weighted": weighted}
    return {"error": f"unknown chain_target: {body.chain_target}", "ok": False}


@router.post("/stac/sentinel2")
async def spectral_stac_s2(body: IndicesBody) -> dict[str, Any]:
    """Recherche STAC Sentinel-2 L2A pure (sans téléchargement raster)."""
    items = fetch_sentinel2_stac(body.lat, body.lon, days_window=body.days_window)
    return {"n_items": len(items), "items": items, "stac": STAC_SENTINEL2}


@router.post("/stac/landsat")
async def spectral_stac_ls(body: IndicesBody) -> dict[str, Any]:
    """Recherche STAC Landsat 8/9 L2 pure (sans téléchargement raster)."""
    items = fetch_landsat_l2_stac(body.lat, body.lon, days_window=body.days_window)
    return {"n_items": len(items), "items": items, "stac": STAC_LANDSAT_PC}
