"""
ENGINE-TERRAIN-V10-SUPRA — Mode HR-READY (NDVI HR + LIDAR Pan-Canada)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω · COMMANDANT STEEVE-MAX · 2026-05-23 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (additif strict, n'altère pas V10 existant).

DOCTRINE
--------
Wrapper HR-READY pour engine V10 existant. Active la **détection** des datasets
HR ingérés (NDVI HR, LiDAR pan-Canada) via le registry `NDVI_LIDAR_P0_REGISTRY_Ω`
et bascule entre :
  - Mode `STANDARD_V10`  : utilise terrain V10 classique (cache standard)
  - Mode `HR_READY`      : datasets HR détectés mais en pré-ingestion (placeholder)
  - Mode `HR_INGESTED`   : datasets HR opérationnels (post P1)

ANTI-GÉNÉRIQUE STRICT : ce module ne fabrique aucune donnée. Il indique
uniquement l'état du pipeline HR aux engines consommateurs.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("bionic.engine_terrain_v10_supra")

ENGINE_NAME = "ENGINE-TERRAIN-V10-SUPRA"
ENGINE_VERSION = "V11-HR-READY-2026-05"
ENGINE_DOCTRINE = "P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω"

# ─── Import registry HR (read-only, soft-fail) ───────────────────────────────
try:
    from engines.v8_institutional import ndvi_lidar_p0_registry_omega as NDVI_LIDAR_P0
except ImportError:
    NDVI_LIDAR_P0 = None  # type: ignore


def get_hr_mode() -> str:
    """Détermine le mode opérationnel actuel du pipeline HR.

    Returns
    -------
    "HR_INGESTED" si datasets réels présents,
    "HR_READY" si placeholders structurels présents,
    "STANDARD_V10" si registry absent.
    """
    if NDVI_LIDAR_P0 is None:
        return "STANDARD_V10"
    status = NDVI_LIDAR_P0.get_status()
    if status == "STRUCTURAL_ACTIVATED_PRE_INGESTION":
        return "HR_READY"
    if status == "HR_INGESTED":
        return "HR_INGESTED"
    return "STANDARD_V10"


def get_terrain_v10_supra(terrain_v10: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """API publique · enrichit le payload terrain_v10 avec mode HR-ready.

    Le terrain V10 existant n'est PAS modifié. On ajoute uniquement un sous-bloc
    `_hr_pipeline_status` décrivant l'état du pipeline NDVI+LIDAR.
    """
    base = dict(terrain_v10 or {})
    mode = get_hr_mode()
    base["_hr_pipeline_status"] = {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "mode": mode,
        "registry_available": NDVI_LIDAR_P0 is not None,
        "ndvi_hr_ready": (
            NDVI_LIDAR_P0 is not None and NDVI_LIDAR_P0.has_ndvi_hr()
        ),
        "lidar_pancanada_ready": (
            NDVI_LIDAR_P0 is not None and NDVI_LIDAR_P0.has_lidar_pancanada()
        ),
    }
    return base


__all__ = ["get_hr_mode", "get_terrain_v10_supra", "ENGINE_NAME", "ENGINE_VERSION"]
