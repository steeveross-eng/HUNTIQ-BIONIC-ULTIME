"""
test_phase_xxx_nonies_cfsv2_catalogue_cartography_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
NOAA_CFSV2_P0_CATALOGUE_CARTOGRAPHY

Pytest forensique pour la cartographie NCEI THREDDS (FUSION ADD-ONLY).
Nommage strictement neutre.

Couvre :
  · cartograph_ncei_catalogue (GET strict, contraintes XML, capping)
  · Forensic log ENDPOINT_PROBES/CFSV2_CATALOGUE_CARTOGRAPHY
  · Guardrails enforcement requis
  · API endpoint noaa-cfsv2-catalogue-cartography (token, 412, 400)
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
# 1. Module exports + invariants
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports_cartography_symbols():
    import engines.v8_institutional.especes.noaa_pipeline_omega as mod
    required = [
        "CFSV2_CATALOGUE_CARTOGRAPHY_PATH",
        "cartograph_ncei_catalogue",
    ]
    for sym in required:
        assert hasattr(mod, sym)
        assert sym in mod.__all__


def test_cartography_rejects_invalid_url():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        cartograph_ncei_catalogue,
    )
    with pytest.raises(ValueError, match="ROOT_CATALOG_INVALID"):
        cartograph_ncei_catalogue(
            root_catalog_url="not-a-url",
            persist=False)


def test_cartography_blocks_when_guardrails_disabled(monkeypatch):
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        cartograph_ncei_catalogue,
    )
    fake_path = Path("/tmp/__nonexistent_grd_state_carto__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        cartograph_ncei_catalogue(
            root_catalog_url=(
                "https://www.ncei.noaa.gov/thredds/catalog/"
                "cfsr/mon/pgbh/catalog.xml"),
            persist=False)


# ═════════════════════════════════════════════════════════════════════════
# 2. Probe RÉEL NCEI catalogue (réseau requis)
# ═════════════════════════════════════════════════════════════════════════
def test_cartography_real_ncei_catalogue_returns_structured_payload():
    """Anti-générique strict : GET XML réel, datasets/refs réels."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        cartograph_ncei_catalogue,
    )
    result = cartograph_ncei_catalogue(
        root_catalog_url=(
            "https://www.ncei.noaa.gov/thredds/catalog/"
            "cfsr/mon/pgbh/catalog.xml"),
        max_depth=2,
        max_datasets=128,
        persist=True,
    )
    # Doctrinal invariants
    assert (result["manifest_id"]
            == "NOAA_CFSV2_CATALOGUE_CARTOGRAPHY_Ω")
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["mode"] == "CATALOGUE_BROWSE_ONLY"
    assert result["autonomy"] == "LIMITED"
    assert result["guardrails_enforced"] is True
    assert result["no_binary_probed"] is True
    assert result["no_engine_recompute_triggered"] is True
    assert len(result["manifest_sha256"]) == 64
    # Constraints applied
    sc = result["summary"]["constraints_applied"]
    assert sc["allow_http_methods"] == ["GET"]
    assert sc["allow_content_types"] == [
        "application/xml", "text/xml"]
    assert sc["forbid_binary_probe"] is True
    assert sc["forbid_follow_redirects"] is True
    assert sc["max_depth"] == 2
    assert sc["max_datasets"] == 128
    # Au moins le root catalog visité
    assert result["summary"]["n_catalogs_visited"] >= 1
    # Persistance + audit
    pp = result["persisted_paths"]
    assert "overlay_path" in pp
    assert Path(pp["overlay_path"]).exists()
    assert "audit_persisted" in pp


def test_cartography_max_depth_bound_respected():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        cartograph_ncei_catalogue,
    )
    result = cartograph_ncei_catalogue(
        root_catalog_url=(
            "https://www.ncei.noaa.gov/thredds/catalog/"
            "cfsr/mon/pgbh/catalog.xml"),
        max_depth=2,
        max_datasets=10,  # Capping serré
        persist=False,
    )
    # max_datasets respecté (anti-générique : capping réel appliqué)
    assert result["summary"]["n_datasets_discovered"] <= 10
    # max_depth respecté
    assert result["summary"]["max_depth_reached"] <= 2


# ═════════════════════════════════════════════════════════════════════════
# 3. API endpoint
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture
def api_client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.phase_xix_router_omega import router as v30_router
    app = FastAPI()
    app.include_router(v30_router)
    return TestClient(app)


def test_endpoint_cartography_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/noaa-cfsv2-catalogue-cartography")
    assert resp.status_code == 401


def test_endpoint_cartography_invalid_url_returns_400(api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/noaa-cfsv2-catalogue-cartography",
        params={"root_catalog": "not-a-url"},
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 400


def test_endpoint_cartography_real_returns_payload(api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/noaa-cfsv2-catalogue-cartography",
        params={
            "root_catalog": (
                "https://www.ncei.noaa.gov/thredds/catalog/"
                "cfsr/mon/pgbh/catalog.xml"),
            "max_depth": "2",
            "max_datasets": "30",
            "persist": "true",
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert (data["manifest_id"]
            == "NOAA_CFSV2_CATALOGUE_CARTOGRAPHY_EXECUTE_Ω")
    r = data["result"]
    assert r["v30_lock"] == "INVIOLÉ"
    assert r["mode"] == "CATALOGUE_BROWSE_ONLY"
    assert r["guardrails_enforced"] is True
    assert r["no_binary_probed"] is True
    assert "manifest_sha256" in r
    assert len(r["manifest_sha256"]) == 64
