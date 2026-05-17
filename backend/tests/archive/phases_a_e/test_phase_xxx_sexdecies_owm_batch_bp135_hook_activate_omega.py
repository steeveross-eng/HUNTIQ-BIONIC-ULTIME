"""
test_phase_xxx_sexdecies_owm_batch_bp135_hook_activate_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
P1_OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE

Pytest forensique pour l'activation du hook BATCH BP135.
Nommage strictement neutre.

Couvre :
  · _find_validated_owm_batch_manifest (lookup history strict)
  · activate_openweathermap_batch_bp135_hook (rejet SHA fabriqué,
    activation réelle, FUSION ADD-ONLY, modules consumers)
  · get_openweathermap_batch_bp135_hook_status (read-only)
  · API endpoints openweathermap-batch-bp135-hook-activate / -status
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
def test_module_exports_batch_bp135_hook_symbols():
    import engines.v8_institutional.especes.noaa_pipeline_omega as mod
    required = [
        "OPENWEATHERMAP_BATCH_BP135_HOOK_PATH",
        "activate_openweathermap_batch_bp135_hook",
        "get_openweathermap_batch_bp135_hook_status",
    ]
    for sym in required:
        assert hasattr(mod, sym)
        assert sym in mod.__all__


# ═════════════════════════════════════════════════════════════════════════
# 2. Anti-générique : rejet manifest fabriqué
# ═════════════════════════════════════════════════════════════════════════
def test_batch_hook_rejects_fabricated_manifest_sha():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        activate_openweathermap_batch_bp135_hook,
    )
    fake = "0" * 64
    result = activate_openweathermap_batch_bp135_hook(
        manifest_sha256=fake, persist=False)
    assert result["activated"] is False
    assert result["verdict"] == (
        "OWM_BATCH_BP135_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")


def test_find_batch_manifest_returns_none_for_unknown_sha():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _find_validated_owm_batch_manifest,
    )
    assert _find_validated_owm_batch_manifest("0" * 64) is None


# ═════════════════════════════════════════════════════════════════════════
# 3. Activation réelle (réseau requis pour générer batch d'abord)
# ═════════════════════════════════════════════════════════════════════════
def test_batch_hook_activates_with_real_validated_manifest():
    """Workflow complet : batch valider → activer hook."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        batch_probe_owm_bp135,
        activate_openweathermap_batch_bp135_hook,
    )
    bres = batch_probe_owm_bp135(
        credentials_api_key="444e2f791375898ce2db3a82b89f4a08",
        species_coordinates={
            "sp1": {"lat": 46.8139, "lon": -71.2080},
            "sp2": {"lat": 47.2000, "lon": -70.3000},
        },
        units="metric",
        persist=True,
        inter_call_sleep_s=0.1,
    )
    if bres.get("n_valid", 0) < 1:
        pytest.skip(
            f"OWM batch failed: {bres.get('verdict')}")
    sha = bres["manifest_sha256"]
    result = activate_openweathermap_batch_bp135_hook(
        manifest_sha256=sha,
        reason="owm_batch_bp135_activated",
        persist=True,
    )
    assert result["activated"] is True
    assert (result["verdict"]
            == "OWM_BATCH_BP135_HOOK_ACTIVATED_OPERATIONAL")
    assert result["validated_manifest_sha256"] == sha
    assert len(result["activation_sha256"]) == 64
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["no_engine_recompute_triggered"] is True
    assert "PHENOLOGIE_FORECAST_5_DAY" in result["consumed_by_modules"]
    assert isinstance(result["species_summary"], list)


def test_batch_hook_get_status_after_activation():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        get_openweathermap_batch_bp135_hook_status,
    )
    st = get_openweathermap_batch_bp135_hook_status()
    assert st["v30_lock"] == "INVIOLÉ"
    assert st["current_status"] in (
        "ACTIVATED_OPERATIONAL", "NOT_ACTIVATED")


# ═════════════════════════════════════════════════════════════════════════
# 4. Guardrails
# ═════════════════════════════════════════════════════════════════════════
def test_batch_hook_blocks_when_guardrails_disabled(monkeypatch):
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        activate_openweathermap_batch_bp135_hook,
    )
    fake_path = Path("/tmp/__nonexistent_grd_batch_hook__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        activate_openweathermap_batch_bp135_hook(
            manifest_sha256="x" * 64, persist=False)


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


def test_endpoint_batch_hook_activate_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-batch-bp135-hook-activate",
        json={"manifest_sha256": "x" * 64})
    assert resp.status_code == 401


def test_endpoint_batch_hook_status_is_public(api_client):
    resp = api_client.get(
        "/api/v30/super-masters/openweathermap-batch-bp135-hook-status")
    assert resp.status_code == 200
    data = resp.json()
    assert (data["manifest_id"]
            == "OWM_BATCH_BP135_HOOK_STATUS_GET_Ω")
    assert data["v30_lock"] == "INVIOLÉ"


def test_endpoint_batch_hook_activate_fake_sha_rejected(api_client):
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-batch-bp135-hook-activate",
        json={
            "manifest_sha256": "0" * 64,
            "reason": "test_fake",
            "persist": False,
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200
    data = resp.json()
    r = data["result"]
    assert r["activated"] is False
    assert r["verdict"] == (
        "OWM_BATCH_BP135_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
