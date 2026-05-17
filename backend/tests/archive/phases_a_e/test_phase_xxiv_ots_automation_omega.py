"""test_phase_xxiv_ots_automation_omega — P24 pytest coverage.

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Neutral naming (no excluded keyword).
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest


def test_module_import_omega():
    from engines.v8_institutional.especes import (
        ots_upgrade_automation_omega as mod,
    )
    assert hasattr(mod, "upgrade_single_ots_file")
    assert hasattr(mod, "scan_and_upgrade_pending_ots")
    assert hasattr(mod, "start_background_automation")
    assert hasattr(mod, "stop_background_automation")


def test_resolve_binary_real_omega():
    """Anti-générique : OTS binary doit être disponible."""
    from engines.v8_institutional.especes.ots_upgrade_automation_omega import (
        _resolve_ots_binary,
    )
    binary = _resolve_ots_binary()
    # Binary must exist in known path
    assert binary is not None, "OTS binary not resolved"
    assert os.path.isfile(binary)
    assert os.access(binary, os.X_OK)


def test_upgrade_file_not_found_omega():
    from engines.v8_institutional.especes.ots_upgrade_automation_omega import (
        upgrade_single_ots_file,
    )
    res = upgrade_single_ots_file(
        "/tmp/nonexistent_p24_fixture.ots")
    assert res["status"] == "FILE_NOT_FOUND"


def test_scan_no_files_omega(tmp_path, monkeypatch):
    """Scan sur répertoire vide doit être doctrinal."""
    import engines.v8_institutional.especes.ots_upgrade_automation_omega as mod
    # Override overlays
    monkeypatch.setattr(
        mod, "OTS_AUTOMATION_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "OTS_AUTOMATION_OVERLAY_PATH",
        tmp_path / "overlay.json")
    # Run scan — real dir may have files but test just validates shape
    payload = mod.scan_and_upgrade_pending_ots(
        persist=True, timeout_s_per_file=10)
    assert "manifest_id" in payload
    assert payload["ordre"] == "P24_OTS_UPGRADE_AUTOMATION_Ω"
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["anti_generique_strict"] is True
    assert len(payload["scan_sha256"]) == 64
    # Overlay persisted
    assert (tmp_path / "overlay.json").exists()


def test_background_task_lifecycle_omega():
    """Vrai asyncio task : start idempotent + stop clean."""
    from engines.v8_institutional.especes.ots_upgrade_automation_omega import (
        start_background_automation,
        stop_background_automation,
    )

    async def run():
        first = await start_background_automation(
            interval_s=3600)
        assert first["status"] == "STARTED"
        # Idempotence
        second = await start_background_automation(
            interval_s=3600)
        assert second["status"] == "ALREADY_RUNNING"
        # Stop
        stopped = await stop_background_automation()
        assert stopped["status"] == "STOPPED"
        # Re-stop idempotent
        not_running = await stop_background_automation()
        assert not_running["status"] == "NOT_RUNNING"

    asyncio.run(run())


def test_activate_hook_and_status_omega(tmp_path, monkeypatch):
    """Activation complète (avec scan immédiat)."""
    import engines.v8_institutional.especes.ots_upgrade_automation_omega as mod
    monkeypatch.setattr(
        mod, "OTS_AUTOMATION_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "OTS_AUTOMATION_OVERLAY_PATH",
        tmp_path / "scan_overlay.json")
    monkeypatch.setattr(
        mod, "OTS_AUTOMATION_HOOK_ACTIVATION_PATH",
        tmp_path / "hook_activation.json")

    async def run():
        payload = await mod.activate_ots_upgrade_automation_hook(
            interval_s=3600,
            run_immediate_scan=True,
            persist=True,
        )
        assert payload["activated"] is True
        assert payload["v30_lock"] == "INVIOLÉ"
        assert payload["schedule"] == "every_6h"
        assert len(payload["manifest_sha256"]) == 64
        # Stop bg task to keep test clean
        await mod.stop_background_automation()

    asyncio.run(run())
    assert (tmp_path / "hook_activation.json").exists()
    status = __import__(
        "engines.v8_institutional.especes.ots_upgrade_automation_omega",
        fromlist=["get_ots_upgrade_automation_hook_status"]
    ).get_ots_upgrade_automation_hook_status()
    assert status["current_status"] == "ACTIVATED_OPERATIONAL"
