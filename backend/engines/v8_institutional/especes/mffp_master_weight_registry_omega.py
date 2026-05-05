"""
mffp_master_weight_registry_omega.py — ORDRE N°52-R9
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · AMPLIFICATION MFFP×1000

Registre institutionnel de pondération MFFP-MASTER pour les moteurs
TERRITOIRE et BIONIC. Définit la doctrine d'amplification :

  WEIGHT_MFFP        = 1.0   (couche MAÎTRESSE · pondération 80% scores)
  WEIGHT_ALL_OTHER   = 0.1   (couches secondaires · 20% pondération)
  score_final = (score_original * 0.2) + (score_MFFP * 0.8)

Ordre R9 cibles de recalcul :
  · corridors, hotspots, affuts, salines
  · zones_vitales, zones_passage, zones_rut, zones_repos, zones_alimentation

Moteurs cibles à `mffp_as_primary_input=True` :
  · engine_corridors_gis_omega
  · engine_chevreuil_omega · engine_orignal_omega · engine_ours_noir_omega
  · engine_dindon_omega · engine_wapiti_omega
  · engine_habitat_omega · engine_vegetation_omega · engine_phenologie_omega
  · engine_calibration_dynamique_omega
  · engine_corridors_vitaux (route corridors_vitaux_router)
  · engine_ecological_orchestrator
  · engine_supra_advanced

ANTI_GÉNÉRIQUE_STRICT :
  Les recalculs effectifs (score_MFFP) nécessitent les couches dérivées
  produites par PHASE_3 du R8 (`GIS_STRUCTURE_FORESTIERE.tif`,
  `GIS_ESSENCES_DOMINANTES.tif`, `GIS_CLASSES_AGE.tif`, etc.).
  Tant que ces couches sont en STUB_READY, le registre est ACTIVÉ mais
  les recalculs sont en STUB_READY (déclenchables une fois R8 finalisé).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mffp_master_weight_omega")

# ═════════════════════════════════════════════════════════════════════════
# Constantes et chemins
# ═════════════════════════════════════════════════════════════════════════
MASTER_WEIGHTS_PATH = Path(
    "/app/backend/data/territoire/MFFP_MASTER_WEIGHTS.json")
R9_STATE_PATH = Path(
    "/app/backend/data/territoire/R9_RECALC_STATE.json")
R9_REPORT_DIR = Path(
    "/app/backend/data/territoire/r9_reports")
MASTER_WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
R9_REPORT_DIR.mkdir(parents=True, exist_ok=True)

SLOT_ID = "FORET_MFFP_PEE_MAJ_Ω"
SLOT_MANIFEST_PATH = Path(
    "/app/backend/data/gis_operational/GIS_RECEPTION_INTAKE_Ω.json")

# Cibles de recalcul R9 (déclarées par le Commandant)
R9_RECALC_TARGETS = [
    "corridors",
    "hotspots",
    "affuts",
    "salines",
    "zones_vitales",
    "zones_passage",
    "zones_rut",
    "zones_repos",
    "zones_alimentation",
]

# Couches MFFP dérivées requises pour recalcul réel
MFFP_DERIVED_LAYERS_REQUIRED = [
    "MFFP_STRUCTURE",       # structure_forestiere (PHASE_3 R8)
    "MFFP_DENSITY",         # densite_couvert (PHASE_3 R8)
    "MFFP_AGE",             # classes_age (PHASE_3 R8)
    "MFFP_FRAGMENTATION",   # fragmentation Dickson 2017 (PHASE_3 R8)
    "MFFP_PRODUCTIVITY",    # productivite (PHASE_3 R8)
    "MFFP_HABITAT",         # habitat_brut (PHASE_3 R8)
    "MFFP_CONNECTIVITY",    # zonage_ecologique_brut (PHASE_3 R8)
    "MFFP_CONTINUITY",      # ZONAGE_ECOLOGIQUE consolidé
]

# Moteurs dépendants à reconfigurer en PRIMARY_INPUT=MFFP
DEPENDENT_ENGINES = [
    {"name": "engine_corridors_gis_omega",
     "category": "corridors",
     "force_rebuild_required": True},
    {"name": "engine_chevreuil_omega",
     "category": "behavior_population",
     "force_rebuild_required": True},
    {"name": "engine_orignal_omega",
     "category": "behavior_population",
     "force_rebuild_required": True},
    {"name": "engine_ours_noir_omega",
     "category": "behavior_population",
     "force_rebuild_required": True},
    {"name": "engine_dindon_omega",
     "category": "behavior_population",
     "force_rebuild_required": True},
    {"name": "engine_wapiti_omega",
     "category": "behavior_population",
     "force_rebuild_required": True},
    {"name": "engine_habitat_omega",
     "category": "habitat",
     "force_rebuild_required": True},
    {"name": "engine_vegetation_omega",
     "category": "vegetation",
     "force_rebuild_required": True},
    {"name": "engine_phenologie_omega",
     "category": "phenology",
     "force_rebuild_required": True},
    {"name": "engine_calibration_dynamique_omega",
     "category": "calibration",
     "force_rebuild_required": True},
    {"name": "engine_corridors_vitaux",
     "category": "corridors",
     "force_rebuild_required": True},
    {"name": "engine_ecological_orchestrator",
     "category": "orchestration",
     "force_rebuild_required": True},
]

_R9_LOCK = threading.Lock()


# ═════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated_utc"] = _utc_now()
    tmp = path.with_suffix(".partial")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    os.replace(str(tmp), str(path))


def read_master_weights() -> Dict[str, Any]:
    """Lit le registre de pondération MFFP. Init si absent."""
    if not MASTER_WEIGHTS_PATH.exists():
        return _init_default_weights()
    try:
        return json.loads(MASTER_WEIGHTS_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("MFFP_WEIGHTS_READ_FALLBACK: %s — re-init", e)
        return _init_default_weights()


def _init_default_weights() -> Dict[str, Any]:
    """Initialise le registre avec les valeurs canoniques R9."""
    data = {
        "manifest_id": "MFFP_MASTER_WEIGHTS_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°52-R9",
        "amplification_label": "MFFP×1000",
        "active": False,  # Désactivé par défaut · explicite via /activate
        "weights": {
            "WEIGHT_MFFP": 1.0,
            "WEIGHT_ALL_OTHER": 0.1,
        },
        "score_formula": (
            "score_final = (score_original * 0.2) + (score_MFFP * 0.8)"
        ),
        "score_coefficients": {
            "alpha_original": 0.2,
            "beta_mffp": 0.8,
        },
        "prioritized_layers": [
            "MFFP_STRUCTURE",
            "MFFP_DENSITY",
            "MFFP_AGE",
            "MFFP_FRAGMENTATION",
        ],
        "mffp_derived_layers_required": MFFP_DERIVED_LAYERS_REQUIRED,
        "recalc_targets": R9_RECALC_TARGETS,
        "dependent_engines": DEPENDENT_ENGINES,
        "v30_lock": "INVIOLÉ",
    }
    _atomic_write(MASTER_WEIGHTS_PATH, data)
    return data


def activate_mffp_master(authority: str) -> Dict[str, Any]:
    """Active le registre · idempotent · trace l'autorité."""
    w = read_master_weights()
    if not w.get("active"):
        w["active"] = True
        w["activated_at_utc"] = _utc_now()
        w["activated_by"] = authority
        # Sceau d'activation : SHA-256 du payload canonicalisé
        canon = json.dumps(
            {k: v for k, v in w.items()
             if k not in ("last_updated_utc", "activation_seal_sha256")},
            sort_keys=True, ensure_ascii=False).encode("utf-8")
        w["activation_seal_sha256"] = hashlib.sha256(canon).hexdigest()
        _atomic_write(MASTER_WEIGHTS_PATH, w)
        logger.info("MFFP_MASTER_ACTIVATED authority=%s seal=%s",
                    authority, w["activation_seal_sha256"])
    return w


