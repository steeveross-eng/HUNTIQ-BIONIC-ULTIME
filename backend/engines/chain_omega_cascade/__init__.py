"""
CHAINE_Ω_CASCADE · Orchestrateur master institutionnel
══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

CHAÎNE DOCTRINALE EXIGÉE :
  SPECTRAL → TERRAIN_HR → GIS → CORRIDORS → TERRITOIRE

Ce module orchestre la cascade institutionnelle dans l'ordre exact prescrit
par la COMMANDE_INSTITUTIONNELLE_Ω PHASE_1+PHASE_2_Ω.

Chaque étape pondère/enrichit les corridors avec un facteur dédié :
  - factor_spectral  ∈ [0.5, 1.5]  (NDVI/NDWI/LST Sentinel-2)
  - factor_terrain   ∈ [0.5, 1.2]  (slope/roughness OpenTopography)
  - factor_gis       ∈ [0.5, 1.5]  (densité humaine + routes Québec)

Facteur global cascade = factor_spectral × factor_terrain × factor_gis
clipped ∈ [0.3, 2.0] (cap doctrinal anti-explosion).

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW MODULE EXTERNE
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from engines.gis_omega import compute_corridors_gis
from engines.spectral_omega import (
    chain_omega_pondere_corridors as spectral_chain_corridors,
    compute_spectral_at_point,
)
from engines.terrain_hr_omega import (
    chain_omega_terrain_pondere_corridors as terrain_chain_corridors,
    compute_terrain_hr_at_point,
)

logger = logging.getLogger("chain_omega_cascade")

CHAIN_NAME = "CHAINE_Ω_CASCADE"
CHAIN_VERSION = "V1_LOCK-PHASE_1+2-2026-05"
CHAIN_DOCTRINE = "SPECTRAL → TERRAIN_HR → GIS → CORRIDORS → TERRITOIRE"


router = APIRouter(prefix="/api/v20/chain-omega",
                    tags=["CHAINE_Ω_CASCADE"])


class CascadeBody(BaseModel):
    lat: float
    lon: float
    corridors: list[dict[str, Any]] | None = None
    halo_m_spectral: float = 200.0
    halo_m_terrain: float = 200.0
    halo_m_gis: float = 5000.0
    grid_n_terrain: int = 7  # plus rapide pour cascade
    lod_terrain: str = "MED"
    include_landsat_lst: bool = False  # désactivé par défaut (lent)


@router.get("/status")
async def chain_status() -> dict[str, Any]:
    return {
        "chain_name": CHAIN_NAME,
        "version": CHAIN_VERSION,
        "doctrine": CHAIN_DOCTRINE,
        "stages": [
            {"order": 1, "name": "SPECTRAL", "engine": "ENGINE-SPECTRAL-Ω"},
            {"order": 2, "name": "TERRAIN_HR", "engine": "ENGINE-TERRAIN-HR-Ω"},
            {"order": 3, "name": "GIS", "engine": "ENGINE-GIS-Ω"},
            {"order": 4, "name": "CORRIDORS", "engine": "ENGINE-IA-CORRIDORS-ORGANIC-Ω"},
            {"order": 5, "name": "TERRITOIRE", "engine": "ENGINE-FUSION-TERRITOIRE-Ω"},
        ],
        "factor_caps": {"min": 0.3, "max": 2.0},
        "active": True,
    }


@router.post("/cascade")
async def chain_cascade(body: CascadeBody) -> dict[str, Any]:
    """Exécute la cascade complète SPECTRAL → TERRAIN_HR → GIS sur des corridors.

    Si `corridors` n'est pas fourni, retourne uniquement les facteurs de
    pondération par stage (mode probe rapide).
    """
    out: dict[str, Any] = {
        "chain": CHAIN_NAME, "version": CHAIN_VERSION,
        "doctrine": CHAIN_DOCTRINE,
        "lat": body.lat, "lon": body.lon,
        "stages": [],
    }
    corridors = list(body.corridors or [{"id": "_probe_", "intensity_level": 2}])

    # ═══ STAGE 1 — SPECTRAL ═══
    try:
        spectral = compute_spectral_at_point(
            body.lat, body.lon, halo_m=body.halo_m_spectral,
            include_landsat_lst=body.include_landsat_lst,
        )
        corridors_after_s = spectral_chain_corridors(corridors, spectral)
        factor_s = float(corridors_after_s[0].get("_spectral_factor", 1.0)) \
            if corridors_after_s else 1.0
        out["stages"].append({
            "order": 1, "name": "SPECTRAL", "ok": True,
            "factor": factor_s,
            "ndvi_normalized": spectral.get("ndvi_normalized"),
            "ndwi_normalized": spectral.get("ndwi_normalized"),
            "fallback": spectral.get("fallback_applied_global", False),
        })
        corridors = corridors_after_s
    except Exception as e:
        logger.warning("[%s] STAGE 1 SPECTRAL failed: %s", CHAIN_NAME, e)
        out["stages"].append({"order": 1, "name": "SPECTRAL", "ok": False,
                               "error": str(e), "factor": 1.0})

    # ═══ STAGE 2 — TERRAIN_HR ═══
    try:
        terrain = compute_terrain_hr_at_point(
            body.lat, body.lon, halo_m=body.halo_m_terrain,
            grid_n=body.grid_n_terrain, lod=body.lod_terrain,
        )
        corridors_after_t = terrain_chain_corridors(corridors, terrain)
        factor_t = float(corridors_after_t[0].get("_terrain_factor", 1.0)) \
            if corridors_after_t else 1.0
        out["stages"].append({
            "order": 2, "name": "TERRAIN_HR", "ok": True,
            "factor": factor_t,
            "slope_mean_pct": terrain.get("slope_aspect", {}).get("stats", {}).get("slope_mean_pct"),
            "tri_mean": terrain.get("roughness_tri", {}).get("stats", {}).get("tri_mean"),
            "fallback": terrain.get("fallback_applied", False),
        })
        corridors = corridors_after_t
    except Exception as e:
        logger.warning("[%s] STAGE 2 TERRAIN_HR failed: %s", CHAIN_NAME, e)
        out["stages"].append({"order": 2, "name": "TERRAIN_HR", "ok": False,
                               "error": str(e), "factor": 1.0})

    # ═══ STAGE 3 — GIS ═══
    try:
        gis_result = compute_corridors_gis(
            corridors, body.lat, body.lon, halo_m=body.halo_m_gis,
        )
        factor_g = float(gis_result.get("gis_factor", 1.0))
        corridors = gis_result.get("corridors", corridors)
        out["stages"].append({
            "order": 3, "name": "GIS", "ok": True,
            "factor": factor_g,
            "n_layers_loaded": gis_result.get("n_layers_loaded"),
            "n_layers_total": gis_result.get("n_layers_total"),
            "gis_operational_omega": gis_result.get("gis_operational_omega"),
        })
    except Exception as e:
        logger.warning("[%s] STAGE 3 GIS failed: %s", CHAIN_NAME, e)
        out["stages"].append({"order": 3, "name": "GIS", "ok": False,
                               "error": str(e), "factor": 1.0})

    # ═══ FACTEUR GLOBAL CASCADE ═══
    factors = [s.get("factor", 1.0) for s in out["stages"]]
    cascade_factor = 1.0
    for f in factors:
        cascade_factor *= float(f)
    cascade_factor = max(0.3, min(2.0, cascade_factor))  # cap doctrinal

    out["cascade_factor_global"] = cascade_factor
    out["n_corridors"] = len(corridors)
    out["corridors"] = corridors
    return out
