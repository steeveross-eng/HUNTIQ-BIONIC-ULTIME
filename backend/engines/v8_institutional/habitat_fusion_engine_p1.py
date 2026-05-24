"""
HABITAT-FUSION-ENGINE-P1 — Mode STRUCTURAL+ CODE-READY
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · NE TÉLÉCHARGE RIEN · NE FABRIQUE AUCUNE DONNÉE.

DOCTRINE
--------
Engine P1 STRUCTURAL+ : conserve **strictement** la logique de scoring du P0
(2 axes actifs · weight_active=0.35) MAIS expose désormais le statut détaillé
des 4 clients d'ingestion réelle (NASA HLS · ESA Sentinel-2 · NRCan HRDEM ·
MFFP Forêt Ouverte) et l'état d'armement INGESTION_P1_ARMED.

DIFFÉRENCE P0 → P1 STRUCTURAL+
------------------------------
| Item                  | P0                       | P1 STRUCTURAL+              |
|-----------------------|--------------------------|------------------------------|
| Code clients          | absent                   | 4 clients CODE-READY        |
| Libs ingestion        | absentes                 | laspy + earthaccess + sentinelhub installés |
| Statut axes           | PRE_INGESTION            | P1_READY_AWAITING_CREDENTIALS|
| Logique scoring       | 2 axes (0.35)            | INCHANGÉE (2 axes 0.35)     |
| Téléchargements       | N/A                      | INERTES (anti-générique)    |
| compute_habitat_score | identique                | identique                    |

Réveil P1 → P2 (post Commandant) :
  - Fournir credentials NASA EDL_TOKEN + ESA Copernicus
  - Confirmer extension disque (INGESTION_P1_DISK_AUTHORIZED=1)
  - Activer INGESTION_P1_ARMED=1
  - Re-générer registries via `gen_p1_ingestion_registries.py` (futur)
  - Re-fusion habitat 4 axes complète (weight_active 0.35 → 1.00)

API publique
------------
  get_p1_status() -> dict                            (statut clients + armement)
  get_ingestion_clients_status() -> dict             (snapshot des 4 clients)
  is_p1_ready_for_ingestion() -> bool                (credentials + ARM flags)
  compute_habitat_score(species, lat, lng, season)   (PROXY vers P0 · weight 0.35)
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger("bionic.habitat_fusion_engine_p1")

ENGINE_NAME = "HABITAT-FUSION-ENGINE-P1"
ENGINE_VERSION = "V1.0-STRUCTURAL_PLUS-AWAITING-CREDENTIALS"
ENGINE_DOCTRINE = "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"
ENGINE_PHASE = "P1_STRUCTURAL+_AWAITING_INGESTION"

# ─── Imports moteur P0 (proxy strict · weight_active=0.35 PRÉSERVÉ) ─────────
try:
    from engines.v8_institutional import habitat_fusion_engine_p0 as HFE_P0
except ImportError:
    HFE_P0 = None  # type: ignore

# ─── Imports clients ingestion P1 (soft-fail strict) ────────────────────────
try:
    from integrations.ingestion_p1 import nasa_hls_client as NASA_HLS
except ImportError:
    NASA_HLS = None  # type: ignore
try:
    from integrations.ingestion_p1 import esa_sentinel2_client as ESA_S2
except ImportError:
    ESA_S2 = None  # type: ignore
try:
    from integrations.ingestion_p1 import nrcan_hrdem_client as NRCAN
except ImportError:
    NRCAN = None  # type: ignore
try:
    from integrations.ingestion_p1 import mffp_foret_ouverte_client as MFFP
except ImportError:
    MFFP = None  # type: ignore


def get_ingestion_clients_status() -> Dict[str, Any]:
    """Snapshot status des 4 clients d'ingestion réelle."""
    return {
        "nasa_hls": NASA_HLS.get_status() if NASA_HLS else {"status": "MODULE_MISSING"},
        "esa_sentinel2_l2a": ESA_S2.get_status() if ESA_S2 else {"status": "MODULE_MISSING"},
        "nrcan_hrdem": NRCAN.get_status() if NRCAN else {"status": "MODULE_MISSING"},
        "mffp_foret_ouverte": MFFP.get_status() if MFFP else {"status": "MODULE_MISSING"},
    }


