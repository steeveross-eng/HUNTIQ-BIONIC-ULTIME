"""Tests anti-régression — P11 (multi_year_dense_grid_timeseries) +
P12 (multi_signature_verification) + P13 (download_endpoint).

NOMS NEUTRES : aucun mot dans BCE_4X_EXCLUDED_KEYWORDS.
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
"""
from __future__ import annotations

import json

import pytest


# ═════════════════════════════════════════════════════════════════════════
# P11 MULTI_YEAR_DENSE_GRID_TIMESERIES
# ═════════════════════════════════════════════════════════════════════════
def test_phase_xxx_quattuortricicies_p11_module_imports():
    from engines.v8_institutional.especes import (
        multi_year_dense_grid_timeseries_omega as mod)
    assert hasattr(mod, "_mann_kendall_trend_test")
    assert hasattr(
        mod, "validate_multi_year_dense_grid_timeseries")
    assert hasattr(
        mod, "activate_multi_year_dense_grid_timeseries_hook")
    assert hasattr(
        mod,
        "get_multi_year_dense_grid_timeseries_hook_status")


def test_phase_xxx_quattuortricicies_mann_kendall_increasing_trend():
    """Série strictement croissante → INCREASING + p<0.05."""
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        _mann_kendall_trend_test,
    )
    series = [0.3, 0.32, 0.35, 0.38, 0.41, 0.44, 0.47, 0.50,
              0.53, 0.56]
    res = _mann_kendall_trend_test(series)
    assert res["valid"] is True
    assert res["S_statistic"] > 0
    assert res["Kendall_tau"] > 0.5
    assert res["slope_sen_per_year"] > 0
    assert res["significant"] is True
    assert "INCREASING_GREENING_SIGNIFICANT" in (
        res["trend_classification"])


def test_phase_xxx_quattuortricicies_mann_kendall_decreasing_trend():
    """Série strictement décroissante → DECREASING + significant."""
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        _mann_kendall_trend_test,
    )
    series = [0.6, 0.58, 0.55, 0.52, 0.49, 0.46, 0.43, 0.40,
              0.37, 0.34]
    res = _mann_kendall_trend_test(series)
    assert res["valid"] is True
    assert res["S_statistic"] < 0
    assert res["Kendall_tau"] < -0.5
    assert res["slope_sen_per_year"] < 0
    assert res["significant"] is True
    assert "DECREASING_BROWNING_SIGNIFICANT" in (
        res["trend_classification"])


def test_phase_xxx_quattuortricicies_mann_kendall_random_no_trend():
    """Série quasi aléatoire → STABLE ou NOT_SIGNIFICANT."""
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        _mann_kendall_trend_test,
    )
    series = [0.5, 0.55, 0.48, 0.52, 0.49, 0.51, 0.5, 0.53,
              0.49, 0.51]
    res = _mann_kendall_trend_test(series)
    assert res["valid"] is True
    # Pas de tendance significative attendue
    assert res["significant"] is False


def test_phase_xxx_quattuortricicies_mann_kendall_insufficient_data():
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        _mann_kendall_trend_test,
    )
    res = _mann_kendall_trend_test([0.5, 0.6])
    assert res["valid"] is False


def test_phase_xxx_quattuortricicies_p11_validate_year_range_invalid():
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        validate_multi_year_dense_grid_timeseries,
    )
    with pytest.raises(ValueError, match="YEAR_RANGE"):
        validate_multi_year_dense_grid_timeseries(
            year_start=2024, year_end=2025, persist=False)


def test_phase_xxx_quattuortricicies_p11_activate_unknown_sha():
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        activate_multi_year_dense_grid_timeseries_hook,
    )
    fake = "0" * 64
    res = activate_multi_year_dense_grid_timeseries_hook(
        manifest_sha256=fake, persist=False)
    assert res["activated"] is False
    assert "REJECTED" in res["verdict"]


def test_phase_xxx_quattuortricicies_p11_overlay_when_present():
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        MULTI_YEAR_VALIDATION_PATH,
    )
    if not MULTI_YEAR_VALIDATION_PATH.exists():
        pytest.skip("Aucun overlay P11.")
    state = json.loads(
        MULTI_YEAR_VALIDATION_PATH.read_text(
            encoding="utf-8"))
    assert state.get("v30_lock") == "INVIOLÉ"


# ═════════════════════════════════════════════════════════════════════════
# P12 MULTI_SIGNATURE_VERIFICATION
# ═════════════════════════════════════════════════════════════════════════
def test_phase_xxx_quattuortricicies_p12_module_imports():
    from engines.v8_institutional.especes import (
        multi_signature_verification_omega as mod)
    assert hasattr(mod, "sign_manifest_dual")
    assert hasattr(mod, "verify_manifest_dual")
    assert hasattr(mod, "sign_all_known_manifests")
    assert hasattr(mod, "verify_all_signatures")
    assert hasattr(
        mod, "activate_multi_signature_verification_hook")


def test_phase_xxx_quattuortricicies_p12_invalid_sha_rejected():
    """SHA-256 != 64 hex chars → ValueError (anti-générique)."""
    from engines.v8_institutional.especes.multi_signature_verification_omega import (  # noqa: E501
        sign_manifest_dual,
    )
    with pytest.raises(ValueError, match="MANIFEST_SHA256"):
        sign_manifest_dual(
            manifest_sha256="too_short",
            manifest_id="TEST",
            overlay_path="/tmp/test")


