"""
test_phase_xxx_septies_cfsv2_p0_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
NOAA_CFSV2_P0_DECISION

Pytest forensique pour la vérification CFSv2 P0 (HEAD_ONLY strict +
pivot CANDIDATE_LIST_ONLY). Nommage strictement neutre.

Couvre :
  · CFSV2_PIVOT_CANDIDATE_LIST (anti-générique, require_commandant_confirm)
  · _is_content_type_acceptable (validation formats binaires)
  · verify_cfsv2_p0_head_only (HEAD strict + guardrails enforce + pivot)
  · list_cfsv2_pivot_candidates (read-only)
  · API endpoints noaa-cfsv2-verification-p0 / noaa-cfsv2-pivot-candidates
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import os
from pathlib import Path

import pytest

# Charger .env (token Commandant + B2 creds)
try:
    from dotenv import load_dotenv
    _BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"
    if _BACKEND_ENV.exists():
        load_dotenv(_BACKEND_ENV, override=False)
except ImportError:
    pass


# ═════════════════════════════════════════════════════════════════════════
# 1. Pivot list invariants (anti-générique strict)
# ═════════════════════════════════════════════════════════════════════════
def test_pivot_candidate_list_doctrinal_invariants():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        CFSV2_PIVOT_CANDIDATE_LIST,
    )
    assert len(CFSV2_PIVOT_CANDIDATE_LIST) >= 2
    labels = {c["label"] for c in CFSV2_PIVOT_CANDIDATE_LIST}
    assert "NCEI_THREDDS_CFSR_MONTHLY" in labels
    assert "COPERNICUS_MARINE_GLOBAL_PHY" in labels
    for c in CFSV2_PIVOT_CANDIDATE_LIST:
        assert "endpoint_root" in c or "access_url" in c
        assert "format_native" in c
        assert "anti_generique_note" in c


def test_list_cfsv2_pivot_candidates_returns_candidate_list_only_mode():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        list_cfsv2_pivot_candidates,
    )
    p = list_cfsv2_pivot_candidates()
    assert p["mode"] == "CANDIDATE_LIST_ONLY"
    assert p["autonomy"] == "LIMITED"
    assert p["require_commandant_confirm"] is True
    assert p["v30_lock"] == "INVIOLÉ"
    assert p["n_candidates"] >= 2


# ═════════════════════════════════════════════════════════════════════════
# 2. Content-type validation (anti-générique)
# ═════════════════════════════════════════════════════════════════════════
def test_content_type_acceptable_for_binary_formats():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _is_content_type_acceptable,
    )
    accept = [
        "application/octet-stream",
        "application/x-grib",
        "application/x-grib2",
        "application/x-netcdf",
        "binary/octet-stream",
    ]
    for ct in accept:
        assert _is_content_type_acceptable(
            ct, "GRIB2_OR_NETCDF") is True


def test_content_type_rejected_for_html_or_none():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _is_content_type_acceptable,
    )
    rej = [
        "text/html",
        "text/html; charset=utf-8",
        "application/xml",
        "application/json",
        None,
        "",
    ]
    for ct in rej:
        assert _is_content_type_acceptable(
            ct, "GRIB2_OR_NETCDF") is False


# ═════════════════════════════════════════════════════════════════════════
# 3. Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_verify_cfsv2_p0_blocks_when_guardrails_disabled(monkeypatch):
    """Si guardrails NOT_ACTIVATED, doit lever GuardrailsNotEnforcedError."""
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        verify_cfsv2_p0_head_only,
    )
    # Forcer le state file inexistant via monkeypatch du module
    fake_path = Path("/tmp/__nonexistent_guardrails_state__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        verify_cfsv2_p0_head_only(persist=False)


# ═════════════════════════════════════════════════════════════════════════
# 4. Probe RÉEL HEAD_ONLY (ensures guardrails activated first)
# ═════════════════════════════════════════════════════════════════════════
def _ensure_guardrails_enforced():
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        restore_and_enforce_guardrails, is_guardrails_enforced,
    )
    if not is_guardrails_enforced():
        restore_and_enforce_guardrails(persist=True)


def test_verify_cfsv2_p0_head_only_returns_real_status():
    """Anti-générique strict : status HTTP RÉEL, pas de fabrication."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        verify_cfsv2_p0_head_only,
    )
    result = verify_cfsv2_p0_head_only(
        bucket="noaa-cfs-pds",
        path=(
            "cfs.20240101/01/6hrly_grib_01/"
            "cfs.tavg.01.2024010100.grb2"),
        expect_format="GRIB2_OR_NETCDF",
        require_no_redirect=True,
        require_http_200=True,
        persist=True,
    )
    assert result["manifest_id"] == "NOAA_CFSV2_VERIFICATION_P0_Ω"
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["guardrails_enforced"] is True
    assert result["no_engine_recompute_triggered"] is True
    # Verdict structurel cohérent
    assert result["verdict"] in (
        "CFSV2_P0_HEAD_PROBE_VALID",
        "CFSV2_P0_HEAD_PROBE_INVALID")
    # Si invalide, pivot list présent
    if not result["valid"]:
        pp = result["pivot_payload"]
        assert pp is not None
        assert pp["mode"] == "CANDIDATE_LIST_ONLY"
        assert pp["require_commandant_confirm"] is True
        assert pp["n_candidates"] >= 2
    # SHA-256 manifest 64 chars hex
    assert len(result["manifest_sha256"]) == 64
    # Persistance forensique + audit
    pp = result["persisted_paths"]
    assert "overlay_path" in pp
    assert Path(pp["overlay_path"]).exists()
    assert "audit_persisted" in pp
    assert Path(pp["audit_persisted"]["audit_path"]).exists()


# ═════════════════════════════════════════════════════════════════════════
# 5. API endpoints
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture
def api_client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.phase_xix_router_omega import router as v30_router
    app = FastAPI()
    app.include_router(v30_router)
    return TestClient(app)


def test_endpoint_cfsv2_verification_p0_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/noaa-cfsv2-verification-p0")
    assert resp.status_code == 401


def test_endpoint_pivot_candidates_is_public(api_client):
    resp = api_client.get(
        "/api/v30/super-masters/noaa-cfsv2-pivot-candidates")
    assert resp.status_code == 200
    data = resp.json()
    assert data["manifest_id"] == "NOAA_CFSV2_PIVOT_LIST_Ω"
    assert data["v30_lock"] == "INVIOLÉ"
    r = data["result"]
    assert r["mode"] == "CANDIDATE_LIST_ONLY"
    assert r["require_commandant_confirm"] is True


def test_endpoint_cfsv2_verification_p0_with_token_returns_payload(
        api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/noaa-cfsv2-verification-p0",
        params={
            "bucket": "noaa-cfs-pds",
            "path": (
                "cfs.20240101/01/6hrly_grib_01/"
                "cfs.tavg.01.2024010100.grb2"),
            "expect_format": "GRIB2_OR_NETCDF",
            "require_no_redirect": "true",
            "require_http_200": "true",
            "persist": "true",
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert (data["manifest_id"]
            == "NOAA_CFSV2_VERIFICATION_P0_EXECUTE_Ω")
    r = data["result"]
    assert r["v30_lock"] == "INVIOLÉ"
    assert r["guardrails_enforced"] is True
    assert "manifest_sha256" in r
    assert len(r["manifest_sha256"]) == 64
    assert r["verdict"] in (
        "CFSV2_P0_HEAD_PROBE_VALID",
        "CFSV2_P0_HEAD_PROBE_INVALID")