def is_p1_ready_for_ingestion() -> bool:
    """True ssi tous les axes critiques sont armables (credentials + ARM)."""
    if any(c is None for c in (NASA_HLS, ESA_S2, NRCAN, MFFP)):
        return False
    return (
        NASA_HLS.is_credential_ready()
        and ESA_S2.is_credential_ready()
        and NRCAN.is_credential_ready()
        and MFFP.is_credential_ready()
        and NASA_HLS.is_armed()
        and ESA_S2.is_armed()
        and NRCAN.is_armed()
        and MFFP.is_armed()
    )


def get_p1_status() -> Dict[str, Any]:
    """Status global P1 STRUCTURAL+."""
    clients = get_ingestion_clients_status()
    n_credential_ready = sum(
        1 for c in clients.values()
        if c.get("credential_ready") is True
    )
    n_armed = sum(
        1 for c in clients.values()
        if c.get("armed_for_ingestion") is True
    )

    # Statut axes en mode P1 STRUCTURAL+
    axes = {
        "vegetation_ndvi_hr": {
            "status": "P1_READY_AWAITING_CREDENTIALS",
            "fusion_weight": 0.30,
            "upstream_clients": ["nasa_hls", "esa_sentinel2_l2a"],
            "active_in_compute": False,  # P0 logic preserved
        },
        "topography_lidar": {
            "status": "P1_READY_AWAITING_CREDENTIALS",
            "fusion_weight": 0.35,
            "upstream_clients": ["nrcan_hrdem", "mffp_foret_ouverte"],
            "active_in_compute": False,
        },
        "corridors_behavior": {
            "status": "READY",
            "fusion_weight": 0.20,
            "upstream_clients": ["ia_corridors_p0"],
            "active_in_compute": True,
        },
        "species_biogeography": {
            "status": "READY",
            "fusion_weight": 0.15,
            "upstream_clients": ["bionic_species_biogeography"],
            "active_in_compute": True,
        },
    }
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "phase": ENGINE_PHASE,
        "p0_engine_available": HFE_P0 is not None,
        "weight_active": 0.35,  # INCHANGÉ vs P0 (anti-générique strict)
        "weight_target_p2_full": 1.00,
        "ingestion_p1_ready": is_p1_ready_for_ingestion(),
        "clients_total": 4,
        "clients_credential_ready": n_credential_ready,
        "clients_armed": n_armed,
        "ingestion_clients": clients,
        "axes": axes,
        "verrou_phase_iii": True,
        "_note_doctrinale": (
            "P1 STRUCTURAL+ · code-ready · aucune ingestion réelle exécutée. "
            "Réveil P2 nécessite : EDL_TOKEN + COPERNICUS_USERNAME/PASSWORD + "
            "INGESTION_P1_ARMED=1 + INGESTION_P1_DISK_AUTHORIZED=1."
        ),
    }


def compute_habitat_score(
    species: str, lat: float, lng: float, season: str = "automne"
) -> Dict[str, Any]:
    """PROXY vers compute_habitat_score P0 (weight_active=0.35 préservé)."""
    if HFE_P0 is None:
        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "doctrine": ENGINE_DOCTRINE,
            "error": "P0 engine unavailable",
            "habitat_score": None,
        }
    result = HFE_P0.compute_habitat_score(species=species, lat=lat, lng=lng, season=season)
    result["engine_proxy"] = ENGINE_NAME
    result["engine_proxy_version"] = ENGINE_VERSION
    result["phase_p1"] = ENGINE_PHASE
    result["ingestion_p1_ready"] = is_p1_ready_for_ingestion()
    return result


__all__ = [
    "ENGINE_NAME", "ENGINE_VERSION", "ENGINE_DOCTRINE", "ENGINE_PHASE",
    "get_p1_status", "get_ingestion_clients_status",
    "is_p1_ready_for_ingestion", "compute_habitat_score",
]
