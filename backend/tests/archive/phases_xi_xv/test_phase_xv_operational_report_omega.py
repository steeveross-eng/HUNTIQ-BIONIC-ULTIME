"""test_phase_xv_operational_report_omega — P15 pytest (neutral naming).

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
"""
from __future__ import annotations

import pytest


def test_module_import_omega():
    from engines.v8_institutional.especes import (
        territoire_omega_report_omega as mod,
    )
    assert hasattr(mod, "generate_territoire_omega_report")
    assert hasattr(mod, "get_territoire_omega_report_status")
    assert mod.SOURCE_OVERLAYS  # non-empty


def test_generate_json_only_omega(tmp_path, monkeypatch):
    """Vérif JSON persisté + SHA deterministic + anti-générique."""
    import engines.v8_institutional.especes.territoire_omega_report_omega as mod
    monkeypatch.setattr(mod, "REPORT_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "REPORT_HISTORY_PATH", tmp_path / "history.jsonl")
    monkeypatch.setattr(
        mod, "REPORTS_STORE", tmp_path / "store")
    payload = mod.generate_territoire_omega_report(
        zone_label="UNIT_TEST_ZONE",
        include_pdf=False,
        include_html=False,
        persist=True,
    )
    assert payload["ordre"] == "P15_TERRITOIRE_Ω_REPORT_CREATE_Ω"
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["anti_generique_strict"] is True
    assert len(payload["report_sha256"]) == 64
    # Real persistence
    assert (tmp_path / "store").is_dir()
    assert (tmp_path / "history.jsonl").exists()
    assert "json_path" in payload["files_generated"]
    # Recommendations deterministic shape
    assert isinstance(payload["operational_recommendations"], list)
    assert payload["recommendations_count"] == len(
        payload["operational_recommendations"])


def test_generate_with_pdf_html_omega(tmp_path, monkeypatch):
    """Vrai PDF + HTML écrits (anti-générique : fichiers réels)."""
    import engines.v8_institutional.especes.territoire_omega_report_omega as mod
    monkeypatch.setattr(mod, "REPORT_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "REPORT_HISTORY_PATH", tmp_path / "history.jsonl")
    monkeypatch.setattr(
        mod, "REPORTS_STORE", tmp_path / "store")
    payload = mod.generate_territoire_omega_report(
        zone_label="UNIT_ZONE_FULL",
        include_pdf=True,
        include_html=True,
        persist=True,
    )
    files = payload["files_generated"]
    # Real filesystem proof
    from pathlib import Path
    html_p = Path(files["html_path"])
    pdf_p = Path(files["pdf_path"])
    assert html_p.exists() and html_p.stat().st_size > 500
    assert pdf_p.exists() and pdf_p.stat().st_size > 1000
    # PDF magic header
    with open(pdf_p, "rb") as f:
        assert f.read(4) == b"%PDF"
    # SHA-256 présent et correct length
    assert len(files["pdf_sha256"]) == 64
    assert len(files["html_sha256"]) == 64


def test_status_empty_and_after_gen_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.territoire_omega_report_omega as mod
    monkeypatch.setattr(mod, "REPORT_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "REPORT_HISTORY_PATH", tmp_path / "history.jsonl")
    monkeypatch.setattr(
        mod, "REPORTS_STORE", tmp_path / "store")
    st0 = mod.get_territoire_omega_report_status()
    assert st0["current_status"] == "NO_REPORTS_GENERATED"
    mod.generate_territoire_omega_report(
        zone_label="Z1", include_pdf=False,
        include_html=False, persist=True)
    st1 = mod.get_territoire_omega_report_status()
    assert st1["current_status"] == "ACTIVE"
    assert st1["n_reports_generated"] == 1
    assert st1["last_zone_label"] == "Z1"
