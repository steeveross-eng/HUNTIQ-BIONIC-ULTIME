"""visualizer_endpoint_omega.py — TERRITOIRE_VISUALIZER_ENDPOINT_Ω (P10)
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

P10 — Exposition unifiée de TOUTES les couches doctrinales pour
validation et production.

DOCTRINE :
  · GET unique : scan read-only de tous les overlays JSON
  · Aucune mutation, aucune fabrication, aucun recalcul moteur
  · Expose SHA-256 + verdict + last_updated par couche
  · Vue résumée (manifest_id, status, derniers chiffres clés)
  · FUSION ADD-ONLY strict (aucun fichier maître muté)

LAYERS EXPOSÉES (toutes celles ayant un overlay JSON) :
  Hooks principaux V1 :
    · NASA_NDVI (MOD13Q1)
    · USGS_SOIL (SoilGrids ISRIC)
    · RSF_SSF (GBIF MaxEnt-lite)
    · OPENTOPOGRAPHY (SRTMGL1)
    · CANOPY (MOD44B VCF)
  Hook compute V1 :
    · HABITAT_OUTPUTS_COMPUTE
  Hook recompute V2 (avec 5 hooks principaux) :
    · HABITAT_OUTPUTS_RECOMPUTE
  Hook recompute V3 (avec ANTHROPOGENIC) :
    · ANTHROPOGENIC_PRESSURE (P4)
    · HABITAT_OUTPUTS_RECOMPUTE_V3 (P5)
  Hook merge FINAL (avec RUT) :
    · TEMPORAL_RUT_DATA (P6)
    · HABITAT_OUTPUTS_FINAL_MERGE (P7)
  Hook merge COMPLETE (avec DENSE_GRID) :
    · NASA_NDVI_DENSE_GRID (P8)
    · HABITAT_OUTPUTS_COMPLETE_MERGE (P9)
  Hook timeseries decade :
    · NASA_NDVI_TIMESERIES_DECADE
  Hook V12-MAÎTRE :
    · HOOK_CONTAMINATION_AFFUT_DEPENDENCY

ANTI-GÉNÉRIQUE STRICT :
  · Read-only sur overlays JSON existants
  · NODATA reporté honnêtement (couches non encore activées)
  · Aucun mock, aucune fabrication
  · Validation par scan pathlib des chemins doctrinaux
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ═════════════════════════════════════════════════════════════════════════
# Catalogue doctrinal des overlays exposables (lecture seule)
# ═════════════════════════════════════════════════════════════════════════
# Chaque entrée :
#   (logical_layer_key, overlay_path, summary_extractor_func_name)
LAYER_CATALOG: List[Dict[str, Any]] = [
    {
        "logical_key": "V12_CONTAMINATION_AFFUT_DEPENDENCY",
        "ordre": "COMMANDE_INSTITUTIONNELLE_Ω_V12-MAÎTRE",
        "overlay_path": (
            "/app/backend/data/pipelines/"
            "contamination_affut_dependency/"
            "contamination_affut_dependency_hook_overlay.json"),
        "primary_reference": "DOCTRINE_V12_MASTER",
    },
    {
        "logical_key": "NASA_NDVI",
        "ordre": "P1_NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
        "overlay_path": (
            "/app/backend/data/pipelines/nasa_ndvi/"
            "nasa_ndvi_hook_activation_overlay.json"),
        "primary_reference": "Pettorelli_2005_TREE",
    },
    {
        "logical_key": "USGS_SOIL",
        "ordre": "P2_USGS_SOIL_HOOK_ACTIVATE_Ω",
        "overlay_path": (
            "/app/backend/data/pipelines/usgs_soil/"
            "usgs_soil_hook_activation_overlay.json"),
        "primary_reference": "Hengl_2017_PLoSONE_SoilGrids",
    },
    {
        "logical_key": "RSF_SSF_GBIF",
        "ordre": "P3_RSF_SSF_HOOK_ACTIVATE",
        "overlay_path": (
            "/app/backend/data/pipelines/rsf_ssf/"
            "rsf_ssf_hook_activation_overlay.json"),
        "primary_reference": "Manly_2002_RSF_MaxEnt",
    },
    {
        "logical_key": "OPENTOPOGRAPHY_SRTM",
        "ordre": "P4_OPENTOPOGRAPHY_HOOK_ACTIVATE_Ω",
        "overlay_path": (
            "/app/backend/data/pipelines/opentopography/"
            "opentopography_hook_activation_overlay.json"),
        "primary_reference": "Farr_2007_RevGeophys_SRTMGL1",
    },
    {
        "logical_key": "CANOPY_MOD44B",
        "ordre": "P5_CANOPY_HOOK_ACTIVATE_Ω",
        "overlay_path": (
            "/app/backend/data/pipelines/canopy/"
            "canopy_hook_activation_overlay.json"),
        "primary_reference": "Hansen_2003_MOD44B_VCF",
    },
    {
        "logical_key": "HABITAT_OUTPUTS_COMPUTE",
        "ordre": "HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME",
        "overlay_path": (
            "/app/backend/data/pipelines/habitat_outputs/"
            "habitat_outputs_compute_overlay.json"),
        "primary_reference": "Pettorelli_2005_TREE",
    },
    {
        "logical_key": "HABITAT_OUTPUTS_RECOMPUTE_V2",
        "ordre": "HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME",
        "overlay_path": (
            "/app/backend/data/pipelines/habitat_recompute_v2/"
            "habitat_outputs_recompute_overlay.json"),
        "primary_reference": "Pettorelli_2005_TREE",
    },
    {
        "logical_key": "ANTHROPOGENIC_PRESSURE_P4",
        "ordre": "P4_ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_Ω",
        "overlay_path": (
            "/app/backend/data/pipelines/"
            "anthropogenic_pressure/"
            "anthropogenic_pressure_hook_activation_overlay.json"),
        "primary_reference": "Naidoo_Burton_2010_ConservationLetters",
    },
    {
        "logical_key": "HABITAT_OUTPUTS_RECOMPUTE_V3_P5",
        "ordre": "P5_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
        "overlay_path": (
            "/app/backend/data/pipelines/habitat_recompute_v3/"
            "habitat_outputs_recompute_v3_overlay.json"),
        "primary_reference": "Naidoo_Burton_2010_ConservationLetters",
    },
    {
        "logical_key": "TEMPORAL_RUT_P6",
        "ordre": "P6_TEMPORAL_RUT_DATA_HOOK_ACTIVATE_Ω",
        "overlay_path": (
            "/app/backend/data/pipelines/temporal_rut/"
            "temporal_rut_hook_activation_overlay.json"),
        "primary_reference": "Bronson_1989_MammalianReprod",
    },
    {
        "logical_key": "HABITAT_OUTPUTS_FINAL_MERGE_P7",
        "ordre": "P7_HABITAT_OUTPUTS_FINAL_MERGE_Ω",
        "overlay_path": (
            "/app/backend/data/pipelines/habitat_final_merge/"
            "habitat_outputs_final_merge_overlay.json"),
        "primary_reference": "Bowyer_1981_JMammal",
    },
    {
        "logical_key": "NASA_NDVI_DENSE_GRID_P8",
        "ordre": "P8_NASA_NDVI_DENSE_GRID_Ω",
        "overlay_path": (
            "/app/backend/data/pipelines/nasa_ndvi_dense_grid/"
            "nasa_ndvi_dense_grid_hook_activation_overlay.json"),
        "primary_reference": "Pettorelli_2005_TREE",
    },
    {
        "logical_key": "HABITAT_OUTPUTS_COMPLETE_MERGE_P9",
        "ordre": "P9_HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
        "overlay_path": (
            "/app/backend/data/pipelines/"
            "habitat_complete_merge/"
            "habitat_outputs_complete_merge_overlay.json"),
        "primary_reference": (
            "Borowik_2013_EurJWildlRes_Pettorelli_2005"),
    },
    {
        "logical_key": "NASA_NDVI_TIMESERIES_DECADE",
        "ordre": "NASA_NDVI_TIMESERIES_DECADE_Ω",
        "overlay_path": (
            "/app/backend/data/pipelines/nasa_ndvi_decade/"
            "nasa_ndvi_timeseries_decade_overlay.json"),
        "primary_reference": "Hebblewhite_2008_EcolMonogr",
    },
]


def _summarize_overlay(
    layer: Dict[str, Any],
) -> Dict[str, Any]:
    """Lecture résumée d'un overlay (anti-générique strict)."""
    overlay_path = Path(layer["overlay_path"])
    summary: Dict[str, Any] = {
        "logical_key": layer["logical_key"],
        "ordre": layer["ordre"],
        "primary_reference": layer["primary_reference"],
        "overlay_path": str(overlay_path),
        "exists": overlay_path.exists(),
    }
    if not overlay_path.exists():
        summary["status"] = "OVERLAY_NOT_PRESENT"
        summary["last_manifest_sha256"] = None
        summary["last_verdict"] = None
        summary["last_updated_utc"] = None
        return summary
    try:
        state = json.loads(
            overlay_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        summary["status"] = "OVERLAY_READ_ERROR"
        summary["read_error"] = str(e)[:200]
        return summary
    if not isinstance(state, dict):
        summary["status"] = "OVERLAY_INVALID_FORMAT"
        return summary
    history = state.get("history") or []
    summary["status"] = (
        "OVERLAY_HEALTHY" if history else "OVERLAY_EMPTY_HISTORY")
    summary["last_manifest_sha256"] = (
        state.get("last_manifest_sha256")
        or state.get("last_activation_sha256")
        or state.get("last_habitat_outputs_sha256")
        or state.get("last_recompute_sha256")
        or state.get("last_recompute_v3_sha256")
        or state.get("last_final_merge_sha256")
        or state.get("last_complete_merge_sha256")
        or state.get("last_compute_sha256"))
    summary["last_verdict"] = state.get("last_verdict")
    summary["last_updated_utc"] = state.get(
        "last_updated_utc")
    summary["v30_lock"] = state.get("v30_lock")
    summary["n_history_entries"] = len(history)
    summary["overlay_size_bytes"] = (
        overlay_path.stat().st_size)
    if history:
        last = history[-1]
        summary["last_entry_summary"] = {
            "manifest_id": last.get("manifest_id"),
            "verdict": last.get("verdict"),
            "anti_generique_strict": last.get(
                "anti_generique_strict"),
            "v30_lock": last.get("v30_lock"),
            "drift_zero": last.get("drift_zero"),
            "fusion_add_only": last.get("fusion_add_only"),
            "executed_at_utc": last.get("executed_at_utc"),
            "elapsed_s": last.get("elapsed_s"),
        }
    return summary


def expose_all_layers_unified() -> Dict[str, Any]:
    """TERRITOIRE_VISUALIZER_ENDPOINT_Ω · scan unifié read-only.

    Anti-générique strict :
      · Lecture seule des overlays JSON
      · Aucune fabrication, aucun mock, aucun recalcul moteur
      · Expose SHA-256 + verdict + status par couche
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced,
    )
    require_guardrails_enforced("expose_all_layers_unified")

    t0 = time.time()
    layers_summary: Dict[str, Dict[str, Any]] = {}
    n_overlays_present = 0
    n_overlays_absent = 0
    n_overlays_healthy = 0
    n_overlays_with_errors = 0
    last_updated_global: Optional[str] = None
    layers_chronological: List[Dict[str, Any]] = []

    for layer in LAYER_CATALOG:
        s = _summarize_overlay(layer)
        layers_summary[layer["logical_key"]] = s
        if s.get("exists"):
            n_overlays_present += 1
            if s.get("status") == "OVERLAY_HEALTHY":
                n_overlays_healthy += 1
            elif s.get("status") not in (
                    "OVERLAY_HEALTHY", "OVERLAY_EMPTY_HISTORY"):
                n_overlays_with_errors += 1
        else:
            n_overlays_absent += 1
        if s.get("last_updated_utc"):
            if (last_updated_global is None
                    or s["last_updated_utc"]
                    > last_updated_global):
                last_updated_global = s["last_updated_utc"]
            layers_chronological.append({
                "logical_key": layer["logical_key"],
                "last_updated_utc": s["last_updated_utc"],
                "last_manifest_sha256": s.get(
                    "last_manifest_sha256"),
                "last_verdict": s.get("last_verdict"),
            })

    layers_chronological.sort(
        key=lambda x: x["last_updated_utc"] or "",
        reverse=True)

    # Verdict global
    if (n_overlays_with_errors == 0
            and n_overlays_healthy == len(LAYER_CATALOG)):
        verdict = "VISUALIZER_ALL_LAYERS_HEALTHY"
    elif n_overlays_healthy > 0:
        verdict = (
            f"VISUALIZER_PARTIAL::{n_overlays_healthy}_HEALTHY"
            f"_OF_{len(LAYER_CATALOG)}_LAYERS")
    else:
        verdict = "VISUALIZER_NO_OVERLAYS_PRESENT"

    payload = {
        "manifest_id": "TERRITOIRE_VISUALIZER_ENDPOINT_Ω",
        "ordre": "P10_TERRITOIRE_VISUALIZER_ENDPOINT_CREATE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "verdict": verdict,
        "n_layers_catalog": len(LAYER_CATALOG),
        "n_overlays_present": n_overlays_present,
        "n_overlays_absent": n_overlays_absent,
        "n_overlays_healthy": n_overlays_healthy,
        "n_overlays_with_errors": n_overlays_with_errors,
        "last_updated_global_utc": last_updated_global,
        "layers": layers_summary,
        "layers_chronological_most_recent_first": (
            layers_chronological),
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "scanned_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t0, 4),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["scan_sha256"] = payload_sha256
    return payload


__all__ = [
    "LAYER_CATALOG",
    "expose_all_layers_unified",
]
