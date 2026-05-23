"""
habitat_fusion_p0_router.py — Router institutionnel HABITAT-FUSION_P0_Ω
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_IA_HABITAT_FUSION_P0_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (router additif, ne touche aucun pipeline V20/V10).

ENDPOINTS DOCTRINAUX
--------------------
  GET /api/v30/habitat-fusion/p0/status
       → Statut global · phase · axes_total · weight_active

  GET /api/v30/habitat-fusion/p0/axes
       → Détail des 4 axes BCE4X · statut/poids/upstream_engine/ingestion_target

  GET /api/v30/habitat-fusion/p0/score?species=X&lat=Y&lon=Z&season=W
       → Score habitat normalisé · contributions axes · divergence biologique

CONTRAINTES
-----------
  - Aucune modification R2/R6/TERRITOIRE_Ω/MANIFEST CDN/V20.
  - Lecture seule des registries IA_CORRIDORS_P0 + NDVI_LIDAR_P0 + HABITAT_FUSION_P0.
  - Soft-fail strict : retours HTTP 200 même si registries dégradés (status_global le reflète).
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger("bionic.habitat_fusion_p0_router")

router = APIRouter(prefix="/api/v30/habitat-fusion/p0", tags=["habitat-fusion-p0"])

# ─── Imports moteur principal (soft-fail) ────────────────────────────────────
try:
    from engines.v8_institutional import habitat_fusion_engine_p0 as HFE
except ImportError as e:
    logger.error(f"[HABITAT_FUSION_P0_ROUTER] engine import failed: {e}")
    HFE = None  # type: ignore


@router.get("/status")
def status_endpoint() -> Dict[str, Any]:
    """Statut synthétique global · phase + ratios."""
    if HFE is None:
        return {
            "served_by": "HABITAT-FUSION-P0-ROUTER",
            "engine_available": False,
            "phase": "ENGINE_UNAVAILABLE",
            "_error": "habitat_fusion_engine_p0 import failed",
        }
    axes_status = HFE.get_axes_status()
    return {
        "served_by": "HABITAT-FUSION-P0-ROUTER",
        "engine": axes_status.get("engine"),
        "version": axes_status.get("version"),
        "doctrine": axes_status.get("doctrine"),
        "phase": axes_status.get("phase"),
        "status_global": axes_status.get("status_global"),
        "axes_total": axes_status.get("axes_total"),
        "axes_ready": axes_status.get("axes_ready"),
        "axes_pre_ingestion": axes_status.get("axes_pre_ingestion"),
        "weight_active_p0": axes_status.get("weight_active_p0"),
        "weight_pending_p1": axes_status.get("weight_pending_p1"),
        "weight_target_p2": axes_status.get("weight_target_p2"),
        "completion_ratio": axes_status.get("completion_ratio"),
        "fully_fused": axes_status.get("fully_fused"),
        "registries_available": axes_status.get("registries_available"),
        "registry_master_present": axes_status.get("registry_master_present"),
    }


@router.get("/axes")
def axes_endpoint() -> Dict[str, Any]:
    """Détail complet des 4 axes BCE4X."""
    if HFE is None:
        raise HTTPException(status_code=503, detail="habitat_fusion_engine_p0 unavailable")
    axes_status = HFE.get_axes_status()
    registry = HFE.get_habitat_fusion_registry()
    return {
        "served_by": "HABITAT-FUSION-P0-ROUTER",
        "engine": axes_status.get("engine"),
        "doctrine": axes_status.get("doctrine"),
        "phase": axes_status.get("phase"),
        "axes": axes_status.get("axes", {}),
        "axes_ready": axes_status.get("axes_ready"),
        "axes_pre_ingestion": axes_status.get("axes_pre_ingestion"),
        "weight_active_p0": axes_status.get("weight_active_p0"),
        "weight_pending_p1": axes_status.get("weight_pending_p1"),
        "ingestion_plan": registry.get("ingestion_plan", {}),
        "consumers_registered": registry.get("consumers_registered", []),
        "constraints_verrou_phase_iii": registry.get("constraints_verrou_phase_iii", {}),
    }


@router.get("/score")
def score_endpoint(
    species: str = Query(..., description="chevreuil | orignal | ours_noir | coyote | dindon_sauvage"),
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    season: str = Query("automne", description="printemps | ete | automne | hiver"),
) -> Dict[str, Any]:
    """Score habitat P0 normalisé · divergence biologique stricte."""
    if HFE is None:
        raise HTTPException(status_code=503, detail="habitat_fusion_engine_p0 unavailable")
    result = HFE.compute_habitat_score(species=species, lat=lat, lng=lon, season=season)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {
        "served_by": "HABITAT-FUSION-P0-ROUTER",
        **result,
    }


@router.get("/registry")
def registry_endpoint() -> Dict[str, Any]:
    """Manifeste maître HABITAT_FUSION_P0_REGISTRY_Ω complet (read-only)."""
    if HFE is None:
        raise HTTPException(status_code=503, detail="habitat_fusion_engine_p0 unavailable")
    return {
        "served_by": "HABITAT-FUSION-P0-ROUTER",
        "registry": HFE.get_habitat_fusion_registry(),
    }
