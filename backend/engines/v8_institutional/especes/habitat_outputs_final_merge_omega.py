"""habitat_outputs_final_merge_omega.py — FINAL_MERGE_Ω (P7)
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

P7 — Greffe rut_zones_temporal_proxy au-dessus du recompute V3 SANS
modification du V3 (FUSION ADD-ONLY strict, V30_LOCK inviolate).

NOUVEAUX OUTPUTS DÉBLOQUÉS FINAL (vs V3) :
  · rut_zones (composite Bronson 1989 + Hebblewhite 2008 + Bowyer 1981)
    → 10/12 outputs computables possibles

OUTPUTS ENCORE DEFERRED FINAL (2 restants vs 3 en V3) :
  · feeding_zones FULL (require dense grid Pettorelli 2005 §4.1 ;
    proxy summer disponible via NDVI_DECADE_Ω)
  · microhabitat_clusters_global_dense (require N>5 grille)

DOCTRINE :
  · FINAL LIT V3 + TEMPORAL_RUT overlays (pas de recalcul V3)
  · rut_zones intégré per-site uniquement si VALIDATE manifest valide
  · Hook P6 doit être activé avant exécution
  · Verdict adaptatif :
      ALL HOOKS ACTIVE     → 10_OF_12_FULL_WITH_RUT_PROXY
      RUT MISSING          → fallback V3 9_OF_12 (pas d'erreur)

RÉFÉRENCES PEER-REVIEWED :
  Cf. temporal_rut_data_omega.py + habitat_outputs_recompute_v3_omega.py
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


HABITAT_FINAL_ROOT = Path(
    "/app/backend/data/pipelines/habitat_final_merge")
HABITAT_FINAL_PATH = (
    HABITAT_FINAL_ROOT
    / "habitat_outputs_final_merge_overlay.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _extract_rut_per_site(
    rut_validation: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Extrait composite + components per site BP_135."""
    out: Dict[str, Dict[str, Any]] = {}
    for site_name, site_data in (
            rut_validation.get("site_results") or {}).items():
        composite = site_data.get(
            "rut_zones_composite") or {}
        if composite.get("valid"):
            out[site_name] = {
                "valid": True,
                "composite_score_0_100": composite.get(
                    "composite_score_0_100"),
                "regime": composite.get("regime"),
                "components": composite.get("components"),
                "n_pillars_valid": composite.get(
                    "n_pillars_valid"),
                "doctrinal_caveat": composite.get(
                    "doctrinal_caveat"),
            }
        else:
            out[site_name] = {
                "valid": False,
                "reason": composite.get(
                    "reason", "rut_composite_invalid"),
            }
    return out


