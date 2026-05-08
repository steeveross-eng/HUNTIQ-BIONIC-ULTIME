"""habitat_outputs_recompute_v3_omega.py — RECOMPUTE_Ω_ULTIME_V3
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

V3 — Greffe pressure_sensitive_zones (Frid & Dill 2002 + Naidoo 2010
+ Tucker 2018) au-dessus du recompute V2 SANS modification du V2 (FUSION
ADD-ONLY strict, V30_LOCK inviolate).

NOUVEAUX OUTPUTS DÉBLOQUÉS V3 (vs V2) :
  · pressure_sensitive_zones (composite OSM + WorldPop)

OUTPUTS DEFERRED V3 (3 restants vs 4 en V2) :
  · rut_zones (PIÈGE TEMPOREL: NDVI Jan-Mar ≠ saisons rut)
  · feeding_zones (require multi-season + dense grid → cf. NDVI_DECADE)
  · microhabitat_clusters_global_dense (require N>5 grille)

DOCTRINE :
  · V3 LIT V2 + ANTHROPOGENIC_PRESSURE overlays (pas de recalcul V2)
  · Pressure intégré per-site uniquement si VALIDATE manifest valide
  · Verdict atteint 9/12 si tous les hooks chargés
  · Manifest SHA-256 ancré, audit persisté

RÉFÉRENCES PEER-REVIEWED :
  [1] Frid & Dill (2002). Conservation Ecology, 6(1):11.
      (Disturbance as predation risk)
  [2] Naidoo & Burton (2010). Conservation Letters, 3:431-440.
      DOI:10.1111/j.1755-263X.2010.00138.x
  [3] Tucker et al. (2018). Science, 359:466-469.
      DOI:10.1126/science.aam9712 (Human Footprint mammal movement)
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


HABITAT_RECOMPUTE_V3_ROOT = Path(
    "/app/backend/data/pipelines/habitat_recompute_v3")
HABITAT_RECOMPUTE_V3_PATH = (
    HABITAT_RECOMPUTE_V3_ROOT
    / "habitat_outputs_recompute_v3_overlay.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _extract_pressure_per_site(
    anthro_validation: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """Extrait composite_index_0_100 + classification per site BP135."""
    out: Dict[str, Dict[str, Any]] = {}
    for site_name, site_data in (
            anthro_validation.get("site_results") or {}).items():
        composite = site_data.get("composite_index") or {}
        zone_class = (
            site_data.get(
                "pressure_sensitive_zone_classification")
            or {})
        if composite.get("valid"):
            out[site_name] = {
                "valid": True,
                "composite_index_0_100": composite.get(
                    "composite_index_0_100"),
                "components": composite.get("components"),
                "raw_inputs": composite.get("raw_inputs"),
                "regime": zone_class.get("regime"),
                "is_pressure_sensitive": zone_class.get(
                    "is_pressure_sensitive"),
            }
        else:
            out[site_name] = {
                "valid": False,
                "reason": composite.get(
                    "reason", "composite_invalid"),
            }
    return out


def _compute_pressure_sensitive_zones_output(
    pressure_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Construit output pressure_sensitive_zones (Frid & Dill 2002).

    Anti-générique strict :
      · DEFERRED si données invalides (pas d'imputation)
      · regime + score + components forensic
    """
    if not pressure_data.get("valid"):
        return {
            "value": None,
            "regime": "DEFERRED_NO_VALID_PRESSURE_DATA",
            "reason": pressure_data.get("reason"),
            "primary_reference": "Frid_Dill_2002_ConservationEcology",
        }
    score = pressure_data["composite_index_0_100"]
    regime = pressure_data["regime"]
    is_sensitive = pressure_data["is_pressure_sensitive"]
    components = pressure_data["components"]
    raw = pressure_data["raw_inputs"]
    return {
        "value": score,
        "unit": "anthropogenic_pressure_index_0_100",
        "regime": regime,
        "is_pressure_sensitive": is_sensitive,
        "doctrinal_caveat": (
            "Score composite Naidoo & Burton 2010 (40% routes + "
            "30% population + 20% bâtiments + 10% landuse). "
            "Sensible >= 50 (caution), >= 75 (avoid). "
            "Refuge anthropique < 25."),
        "components": components,
        "raw_inputs": raw,
        "primary_references": [
            "Frid_Dill_2002_ConservationEcology",
            "Naidoo_Burton_2010_ConservationLetters",
            "Tucker_2018_Science",
        ],
    }


