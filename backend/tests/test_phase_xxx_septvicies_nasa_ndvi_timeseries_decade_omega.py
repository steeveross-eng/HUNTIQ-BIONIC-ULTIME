"""test_phase_xxx_septvicies_nasa_ndvi_timeseries_decade_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour NASA_NDVI_TIMESERIES_DECADE_Ω.

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("/app/backend")))


def test_module_imports():
    """Module nasa_ndvi_timeseries_decade_omega doit s'importer."""
    from engines.v8_institutional.especes import (
        nasa_ndvi_timeseries_decade_omega,
    )
    assert hasattr(nasa_ndvi_timeseries_decade_omega,
                   "validate_nasa_ndvi_timeseries_decade")
    assert hasattr(nasa_ndvi_timeseries_decade_omega,
                   "get_ndvi_decade_status")


def test_seasonal_windows_2_doctrinal():
    """2 fenêtres saisonnières doctrinales : summer + fall."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        SEASONAL_WINDOWS_DOCTRINAL,
    )
    assert "summer_growing_peak" in SEASONAL_WINDOWS_DOCTRINAL
    assert "fall_pre_rut" in SEASONAL_WINDOWS_DOCTRINAL
    summer = SEASONAL_WINDOWS_DOCTRINAL["summer_growing_peak"]
    assert summer["max_tiles_mod13q1"] == 6
    assert "Borowik" in summer["primary_reference"]
    fall = SEASONAL_WINDOWS_DOCTRINAL["fall_pre_rut"]
    assert fall["max_tiles_mod13q1"] == 4
    assert "Hebblewhite" in fall["primary_reference"]


def test_modis_a_year_doy_format():
    """Format AYYYY{DDD:03d} strict."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        _modis_a_year_doy,
    )
    assert _modis_a_year_doy(2024, 153) == "A2024153"
    assert _modis_a_year_doy(2024, 5) == "A2024005"


def test_aggregate_yearly_stats_decade_mean_correct():
    """Agrégation décade : mean, std, trend correctement calculés."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        _aggregate_yearly_stats,
    )
    bands = {
        2020: {"NDVI": {"valid": True, "stats": {
            "mean": 0.5, "max": 0.7}}},
        2021: {"NDVI": {"valid": True, "stats": {
            "mean": 0.55, "max": 0.72}}},
        2022: {"NDVI": {"valid": True, "stats": {
            "mean": 0.6, "max": 0.75}}},
        2023: {"NDVI": {"valid": True, "stats": {
            "mean": 0.58, "max": 0.74}}},
        2024: {"NDVI": {"valid": True, "stats": {
            "mean": 0.62, "max": 0.78}}},
    }
    res = _aggregate_yearly_stats(bands)
    assert res["valid"] is True
    assert res["n_years_valid"] == 5
    # Mean = (0.5+0.55+0.6+0.58+0.62)/5 = 0.57
    assert res["decade_mean_ndvi"] == 0.57
    assert res["decade_max_ndvi"] == 0.78
    assert res["trend_slope_ndvi_per_year"] is not None
    # Trend > 0 (croissant)
    assert res["trend_slope_ndvi_per_year"] > 0


def test_aggregate_yearly_stats_no_data_invalid():
    """Aucune année valide → invalid."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        _aggregate_yearly_stats,
    )
    bands = {
        2020: {"NDVI": {"valid": False}},
        2021: {"NDVI": {"valid": False}},
    }
    res = _aggregate_yearly_stats(bands)
    assert res["valid"] is False
    assert res["n_years_valid"] == 0