def deactivate_mffp_master(authority: str) -> Dict[str, Any]:
    """Désactive l'amplification (rollback)."""
    w = read_master_weights()
    if w.get("active"):
        w["active"] = False
        w["deactivated_at_utc"] = _utc_now()
        w["deactivated_by"] = authority
        _atomic_write(MASTER_WEIGHTS_PATH, w)
    return w


# ═════════════════════════════════════════════════════════════════════════
# Vérification disponibilité couches MFFP dérivées (PHASE_3 R8)
# ═════════════════════════════════════════════════════════════════════════
def check_mffp_derived_layers_availability() -> Dict[str, Any]:
    """Inspecte le state R8 pour déterminer si PHASE_3 a produit les
    couches MFFP dérivées requises.

    Retourne :
      · all_available : bool
      · per_layer : dict[layer_id → bool]
      · phase_3_status : str
      · blocker_reason : str (si non disponible)
    """
    from engines.v8_institutional.especes.pee_maj_r8_orchestrator_omega \
        import read_state as r8_read_state
    r8 = r8_read_state()
    phase_3 = (r8.get("phases") or {}).get(
        "PHASE_3_DERIVATION_9_COUCHES", {})
    p3_status = phase_3.get("status")

    per_layer = {layer: False for layer in MFFP_DERIVED_LAYERS_REQUIRED}
    all_available = False
    blocker_reason: Optional[str] = None

    if p3_status == "OK":
        # PHASE_3 réellement exécutée : vérifier les artifacts
        results = phase_3.get("results") or {}
        # Spec future : results["artifacts_persisted"] = [<paths>]
        per_layer = {
            layer: layer in (results.get("artifacts_keys") or [])
            for layer in MFFP_DERIVED_LAYERS_REQUIRED
        }
        all_available = all(per_layer.values())
        if not all_available:
            missing = [k for k, v in per_layer.items() if not v]
            blocker_reason = f"R8_PHASE_3_PARTIAL · missing={missing}"
    elif p3_status == "STUB_READY":
        blocker_reason = (
            "R8_PHASE_3_STUB_READY · les 9 couches dérivées n'ont pas "
            "encore été calculées. PHASE_3 du R8 doit être exécutée "
            "(specs métier + algorithmes BCE-4X requis).")
    else:
        blocker_reason = (
            f"R8_PHASE_3_NOT_READY · status={p3_status or 'NEVER_RUN'}. "
            "Lancer POST /diagnostic/pee-maj/r8-execute préalablement.")

    return {
        "all_available": all_available,
        "per_layer": per_layer,
        "phase_3_status": p3_status,
        "blocker_reason": blocker_reason,
        "mffp_derived_layers_required": MFFP_DERIVED_LAYERS_REQUIRED,
    }


