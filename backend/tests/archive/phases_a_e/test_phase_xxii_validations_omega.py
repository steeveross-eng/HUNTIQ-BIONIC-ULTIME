"""test_phase_xxii_validations_omega — P22 pytest coverage neutral.

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Naming strictly neutral (no excluded keyword).
"""
from __future__ import annotations

import json
import hashlib

import pytest


def _mk_sha():
    return hashlib.sha256(b"doctrinal_payload_P22").hexdigest()


def test_module_import_omega():
    from engines.v8_institutional.especes import (
        commandant_validations_omega as mod,
    )
    assert hasattr(mod, "record_commandant_validation")
    assert hasattr(mod, "get_commandant_validations_status")


def test_record_rejects_invalid_decision_omega():
    from engines.v8_institutional.especes.commandant_validations_omega import (
        record_commandant_validation,
    )
    with pytest.raises(ValueError, match="DECISION_INVALID"):
        record_commandant_validation(
            scope="UNIT_TEST_SCOPE",
            decision="NOT_A_VALID_DECISION",
            sha256_list=[_mk_sha()],
            notes="invalid decision smoke",
        )


def test_record_rejects_bad_sha_omega():
    from engines.v8_institutional.especes.commandant_validations_omega import (
        record_commandant_validation,
    )
    with pytest.raises(ValueError, match="SHA256_INVALID"):
        record_commandant_validation(
            scope="UNIT_TEST_SCOPE",
            decision="APPROVED",
            sha256_list=["abcd"],  # too short
        )


def test_record_and_status_omega(tmp_path, monkeypatch):
    """Anti-générique : vraie persistance JSONL + overlay."""
    # Redirect persistence to tmp_path
    import engines.v8_institutional.especes.commandant_validations_omega as mod
    monkeypatch.setattr(
        mod, "VALIDATIONS_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "VALIDATIONS_HISTORY_PATH",
        tmp_path / "history.jsonl")
    monkeypatch.setattr(
        mod, "VALIDATIONS_OVERLAY_PATH",
        tmp_path / "overlay.json")
    sha_a = _mk_sha()
    sha_b = hashlib.sha256(b"second_payload").hexdigest()
    payload = mod.record_commandant_validation(
        scope="UNIT_TEST_P22_SMOKE",
        decision="APPROVED",
        sha256_list=[sha_a, sha_b],
        notes="unit-test doctrinal",
        persist=True,
    )
    assert payload["decision"] == "APPROVED"
    assert payload["n_sha_validated"] == 2
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["anti_generique_strict"] is True
    assert len(payload["validation_sha256"]) == 64
    # Verify JSONL persistence
    lines = (tmp_path / "history.jsonl").read_text(
        encoding="utf-8").splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["scope"] == "UNIT_TEST_P22_SMOKE"
    # Status
    status = mod.get_commandant_validations_status()
    assert status["current_status"] == "ACTIVE"
    assert status["n_validations_history"] == 1
    assert status["last_decision"] == "APPROVED"
    assert status["v30_lock"] == "INVIOLÉ"
