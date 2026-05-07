"""test_phase_xxx_octodecies_nasa_ndvi_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour :
  · NASA_NDVI_P0_VALIDATE_Ω_ULTIME
  · NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
Aucun appel HTTP réel exécuté ici (probes RÉELS via curl séparément).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Path injection
sys.path.insert(0, str(Path("/app/backend")))


# ═════════════════════════════════════════════════════════════════════════
# Section 1 — Module structure + registry doctrinal
# ═════════════════════════════════════════════════════════════════════════
def test_nasa_ndvi_module_imports():
    """Le module nasa_ndvi_omega doit s'importer."""
    from engines.v8_institutional.especes import nasa_ndvi_omega
    assert hasattr(nasa_ndvi_omega, "validate_nasa_ndvi_per_species")
    assert hasattr(nasa_ndvi_omega, "activate_nasa_ndvi_hook")
    assert hasattr(nasa_ndvi_omega, "get_nasa_ndvi_hook_status")


def test_nasa_ndvi_modis_products_registry_anti_generique():
    """Le registry MODIS doit contenir UNIQUEMENT les bandes RÉELLES.

    MOD13Q1 : NDVI/EVI/VI_Quality/pixel_reliability + bandes auxiliaires
    MOD15A2H : Lai/Fpar
    MOD17A2H : Gpp/PsnNet
    """
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        MODIS_PRODUCTS_BANDS_REGISTRY,
    )
    assert "MOD13Q1" in MODIS_PRODUCTS_BANDS_REGISTRY
    assert "MOD15A2H" in MODIS_PRODUCTS_BANDS_REGISTRY
    assert "MOD17A2H" in MODIS_PRODUCTS_BANDS_REGISTRY

    mod13 = MODIS_PRODUCTS_BANDS_REGISTRY["MOD13Q1"]
    bands = mod13["available_bands"]
    # Bandes RÉELLES présentes
    assert "250m_16_days_NDVI" in bands
    assert "250m_16_days_EVI" in bands
    assert "250m_16_days_VI_Quality" in bands
    assert "250m_16_days_pixel_reliability" in bands
    # Anti-générique : LAI/FPAR/GPP NE sont PAS dans MOD13Q1
    assert not any("Lai" in b for b in bands), (
        "MOD13Q1 ne doit PAS contenir Lai (anti-générique strict)")
    assert not any("Fpar" in b for b in bands), (
        "MOD13Q1 ne doit PAS contenir Fpar (anti-générique strict)")
    assert not any("Gpp" in b for b in bands), (
        "MOD13Q1 ne doit PAS contenir Gpp (anti-générique strict)")


def test_nasa_ndvi_logical_to_band_mapping_strict():
    """Le mapping logique doit pointer vers le PRODUIT RÉEL."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        NDVI_LOGICAL_TO_BAND,
    )
    assert NDVI_LOGICAL_TO_BAND["NDVI"]["product"] == "MOD13Q1"
    assert NDVI_LOGICAL_TO_BAND["EVI"]["product"] == "MOD13Q1"
    assert NDVI_LOGICAL_TO_BAND["VI_QUALITY"]["product"] == "MOD13Q1"
    # Anti-générique : LAI/FPAR routés vers MOD15A2H (pas MOD13Q1)
    assert NDVI_LOGICAL_TO_BAND["LAI"]["product"] == "MOD15A2H"
    assert NDVI_LOGICAL_TO_BAND["FPAR"]["product"] == "MOD15A2H"
    # GPP routé vers MOD17A2H
    assert NDVI_LOGICAL_TO_BAND["GPP"]["product"] == "MOD17A2H"


def test_nasa_ndvi_validation_path_under_pipelines():
    """Persistance dans /app/backend/data/pipelines/nasa_ndvi/."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        NASA_NDVI_VALIDATION_PATH, NASA_NDVI_HOOK_ACTIVATION_PATH,
    )
    assert "data/pipelines/nasa_ndvi" in str(NASA_NDVI_VALIDATION_PATH)
    assert "data/pipelines/nasa_ndvi" in str(
        NASA_NDVI_HOOK_ACTIVATION_PATH)
    assert str(NASA_NDVI_VALIDATION_PATH).endswith(
        "_overlay.json")


