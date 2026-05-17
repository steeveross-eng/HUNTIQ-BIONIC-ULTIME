"""Tests anti-régression — nasa_ndvi_dense_grid_omega.py (P8) +
habitat_outputs_complete_merge_omega.py (P9).

NOMS NEUTRES : aucun mot dans BCE_4X_EXCLUDED_KEYWORDS.
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
"""
from __future__ import annotations

import json
import math

import pytest


# ═════════════════════════════════════════════════════════════════════════
# P8 NASA_NDVI_DENSE_GRID
# ═════════════════════════════════════════════════════════════════════════
def test_phase_xxx_duotricicies_dense_grid_module_imports_clean():
    from engines.v8_institutional.especes import (
        nasa_ndvi_dense_grid_omega as mod)
    assert hasattr(mod, "ECOLOGICAL_NDVI_BINS")
    assert hasattr(mod, "validate_nasa_ndvi_dense_grid")
    assert hasattr(mod, "activate_nasa_ndvi_dense_grid_hook")
    assert hasattr(mod, "get_nasa_ndvi_dense_grid_hook_status")
    assert hasattr(mod, "get_last_validated_dense_grid")


def test_phase_xxx_duotricicies_5_clusters_doctrinal():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        ECOLOGICAL_NDVI_BINS,
    )
    assert len(ECOLOGICAL_NDVI_BINS) == 5
    labels = [label for _, _, label in ECOLOGICAL_NDVI_BINS]
    assert "BARREN_LOW_PRODUCTIVITY" in labels
    assert "SHRUBLAND_MODERATE" in labels
    assert "OPEN_FOREST_HIGH_PRODUCTIVITY" in labels
    assert "DENSE_FOREST_PRIMARY" in labels
    assert "CANOPY_CLIMAX_OVERSTOCK" in labels


def test_phase_xxx_duotricicies_percentile_basic():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        _percentile,
    )
    values = [0.0, 0.25, 0.5, 0.75, 1.0]
    assert _percentile(values, 0) == 0.0
    assert _percentile(values, 50) == 0.5
    assert _percentile(values, 100) == 1.0


def test_phase_xxx_duotricicies_percentile_empty():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        _percentile,
    )
    assert math.isnan(_percentile([], 50))


def test_phase_xxx_duotricicies_flatten_pixels_decode_scale_nodata_excluded():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        _flatten_pixels_decode_scale,
    )
    subset = [
        {"data": [5000, -3000, 6000]},
        {"data": [-3000, 7000]},
    ]
    valid, n_total, n_nodata = _flatten_pixels_decode_scale(
        subset, nodata=-3000, scale=0.0001)
    assert n_total == 5
    assert n_nodata == 2
    assert len(valid) == 3
    assert valid == pytest.approx([0.5, 0.6, 0.7])


def test_phase_xxx_duotricicies_partition_invalid_when_empty():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        _ecological_partition_pixels,
    )
    res = _ecological_partition_pixels([])
    assert res["valid"] is False


def test_phase_xxx_duotricicies_partition_5_clusters():
    """Pixels distribués → 5 clusters avec Shannon evenness > 0."""
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        _ecological_partition_pixels,
    )
    pixels = (
        [0.1] * 20 + [0.3] * 20 + [0.5] * 20
        + [0.7] * 20 + [0.9] * 20)
    res = _ecological_partition_pixels(pixels)
    assert res["valid"] is True
    assert res["n_pixels_valid"] == 100
    # Distribution uniforme → evenness max
    assert res["shannon_evenness"] >= 0.99


def test_phase_xxx_duotricicies_feeding_zones_full_dense_in_optimum():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        _compute_feeding_zones_full_dense,
    )
    pixels = [0.55] * 100
    res = _compute_feeding_zones_full_dense(
        pixels,
        species_optimum_low=0.5,
        species_optimum_high=0.7)
    assert res["value"] is not None
    assert res["regime"] == (
        "HIGH_QUALITY_FEEDING_ZONE_FULL_DENSE")
    assert (
        res["components"][
            "pct_pixels_in_species_optimum_range"] == 100.0)


