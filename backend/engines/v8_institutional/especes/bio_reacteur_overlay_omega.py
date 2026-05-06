"""
bio_reacteur_overlay_omega.py — ORDRE N°53-BIS
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

ENRICHISSEMENT BIO_REACTEUR_Ω en mode FUSION ADD-ONLY uniquement via les
sources RÉELLEMENT PRÉSENTES (BP135 · rasters R9). Aucune fabrication.

INFRASTRUCTURE D'INGESTION pluggable pour les 6 sources externes :
  · NOAA           (.nc/.grib2)        → ENVIRONNEMENT
  · NASA           (.tif/.hdf)         → NUTRITION + ENVIRONNEMENT
  · USGS           (.tif/.csv)         → COMPORTEMENT + PREDICTIF
  · RSF/SSF        (.pkl/.json)        → PREDICTIF
  · MaxEnt         (.jar/.asc/.tif)    → PREDICTIF
  · Forecast 48h   (stream)            → ENVIRONNEMENT

Tant que les sources externes sont absentes du disque, leur status reste
`paths_absent` honnête (skip_with_log). L'overlay BIO_REACTEUR n'utilise
QUE les sources réellement présentes (anti-générique strict).

Doctrine FUSION ADD-ONLY :
  · NE MODIFIE PAS les fichiers BIO_REACTEUR_Ω_<ESPECE>.json (V30 LOCKED)
  · NE MODIFIE PAS bio_profile_135.json (V30 LOCKED)
  · NE MODIFIE PAS super_engines_omega_logic.py (V30 LOCKED)
  · L'overlay est appliqué EN MÉMOIRE puis transmis aux super engines.

═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import copy
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("bio_reacteur_overlay_omega")

from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
    load_bio_profile_135,
    file_sha256 as bp135_sha256,
    index_entries,
    ESPECES_135,
)
from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
    ESPECES_SUPPORTEES,
    load_all_bio_reacteurs,
)


# ═════════════════════════════════════════════════════════════════════════
# 1. Registry des 6 sources externes (état + paths configurés)
#    ORDRE N°53-BIS-SUITE : sous-paths doctrinaux précis du Commandant.
# ═════════════════════════════════════════════════════════════════════════
ESPECES_FOR_MODELS = ["chevreuil", "orignal", "ours_noir",
                      "dindon_sauvage", "wapiti"]


def _per_species_paths(base: str) -> List[Path]:
    """Produit la liste des paths {base}/<espece>/ pour les 5 espèces."""
    return [Path(base) / esp for esp in ESPECES_FOR_MODELS]


EXTERNAL_SOURCES_REGISTRY: List[Dict[str, Any]] = [
    {
        "source_name": "NOAA",
        "paths": [Path("/data/external/noaa")],
        "expected_subpath_glob": "2025/*",
        "formats": [".nc", ".grib2"],
        "hooks_targets": ["ENVIRONNEMENT"],
        "consumed_by_masters": ["SENSORIEL_MASTER_Ω"],
        "official_https_sources": [
            "https://www.noaa.gov",
            "https://www.ncei.noaa.gov",
            "https://psl.noaa.gov",
            "https://www.ncdc.noaa.gov/data-access/model-data/"
            "model-datasets",
        ],
    },
    {
        "source_name": "NASA",
        "paths": [Path("/data/external/nasa")],
        "expected_subpath_glob": "ndvi/*",
        "formats": [".tif", ".hdf"],
        "hooks_targets": ["NUTRITION", "ENVIRONNEMENT"],
        "consumed_by_masters": [
            "NUTRITION_MASTER_Ω", "SENSORIEL_MASTER_Ω"],
        "official_https_sources": [
            "https://earthdata.nasa.gov",
            "https://lpdaac.usgs.gov",
            "https://modis.gsfc.nasa.gov",
            "https://search.earthdata.nasa.gov",
        ],
    },
    {
        "source_name": "USGS",
        "paths": [Path("/data/external/usgs")],
        "expected_subpath_glob": "soil/*",
        "formats": [".tif", ".csv"],
        "hooks_targets": ["COMPORTEMENT", "PREDICTIF"],
        "consumed_by_masters": [
            "COMPORTEMENT_MASTER_Ω", "GOUVERNANCE_MASTER_Ω"],
        "official_https_sources": [
            "https://www.usgs.gov",
            "https://www.sciencebase.gov",
            "https://prd-tnm.s3.amazonaws.com/index.html",
            "https://mrdata.usgs.gov",
        ],
    },
    {
        "source_name": "RSF_SSF",
        "paths": (
            _per_species_paths("/models/rsf")
            + _per_species_paths("/models/ssf")),
        "expected_subpath_glob": "*",
        "formats": [".pkl", ".rds", ".json"],
        "hooks_targets": ["PREDICTIF"],
        "consumed_by_masters": ["GOUVERNANCE_MASTER_Ω"],
        "per_species_aware": True,
        "official_https_sources": [
            "https://movementecologyjournal.biomedcentral.com",
            "https://www.usgs.gov",
        ],
    },
    {
        "source_name": "MAXENT",
        "paths": _per_species_paths("/models/maxent"),
        "expected_subpath_glob": "*",
        "formats": [".jar", ".asc", ".tif"],
        "hooks_targets": ["PREDICTIF"],
        "consumed_by_masters": ["GOUVERNANCE_MASTER_Ω"],
        "per_species_aware": True,
        "official_https_sources": [
            "https://biodiversityinformatics.amnh.org/open_source/maxent",
            "https://github.com/mrmaxent/maxent",
        ],
    },
    {
        "source_name": "FORECAST_48H",
        "paths": [Path("/streams/forecast48h")],
        "expected_subpath_glob": "*",
        "formats": [".nc", ".json", ".csv"],
        "hooks_targets": ["ENVIRONNEMENT"],
        "consumed_by_masters": ["SENSORIEL_MASTER_Ω"],
        "official_https_sources": [
            "https://www.weather.gov",
            "https://api.weather.gov",
            "https://www.nws.noaa.gov",
        ],
    },
]


def _detect_file_anomalies(path: Path,
                           expected_formats: List[str]) -> List[str]:
    """Détecte les anomalies doctrinales d'un fichier source externe.

    Anomalies retournées :
      · `zero_size`         : fichier vide
      · `format_unexpected` : extension hors formats attendus
      · `unreadable`        : I/O error
    """
    anomalies: List[str] = []
    try:
        st = path.stat()
        if st.st_size == 0:
            anomalies.append("zero_size")
    except OSError:
        anomalies.append("unreadable")
    if path.suffix not in expected_formats:
        anomalies.append("format_unexpected")
    return anomalies


def scan_external_sources() -> Dict[str, Any]:
    """Scanne les 6 sources externes configurées · état réel disque.

    ORDRE N°53-BIS-SUITE :
      · Détection d'anomalies par fichier (zero_size, format_unexpected,
        unreadable).
      · `available=True` ssi ≥1 fichier valide (sans anomalie).
      · Anomalies → `available=False` + log dans `anomalies_detected`.
      · Anti-générique strict : aucune fabrication.
    """
    results: List[Dict[str, Any]] = []
    for src in EXTERNAL_SOURCES_REGISTRY:
        paths_present: List[str] = []
        paths_absent: List[str] = []
        files_valid: List[str] = []
        files_anomalies: List[Dict[str, Any]] = []
        for p in src["paths"]:
            if p.exists() and p.is_dir():
                paths_present.append(str(p))
                for fmt in src["formats"]:
                    for f in p.rglob(f"*{fmt}"):
                        if not f.is_file():
                            continue
                        anomalies = _detect_file_anomalies(
                            f, src["formats"])
                        if anomalies:
                            files_anomalies.append({
                                "path": str(f),
                                "anomalies": anomalies,
                            })
                        else:
                            files_valid.append(str(f))
            else:
                paths_absent.append(str(p))
        available = len(files_valid) > 0 and len(files_anomalies) == 0
        results.append({
            "source_name": src["source_name"],
            "paths_present": paths_present,
            "paths_absent": paths_absent,
            "expected_subpath_glob": src.get("expected_subpath_glob", "*"),
            "per_species_aware": src.get("per_species_aware", False),
            "n_files_valid": len(files_valid),
            "n_files_anomalies": len(files_anomalies),
            "files_sample_valid": files_valid[:5],
            "anomalies_detected": files_anomalies[:10],
            "formats_expected": src["formats"],
            "hooks_targets": src["hooks_targets"],
            "consumed_by_masters": src["consumed_by_masters"],
            "official_https_sources": src.get(
                "official_https_sources", []),
            "available": available,
            "fallback_when_unavailable": "skip_with_log",
            "anti_generique_strict": True,
        })
    n_available = sum(1 for r in results if r["available"])
    n_anomalies_total = sum(
        r["n_files_anomalies"] for r in results)
    return {
        "manifest_id": "EXTERNAL_SOURCES_SCAN_Ω",
        "ordre": "N°53-BIS-SUITE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "scanned_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
        "n_sources_total": len(results),
        "n_sources_available": n_available,
        "n_sources_absent": len(results) - n_available,
        "n_anomalies_total": n_anomalies_total,
        "sources": results,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 2. Mapping conservatif BP135 → BIO_REACTEUR (NUTRITION uniquement)
#    Anti-générique strict : seulement les paramètres à correspondance
#    scientifique directe + numériquement exploitable.
# ═════════════════════════════════════════════════════════════════════════
BP135_TO_BR_NUTRITION_MAPPING = {
    # nutrition.besoins_proteines ← ALI besoin protéines
    "nutrition.besoins_proteines": {
        "bp135_param_id": "ALI-003",
        "bp135_param_name": "besoin_proteine_brute",
        "br_target_engine": "ENGINE_NUTRITION",
        "rationale": "Besoin protéique brut quotidien (% matière sèche).",
    },
    # nutrition.besoins_energetiques ← ALI énergie de base été
    "nutrition.besoins_energetiques": {
        "bp135_param_id": "ALI-011",
        "bp135_param_name": "besoin_energetique_basal_ete",
        "br_target_engine": "ENGINE_NUTRITION",
        "rationale": "Besoin énergétique basal estival (kcal/jour).",
    },
    # nutrition.besoins_mineraux.sodium ← ALI sodium
    "nutrition.besoins_mineraux.sodium": {
        "bp135_param_id": "ALI-008",
        "bp135_param_name": "besoin_sodium",
        "br_target_engine": "ENGINE_MINERAUX",
        "rationale": "Besoin sodium quotidien (mg/jour).",
    },
    # nutrition.besoins_mineraux.calcium ← ALI calcium
    "nutrition.besoins_mineraux.calcium": {
        "bp135_param_id": "ALI-009",
        "bp135_param_name": "besoin_calcium",
        "br_target_engine": "ENGINE_MINERAUX",
        "rationale": "Besoin calcium quotidien (mg/jour).",
    },
    # nutrition.besoins_mineraux.magnesium ← (aucun match BP135 direct)
    # → reste vide (anti-générique strict, pas de fabrication)
}


def _get_bp135_value_for_species(
    bp135_idx: Dict[str, Any],
    block: str,
    espece_bp135: str,
    parameter_id: str,
) -> Optional[float]:
    """Cherche value_typical (numérique) d'un paramètre BP135 pour une espèce.

    Returns None si non trouvé ou non numérique.
    Anti-générique : aucune valeur fabriquée.
    """
    entries = bp135_idx["by_block_species"].get(
        block, {}).get(espece_bp135, [])
    for e in entries:
        if e.get("parameter_id") == parameter_id:
            v = e.get("value_typical")
            if isinstance(v, (int, float)):
                return float(v)
            return None
    return None


def compute_overlay_for_species(espece_br: str) -> Dict[str, Any]:
    """Calcule l'overlay BIO_REACTEUR pour une espèce, basé sur BP135.

    Args:
      espece_br: identifiant BR (ESPECES_SUPPORTEES) — coincide avec ESPECES_135.

    Returns:
      overlay dict {
        "patches": [{dotted_path, target_engine, source, value, bp135_param}],
        "skipped_anti_generique": [...],
        "summary": {...}
      }
    """
    if espece_br not in ESPECES_SUPPORTEES:
        raise ValueError(f"espece_br invalide : {espece_br}")

    bp = load_bio_profile_135()  # noqa: F841 (sanity load + lru_cache warmup)
    idx = index_entries()

    patches: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    # NUTRITION mapping (espèce identique côté BR/BP135)
    espece_bp = espece_br
    for dotted, mapping in BP135_TO_BR_NUTRITION_MAPPING.items():
        # Recherche dans tous les blocs ALIMENTATION/PHYSIOLOGIE
        value = None
        bp_param_block = None
        for blk in ("ALIMENTATION", "PHYSIOLOGIE"):
            v = _get_bp135_value_for_species(
                idx, blk, espece_bp, mapping["bp135_param_id"])
            if v is not None:
                value = v
                bp_param_block = blk
                break

        if value is None:
            skipped.append({
                "dotted_path": dotted,
                "reason": "bp135_value_absent_or_non_numeric",
                "bp135_param_id": mapping["bp135_param_id"],
                "anti_generique_strict": True,
            })
            continue

        patches.append({
            "dotted_path": dotted,
            "target_engine": mapping["br_target_engine"],
            "source": "BP135",
            "bp135_param_id": mapping["bp135_param_id"],
            "bp135_param_name": mapping["bp135_param_name"],
            "bp135_block": bp_param_block,
            "value": value,
            "rationale": mapping["rationale"],
        })

    return {
        "manifest_id": "BIO_REACTEUR_OVERLAY_Ω",
        "ordre": "N°53-BIS",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "espece": espece_br,
        "patches": patches,
        "skipped_anti_generique": skipped,
        "summary": {
            "n_patches_applied": len(patches),
            "n_skipped_anti_generique": len(skipped),
            "patches_per_target_engine": {
                eng: sum(1 for p in patches
                         if p["target_engine"] == eng)
                for eng in {p["target_engine"] for p in patches}
            },
        },
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 3. Application overlay sur BIO_REACTEUR (mémoire uniquement)
# ═════════════════════════════════════════════════════════════════════════
def merge_overlay(br_dict: Dict[str, Any],
                  overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Applique un overlay sur BR (deepcopy en mémoire, FUSION ADD-ONLY).

    Règle stricte : un patch n'est appliqué que si le path BR est :
      · ABSENT, ou
      · présent mais value est `None`, `[]`, `{}` ou `""`.
    Une valeur BR existante non vide est PRÉSERVÉE (FUSION ADD-ONLY strict).
    """
    enriched = copy.deepcopy(br_dict)
    out_engines = enriched.setdefault("bio_reacteur_outputs", {})
    n_applied = 0
    n_preserved = 0
    application_log: List[Dict[str, Any]] = []

    for patch in overlay.get("patches", []):
        engine = patch["target_engine"]
        dotted = patch["dotted_path"]
        new_value = patch["value"]

        eng_block = out_engines.setdefault(engine, {})
        params = eng_block.setdefault("parametres_alimentes", {})

        existing = params.get(dotted)
        existing_value = None
        if isinstance(existing, dict) and "value" in existing:
            existing_value = existing["value"]
        else:
            existing_value = existing

        is_empty = (
            existing is None
            or existing_value is None
            or existing_value == []
            or existing_value == {}
            or existing_value == "")

        if is_empty:
            # Application FUSION ADD-ONLY
            params[dotted] = {
                "value": new_value,
                "signature": {
                    "source": "BP135_OVERLAY",
                    "bp135_param_id": patch.get("bp135_param_id"),
                    "bp135_block": patch.get("bp135_block"),
                    "applied_via_overlay": True,
                    "ordre": "N°53-BIS",
                },
            }
            n_applied += 1
            application_log.append({
                "dotted_path": dotted,
                "action": "applied",
                "value": new_value,
            })
        else:
            n_preserved += 1
            application_log.append({
                "dotted_path": dotted,
                "action": "preserved_existing",
                "existing_value_type": type(existing_value).__name__,
            })

    return {
        "enriched_br": enriched,
        "n_applied": n_applied,
        "n_preserved_existing": n_preserved,
        "application_log": application_log,
    }