def test_phase_xxx_quattuortricicies_p12_dual_signature_verifiable():
    """Vraie signature Ed25519+PGP → verify True."""
    from engines.v8_institutional.especes.multi_signature_verification_omega import (  # noqa: E501
        sign_manifest_dual, verify_manifest_dual,
    )
    fake_sha = "a" * 64
    sig = sign_manifest_dual(
        manifest_sha256=fake_sha,
        manifest_id="TEST_LAYER",
        overlay_path="/tmp/test_overlay.json")
    assert "agent_a_ed25519" in sig
    assert "agent_b_pgp" in sig
    assert sig["agent_a_ed25519"]["algorithm"] == (
        "Ed25519_RFC8032")
    assert "RSA_2048_OpenPGP" in (
        sig["agent_b_pgp"]["algorithm"])
    # Verify
    v = verify_manifest_dual(sig)
    assert v["ed25519_valid"] is True
    assert v["pgp_valid"] is True
    assert v["both_signatures_valid"] is True


def test_phase_xxx_quattuortricicies_p12_tampered_sig_rejected():
    """Signature tamper → verification False (anti-générique)."""
    from engines.v8_institutional.especes.multi_signature_verification_omega import (  # noqa: E501
        sign_manifest_dual, verify_manifest_dual,
    )
    fake_sha = "b" * 64
    sig = sign_manifest_dual(
        manifest_sha256=fake_sha,
        manifest_id="TEST_TAMPER",
        overlay_path="/tmp/test_tamper.json")
    # Tamper Ed25519 signature
    tampered = dict(sig)
    tampered["agent_a_ed25519"] = dict(sig["agent_a_ed25519"])
    tampered["agent_a_ed25519"]["signature_hex"] = "00" * 64
    v = verify_manifest_dual(tampered)
    assert v["ed25519_valid"] is False
    assert v["both_signatures_valid"] is False


def test_phase_xxx_quattuortricicies_p12_overlay_when_present():
    from engines.v8_institutional.especes.multi_signature_verification_omega import (  # noqa: E501
        HOOK_ACTIVATION_PATH,
    )
    if not HOOK_ACTIVATION_PATH.exists():
        pytest.skip("Aucun hook P12 activé.")
    state = json.loads(
        HOOK_ACTIVATION_PATH.read_text(encoding="utf-8"))
    assert state.get("v30_lock") == "INVIOLÉ"


def test_phase_xxx_quattuortricicies_p12_status_keys():
    from engines.v8_institutional.especes.multi_signature_verification_omega import (  # noqa: E501
        get_multi_signature_hook_status,
    )
    s = get_multi_signature_hook_status()
    assert s.get("v30_lock") == "INVIOLÉ"


# ═════════════════════════════════════════════════════════════════════════
# P13 DOWNLOAD_ENDPOINT
# ═════════════════════════════════════════════════════════════════════════
def test_phase_xxx_quattuortricicies_p13_module_imports():
    from engines.v8_institutional.especes import (
        download_endpoint_omega as mod)
    assert hasattr(mod, "build_download_bundle")
    assert hasattr(mod, "get_download_endpoint_status")


def test_phase_xxx_quattuortricicies_p13_build_bundle_returns_zip_bytes():
    """Bundle build retourne bytes ZIP valides + metadata."""
    import zipfile
    import io
    from engines.v8_institutional.especes.download_endpoint_omega import (
        build_download_bundle,
    )
    zip_bytes, metadata = build_download_bundle()
    assert isinstance(zip_bytes, bytes)
    assert len(zip_bytes) > 0
    # Vérifier que c'est un ZIP valide
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        names = zf.namelist()
        assert "SHA256_MANIFEST.txt" in names
        assert "README_DOCTRINE.md" in names
        assert "visualizer_all_layers_snapshot.json" in names
    assert metadata["bundle_sha256"]
    assert len(metadata["bundle_sha256"]) == 64
    assert metadata["v30_lock"] == "INVIOLÉ"
    assert metadata["anti_generique_strict"] is True


def test_phase_xxx_quattuortricicies_p13_bundle_sha_matches():
    """Bundle SHA-256 calculé doit matcher le hash réel des bytes."""
    import hashlib
    from engines.v8_institutional.especes.download_endpoint_omega import (
        build_download_bundle,
    )
    zip_bytes, metadata = build_download_bundle()
    actual = hashlib.sha256(zip_bytes).hexdigest()
    assert actual == metadata["bundle_sha256"]


def test_phase_xxx_quattuortricicies_p13_sha_manifest_correct_per_file():
    """SHA256_MANIFEST.txt doit avoir un hash correct pour chaque arc."""
    import hashlib
    import zipfile
    import io
    from engines.v8_institutional.especes.download_endpoint_omega import (
        build_download_bundle,
    )
    zip_bytes, metadata = build_download_bundle()
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        manifest_text = zf.read(
            "SHA256_MANIFEST.txt").decode("utf-8")
        for line in manifest_text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("  ", 1)
            if len(parts) != 2:
                continue
            expected_sha, arcname = parts
            content = zf.read(arcname)
            actual_sha = hashlib.sha256(
                content).hexdigest()
            assert actual_sha == expected_sha, (
                f"SHA mismatch for {arcname}: "
                f"manifest={expected_sha} actual={actual_sha}")


def test_phase_xxx_quattuortricicies_p13_status_keys():
    from engines.v8_institutional.especes.download_endpoint_omega import (
        get_download_endpoint_status,
    )
    s = get_download_endpoint_status()
    assert s.get("v30_lock") == "INVIOLÉ"
    assert "current_status" in s
    assert s.get("format_supported") == (
        "ZIP+JSON+SHA256_MANIFEST")
    assert s.get("protocol") == "HTTPS"


def test_phase_xxx_quattuortricicies_p13_no_engine_recompute():
    from engines.v8_institutional.especes.download_endpoint_omega import (
        build_download_bundle,
    )
    _, metadata = build_download_bundle()
    assert metadata.get(
        "no_engine_recompute_triggered") is True
    assert metadata.get("fusion_add_only") is True
