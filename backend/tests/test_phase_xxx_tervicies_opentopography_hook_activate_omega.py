"""test_phase_xxx_tervicies_opentopography_hook_activate_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour OPENTOPOGRAPHY_HOOK_ACTIVATE_Ω.

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
Aucun appel HTTP réel exécuté ici (probes RÉELS via curl séparément).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("/app/backend")))


def test_hook_activate_function_exposed():
    """Module expose activate_opentopography_hook."""
    from engines.v8_institutional.especes import (
        opentopography_omega,
    )
    assert hasattr(opentopography_omega,
                   "activate_opentopography_hook")
    assert hasattr(opentopography_omega,
                   "get_opentopography_hook_status")
    assert hasattr(opentopography_omega,
                   "OPENTOPOGRAPHY_HOOK_ACTIVATION_PATH")


def test_hook_activation_path_under_pipelines():
    """Persistance hook dans pipelines/opentopography/."""
    from engines.v8_institutional.especes.opentopography_omega import (
        OPENTOPOGRAPHY_HOOK_ACTIVATION_PATH,
    )
    assert "data/pipelines/opentopography" in str(
        OPENTOPOGRAPHY_HOOK_ACTIVATION_PATH)
    assert str(OPENTOPOGRAPHY_HOOK_ACTIVATION_PATH).endswith(
        "_overlay.json")


def test_activate_rejects_fabricated_manifest_sha256():
    """SHA fabriqué (64 zéros) doit être REJETÉ."""
    from engines.v8_institutional.especes.opentopography_omega import (
        activate_opentopography_hook,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        result = activate_opentopography_hook(
            manifest_sha256="0" * 64,
            reason="test_fabricated_manifest_rejection",
            persist=False,
        )
        assert result["activated"] is False
        assert (
            "REJECTED" in result["verdict"])
        assert result["anti_generique_strict"] is True
        assert result["v30_lock"] == "INVIOLÉ"
        assert result["no_engine_recompute_triggered"] is True
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_activate_rejects_random_sha256():
    """SHA random non présent dans history doit être REJETÉ."""
    from engines.v8_institutional.especes.opentopography_omega import (
        activate_opentopography_hook,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        result = activate_opentopography_hook(
            manifest_sha256="a" * 64,
            reason="test_random_sha_rejection",
            persist=False,
        )
        assert result["activated"] is False
        assert "REJECTED" in result["verdict"]
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_find_validated_manifest_returns_none_for_unknown():
    """SHA inconnu → None."""
    from engines.v8_institutional.especes.opentopography_omega import (
        _find_validated_opentopography_manifest,
    )
    result = _find_validated_opentopography_manifest("z" * 64)
    assert result is None


def test_activate_requires_guardrails_enforced():
    """Sans guardrails, hook_activate lève GuardrailsNotEnforced."""
    from engines.v8_institutional.especes import (
        opentopography_omega, pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            opentopography_omega.activate_opentopography_hook(
                manifest_sha256="x" * 64, persist=False)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_get_hook_status_returns_valid_dict():
    """get_hook_status retourne dict structurel valide."""
    from engines.v8_institutional.especes.opentopography_omega import (
        get_opentopography_hook_status,
    )
    status = get_opentopography_hook_status()
    assert "manifest_id" in status
    assert "current_status" in status
    assert "v30_lock" in status
    assert status["v30_lock"] == "INVIOLÉ"
    assert status["current_status"] in (
        "NOT_ACTIVATED", "ACTIVATED_OPERATIONAL")


def test_hook_payload_lists_consumed_modules():
    """Payload activation expose consumed_by_modules (6 attendus)."""
    from engines.v8_institutional.especes.opentopography_omega import (
        activate_opentopography_hook,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        # Reject path expose pas consumed_by_modules → on teste structure
        result = activate_opentopography_hook(
            manifest_sha256="0" * 64, persist=False)
        # Sur reject : pas de consumed_by_modules
        # Sur succès on testerait via mock find_validated
        assert "verdict" in result
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_hook_payload_anti_generique_when_succeeds_via_mock():
    """Test cycle complet via mock _find_validated."""
    from engines.v8_institutional.especes import (
        opentopography_omega, pipeline_guardrails_omega,
    )
    original_find = (
        opentopography_omega
        ._find_validated_opentopography_manifest)
    original_enforced = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)

        def mock_find(sha):
            return {
                "manifest_sha256": sha,
                "executed_at_utc": "2026-05-08T00:00:00+00:00",
                "endpoint": "https://portal.opentopography.org/"
                            "API/globaldem",
                "demtypes_validated_in_registry": ["SRTMGL1"],
                "half_window_deg": 0.01,
                "n_sites_total": 5,
                "n_calls_success": 5,
                "site_results": {
                    "espece_a": {
                        "lat": 46.86, "lon": -71.21,
                        "n_dem_probed": 1, "n_dem_valid": 1,
                        "per_dem": {
                            "SRTMGL1": {
                                "valid": True,
                                "stats": {
                                    "elevation_min_m": 10,
                                    "elevation_max_m": 100,
                                    "elevation_mean_m": 50,
                                    "elevation_std_m": 20,
                                    "slope_mean_deg": 5.0,
                                    "slope_max_deg": 30.0,
                                    "n_valid": 5184,
                                },
                            },
                        },
                    },
                },
                "scientific_references_peer_reviewed": [
                    "Farr et al. (2007).",
                ],
            }
        opentopography_omega._find_validated_opentopography_manifest = mock_find  # noqa: E501

        result = (
            opentopography_omega.activate_opentopography_hook(
                manifest_sha256="abc" * 21 + "f",
                reason="test_mock",
                persist=False,
            ))
        assert result["activated"] is True
        assert (result["verdict"]
                == "OPENTOPOGRAPHY_HOOK_ACTIVATED_OPERATIONAL")
        assert "consumed_by_modules" in result
        assert len(result["consumed_by_modules"]) == 6
        assert (
            "BEDDING_ZONES_SLOPE_BASED_COMPUTE"
            in result["consumed_by_modules"])
        assert (
            "MOVEMENT_CORRIDORS_LEAST_COST_PATH"
            in result["consumed_by_modules"])
        assert "activation_sha256" in result
        assert len(result["activation_sha256"]) == 64
        # Sites summary preserved
        assert len(result["sites_summary"]) == 1
        assert (
            result["sites_summary"][0]["site_name"]
            == "espece_a")
        # Outputs partially unblocked
        unblocked = result[
            "deferred_outputs_partially_unblocked_via_this_hook"]
        assert len(unblocked) == 4
        assert any(
            "bedding_zones" in o for o in unblocked)
        assert any(
            "movement_corridors" in o for o in unblocked)
    finally:
        opentopography_omega._find_validated_opentopography_manifest = (  # noqa: E501
            original_find)
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enforced)


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
