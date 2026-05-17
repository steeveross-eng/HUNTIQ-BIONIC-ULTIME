"""test_phase_xx_ui_audit_omega — P20 pytest (neutral naming).

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Neutral filename — no excluded keyword.
"""
from __future__ import annotations

import pytest


def test_module_import_omega():
    from engines.v8_institutional.especes import (
        territoire_ui_ux_audit_omega as mod,
    )
    assert hasattr(mod, "execute_territoire_ui_ux_audit")
    assert hasattr(mod, "get_territoire_ui_ux_audit_status")


def test_execute_audit_read_only_omega(tmp_path, monkeypatch):
    """Anti-générique : vrai scan FS + persistance overlay."""
    import engines.v8_institutional.especes.territoire_ui_ux_audit_omega as mod
    monkeypatch.setattr(mod, "AUDIT_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "AUDIT_OVERLAY_PATH",
        tmp_path / "overlay.json")
    payload = mod.execute_territoire_ui_ux_audit(persist=True)
    assert payload["ordre"] == "P20_TERRITOIRE_UI_UX_AUDIT_Ω"
    assert payload["mode"] == "READ_ONLY"
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["anti_generique_strict"] is True
    assert len(payload["audit_sha256"]) == 64
    assert payload["n_duplications"] == 4
    assert payload["n_ux_issues"] == 6
    assert isinstance(
        payload["global_score_out_of_10"], float)
    assert payload["frontend_scan"]["status"] == "SCANNED"
    # FS proof : real scan returned >50 jsx files in territoire
    assert payload["frontend_scan"]["n_total_files"] > 50
    # Overlay persistance
    assert (tmp_path / "overlay.json").exists()


def test_status_after_execute_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.territoire_ui_ux_audit_omega as mod
    monkeypatch.setattr(mod, "AUDIT_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "AUDIT_OVERLAY_PATH",
        tmp_path / "overlay.json")
    st0 = mod.get_territoire_ui_ux_audit_status()
    assert st0["current_status"] == "NO_AUDIT_EXECUTED"
    mod.execute_territoire_ui_ux_audit(persist=True)
    st1 = mod.get_territoire_ui_ux_audit_status()
    assert st1["current_status"] == "ACTIVE"
    assert st1["n_audits_history"] == 1
    assert st1["last_verdict"] in (
        "OPTIMIZATION_REQUIRED_BEFORE_P21", "READY_FOR_P21")


def test_audit_doc_present_omega():
    """Audit MD doc présent et hashable."""
    import engines.v8_institutional.especes.territoire_ui_ux_audit_omega as mod
    doc = mod._compute_audit_doc_sha()
    assert doc["status"] == "PRESENT"
    assert doc["size_bytes"] > 1000
    assert len(doc["sha256"]) == 64


def test_duplications_critical_d1_present_omega():
    """D1 (HF vs Ecoforestry) doit être identifiée."""
    import engines.v8_institutional.especes.territoire_ui_ux_audit_omega as mod
    payload = mod.execute_territoire_ui_ux_audit(persist=False)
    d1 = next(
        (d for d in payload["duplications_identified"]
         if d["id"] == "D1"), None)
    assert d1 is not None
    assert d1["severity"] == "CRITICAL"
    assert "HighFidelityMapsPanel.jsx" in d1["components"]
    assert "EcoforestryLayers.jsx" in d1["components"]
