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
  compute_habitat_score_p0(lat, lon, species, season) -> dict        # legacy alias
  compute_habitat_score(species, lat, lng, season) -> dict           # signature directive Commandant
  get_fusion_status() -> dict                                        # legacy alias
  get_axes_status() -> dict                                          # statut détaillé des 4 axes
  get_habitat_fusion_registry() -> dict                              # manifeste maître HABITAT_FUSION_P0_REGISTRY_Ω
  is_full_fusion_available() -> bool
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger("bionic.habitat_fusion_engine_p0")

ENGINE_NAME = "HABITAT-FUSION-ENGINE-P0"
ENGINE_VERSION = "V1-PRE-FUSION-2026-05"
ENGINE_DOCTRINE = "P22ΩΩ_IA_HABITAT_FUSION_P0_Ω"

# ─── Imports read-only registries (soft-fail strict) ─────────────────────────
try:
    from engines.v8_institutional import ndvi_lidar_p0_registry_omega as NDVI_LIDAR_P0
except ImportError:
    NDVI_LIDAR_P0 = None  # type: ignore

try:
    from engines.v8_institutional import ia_corridors_registry_omega as IA_CORRIDORS_P0
except ImportError:
    IA_CORRIDORS_P0 = None  # type: ignore

try:
    from engines.v8_institutional import habitat_fusion_registry_omega as HABITAT_FUSION_P0
except ImportError:
    HABITAT_FUSION_P0 = None  # type: ignore


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
    "compute_habitat_score_p0", "compute_habitat_score",
    "get_fusion_status", "get_axes_status",
    "get_habitat_fusion_registry", "is_full_fusion_available",
    "ENGINE_NAME", "ENGINE_VERSION", "ENGINE_DOCTRINE",
]


# ═════════════════════════════════════════════════════════════════════════════
# P22ΩΩ_IA_HABITAT_FUSION_P0_Ω · 2026-02-20 · Extensions doctrinales
# Additif strict — Verrou Phase III maintenu.
# ═════════════════════════════════════════════════════════════════════════════

# Signatures espèces & saisons doctrinales
_SPECIES_CANONICAL = ("chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage")
_SEASONS_CANONICAL = ("printemps", "ete", "automne", "hiver")


def _normalize_species(species: str) -> str:
    s = (species or "").lower().strip()
    aliases = {
        "cerf": "chevreuil",
        "chevreuil_de_virginie": "chevreuil",
        "white_tailed_deer": "chevreuil",
        "moose": "orignal",
        "black_bear": "ours_noir",
        "ours": "ours_noir",
        "wild_turkey": "dindon_sauvage",
        "dindon": "dindon_sauvage",
        "canis_latrans": "coyote",
    }
    return aliases.get(s, s)


def _normalize_season(season: str) -> str:
    s = (season or "automne").lower().strip()
    aliases = {
        "spring": "printemps", "summer": "ete", "été": "ete",
        "fall": "automne", "autumn": "automne", "winter": "hiver",
    }
    return aliases.get(s, s)


