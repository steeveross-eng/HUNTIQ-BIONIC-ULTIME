"""
test_phase_xxx_decies_copernicus_catalogue_cartography_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
COPERNICUS_P0_CATALOGUE_CARTOGRAPHY

Pytest forensique pour la cartographie Copernicus Marine THREDDS.
Nommage strictement neutre.

Couvre :
  · cartograph_ncei_catalogue avec provider=COPERNICUS_MARINE
  · forensic_event=COPERNICUS_CATALOGUE_CARTOGRAPHY (configurable)
  · base URLs Copernicus (my.cmems-du.eu/thredds/dodsC/...)
  · API endpoint copernicus-catalogue-cartography (token, 412, 400)
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
# 1. Function-level Copernicus probe (réseau requis)
# ═════════════════════════════════════════════════════════════════════════
def test_copernicus_cartography_real_endpoint_returns_payload():
    """Anti-générique : probe RÉEL Copernicus, status réel reporté."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        cartograph_ncei_catalogue,
    )
    result = cartograph_ncei_catalogue(
        root_catalog_url=(
            "https://my.cmems-du.eu/thredds/catalog/catalog.xml"),
        max_depth=1,
        max_datasets=128,
        persist=True,
        provider="COPERNICUS_MARINE",
        forensic_event="COPERNICUS_CATALOGUE_CARTOGRAPHY",
        ordre="COPERNICUS_P0_CATALOGUE_CARTOGRAPHY",
        base_dodsc_url="https://my.cmems-du.eu/thredds/dodsC/",
        base_fileserver_url=(
            "https://my.cmems-du.eu/thredds/fileServer/"),
    )
    assert (result["manifest_id"]
            == "NOAA_CFSV2_CATALOGUE_CARTOGRAPHY_Ω")
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["mode"] == "CATALOGUE_BROWSE_ONLY"
    assert result["autonomy"] == "LIMITED"
    assert result["guardrails_enforced"] is True
    assert result["no_binary_probed"] is True
    assert result["provider"] == "COPERNICUS_MARINE"
    assert (result["forensic_event"]
            == "COPERNICUS_CATALOGUE_CARTOGRAPHY")
    assert (result["ordre"]
            == "COPERNICUS_P0_CATALOGUE_CARTOGRAPHY")
    assert len(result["manifest_sha256"]) == 64
    sc = result["summary"]["constraints_applied"]
    assert sc["allow_http_methods"] == ["GET"]
    assert sc["max_depth"] == 1
    assert sc["max_datasets"] == 128
    # Au moins le root visité
    assert result["summary"]["n_catalogs_visited"] >= 1


# ═════════════════════════════════════════════════════════════════════════
# 2. Forensic log event Copernicus persisté
# ═════════════════════════════════════════════════════════════════════════
def test_copernicus_forensic_event_persisted():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        cartograph_ncei_catalogue,
    )
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        list_forensic_events,
    )
    cartograph_ncei_catalogue(
        root_catalog_url=(
            "https://my.cmems-du.eu/thredds/catalog/catalog.xml"),
        max_depth=1,
        max_datasets=10,
        persist=False,  # Pas d'overlay mais forensic log persisté
        provider="COPERNICUS_MARINE",
        forensic_event="COPERNICUS_CATALOGUE_CARTOGRAPHY",
        ordre="COPERNICUS_P0_CATALOGUE_CARTOGRAPHY",
        base_dodsc_url="https://my.cmems-du.eu/thredds/dodsC/",
    )
    listing = list_forensic_events(scope="ENDPOINT_PROBES", limit=200)
    coper_events = [
        e for e in listing["events"]
        if e["event"] == "COPERNICUS_CATALOGUE_CARTOGRAPHY"]
    assert len(coper_events) >= 1
    # Provider tracé
    last_ev = coper_events[-1]
    assert last_ev["details"]["provider"] == "COPERNICUS_MARINE"


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


def test_endpoint_copernicus_cartography_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/copernicus-catalogue-cartography")
    assert resp.status_code == 401


def test_endpoint_copernicus_cartography_invalid_url_returns_400(
        api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/copernicus-catalogue-cartography",
        params={"root_catalog": "not-a-url"},
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 400


def test_endpoint_copernicus_cartography_real_returns_payload(
        api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/copernicus-catalogue-cartography",
        params={
            "root_catalog": (
                "https://my.cmems-du.eu/thredds/catalog/catalog.xml"),
            "max_depth": "1",
            "max_datasets": "30",
            "persist": "true",
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert (data["manifest_id"]
            == "COPERNICUS_CATALOGUE_CARTOGRAPHY_EXECUTE_Ω")
    r = data["result"]
    assert r["v30_lock"] == "INVIOLÉ"
    assert r["mode"] == "CATALOGUE_BROWSE_ONLY"
    assert r["provider"] == "COPERNICUS_MARINE"
    assert r["no_binary_probed"] is True
    assert "manifest_sha256" in r
    assert len(r["manifest_sha256"]) == 64