def test_phase_xxx_duotricicies_feeding_zones_full_dense_no_pixels():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        _compute_feeding_zones_full_dense,
    )
    res = _compute_feeding_zones_full_dense(
        [], species_optimum_low=0.5, species_optimum_high=0.7)
    assert res["value"] is None
    assert res["regime"] == "DEFERRED_NO_VALID_PIXELS"


def test_phase_xxx_duotricicies_microhabitat_global_aggregate():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        _aggregate_microhabitat_clusters_global,
    )
    fake = {
        "site_a": {
            "valid": True,
            "n_pixels_valid": 100,
            "bins_count": {
                "BARREN_LOW_PRODUCTIVITY": 50,
                "SHRUBLAND_MODERATE": 50,
                "OPEN_FOREST_HIGH_PRODUCTIVITY": 0,
                "DENSE_FOREST_PRIMARY": 0,
                "CANOPY_CLIMAX_OVERSTOCK": 0,
            },
            "shannon_diversity_h": 0.6931,
        },
    }
    res = _aggregate_microhabitat_clusters_global(fake)
    assert res["value"] is not None
    assert "shannon_diversity_h" in res["unit"]


def test_phase_xxx_duotricicies_dense_grid_activate_rejects_unknown_sha():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        activate_nasa_ndvi_dense_grid_hook,
    )
    fake = "0" * 64
    res = activate_nasa_ndvi_dense_grid_hook(
        manifest_sha256=fake, persist=False)
    assert res["activated"] is False
    assert "REJECTED" in res["verdict"]


def test_phase_xxx_duotricicies_dense_grid_overlay_when_present():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        DENSE_GRID_VALIDATION_PATH,
    )
    if not DENSE_GRID_VALIDATION_PATH.exists():
        pytest.skip("Aucun overlay dense grid encore.")
    state = json.loads(
        DENSE_GRID_VALIDATION_PATH.read_text(
            encoding="utf-8"))
    assert state.get("v30_lock") == "INVIOLÉ"


def test_phase_xxx_duotricicies_dense_grid_status_keys():
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (  # noqa: E501
        get_nasa_ndvi_dense_grid_hook_status,
    )
    s = get_nasa_ndvi_dense_grid_hook_status()
    assert s.get("v30_lock") == "INVIOLÉ"
    assert "current_status" in s


# ═════════════════════════════════════════════════════════════════════════
# P9 HABITAT_OUTPUTS_COMPLETE_MERGE
# ═════════════════════════════════════════════════════════════════════════
def test_phase_xxx_duotricicies_complete_merge_module_imports_clean():
    from engines.v8_institutional.especes import (
        habitat_outputs_complete_merge_omega as mod)
    assert hasattr(mod, "merge_habitat_outputs_complete")
    assert hasattr(mod, "get_habitat_complete_merge_status")


def test_phase_xxx_duotricicies_extract_feeding_full_per_site_valid():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        _extract_feeding_full_per_site,
    )
    fake = {
        "site_results": {
            "espece_a": {
                "bands_dense_grid": {
                    "250m_16_days_NDVI": {
                        "feeding_zones_full_dense": {
                            "value": 75.0,
                            "regime": "HIGH",
                            "components": {"x": 1},
                            "species_thresholds_used": {},
                        },
                    },
                },
            },
        },
    }
    out = _extract_feeding_full_per_site(fake)
    assert out["espece_a"]["valid"] is True
    assert out["espece_a"]["feeding_full_score"] == 75.0


def test_phase_xxx_duotricicies_extract_feeding_full_per_site_invalid():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        _extract_feeding_full_per_site,
    )
    fake = {
        "site_results": {
            "espece_a": {
                "bands_dense_grid": {
                    "250m_16_days_NDVI": {
                        "feeding_zones_full_dense": {
                            "value": None,
                            "regime": "DEFERRED",
                        },
                    },
                },
            },
        },
    }
    out = _extract_feeding_full_per_site(fake)
    assert out["espece_a"]["valid"] is False


def test_phase_xxx_duotricicies_compute_feeding_full_output_deferred():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        _compute_feeding_zones_full_output,
    )
    out = _compute_feeding_zones_full_output({
        "valid": False,
        "reason": "missing",
    })
    assert out["value"] is None
    assert out["regime"] == "DEFERRED_NO_VALID_DENSE_GRID"