def get_axes_status() -> Dict[str, Any]:
    """État détaillé des 4 axes BCE4X avec flux de poids actifs/dormants.

    Retourne un payload exhaustif :
      - 4 axes (vegetation_ndvi_hr · topography_lidar · corridors_behavior · species_biogeography)
      - Statut · poids · upstream_engine · ingestion_target par axe
      - Synthèse globale (weight_active · completion_ratio · phase)
    """
    # Source primaire : manifeste maître HABITAT_FUSION_P0_REGISTRY_Ω
    if HABITAT_FUSION_P0 is not None:
        master = HABITAT_FUSION_P0.get_master_registry()
        if master:
            axes = master.get("fusion_axes_p0", {})
            weight_ready = sum(
                float(a.get("fusion_weight", 0.0))
                for a in axes.values()
                if a.get("status") == "READY"
            )
            weight_pending = sum(
                float(a.get("fusion_weight", 0.0))
                for a in axes.values()
                if a.get("status") == "PRE_INGESTION"
            )
            return {
                "engine": ENGINE_NAME,
                "version": ENGINE_VERSION,
                "doctrine": ENGINE_DOCTRINE,
                "phase": master.get("_phase", "P0_PRE_FUSION"),
                "status_global": master.get("_status", "STRUCTURAL_ACTIVATED_PRE_INGESTION"),
                "axes_total": master.get("axes_total", len(axes)),
                "axes_ready": master.get("axes_ready", 0),
                "axes_pre_ingestion": master.get("axes_pre_ingestion", 0),
                "weight_active_p0": round(weight_ready, 2),
                "weight_pending_p1": round(weight_pending, 2),
                "weight_target_p2": float(master.get("weight_target_p2", 1.0)),
                "completion_ratio": float(master.get("completion_ratio_p0", weight_ready)),
                "fully_fused": weight_pending == 0.0 and weight_ready > 0.0,
                "registry_master_present": True,
                "axes": {
                    name: {
                        "status": data.get("status"),
                        "fusion_weight": data.get("fusion_weight"),
                        "upstream_engine": data.get("upstream_engine"),
                        "ingestion_target": data.get("ingestion_target"),
                    }
                    for name, data in axes.items()
                },
                "registries_available": {
                    "habitat_fusion_p0_master": True,
                    "ndvi_lidar_p0": NDVI_LIDAR_P0 is not None,
                    "ia_corridors_p0": IA_CORRIDORS_P0 is not None,
                },
            }

    # Fallback : reconstruction depuis NDVI_LIDAR_P0 manifest
    legacy = get_fusion_status()
    legacy["registry_master_present"] = False
    legacy["_note"] = "fallback · manifeste maître absent · re-générer via gen_habitat_fusion_p0_registry_omega.py"
    return legacy


def get_habitat_fusion_registry() -> Dict[str, Any]:
    """Manifeste maître HABITAT_FUSION_P0_REGISTRY_Ω (read-only)."""
    if HABITAT_FUSION_P0 is None:
        return {"_status": "REGISTRY_LOADER_UNAVAILABLE"}
    return HABITAT_FUSION_P0.get_master_registry() or {"_status": "EMPTY"}


