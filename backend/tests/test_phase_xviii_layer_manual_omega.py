"""test_phase_xviii_layer_manual_omega — P18 pytest (neutral naming).

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
"""
from __future__ import annotations

import pytest


def test_module_import_omega():
    from engines.v8_institutional.especes import (
        layer_interpretation_manual_omega as mod,
    )
    assert hasattr(mod, "generate_layer_interpretation_manual")
    assert hasattr(mod, "get_layer_manual_status")


def test_catalog_18_layers_omega():
    from engines.v8_institutional.especes.layer_interpretation_manual_omega import (  # noqa: E501
        LAYERS_CATALOG,
    )
    assert len(LAYERS_CATALOG) == 18
    # Each layer has required keys
    required = {"code", "name", "definition",
                "usage", "example", "source_overlay"}
    for l in LAYERS_CATALOG:
        assert required.issubset(l.keys())
        # Code format L\d{2}_
        assert l["code"].startswith("L")


def test_generate_json_only_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.layer_interpretation_manual_omega as mod  # noqa: E501
    monkeypatch.setattr(mod, "MANUAL_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "MANUAL_HISTORY_PATH", tmp_path / "h.jsonl")
    monkeypatch.setattr(
        mod, "MANUAL_STORE", tmp_path / "store")
    payload = mod.generate_layer_interpretation_manual(
        include_pdf=False, include_html=False, persist=True)
    assert payload["n_layers"] == 18
    assert payload["ordre"] == "P18_LAYER_INTERPRETATION_MANUAL_Ω"
    assert len(payload["manual_sha256"]) == 64
    assert payload["v30_lock"] == "INVIOLÉ"


def test_generate_pdf_html_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.layer_interpretation_manual_omega as mod  # noqa: E501
    monkeypatch.setattr(mod, "MANUAL_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "MANUAL_HISTORY_PATH", tmp_path / "h.jsonl")
    monkeypatch.setattr(
        mod, "MANUAL_STORE", tmp_path / "store")
    payload = mod.generate_layer_interpretation_manual(
        include_pdf=True, include_html=True, persist=True)
    files = payload["files_generated"]
    from pathlib import Path
    pdf_p = Path(files["pdf_path"])
    html_p = Path(files["html_path"])
    assert pdf_p.exists() and pdf_p.stat().st_size > 2000
    assert html_p.exists() and html_p.stat().st_size > 1000
    with open(pdf_p, "rb") as f:
        assert f.read(4) == b"%PDF"
    # HTML contains all 18 layer codes
    html_text = html_p.read_text(encoding="utf-8")
    from engines.v8_institutional.especes.layer_interpretation_manual_omega import (  # noqa: E501
        LAYERS_CATALOG,
    )
    for l in LAYERS_CATALOG:
        assert l["code"] in html_text


def test_status_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.layer_interpretation_manual_omega as mod  # noqa: E501
    monkeypatch.setattr(mod, "MANUAL_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "MANUAL_HISTORY_PATH", tmp_path / "h.jsonl")
    monkeypatch.setattr(
        mod, "MANUAL_STORE", tmp_path / "store")
    st0 = mod.get_layer_manual_status()
    assert st0["current_status"] == "NO_MANUAL_GENERATED"
    mod.generate_layer_interpretation_manual(
        include_pdf=False, include_html=False)
    st1 = mod.get_layer_manual_status()
    assert st1["current_status"] == "ACTIVE"
    assert st1["n_manuals_generated"] == 1
    assert st1["n_layers"] == 18