# ═════════════════════════════════════════════════════════════════════════
# Section 2 — Validation des coords + guardrails
# ═════════════════════════════════════════════════════════════════════════
def test_validate_requires_guardrails_enforced():
    """Sans guardrails ENFORCED, validate doit lever GuardrailsNotEnforced.

    Note : on monkeypatch is_guardrails_enforced pour ce test
    spécifique sans toucher l'état global.
    """
    from engines.v8_institutional.especes import (
        nasa_ndvi_omega, pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            nasa_ndvi_omega.validate_nasa_ndvi_per_species(
                species_coordinates={"x": {"lat": 46.0, "lon": -71.0}},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_rejects_empty_species_coordinates():
    """species_coordinates vide doit lever ValueError."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        validate_nasa_ndvi_per_species,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    # Force ENFORCED state pour ce test
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        with pytest.raises(ValueError, match="SPECIES_COORDINATES_REQUIRED"):
            validate_nasa_ndvi_per_species(
                species_coordinates={},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_rejects_invalid_coords_lat_out_of_range():
    """Lat hors [-90, 90] doit lever ValueError."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        validate_nasa_ndvi_per_species,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        with pytest.raises(ValueError, match="COORDS_INVALID"):
            validate_nasa_ndvi_per_species(
                species_coordinates={
                    "espece_a": {"lat": 999.0, "lon": -71.0}},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


# ═════════════════════════════════════════════════════════════════════════
# Section 3 — Stats anti-générique (rejet nodata, pas d'imputation)
# ═════════════════════════════════════════════════════════════════════════
def test_compute_stats_rejects_nodata_no_imputation():
    """Les valeurs nodata=-3000 doivent être REJETÉES (pas imputées)."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        _compute_band_stats_from_modis_subset,
    )
    subset = [
        {"data": [-3000], "calendar_date": "2025-01-01"},
        {"data": [5000], "calendar_date": "2025-01-17"},
        {"data": [7500], "calendar_date": "2025-02-02"},
        {"data": [-3000], "calendar_date": "2025-02-18"},
    ]
    stats = _compute_band_stats_from_modis_subset(
        subset, scale_factor=0.0001, nodata_value=-3000)
    assert stats["n_total"] == 4
    assert stats["n_valid"] == 2
    assert stats["n_nodata"] == 2
    # Anti-générique : aucune imputation, mean calculé sur valides only
    assert stats["mean"] == round(
        ((5000 + 7500) / 2) * 0.0001, 4)
    assert stats["min"] == round(5000 * 0.0001, 4)
    assert stats["max"] == round(7500 * 0.0001, 4)


def test_compute_stats_all_nodata_returns_no_valid():
    """Subset 100% nodata doit retourner n_valid=0 sans imputation."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        _compute_band_stats_from_modis_subset,
    )
    subset = [
        {"data": [-3000], "calendar_date": "2025-01-01"},
        {"data": [-3000], "calendar_date": "2025-01-17"},
    ]
    stats = _compute_band_stats_from_modis_subset(
        subset, scale_factor=0.0001)
    assert stats["n_valid"] == 0
    assert stats["n_nodata"] == 2
    assert stats["min"] is None
    assert stats["max"] is None
    assert stats["mean"] is None
    assert stats["interpretation"] == "no_valid_values"


def test_modis_a_year_doy_format():
    """Format MODIS AYYYYDDD doit être correctement généré."""
    from datetime import datetime, timezone
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        _modis_a_year_doy,
    )
    d = datetime(2025, 1, 1, tzinfo=timezone.utc)
    assert _modis_a_year_doy(d) == "A2025001"
    d2 = datetime(2024, 12, 31, tzinfo=timezone.utc)
    assert _modis_a_year_doy(d2) == "A2024366"  # leap year
    d3 = datetime(2025, 2, 17, tzinfo=timezone.utc)
    assert _modis_a_year_doy(d3) == "A2025048"


# ═════════════════════════════════════════════════════════════════════════
# Section 4 — Hook activate : anti-générique manifest fabriqué REJECTED
# ═════════════════════════════════════════════════════════════════════════
def test_activate_rejects_fabricated_manifest_sha256():
    """Activation sur SHA fabriqué (64 zéros) doit être REJETÉE."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        activate_nasa_ndvi_hook,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        result = activate_nasa_ndvi_hook(
            manifest_sha256="0" * 64,
            reason="test_fabricated_manifest_rejection",
            persist=False,
        )
        assert result["activated"] is False
        assert result["verdict"] == (
            "NASA_NDVI_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
        assert result["anti_generique_strict"] is True
        assert result["v30_lock"] == "INVIOLÉ"
        assert result["no_engine_recompute_triggered"] is True
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_activate_rejects_random_sha256():
    """SHA random non présent dans history doit être REJETÉ."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        activate_nasa_ndvi_hook,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        result = activate_nasa_ndvi_hook(
            manifest_sha256=("a" * 64),
            reason="test_random_sha_rejection",
            persist=False,
        )
        assert result["activated"] is False
        assert "REJECTED" in result["verdict"]
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_find_validated_manifest_returns_none_for_unknown():
    """_find_validated_nasa_ndvi_manifest sur SHA inconnu = None."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        _find_validated_nasa_ndvi_manifest,
    )
    result = _find_validated_nasa_ndvi_manifest("z" * 64)
    assert result is None


def test_get_status_when_no_activation():
    """get_nasa_ndvi_hook_status retourne dict valide même sans
    activation (cas défensif si fichier absent).
    """
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        get_nasa_ndvi_hook_status, NASA_NDVI_HOOK_ACTIVATION_PATH,
    )
    status = get_nasa_ndvi_hook_status()
    # Doit retourner dict avec champs minimaux structurels
    assert "manifest_id" in status
    assert "current_status" in status
    assert "v30_lock" in status
    assert status["v30_lock"] == "INVIOLÉ"
    assert status["current_status"] in (
        "NOT_ACTIVATED", "ACTIVATED_OPERATIONAL")


# ═════════════════════════════════════════════════════════════════════════
# Section 5 — Anti-régression V30_LOCK
# ═════════════════════════════════════════════════════════════════════════
def test_v30_lock_bp135_sha256_unchanged():
    """BP135 SHA-256 ne doit JAMAIS changer après import nasa_ndvi."""
    bp135_path = Path(
        "/app/backend/data/registry_docs/bio_profile_omega_135/"
        "BIO_PROFILE_OMEGA_135_OFFICIAL.json")
    if not bp135_path.exists():
        pytest.skip("BP135 official non présent (déploiement minimal)")
    import hashlib
    sha_before = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    from engines.v8_institutional.especes import nasa_ndvi_omega  # noqa: F401
    sha_after = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    assert sha_before == sha_after, (
        "V30_LOCK VIOLÉ : BP135 SHA-256 a changé après import "
        "nasa_ndvi_omega")


def test_super_engines_omega_logic_not_modified_after_import():
    """super_engines_omega_logic.py ne doit JAMAIS être modifié."""
    sel_path = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "super_engines_omega_logic.py")
    if not sel_path.exists():
        pytest.skip("super_engines_omega_logic absent (env minimal)")
    import hashlib
    sha_before = hashlib.sha256(sel_path.read_bytes()).hexdigest()
    from engines.v8_institutional.especes import nasa_ndvi_omega  # noqa: F401
    sha_after = hashlib.sha256(sel_path.read_bytes()).hexdigest()
    assert sha_before == sha_after


def test_nasa_ndvi_module_does_not_import_super_engines_logic():
    """nasa_ndvi_omega ne doit PAS importer super_engines_omega_logic.

    Anti-régression doctrinale : le module NASA_NDVI ne doit pas
    déclencher de recalcul moteur (NO_ENGINE_RECOMPUTE_TRIGGERED).
    """
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "nasa_ndvi_omega.py").read_text(encoding="utf-8")
    assert "super_engines_omega_logic" not in src, (
        "NASA_NDVI ne doit PAS importer super_engines_omega_logic")
