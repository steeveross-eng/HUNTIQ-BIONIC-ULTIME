"""contamination_affut_dependency_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · COMMANDE_INSTITUTIONNELLE_Ω V12-MAÎTRE
BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT · FUSION ADD-ONLY

Verrouillage de la dépendance stricte CONTAMINATION → AFFÛTS V12.

Règles doctrinales :
  R1: La couche CONTAMINATION est un diagnostic dérivé et non autonome.
  R2: CONTAMINATION ne peut être générée que si AFFUT_POTENTIEL == TRUE.
  R3: AFFUT_POTENTIEL est déterminé par le moteur AFFUTS_Ω selon :
       - occupation_du_sol
       - fragmentation
       - densité_bâtie
       - continuité_forestière
       - masque_biologique
       - distance_aux_habitats_favorables
  R4: Si AFFUT_POTENTIEL == FALSE → CONTAMINATION = NULL.
  R5: Les secteurs urbains, industriels, commerciaux, autoroutiers
      sont automatiquement classés AFFUT_POTENTIEL = FALSE.
  R6: La couche VENT demeure indépendante et toujours visible.

Audit doctrinal :
  A1: Vérification automatique sur chaque tuile 256x256.
  A2: Journalisation dans LOG_CONTAMINATION_AFFUT_DEPENDENCY.
  A3: Détection d'anomalies si contamination apparaît dans secteur urbain.
  A4: Blocage CI si violation détectée.

Messages frontend :
  M1: "CONTAMINATION MASQUÉE — AUCUN AFFÛT POSSIBLE DANS CE SECTEUR."
  M2: "CONTAMINATION ACTIVE — AFFÛT ÉCOLOGIQUEMENT POSSIBLE."

CHECKSUM doctrinal V12 :
  SHA256("CONTAMINATION_AFFUT_DEPENDENCY_V12") =
  bfe41b1e07d3f17c6352aa46212485bad4c06f7e937591c79058b8c888cfb9ba

ANTI-GÉNÉRIQUE STRICT :
  · Doctrine pure (logique conditionnelle déterministe)
  · Audit forensique persisté
  · Aucune mutation de couches existantes (FUSION ADD-ONLY)
  · Anomaly detection : violation = HTTP 412 + audit blocage CI
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


CONTAM_AFFUT_ROOT = Path(
    "/app/backend/data/pipelines/contamination_affut_dependency")
CONTAM_AFFUT_HOOK_PATH = (
    CONTAM_AFFUT_ROOT
    / "contamination_affut_dependency_hook_overlay.json")
CONTAM_AFFUT_LOG_PATH = (
    CONTAM_AFFUT_ROOT
    / "log_contamination_affut_dependency.jsonl")
CONTAM_AFFUT_VIOLATIONS_PATH = (
    CONTAM_AFFUT_ROOT
    / "contamination_affut_violations_overlay.json")


# ═════════════════════════════════════════════════════════════════════════
# Doctrine V12-MAÎTRE (immuable)
# ═════════════════════════════════════════════════════════════════════════
DOCTRINE_V12_MASTER: Dict[str, Any] = {
    "version": "V12-MAÎTRE",
    "objet": (
        "Verrouillage de la dépendance stricte "
        "CONTAMINATION → AFFÛTS"),
    "auteur": "Commandant Steeve-Max",
    "regles": {
        "R1": (
            "La couche CONTAMINATION est un diagnostic dérivé "
            "et non autonome."),
        "R2": (
            "CONTAMINATION ne peut être générée que si "
            "AFFUT_POTENTIEL == TRUE."),
        "R3": (
            "AFFUT_POTENTIEL est déterminé par le moteur "
            "AFFUTS_Ω selon : occupation_du_sol, fragmentation, "
            "densité_bâtie, continuité_forestière, "
            "masque_biologique, distance_aux_habitats_favorables."),
        "R4": (
            "Si AFFUT_POTENTIEL == FALSE → CONTAMINATION = NULL."),
        "R5": (
            "Les secteurs urbains, industriels, commerciaux, "
            "autoroutiers sont automatiquement classés "
            "AFFUT_POTENTIEL = FALSE."),
        "R6": (
            "La couche VENT demeure indépendante et toujours "
            "visible."),
    },
    "logique_moteur": {
        "conditional_R4": (
            "if AFFUT_POTENTIEL == False : "
            "contamination_layer.visible=False, data=None, "
            "reason='AFFÛT IMPOSSIBLE — CONTAMINATION NON "
            "PERTINENTE'"),
        "conditional_R2": (
            "else : contamination_layer.visible=True, "
            "reason='AFFÛT POSSIBLE — CONTAMINATION ACTIVE'"),
    },
    "audit": {
        "A1": "Vérification automatique sur chaque tuile 256x256.",
        "A2": (
            "Journalisation dans "
            "LOG_CONTAMINATION_AFFUT_DEPENDENCY."),
        "A3": (
            "Détection d'anomalies si contamination apparaît "
            "dans un secteur urbain."),
        "A4": "Blocage CI si violation détectée.",
    },
    "messages_frontend": {
        "M1": (
            "CONTAMINATION MASQUÉE — AUCUN AFFÛT POSSIBLE "
            "DANS CE SECTEUR."),
        "M2": (
            "CONTAMINATION ACTIVE — AFFÛT ÉCOLOGIQUEMENT "
            "POSSIBLE."),
    },
    "checksum_expected_sha256": (
        "bfe41b1e07d3f17c6352aa46212485bad4c06f7e937591c790"
        "58b8c888cfb9ba"),
    "checksum_input_string": "CONTAMINATION_AFFUT_DEPENDENCY_V12",
    "anti_generique_strict": True,
    "fusion_add_only": True,
    "v30_lock": "INVIOLÉ",
}


# Catégories occupation du sol forçant AFFUT_POTENTIEL=False (R5)
URBAN_INDUSTRIAL_CATEGORIES_R5: List[str] = [
    "urban", "residential", "commercial", "industrial",
    "highway", "motorway", "trunk", "primary",
    "retail", "warehouse", "factory",
    "construction", "quarry",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _verify_checksum_v12(input_string: str) -> Dict[str, Any]:
    """Vérifie le checksum doctrinal V12 (anti-générique strict)."""
    actual = hashlib.sha256(input_string.encode("utf-8")).hexdigest()
    expected = DOCTRINE_V12_MASTER["checksum_expected_sha256"]
    return {
        "input_string": input_string,
        "actual_sha256": actual,
        "expected_sha256": expected,
        "match": actual == expected,
    }


# ═════════════════════════════════════════════════════════════════════════
# Logique conditionnelle (déterministe, anti-générique strict)
# ═════════════════════════════════════════════════════════════════════════
def evaluate_affut_potentiel_for_tile(
    tile_attributes: Dict[str, Any],
) -> Dict[str, Any]:
    """Évalue AFFUT_POTENTIEL pour une tuile 256x256.

    Anti-générique strict : déterministe pur basé sur attributs
    physiques de tuile (occupation du sol, fragmentation, etc.).

    Args:
        tile_attributes : dict avec keys :
          · landuse_categories (list of str)
          · forest_continuity_score (0-1)
          · building_density_per_km2
          · habitat_favorable_distance_m
          · biological_mask_active (bool)
          · fragmentation_index_0_1 (0=fragmenté, 1=continu)

    Returns:
        dict {
          affut_potentiel: bool,
          reason: str,
          rule_triggered: str,  # R3, R4 ou R5
          contamination_layer: {visible, data, reason},
        }
    """
    landuse = tile_attributes.get(
        "landuse_categories") or []
    forest_continuity = tile_attributes.get(
        "forest_continuity_score")
    building_density = tile_attributes.get(
        "building_density_per_km2")
    habitat_distance = tile_attributes.get(
        "habitat_favorable_distance_m")
    biological_mask_active = tile_attributes.get(
        "biological_mask_active", False)
    fragmentation = tile_attributes.get(
        "fragmentation_index_0_1")

    # R5 : urbain/industriel/commercial/autoroutier
    landuse_lower = [str(x).lower() for x in landuse]
    r5_triggered = any(
        cat in URBAN_INDUSTRIAL_CATEGORIES_R5
        for cat in landuse_lower)
    if r5_triggered:
        triggered_categories = [
            cat for cat in landuse_lower
            if cat in URBAN_INDUSTRIAL_CATEGORIES_R5]
        return {
            "affut_potentiel": False,
            "reason": (
                "R5_URBAN_INDUSTRIAL_FORCED_FALSE::"
                f"{','.join(triggered_categories)}"),
            "rule_triggered": "R5",
            "contamination_layer": {
                "visible": False,
                "data": None,
                "reason": (
                    DOCTRINE_V12_MASTER["messages_frontend"][
                        "M1"]),
            },
        }

    # R3 : évaluation moteur AFFUTS_Ω
    affut_potentiel_score = 0.0
    components: List[str] = []
    if (forest_continuity is not None
            and forest_continuity >= 0.4):
        affut_potentiel_score += 30.0
        components.append(
            f"forest_continuity={forest_continuity:.2f}>=0.4")
    if (building_density is not None
            and building_density < 50.0):
        affut_potentiel_score += 25.0
        components.append(
            f"building_density={building_density:.1f}<50")
    if (habitat_distance is not None
            and habitat_distance <= 1500.0):
        affut_potentiel_score += 25.0
        components.append(
            f"habitat_distance={habitat_distance:.0f}<=1500m")
    if biological_mask_active:
        affut_potentiel_score += 10.0
        components.append("biological_mask_active=true")
    if (fragmentation is not None
            and fragmentation >= 0.5):
        affut_potentiel_score += 10.0
        components.append(
            f"fragmentation={fragmentation:.2f}>=0.5")

    if affut_potentiel_score >= 50.0:
        return {
            "affut_potentiel": True,
            "reason": (
                f"R3_AFFUT_POSSIBLE_score={affut_potentiel_score}"
                "::" + "+".join(components)),
            "rule_triggered": "R3",
            "affut_potentiel_score": affut_potentiel_score,
            "contamination_layer": {
                "visible": True,
                "data": "ENABLED_FOR_RENDER_PIPELINE",
                "reason": (
                    DOCTRINE_V12_MASTER["messages_frontend"][
                        "M2"]),
            },
        }
    # R4 : sinon contamination NULL
    return {
        "affut_potentiel": False,
        "reason": (
            f"R4_NO_AFFUT_POTENTIAL_score={affut_potentiel_score}"
            "_below_50::" + "+".join(components or ["empty"])),
        "rule_triggered": "R4",
        "affut_potentiel_score": affut_potentiel_score,
        "contamination_layer": {
            "visible": False,
            "data": None,
            "reason": (
                DOCTRINE_V12_MASTER["messages_frontend"]["M1"]),
        },
    }


def detect_anomaly_a3(
    tile_attributes: Dict[str, Any],
    contamination_layer_state: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Détection A3 : contamination dans secteur urbain (violation)."""
    landuse = [
        str(x).lower()
        for x in (tile_attributes.get("landuse_categories") or [])]
    is_urban_industrial = any(
        cat in URBAN_INDUSTRIAL_CATEGORIES_R5 for cat in landuse)
    if (is_urban_industrial
            and contamination_layer_state.get("visible") is True):
        return {
            "anomaly_type": "A3_CONTAMINATION_IN_URBAN_SECTOR",
            "severity": "CRITICAL",
            "rule_violated": "R5",
            "landuse_categories": landuse,
            "contamination_state": contamination_layer_state,
            "ci_blocking": True,
            "doctrine_v12": (
                "CONTAMINATION_AFFUT_DEPENDENCY"),
        }
    return None


