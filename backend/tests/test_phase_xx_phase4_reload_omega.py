"""test_phase_xx_phase4_reload_omega — P20_PHASE4 force reload doctrinal.

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Neutral filename — no excluded keyword.
"""
from __future__ import annotations

import pytest


def test_module_import_omega():
    from engines.v8_institutional.especes import (
        territoire_omega_reload_omega as mod,
    )
    assert hasattr(mod, "execute_territoire_omega_reload")
    assert hasattr(mod, "get_territoire_omega_reload_status")
    assert mod.WATCHDOG_TIMEOUT_S_DEFAULT == 600
    assert len(mod.DOCTRINAL_OVERLAYS_GLOBS) >= 15


def test_invalid_watchdog_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.territoire_omega_reload_omega as mod
    monkeypatch.setattr(mod, "RELOAD_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "RELOAD_OVERLAY_PATH", tmp_path / "overlay.json")
    with pytest.raises(ValueError, match="WATCHDOG_TIMEOUT_INVALID"):
        mod.execute_territoire_omega_reload(
            persist=True, watchdog_timeout_s=10)
    with pytest.raises(ValueError, match="WATCHDOG_TIMEOUT_INVALID"):
        mod.execute_territoire_omega_reload(
            persist=True, watchdog_timeout_s=99999)


def test_execute_reload_omega(tmp_path, monkeypatch):
    """Anti-générique : vrai reload + scan + persistence overlay."""
    import engines.v8_institutional.especes.territoire_omega_reload_omega as mod
    monkeypatch.setattr(mod, "RELOAD_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "RELOAD_OVERLAY_PATH", tmp_path / "overlay.json")
    payload = mod.execute_territoire_omega_reload(
        persist=True, watchdog_timeout_s=600)
    assert payload["verdict"] == (
        "TERRITOIRE_OMEGA_RELOAD_COMPLETED")
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["watchdog_state"]["current_timeout_s"] == 600
    assert payload["watchdog_state"]["previous_timeout_s"] == 300
    assert (payload["force_reload_actions"][
        "init_pipeline_timeout"] == "EXTENDED_TO_600S")
    assert len(payload["reload_sha256"]) == 64
    # Real reload happened
    assert (
        payload["engine_reload_summary"]["n_reloaded"] >= 1)
    # Real scan happened
    assert "n_overlays_scanned" in (
        payload["overlay_scan_summary"])
    # Real persistence
    assert (tmp_path / "overlay.json").exists()


def test_status_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.territoire_omega_reload_omega as mod
    monkeypatch.setattr(mod, "RELOAD_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "RELOAD_OVERLAY_PATH", tmp_path / "overlay.json")
    st0 = mod.get_territoire_omega_reload_status()
    assert st0["current_status"] == "NO_RELOAD_EXECUTED"
    mod.execute_territoire_omega_reload(persist=True)
    st1 = mod.get_territoire_omega_reload_status()
    assert st1["current_status"] == "ACTIVE"
    assert st1["n_reloads_history"] == 1
    assert (st1["watchdog_timeout_s_default"] == 600)


def test_purge_lru_caches_omega():
    """Anti-générique : purge GC réel."""
    import engines.v8_institutional.especes.territoire_omega_reload_omega as mod
    res = mod._purge_lru_caches()
    assert "n_lru_caches_purged" in res
    assert "gc_objects_collected" in res
    assert isinstance(res["gc_objects_collected"], int)