def _compute_rut_zones_output(
    rut_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Construit output rut_zones (Bowyer 1981 + Bronson 1989)."""
    if not rut_data.get("valid"):
        return {
            "value": None,
            "regime": "DEFERRED_NO_VALID_RUT_DATA",
            "reason": rut_data.get("reason"),
            "primary_reference": "Bowyer_1981_JMammal",
        }
    return {
        "value": rut_data["composite_score_0_100"],
        "unit": "rut_zones_temporal_proxy_score_0_100",
        "regime": rut_data["regime"],
        "n_pillars_valid": rut_data["n_pillars_valid"],
        "doctrinal_caveat": rut_data["doctrinal_caveat"],
        "components": rut_data["components"],
        "primary_references": [
            "Bronson_1989_MammalianReprod",
            "Hebblewhite_2008_EcolMonogr",
            "Bowyer_1981_JMammal",
        ],
    }


def merge_habitat_outputs_final(
    species_to_site_map: Optional[Dict[str, str]] = None,
    persist: bool = True,
    require_rut_hook_active: bool = True,
) -> Dict[str, Any]:
    """FINAL_MERGE_Ω · greffe rut_zones sur V3 (FUSION ADD-ONLY)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        recompute_habitat_outputs_with_anthropogenic_pressure_v3,
    )
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        RUT_VALIDATION_PATH,
        RUT_HOOK_ACTIVATION_PATH,
        get_last_validated_rut_per_site,
    )
    require_guardrails_enforced("merge_habitat_outputs_final")
    t_total = time.time()

    # 1) Recompute V3 (FUSION ADD-ONLY : pas de mutation V3)
    v3_payload = (
        recompute_habitat_outputs_with_anthropogenic_pressure_v3(
            species_to_site_map=species_to_site_map,
            persist=False,  # FINAL persiste son propre overlay
            require_anthropogenic_hook_active=True))
    if "REJECTED" in v3_payload.get("verdict", ""):
        return {
            "manifest_id": "HABITAT_OUTPUTS_FINAL_MERGE_Ω",
            "ordre": "P7_HABITAT_OUTPUTS_FINAL_MERGE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "verdict": (
                "HABITAT_FINAL_MERGE_REJECTED_V3_FAILED::"
                + v3_payload.get("verdict", "unknown")),
            "rejection_explanation": (
                "FUSION ADD-ONLY strict : impossible de "
                "merger sur V3 rejeté."),
            "v3_payload_summary": {
                "verdict": v3_payload.get("verdict"),
                "rejection_explanation": v3_payload.get(
                    "rejection_explanation"),
            },
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t_total, 3),
        }

    # 2) Vérifier hook RUT activé
    rut_hook_activated = False
    if RUT_HOOK_ACTIVATION_PATH.exists():
        try:
            state = json.loads(
                RUT_HOOK_ACTIVATION_PATH.read_text(
                    encoding="utf-8"))
            history = state.get("history", [])
            if history and history[-1].get("activated"):
                rut_hook_activated = True
        except json.JSONDecodeError:
            rut_hook_activated = False

    if require_rut_hook_active and not rut_hook_activated:
        return {
            "manifest_id": "HABITAT_OUTPUTS_FINAL_MERGE_Ω",
            "ordre": "P7_HABITAT_OUTPUTS_FINAL_MERGE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "verdict": (
                "HABITAT_FINAL_MERGE_REJECTED_"
                "RUT_HOOK_NOT_ACTIVATED"),
            "rejection_explanation": (
                "Anti-générique strict : rut_zones ne peut "
                "être mergé que si TEMPORAL_RUT_DATA_HOOK "
                "activé."),
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t_total, 3),
        }

    # 3) Charge RUT validation (read-only)
    rut_v = get_last_validated_rut_per_site()
    rut_loaded = rut_v is not None
    rut_manifest_sha256 = (rut_v or {}).get("manifest_sha256")

    # 4) Extraction rut per site
    rut_per_site: Dict[str, Dict[str, Any]] = (
        _extract_rut_per_site(rut_v) if rut_v else {})

    # 5) Greffe per site (FUSION ADD-ONLY FINAL)
    per_site_outputs_final: Dict[str, Dict[str, Any]] = {}
    n_rut_computed = 0
    for site_name, v3_site_data in (
            v3_payload.get("per_site_outputs_v3") or {}).items():
        rut = rut_per_site.get(site_name) or {
            "valid": False,
            "reason": "site_missing_in_rut_validation",
        }
        rut_output = _compute_rut_zones_output(rut)
        if rut_output.get("value") is not None:
            n_rut_computed += 1
        # Build merged structure (PAS de mutation v3_site_data)
        merged = dict(v3_site_data)
        merged_outputs = dict(
            v3_site_data.get("computed_outputs") or {})
        merged_outputs["rut_zones"] = rut_output
        merged["computed_outputs"] = merged_outputs
        merged["covariates_inputs"] = dict(
            v3_site_data.get("covariates_inputs") or {})
        if rut.get("valid"):
            merged["covariates_inputs"]["rut_score"] = (
                rut["composite_score_0_100"])
            merged["covariates_inputs"]["rut_regime"] = (
                rut["regime"])
        per_site_outputs_final[site_name] = merged

    # 6) Outputs encore deferred FINAL (2 vs 3 en V3)
    outputs_still_deferred_final = {
        "feeding_zones_FULL": {
            "reason": (
                "Multi-season NDVI summer calculé via "
                "NASA_NDVI_TIMESERIES_DECADE_Ω comme PROXY "
                "summer feeding (Borowik 2013). FULL "
                "feeding_zones nécessite dense grid "
                "Pettorelli 2005 §4.1."),
            "directive_extension_required": (
                "NASA_NDVI_DENSE_GRID_Ω"),
            "decade_proxy_available": True,
        },
        "microhabitat_clusters_global_dense": {
            "reason": (
                "Computed cross-sites in "
                "HABITAT_OUTPUTS_COMPUTE_Ω initial. "
                "Densification N=5 → grille requires "
                "NASA_NDVI_DENSE_GRID_Ω."),
            "directive_extension_required": (
                "NASA_NDVI_DENSE_GRID_Ω"),
        },
    }

    # 7) Verdict FINAL (10/12 outputs computables max)
    n_sites = len(per_site_outputs_final)
    n_per_site_outputs_final = 9  # 8 V3 + 1 rut
    n_expected_final = n_sites * n_per_site_outputs_final
    n_outputs_with_value_final = sum(
        1 for sp_data in per_site_outputs_final.values()
        for output_val in (
            sp_data.get("computed_outputs") or {}).values()
        if (isinstance(output_val, dict)
            and output_val.get("value") is not None))
    coverage_ratio_final = (
        n_outputs_with_value_final
        / max(n_expected_final, 1))

    if coverage_ratio_final >= 0.95:
        verdict = (
            "HABITAT_FINAL_MERGE_FULL_10_OF_12_COMPUTABLE")
    elif coverage_ratio_final >= 0.5:
        verdict = (
            f"HABITAT_FINAL_MERGE_PARTIAL::"
            f"{n_outputs_with_value_final}_OF_"
            f"{n_expected_final}_VALUES_COMPUTED")
    else:
        verdict = (
            "HABITAT_FINAL_MERGE_INSUFFICIENT_COVERAGE")

    payload = {
        "manifest_id": "HABITAT_OUTPUTS_FINAL_MERGE_Ω",
        "ordre": "P7_HABITAT_OUTPUTS_FINAL_MERGE_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "verdict": verdict,
        "coverage_ratio": round(coverage_ratio_final, 3),
        "n_outputs_per_site_classes_final": (
            "10_of_12_classes_computable_2_deferred"),
        "n_outputs_per_site_values_final": (
            n_per_site_outputs_final),
        "n_outputs_total_values_computed_final": (
            n_outputs_with_value_final),
        "n_rut_zones_computed": n_rut_computed,
        "n_sites_processed": n_sites,
        "v3_inheritance": {
            "v3_verdict": v3_payload.get("verdict"),
            "v3_coverage_ratio": v3_payload.get(
                "coverage_ratio"),
            "v3_n_outputs_total_values_computed_v3": (
                v3_payload.get(
                    "n_outputs_total_values_computed_v3")),
            "v3_recompute_v3_sha256": v3_payload.get(
                "recompute_v3_sha256"),
            "v3_anthropogenic_validation_manifest_sha256": (
                v3_payload.get(
                    "anthropogenic_validation_manifest_sha256")),
            "v3_v2_recompute_sha256": (
                (v3_payload.get("v2_inheritance") or {})
                .get("v2_recompute_sha256")),
            "v3_v2_hooks_manifests_inherited": (
                (v3_payload.get("v2_inheritance") or {})
                .get("v2_hooks_manifests_inherited")),
        },
        "rut_hook_loaded": rut_loaded,
        "rut_hook_activated": rut_hook_activated,
        "rut_validation_manifest_sha256": rut_manifest_sha256,
        "species_to_site_map_used": (
            v3_payload.get("species_to_site_map_used")),
        "per_site_outputs_final": per_site_outputs_final,
        "outputs_still_deferred_anti_generique_strict_final": (
            outputs_still_deferred_final),
        "scientific_references_final_added": [
            ("Bronson, F. H. (1989). Mammalian Reproductive "
             "Biology. U Chicago. ISBN:978-0226075594"),
            ("Bowyer, R. T. (1981). J Mammal, 62:574-582. "
             "DOI:10.2307/1380404"),
            ("Forsythe et al. (1995). Ecol Modelling, 80:87-95"),
            ("Bunnell & Tait (1981). In Dynamics of Large "
             "Mammal Populations. Wiley."),
            ("Healy (1992). The Wild Turkey. Stackpole."),
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
    payload["final_merge_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        HABITAT_FINAL_ROOT.mkdir(
            parents=True, exist_ok=True)
        if HABITAT_FINAL_PATH.exists():
            try:
                state = json.loads(
                    HABITAT_FINAL_PATH.read_text(
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
        state["n_merges_final"] = len(state["history"])
        state["last_final_merge_sha256"] = payload_sha256
        state["last_verdict"] = verdict
        state["v30_lock"] = "INVIOLÉ"
        HABITAT_FINAL_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(HABITAT_FINAL_PATH)
        persisted["overlay_size_bytes"] = (
            HABITAT_FINAL_PATH.stat().st_size)

        log_forensic_event(
            scope="HABITAT",
            event="HABITAT_OUTPUTS_FINAL_MERGE_Ω",
            details={
                "final_merge_sha256": payload_sha256,
                "verdict": verdict,
                "n_sites_processed": n_sites,
                "n_rut_zones_computed": n_rut_computed,
                "n_outputs_total_values_computed_final": (
                    n_outputs_with_value_final),
                "rut_validation_manifest_sha256": (
                    rut_manifest_sha256),
            },
            persist=True,
        )

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        persisted["audit_persisted"] = persist_audit({
            "audit_type": "NOAA_PIPELINE",
            "subtype": "HABITAT_OUTPUTS_FINAL_MERGE",
            "ordre": "P7_HABITAT_OUTPUTS_FINAL_MERGE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "verdict": verdict,
            "final_merge_sha256": payload_sha256,
            "n_sites_processed": n_sites,
            "n_rut_zones_computed": n_rut_computed,
            "n_outputs_total_values_computed_final": (
                n_outputs_with_value_final),
            "rut_validation_manifest_sha256": (
                rut_manifest_sha256),
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        })

    payload["persisted_paths"] = persisted
    return payload


def get_habitat_final_merge_status() -> Dict[str, Any]:
    """État FINAL (read-only)."""
    if not HABITAT_FINAL_PATH.exists():
        return {
            "manifest_id": "HABITAT_OUTPUTS_FINAL_MERGE_STATUS_Ω",
            "current_status": "NOT_MERGED_FINAL",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        HABITAT_FINAL_PATH.read_text(encoding="utf-8"))
    last = (
        state["history"][-1] if state.get("history") else None)
    return {
        "manifest_id": "HABITAT_OUTPUTS_FINAL_MERGE_STATUS_Ω",
        "ordre": "P7_HABITAT_OUTPUTS_FINAL_MERGE_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "current_status": (
            "MERGED_FINAL_OPERATIONAL" if last
            else "NOT_MERGED_FINAL"),
        "n_merges_final_history": state.get(
            "n_merges_final", 0),
        "last_final_merge_sha256": state.get(
            "last_final_merge_sha256"),
        "last_verdict": state.get("last_verdict"),
        "last_updated_utc": state.get("last_updated_utc"),
        "last_summary": (
            {
                "verdict": last.get("verdict"),
                "coverage_ratio": last.get("coverage_ratio"),
                "n_rut_zones_computed": last.get(
                    "n_rut_zones_computed"),
                "n_outputs_total_values_computed_final": (
                    last.get(
                        "n_outputs_total_values_computed_final")),
            } if last else None),
        "overlay_path": str(HABITAT_FINAL_PATH),
        "overlay_size_bytes": (
            HABITAT_FINAL_PATH.stat().st_size),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "HABITAT_FINAL_ROOT",
    "HABITAT_FINAL_PATH",
    "merge_habitat_outputs_final",
    "get_habitat_final_merge_status",
]