def test_compute_feeding_zones_optimal_consistent():
    """NDVI optimum + low std → HIGH_QUALITY_FEEDING_ZONE."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        _compute_feeding_zones_summer,
    )
    summer_stats = {
        "valid": True,
        "n_years_valid": 5,
        "decade_mean_ndvi": 0.55,
        "decade_std_ndvi": 0.05,
    }
    thresholds = {
        "ndvi_optimal_low": 0.4,
        "ndvi_optimal_high": 0.7,
    }
    res = _compute_feeding_zones_summer(summer_stats, thresholds)
    assert res["regime"] == "HIGH_QUALITY_FEEDING_ZONE_DECADE"
    assert res["value"] >= 75.0
    assert "Borowik" in res["primary_reference"]


def test_compute_feeding_zones_no_data_deferred():
    """Sans summer data → DEFERRED."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        _compute_feeding_zones_summer,
    )
    res = _compute_feeding_zones_summer(
        {"valid": False}, {"ndvi_optimal_low": 0.4,
                            "ndvi_optimal_high": 0.7})
    assert res["value"] is None
    assert "DEFERRED" in res["regime"]


def test_compute_rut_proxy_optimal_pre_rut():
    """NDVI fall 0.3-0.5 + low std → OPTIMAL_RUT_PRE_PHENOLOGY."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        _compute_rut_phenology_proxy,
    )
    fall_stats = {
        "valid": True,
        "n_years_valid": 5,
        "decade_mean_ndvi": 0.4,
        "decade_std_ndvi": 0.03,
    }
    res = _compute_rut_phenology_proxy(fall_stats, "cerf")
    assert res["regime"] == "OPTIMAL_RUT_PRE_PHENOLOGY"
    assert res["value"] >= 90.0
    assert "PROXY" in res["doctrinal_caveat"]


def test_compute_rut_proxy_dormant_winter():
    """NDVI fall < 0.3 → DORMANT_LATE_RUT_PROXY."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        _compute_rut_phenology_proxy,
    )
    res = _compute_rut_phenology_proxy(
        {"valid": True, "n_years_valid": 5,
         "decade_mean_ndvi": 0.15, "decade_std_ndvi": 0.05},
        "orignal")
    assert res["regime"] == "DORMANT_LATE_RUT_PROXY"
    assert res["value"] < 70.0


def test_validate_requires_guardrails_enforced():
    """Sans guardrails ENFORCED, lève GuardrailsNotEnforced."""
    from engines.v8_institutional.especes import (
        nasa_ndvi_timeseries_decade_omega,
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            nasa_ndvi_timeseries_decade_omega.validate_nasa_ndvi_timeseries_decade(  # noqa: E501
                site_coordinates={"x": {"lat": 46.0, "lon": -71.0}},
                persist=False)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_rejects_empty_coords():
    """Empty coords → ValueError."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        validate_nasa_ndvi_timeseries_decade,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        with pytest.raises(
                ValueError, match="SITE_COORDINATES_REQUIRED"):
            validate_nasa_ndvi_timeseries_decade(
                site_coordinates={}, persist=False)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validation_path_under_pipelines():
    """Persistance dans data/pipelines/nasa_ndvi_decade/."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        NDVI_DECADE_VALIDATION_PATH,
    )
    assert "data/pipelines/nasa_ndvi_decade" in str(
        NDVI_DECADE_VALIDATION_PATH)


def test_get_status_returns_valid_dict():
    """get_status retourne dict valide."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        get_ndvi_decade_status,
    )
    s = get_ndvi_decade_status()
    assert "manifest_id" in s
    assert "current_status" in s
    assert s["v30_lock"] == "INVIOLÉ"


def test_module_does_not_import_super_engines_logic():
    """Anti-régression : NO_ENGINE_RECOMPUTE_TRIGGERED."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "nasa_ndvi_timeseries_decade_omega.py").read_text(
            encoding="utf-8")
    assert "super_engines_omega_logic" not in src


def test_v30_lock_bp135_sha256_unchanged_after_import():
    """BP135 SHA-256 ne doit JAMAIS changer."""
    bp135_path = Path(
        "/app/backend/data/registry_docs/bio_profile_omega_135/"
        "BIO_PROFILE_OMEGA_135_OFFICIAL.json")
    if not bp135_path.exists():
        pytest.skip("BP135 official non présent")
    import hashlib
    sha_before = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    from engines.v8_institutional.especes import (  # noqa: F401
        nasa_ndvi_timeseries_decade_omega,
    )
    sha_after = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    assert sha_before == sha_after
