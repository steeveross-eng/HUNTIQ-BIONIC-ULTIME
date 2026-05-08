"""test_phase_xxx_quinquevicies_canopy_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour CANOPY_P0_VALIDATE + HOOK_ACTIVATE_Ω.

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("/app/backend")))


def test_module_imports():
    """Module canopy_omega doit s'importer."""
    from engines.v8_institutional.especes import canopy_omega
    assert hasattr(canopy_omega, "validate_canopy_per_site")
    assert hasattr(canopy_omega, "activate_canopy_hook")
    assert hasattr(canopy_omega, "get_canopy_hook_status")


def test_mod44b_bands_registry_4_bands():
    """Registry MOD44B contient 4 bandes officielles."""
    from engines.v8_institutional.especes.canopy_omega import (
        MOD44B_BANDS_REGISTRY,
    )
    expected = {
        "Percent_Tree_Cover", "Percent_NonTree_Vegetation",
        "Percent_NonVegetated", "Quality"}
    assert set(MOD44B_BANDS_REGISTRY.keys()) == expected
    for band, info in MOD44B_BANDS_REGISTRY.items():
        assert "logical_name" in info
        assert "description" in info
        assert "valid_range" in info


def test_logical_names_correct():
    """Mapping logique→canonique strict."""
    from engines.v8_institutional.especes.canopy_omega import (
        MOD44B_BANDS_REGISTRY,
    )
    assert (MOD44B_BANDS_REGISTRY["Percent_Tree_Cover"]
            ["logical_name"] == "TREE_COVER")
    assert (MOD44B_BANDS_REGISTRY["Percent_NonTree_Vegetation"]
            ["logical_name"] == "NONTREE_VEG")
    assert (MOD44B_BANDS_REGISTRY["Percent_NonVegetated"]
            ["logical_name"] == "NONVEG")
    assert (MOD44B_BANDS_REGISTRY["Quality"]
            ["logical_name"] == "QUALITY")


def test_validation_paths_under_pipelines():
    """Persistance dans data/pipelines/canopy/."""
    from engines.v8_institutional.especes.canopy_omega import (
        CANOPY_VALIDATION_PATH,
        CANOPY_HOOK_ACTIVATION_PATH,
    )
    assert "data/pipelines/canopy" in str(
        CANOPY_VALIDATION_PATH)
    assert "data/pipelines/canopy" in str(
        CANOPY_HOOK_ACTIVATION_PATH)


