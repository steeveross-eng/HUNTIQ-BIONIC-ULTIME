"""
HABITAT-FUSION-ENGINE-P0 — Pré-Fusion Habitat BCE4X
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω · COMMANDANT STEEVE-MAX · 2026-05-23 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (engine nouveau, ne touche aucun pipeline existant).

DOCTRINE
--------
Engine de **pré-fusion habitat** Phase P0. Architecture STRUCTURELLE uniquement
en pré-ingestion (les données NDVI HR + LiDAR pan-Canada ne sont pas encore
disponibles). L'engine déclare son contrat d'API et expose le statut de
pré-fusion pour les engines consommateurs (vision IA, corridors, scoring).

FUSION AXES P0 (manifest habitat_fusion_sources_manifest.json)
--------------------------------------------------------------
  - vegetation_ndvi_hr      · poids 0.30 · status PRE_INGESTION
  - topography_lidar        · poids 0.35 · status PRE_INGESTION
  - corridors_behavior      · poids 0.20 · status READY (IA_CORRIDORS_P0_Ω)
  - species_biogeography    · poids 0.15 · status READY (bionic_species_biogeography.json)

API publique
------------
  compute_habitat_score_p0(lat, lon, species, season) -> dict
  get_fusion_status() -> dict
  is_full_fusion_available() -> bool
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger("bionic.habitat_fusion_engine_p0")

ENGINE_NAME = "HABITAT-FUSION-ENGINE-P0"
ENGINE_VERSION = "V1-PRE-FUSION-2026-05"
ENGINE_DOCTRINE = "P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω"

# ─── Imports read-only registries (soft-fail strict) ─────────────────────────
try:
    from engines.v8_institutional import ndvi_lidar_p0_registry_omega as NDVI_LIDAR_P0
except ImportError:
    NDVI_LIDAR_P0 = None  # type: ignore

try:
    from engines.v8_institutional import ia_corridors_registry_omega as IA_CORRIDORS_P0
except ImportError:
    IA_CORRIDORS_P0 = None  # type: ignore


def get_fusion_status() -> Dict[str, Any]:
    """État de pré-fusion habitat · expose statut des 4 axes BCE4X."""
    fusion_manifest = (
        NDVI_LIDAR_P0.get_habitat_fusion_manifest() if NDVI_LIDAR_P0 else {}
    )
    axes = fusion_manifest.get("fusion_axes_p0", {})
    n_ready = sum(1 for a in axes.values() if a.get("status") == "READY")
    n_pre = sum(1 for a in axes.values() if a.get("status") == "PRE_INGESTION")
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "phase": "P0_PRE_FUSION",
        "axes_ready": n_ready,
        "axes_pending": n_pre,
        "axes_total": len(axes),
        "fully_fused": n_pre == 0 and n_ready == len(axes),
        "registries_available": {
            "ndvi_lidar_p0": NDVI_LIDAR_P0 is not None,
            "ia_corridors_p0": IA_CORRIDORS_P0 is not None,
        },
        "axes_detail": {
            name: {"status": data.get("status"), "weight": data.get("fusion_weight")}
            for name, data in axes.items()
        },
    }


def is_full_fusion_available() -> bool:
    status = get_fusion_status()
    return bool(status.get("fully_fused", False))


def compute_habitat_score_p0(
    lat: float, lon: float, species: str, season: str = "automne"
) -> Dict[str, Any]:
    """Calcul de score habitat P0 · combine les axes READY uniquement.

    En P0 (pré-ingestion NDVI HR + LiDAR), seuls 2 axes sur 4 contribuent :
    - corridors_behavior (IA_CORRIDORS_P0_Ω) · poids 0.20
    - species_biogeography (bionic_species_biogeography) · poids 0.15

    Le score est explicitement marqué `partial_p0=True` pour informer les
    consommateurs qu'une re-fusion sera nécessaire post-ingestion P1.
    """
    contributions: Dict[str, Any] = {}
    score_sum = 0.0
    weight_sum = 0.0

    # Axe corridors_behavior (READY)
    if IA_CORRIDORS_P0 is not None:
        behavior = IA_CORRIDORS_P0.get_behavior_profile(species)
        ia = behavior.get("comportement_ia", {})
        # Score subjectif basé sur l'amplitude/sinuosity_factor (réel · 0-1)
        # Normalisation : amplitude 0.4-0.7 → 50-100
        amp = float(ia.get("amplitude", 0.5))
        score_corr = min(100.0, max(0.0, (amp - 0.3) / 0.4 * 100.0))
        weight = 0.20
        contributions["corridors_behavior"] = {
            "score": round(score_corr, 1),
            "weight": weight,
            "status": "READY",
            "source": "IA_CORRIDORS_P0_Ω.behavior_profiles",
        }
        score_sum += score_corr * weight
        weight_sum += weight

    # Axe species_biogeography (READY)
    if IA_CORRIDORS_P0 is not None:
        temp_sig = IA_CORRIDORS_P0.get_temporal_signature(species)
        bio = temp_sig.get("biogeographie", {})
        provinces = bio.get("provinces_ca_actives", [])
        # Score = % provinces où espèce présente (max 13 provinces CA)
        score_bio = min(100.0, (len(provinces) / 13.0) * 100.0)
        weight = 0.15
        contributions["species_biogeography"] = {
            "score": round(score_bio, 1),
            "weight": weight,
            "status": "READY",
            "source": "IA_CORRIDORS_P0_Ω.temporal_signatures.biogeographie",
        }
        score_sum += score_bio * weight
        weight_sum += weight

    # Axes pré-ingestion (NDVI HR + LiDAR) — déclarés mais non scorés
    for pending_axis in ("vegetation_ndvi_hr", "topography_lidar"):
        contributions[pending_axis] = {
            "score": None,
            "weight": 0.30 if pending_axis == "vegetation_ndvi_hr" else 0.35,
            "status": "PRE_INGESTION",
            "source": "NDVI_LIDAR_P0 placeholder · awaiting P1 ingestion",
        }

    partial_score = (score_sum / weight_sum * 100.0 / 100.0) if weight_sum > 0 else None

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "lat": lat, "lon": lon, "species": species, "season": season,
        "habitat_score_partial_p0": round(partial_score, 1) if partial_score is not None else None,
        "partial_p0": True,
        "weight_total_active": round(weight_sum, 2),
        "weight_total_full_target": 1.00,
        "completion_ratio": round(weight_sum, 2),
        "contributions": contributions,
        "_note_doctrinale": "Score partiel P0 · refusion complète post NDVI HR + LiDAR P1",
    }


__all__ = [
    "compute_habitat_score_p0", "get_fusion_status", "is_full_fusion_available",
    "ENGINE_NAME", "ENGINE_VERSION",
]
