"""test_phase_xxx_duovicies_opentopography_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour OPENTOPOGRAPHY_P0_VALIDATE_Ω.

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
Aucun appel HTTP réel exécuté ici (probes RÉELS via curl séparément).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("/app/backend")))


# Charge .env vars manuellement si pas déjà dans environ
@pytest.fixture(autouse=True)
def _load_opentopography_key_from_env_file():
    """Charge OPENTOPOGRAPHY_API_KEY depuis backend/.env si absent."""
    if not os.environ.get("OPENTOPOGRAPHY_API_KEY"):
        env_path = Path("/app/backend/.env")
        if env_path.exists():
            for line in env_path.read_text(
                    encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("OPENTOPOGRAPHY_API_KEY="):
                    os.environ["OPENTOPOGRAPHY_API_KEY"] = (
                        line.split("=", 1)[1].strip())
                    break
    yield


# ═════════════════════════════════════════════════════════════════════════
# Section 1 — Module structure + DEM registry
# ═════════════════════════════════════════════════════════════════════════
def test_opentopography_module_imports():
    """Module opentopography_omega doit exposer signatures."""
    from engines.v8_institutional.especes import (
        opentopography_omega,
    )
    assert hasattr(opentopography_omega,
                   "validate_opentopography_per_site")
    assert hasattr(opentopography_omega,
                   "get_opentopography_validation_status")


def test_dem_datasets_registry_6_datasets_min():
    """Registry DEM doit contenir au moins 6 datasets connus."""
    from engines.v8_institutional.especes.opentopography_omega import (
        DEM_DATASETS_REGISTRY,
    )
    expected_min = {
        "SRTMGL3", "SRTMGL1", "NASADEM",
        "AW3D30", "COP30"}
    assert expected_min.issubset(set(DEM_DATASETS_REGISTRY.keys()))
    for dem_name, info in DEM_DATASETS_REGISTRY.items():
        assert "description" in info
        assert "resolution_m_approx" in info
        assert "lat_coverage_deg" in info
        assert "license" in info
        assert "primary_reference" in info
        assert info["resolution_m_approx"] > 0


def test_validation_path_under_pipelines():
    """Persistance dans /app/backend/data/pipelines/opentopography/."""
    from engines.v8_institutional.especes.opentopography_omega import (
        OPENTOPOGRAPHY_ROOT, OPENTOPOGRAPHY_VALIDATION_PATH,
    )
    assert "data/pipelines/opentopography" in str(
        OPENTOPOGRAPHY_ROOT)
    assert "data/pipelines/opentopography" in str(
        OPENTOPOGRAPHY_VALIDATION_PATH)


# ═════════════════════════════════════════════════════════════════════════
# Section 2 — API key handling (sécurisé)
# ═════════════════════════════════════════════════════════════════════════
def test_get_api_key_reads_from_env():
    """API key lue depuis os.environ uniquement (anti-générique)."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _get_api_key,
    )
    # La clé est déjà dans .env → doit être disponible
    key = _get_api_key()
    assert isinstance(key, str)
    assert len(key) >= 20


def test_get_api_key_raises_when_missing():
    """Sans env var, lève ValueError (anti-générique strict)."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _get_api_key,
    )
    original = os.environ.get("OPENTOPOGRAPHY_API_KEY")
    try:
        os.environ.pop("OPENTOPOGRAPHY_API_KEY", None)
        with pytest.raises(
                ValueError,
                match="OPENTOPOGRAPHY_API_KEY missing"):
            _get_api_key()
    finally:
        if original is not None:
            os.environ["OPENTOPOGRAPHY_API_KEY"] = original


def test_get_api_key_rejects_placeholder():
    """Placeholder 'YOUR_KEY_HERE' rejeté (anti-générique)."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _get_api_key,
    )
    original = os.environ.get("OPENTOPOGRAPHY_API_KEY")
    try:
        os.environ["OPENTOPOGRAPHY_API_KEY"] = "YOUR_KEY_HERE"
        with pytest.raises(ValueError):
            _get_api_key()
    finally:
        if original is not None:
            os.environ["OPENTOPOGRAPHY_API_KEY"] = original
        else:
            os.environ.pop("OPENTOPOGRAPHY_API_KEY", None)


