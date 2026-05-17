"""
test_phase_xxx_undecies_copernicus_api_validate_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
COPERNICUS_API_P0_VALIDATE

Pytest forensique pour la validation HEAD_ONLY de l'API REST Copernicus
Marine avec détection placeholder STRICTE et masquage token.

Couvre :
  · _is_placeholder_token (détection placeholders templates exhaustive)
  · _mask_token (anti-leakage strict)
  · validate_copernicus_api_endpoint (HEAD strict, placeholder rejected)
  · API endpoint copernicus-api-validate (POST body, token masqué)
  · Anti-générique : un placeholder n'est JAMAIS envoyé en Bearer
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import os
from pathlib import Path

import pytest

try:
    from dotenv import load_dotenv
    _BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"
    if _BACKEND_ENV.exists():
        load_dotenv(_BACKEND_ENV, override=False)
except ImportError:
    pass


def _ensure_guardrails_enforced():
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        restore_and_enforce_guardrails, is_guardrails_enforced,
    )
    if not is_guardrails_enforced():
        restore_and_enforce_guardrails(persist=True)


# ═════════════════════════════════════════════════════════════════════════
# 1. Placeholder detection (anti-générique strict)
# ═════════════════════════════════════════════════════════════════════════
def test_placeholder_detection_classic_templates():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _is_placeholder_token,
    )
    placeholders = [
        "VOTRE_TOKEN_ICI",
        "votre_token_ici",  # case-insensitive
        "  VOTRE_TOKEN_ICI  ",  # trim
        "YOUR_TOKEN_HERE",
        "PLACEHOLDER",
        "TODO",
        "TBD",
        "REPLACE_ME",
        "<your_token>",
        "<API_KEY>",
        "XXX",
        "TEST_TOKEN",
        "EXAMPLE_TOKEN",
        "",
        None,
        "VOTRE_API_KEY_COPERNICUS",  # heuristique VOTRE_*
        "YOUR_AWS_KEY",  # heuristique YOUR_*
    ]
    for p in placeholders:
        assert _is_placeholder_token(p) is True, (
            f"Should detect placeholder: {p!r}")


def test_real_tokens_not_detected_as_placeholder():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _is_placeholder_token,
    )
    real_like = [
        "abc123def456ghi789jkl012mno345p",  # 31 chars random
        "K006abcdef0123456789ABCDEF0123",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",  # JWT-like
    ]
    for t in real_like:
        assert _is_placeholder_token(t) is False, (
            f"Should NOT detect as placeholder: {t!r}")


# ═════════════════════════════════════════════════════════════════════════
# 2. Token masking (anti-leakage)
# ═════════════════════════════════════════════════════════════════════════
def test_mask_token_never_leaks_full_token():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _mask_token,
    )
    secret = "abcdef0123456789SECRETvaluexyz"
    masked = _mask_token(secret)
    assert "MASKED" in masked
    assert "SECRET" not in masked
    assert "0123456789" not in masked
    # Mais doit retourner un hint utile (longueur)
    assert str(len(secret)) in masked


def test_mask_token_handles_empty_and_short():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _mask_token,
    )
    assert "NULL_OR_EMPTY" in _mask_token(None)
    assert "NULL_OR_EMPTY" in _mask_token("")
    short = _mask_token("ab")
    assert "MASKED" in short and "ab" not in short


# ═════════════════════════════════════════════════════════════════════════
# 3. Module exports
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports_copernicus_api_symbols():
    import engines.v8_institutional.especes.noaa_pipeline_omega as mod
    required = [
        "COPERNICUS_API_PLACEHOLDERS",
        "COPERNICUS_API_VALIDATION_PATH",
        "validate_copernicus_api_endpoint",
    ]
    for sym in required:
        assert hasattr(mod, sym)
        assert sym in mod.__all__


# ═════════════════════════════════════════════════════════════════════════
# 4. Validation avec placeholder (DOIT être rejeté SANS auth)
# ═════════════════════════════════════════════════════════════════════════
def test_validate_with_placeholder_token_rejected_anti_generique():
    """ANTI-GÉNÉRIQUE STRICT : VOTRE_TOKEN_ICI rejeté sans Bearer envoyé."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_copernicus_api_endpoint,
    )
    result = validate_copernicus_api_endpoint(
        endpoint="https://data.marine.copernicus.eu/api/v1/products",
        api_key="VOTRE_TOKEN_ICI",
        persist=False,
    )
    assert (result["verdict"]
            == "COPERNICUS_API_REJECTED_PLACEHOLDER_TOKEN_DETECTED")
    assert result["valid"] is False
    # Le token n'a JAMAIS été envoyé
    assert result["probe"]["auth_header_set"] is False
    assert (result["criteria_evaluation"]
            ["auth_header_was_sent"] is False)
    assert (result["criteria_evaluation"]
            ["placeholder_token_detected"] is True)
    # Anti-leakage : token dans le payload est masqué
    full_payload_str = str(result)
    assert "VOTRE_TOKEN_ICI" in full_payload_str  # OK : on le rapporte
    # Mais probe/details ne doit pas le re-fuiter en Authorization
    # (déjà testé via auth_header_set=False)


def test_validate_with_empty_token_rejected_as_placeholder():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_copernicus_api_endpoint,
    )
    result = validate_copernicus_api_endpoint(
        endpoint="https://data.marine.copernicus.eu/api/v1/products",
        api_key=None,
        persist=False,
    )
    assert (result["verdict"]
            == "COPERNICUS_API_REJECTED_PLACEHOLDER_TOKEN_DETECTED")
    assert result["probe"]["auth_header_set"] is False


# ═════════════════════════════════════════════════════════════════════════
# 5. Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_validate_blocks_when_guardrails_disabled(monkeypatch):
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_copernicus_api_endpoint,
    )
    fake_path = Path("/tmp/__nonexistent_grd_state_coper_api__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        validate_copernicus_api_endpoint(
            endpoint=(
                "https://data.marine.copernicus.eu/api/v1/products"),
            api_key=None,
            persist=False)


def test_validate_rejects_invalid_url():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_copernicus_api_endpoint,
    )
    with pytest.raises(ValueError, match="ENDPOINT_INVALID"):
        validate_copernicus_api_endpoint(
            endpoint="not-a-url", api_key=None, persist=False)


# ═════════════════════════════════════════════════════════════════════════
# 6. API endpoint
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture
def api_client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.phase_xix_router_omega import router as v30_router
    app = FastAPI()
    app.include_router(v30_router)
    return TestClient(app)


def test_endpoint_copernicus_api_validate_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/copernicus-api-validate",
        json={
            "endpoint": (
                "https://data.marine.copernicus.eu/api/v1/products"),
            "api_key": "VOTRE_TOKEN_ICI",
        })
    assert resp.status_code == 401


def test_endpoint_copernicus_api_validate_placeholder_rejected(
        api_client):
    """L'endpoint doit reporter le rejet placeholder + persister."""
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/copernicus-api-validate",
        json={
            "endpoint": (
                "https://data.marine.copernicus.eu/api/v1/products"),
            "api_key": "VOTRE_TOKEN_ICI",
            "expect_content_type": "application/json",
            "require_no_redirect": True,
            "require_http_200": True,
            "persist": True,
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["manifest_id"] == "COPERNICUS_API_VALIDATE_EXECUTE_Ω"
    r = data["result"]
    assert (r["verdict"]
            == "COPERNICUS_API_REJECTED_PLACEHOLDER_TOKEN_DETECTED")
    assert r["valid"] is False
    assert r["probe"]["auth_header_set"] is False
    assert r["v30_lock"] == "INVIOLÉ"
