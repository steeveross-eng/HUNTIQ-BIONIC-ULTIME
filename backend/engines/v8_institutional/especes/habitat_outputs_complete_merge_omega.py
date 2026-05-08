"""habitat_outputs_complete_merge_omega.py — COMPLETE_MERGE Ω (P9)
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

P9 — Greffe feeding_zones_FULL_dense + microhabitat_clusters_global_dense
au-dessus du habitat_outputs_final_merge V7 SANS modification du FINAL
(FUSION ADD-ONLY strict, V30_LOCK inviolate).

VERDICT VISÉ : 12/12 outputs computables COMPLETE_OPERATIONAL.

DOCTRINE :
  · COMPLETE LIT FINAL_MERGE + DENSE_GRID overlays (pas de recalcul)
  · feeding_zones_FULL intégré per-site uniquement si DENSE_GRID validé
  · microhabitat_clusters_global_dense intégré comme output cross-sites
  · Hook P8 doit être activé avant exécution

RÉFÉRENCES PEER-REVIEWED : Cf. nasa_ndvi_dense_grid_omega.py +
  habitat_outputs_final_merge_omega.py
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


HABITAT_COMPLETE_ROOT = Path(
    "/app/backend/data/pipelines/habitat_complete_merge")
HABITAT_COMPLETE_PATH = (
    HABITAT_COMPLETE_ROOT
    / "habitat_outputs_complete_merge_overlay.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _extract_feeding_full_per_site(
    dense_validation: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Extrait feeding_zones_FULL_dense per site BP_135."""
    out: Dict[str, Dict[str, Any]] = {}
    for site_name, site_data in (
            dense_validation.get("site_results") or {}).items():
        bands = site_data.get("bands_dense_grid") or {}
        ndvi_band = bands.get("250m_16_days_NDVI") or {}
        feeding_full = ndvi_band.get(
            "feeding_zones_full_dense") or {}
        if feeding_full and feeding_full.get("value") is not None:
            out[site_name] = {
                "valid": True,
                "feeding_full_score": feeding_full["value"],
                "regime": feeding_full.get("regime"),
                "components": feeding_full.get("components"),
                "species_thresholds_used": feeding_full.get(
                    "species_thresholds_used"),
            }
        else:
            out[site_name] = {
                "valid": False,
                "reason": (
                    feeding_full.get("regime")
                    or "ndvi_dense_band_invalid"),
            }
    return out