def test_mask_api_key_hides_middle():
    """Masquage clé (anti-leak logs)."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _mask_api_key,
    )
    masked = _mask_api_key(
        "3dbfddc5f97246eb0be5dfe7272ccc2b")
    assert masked == "3dbf...cc2b"
    assert "ddc5" not in masked
    assert "f972" not in masked


def test_mask_api_key_short_returns_stars():
    """Clé courte/vide → ***."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _mask_api_key,
    )
    assert _mask_api_key("") == "***"
    assert _mask_api_key("abc") == "***"


# ═════════════════════════════════════════════════════════════════════════
# Section 3 — Parser AAIGrid anti-générique
# ═════════════════════════════════════════════════════════════════════════
def test_parse_aaigrid_basic_with_real_values():
    """Parse AAIGrid simple avec valeurs réelles + nodata."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _parse_aaigrid_to_stats,
    )
    aai = """ncols 3
nrows 3
xllcorner -71.25
yllcorner 46.85
cellsize 0.001
NODATA_value 0
100 110 120
105 0 130
110 115 140"""
    stats = _parse_aaigrid_to_stats(aai)
    assert stats["valid"] is True
    assert stats["n_total_pixels"] == 9
    assert stats["n_valid"] == 8  # 1 nodata
    assert stats["n_nodata"] == 1
    assert stats["elevation_min_m"] == 100.0
    assert stats["elevation_max_m"] == 140.0
    # Mean = (100+110+120+105+130+110+115+140)/8 = 116.25
    assert stats["elevation_mean_m"] == 116.25


def test_parse_aaigrid_all_nodata_returns_invalid():
    """100% nodata → valid=False sans imputation."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _parse_aaigrid_to_stats,
    )
    aai = """ncols 2
nrows 2
xllcorner -71.0
yllcorner 47.0
cellsize 0.001
NODATA_value -9999
-9999 -9999
-9999 -9999"""
    stats = _parse_aaigrid_to_stats(aai)
    assert stats["valid"] is False
    assert stats["reason"] == "aaigrid_all_nodata_no_imputation"
    assert stats["n_valid"] == 0
    assert stats["n_nodata"] == 4


def test_parse_aaigrid_empty_returns_invalid():
    """Empty body → invalid."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _parse_aaigrid_to_stats,
    )
    stats = _parse_aaigrid_to_stats("")
    assert stats["valid"] is False
    assert stats["reason"] == "empty_aaigrid_body"


def test_parse_aaigrid_missing_header_returns_invalid():
    """Header incomplet → invalid avec partial header."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _parse_aaigrid_to_stats,
    )
    aai = """ncols 3
nrows 3
xllcorner -71.0"""  # missing cellsize, nodata, body
    stats = _parse_aaigrid_to_stats(aai)
    assert stats["valid"] is False
    assert "aaigrid_header_missing" in stats["reason"]


def test_parse_aaigrid_computes_slope_proxy():
    """Slope proxy en degrés calculé via finite differences."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _parse_aaigrid_to_stats,
    )
    # Grille avec gradient marqué
    aai = """ncols 3
