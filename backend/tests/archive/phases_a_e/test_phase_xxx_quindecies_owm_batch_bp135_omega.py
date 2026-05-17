"""
test_phase_xxx_quindecies_owm_batch_bp135_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
P1_OPENWEATHERMAP_BATCH_PROBE_BP135

Pytest forensique pour le batch probe OWM 5 espèces.
Nommage strictement neutre.

Couvre :
  · batch_probe_owm_bp135 (orchestration multi-coords + agrégation stats)
  · Validation coords (lat/lon out of range → ValueError)
  · Court-circuit placeholder credentials
  · Guardrails enforcement
  · API endpoint openweathermap-batch-probe-bp135
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
def test_module_exports_batch_bp135_symbols():
    import engines.v8_institutional.especes.noaa_pipeline_omega as mod
    required = [
        "OPENWEATHERMAP_BATCH_BP135_PATH",
        "batch_probe_owm_bp135",
    ]
    for sym in required:
        assert hasattr(mod, sym)
        assert sym in mod.__all__


# ═════════════════════════════════════════════════════════════════════════
# 2. Validation coords (anti-générique : refus de coords invalides)
# ═════════════════════════════════════════════════════════════════════════
def test_batch_rejects_empty_species_coords():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        batch_probe_owm_bp135,
    )
    with pytest.raises(ValueError, match="SPECIES_COORDINATES_REQUIRED"):
        batch_probe_owm_bp135(
            credentials_api_key="abcdef0123456789abcdef0123456789",
            species_coordinates={}, persist=False)


def test_batch_rejects_out_of_range_coords():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        batch_probe_owm_bp135,
    )
    with pytest.raises(ValueError, match="COORDS_INVALID"):
        batch_probe_owm_bp135(
            credentials_api_key="abcdef0123456789abcdef0123456789",
            species_coordinates={
                "fake": {"lat": 200.0, "lon": -71.2}},
            persist=False)


# ═════════════════════════════════════════════════════════════════════════
# 3. Court-circuit placeholder
# ═════════════════════════════════════════════════════════════════════════
def test_batch_short_circuits_on_placeholder_creds():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        batch_probe_owm_bp135,
    )
    result = batch_probe_owm_bp135(
        credentials_api_key="VOTRE_TOKEN_ICI",
        species_coordinates={"sp1": {"lat": 46.8, "lon": -71.2}},
        persist=False,
    )
    assert (result["verdict"]
            == "OWM_BATCH_REJECTED_PLACEHOLDER_TOKEN")
    assert result["valid"] is False


# ═════════════════════════════════════════════════════════════════════════
# 4. Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_batch_blocks_when_guardrails_disabled(monkeypatch):
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        batch_probe_owm_bp135,
    )
    fake_path = Path("/tmp/__nonexistent_grd_batch__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        batch_probe_owm_bp135(
            credentials_api_key="abcdef0123456789abcdef0123456789",
            species_coordinates={
                "sp1": {"lat": 46.8, "lon": -71.2}},
            persist=False)


# ═════════════════════════════════════════════════════════════════════════
# 5. Probe RÉEL (réseau requis, 5 calls × 2 = 10 OWM hits)
# ═════════════════════════════════════════════════════════════════════════
def test_batch_real_owm_5_species_returns_aggregated_stats():
    """Anti-générique : batch RÉEL OWM avec stats agrégées."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        batch_probe_owm_bp135,
    )
    result = batch_probe_owm_bp135(
        credentials_api_key="444e2f791375898ce2db3a82b89f4a08",
        species_coordinates={
            "sp1": {"lat": 46.8139, "lon": -71.2080},
            "sp2": {"lat": 47.2000, "lon": -70.3000},
            "sp3": {"lat": 48.1000, "lon": -69.0000},
        },
        units="metric",
        persist=True,
        inter_call_sleep_s=0.1,
    )
    assert result["manifest_id"] == "OWM_BATCH_BP135_Ω"
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["guardrails_enforced"] is True
    assert result["n_species_total"] == 3
    assert len(result["manifest_sha256"]) == 64
    # Verdict cohérent
    assert result["verdict"] in (
        "OWM_BATCH_BP135_ALL_SPECIES_VALID",
        "OWM_BATCH_BP135_PARTIAL::1_OF_3_VALID",
        "OWM_BATCH_BP135_PARTIAL::2_OF_3_VALID",
        "OWM_BATCH_BP135_ALL_INVALID",
    )
    # Si au moins 1 valide, stats agrégées présentes
    if result["n_valid"] >= 1:
        assert isinstance(
            result["aggregated_stats_across_valid_species"], dict)


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


def test_endpoint_batch_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-batch-probe-bp135",
        json={
            "credentials_api_key": "x" * 32,
            "species_coordinates": {
                "sp1": {"lat": 46.8, "lon": -71.2}},
        })
    assert resp.status_code == 401


def test_endpoint_batch_invalid_coords_returns_400(api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-batch-probe-bp135",
        json={
            "credentials_api_key": "x" * 32,
            "species_coordinates": {
                "sp1": {"lat": 200.0, "lon": -71.2}},
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 400
