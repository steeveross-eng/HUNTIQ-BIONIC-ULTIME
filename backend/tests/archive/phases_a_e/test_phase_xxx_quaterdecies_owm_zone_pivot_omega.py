"""
test_phase_xxx_quaterdecies_owm_zone_pivot_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
P0_OPENWEATHERMAP_PIVOT_TERRITOIRE

Pytest forensique pour le pivot enrichi OWM (current + forecast + 7 vars).
Nommage strictement neutre (zone, pas territoire).

Couvre :
  · _extract_path (extraction nested anti-générique)
  · _http_get_json_strict (helper GET JSON sans redirect)
  · validate_openweathermap_zone_pivot (double probe + extraction vars)
  · API endpoint openweathermap-zone-pivot
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
# 1. _extract_path (anti-générique : retourne None si chemin absent)
# ═════════════════════════════════════════════════════════════════════════
def test_extract_path_returns_real_value_when_present():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _extract_path,
    )
    d = {"main": {"temp": 9.29, "humidity": 67}, "name": "Québec"}
    assert _extract_path(d, ["main", "temp"]) == 9.29
    assert _extract_path(d, ["main", "humidity"]) == 67
    assert _extract_path(d, ["name"]) == "Québec"


def test_extract_path_returns_none_when_absent():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _extract_path,
    )
    d = {"main": {"temp": 9.29}}
    assert _extract_path(d, ["wind", "speed"]) is None
    assert _extract_path(d, ["main", "pressure"]) is None
    assert _extract_path(d, ["clouds", "all"]) is None


# ═════════════════════════════════════════════════════════════════════════
# 2. Module exports
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports_zone_pivot_symbols():
    import engines.v8_institutional.especes.noaa_pipeline_omega as mod
    required = [
        "OPENWEATHERMAP_ZONE_PIVOT_PATH",
        "validate_openweathermap_zone_pivot",
    ]
    for sym in required:
        assert hasattr(mod, sym)
        assert sym in mod.__all__


# ═════════════════════════════════════════════════════════════════════════
# 3. Court-circuit double placeholder
# ═════════════════════════════════════════════════════════════════════════
def test_zone_pivot_both_placeholders_short_circuit():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_zone_pivot,
    )
    result = validate_openweathermap_zone_pivot(
        credentials_api_key="VOTRE_TOKEN_ICI",
        query_params={
            "lat": 46.81, "lon": -71.21,
            "appid": "TON_APPID_ICI", "units": "metric",
        },
        persist=False,
    )
    assert (result["verdict"]
            == "OWM_ZONE_PIVOT_REJECTED_BOTH_PLACEHOLDERS_DETECTED")
    assert result["valid"] is False
    assert result["auth_strategy"] == "NONE_BOTH_PLACEHOLDERS"


# ═════════════════════════════════════════════════════════════════════════
# 4. Probe RÉEL double endpoint (réseau requis)
# ═════════════════════════════════════════════════════════════════════════
def test_zone_pivot_real_owm_double_probe_quebec():
    """Anti-générique : double probe RÉEL OWM avec extraction variables."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_zone_pivot,
    )
    result = validate_openweathermap_zone_pivot(
        credentials_api_key=None,
        query_params={
            "lat": 46.8139,
            "lon": -71.2080,
            "appid": "3dbfddc5f97246eb0be5dfe7272ccc2b",
            "units": "metric",
        },
        variables_requested={
            "temperature": True, "humidity": True, "pressure": True,
            "wind_speed": True, "wind_direction": True,
            "cloud_cover": True, "precipitation": True,
        },
        persist=True,
    )
    assert result["manifest_id"] == "OWM_ZONE_PIVOT_Ω"
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["guardrails_enforced"] is True
    assert result["auth_strategy"] == "QUERY_PARAM_APPID"
    assert len(result["manifest_sha256"]) == 64
    # Verdict cohérent
    assert result["verdict"] in (
        "OWM_ZONE_PIVOT_VALID_BOTH_ENDPOINTS_LIVE",
        "OWM_ZONE_PIVOT_VALID_CURRENT_ONLY_FORECAST_FAILED",
        "OWM_ZONE_PIVOT_VALID_FORECAST_ONLY_CURRENT_FAILED",
        "OWM_ZONE_PIVOT_INVALID_HTTP_401",
        "OWM_ZONE_PIVOT_INVALID_HTTP_429_RATE_LIMITED",
        "OWM_ZONE_PIVOT_INVALID_OTHER",
    )
    # Anti-leakage
    real_token = "3dbfddc5f97246eb0be5dfe7272ccc2b"
    assert real_token not in result["probe_current_summary"][
        "url_masked"]
    assert real_token not in result["probe_forecast_summary"][
        "url_masked"]
    assert "MASKED" in result["query_appid_masked"]


# ═════════════════════════════════════════════════════════════════════════
# 5. Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_zone_pivot_blocks_when_guardrails_disabled(monkeypatch):
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_zone_pivot,
    )
    fake_path = Path("/tmp/__nonexistent_grd_zp__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        validate_openweathermap_zone_pivot(persist=False)


def test_zone_pivot_rejects_invalid_urls():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_zone_pivot,
    )
    with pytest.raises(ValueError, match="ENDPOINT_CURRENT_INVALID"):
        validate_openweathermap_zone_pivot(
            endpoint_current="not-a-url",
            persist=False)
    with pytest.raises(ValueError, match="ENDPOINT_FORECAST_INVALID"):
        validate_openweathermap_zone_pivot(
            endpoint_forecast="not-a-url",
            persist=False)


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


def test_endpoint_zone_pivot_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-zone-pivot",
        json={"query_params": {"q": "Quebec,CA"}})
    assert resp.status_code == 401


def test_endpoint_zone_pivot_real_returns_payload(api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-zone-pivot",
        json={
            "query_params": {
                "lat": 46.8139,
                "lon": -71.2080,
                "appid": "3dbfddc5f97246eb0be5dfe7272ccc2b",
                "units": "metric",
            },
            "variables_requested": {
                "temperature": True, "humidity": True,
                "pressure": True, "wind_speed": True,
                "wind_direction": True, "cloud_cover": True,
                "precipitation": True,
            },
            "persist": True,
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["manifest_id"] == "OWM_ZONE_PIVOT_EXECUTE_Ω"
    r = data["result"]
    assert r["v30_lock"] == "INVIOLÉ"
    assert r["auth_strategy"] == "QUERY_PARAM_APPID"
    assert len(r["manifest_sha256"]) == 64
