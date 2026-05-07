"""test_phase_xxx_vicies_usgs_soil_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour USGS_SOIL_P0_VALIDATE_Ω + HOOK_ACTIVATE_Ω.

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
Aucun appel HTTP réel exécuté ici (probes RÉELS via curl séparément).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("/app/backend")))


# ═════════════════════════════════════════════════════════════════════════
# Section 1 — Module structure + registry SoilGrids
# ═════════════════════════════════════════════════════════════════════════
def test_usgs_soil_module_imports():
    """Module usgs_soil_omega doit exposer signatures requises."""
    from engines.v8_institutional.especes import usgs_soil_omega
    assert hasattr(usgs_soil_omega,
                   "validate_usgs_soil_per_species")
    assert hasattr(usgs_soil_omega, "activate_usgs_soil_hook")
    assert hasattr(usgs_soil_omega, "get_usgs_soil_hook_status")


def test_soilgrids_registry_6_properties_min():
    """Registry SoilGrids doit contenir au moins 6 propriétés clés."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        SOILGRIDS_PROPERTIES_REGISTRY,
    )
    expected_min = {
        "phh2o", "cec", "nitrogen", "clay", "sand", "soc"}
    assert expected_min.issubset(
        set(SOILGRIDS_PROPERTIES_REGISTRY.keys()))
    for prop, info in SOILGRIDS_PROPERTIES_REGISTRY.items():
        assert "description" in info
        assert "d_factor" in info
        assert "target_units" in info
        assert "depth_layers_cm" in info
        assert info["d_factor"] > 0


def test_terrestrial_offsets_4_cardinal_directions():
    """4 offsets cardinaux séquentiels (anti-générique)."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        TERRESTRIAL_OFFSETS_CARDINAL,
    )
    assert len(TERRESTRIAL_OFFSETS_CARDINAL) == 4
    expected = {(+0.05, 0.0), (-0.05, 0.0),
                (0.0, +0.05), (0.0, -0.05)}
    assert set(TERRESTRIAL_OFFSETS_CARDINAL) == expected


def test_validation_path_under_pipelines():
    """Persistance dans /app/backend/data/pipelines/usgs_soil/."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        USGS_SOIL_VALIDATION_PATH, USGS_SOIL_HOOK_ACTIVATION_PATH,
    )
    assert "data/pipelines/usgs_soil" in str(
        USGS_SOIL_VALIDATION_PATH)
    assert "data/pipelines/usgs_soil" in str(
        USGS_SOIL_HOOK_ACTIVATION_PATH)