nrows 3
xllcorner -71.0
yllcorner 47.0
cellsize 0.001
NODATA_value -9999
100 100 100
200 200 200
300 300 300"""
    stats = _parse_aaigrid_to_stats(aai)
    assert stats["valid"] is True
    # Pente Y=100/cell → ~80° si cell ~10m, mais cell=0.001° lat≈111m
    # → slope = atan(100/111) ≈ 42°
    assert stats["slope_mean_deg"] is not None
    assert stats["slope_mean_deg"] > 30.0


# ═════════════════════════════════════════════════════════════════════════
# Section 4 — Validation coords + guardrails
# ═════════════════════════════════════════════════════════════════════════
def test_validate_requires_guardrails_enforced():
    """Sans guardrails ENFORCED, lève GuardrailsNotEnforced."""
    from engines.v8_institutional.especes import (
        opentopography_omega, pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            opentopography_omega.validate_opentopography_per_site(
                site_coordinates={
                    "x": {"lat": 46.0, "lon": -71.0}},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_rejects_empty_site_coordinates():
    """site_coordinates vide → ValueError."""
    from engines.v8_institutional.especes.opentopography_omega import (
        validate_opentopography_per_site,
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
            validate_opentopography_per_site(
                site_coordinates={}, persist=False)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_rejects_invalid_coords():
    """Coords invalides → ValueError."""
    from engines.v8_institutional.especes.opentopography_omega import (
        validate_opentopography_per_site,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        with pytest.raises(ValueError, match="COORDS_INVALID"):
            validate_opentopography_per_site(
                site_coordinates={
                    "espece_a": {"lat": 999.0, "lon": -71.0}},
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_validate_filters_unknown_demtypes():
    """DEM types inconnus filtrés (anti-générique)."""
    from engines.v8_institutional.especes import (
        opentopography_omega, pipeline_guardrails_omega,
    )
    original_probe = (
        opentopography_omega._probe_dem_at_site)
    original_enforced = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)

        def mock_probe(lat, lon, demtype, half_window_deg=0.01,
                       timeout_s=30):
            return {
                "lat": lat, "lon": lon, "demtype": demtype,
                "valid": True,
                "stats": {"elevation_mean_m": 100.0,
                          "n_valid": 100, "n_nodata": 0},
                "header": {"ncols": 10, "nrows": 10},
                "http_record": {"http_status": 200,
                                "elapsed_ms": 100},
            }
        opentopography_omega._probe_dem_at_site = mock_probe

        result = (
            opentopography_omega
            .validate_opentopography_per_site(
                site_coordinates={
                    "x": {"lat": 46.0, "lon": -71.0}},
                demtypes=["SRTMGL1", "FAKE_DEM_99",
                          "INVALID_DATASET"],
                persist=False,
            ))
        assert "SRTMGL1" in result[
            "demtypes_validated_in_registry"]
        assert "FAKE_DEM_99" in result[
            "demtypes_unknown_skipped"]
        assert "INVALID_DATASET" in result[
            "demtypes_unknown_skipped"]
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enforced)
        opentopography_omega._probe_dem_at_site = original_probe


# ═════════════════════════════════════════════════════════════════════════
# Section 5 — Status read-only
# ═════════════════════════════════════════════════════════════════════════
def test_get_status_returns_valid_dict():
    """get_status retourne dict valide structurel."""
    from engines.v8_institutional.especes.opentopography_omega import (
        get_opentopography_validation_status,
    )
    status = get_opentopography_validation_status()
    assert "manifest_id" in status
    assert "current_status" in status
    assert "v30_lock" in status
    assert status["v30_lock"] == "INVIOLÉ"
    assert status["current_status"] in (
        "NOT_VALIDATED", "VALIDATED_OPERATIONAL")


# ═════════════════════════════════════════════════════════════════════════
# Section 6 — Anti-régression V30_LOCK + sécurité API key
# ═════════════════════════════════════════════════════════════════════════
def test_module_does_not_import_super_engines_logic():
    """Anti-régression : NO_ENGINE_RECOMPUTE_TRIGGERED."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "opentopography_omega.py").read_text(encoding="utf-8")
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
    from engines.v8_institutional.especes import (
        opentopography_omega,
    )  # noqa: F401
    sha_after = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    assert sha_before == sha_after


def test_module_does_not_hardcode_api_key():
    """Sécurité : aucune clé hardcodée dans le module."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "opentopography_omega.py").read_text(encoding="utf-8")
    # La clé fournie 3dbfddc5f97246eb0be5dfe7272ccc2b
    # ne doit JAMAIS apparaître dans le code source
    assert "3dbfddc5f97246eb" not in src
    assert "f97246eb0be5dfe7" not in src
    # Pattern d'accès env obligatoire
    assert 'os.environ' in src
    assert 'OPENTOPOGRAPHY_API_KEY' in src
