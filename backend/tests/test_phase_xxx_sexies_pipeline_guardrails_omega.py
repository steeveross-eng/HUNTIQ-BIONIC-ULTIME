"""
test_phase_xxx_sexies_pipeline_guardrails_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
PIPELINE_GUARDRAILS_RESTORE

Pytest forensique pour le module pipeline_guardrails_omega + endpoints.
Nommage strictement neutre (aucun keyword exclu par conftest.py).

Couvre :
  · GUARDRAILS_DOCTRINE invariants (drift_zero, lock V30, safety_nets)
  · restore_and_enforce_guardrails (FUSION ADD-ONLY history, SHA-256)
  · get_guardrails_state (read-only)
  · log_forensic_event + list_forensic_events (JSONL append)
  · is_guardrails_enforced + require_guardrails_enforced
  · API endpoints pipeline-guardrails-restore / status / forensic-log
  · API endpoint noaa-cfsv2-candidate-probe (412 sans guardrails)
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import json
from pathlib import Path

import pytest

# Charger .env (token Commandant pour endpoints)
try:
    from dotenv import load_dotenv
    _BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"
    if _BACKEND_ENV.exists():
        load_dotenv(_BACKEND_ENV, override=False)
except ImportError:
    pass


# ═════════════════════════════════════════════════════════════════════════
# 1. Doctrine canonique (immuable runtime)
# ═════════════════════════════════════════════════════════════════════════
def test_guardrails_doctrine_invariants():
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GUARDRAILS_DOCTRINE,
    )
    assert GUARDRAILS_DOCTRINE["doctrine"] == "BCE-4X"
    assert GUARDRAILS_DOCTRINE["profile"] == "STEVE_MAX"
    p = GUARDRAILS_DOCTRINE["protections"]
    assert p["drift_control"] == "DRIFT_ZERO_STRICT"
    assert p["lock_level"] == "V30_LOCK_INVIOLABLE"
    assert p["anti_regression"] == "FULL_PYTEST_ENFORCED"
    assert "NO_AUTO_HOOK_EXPANSION" in p["safety_nets"]
    assert "NO_PARALLEL_HOOKS_WITHOUT_EXPLICIT_DIRECTIVE" in p[
        "safety_nets"]
    assert ("NO_ENDPOINT_SWITCH_WITHOUT_COMMANDANT_CONFIRM"
            in p["safety_nets"])
    assert p["modularity"] == "100_PERCENT_MODULAR"
    assert p["logging"]["audit_level"] == "FORENSIC"
    assert set(p["logging"]["scope"]) == {
        "B2_CREDENTIALS", "ENDPOINT_PROBES",
        "HOOK_ACTIVATIONS", "CONFIG_CHANGES",
    }
    assert p["execution_mode"]["autonomy"] == "LIMITED"
    assert p["execution_mode"][
        "default_posture"] == "STANDBY_STRICT"
    assert p["execution_mode"][
        "require_token"] == "X-COMMANDANT-TOKEN"


def test_module_exports_all_required_symbols():
    import engines.v8_institutional.especes.pipeline_guardrails_omega as mod
    required = [
        "GUARDRAILS_DOCTRINE", "VALID_FORENSIC_SCOPES",
        "restore_and_enforce_guardrails", "get_guardrails_state",
        "log_forensic_event", "list_forensic_events",
        "is_guardrails_enforced", "require_guardrails_enforced",
        "GuardrailsNotEnforcedError",
    ]
    for sym in required:
        assert hasattr(mod, sym)
        assert sym in mod.__all__


# ═════════════════════════════════════════════════════════════════════════
# 2. Restore & enforce (FUSION ADD-ONLY history)
# ═════════════════════════════════════════════════════════════════════════
def test_restore_and_enforce_creates_state_with_sha256():
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        restore_and_enforce_guardrails,
        GUARDRAILS_STATE_PATH,
    )
    result = restore_and_enforce_guardrails(persist=True)
    assert result["activated"] is True
    assert result["status"] == "RESTORE_AND_ENFORCE_ALL_GUARDRAILS"
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["drift_zero"] is True
    sha = result["activation_sha256"]
    assert len(sha) == 64
    assert all(c in "0123456789abcdef" for c in sha)
    assert GUARDRAILS_STATE_PATH.exists()
    state = json.loads(
        GUARDRAILS_STATE_PATH.read_text(encoding="utf-8"))
    assert state["current_status"] == "ENFORCED"
    assert state["n_activations"] >= 1
    assert state["history"][-1]["activation_sha256"] == sha


def test_restore_is_fusion_add_only_history():
    """Re-activation incremente n_activations sans écraser history."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        restore_and_enforce_guardrails,
        GUARDRAILS_STATE_PATH,
    )
    r1 = restore_and_enforce_guardrails(persist=True)
    s1 = json.loads(
        GUARDRAILS_STATE_PATH.read_text(encoding="utf-8"))
    n1 = s1["n_activations"]
    r2 = restore_and_enforce_guardrails(persist=True)
    assert r2["activated"] is True
    s2 = json.loads(
        GUARDRAILS_STATE_PATH.read_text(encoding="utf-8"))
    n2 = s2["n_activations"]
    assert n2 == n1 + 1
    assert r1["activation_sha256"] in [
        h["activation_sha256"] for h in s2["history"]]


