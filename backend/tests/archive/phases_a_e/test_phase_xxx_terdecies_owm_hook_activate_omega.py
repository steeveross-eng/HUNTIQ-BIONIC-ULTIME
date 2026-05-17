"""
test_phase_xxx_terdecies_owm_hook_activate_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
P0_OPENWEATHERMAP_HOOK_ACTIVATE

Pytest forensique pour l'activation officielle du hook OWM.
Nommage strictement neutre.

Couvre :
  · _find_validated_owm_manifest (lookup history strict)
  · activate_openweathermap_hook (rejet si manifest non validé,
    activation si valid, FUSION ADD-ONLY history)
  · get_openweathermap_hook_status (read-only)
  · API endpoints openweathermap-hook-activate / hook-status
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
def test_module_exports_owm_hook_symbols():
    import engines.v8_institutional.especes.noaa_pipeline_omega as mod
    required = [
        "OPENWEATHERMAP_HOOK_ACTIVATION_PATH",
        "activate_openweathermap_hook",
        "get_openweathermap_hook_status",
    ]
    for sym in required:
        assert hasattr(mod, sym)
        assert sym in mod.__all__


# ═════════════════════════════════════════════════════════════════════════
# 2. Anti-générique : rejet si manifest non validé
# ═════════════════════════════════════════════════════════════════════════
def test_activate_rejects_fabricated_manifest_sha256():
    """Anti-générique strict : refus d'activer un manifest inconnu."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        activate_openweathermap_hook,
    )
    fake_sha = "0" * 64  # 64 chars hex mais inexistant en history
    result = activate_openweathermap_hook(
        manifest_sha256=fake_sha,
        reason="owm_hook_activated",
        persist=False,
    )
    assert result["activated"] is False
    assert result["verdict"] == (
        "OPENWEATHERMAP_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["anti_generique_strict"] is True


def test_activate_finds_validated_manifest_helper():
    """_find_validated_owm_manifest retourne None pour SHA inconnu."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _find_validated_owm_manifest,
    )
    assert _find_validated_owm_manifest("0" * 64) is None


# ═════════════════════════════════════════════════════════════════════════
# 3. Activation réelle (réseau requis pour valider d'abord)
# ═════════════════════════════════════════════════════════════════════════
def test_activate_with_real_validated_manifest_succeeds():
    """Workflow complet : valider OWM → activer le hook avec son SHA."""
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_endpoint,
        activate_openweathermap_hook,
        OPENWEATHERMAP_HOOK_ACTIVATION_PATH,
    )
    # Étape 1 : validation live (génère un manifest validé)
    val = validate_openweathermap_endpoint(
        endpoint=(
            "https://api.openweathermap.org/data/2.5/weather"),
        credentials_api_key=None,
        query_params={
            "q": "Quebec,CA",
            "appid": "444e2f791375898ce2db3a82b89f4a08",
        },
        persist=True,
    )
    if val["verdict"] != "OPENWEATHERMAP_VALID_LIVE_DATA_RETURNED":
        pytest.skip(
            f"OWM not returning valid data: {val['verdict']}")
    val_sha = val["manifest_sha256"]
    # Étape 2 : activation officielle
    act = activate_openweathermap_hook(
        manifest_sha256=val_sha,
        reason="owm_hook_activated",
        persist=True,
    )
    assert act["activated"] is True
    assert (act["verdict"]
            == "OPENWEATHERMAP_HOOK_ACTIVATED_OPERATIONAL")
    assert act["validated_manifest_sha256"] == val_sha
    assert len(act["activation_sha256"]) == 64
    assert act["v30_lock"] == "INVIOLÉ"
    assert act["no_engine_recompute_triggered"] is True
    # Persistance vérifiée
    assert OPENWEATHERMAP_HOOK_ACTIVATION_PATH.exists()
    pp = act["persisted_paths"]
    assert "audit_persisted" in pp


def test_get_status_after_activation():
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        get_openweathermap_hook_status,
    )
    st = get_openweathermap_hook_status()
    assert st["v30_lock"] == "INVIOLÉ"
    assert st["current_status"] in (
        "ACTIVATED_OPERATIONAL", "NOT_ACTIVATED")


# ═════════════════════════════════════════════════════════════════════════
# 4. Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_activate_blocks_when_guardrails_disabled(monkeypatch):
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        activate_openweathermap_hook,
    )
    fake_path = Path("/tmp/__nonexistent_grd_owm_act__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        activate_openweathermap_hook(
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


def test_endpoint_owm_activate_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-hook-activate",
        json={"manifest_sha256": "x" * 64})
    assert resp.status_code == 401


def test_endpoint_owm_status_is_public(api_client):
    resp = api_client.get(
        "/api/v30/super-masters/openweathermap-hook-status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["manifest_id"] == "OPENWEATHERMAP_HOOK_STATUS_GET_Ω"
    assert data["v30_lock"] == "INVIOLÉ"


def test_endpoint_owm_activate_fake_sha_rejected(api_client):
    """Endpoint avec SHA fabriqué doit retourner 200 mais activated=False."""
    _ensure_guardrails_enforced()
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/openweathermap-hook-activate",
        json={
            "manifest_sha256": "0" * 64,
            "reason": "test_fake",
            "persist": False,
        },
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert (data["manifest_id"]
            == "OPENWEATHERMAP_HOOK_ACTIVATE_EXECUTE_Ω")
    r = data["result"]
    assert r["activated"] is False
    assert r["verdict"] == (
        "OPENWEATHERMAP_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