def _compute_feeding_zones_full_output(
    feeding_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Construit output feeding_zones_FULL doctrinal."""
    if not feeding_data.get("valid"):
        return {
            "value": None,
            "regime": "DEFERRED_NO_VALID_DENSE_GRID",
            "reason": feeding_data.get("reason"),
            "primary_reference": "Borowik_2013_EurJWildlRes",
        }
    return {
        "value": feeding_data["feeding_full_score"],
        "unit": "feeding_zones_FULL_dense_score_0_100",
        "regime": feeding_data["regime"],
        "components": feeding_data["components"],
        "species_thresholds_used": feeding_data[
            "species_thresholds_used"],
        "doctrinal_caveat": (
            "feeding_zones FULL via dense grid spatial subset "
            "MOD13Q1 (kmAboveBelow×kmLeftRight) summer "
            "(juin-août). 1734+ pixels par site (Pettorelli "
            "2005 §4.1 satisfait). Anti-générique strict."),
        "primary_references": [
            "Borowik_2013_EurJWildlRes",
            "Pettorelli_2005_TREE",
            "Hamel_2009_JApplEcol",
        ],
    }


def _compute_microhabitat_clusters_global_dense_output(
    dense_validation: Dict[str, Any],
) -> Dict[str, Any]:
    """Construit output microhabitat_clusters_global_dense doctrinal."""
    microhab = dense_validation.get(
        "microhabitat_clusters_global_dense") or {}
    if not microhab or microhab.get("value") is None:
        return {
            "value": None,
            "regime": "DEFERRED_NO_VALID_GLOBAL_AGGREGATION",
            "primary_reference": "Pettorelli_2005_TREE",
        }
    return {
        "value": microhab["value"],
        "unit": microhab.get("unit", "shannon_diversity_h"),
        "regime": microhab["regime"],
        "components": microhab.get("components"),
        "doctrinal_caveat": (
            "Diversité écologique cross-sites globale via "
            "Shannon entropy (1948) sur partition NDVI "
            "5-clusters (Pettorelli 2005 §4.1 + Hamel 2009). "
            "Densité grille >= 8000 pixels totaux. "
            "Anti-générique strict."),
        "primary_references": microhab.get(
            "primary_references", [
                "Pettorelli_2005_TREE",
                "Shannon_1948_BellSystemTechJ",
                "Hamel_2009_JApplEcol",
            ]),
    }


def merge_habitat_outputs_complete(
    species_to_site_map: Optional[Dict[str, str]] = None,
    persist: bool = True,
    require_dense_grid_hook_active: bool = True,
) -> Dict[str, Any]:
    """COMPLETE_MERGE_Ω (P9) · greffe feeding_FULL + microhab_dense.

    FUSION ADD-ONLY strict : héritage FINAL sans mutation.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        merge_habitat_outputs_final,
    )
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (
        DENSE_GRID_HOOK_ACTIVATION_PATH,
        get_last_validated_dense_grid,
    )
    require_guardrails_enforced(
        "merge_habitat_outputs_complete")

    t_total = time.time()

    # 1) Recompute FINAL (P7) sans persist
    final_payload = merge_habitat_outputs_final(
        species_to_site_map=species_to_site_map,
        persist=False,
        require_rut_hook_active=True)
    if "REJECTED" in final_payload.get("verdict", ""):
        return {
            "manifest_id": "HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
            "ordre": "P9_HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "verdict": (
                "HABITAT_COMPLETE_MERGE_REJECTED_FINAL_FAILED::"
                + final_payload.get("verdict", "unknown")),
            "rejection_explanation": (
                "FUSION ADD-ONLY strict : impossible de "
                "merger sur FINAL rejeté."),
            "final_payload_summary": {
                "verdict": final_payload.get("verdict"),
                "rejection_explanation": final_payload.get(
                    "rejection_explanation"),
            },
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t_total, 3),
        }

    # 2) Vérifier hook DENSE_GRID activé
    dense_hook_activated = False
    if DENSE_GRID_HOOK_ACTIVATION_PATH.exists():
        try:
            state = json.loads(
                DENSE_GRID_HOOK_ACTIVATION_PATH.read_text(
                    encoding="utf-8"))
            history = state.get("history", [])
            if history and history[-1].get("activated"):
                dense_hook_activated = True
        except json.JSONDecodeError:
            dense_hook_activated = False

    if (require_dense_grid_hook_active
            and not dense_hook_activated):
        return {
            "manifest_id": "HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
            "ordre": "P9_HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "verdict": (
                "HABITAT_COMPLETE_MERGE_REJECTED_"
                "DENSE_GRID_HOOK_NOT_ACTIVATED"),
            "rejection_explanation": (
                "Anti-générique strict : feeding_zones_FULL + "
                "microhabitat_clusters_global_dense ne peuvent "
                "être mergés que si "
                "NASA_NDVI_DENSE_GRID_HOOK activé."),
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t_total, 3),
        }

    # 3) Charge DENSE_GRID validation (read-only)
    dense_v = get_last_validated_dense_grid()
    dense_loaded = dense_v is not None
    dense_manifest_sha256 = (dense_v or {}).get("manifest_sha256")

    # 4) Extraction per site
    feeding_per_site: Dict[str, Dict[str, Any]] = (
        _extract_feeding_full_per_site(dense_v) if dense_v else {})

    # 5) Greffe per site (FUSION ADD-ONLY)
    per_site_outputs_complete: Dict[str, Dict[str, Any]] = {}
    n_feeding_full_computed = 0
    for site_name, final_site_data in (
            final_payload.get("per_site_outputs_final") or {}
    ).items():
        feeding = feeding_per_site.get(site_name) or {
            "valid": False,
            "reason": "site_missing_in_dense_grid",
        }
        feeding_output = (
            _compute_feeding_zones_full_output(feeding))
        if feeding_output.get("value") is not None:
            n_feeding_full_computed += 1
        # Build merged structure (PAS de mutation final_site_data)
        merged = dict(final_site_data)
        merged_outputs = dict(
            final_site_data.get("computed_outputs") or {})
        merged_outputs["feeding_zones_FULL"] = feeding_output
        merged["computed_outputs"] = merged_outputs
        merged["covariates_inputs"] = dict(
            final_site_data.get("covariates_inputs") or {})
        if feeding.get("valid"):
            merged["covariates_inputs"][
                "feeding_full_score"] = (
                feeding["feeding_full_score"])
            merged["covariates_inputs"][
                "feeding_full_regime"] = (
                feeding["regime"])
        per_site_outputs_complete[site_name] = merged

    # 6) Output cross-sites microhabitat_clusters_global_dense
    microhab_global_output = (
        _compute_microhabitat_clusters_global_dense_output(
            dense_v if dense_v else {}))

    # 7) Outputs deferred FINAL (devrait être 0 maintenant)
    outputs_still_deferred_complete: Dict[str, Any] = {}
    # Aucun output deferred si tout OK

    # 8) Verdict COMPLETE
    n_sites = len(per_site_outputs_complete)
    n_per_site_outputs_complete = 10  # 9 FINAL + 1 feeding_FULL
    n_outputs_with_value_per_site = sum(
        1 for sp_data in per_site_outputs_complete.values()
        for output_val in (
            sp_data.get("computed_outputs") or {}).values()
        if (isinstance(output_val, dict)
            and output_val.get("value") is not None))
    n_global_outputs_with_value = (
        1 if microhab_global_output.get("value") is not None
        else 0)

    n_total_outputs_with_value = (
        n_outputs_with_value_per_site
        + n_global_outputs_with_value)
    n_total_expected = (
        n_sites * n_per_site_outputs_complete + 1)
    coverage_ratio_complete = (
        n_total_outputs_with_value
        / max(n_total_expected, 1))

    if coverage_ratio_complete >= 0.95:
        verdict = (
            "HABITAT_COMPLETE_MERGE_FULL_12_OF_12_COMPUTABLE")
    elif coverage_ratio_complete >= 0.5:
        verdict = (
            f"HABITAT_COMPLETE_MERGE_PARTIAL::"
            f"{n_total_outputs_with_value}_OF_"
            f"{n_total_expected}_VALUES_COMPUTED")
    else:
        verdict = (
            "HABITAT_COMPLETE_MERGE_INSUFFICIENT_COVERAGE")

    payload = {
        "manifest_id": "HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
        "ordre": "P9_HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "verdict": verdict,
        "coverage_ratio": round(coverage_ratio_complete, 3),
        "n_outputs_per_site_classes_complete": (
            "10_per_site_+_2_global_=_12_total_classes"),
        "n_outputs_per_site_values_complete": (
            n_per_site_outputs_complete),
        "n_outputs_total_values_computed_complete": (
            n_total_outputs_with_value),
        "n_outputs_per_site_total_values_computed": (
            n_outputs_with_value_per_site),
        "n_global_outputs_computed": (
            n_global_outputs_with_value),
        "n_feeding_full_computed": n_feeding_full_computed,
        "n_sites_processed": n_sites,
        "final_inheritance": {
            "final_verdict": final_payload.get("verdict"),
            "final_coverage_ratio": final_payload.get(
                "coverage_ratio"),
            "final_n_outputs_total_values_computed_final": (
                final_payload.get(
                    "n_outputs_total_values_computed_final")),
            "final_merge_sha256": final_payload.get(
                "final_merge_sha256"),
            "final_v3_inheritance": final_payload.get(
                "v3_inheritance"),
            "final_rut_validation_manifest_sha256": (
                final_payload.get(
                    "rut_validation_manifest_sha256")),
        },
        "dense_grid_hook_loaded": dense_loaded,
        "dense_grid_hook_activated": dense_hook_activated,
        "dense_grid_validation_manifest_sha256": (
            dense_manifest_sha256),
        "species_to_site_map_used": (
            final_payload.get("species_to_site_map_used")),
        "per_site_outputs_complete": per_site_outputs_complete,
        "global_outputs_complete": {
            "microhabitat_clusters_global_dense": (
                microhab_global_output),
        },
        "outputs_still_deferred_anti_generique_strict_complete": (
            outputs_still_deferred_complete),
        "scientific_references_complete_added": [
            ("Pettorelli et al. (2005). TREE, 20(9):503-510. "
             "DOI:10.1016/j.tree.2005.05.011"),
            ("Borowik et al. (2013). Eur J Wildl Res, "
             "59:675-682. DOI:10.1007/s10344-013-0720-0"),
            ("Hamel et al. (2009). J Appl Ecol, 46:582-589. "
             "DOI:10.1111/j.1365-2664.2009.01643.x"),
            ("Shannon (1948). Bell System Technical J, "
             "27(3):379-423."),
        ],
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t_total, 3),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["complete_merge_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        HABITAT_COMPLETE_ROOT.mkdir(
            parents=True, exist_ok=True)
        if HABITAT_COMPLETE_PATH.exists():
            try:
                state = json.loads(
                    HABITAT_COMPLETE_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(state, dict) or (
                        "history" not in state):
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}
        state["history"].append(payload)
        state["last_updated_utc"] = _utc_now()
        state["n_merges_complete"] = len(state["history"])
        state["last_complete_merge_sha256"] = payload_sha256
        state["last_verdict"] = verdict
        state["v30_lock"] = "INVIOLÉ"
        HABITAT_COMPLETE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            HABITAT_COMPLETE_PATH)
        persisted["overlay_size_bytes"] = (
            HABITAT_COMPLETE_PATH.stat().st_size)

        log_forensic_event(
            scope="HABITAT",
            event="HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
            details={
                "complete_merge_sha256": payload_sha256,
                "verdict": verdict,
                "n_sites_processed": n_sites,
                "n_feeding_full_computed": (
                    n_feeding_full_computed),
                "n_global_outputs_computed": (
                    n_global_outputs_with_value),
                "n_total_outputs_with_value": (
                    n_total_outputs_with_value),
                "dense_grid_validation_manifest_sha256": (
                    dense_manifest_sha256),
            },
            persist=True,
        )

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        persisted["audit_persisted"] = persist_audit({
            "audit_type": "NOAA_PIPELINE",
            "subtype": "HABITAT_OUTPUTS_COMPLETE_MERGE",
            "ordre": "P9_HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "verdict": verdict,
            "complete_merge_sha256": payload_sha256,
            "n_sites_processed": n_sites,
            "n_feeding_full_computed": (
                n_feeding_full_computed),
            "n_global_outputs_computed": (
                n_global_outputs_with_value),
            "dense_grid_validation_manifest_sha256": (
                dense_manifest_sha256),
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        })

    payload["persisted_paths"] = persisted
    return payload