def test_get_guardrails_state_reflects_activated():
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        restore_and_enforce_guardrails, get_guardrails_state,
    )
    restore_and_enforce_guardrails(persist=True)
    st = get_guardrails_state()
    assert st["current_status"] == "ENFORCED"
    assert st["v30_lock"] == "INVIOLÉ"
    assert "current_activation_sha256" in st


def test_is_guardrails_enforced_returns_true_after_restore():
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        restore_and_enforce_guardrails, is_guardrails_enforced,
    )
    restore_and_enforce_guardrails(persist=True)
    assert is_guardrails_enforced() is True


def test_require_guardrails_enforced_does_not_raise_when_active():
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        restore_and_enforce_guardrails, require_guardrails_enforced,
    )
    restore_and_enforce_guardrails(persist=True)
    require_guardrails_enforced("test_op")  # ne lève pas


# ═════════════════════════════════════════════════════════════════════════
# 3. Forensic logger (JSONL append-only)
# ═════════════════════════════════════════════════════════════════════════
def test_log_forensic_event_persists_record():
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        log_forensic_event, list_forensic_events,
        GUARDRAILS_FORENSIC_LOG_PATH,
    )
    rec = log_forensic_event(
        scope="ENDPOINT_PROBES",
        event="UNIT_TEST_PROBE",
        details={"bucket": "test-bucket", "http_status": 200},
        persist=True,
    )
    assert rec["scope"] == "ENDPOINT_PROBES"
    assert rec["event"] == "UNIT_TEST_PROBE"
    assert rec["v30_lock"] == "INVIOLÉ"
    assert len(rec["record_sha256"]) == 64
    assert GUARDRAILS_FORENSIC_LOG_PATH.exists()
    listing = list_forensic_events(scope="ENDPOINT_PROBES", limit=50)
    found = [
        e for e in listing["events"]
        if e["event"] == "UNIT_TEST_PROBE"]
    assert len(found) >= 1


def test_log_forensic_event_rejects_invalid_scope():
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        log_forensic_event,
    )
    with pytest.raises(ValueError, match="FORENSIC_SCOPE_INVALID"):
        log_forensic_event(
            scope="INVALID_SCOPE",
            event="X",
            details=None,
            persist=False)


# ═════════════════════════════════════════════════════════════════════════
# 4. API endpoints
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture
def api_client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.phase_xix_router_omega import router as v30_router
    app = FastAPI()
    app.include_router(v30_router)
    return TestClient(app)


def test_endpoint_guardrails_restore_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/pipeline-guardrails-restore")
    assert resp.status_code == 401


def test_endpoint_guardrails_status_is_public(api_client):
    resp = api_client.get(
        "/api/v30/super-masters/pipeline-guardrails-status")
    assert resp.status_code == 200
    data = resp.json()
    assert (data["manifest_id"]
            == "PIPELINE_GUARDRAILS_STATUS_GET_Ω")
    assert data["v30_lock"] == "INVIOLÉ"


def test_endpoint_guardrails_restore_with_token(api_client):
    import os
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/pipeline-guardrails-restore",
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert (data["manifest_id"]
            == "PIPELINE_GUARDRAILS_RESTORE_EXECUTE_Ω")
    r = data["result"]
    assert r["activated"] is True
    assert r["status"] == "RESTORE_AND_ENFORCE_ALL_GUARDRAILS"
    assert len(r["activation_sha256"]) == 64


def test_endpoint_forensic_log_filters_by_scope(api_client):
    """Public RO + filtre scope."""
    resp = api_client.get(
        "/api/v30/super-masters/pipeline-guardrails-forensic-log",
        params={"scope": "CONFIG_CHANGES", "limit": "20"})
    assert resp.status_code == 200
    data = resp.json()
    r = data["result"]
    assert r["scope_filter"] == "CONFIG_CHANGES"
    for e in r["events"]:
        assert e["scope"] == "CONFIG_CHANGES"


def test_endpoint_forensic_log_rejects_invalid_scope(api_client):
    resp = api_client.get(
        "/api/v30/super-masters/pipeline-guardrails-forensic-log",
        params={"scope": "BOGUS_SCOPE"})
    assert resp.status_code == 400


def test_endpoint_cfsv2_candidate_probe_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/noaa-cfsv2-candidate-probe")
    assert resp.status_code == 401