# ═════════════════════════════════════════════════════════════════════════
# Planificateur de recalcul R9 (orchestrateur)
# ═════════════════════════════════════════════════════════════════════════
def read_r9_state() -> Dict[str, Any]:
    if not R9_STATE_PATH.exists():
        return {}
    try:
        return json.loads(R9_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _update_target(state: Dict[str, Any], target: str, status: str,
                    **kwargs) -> None:
    state["targets"][target]["status"] = status
    state["targets"][target]["last_update_utc"] = _utc_now()
    state["targets"][target].update(kwargs)
    _atomic_write(R9_STATE_PATH, state)


def _execute_recalc_r9(run_id: str, force: bool) -> None:
    """Background thread : pour chaque cible, applique le recalcul si
    inputs MFFP disponibles ; sinon STUB_READY explicite."""
    state = read_r9_state()
    try:
        # Vérification couches MFFP dérivées
        availability = check_mffp_derived_layers_availability()
        state["mffp_layers_availability"] = availability
        _atomic_write(R9_STATE_PATH, state)

        # Pour chaque cible : recalculer ou STUB_READY
        weights = read_master_weights()
        for target in R9_RECALC_TARGETS:
            _update_target(state, target, "RUNNING",
                            started_at_utc=_utc_now())
            t0 = time.time()
            try:
                if availability["all_available"]:
                    # CHEMIN RÉEL (à implémenter quand R8 PHASE_3 finalisée)
                    # Pour l'instant : marquer comme NOT_IMPLEMENTED
                    # car les fonctions de recalcul effectif requièrent
                    # les algorithmes métier (corridors avec WEIGHT_MFFP, etc.)
                    _update_target(
                        state, target,
                        "STUB_READY_AWAITING_BUSINESS_LOGIC",
                        completed_at_utc=_utc_now(),
                        elapsed_s=round(time.time() - t0, 2),
                        anti_generique_note=(
                            "Couches MFFP disponibles mais logique de "
                            f"recalcul {target} non encore implémentée. "
                            "Spécifications métier R9 à fournir : "
                            "comment combiner score_original × 0.2 + "
                            "score_MFFP × 0.8 par cible."),
                    )
                else:
                    _update_target(
                        state, target,
                        "STUB_READY_BLOCKED_BY_R8_PHASE_3",
                        completed_at_utc=_utc_now(),
                        elapsed_s=round(time.time() - t0, 2),
                        blocker=availability["blocker_reason"],
                        weights_applied=weights.get("weights"),
                        score_formula_applied=weights.get("score_formula"),
                    )
            except Exception as e:
                _update_target(
                    state, target, "FAILED",
                    completed_at_utc=_utc_now(),
                    error=str(e)[:500],
                    traceback=traceback.format_exc()[-1000:])

        # Dependencies update (PRIMARY_INPUT MFFP) — toujours exécutable
        deps_marked = []
        for eng in DEPENDENT_ENGINES:
            deps_marked.append({
                "engine_name": eng["name"],
                "category": eng["category"],
                "primary_input": "MFFP",
                "force_rebuild_pending": True,
                "marked_at_utc": _utc_now(),
            })
        state["engine_dependencies_marked"] = deps_marked
        state["engine_dependencies_count"] = len(deps_marked)

        # Synthèse
        statuses = {
            t: state["targets"][t]["status"]
            for t in R9_RECALC_TARGETS
        }
        state["targets_summary"] = statuses
        if all(s == "OK" for s in statuses.values()):
            state["status"] = "OK"
        elif any(s.startswith("STUB_READY") for s in statuses.values()):
            state["status"] = "OK_WITH_STUBS"
        else:
            state["status"] = "MIXED"
        state["completed_at_utc"] = _utc_now()
        state["total_elapsed_s"] = round(
            time.time()
            - datetime.fromisoformat(state["started_at_utc"]).timestamp(), 2)
        _atomic_write(R9_STATE_PATH, state)

        # Rapport BIONIC_AMPLIFICATION_REPORT
        report = {
            "manifest_id": "BIONIC_AMPLIFICATION_REPORT_R9_Ω",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "ordre": "N°52-R9",
            "amplification_label": "MFFP×1000",
            "run_id": run_id,
            "started_at_utc": state["started_at_utc"],
            "completed_at_utc": state["completed_at_utc"],
            "total_elapsed_s": state["total_elapsed_s"],
            "status_global": state["status"],
            "weights_applied": weights.get("weights"),
            "score_formula_applied": weights.get("score_formula"),
            "mffp_layers_availability": availability,
            "targets_summary": statuses,
            "engine_dependencies_count": len(deps_marked),
            "engine_dependencies": deps_marked,
            "next_steps_to_unlock_real_recalc": [
                "Exécuter R8 PHASE_3_DERIVATION_9_COUCHES en mode RÉEL "
                "(specs algorithmiques BCE-4X + dictionnaires MFFP_CODES)",
                "Implémenter les 9 fonctions de recalcul WEIGHT_MFFP "
                "(corridors, hotspots, affuts, salines, zones_*)",
                "Chaque fonction métier doit appliquer "
                "score_final = score_original × 0.2 + score_MFFP × 0.8",
            ],
            "v30_lock": "INVIOLÉ",
        }
        report_path = R9_REPORT_DIR / f"BIONIC_AMPLIFICATION_REPORT_{run_id}.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8")
        state["report_path"] = str(report_path)
        _atomic_write(R9_STATE_PATH, state)
        logger.info("R9_EXEC_DONE run_id=%s status=%s report=%s",
                    run_id, state["status"], report_path)
    finally:
        try:
            _R9_LOCK.release()
        except RuntimeError:
            pass


