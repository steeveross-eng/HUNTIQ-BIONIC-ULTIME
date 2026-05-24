"""
habitat_fusion_p1_router.py — Router institutionnel HABITAT-FUSION_P1_STRUCTURAL+_Ω
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · NE TÉLÉCHARGE RIEN · NE FABRIQUE AUCUNE DONNÉE.

ENDPOINTS
---------
  GET /api/v30/habitat-fusion/p1/status
       → Statut global P1 STRUCTURAL+ · armement clients · weight_active

  GET /api/v30/habitat-fusion/p1/clients
       → Snapshot des 4 clients (NASA HLS · ESA S2 · NRCan HRDEM · MFFP)

  GET /api/v30/habitat-fusion/p1/score?species=X&lat=Y&lon=Z&season=W
       → PROXY vers compute_habitat_score P0 (anti-générique strict)
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger("bionic.habitat_fusion_p1_router")

router = APIRouter(prefix="/api/v30/habitat-fusion/p1", tags=["habitat-fusion-p1"])

try:
    from engines.v8_institutional import habitat_fusion_engine_p1 as HFE_P1
except ImportError as e:
    logger.error(f"[HABITAT_FUSION_P1_ROUTER] engine import failed: {e}")
    HFE_P1 = None  # type: ignore


@router.get("/status")
def status_endpoint() -> Dict[str, Any]:
    if HFE_P1 is None:
        return {
            "served_by": "HABITAT-FUSION-P1-ROUTER",
            "engine_available": False,
            "phase": "ENGINE_UNAVAILABLE",
        }
    return {"served_by": "HABITAT-FUSION-P1-ROUTER", **HFE_P1.get_p1_status()}


@router.get("/clients")
def clients_endpoint() -> Dict[str, Any]:
    if HFE_P1 is None:
        raise HTTPException(status_code=503, detail="habitat_fusion_engine_p1 unavailable")
    return {
        "served_by": "HABITAT-FUSION-P1-ROUTER",
        "clients": HFE_P1.get_ingestion_clients_status(),
        "ingestion_p1_ready": HFE_P1.is_p1_ready_for_ingestion(),
    }


@router.get("/score")
def score_endpoint(
    species: str = Query(..., description="chevreuil | orignal | ours_noir | coyote | dindon_sauvage"),
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    season: str = Query("automne"),
) -> Dict[str, Any]:
    if HFE_P1 is None:
        raise HTTPException(status_code=503, detail="habitat_fusion_engine_p1 unavailable")
    result = HFE_P1.compute_habitat_score(species=species, lat=lat, lng=lon, season=season)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"served_by": "HABITAT-FUSION-P1-ROUTER", **result}
