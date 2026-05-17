"""
test_phase_xxx_duodecies_openweathermap_validate_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
OPENWEATHERMAP_P0_VALIDATE

Pytest forensique pour la validation OWM avec double placeholder check.
Nommage strictement neutre.

Couvre :
  · validate_openweathermap_endpoint (GET_JSON, double placeholder check)
  · Détection placeholder credentials_api_key + query_params['appid']
  · Sélection auth strategy (QUERY_PARAM_APPID > BEARER_HEADER > NONE)
  · Court-circuit "no requête HTTP si les deux placeholders"
  · Signature OWM canonique (weather + main + name)
  · API endpoint openweathermap-validate
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
# 1. Module exports
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports_owm_symbols():
    import engines.v8_institutional.especes.noaa_pipeline_omega as mod
    required = [
        "OPENWEATHERMAP_VALIDATION_PATH",
        "validate_openweathermap_endpoint",
    ]
    for sym in required:
        assert hasattr(mod, sym)
        assert sym in mod.__all__


# ═════════════════════════════════════════════════════════════════════════
# 2. Court-circuit double placeholder (anti-générique strict)
# ═════════════════════════════════════════════════════════════════════════
def test_owm_both_placeholders_short_circuit_no_http():
    """Si les deux tokens sont placeholders, AUCUNE requête HTTP émise."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_endpoint,
    )
    result = validate_openweathermap_endpoint(
        endpoint=(
            "https://api.openweathermap.org/data/2.5/weather"),
        credentials_api_key="TON_API_KEY_ICI",
        query_params={
            "q": "Quebec,CA",
            "appid": "VOTRE_APPID_ICI",
        },
        persist=False,
    )
    assert (result["verdict"]
            == "OPENWEATHERMAP_REJECTED_BOTH_PLACEHOLDERS_DETECTED")
    assert result["valid"] is False
    assert result["auth_strategy"] == "NONE_BOTH_PLACEHOLDERS"
    p = result["probe"]
    assert p["http_status"] is None
    assert p["elapsed_ms"] == 0.0
    assert p["credentials_placeholder_detected"] is True
    assert p["query_appid_placeholder_detected"] is True


# ═════════════════════════════════════════════════════════════════════════
# 3. Auth strategy selection (anti-générique)
# ═════════════════════════════════════════════════════════════════════════
def test_owm_query_appid_real_credentials_placeholder_uses_query():
    """Quand appid query réel + credentials placeholder → QUERY auth."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_endpoint,
    )
    result = validate_openweathermap_endpoint(
        endpoint=(
            "https://api.openweathermap.org/data/2.5/weather"),
        credentials_api_key="TON_API_KEY_ICI",  # placeholder
        query_params={
            "q": "Quebec,CA",
            # 32 chars hex = format OWM réel
            "appid": "444e2f791375898ce2db3a82b89f4a08",
        },
        persist=True,
    )
    assert result["auth_strategy"] == "QUERY_PARAM_APPID"
    p = result["probe"]
    assert p["credentials_placeholder_detected"] is True
    assert p["query_appid_placeholder_detected"] is False
    # URL masquée mais pas le token réel exposé en payload
    assert "444e2f79" not in result["probe"]["url_masked"]
    assert "MASKED" in result["probe"]["url_masked"]
    # Verdict cohérent (peut être VALID ou INVALID selon réponse OWM)
    assert result["verdict"] in (
        "OPENWEATHERMAP_VALID_LIVE_DATA_RETURNED",
        "OPENWEATHERMAP_INVALID_HTTP_401_INVALID_API_KEY",
        "OPENWEATHERMAP_INVALID_HTTP_404",
        "OPENWEATHERMAP_INVALID_HTTP_429_RATE_LIMITED",
        "OPENWEATHERMAP_INVALID_HTTP_200_BUT_NO_OWM_SIGNATURE",
        "OPENWEATHERMAP_INVALID_OTHER",
        "OPENWEATHERMAP_INVALID_REDIRECT_DETECTED",
    )


def test_owm_only_credentials_real_uses_bearer():
    """Si seul credentials réel et no appid → BEARER_HEADER."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_endpoint,
    )
    result = validate_openweathermap_endpoint(
        endpoint=(
            "https://api.openweathermap.org/data/2.5/weather"),
        credentials_api_key="abcdef0123456789abcdef0123456789",
        query_params={"q": "Quebec,CA"},
        persist=False,
    )
    assert result["auth_strategy"] == "BEARER_HEADER"


# ═════════════════════════════════════════════════════════════════════════
# 4. Token masking (anti-leakage strict)
# ═════════════════════════════════════════════════════════════════════════
def test_owm_token_masking_anti_leakage():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_endpoint,
    )
    real_token = "444e2f791375898ce2db3a82b89f4a08"
    result = validate_openweathermap_endpoint(
        endpoint=(
            "https://api.openweathermap.org/data/2.5/weather"),
        credentials_api_key=None,
        query_params={"q": "Quebec,CA", "appid": real_token},
        persist=False,
    )
    # Doit être masqué dans probe et URL masquée
    assert "MASKED" in result["probe"]["query_appid_masked"]
    assert real_token not in result["probe"]["url_masked"]


def test_placeholder_french_tutoiement_patterns_detected():
    """Heuristique étendue : TON_*, TA_*, MON_*, MA_*, MES_* détectés."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _is_placeholder_token,
    )
    french_placeholders = [
        "TON_API_KEY_ICI",
        "TON_TOKEN",
        "TA_CLE_API",
        "MON_TOKEN_OWM",
        "MA_API_KEY",
        "MES_CREDENTIALS",
    ]
    for p in french_placeholders:
        assert _is_placeholder_token(p) is True, (
            f"Should detect French placeholder: {p!r}")


# ═════════════════════════════════════════════════════════════════════════
# 5. Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_owm_blocks_when_guardrails_disabled(monkeypatch):
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_endpoint,
    )
    fake_path = Path("/tmp/__nonexistent_grd_owm__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        validate_openweathermap_endpoint(persist=False)


def test_owm_rejects_invalid_url():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_endpoint,
    )
    with pytest.raises(ValueError, match="ENDPOINT_INVALID"):
        validate_openweathermap_endpoint(
            endpoint="not-a-url", persist=False)


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


def test_endpoint_owm_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-validate",
        json={
            "endpoint": (
                "https://api.openweathermap.org/data/2.5/weather"),
            "credentials_api_key": "TON_API_KEY_ICI",
            "query_params": {
                "q": "Quebec,CA",
                "appid": "VOTRE_APPID_ICI",
            },
        })
    assert resp.status_code == 401


def test_endpoint_owm_double_placeholder_returns_payload(api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-validate",
        json={
            "endpoint": (
                "https://api.openweathermap.org/data/2.5/weather"),
            "credentials_api_key": "TON_API_KEY_ICI",
            "query_params": {
                "q": "Quebec,CA",
                "appid": "VOTRE_APPID_ICI",
            },
            "persist": True,
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["manifest_id"] == "OPENWEATHERMAP_VALIDATE_EXECUTE_Ω"
    r = data["result"]
    assert (r["verdict"]
            == "OPENWEATHERMAP_REJECTED_BOTH_PLACEHOLDERS_DETECTED")
    assert r["valid"] is False
    assert r["auth_strategy"] == "NONE_BOTH_PLACEHOLDERS"
    assert r["v30_lock"] == "INVIOLÉ"
