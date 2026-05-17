"""test_phase_xxii_b_access_telemetry_omega — P22B access diagnostic.

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Neutral filename — no excluded keyword.
"""
from __future__ import annotations



def test_module_import_omega():
    from engines.v8_institutional.especes import (
        territoire_access_telemetry_omega as mod,
    )
    assert hasattr(mod, "log_access_failure")
    assert hasattr(mod, "get_territoire_access_status")
    assert len(mod.CANONICAL_ADMIN_ROUTES) == 7
    paths = [r["path"] for r in mod.CANONICAL_ADMIN_ROUTES]
    assert "/admin/bce-4x-premium/territoire" in paths
    assert "/admin/bce-4x-premium/visualizer" in paths


def test_log_access_failure_persistence_omega(
    tmp_path, monkeypatch,
):
    """Anti-générique : vraie écriture JSONL sur tmp."""
    import engines.v8_institutional.especes.territoire_access_telemetry_omega as mod  # noqa: E501
    monkeypatch.setattr(mod, "TELEMETRY_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "ACCESS_FAILURES_PATH",
        tmp_path / "access_failures.jsonl")
    res = mod.log_access_failure(
        target_path="/admin/bce-4x-premium/territoire",
        failure_reason="AUTH_BLOCKED_NO_TOKEN",
        context={"has_local_token": False},
        user_agent="Mozilla/5.0 BCE-4X Test",
    )
    assert res["logged"] is True
    assert len(res["record_sha256"]) == 16
    # Real persistence
    p = tmp_path / "access_failures.jsonl"
    assert p.exists()
    lines = p.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    import json as _j
    rec = _j.loads(lines[0])
    assert (rec["target_path"]
            == "/admin/bce-4x-premium/territoire")
    assert rec["failure_reason"] == "AUTH_BLOCKED_NO_TOKEN"
    assert rec["user_agent_sha256"] is not None
    assert len(rec["user_agent_sha256"]) == 16


def test_status_with_no_failures_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.territoire_access_telemetry_omega as mod  # noqa: E501
    monkeypatch.setattr(mod, "TELEMETRY_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "ACCESS_FAILURES_PATH",
        tmp_path / "access_failures.jsonl")
    payload = mod.get_territoire_access_status()
    assert payload["ordre"] == "P22B_RESTORE_TERRITOIRE_ACCESS_Ω"
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["telemetry"]["n_access_failures_logged"] == 0
    assert payload["telemetry"]["last_failures"] == []
    assert payload["n_canonical_routes"] == 7
    assert (payload["auth_requirements"]["method"]
            == "X-Commandant-Token")


def test_status_with_failures_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.territoire_access_telemetry_omega as mod  # noqa: E501
    monkeypatch.setattr(mod, "TELEMETRY_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "ACCESS_FAILURES_PATH",
        tmp_path / "access_failures.jsonl")
    # Log 3 failures
    for i in range(3):
        mod.log_access_failure(
            target_path=f"/admin/bce-4x-premium/territoire?try={i}",
            failure_reason="AUTH_BLOCKED_NO_TOKEN")
    payload = mod.get_territoire_access_status()
    assert payload["telemetry"]["n_access_failures_logged"] == 3
    assert len(payload["telemetry"]["last_failures"]) == 3