def recompute_habitat_outputs_with_anthropogenic_pressure_v3(
    species_to_site_map: Optional[Dict[str, str]] = None,
    persist: bool = True,
    require_anthropogenic_hook_active: bool = True,
) -> Dict[str, Any]:
    """RECOMPUTE_Ω_ULTIME_V3 · greffe pressure_sensitive_zones sur V2.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412)
      2. Recompute V2 (orchestrateur 5 hooks principaux)
      3. Charge ANTHRO_VALIDATION_PATH (lecture seule, pas de mutation)
      4. Pour chaque site V2, greffe pressure_sensitive_zones
      5. Verdict 9_OF_12 si tous les hooks chargés
      6. Persist V3 overlay + audit
      7. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO + FUSION ADD-ONLY
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        recompute_habitat_outputs_with_all_hooks,
    )
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        ANTHRO_VALIDATION_PATH,
        ANTHRO_HOOK_ACTIVATION_PATH,
        get_last_validated_pressure_per_site,
    )
    require_guardrails_enforced(
        "recompute_habitat_outputs_with_anthropogenic_pressure_v3")

    t_total = time.time()

    # 1) Recompute V2 (FUSION ADD-ONLY : pas de mutation V2)
    v2_payload = recompute_habitat_outputs_with_all_hooks(
        species_to_site_map=species_to_site_map,
        persist=False,  # V3 persiste son propre overlay
    )

    # 2) Charge ANTHRO validation (read-only)
    anthro_v = get_last_validated_pressure_per_site()
    anthro_loaded = anthro_v is not None
    anthro_manifest_sha256 = (
        (anthro_v or {}).get("manifest_sha256"))

    # 3) Vérifier l'activation du hook (anti-générique strict)
    anthro_hook_activated = False
    if ANTHRO_HOOK_ACTIVATION_PATH.exists():
        try:
            state = json.loads(
                ANTHRO_HOOK_ACTIVATION_PATH.read_text(
                    encoding="utf-8"))
            history = state.get("history", [])
            if history and history[-1].get("activated"):
                anthro_hook_activated = True
        except json.JSONDecodeError:
            anthro_hook_activated = False

    if (require_anthropogenic_hook_active
            and not anthro_hook_activated):
        return {
            "manifest_id":
                "HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
            "ordre":
                "P5_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "verdict": (
                "HABITAT_OUTPUTS_RECOMPUTE_V3_REJECTED_"
                "ANTHROPOGENIC_HOOK_NOT_ACTIVATED"),
            "rejection_explanation": (
                "Anti-générique strict : pressure_sensitive_zones "
                "ne peut être calculé que si "
                "ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_Ω a été "
                "exécuté avec succès. Aucune greffe sur V2."),
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t_total, 3),
        }

    # 4) Extraction pressure per site
    pressure_per_site: Dict[str, Dict[str, Any]] = (
        _extract_pressure_per_site(anthro_v) if anthro_v else {})

    # 5) Greffe per site (FUSION ADD-ONLY V3)
    per_site_outputs_v3: Dict[str, Dict[str, Any]] = {}
    n_pressure_computed = 0
    for site_name, v2_site_data in (
            v2_payload.get("per_site_outputs") or {}).items():
        pressure = pressure_per_site.get(site_name) or {
            "valid": False,
            "reason": "site_missing_in_anthropogenic_validation",
        }
        pressure_output = (
            _compute_pressure_sensitive_zones_output(pressure))
        if pressure_output.get("value") is not None:
            n_pressure_computed += 1
        # Build new structure (PAS de mutation v2_site_data)
        merged = dict(v2_site_data)
        merged_outputs = dict(
            v2_site_data.get("computed_outputs") or {})
        merged_outputs["pressure_sensitive_zones"] = (
            pressure_output)
        merged["computed_outputs"] = merged_outputs
        merged["covariates_inputs"] = dict(
            v2_site_data.get("covariates_inputs") or {})
        if pressure.get("valid"):
            merged["covariates_inputs"][
                "anthropogenic_pressure_score"] = (
                pressure["composite_index_0_100"])
            merged["covariates_inputs"][
                "anthropogenic_pressure_regime"] = (
                pressure["regime"])
        per_site_outputs_v3[site_name] = merged

    # 6) Outputs encore deferred (V3 : 3 vs 4 en V2)
    outputs_still_deferred_v3 = {
        "rut_zones": {
            "reason": (
                "PIÈGE TEMPOREL inchangé : NDVI Jan-Mar ≠ "
                "saisons rut espèces (cerf=oct-nov, etc.)"),
            "directive_extension_required": (
                "TEMPORAL_RUT_DATA_HOOK_ACTIVATE"),
        },
        "feeding_zones": {
            "reason": (
                "Multi-season NDVI calculé via "
                "NASA_NDVI_TIMESERIES_DECADE_Ω comme PROXY "
                "summer feeding. FULL feeding_zones nécessite "
                "dense grid Pettorelli 2005 §4.1."),
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

    # 7) Verdict V3
    n_sites = len(per_site_outputs_v3)
    n_per_site_outputs_v3 = 8  # 7 V2 + 1 pressure_sensitive_zones
    n_expected_v3 = n_sites * n_per_site_outputs_v3
    n_outputs_with_value_v3 = sum(
        1 for sp_data in per_site_outputs_v3.values()
        for output_val in (
            sp_data.get("computed_outputs") or {}).values()
        if (isinstance(output_val, dict)
            and output_val.get("value") is not None))
    coverage_ratio_v3 = (
        n_outputs_with_value_v3 / max(n_expected_v3, 1))

    if coverage_ratio_v3 >= 0.95:
        verdict = (
            "HABITAT_OUTPUTS_RECOMPUTE_V3_FULL_9_OF_12_COMPUTABLE")
    elif coverage_ratio_v3 >= 0.5:
        verdict = (
            f"HABITAT_OUTPUTS_RECOMPUTE_V3_PARTIAL::"
            f"{n_outputs_with_value_v3}_OF_"
            f"{n_expected_v3}_VALUES_COMPUTED")
    else:
        verdict = (
            "HABITAT_OUTPUTS_RECOMPUTE_V3_INSUFFICIENT_COVERAGE")

    payload = {
        "manifest_id": "HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
        "ordre": "P5_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "verdict": verdict,
        "coverage_ratio": round(coverage_ratio_v3, 3),
        "n_outputs_per_site_classes_v3": (
            "9_of_12_classes_computable_3_deferred"),
        "n_outputs_per_site_values_v3": n_per_site_outputs_v3,
        "n_outputs_total_values_computed_v3": (
            n_outputs_with_value_v3),
        "n_pressure_sensitive_zones_computed": (
            n_pressure_computed),
        "n_sites_processed": n_sites,
        "v2_inheritance": {
            "v2_verdict": v2_payload.get("verdict"),
            "v2_coverage_ratio": v2_payload.get(
                "coverage_ratio"),
            "v2_n_outputs_total_values_computed": (
                v2_payload.get(
                    "n_outputs_total_values_computed")),
            "v2_recompute_sha256": v2_payload.get(
                "recompute_sha256"),
            "v2_hooks_manifests_inherited": v2_payload.get(
                "hooks_manifests_inherited"),
        },
        "anthropogenic_hook_loaded": anthro_loaded,
        "anthropogenic_hook_activated": (
            anthro_hook_activated),
        "anthropogenic_validation_manifest_sha256": (
            anthro_manifest_sha256),
        "species_to_site_map_used": (
            v2_payload.get("species_to_site_map_used")),
        "per_site_outputs_v3": per_site_outputs_v3,
        "corridor_continuity_inter_sites_v2": (
            v2_payload.get("corridor_continuity_inter_sites")),
        "outputs_still_deferred_anti_generique_strict_v3": (
            outputs_still_deferred_v3),
        "scientific_references_v3_added": [
            ("Frid & Dill (2002). Conservation Ecology, "
             "6(1):11."),
            ("Naidoo & Burton (2010). Conservation Letters, "
             "3:431-440. "
             "DOI:10.1111/j.1755-263X.2010.00138.x"),
            ("Tucker et al. (2018). Science, 359:466-469. "
             "DOI:10.1126/science.aam9712"),
            ("Haklay (2010). Env & Planning B, 37:682-703."),
            ("Tatem (2017). Scientific Data, 4:170004."),
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
    payload["recompute_v3_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        HABITAT_RECOMPUTE_V3_ROOT.mkdir(
            parents=True, exist_ok=True)
        if HABITAT_RECOMPUTE_V3_PATH.exists():
            try:
                state = json.loads(
                    HABITAT_RECOMPUTE_V3_PATH.read_text(
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
        state["n_recomputations_v3"] = len(state["history"])
        state["last_recompute_v3_sha256"] = payload_sha256
        state["last_verdict"] = verdict
        state["v30_lock"] = "INVIOLÉ"
        HABITAT_RECOMPUTE_V3_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            HABITAT_RECOMPUTE_V3_PATH)
        persisted["overlay_size_bytes"] = (
            HABITAT_RECOMPUTE_V3_PATH.stat().st_size)
        persisted["n_recomputations_v3_history"] = state[
            "n_recomputations_v3"]

        log_forensic_event(
            scope="HABITAT",
            event="HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
            details={
                "recompute_v3_sha256": payload_sha256,
                "verdict": verdict,
                "n_sites_processed": n_sites,
                "n_pressure_sensitive_zones_computed": (
                    n_pressure_computed),
                "n_outputs_total_values_computed_v3": (
                    n_outputs_with_value_v3),
                "anthropogenic_validation_manifest_sha256": (
                    anthro_manifest_sha256),
            },
            persist=True,
        )

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "HABITAT_OUTPUTS_RECOMPUTE_V3",
            "ordre":
                "P5_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "verdict": verdict,
            "recompute_v3_sha256": payload_sha256,
            "n_sites_processed": n_sites,
            "n_pressure_sensitive_zones_computed": (
                n_pressure_computed),
            "n_outputs_total_values_computed_v3": (
                n_outputs_with_value_v3),
            "anthropogenic_validation_manifest_sha256": (
                anthro_manifest_sha256),
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(
            audit_payload)

    payload["persisted_paths"] = persisted
    return payload


def get_habitat_recompute_v3_status() -> Dict[str, Any]:
    """État actuel du V3 (read-only)."""
    if not HABITAT_RECOMPUTE_V3_PATH.exists():
        return {
            "manifest_id":
                "HABITAT_OUTPUTS_RECOMPUTE_V3_STATUS_Ω",
            "ordre":
                "P5_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
            "current_status": "NOT_RECOMPUTED_V3",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        HABITAT_RECOMPUTE_V3_PATH.read_text(encoding="utf-8"))
    last = (
        state["history"][-1] if state.get("history") else None)
    return {
        "manifest_id":
            "HABITAT_OUTPUTS_RECOMPUTE_V3_STATUS_Ω",
        "ordre":
            "P5_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "current_status": (
            "RECOMPUTED_V3_OPERATIONAL" if last
            else "NOT_RECOMPUTED_V3"),
        "n_recomputations_v3_history": state.get(
            "n_recomputations_v3", 0),
        "last_recompute_v3_sha256": state.get(
            "last_recompute_v3_sha256"),
        "last_verdict": state.get("last_verdict"),
        "last_updated_utc": state.get("last_updated_utc"),
        "last_summary": (
            {
                "verdict": last.get("verdict"),
                "coverage_ratio": last.get("coverage_ratio"),
                "n_pressure_sensitive_zones_computed": (
                    last.get(
                        "n_pressure_sensitive_zones_computed")),
                "n_outputs_total_values_computed_v3": (
                    last.get(
                        "n_outputs_total_values_computed_v3")),
            } if last else None),
        "overlay_path": str(HABITAT_RECOMPUTE_V3_PATH),
        "overlay_size_bytes": (
            HABITAT_RECOMPUTE_V3_PATH.stat().st_size),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "HABITAT_RECOMPUTE_V3_ROOT",
    "HABITAT_RECOMPUTE_V3_PATH",
    "recompute_habitat_outputs_with_anthropogenic_pressure_v3",
    "get_habitat_recompute_v3_status",
]