# ═════════════════════════════════════════════════════════════════════════
# Section 2 — Validation coords + guardrails
# ═════════════════════════════════════════════════════════════════════════
def test_validate_requires_guardrails_enforced():
    """Sans guardrails ENFORCED, lève GuardrailsNotEnforced."""
    from engines.v8_institutional.especes import (
        usgs_soil_omega, pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            usgs_soil_omega.validate_usgs_soil_per_species(
                species_coordinates={
                    "x": {"lat": 46.0, "lon": -71.0}},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_rejects_empty_species_coordinates():
    """species_coordinates vide → ValueError."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        validate_usgs_soil_per_species,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        with pytest.raises(
                ValueError, match="SPECIES_COORDINATES_REQUIRED"):
            validate_usgs_soil_per_species(
                species_coordinates={},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_rejects_invalid_coords():
    """Coords invalides → ValueError."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        validate_usgs_soil_per_species,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        with pytest.raises(ValueError, match="COORDS_INVALID"):
            validate_usgs_soil_per_species(
                species_coordinates={
                    "espece_a": {"lat": 999.0, "lon": -71.0}},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


# ═════════════════════════════════════════════════════════════════════════
# Section 3 — Helpers extraction SoilGrids
# ═════════════════════════════════════════════════════════════════════════
def test_extract_property_mean_with_d_factor_division():
    """Extraction applique le d_factor (e.g., phh2o×10 → pH)."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        _extract_property_mean_from_soilgrids,
    )
    parsed = {
        "properties": {
            "layers": [
                {
                    "name": "phh2o",
                    "unit_measure": {"d_factor": 10},
                    "depths": [
                        {"label": "0-5cm",
                         "values": {"mean": 60}},
                    ],
                },
            ],
        },
    }
    val = _extract_property_mean_from_soilgrids(
        parsed, "phh2o", "0-5cm")
    assert val == 6.0  # 60 / d_factor 10 → pH 6.0


def test_extract_property_mean_returns_none_for_missing():
    """Propriété/profondeur inexistante → None (pas d'imputation)."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        _extract_property_mean_from_soilgrids,
    )
    parsed = {"properties": {"layers": []}}
    assert _extract_property_mean_from_soilgrids(
        parsed, "phh2o", "0-5cm") is None


def test_extract_property_mean_returns_none_for_null_value():
    """mean=null → None (anti-générique : pas d'imputation)."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        _extract_property_mean_from_soilgrids,
    )
    parsed = {
        "properties": {
            "layers": [
                {
                    "name": "phh2o",
                    "unit_measure": {"d_factor": 10},
                    "depths": [
                        {"label": "0-5cm",
                         "values": {"mean": None}},
                    ],
                },
            ],
        },
    }
    assert _extract_property_mean_from_soilgrids(
        parsed, "phh2o", "0-5cm") is None


# ═════════════════════════════════════════════════════════════════════════
# Section 4 — Hook activate : anti-générique manifest fabriqué REJECTED
# ═════════════════════════════════════════════════════════════════════════
def test_activate_rejects_fabricated_manifest_sha256():
    """SHA fabriqué (64 zéros) doit être REJETÉ."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        activate_usgs_soil_hook,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        result = activate_usgs_soil_hook(
            manifest_sha256="0" * 64,
            reason="test_fabricated_manifest_rejection",
            persist=False,
        )
        assert result["activated"] is False
        assert result["verdict"] == (
            "USGS_SOIL_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
        assert result["anti_generique_strict"] is True
        assert result["v30_lock"] == "INVIOLÉ"
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_find_validated_manifest_returns_none_for_unknown():
    """SHA inconnu → None."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        _find_validated_usgs_soil_manifest,
    )
    result = _find_validated_usgs_soil_manifest("z" * 64)
    assert result is None


def test_get_status_when_no_activation():
    """get_usgs_soil_hook_status retourne dict valide."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        get_usgs_soil_hook_status,
    )
    status = get_usgs_soil_hook_status()
    assert "manifest_id" in status
    assert "current_status" in status
    assert "v30_lock" in status
    assert status["v30_lock"] == "INVIOLÉ"
    assert status["current_status"] in (
        "NOT_ACTIVATED", "ACTIVATED_OPERATIONAL")


# ═════════════════════════════════════════════════════════════════════════
# Section 5 — Pivot doctrinal anti-générique
# ═════════════════════════════════════════════════════════════════════════
def test_pivot_doctrinal_documented_in_module_source():
    """Le pivot USGS→SoilGrids ISRIC est documenté dans le module."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "usgs_soil_omega.py").read_text(encoding="utf-8")
    # Citations peer-reviewed obligatoires
    assert "Hengl" in src
    assert "Poggio" in src
    assert "10.1371/journal.pone.0169748" in src
    assert "10.5194/soil-7-217-2021" in src
    # Pivot explicite documenté
    assert "SOILGRIDS_ISRIC" in src
    assert "USGS_NGS" in src or "US continental" in src


def test_pivot_doctrinal_in_validate_payload_anti_generique():
    """Le payload VALIDATE expose le pivot doctrinal anti-générique."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        validate_usgs_soil_per_species,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega, usgs_soil_omega,
    )
    # Mock le HTTP probe pour test offline
    original_probe = (
        usgs_soil_omega._probe_with_terrestrial_offset_fallback)
    original_enforced = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)

        def mock_probe(lat, lon, props, depth_label="0-5cm",
                       timeout_s=15):
            return {
                "coord_origin": {"lat": lat, "lon": lon},
                "coord_used": {"lat": lat, "lon": lon},
                "offset_applied": {"d_lat": 0.0, "d_lon": 0.0},
                "offset_strategy": "ORIGINAL_COORD_VALID",
                "fallback_attempts": [],
                "probe_record": {
                    "lat": lat, "lon": lon, "url": "mock",
                    "http_status": 200, "elapsed_ms": 10.0,
                    "reason": None,
                    "extracted_properties": {p: 5.5 for p in props},
                    "n_properties_valid": len(props),
                    "n_properties_requested": len(props),
                },
                "valid": True,
            }
        usgs_soil_omega._probe_with_terrestrial_offset_fallback = (
            mock_probe)

        result = validate_usgs_soil_per_species(
            species_coordinates={
                "espece_a": {"lat": 46.0, "lon": -71.0}},
            properties=["phh2o", "cec"],
            persist=False,
        )
        assert "pivot_doctrinal_anti_generique" in result
        pivot = result["pivot_doctrinal_anti_generique"]
        assert "Hengl" in pivot["scientific_reference_primary"]
        assert "Poggio" in pivot["scientific_reference_v2"]
        assert (result["provider_logical"] == "USGS_SOIL")
        assert (result["provider_physical"]
                == "SOILGRIDS_ISRIC")
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enforced)
        usgs_soil_omega._probe_with_terrestrial_offset_fallback = (
            original_probe)


