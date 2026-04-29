"""
test_phase_xiv_omega.py — Tests Phase XIV
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3

Couvre :
  - BLOC 2 : CI hook sceau (verify, recompute, log)
  - BLOC 3 : Audit longitudinal (snapshot, diff, paths, continuity)
  - BLOC 4 : Pré-activation SUPER ENGINES_Ω (6 interfaces, lock SHA)
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, "/app/backend")

from engines.v8_institutional.especes.sceau_phase_xiii_validator_omega import (  # noqa: E402
    verify_sceau, recompute_sceau_cumulatif, get_sceau_reference,
    SCEAU_LOG_PATH,
)
from engines.v8_institutional.especes.audit_longitudinal_omega import (  # noqa: E402
    take_snapshot, diff_against_baseline, list_paths_propagation,
    pipeline_continuity_check, full_longitudinal_report,
)
from engines.v8_institutional.especes.super_engines_omega_specs import (  # noqa: E402
    SUPER_ENGINES_Ω, SUPER_ENGINE_LOCK_SHA256, list_super_engines, SuperEngineSpec,
)


# ─────────────────────────────────────────────────────────────────────
# BLOC 2 — CI hook sceau
# ─────────────────────────────────────────────────────────────────────

def test_xiv_b2_01_recompute_sceau_works():
    """recompute_sceau_cumulatif renvoie un SHA-256 hex live."""
    r = recompute_sceau_cumulatif()
    assert r["ok"] is True
    assert isinstance(r["live_sha_cumulatif"], str)
    assert len(r["live_sha_cumulatif"]) == 64


def test_xiv_b2_02_reference_loaded():
    """get_sceau_reference renvoie bien le SHA scellé."""
    r = get_sceau_reference()
    assert r["ok"] is True
    assert isinstance(r["sceau_sha_cumulatif_reference"], str)
    assert len(r["sceau_sha_cumulatif_reference"]) == 64


def test_xiv_b2_03_verify_sceau_match():
    """verify_sceau renvoie verified=True (live==reference) post-Phase XIII."""
    r = verify_sceau()
    assert r["verified"] is True, f"sceau corrompu: live={r['live_sha_cumulatif']} ref={r['reference_sha_cumulatif']}"
    assert r["deployment_action"] == "ALLOW"


def test_xiv_b2_04_log_jsonl_appended():
    """Après verify_sceau, le log JSONL contient au moins une ligne."""
    verify_sceau()  # append
    assert SCEAU_LOG_PATH.exists()
    lines = SCEAU_LOG_PATH.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) >= 1
    last = json.loads(lines[-1])
    assert last["verified"] is True
    assert last["deployment_action"] == "ALLOW"


# ─────────────────────────────────────────────────────────────────────
# BLOC 3 — Audit longitudinal
# ─────────────────────────────────────────────────────────────────────

def test_xiv_b3_01_take_snapshot_artefacts():
    snap = take_snapshot()
    assert snap["artefact_count"] >= 30  # 5*4 BIO_PROFILE + 5*2 BIO_REACTEUR + INDEX/SCEAU + V30(2)
    assert snap["by_phase"]["XII"] >= 20
    assert snap["by_phase"]["XIII"] >= 13
    assert snap["by_phase"]["V30_LOCK"] == 2


def test_xiv_b3_02_diff_baseline_stable():
    d = diff_against_baseline()
    assert d["ok"] is True
    # Au minimum, les SHAs ne doivent pas avoir bougé entre baseline et live
    assert d["modified"] == [], f"Artefacts modifiés inattendus: {d['modified']}"


def test_xiv_b3_03_paths_propagation_275():
    p = list_paths_propagation()
    assert p["total_paths"] == 275
    assert p["expected_paths"] == 275
    assert p["match"] is True


def test_xiv_b3_04_pipeline_continuity_all_ok():
    c = pipeline_continuity_check()
    assert c["all_ok"] is True
    assert c["espece_count"] == 5
    for esp in c["espece_reports"]:
        assert esp["ok"] is True
        assert esp["engines_count"] == 13
        assert esp["bp_actual_sha256"] == esp["bp_declared_sha256"]


def test_xiv_b3_05_full_report_assembled():
    r = full_longitudinal_report()
    assert r["doctrine"] == "BCE-4X_ULTIME_ABSOLU_x3"
    assert r["paths_propagation_summary"]["match"] is True
    assert r["pipeline_continuity"]["all_ok"] is True
    assert r["snapshot"]["artefact_count"] >= 30


# ─────────────────────────────────────────────────────────────────────
# BLOC 4 — SUPER ENGINES_Ω (interfaces uniquement)
# ─────────────────────────────────────────────────────────────────────

EXPECTED_SUPER_ENGINES = [
    "ENGINE_CORRIDORS_MASTER_Ω",
    "ENGINE_NUTRITION_MASTER_Ω",
    "ENGINE_SENSORIEL_MASTER_Ω",
    "ENGINE_COMPORTEMENT_MASTER_Ω",
    "ENGINE_GOUVERNANCE_MASTER_Ω",
    "ENGINE_TERRITOIRE_MASTER_Ω",
]


def test_xiv_b4_01_six_super_engines_present():
    assert len(SUPER_ENGINES_Ω) == 6
    assert sorted(SUPER_ENGINES_Ω.keys()) == sorted(EXPECTED_SUPER_ENGINES)


def test_xiv_b4_02_super_engines_immutable_and_no_logic_yet():
    import dataclasses
    for sid, spec in SUPER_ENGINES_Ω.items():
        assert isinstance(spec, SuperEngineSpec)
        assert spec.activation_status == "PRE_ACTIVATED_AWAITING_PHASE_XV_LOGIC"
        assert spec.anti_generique_strict is True
        assert spec.fallback_authorized is False
        assert spec.interpolation_authorized is False
        assert spec.phase_creation == "PHASE_XIV"
        assert spec.bio_reacteur_dependency.startswith("BIO_REACTEURS_Ω_<ESPECE>.json")
        # Spec frozen → pas modifiable
        with pytest.raises(dataclasses.FrozenInstanceError):
            spec.anti_generique_strict = False  # type: ignore


def test_xiv_b4_03_lock_sha_present():
    assert isinstance(SUPER_ENGINE_LOCK_SHA256, str)
    assert len(SUPER_ENGINE_LOCK_SHA256) == 64


def test_xiv_b4_04_list_super_engines_stable():
    j = list_super_engines()
    assert j["super_engines_count"] == 6
    assert j["super_engine_lock_sha256"] == SUPER_ENGINE_LOCK_SHA256
    assert j["bio_reacteur_dependency_obligatoire"] is True
    assert j["fallback_authorized"] is False
    assert j["interpolation_authorized"] is False


def test_xiv_b4_05_master_engine_consumes_5_others():
    """ENGINE_TERRITOIRE_MASTER_Ω consomme les 5 autres SUPER ENGINES."""
    spec = SUPER_ENGINES_Ω["ENGINE_TERRITOIRE_MASTER_Ω"]
    consumed = spec.engines_consumed
    for other in [
        "ENGINE_CORRIDORS_MASTER_Ω", "ENGINE_NUTRITION_MASTER_Ω",
        "ENGINE_SENSORIEL_MASTER_Ω", "ENGINE_COMPORTEMENT_MASTER_Ω",
        "ENGINE_GOUVERNANCE_MASTER_Ω",
    ]:
        assert other in consumed
