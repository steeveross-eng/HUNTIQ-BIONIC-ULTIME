"""
test_phase_xxx_octies_cfsv2_pivot_verify_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
NOAA_CFSV2_P0_PIVOT_VERIFY

Pytest forensique pour la vérification pivot CFSv2 (NCEI THREDDS).
Nommage strictement neutre.

Couvre :
  · _is_content_type_acceptable_opendap (validation OPeNDAP-aware)
  · verify_cfsv2_pivot_head_only (HEAD + DDS, guardrails enforce)
  · API endpoint noaa-cfsv2-pivot-verify
  · Anti-générique : URL invalide → ValueError, network error → reason
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
# 1. Validation content-type OPeNDAP-aware
# ═════════════════════════════════════════════════════════════════════════
def test_opendap_content_types_accepted():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _is_content_type_acceptable_opendap,
    )
    accept = [
        "text/plain",
        "application/octet-stream",
        "application/x-netcdf",
        "application/x-dods-dds",
        "application/x-dods-das",
        "application/x-dods-dods",
        "binary/octet-stream",
    ]
    for ct in accept:
        assert _is_content_type_acceptable_opendap(ct) is True


def test_opendap_content_types_rejected():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _is_content_type_acceptable_opendap,
    )
    reject = [
        "text/html",
        "text/html; charset=utf-8",
        "image/png",
        None,
        "",
    ]
    for ct in reject:
        assert _is_content_type_acceptable_opendap(ct) is False


# ═════════════════════════════════════════════════════════════════════════
# 2. Module exports
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports_pivot_verify_symbols():
    import engines.v8_institutional.especes.noaa_pipeline_omega as mod
    required = [
        "CFSV2_PIVOT_VERIFICATION_PATH",
        "verify_cfsv2_pivot_head_only",
    ]
    for sym in required:
        assert hasattr(mod, sym)
        assert sym in mod.__all__


# ═════════════════════════════════════════════════════════════════════════
# 3. Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_pivot_verify_blocks_when_guardrails_disabled(monkeypatch):
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        verify_cfsv2_pivot_head_only,
    )
    fake_path = Path(
        "/tmp/__nonexistent_guardrails_pivot_verify__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        verify_cfsv2_pivot_head_only(
            endpoint="https://www.ncei.noaa.gov/thredds/dodsC/test.nc",
            persist=False)


def test_pivot_verify_rejects_invalid_url():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        verify_cfsv2_pivot_head_only,
    )
    with pytest.raises(ValueError, match="ENDPOINT_INVALID"):
        verify_cfsv2_pivot_head_only(
            endpoint="not-a-valid-url", persist=False)


# ═════════════════════════════════════════════════════════════════════════
# 4. Probe RÉEL NCEI THREDDS (réseau requis)
# ═════════════════════════════════════════════════════════════════════════
def test_pivot_verify_real_ncei_thredds_endpoint():
    """Anti-générique : probe RÉEL NCEI THREDDS, status réel reporté."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        verify_cfsv2_pivot_head_only,
    )
    result = verify_cfsv2_pivot_head_only(
        endpoint=(
            "https://www.ncei.noaa.gov/thredds/dodsC/cfsr/mon/"
            "pgbh/pgbh.202401.nc"),
        provider="NCEI_THREDDS_CFSR_MONTHLY",
        expect_format="GRIB2_OR_NETCDF",
        expect_opendap=True,
        require_no_redirect=True,
        require_http_200=True,
        persist=True,
    )
    assert result["manifest_id"] == "NOAA_CFSV2_PIVOT_VERIFY_Ω"
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["guardrails_enforced"] is True
    assert result["autonomy"] == "LIMITED"
    assert result["no_engine_recompute_triggered"] is True
    assert len(result["manifest_sha256"]) == 64
    # DDS probe exécuté car expect_opendap=True
    assert result["probe_dds"] is not None
    # Verdict cohérent (un de la liste)
    assert result["verdict"] in (
        "CFSV2_PIVOT_VALID_OPENDAP_DDS_CONFIRMED",
        "CFSV2_PIVOT_VALID_HEAD_OK_DDS_FALLBACK",
        "CFSV2_PIVOT_INVALID_REDIRECT_DETECTED",
        "CFSV2_PIVOT_INVALID_HTTP_404",
        "CFSV2_PIVOT_INVALID_NETWORK_ERROR",
        "CFSV2_PIVOT_INVALID_OTHER",
    )
    # Persistance
    pp = result["persisted_paths"]
    assert "overlay_path" in pp
    assert Path(pp["overlay_path"]).exists()
    assert "audit_persisted" in pp


# ═════════════════════════════════════════════════════════════════════════
# 5. API endpoint
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture
def api_client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.phase_xix_router_omega import router as v30_router
    app = FastAPI()
    app.include_router(v30_router)
    return TestClient(app)


def test_endpoint_pivot_verify_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/noaa-cfsv2-pivot-verify",
        params={"endpoint": "https://example.org/test.nc"})
    assert resp.status_code == 401


def test_endpoint_pivot_verify_invalid_url_returns_400(api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/noaa-cfsv2-pivot-verify",
        params={"endpoint": "not-a-url"},
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 400


def test_endpoint_pivot_verify_real_ncei_returns_payload(api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/noaa-cfsv2-pivot-verify",
        params={
            "endpoint": (
                "https://www.ncei.noaa.gov/thredds/dodsC/"
                "cfsr/mon/pgbh/pgbh.202401.nc"),
            "provider": "NCEI_THREDDS_CFSR_MONTHLY",
            "expect_format": "GRIB2_OR_NETCDF",
            "expect_opendap": "true",
            "require_no_redirect": "true",
            "require_http_200": "true",
            "persist": "true",
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert (data["manifest_id"]
            == "NOAA_CFSV2_PIVOT_VERIFY_EXECUTE_Ω")
    r = data["result"]
    assert r["v30_lock"] == "INVIOLÉ"
    assert r["guardrails_enforced"] is True
    assert "manifest_sha256" in r
    assert len(r["manifest_sha256"]) == 64