def start_r9_recalc_background(force: bool = False,
                                authority: str = "COMMANDANT_STEEVE_MAX"
                                ) -> Dict[str, Any]:
    """Démarre le run R9 en background. Idempotent (lock + state)."""
    current = read_r9_state()
    is_zombie = False
    if current.get("status") == "RUNNING":
        try:
            last = datetime.fromisoformat(current.get("last_update_utc", ""))
            age_s = (datetime.now(timezone.utc) - last).total_seconds()
            if age_s > 120:
                is_zombie = True
        except Exception:
            is_zombie = True
        if is_zombie:
            try:
                _R9_LOCK.release()
            except RuntimeError:
                pass
            current["status"] = "ZOMBIE_POD_RESTART"
            _atomic_write(R9_STATE_PATH, current)

    if not _R9_LOCK.acquire(blocking=False):
        return {"ok": False, "reason": "ALREADY_RUNNING",
                "current_state": read_r9_state()}
    current = read_r9_state()
    if current.get("status") == "RUNNING" and not force:
        _R9_LOCK.release()
        return {"ok": False, "reason": "ALREADY_RUNNING",
                "current_state": current}

    # Garantir activation registre avant lancement
    activate_mffp_master(authority=authority)

    run_id = f"R9_{int(time.time())}_{os.urandom(3).hex()}"
    state = {
        "run_id": run_id,
        "status": "RUNNING",
        "started_at_utc": _utc_now(),
        "last_update_utc": _utc_now(),
        "ordre": "N°52-R9",
        "amplification_label": "MFFP×1000",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "authority": authority,
        "targets": {
            t: {"status": "PENDING"} for t in R9_RECALC_TARGETS
        },
    }
    _atomic_write(R9_STATE_PATH, state)

    t = threading.Thread(
        target=_execute_recalc_r9, args=(run_id, force),
        name=f"R9-{run_id}", daemon=True)
    t.start()
    return {"ok": True, "run_id": run_id, "status": "RUNNING",
            "state_path": str(R9_STATE_PATH),
            "started_at_utc": state["started_at_utc"],
            "previous_run_was_zombie": is_zombie}


__all__ = [
    "read_master_weights",
    "activate_mffp_master",
    "deactivate_mffp_master",
    "check_mffp_derived_layers_availability",
    "start_r9_recalc_background",
    "read_r9_state",
    "MASTER_WEIGHTS_PATH",
    "R9_STATE_PATH",
    "R9_RECALC_TARGETS",
    "DEPENDENT_ENGINES",
    "MFFP_DERIVED_LAYERS_REQUIRED",
]