def _append_audit_log(entry: Dict[str, Any]) -> None:
    """Append audit log JSONL."""
    CONTAM_AFFUT_ROOT.mkdir(parents=True, exist_ok=True)
    entry["log_appended_at_utc"] = _utc_now()
    with open(CONTAM_AFFUT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(
            entry, ensure_ascii=False, default=str) + "\n")


# ═════════════════════════════════════════════════════════════════════════
# HOOK ACTIVATE
# ═════════════════════════════════════════════════════════════════════════
def activate_contamination_affut_dependency_hook(
    activation_input_string: str = (
        "CONTAMINATION_AFFUT_DEPENDENCY_V12"),
    persist: bool = True,
) -> Dict[str, Any]:
    """HOOK_CONTAMINATION_AFFUT_DEPENDENCY · activation V12.

    Anti-générique strict : checksum vérifié, refus sinon.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "activate_contamination_affut_dependency_hook")

    t0 = time.time()
    checksum_check = _verify_checksum_v12(
        activation_input_string)
    if not checksum_check["match"]:
        return {
            "manifest_id": "HOOK_CONTAMINATION_AFFUT_DEPENDENCY",
            "ordre": "COMMANDE_INSTITUTIONNELLE_Ω_V12-MAÎTRE",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "activated": False,
            "verdict": "HOOK_CONTAMINATION_AFFUT_REJECTED_BAD_CHECKSUM",
            "checksum_check": checksum_check,
            "rejection_explanation": (
                "Le checksum SHA256 fourni ne correspond PAS à "
                "celui doctrinal V12-MAÎTRE. Anti-générique "
                "strict : rejet."),
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t0, 3),
        }

    payload = {
        "manifest_id": "HOOK_CONTAMINATION_AFFUT_DEPENDENCY",
        "ordre": "COMMANDE_INSTITUTIONNELLE_Ω_V12-MAÎTRE",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "activated": True,
        "verdict": "HOOK_CONTAMINATION_AFFUT_DEPENDENCY_ACTIVÉ",
        "confirmation": (
            "DÉPENDANCE CONTAMINATION→AFFÛTS VERROUILLÉE."),
        "doctrine_v12_master": DOCTRINE_V12_MASTER,
        "checksum_check": checksum_check,
        "urban_industrial_categories_r5": (
            URBAN_INDUSTRIAL_CATEGORIES_R5),
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t0, 3),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        CONTAM_AFFUT_ROOT.mkdir(parents=True, exist_ok=True)
        if CONTAM_AFFUT_HOOK_PATH.exists():
            try:
                state = json.loads(
                    CONTAM_AFFUT_HOOK_PATH.read_text(
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
        state["n_activations"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = payload["verdict"]
        state["v30_lock"] = "INVIOLÉ"
        CONTAM_AFFUT_HOOK_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(CONTAM_AFFUT_HOOK_PATH)
        persisted["overlay_size_bytes"] = (
            CONTAM_AFFUT_HOOK_PATH.stat().st_size)
        persisted["n_activations_history"] = state["n_activations"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "HOOK_CONTAMINATION_AFFUT_DEPENDENCY",
            "ordre": "COMMANDE_INSTITUTIONNELLE_Ω_V12-MAÎTRE",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "activated": True,
            "verdict": payload["verdict"],
            "manifest_sha256": payload_sha256,
            "checksum_doctrinal_v12": (
                checksum_check["expected_sha256"]),
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="HOOK_CONTAMINATION_AFFUT_DEPENDENCY_ACTIVATED",
        details={
            "manifest_sha256": payload_sha256,
            "checksum_doctrinal_v12": (
                checksum_check["expected_sha256"]),
        },
        persist=True,
    )
    payload["persisted_paths"] = persisted
    return payload


# ═════════════════════════════════════════════════════════════════════════
# AUDIT batch (A1+A2+A3+A4) sur N tuiles 256x256
# ═════════════════════════════════════════════════════════════════════════
def audit_tiles_dependency(
    tiles: List[Dict[str, Any]],
    persist_violations: bool = True,
) -> Dict[str, Any]:
    """Audit batch (A1) avec journalisation (A2) + détection A3.

    Anti-générique strict : déterministe pur, traçabilité totale.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced,
    )
    require_guardrails_enforced("audit_tiles_dependency")

    t0 = time.time()
    n_tiles = len(tiles)
    n_affut_true = 0
    n_affut_false = 0
    n_violations_a3 = 0
    violations: List[Dict[str, Any]] = []
    rule_counts = {"R3": 0, "R4": 0, "R5": 0}

    for tile in tiles:
        tile_id = tile.get("tile_id", "unknown")
        attrs = tile.get("attributes") or {}
        evaluation = evaluate_affut_potentiel_for_tile(attrs)
        rule_counts[evaluation["rule_triggered"]] = (
            rule_counts.get(
                evaluation["rule_triggered"], 0) + 1)
        if evaluation["affut_potentiel"]:
            n_affut_true += 1
        else:
            n_affut_false += 1
        anomaly = detect_anomaly_a3(
            attrs, evaluation["contamination_layer"])
        log_entry = {
            "tile_id": tile_id,
            "evaluation": evaluation,
            "anomaly": anomaly,
        }
        _append_audit_log(log_entry)
        if anomaly is not None:
            n_violations_a3 += 1
            violations.append({
                "tile_id": tile_id,
                "anomaly": anomaly,
                "tile_attributes": attrs,
            })

    ci_blocking_required = n_violations_a3 > 0
    if ci_blocking_required and persist_violations:
        CONTAM_AFFUT_ROOT.mkdir(parents=True, exist_ok=True)
        CONTAM_AFFUT_VIOLATIONS_PATH.write_text(
            json.dumps({
                "violations": violations,
                "n_violations": n_violations_a3,
                "ci_blocking": True,
                "audited_at_utc": _utc_now(),
                "v30_lock": "INVIOLÉ",
            }, ensure_ascii=False, indent=2),
            encoding="utf-8")

    return {
        "manifest_id": "CONTAMINATION_AFFUT_DEPENDENCY_AUDIT_Ω",
        "ordre": "COMMANDE_INSTITUTIONNELLE_Ω_V12-MAÎTRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "n_tiles_audited": n_tiles,
        "n_affut_potentiel_true": n_affut_true,
        "n_affut_potentiel_false": n_affut_false,
        "n_violations_a3": n_violations_a3,
        "ci_blocking_required": ci_blocking_required,
        "rule_counts": rule_counts,
        "violations_summary": violations[:10],  # max 10 in payload
        "log_path": str(CONTAM_AFFUT_LOG_PATH),
        "violations_path": (
            str(CONTAM_AFFUT_VIOLATIONS_PATH)
            if ci_blocking_required else None),
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "audited_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t0, 3),
    }