def compute_habitat_score(
    species: str, lat: float, lng: float, season: str = "automne"
) -> Dict[str, Any]:
    """Signature directive Commandant : (species, lat, lng, season).

    Computation principale du score habitat P0 · combine les axes READY
    (corridors_behavior + species_biogeography) en P0_PRE_FUSION. Les axes
    NDVI HR + LiDAR sont déclarés mais retournent un score `None` tant que
    l'ingestion P1 n'a pas été effectuée.

    Retourne un payload divergent par espèce × saison (divergence biologique
    stricte respectée via IA_CORRIDORS_P0_Ω + biogéographie).
    """
    sp = _normalize_species(species)
    sn = _normalize_season(season)

    if sp not in _SPECIES_CANONICAL:
        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "doctrine": ENGINE_DOCTRINE,
            "error": f"species_unknown · '{species}' (canonical: {list(_SPECIES_CANONICAL)})",
            "habitat_score": None,
            "partial_p0": True,
        }

    contributions: Dict[str, Any] = {}
    score_sum = 0.0
    weight_sum_active = 0.0
    weight_sum_target = 0.0

    # ─── Axe corridors_behavior (READY) ────────────────────────────────────
    weight_corr = 0.20
    weight_sum_target += weight_corr
    score_corr = None
    if IA_CORRIDORS_P0 is not None:
        behavior = IA_CORRIDORS_P0.get_behavior_profile(sp)
        ia = behavior.get("comportement_ia", {})
        amp = float(ia.get("amplitude", 0.5))
        sinuosity = float(behavior.get("geometrie", {}).get("sinuosity_factor", 1.0))
        # Score = combinaison amplitude IA (0.4-0.7) + facteur sinuosité (1.0-1.8)
        # Normalisé 0-100
        score_amp = min(100.0, max(0.0, (amp - 0.3) / 0.4 * 100.0))
        score_sinu = min(100.0, max(0.0, (sinuosity - 1.0) / 0.8 * 100.0))
        score_corr = round((score_amp * 0.6 + score_sinu * 0.4), 1)
        contributions["corridors_behavior"] = {
            "score_0_100": score_corr,
            "fusion_weight": weight_corr,
            "weighted_score": round(score_corr * weight_corr, 2),
            "status": "READY",
            "source": "IA_CORRIDORS_P0_Ω.behavior_profiles",
            "raw": {"amplitude": amp, "sinuosity_factor": sinuosity},
        }
        score_sum += score_corr * weight_corr
        weight_sum_active += weight_corr
    else:
        contributions["corridors_behavior"] = {
            "score_0_100": None, "fusion_weight": weight_corr,
            "status": "READY_LOADER_MISSING",
        }

    # ─── Axe species_biogeography (READY · saison-aware) ────────────────────
    weight_bio = 0.15
    weight_sum_target += weight_bio
    score_bio = None
    if IA_CORRIDORS_P0 is not None:
        temp_sig = IA_CORRIDORS_P0.get_temporal_signature(sp)
        bio = temp_sig.get("biogeographie", {})
        provinces = bio.get("provinces_ca_actives", [])
        # Score base = % provinces actives (max 13)
        score_provinces = min(100.0, (len(provinces) / 13.0) * 100.0)
        # Modulation saison : indices saisonniers réels du dataset
        season_data = temp_sig.get("saisonnalite", {}).get(sn, {})
        mobilite = float(season_data.get("mobilite_corridor", 0.7))
        couvert = float(season_data.get("preference_couvert", 0.6))
        hydro = float(season_data.get("affinite_hydro", 0.5))
        pic_activite = bool(season_data.get("_pic_activite", False))
        # Indice composite saisonnier ∈ [0.3, 1.5] (0.6·mobilité + 0.25·couvert + 0.15·hydro + bonus pic)
        seasonal_index = (
            0.60 * mobilite + 0.25 * couvert + 0.15 * hydro + (0.20 if pic_activite else 0.0)
        )
        seasonal_index = max(0.3, min(1.5, seasonal_index))
        score_bio = round(score_provinces * seasonal_index, 1)
        score_bio = min(100.0, max(0.0, score_bio))
        contributions["species_biogeography"] = {
            "score_0_100": score_bio,
            "fusion_weight": weight_bio,
            "weighted_score": round(score_bio * weight_bio, 2),
            "status": "READY",
            "source": "IA_CORRIDORS_P0_Ω.temporal_signatures.biogeographie",
            "raw": {
                "provinces_ca_actives_count": len(provinces),
                "season": sn,
                "mobilite_corridor": mobilite,
                "preference_couvert": couvert,
                "affinite_hydro": hydro,
                "pic_activite": pic_activite,
                "seasonal_index": round(seasonal_index, 3),
            },
        }
        score_sum += score_bio * weight_bio
        weight_sum_active += weight_bio
    else:
        contributions["species_biogeography"] = {
            "score_0_100": None, "fusion_weight": weight_bio,
            "status": "READY_LOADER_MISSING",
        }

    # ─── Axes PRE_INGESTION (NDVI HR + LiDAR) ──────────────────────────────
    for axis_name, weight in (
        ("vegetation_ndvi_hr", 0.30),
        ("topography_lidar", 0.35),
    ):
        weight_sum_target += weight
        contributions[axis_name] = {
            "score_0_100": None,
            "fusion_weight": weight,
            "weighted_score": None,
            "status": "PRE_INGESTION",
            "source": "NDVI_LIDAR_P0 placeholder · awaiting P1 ingestion",
        }

    # Score habitat normalisé sur les axes ACTIFS (P0) uniquement
    habitat_score_active = (
        round(score_sum / weight_sum_active, 1)
        if weight_sum_active > 0 else None
    )

    # Score projeté complet (axes manquants assumés à 50/100 neutre — informatif)
    completion_ratio = round(weight_sum_active / weight_sum_target, 2)

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "phase": "P0_PRE_FUSION",
        "lat": lat, "lng": lng,
        "species": sp, "season": sn,
        "habitat_score": habitat_score_active,
        "habitat_score_partial_p0": habitat_score_active,
        "partial_p0": True,
        "weight_active": round(weight_sum_active, 2),
        "weight_target_full": round(weight_sum_target, 2),
        "completion_ratio": completion_ratio,
        "contributions": contributions,
        "biological_divergence_strict": True,
        "_note_doctrinale": (
            "Score actif P0 normalisé sur 2/4 axes READY "
            "(corridors_behavior + species_biogeography). "
            "Re-fusion complète post NDVI HR + LiDAR P1."
        ),
    }