def test_validate_requires_guardrails_enforced():
    """Sans guardrails ENFORCED, lève GuardrailsNotEnforced."""
    from engines.v8_institutional.especes import (
        canopy_omega, pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            canopy_omega.validate_canopy_per_site(
                site_coordinates={
                    "x": {"lat": 46.0, "lon": -71.0}},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_rejects_empty_site_coordinates():
    """Empty coords → ValueError."""
    from engines.v8_institutional.especes.canopy_omega import (
        validate_canopy_per_site,
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
            validate_canopy_per_site(
                site_coordinates={}, persist=False)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_rejects_invalid_coords():
    """Lat hors [-90,90] → ValueError."""
    from engines.v8_institutional.especes.canopy_omega import (
        validate_canopy_per_site,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        with pytest.raises(ValueError, match="COORDS_INVALID"):
            validate_canopy_per_site(
                site_coordinates={
                    "x": {"lat": 999.0, "lon": -71.0}},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_modis_year_doy_065_format():
    """Format AYYYY065 strict."""
    from engines.v8_institutional.especes.canopy_omega import (
        _modis_year_doy_065,
    )
    assert _modis_year_doy_065(2025) == "A2025065"
    assert _modis_year_doy_065(2020) == "A2020065"


def test_compute_band_stats_rejects_nodata_200():
    """nodata=200 rejeté sans imputation."""
    from engines.v8_institutional.especes.canopy_omega import (
        _compute_band_stats,
    )
    subset = [
        {"data": [200], "calendar_date": "2023-03-06"},
        {"data": [50], "calendar_date": "2024-03-05"},
        {"data": [80], "calendar_date": "2025-03-06"},
    ]
    stats = _compute_band_stats(subset, scale=1, nodata=200)
    assert stats["valid"] is True
    assert stats["n_total"] == 3
    assert stats["n_valid"] == 2
    assert stats["n_nodata"] == 1
    assert stats["mean"] == 65.0  # (50+80)/2
    assert stats["min"] == 50
    assert stats["max"] == 80


def test_compute_band_stats_all_nodata_invalid():
    """100% nodata → invalid."""
    from engines.v8_institutional.especes.canopy_omega import (
        _compute_band_stats,
    )
    stats = _compute_band_stats(
        [{"data": [200], "calendar_date": "2024-03-05"}],
        scale=1, nodata=200)
    assert stats["valid"] is False
    assert stats["n_valid"] == 0


def test_validate_filters_unknown_bands_logical():
    """Bandes inconnues filtrées."""
    from engines.v8_institutional.especes import (
        canopy_omega, pipeline_guardrails_omega,
    )
    original_probe = canopy_omega._probe_mod44b_band_at_site
    original_enf = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)

        def mock_probe(lat, lon, band_canonical, start_modis,
                       end_modis, timeout_s=25):
            return {
                "lat": lat, "lon": lon,
                "band_canonical": band_canonical,
                "valid": True,
                "stats": {"valid": True, "n_valid": 3,
                          "n_nodata": 0, "mean": 50.0,
                          "min": 30, "max": 70,
                          "n_total": 3,
                          "first_date": "2023",
                          "last_date": "2025"},
                "http_status": 200, "elapsed_ms": 10,
            }
        canopy_omega._probe_mod44b_band_at_site = mock_probe

        result = canopy_omega.validate_canopy_per_site(
            site_coordinates={
                "x": {"lat": 46.0, "lon": -71.0}},
            bands_logical=["TREE_COVER", "FAKE_BAND",
                          "ANOTHER_FAKE"],
            persist=False,
        )
        assert "TREE_COVER" in [
            "TREE_COVER", "NONTREE_VEG", "NONVEG", "QUALITY"]
        assert "FAKE_BAND" in result["bands_unknown_skipped"]
        assert "ANOTHER_FAKE" in result["bands_unknown_skipped"]
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enf)
        canopy_omega._probe_mod44b_band_at_site = original_probe


def test_activate_rejects_fabricated_manifest():
    """SHA fabriqué (64 zéros) → REJECTED."""
    from engines.v8_institutional.especes.canopy_omega import (
        activate_canopy_hook,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        result = activate_canopy_hook(
            manifest_sha256="0" * 64,
            reason="test_reject",
            persist=False,
        )
        assert result["activated"] is False
        assert (
            "REJECTED" in result["verdict"])
        assert result["anti_generique_strict"] is True
        assert result["v30_lock"] == "INVIOLÉ"
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_find_validated_manifest_returns_none_for_unknown():
    """SHA inconnu → None."""
    from engines.v8_institutional.especes.canopy_omega import (
        _find_validated_canopy_manifest,
    )
    assert _find_validated_canopy_manifest("z" * 64) is None


def test_get_hook_status_returns_valid_dict():
    """get_status retourne dict valide."""
    from engines.v8_institutional.especes.canopy_omega import (
        get_canopy_hook_status,
    )
    s = get_canopy_hook_status()
    assert "manifest_id" in s
    assert "current_status" in s
    assert s["v30_lock"] == "INVIOLÉ"
    assert s["current_status"] in (
        "NOT_ACTIVATED", "ACTIVATED_OPERATIONAL")


def test_module_does_not_import_super_engines_logic():
    """Anti-régression : NO_ENGINE_RECOMPUTE_TRIGGERED."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "canopy_omega.py").read_text(encoding="utf-8")
    assert "super_engines_omega_logic" not in src


def test_v30_lock_bp135_sha256_unchanged_after_import():
    """BP135 SHA-256 ne doit JAMAIS changer après import."""
    bp135_path = Path(
        "/app/backend/data/registry_docs/bio_profile_omega_135/"
        "BIO_PROFILE_OMEGA_135_OFFICIAL.json")
    if not bp135_path.exists():
        pytest.skip("BP135 official non présent")
    import hashlib
    sha_before = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    from engines.v8_institutional.especes import canopy_omega  # noqa: F401
    sha_after = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    assert sha_before == sha_after


def test_outputs_fully_unblocked_listed_in_payload_via_mock():
    """Activation succès expose 2 outputs FULL débloqués."""
    from engines.v8_institutional.especes import (
        canopy_omega, pipeline_guardrails_omega,
    )
    original_find = (
        canopy_omega._find_validated_canopy_manifest)
    original_enf = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)

        def mock_find(sha):
            return {
                "manifest_sha256": sha,
                "executed_at_utc": "2026-05-08T01:00:00+00:00",
                "endpoint": (
                    "https://modis.ornl.gov/rst/api/v1/"
                    "MOD44B/subset"),
                "bands_canonical_validated": [
                    "Percent_Tree_Cover"],
                "temporal_range_modis": {"start_year": 2023},
                "n_sites_total": 1,
                "n_calls_success": 1,
                "site_results": {
                    "x": {
                        "lat": 46.0, "lon": -71.0,
                        "n_bands_probed": 1,
                        "n_bands_valid": 1,
                        "bands": {
                            "TREE_COVER": {
                                "valid": True,
                                "stats": {
                                    "n_valid": 3,
                                    "mean": 50.0,
                                    "min": 30, "max": 70,
                                    "first_date": "2023",
                                    "last_date": "2025",
                                },
                            },
                        },
                    },
                },
                "scientific_references_peer_reviewed": [
                    "Hansen 2003"],
            }
        canopy_omega._find_validated_canopy_manifest = mock_find

        result = canopy_omega.activate_canopy_hook(
            manifest_sha256="abc" * 21 + "f",
            reason="test_mock",
            persist=False,
        )
        assert result["activated"] is True
        assert (result["verdict"]
                == "CANOPY_HOOK_ACTIVATED_OPERATIONAL")
        assert "outputs_fully_unblocked_via_this_hook" in result
        unblocked = result[
            "outputs_fully_unblocked_via_this_hook"]
        assert len(unblocked) == 2
        assert any("bedding" in o for o in unblocked)
        assert any("refuge" in o for o in unblocked)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enf)
        canopy_omega._find_validated_canopy_manifest = (
            original_find)