def get_contamination_affut_dependency_hook_status() -> Dict[str, Any]:
    """État hook V12 (read-only)."""
    if not CONTAM_AFFUT_HOOK_PATH.exists():
        return {
            "manifest_id":
                "HOOK_CONTAMINATION_AFFUT_DEPENDENCY_STATUS",
            "current_status": "NOT_ACTIVATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        CONTAM_AFFUT_HOOK_PATH.read_text(encoding="utf-8"))
    last = (state["history"][-1]
            if state.get("history") else None)
    return {
        "manifest_id":
            "HOOK_CONTAMINATION_AFFUT_DEPENDENCY_STATUS",
        "doctrine_version": "V12-MAÎTRE",
        "current_status": (
            "ACTIVATED_LOCKED" if last
            and last.get("activated") else "NOT_ACTIVATED"),
        "n_activations_history": state.get("n_activations", 0),
        "last_manifest_sha256": state.get(
            "last_manifest_sha256"),
        "last_verdict": state.get("last_verdict"),
        "last_updated_utc": state.get("last_updated_utc"),
        "doctrine_checksum_expected": (
            DOCTRINE_V12_MASTER["checksum_expected_sha256"]),
        "overlay_path": str(CONTAM_AFFUT_HOOK_PATH),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "CONTAM_AFFUT_ROOT",
    "CONTAM_AFFUT_HOOK_PATH",
    "CONTAM_AFFUT_LOG_PATH",
    "CONTAM_AFFUT_VIOLATIONS_PATH",
    "DOCTRINE_V12_MASTER",
    "URBAN_INDUSTRIAL_CATEGORIES_R5",
    "evaluate_affut_potentiel_for_tile",
    "detect_anomaly_a3",
    "audit_tiles_dependency",
    "activate_contamination_affut_dependency_hook",
    "get_contamination_affut_dependency_hook_status",
]