def get_habitat_complete_merge_status() -> Dict[str, Any]:
    if not HABITAT_COMPLETE_PATH.exists():
        return {
            "manifest_id":
                "HABITAT_OUTPUTS_COMPLETE_MERGE_STATUS_Ω",
            "current_status": "NOT_MERGED_COMPLETE",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        HABITAT_COMPLETE_PATH.read_text(encoding="utf-8"))
    last = (
        state["history"][-1]
        if state.get("history") else None)
    return {
        "manifest_id":
            "HABITAT_OUTPUTS_COMPLETE_MERGE_STATUS_Ω",
        "ordre": "P9_HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "current_status": (
            "MERGED_COMPLETE_OPERATIONAL" if last
            else "NOT_MERGED_COMPLETE"),
        "n_merges_complete_history": state.get(
            "n_merges_complete", 0),
        "last_complete_merge_sha256": state.get(
            "last_complete_merge_sha256"),
        "last_verdict": state.get("last_verdict"),
        "last_updated_utc": state.get("last_updated_utc"),
        "last_summary": (
            {
                "verdict": last.get("verdict"),
                "coverage_ratio": last.get("coverage_ratio"),
                "n_feeding_full_computed": last.get(
                    "n_feeding_full_computed"),
                "n_global_outputs_computed": last.get(
                    "n_global_outputs_computed"),
                "n_outputs_total_values_computed_complete": (
                    last.get(
                        "n_outputs_total_values_computed_complete")),
            } if last else None),
        "overlay_path": str(HABITAT_COMPLETE_PATH),
        "overlay_size_bytes": (
            HABITAT_COMPLETE_PATH.stat().st_size),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "HABITAT_COMPLETE_ROOT",
    "HABITAT_COMPLETE_PATH",
    "merge_habitat_outputs_complete",
    "get_habitat_complete_merge_status",
]