def test_validate_filters_unknown_properties():
    """Propriétés inconnues du registry filtrées (anti-générique)."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        validate_usgs_soil_per_species,
        SOILGRIDS_PROPERTIES_REGISTRY,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega, usgs_soil_omega,
    )
    original_probe = (
        usgs_soil_omega._probe_with_terrestrial_offset_fallback)
    original_enforced = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)

        def mock_probe(lat, lon, props, depth_label="0-5cm",
                       timeout_s=15):
            return {
                "coord_origin": {"lat": lat, "lon": lon},
                "coord_used": {"lat": lat, "lon": lon},
                "offset_applied": {"d_lat": 0.0, "d_lon": 0.0},
                "offset_strategy": "ORIGINAL_COORD_VALID",
                "fallback_attempts": [],
                "probe_record": {
                    "n_properties_valid": len(props),
                    "n_properties_requested": len(props),
                },
                "valid": True,
            }
        usgs_soil_omega._probe_with_terrestrial_offset_fallback = (
            mock_probe)

        result = validate_usgs_soil_per_species(
            species_coordinates={
                "x": {"lat": 46.0, "lon": -71.0}},
            properties=["phh2o", "FAKE_PROP_99",
                        "ANOTHER_FAKE"],
            persist=False,
        )
        assert "phh2o" in result[
            "properties_validated_in_registry"]
        assert "FAKE_PROP_99" in result[
            "properties_unknown_skipped"]
        assert "ANOTHER_FAKE" in result[
            "properties_unknown_skipped"]
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enforced)
        usgs_soil_omega._probe_with_terrestrial_offset_fallback = (
            original_probe)


# ═════════════════════════════════════════════════════════════════════════
# Section 6 — Anti-régression V30_LOCK
# ═════════════════════════════════════════════════════════════════════════
def test_module_does_not_import_super_engines_logic():
    """Anti-régression doctrinale : NO_ENGINE_RECOMPUTE_TRIGGERED."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "usgs_soil_omega.py").read_text(encoding="utf-8")
    assert "super_engines_omega_logic" not in src


def test_v30_lock_bp135_sha256_unchanged_after_import():
    """BP135 SHA-256 ne doit JAMAIS changer après import usgs_soil."""
    bp135_path = Path(
        "/app/backend/data/registry_docs/bio_profile_omega_135/"
        "BIO_PROFILE_OMEGA_135_OFFICIAL.json")
    if not bp135_path.exists():
        pytest.skip("BP135 official non présent")
    import hashlib
    sha_before = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    from engines.v8_institutional.especes import (
        usgs_soil_omega,
    )  # noqa: F401
    sha_after = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    assert sha_before == sha_after


def test_naming_neutral_no_excluded_keywords_in_module():
    """Le module ne doit contenir aucun mot-clé exclu BCE-4X."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "usgs_soil_omega.py").read_text(encoding="utf-8").lower()
    excluded = ["leaflet", "mapbox", "stands_map",
                "hunting_path", "heatmap_layer", "bionic_zone"]
    # Note: 'corridor', 'territoire', 'waypoint' sont autorisés en
    # docstrings/commentaires si dans contexte scientifique pertinent
    for kw in excluded:
        assert kw not in src, (
            f"Excluded keyword '{kw}' found in module")


def test_validate_persists_in_dedicated_pipeline_directory():
    """La persistance se fait dans data/pipelines/usgs_soil/, pas
    dans bio_profile_omega_135 (V30_LOCK)."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        USGS_SOIL_ROOT, USGS_SOIL_VALIDATION_PATH,
    )
    assert "pipelines/usgs_soil" in str(USGS_SOIL_ROOT)
    assert "registry_docs" not in str(USGS_SOIL_ROOT)
    assert str(USGS_SOIL_VALIDATION_PATH).startswith(
        str(USGS_SOIL_ROOT))
