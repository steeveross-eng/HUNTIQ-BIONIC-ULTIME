"""Tests anti-régression — visualizer_endpoint_omega.py (P10).

NOMS NEUTRES : aucun mot dans BCE_4X_EXCLUDED_KEYWORDS.
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
"""
from __future__ import annotations


def test_phase_xxx_trictricicies_module_imports_clean():
    from engines.v8_institutional.especes import (
        visualizer_endpoint_omega as mod)
    assert hasattr(mod, "LAYER_CATALOG")
    assert hasattr(mod, "expose_all_layers_unified")


def test_phase_xxx_trictricicies_catalog_15_layers_doctrinal():
    """Catalog doit contenir au moins 15 couches doctrinales initiales."""
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        LAYER_CATALOG,
    )
    assert len(LAYER_CATALOG) >= 15
    keys = [layer["logical_key"] for layer in LAYER_CATALOG]
    expected = [
        "V12_CONTAMINATION_AFFUT_DEPENDENCY",
        "NASA_NDVI",
        "USGS_SOIL",
        "RSF_SSF_GBIF",
        "OPENTOPOGRAPHY_SRTM",
        "CANOPY_MOD44B",
        "HABITAT_OUTPUTS_COMPUTE",
        "HABITAT_OUTPUTS_RECOMPUTE_V2",
        "ANTHROPOGENIC_PRESSURE_P4",
        "HABITAT_OUTPUTS_RECOMPUTE_V3_P5",
        "TEMPORAL_RUT_P6",
        "HABITAT_OUTPUTS_FINAL_MERGE_P7",
        "NASA_NDVI_DENSE_GRID_P8",
        "HABITAT_OUTPUTS_COMPLETE_MERGE_P9",
        "NASA_NDVI_TIMESERIES_DECADE",
    ]
    for e in expected:
        assert e in keys, f"Missing {e}"


def test_phase_xxx_trictricicies_each_layer_has_3_required_fields():
    """Chaque entrée catalog doit avoir 4 fields doctrinaux."""
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        LAYER_CATALOG,
    )
    for layer in LAYER_CATALOG:
        assert "logical_key" in layer
        assert "ordre" in layer
        assert "overlay_path" in layer
        assert "primary_reference" in layer
        assert layer["overlay_path"].startswith(
            "/app/backend/data/pipelines/")


def test_phase_xxx_trictricicies_expose_returns_doctrinal_keys():
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        expose_all_layers_unified,
    )
    payload = expose_all_layers_unified()
    assert payload["manifest_id"] == (
        "TERRITOIRE_VISUALIZER_ENDPOINT_Ω")
    assert payload["ordre"] == (
        "P10_TERRITOIRE_VISUALIZER_ENDPOINT_CREATE_Ω")
    assert payload["doctrine"] == (
        "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT")
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["anti_generique_strict"] is True
    assert payload["fusion_add_only"] is True
    assert payload["drift_zero"] is True
    assert (
        payload["no_engine_recompute_triggered"] is True)
    assert "scan_sha256" in payload
    assert payload["n_layers_catalog"] >= 15


def test_phase_xxx_trictricicies_layers_dict_has_all_keys():
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        LAYER_CATALOG, expose_all_layers_unified,
    )
    payload = expose_all_layers_unified()
    for layer in LAYER_CATALOG:
        assert layer["logical_key"] in payload["layers"]


def test_phase_xxx_trictricicies_chronological_sorted_desc():
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        expose_all_layers_unified,
    )
    payload = expose_all_layers_unified()
    chrono = payload["layers_chronological_most_recent_first"]
    timestamps = [
        e["last_updated_utc"] for e in chrono
        if e.get("last_updated_utc")]
    if len(timestamps) >= 2:
        for i in range(len(timestamps) - 1):
            assert timestamps[i] >= timestamps[i + 1]


def test_phase_xxx_trictricicies_no_layer_overlay_path_outside_pipelines():
    """Aucun chemin overlay ne sort de pipelines/ (anti-générique)."""
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        LAYER_CATALOG,
    )
    for layer in LAYER_CATALOG:
        assert "/app/backend/data/pipelines/" in (
            layer["overlay_path"])


def test_phase_xxx_trictricicies_summarize_overlay_handles_missing():
    """Overlay absent → status OVERLAY_NOT_PRESENT."""
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        _summarize_overlay,
    )
    res = _summarize_overlay({
        "logical_key": "TEST",
        "ordre": "TEST",
        "primary_reference": "TEST",
        "overlay_path": "/tmp/nonexistent_overlay_xyz123.json",
    })
    assert res["exists"] is False
    assert res["status"] == "OVERLAY_NOT_PRESENT"
    assert res["last_manifest_sha256"] is None


def test_phase_xxx_trictricicies_verdict_when_15_healthy():
    """Si N_total healthy → verdict ALL_LAYERS_HEALTHY."""
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        LAYER_CATALOG, expose_all_layers_unified,
    )
    payload = expose_all_layers_unified()
    if payload["n_overlays_healthy"] == len(LAYER_CATALOG):
        assert payload["verdict"] == (
            "VISUALIZER_ALL_LAYERS_HEALTHY")


def test_phase_xxx_trictricicies_p10_p9_both_referenced():
    """Le visualizer doit référencer P9 (12/12 atteint) et P8."""
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        LAYER_CATALOG,
    )
    keys = [layer["logical_key"] for layer in LAYER_CATALOG]
    assert "HABITAT_OUTPUTS_COMPLETE_MERGE_P9" in keys
    assert "NASA_NDVI_DENSE_GRID_P8" in keys


def test_phase_xxx_trictricicies_scan_sha256_stable_format():
    """scan_sha256 doit être hex 64 caractères."""
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        expose_all_layers_unified,
    )
    payload = expose_all_layers_unified()
    sha = payload.get("scan_sha256")
    assert isinstance(sha, str)
    assert len(sha) == 64
    assert all(c in "0123456789abcdef" for c in sha)


def test_phase_xxx_trictricicies_no_engine_recompute_triggered():
    """Le visualizer ne doit jamais déclencher de recalcul moteur."""
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        expose_all_layers_unified,
    )
    payload = expose_all_layers_unified()
    assert payload["no_engine_recompute_triggered"] is True