def test_phase_xxx_duotricicies_compute_feeding_full_output_valid():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        _compute_feeding_zones_full_output,
    )
    out = _compute_feeding_zones_full_output({
        "valid": True,
        "feeding_full_score": 60.0,
        "regime": "MODERATE_FEEDING_ZONE_FULL_DENSE",
        "components": {"x": 1},
        "species_thresholds_used": {},
    })
    assert out["value"] == 60.0
    assert out["unit"] == (
        "feeding_zones_FULL_dense_score_0_100")
    assert "Borowik_2013_EurJWildlRes" in (
        out["primary_references"])


def test_phase_xxx_duotricicies_compute_microhabitat_global_dense_output():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        _compute_microhabitat_clusters_global_dense_output,
    )
    out = _compute_microhabitat_clusters_global_dense_output({
        "microhabitat_clusters_global_dense": {
            "value": 1.3,
            "regime": "HIGH_GLOBAL_DIVERSITY",
            "unit": "shannon_diversity_h",
            "components": {"n": 5},
        },
    })
    assert out["value"] == 1.3
    assert out["regime"] == "HIGH_GLOBAL_DIVERSITY"


def test_phase_xxx_duotricicies_complete_overlay_when_present():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        HABITAT_COMPLETE_PATH,
    )
    if not HABITAT_COMPLETE_PATH.exists():
        pytest.skip("Aucun complete merge encore exécuté.")
    state = json.loads(
        HABITAT_COMPLETE_PATH.read_text(encoding="utf-8"))
    assert state.get("v30_lock") == "INVIOLÉ"
    assert "history" in state


def test_phase_xxx_duotricicies_complete_full_inheritance_present():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        HABITAT_COMPLETE_PATH,
    )
    if not HABITAT_COMPLETE_PATH.exists():
        pytest.skip("Aucun complete merge encore exécuté.")
    state = json.loads(
        HABITAT_COMPLETE_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History vide.")
    last = state["history"][-1]
    final_inh = last.get("final_inheritance") or {}
    assert "final_merge_sha256" in final_inh
    assert "final_v3_inheritance" in final_inh
    assert "final_rut_validation_manifest_sha256" in final_inh


def test_phase_xxx_duotricicies_complete_feeding_full_present_per_site():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        HABITAT_COMPLETE_PATH,
    )
    if not HABITAT_COMPLETE_PATH.exists():
        pytest.skip("Aucun complete merge encore exécuté.")
    state = json.loads(
        HABITAT_COMPLETE_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History vide.")
    last = state["history"][-1]
    per_site = last.get("per_site_outputs_complete") or {}
    if not per_site:
        pytest.skip("Aucun site complete.")
    for site_name, sd in per_site.items():
        outputs = sd.get("computed_outputs") or {}
        assert "feeding_zones_FULL" in outputs
        assert "rut_zones" in outputs
        assert "pressure_sensitive_zones" in outputs


def test_phase_xxx_duotricicies_complete_global_microhab_present():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        HABITAT_COMPLETE_PATH,
    )
    if not HABITAT_COMPLETE_PATH.exists():
        pytest.skip("Aucun complete merge encore exécuté.")
    state = json.loads(
        HABITAT_COMPLETE_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History vide.")
    last = state["history"][-1]
    glob = last.get("global_outputs_complete") or {}
    assert "microhabitat_clusters_global_dense" in glob


def test_phase_xxx_duotricicies_complete_no_outputs_deferred():
    """Verdict 12/12 ne doit avoir aucun output deferred."""
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        HABITAT_COMPLETE_PATH,
    )
    if not HABITAT_COMPLETE_PATH.exists():
        pytest.skip("Aucun complete merge encore exécuté.")
    state = json.loads(
        HABITAT_COMPLETE_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History vide.")
    last = state["history"][-1]
    deferred = last.get(
        "outputs_still_deferred_anti_generique_strict_complete"
    ) or {}
    if "12_OF_12" in (last.get("verdict") or ""):
        assert deferred == {}


def test_phase_xxx_duotricicies_complete_status_doctrinal_keys():
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        get_habitat_complete_merge_status,
    )
    s = get_habitat_complete_merge_status()
    assert s.get("v30_lock") == "INVIOLÉ"
    assert s.get("ordre") == (
        "P9_HABITAT_OUTPUTS_COMPLETE_MERGE_Ω")
