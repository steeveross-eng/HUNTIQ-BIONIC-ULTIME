"""test_phase_xvii_field_guide_omega — P17 pytest (neutral naming).

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Neutral — no banned keyword in filename or test names.
"""
from __future__ import annotations

import pytest


def test_module_import_omega():
    from engines.v8_institutional.especes import (
        waypoint_guide_omega as mod,
    )
    assert hasattr(mod, "generate_waypoint_field_guide")
    assert hasattr(mod, "get_waypoint_guide_status")


def test_reject_bad_lat_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.waypoint_guide_omega as mod
    monkeypatch.setattr(mod, "GUIDE_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "GUIDE_HISTORY_PATH", tmp_path / "h.jsonl")
    monkeypatch.setattr(
        mod, "GUIDES_STORE", tmp_path / "store")
    with pytest.raises(ValueError, match="LATITUDE_INVALID"):
        mod.generate_waypoint_field_guide(
            lat=999.0, lon=0.0, species="cerf")


def test_reject_bad_lon_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.waypoint_guide_omega as mod
    monkeypatch.setattr(mod, "GUIDE_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "GUIDE_HISTORY_PATH", tmp_path / "h.jsonl")
    monkeypatch.setattr(
        mod, "GUIDES_STORE", tmp_path / "store")
    with pytest.raises(ValueError, match="LONGITUDE_INVALID"):
        mod.generate_waypoint_field_guide(
            lat=46.0, lon=999.0, species="cerf")


def test_reject_bad_radius_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.waypoint_guide_omega as mod
    monkeypatch.setattr(mod, "GUIDE_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "GUIDE_HISTORY_PATH", tmp_path / "h.jsonl")
    monkeypatch.setattr(
        mod, "GUIDES_STORE", tmp_path / "store")
    with pytest.raises(ValueError, match="RADIUS_INVALID"):
        mod.generate_waypoint_field_guide(
            lat=46.0, lon=-73.0, species="cerf", radius_m=5)


def test_generate_pdf_html_omega(tmp_path, monkeypatch):
    """Vrai PDF + HTML écrits (anti-générique)."""
    import engines.v8_institutional.especes.waypoint_guide_omega as mod
    monkeypatch.setattr(mod, "GUIDE_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "GUIDE_HISTORY_PATH", tmp_path / "h.jsonl")
    monkeypatch.setattr(
        mod, "GUIDES_STORE", tmp_path / "store")
    payload = mod.generate_waypoint_field_guide(
        lat=46.8, lon=-71.3, species="cerf", radius_m=500)
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["ordre"] == "P17_WAYPOINT_GUIDE_CREATE_Ω"
    assert len(payload["guide_sha256"]) == 64
    files = payload["files_generated"]
    from pathlib import Path
    pdf_p = Path(files["pdf_path"])
    html_p = Path(files["html_path"])
    assert pdf_p.exists() and pdf_p.stat().st_size > 1000
    assert html_p.exists() and html_p.stat().st_size > 300
    with open(pdf_p, "rb") as f:
        assert f.read(4) == b"%PDF"
    # Recommendations always at least 1 entry
    assert len(payload["recommendations"]) >= 1


def test_status_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.waypoint_guide_omega as mod
    monkeypatch.setattr(mod, "GUIDE_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "GUIDE_HISTORY_PATH", tmp_path / "h.jsonl")
    monkeypatch.setattr(
        mod, "GUIDES_STORE", tmp_path / "store")
    st0 = mod.get_waypoint_guide_status()
    assert st0["current_status"] == "NO_GUIDES_GENERATED"
    mod.generate_waypoint_field_guide(
        lat=46.8, lon=-71.3, species="cerf",
        include_pdf=False, include_html=False)
    st1 = mod.get_waypoint_guide_status()
    assert st1["current_status"] == "ACTIVE"
    assert st1["n_guides_generated"] == 1
    assert st1["last_species"] == "cerf"