# ═════════════════════════════════════════════════════════════════════════
# 4. Calcul SUPER ENGINES avec overlay
# ═════════════════════════════════════════════════════════════════════════
def compute_super_engines_with_overlay() -> Dict[str, Any]:
    """Calcule les 6 SUPER ENGINES_Ω en utilisant les BR + overlay BP135.

    Aucune mutation disque : overlay appliqué en mémoire uniquement.
    Pipeline : BR original → overlay BP135 → super_engines_omega_logic.
    """
    from engines.v8_institutional.especes.super_engines_omega_logic import (
        compute_corridors_master, compute_nutrition_master,
        compute_sensoriel_master, compute_comportement_master,
        compute_gouvernance_master, compute_territoire_master,
    )
    from engines.v8_institutional.especes.super_engines_omega_specs import (
        SUPER_ENGINE_LOCK_SHA256,
    )

    t0 = time.time()
    bio_reacteurs_original = load_all_bio_reacteurs()
    bio_reacteurs_enriched: Dict[str, Dict[str, Any]] = {}
    overlays_per_species: Dict[str, Dict[str, Any]] = {}
    application_summary: Dict[str, Dict[str, Any]] = {}

    for esp in ESPECES_SUPPORTEES:
        ovl = compute_overlay_for_species(esp)
        merged = merge_overlay(bio_reacteurs_original[esp], ovl)
        bio_reacteurs_enriched[esp] = merged["enriched_br"]
        overlays_per_species[esp] = ovl
        application_summary[esp] = {
            "n_applied": merged["n_applied"],
            "n_preserved_existing": merged["n_preserved_existing"],
        }

    # Recalcul des 6 super engines avec BR enrichis
    out_corridors = compute_corridors_master(bio_reacteurs_enriched)
    out_nutrition = compute_nutrition_master(bio_reacteurs_enriched)
    out_sensoriel = compute_sensoriel_master(bio_reacteurs_enriched)
    out_comportement = compute_comportement_master(bio_reacteurs_enriched)
    out_gouvernance = compute_gouvernance_master(bio_reacteurs_enriched)
    out_territoire = compute_territoire_master(bio_reacteurs_enriched)

    return {
        "manifest_id": "SUPER_ENGINES_WITH_BP135_OVERLAY_Ω",
        "ordre": "N°53-BIS",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "computed_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
        "super_engine_lock_sha256": SUPER_ENGINE_LOCK_SHA256,
        "bp135_sha256": bp135_sha256(),
        "engines": {
            "ENGINE_CORRIDORS_MASTER_Ω": out_corridors,
            "ENGINE_NUTRITION_MASTER_Ω": out_nutrition,
            "ENGINE_SENSORIEL_MASTER_Ω": out_sensoriel,
            "ENGINE_COMPORTEMENT_MASTER_Ω": out_comportement,
            "ENGINE_GOUVERNANCE_MASTER_Ω": out_gouvernance,
            "ENGINE_TERRITOIRE_MASTER_Ω": out_territoire,
        },
        "overlay_application_summary_per_species": application_summary,
        "n_species_enriched": len(ESPECES_SUPPORTEES),
        "elapsed_s": round(time.time() - t0, 3),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 5. Recouplage BP135 ↔ SUPER_ENGINES avec overlay (fusion ADD-ONLY)
# ═════════════════════════════════════════════════════════════════════════
def compute_overlay_fusion(
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Recouplage BP135 ↔ SUPER_ENGINES après application de l'overlay BR.

    Args:
      weights: {"bio_reacteur_overlay": 0..1, "bp135": 0..1}, somme = 1.0.

    Returns:
      Score fusion par master + drift POST-overlay vs PRÉ-overlay.
    """
    from engines.v8_institutional.especes.super_engines_bp135_coupling_omega import (  # noqa: E501
        compute_super_engines_bp135_fusion,
        compute_all_masters_direct_bp135,
        MASTER_LONG_TO_SHORT,
    )

    if weights is None:
        weights = {"bio_reacteur_overlay": 0.5, "bp135": 0.5}
    w_br = float(weights.get("bio_reacteur_overlay", 0.5))
    w_bp = float(weights.get("bp135", 0.5))
    total = w_br + w_bp
    if total <= 0:
        raise ValueError(f"weights_sum_invalid::{total}")
    w_br /= total
    w_bp /= total

    t0 = time.time()
    # Snapshot PRÉ-overlay (référence baseline)
    pre_overlay = compute_super_engines_bp135_fusion(
        weights={"bio_reacteur": 0.5, "bp135": 0.5})
    # POST-overlay : BR enrichis
    post_engines = compute_super_engines_with_overlay()
    bp_bundle = compute_all_masters_direct_bp135()

    # Fusion par master avec overlay BR
    fusion_results: Dict[str, Any] = {}
    for long_id, br_engine in post_engines["engines"].items():
        short_id = MASTER_LONG_TO_SHORT.get(long_id)
        # Score canonique BR : score_<engine>_master_omega
        br_score_key = next(
            (k for k in br_engine
             if k.startswith("score_") and k.endswith("_master_omega")),
            None)
        br_score = (
            br_engine.get(br_score_key, 0.0) if br_score_key else 0.0)

        if short_id and short_id in bp_bundle["masters_results"]:
            bp_engine = bp_bundle["masters_results"][short_id]
            bp_score = bp_engine["score_master_bp135_direct"]
            fusion_score = round(w_br * br_score + w_bp * bp_score, 2)
            drift_post = round(abs(br_score - bp_score), 2)
        else:
            bp_score = None
            fusion_score = br_score
            drift_post = None

        # Calcul du PRE drift pour mesurer l'amélioration
        pre_v = pre_overlay["fusion_results"].get(long_id, {})
        drift_pre = pre_v.get("drift_br_vs_bp135")
        drift_improvement = (
            round(drift_pre - drift_post, 2)
            if drift_pre is not None and drift_post is not None
            else None)

        fusion_results[long_id] = {
            "master_id_long": long_id,
            "master_id_short": short_id,
            "br_score_post_overlay": br_score,
            "br_score_pre_overlay": pre_v.get("bio_reacteur_score"),
            "bp135_direct_score": bp_score,
            "fusion_score_post_overlay": fusion_score,
            "fusion_score_pre_overlay": pre_v.get("fusion_score"),
            "drift_br_vs_bp135_post": drift_post,
            "drift_br_vs_bp135_pre": drift_pre,
            "drift_improvement": drift_improvement,
            "drift_alert_post": (
                drift_post is not None and drift_post > 30.0),
            "weights_applied": {
                "bio_reacteur_overlay": round(w_br, 3),
                "bp135": round(w_bp, 3),
            },
            "couplage_actif": (short_id is not None),
        }

    score_global_fusion = round(
        sum(v["fusion_score_post_overlay"]
            for v in fusion_results.values())
        / len(fusion_results), 2)

    drifts_post = [
        v["drift_br_vs_bp135_post"]
        for v in fusion_results.values()
        if v.get("drift_br_vs_bp135_post") is not None
    ]
    drifts_pre = [
        v["drift_br_vs_bp135_pre"]
        for v in fusion_results.values()
        if v.get("drift_br_vs_bp135_pre") is not None
    ]
    drift_max_post = max(drifts_post) if drifts_post else 0.0
    drift_mean_post = (
        round(sum(drifts_post) / len(drifts_post), 2)
        if drifts_post else 0.0)
    drift_max_pre = max(drifts_pre) if drifts_pre else 0.0
    drift_mean_pre = (
        round(sum(drifts_pre) / len(drifts_pre), 2)
        if drifts_pre else 0.0)

    return {
        "manifest_id": "BP135_OVERLAY_FUSION_Ω",
        "ordre": "N°53-BIS",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "mode": "overlay_fusion",
        "weights_doctrinal": {
            "bio_reacteur_overlay": round(w_br, 3),
            "bp135": round(w_bp, 3),
        },
        "score_global_fusion_post_overlay": score_global_fusion,
        "score_global_fusion_pre_overlay": (
            pre_overlay["score_global_fusion"]),
        "drift_max_post_overlay": drift_max_post,
        "drift_mean_post_overlay": drift_mean_post,
        "drift_max_pre_overlay": drift_max_pre,
        "drift_mean_pre_overlay": drift_mean_pre,
        "drift_improvement_max": round(
            drift_max_pre - drift_max_post, 2),
        "drift_improvement_mean": round(
            drift_mean_pre - drift_mean_post, 2),
        "fusion_results": fusion_results,
        "overlay_application_summary": (
            post_engines["overlay_application_summary_per_species"]),
        "elapsed_s": round(time.time() - t0, 3),
        "computed_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 6. Persistance audit forensique
# ═════════════════════════════════════════════════════════════════════════
AUDITS_ROOT = Path("/app/backend/data/audits_bp135")


def persist_audit(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persiste un audit dans /app/backend/data/audits_bp135/.

    Filename: audit_<timestamp>_<sha8>.json
    SHA-256 du payload calculé pour traçabilité longitudinale.
    """
    AUDITS_ROOT.mkdir(parents=True, exist_ok=True)
    payload_json = json.dumps(payload, sort_keys=True,
                              ensure_ascii=False, default=str)
    audit_sha256 = hashlib.sha256(
        payload_json.encode("utf-8")).hexdigest()
    sha8 = audit_sha256[:8]
    ts = datetime.now(
        timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"audit_{ts}_{sha8}.json"
    out_path = AUDITS_ROOT / filename
    persisted_payload = {
        "audit_filename": filename,
        "audit_sha256": audit_sha256,
        "persisted_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
        "ordre": "N°53-BIS",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "audit_payload": payload,
    }
    out_path.write_text(
        json.dumps(persisted_payload, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return {
        "audit_filename": filename,
        "audit_path": str(out_path),
        "audit_sha256": audit_sha256,
        "audit_size_bytes": out_path.stat().st_size,
        "persisted_at_utc": persisted_payload["persisted_at_utc"],
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 7. Recouplage avec audit before/after (ORDRE N°53-BIS-SUITE)
# ═════════════════════════════════════════════════════════════════════════
def recompute_with_drift_audit(
    reason: str = "manual_recompute",
    weights: Optional[Dict[str, float]] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    """Recouplage SUPER_ENGINES + audit forensique BEFORE/AFTER dédié.

    Args:
      reason: cause du recalcul (e.g., "hooks_activated", "manual",
        "ndvi_arrived", "noaa_dump_2025_q1").
      weights: poids fusion (default 50/50).
      persist: True → persiste audit dans audits_bp135/.

    Returns:
      {
        "before": {drift_max, drift_mean, score_global_fusion},
        "after":  {drift_max, drift_mean, score_global_fusion},
        "deltas": {drift_max, drift_mean, score_global_fusion},
        "audit_persisted": {...} | None,
        "v30_lock": "INVIOLÉ",
      }
    """
    from engines.v8_institutional.especes.super_engines_bp135_coupling_omega import (  # noqa: E501
        compute_super_engines_bp135_fusion,
    )
    if weights is None:
        weights = {"bio_reacteur_overlay": 0.5, "bp135": 0.5}

    t0 = time.time()
    # BEFORE = couplage standard sans overlay (canal BIO_REACTEUR brut)
    before = compute_super_engines_bp135_fusion(
        weights={"bio_reacteur": 0.5, "bp135": 0.5})
    before_snapshot = {
        "drift_max": before["drift_max_br_vs_bp135"],
        "drift_mean": before["drift_mean_br_vs_bp135"],
        "score_global_fusion": before["score_global_fusion"],
        "anti_generique_pass_global": before["anti_generique_pass_global"],
        "snapshot_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
    }

    # AFTER = couplage POST-overlay BP135→BR
    after = compute_overlay_fusion(weights=weights)
    after_snapshot = {
        "drift_max": after["drift_max_post_overlay"],
        "drift_mean": after["drift_mean_post_overlay"],
        "score_global_fusion": after["score_global_fusion_post_overlay"],
        "snapshot_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
    }

    deltas = {
        "drift_max": round(
            before_snapshot["drift_max"]
            - after_snapshot["drift_max"], 3),
        "drift_mean": round(
            before_snapshot["drift_mean"]
            - after_snapshot["drift_mean"], 3),
        "score_global_fusion": round(
            after_snapshot["score_global_fusion"]
            - before_snapshot["score_global_fusion"], 3),
    }

    # Sources scan (pour traçabilité activation hooks)
    sources_scan = scan_external_sources()

    payload = {
        "manifest_id": "RECOMPUTE_DRIFT_AUDIT_Ω",
        "ordre": "N°53-BIS-SUITE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "audit_type": "recompute_with_drift_before_after",
        "reason": reason,
        "weights_doctrinal": weights,
        "before": before_snapshot,
        "after": after_snapshot,
        "deltas": deltas,
        "improvement_drift_max": deltas["drift_max"],
        "improvement_drift_mean": deltas["drift_mean"],
        "improvement_score_global_fusion": deltas["score_global_fusion"],
        "external_sources_state": {
            "n_total": sources_scan["n_sources_total"],
            "n_available": sources_scan["n_sources_available"],
            "n_absent": sources_scan["n_sources_absent"],
            "n_anomalies_total": sources_scan.get("n_anomalies_total", 0),
        },
        "bp135_sha256": bp135_sha256(),
        "elapsed_s": round(time.time() - t0, 3),
        "computed_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
        "v30_lock": "INVIOLÉ",
    }

    audit_meta = None
    if persist:
        audit_meta = persist_audit(payload)
        payload["audit_persisted"] = audit_meta

    return payload


# ═════════════════════════════════════════════════════════════════════════
# 8. API READ-ONLY : liste audits persistés
# ═════════════════════════════════════════════════════════════════════════
def list_audits(
    page: int = 1,
    page_size: int = 50,
    drift_max_min: Optional[float] = None,
    drift_max_max: Optional[float] = None,
    drift_mean_min: Optional[float] = None,
    drift_mean_max: Optional[float] = None,
    since_utc: Optional[str] = None,
    audit_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Liste paginée et filtrable des audits persistés.

    Champs obligatoires retournés par audit :
      · audit_id              (= filename sans .json)
      · timestamp_utc         (= persisted_at_utc)
      · sha256                (= audit_sha256)
      · drift_max
      · drift_mean
      · score_global_fusion
      · bp135_sha256

    Read-only · strictement dérivé des fichiers d'audit · aucune mutation.
    """
    if not AUDITS_ROOT.exists():
        return {
            "manifest_id": "AUDITS_LIST_Ω",
            "ordre": "N°53-BIS-SUITE",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "page": page,
            "page_size": page_size,
            "total": 0,
            "n_returned": 0,
            "audits": [],
            "v30_lock": "INVIOLÉ",
        }

    page = max(1, int(page))
    page_size = max(1, min(500, int(page_size)))

    audit_files = sorted(
        AUDITS_ROOT.glob("audit_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    parsed: List[Dict[str, Any]] = []
    for f in audit_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        ap = data.get("audit_payload", {})
        # Champs obligatoires (tolérants aux différents types d'audit)
        # 1. drift_max / drift_mean / score_global_fusion :
        #    cherche dans payload root puis dans before/after
        drift_max = (
            ap.get("drift_max_post_overlay")
            or ap.get("drift_max_master_score")
            or ap.get("after", {}).get("drift_max")
            or ap.get("drift_max_br_vs_bp135")
            or 0.0)
        drift_mean = (
            ap.get("drift_mean_post_overlay")
            or ap.get("drift_mean_master_score")
            or ap.get("after", {}).get("drift_mean")
            or ap.get("drift_mean_br_vs_bp135")
            or 0.0)
        score_global_fusion = (
            ap.get("score_global_fusion_post_overlay")
            or ap.get("after", {}).get("score_global_fusion")
            or ap.get("score_global_fusion")
            or 0.0)
        bp135_sha = (
            ap.get("bp135_sha256")
            or ap.get("v30_lock_status", {}).get("bp135_sha256")
            or "")
        record = {
            "audit_id": f.stem,
            "filename": f.name,
            "timestamp_utc": data.get("persisted_at_utc"),
            "sha256": data.get("audit_sha256"),
            "drift_max": float(drift_max),
            "drift_mean": float(drift_mean),
            "score_global_fusion": float(score_global_fusion),
            "bp135_sha256": bp135_sha,
            "audit_type": (
                ap.get("audit_type")
                or ap.get("manifest_id")
                or "unknown"),
            "ordre": ap.get("ordre", data.get("ordre")),
            "size_bytes": f.stat().st_size,
        }
        # Filtres
        if (drift_max_min is not None
                and record["drift_max"] < drift_max_min):
            continue
        if (drift_max_max is not None
                and record["drift_max"] > drift_max_max):
            continue
        if (drift_mean_min is not None
                and record["drift_mean"] < drift_mean_min):
            continue
        if (drift_mean_max is not None
                and record["drift_mean"] > drift_mean_max):
            continue
        if (since_utc is not None
                and record["timestamp_utc"] is not None
                and record["timestamp_utc"] < since_utc):
            continue
        if (audit_type is not None
                and audit_type.lower() not in (
                    record["audit_type"] or "").lower()):
            continue
        parsed.append(record)

    total = len(parsed)
    start = (page - 1) * page_size
    end = start + page_size
    paged = parsed[start:end]

    return {
        "manifest_id": "AUDITS_LIST_Ω",
        "ordre": "N°53-BIS-SUITE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "page": page,
        "page_size": page_size,
        "total": total,
        "n_returned": len(paged),
        "filters_applied": {
            "drift_max_min": drift_max_min,
            "drift_max_max": drift_max_max,
            "drift_mean_min": drift_mean_min,
            "drift_mean_max": drift_mean_max,
            "since_utc": since_utc,
            "audit_type": audit_type,
        },
        "audits": paged,
        "audits_root": str(AUDITS_ROOT),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
    }


# ═════════════════════════════════════════════════════════════════════════
# 9. ORDRE N°53-BIS-SUITE-ULTIME — Audits trend (time series read-only)
# ═════════════════════════════════════════════════════════════════════════
def list_audits_trend(
    limit: int = 30,
    since_utc: Optional[str] = None,
    audit_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Série temporelle des N derniers audits persistés (read-only).

    Strictement dérivée de la persistance disque (aucun recalcul).
    Trié par mtime ASCENDANT (plus ancien → plus récent) — granularité
    microseconde, robuste face aux audits créés dans la même seconde.

    Champs par point :
      · timestamp_utc, drift_max, drift_mean, score_global_fusion, sha256

    Args:
      limit:      nombre maximum de points (default 30, max 500)
      since_utc:  filtre temporel (ISO 8601)
      audit_type: filtre par type d'audit (substring)
    """
    limit = max(1, min(500, int(limit)))
    # list_audits retourne déjà trié par mtime DESC (plus récent d'abord)
    # On inverse pour obtenir l'ordre chronologique ASC (ancien → récent).
    all_audits = list_audits(
        page=1, page_size=500,
        since_utc=since_utc, audit_type=audit_type,
    )["audits"]
    series = list(reversed(all_audits))  # ASC chronologique par mtime
    # Conserver les N derniers points (les plus récents)
    if len(series) > limit:
        series = series[-limit:]

    # Format série temporelle (champs strictement requis Commandant)
    points = [
        {
            "timestamp_utc": a["timestamp_utc"],
            "drift_max": a["drift_max"],
            "drift_mean": a["drift_mean"],
            "score_global_fusion": a["score_global_fusion"],
            "sha256": a["sha256"],
            "audit_id": a["audit_id"],
            "bp135_sha256": a["bp135_sha256"],
        }
        for a in series
    ]

    # Statistiques agrégées de la série
    drift_max_values = [p["drift_max"] for p in points]
    drift_mean_values = [p["drift_mean"] for p in points]
    score_values = [p["score_global_fusion"] for p in points]
    stats = {
        "n_points": len(points),
        "drift_max": {
            "min": min(drift_max_values) if drift_max_values else 0.0,
            "max": max(drift_max_values) if drift_max_values else 0.0,
            "first": drift_max_values[0] if drift_max_values else 0.0,
            "last": drift_max_values[-1] if drift_max_values else 0.0,
        },
        "drift_mean": {
            "min": min(drift_mean_values) if drift_mean_values else 0.0,
            "max": max(drift_mean_values) if drift_mean_values else 0.0,
            "first": drift_mean_values[0] if drift_mean_values else 0.0,
            "last": drift_mean_values[-1] if drift_mean_values else 0.0,
        },
        "score_global_fusion": {
            "min": min(score_values) if score_values else 0.0,
            "max": max(score_values) if score_values else 0.0,
            "first": score_values[0] if score_values else 0.0,
            "last": score_values[-1] if score_values else 0.0,
        },
    }
    if drift_max_values:
        stats["drift_max"]["delta_first_to_last"] = round(
            drift_max_values[-1] - drift_max_values[0], 3)
        stats["drift_mean"]["delta_first_to_last"] = round(
            drift_mean_values[-1] - drift_mean_values[0], 3)
        stats["score_global_fusion"]["delta_first_to_last"] = round(
            score_values[-1] - score_values[0], 3)

    return {
        "manifest_id": "AUDITS_TREND_Ω",
        "ordre": "N°53-BIS-SUITE-ULTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "limit_requested": limit,
        "n_points_returned": len(points),
        "filters_applied": {
            "since_utc": since_utc,
            "audit_type": audit_type,
        },
        "time_series_order": "chronological_ascending",
        "points": points,
        "aggregated_stats": stats,
        "audits_root": str(AUDITS_ROOT),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
    }


# ═════════════════════════════════════════════════════════════════════════
# 10. ORDRE N°53-BIS-SUITE-ULTIME — Watcher d'activation hooks
#     Détecte un changement d'état (PATHS_ABSENT → AVAILABLE) et déclenche
#     automatiquement un recompute_with_drift_audit doctrinal.
# ═════════════════════════════════════════════════════════════════════════
HOOKS_WATCHER_STATE_PATH = AUDITS_ROOT / "_hooks_watcher_state.json"


def _read_watcher_state() -> Dict[str, Any]:
    """Charge l'état précédent du watcher (ou vide si premier appel)."""
    if not HOOKS_WATCHER_STATE_PATH.exists():
        return {}
    try:
        return json.loads(
            HOOKS_WATCHER_STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_watcher_state(state: Dict[str, Any]) -> None:
    """Persiste l'état du watcher (FUSION ADD-ONLY isolated)."""
    AUDITS_ROOT.mkdir(parents=True, exist_ok=True)
    HOOKS_WATCHER_STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8")


def watch_and_recompute_if_hooks_activated(
    force: bool = False,
) -> Dict[str, Any]:
    """Détecte les transitions d'état des sources externes et déclenche
    un recompute_with_drift_audit si au moins une source est passée
    de PATHS_ABSENT/anomalous à AVAILABLE.

    Args:
      force: True → recompute toujours (ignore le watcher state).

    Returns:
      Dict avec :
        · transitions_detected : liste des sources ayant changé d'état
        · recompute_triggered  : True si recompute exécuté
        · recompute_audit      : payload audit BEFORE/AFTER (si triggered)
        · current_state        : état actuel des 6 sources
    """
    current_scan = scan_external_sources()
    current_states = {
        s["source_name"]: {
            "available": s["available"],
            "n_files_valid": s["n_files_valid"],
            "n_files_anomalies": s["n_files_anomalies"],
        }
        for s in current_scan["sources"]
    }
    previous = _read_watcher_state()
    previous_states = previous.get("source_states", {})

    transitions: List[Dict[str, Any]] = []
    for src_name, cur in current_states.items():
        prev = previous_states.get(src_name, {
            "available": False, "n_files_valid": 0,
            "n_files_anomalies": 0,
        })
        if (not prev.get("available")) and cur["available"]:
            transitions.append({
                "source": src_name,
                "transition": "PATHS_ABSENT_TO_AVAILABLE",
                "previous": prev,
                "current": cur,
            })
        elif prev.get("available") and (not cur["available"]):
            transitions.append({
                "source": src_name,
                "transition": "AVAILABLE_TO_PATHS_ABSENT",
                "previous": prev,
                "current": cur,
            })
        elif (cur["available"]
              and cur["n_files_valid"] != prev.get("n_files_valid", 0)):
            transitions.append({
                "source": src_name,
                "transition": "AVAILABLE_FILES_CHANGED",
                "previous": prev,
                "current": cur,
            })

    should_recompute = (
        force or any(
            t["transition"] == "PATHS_ABSENT_TO_AVAILABLE"
            or t["transition"] == "AVAILABLE_FILES_CHANGED"
            for t in transitions))

    recompute_payload = None
    if should_recompute:
        reasons = ["force_recompute"] if force else [
            f"{t['source']}_{t['transition']}" for t in transitions
            if t["transition"] != "AVAILABLE_TO_PATHS_ABSENT"
        ]
        recompute_payload = recompute_with_drift_audit(
            reason=f"hooks_watcher::{','.join(reasons)[:200]}",
            persist=True,
        )

    # Mise à jour state du watcher
    new_state = {
        "last_scan_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
        "source_states": current_states,
        "last_transitions": transitions,
        "last_recompute_audit_id": (
            recompute_payload.get("audit_persisted", {}).get(
                "audit_filename", "").replace(".json", "")
            if recompute_payload else None),
    }
    _write_watcher_state(new_state)

    return {
        "manifest_id": "HOOKS_WATCHER_RECOMPUTE_Ω",
        "ordre": "N°53-BIS-SUITE-ULTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "transitions_detected": transitions,
        "n_transitions": len(transitions),
        "force_requested": force,
        "recompute_triggered": should_recompute,
        "recompute_audit": recompute_payload,
        "current_state": current_states,
        "watcher_state_path": str(HOOKS_WATCHER_STATE_PATH),
        "v30_lock": "INVIOLÉ",
        "computed_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
    }


__all__ = [
    "EXTERNAL_SOURCES_REGISTRY",
    "BP135_TO_BR_NUTRITION_MAPPING",
    "ESPECES_FOR_MODELS",
    "AUDITS_ROOT",
    "HOOKS_WATCHER_STATE_PATH",
    "scan_external_sources",
    "compute_overlay_for_species",
    "merge_overlay",
    "compute_super_engines_with_overlay",
    "compute_overlay_fusion",
    "persist_audit",
    "recompute_with_drift_audit",
    "list_audits",
    "list_audits_trend",
    "watch_and_recompute_if_hooks_activated",
]
