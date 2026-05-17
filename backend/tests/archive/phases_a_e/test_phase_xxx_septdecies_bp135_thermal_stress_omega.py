"""
test_phase_xxx_septdecies_bp135_thermal_stress_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
P1_BP135_THERMAL_STRESS_INDEX_ACTIVATE

Pytest forensique pour le module TSI BP135.
Nommage strictement neutre.

Couvre :
  · BP135_THERMAL_LIMITS_V1 (5 espèces avec références scientifiques)
  · _compute_species_tsi (TCZ-based, modulateurs)
  · compute_bp135_thermal_stress_index (orchestration + persistance)
  · API endpoints bp135-thermal-stress-index-activate/-status
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
# 1. Manifest seuils thermiques (5 espèces, sources scientifiques)
# ═════════════════════════════════════════════════════════════════════════
def test_thermal_limits_v1_has_5_species():
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        BP135_THERMAL_LIMITS_V1,
    )
    assert set(BP135_THERMAL_LIMITS_V1.keys()) == {
        "cerf", "orignal", "ours", "dindon", "wapiti"}
    for sp, limits in BP135_THERMAL_LIMITS_V1.items():
        assert "scientific_name" in limits
        assert "lct_winter_celsius" in limits
        assert "uct_celsius" in limits
        assert isinstance(
            limits["scientific_references"], list)
        assert len(limits["scientific_references"]) >= 1


def test_thermal_limits_orignal_lct_correctly_lower_than_cerf():
    """Orignal a LCT plus basse (-30°C) que cerf (-10°C) : moose-cold-tolerant."""
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        BP135_THERMAL_LIMITS_V1,
    )
    assert (BP135_THERMAL_LIMITS_V1["orignal"]["lct_winter_celsius"]
            < BP135_THERMAL_LIMITS_V1["cerf"]["lct_winter_celsius"])
    # Orignal UCT plus basse (14°C) — heat stress prone
    assert (BP135_THERMAL_LIMITS_V1["orignal"]["uct_celsius"]
            < BP135_THERMAL_LIMITS_V1["cerf"]["uct_celsius"])


# ═════════════════════════════════════════════════════════════════════════
# 2. Calcul TSI déterministe
# ═════════════════════════════════════════════════════════════════════════
def test_compute_tsi_within_tcz_returns_zero():
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        _compute_species_tsi, BP135_THERMAL_LIMITS_V1,
    )
    # Cerf à 15°C, dans TCZ → 0
    res = _compute_species_tsi(
        "cerf", BP135_THERMAL_LIMITS_V1["cerf"],
        {"temperature": 15.0, "humidity": 60,
         "wind_speed": 3.0})
    assert res["tsi_score"] == 0.0
    assert res["risk_class"] == "LOW"
    assert res["thermal_zone"] == "WITHIN_TCZ_COMFORT"


def test_compute_tsi_above_uct_returns_heat_stress():
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        _compute_species_tsi, BP135_THERMAL_LIMITS_V1,
    )
    # Orignal à 25°C : UCT=14°C, donc 25-14=11°C × 5 = 55 TSI
    res = _compute_species_tsi(
        "orignal", BP135_THERMAL_LIMITS_V1["orignal"],
        {"temperature": 25.0, "humidity": 60,
         "wind_speed": 2.0})
    assert res["thermal_zone"] == "ABOVE_UCT_HEAT_STRESS"
    assert 50.0 <= res["tsi_score"] <= 60.0
    assert res["risk_class"] == "HIGH"


def test_compute_tsi_below_lct_returns_cold_stress():
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        _compute_species_tsi, BP135_THERMAL_LIMITS_V1,
        _is_active_winter_season,
    )
    cerf_limits = BP135_THERMAL_LIMITS_V1["cerf"]
    lct = (cerf_limits["lct_winter_celsius"]
           if _is_active_winter_season()
           else cerf_limits["lct_summer_celsius"])
    # Cerf à lct - 6°C : 6×5=30 TSI base
    res = _compute_species_tsi(
        "cerf", cerf_limits,
        {"temperature": lct - 6, "humidity": 50,
         "wind_speed": 2.0})
    assert res["thermal_zone"] == "BELOW_LCT_COLD_STRESS"
    assert 25.0 <= res["tsi_score"] <= 35.0
    assert res["risk_class"] in ("LOW", "MODERATE")


def test_compute_tsi_high_humidity_adds_modulator():
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        _compute_species_tsi, BP135_THERMAL_LIMITS_V1,
    )
    res = _compute_species_tsi(
        "wapiti", BP135_THERMAL_LIMITS_V1["wapiti"],
        {"temperature": 25.0, "humidity": 95,  # > 87 thr
         "wind_speed": 2.0})
    assert (res["tsi_components"].get("humidity_modulator")
            == 10.0)


def test_compute_tsi_missing_temperature_returns_unknown():
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        _compute_species_tsi, BP135_THERMAL_LIMITS_V1,
    )
    res = _compute_species_tsi(
        "cerf", BP135_THERMAL_LIMITS_V1["cerf"],
        {"humidity": 70, "wind_speed": 3.0})
    assert res["tsi_score"] is None
    assert res["risk_class"] == "UNKNOWN_NO_TEMPERATURE"
    assert "temperature" in res["missing_variables"]


# ═════════════════════════════════════════════════════════════════════════
# 3. Manifest persisté (idempotent)
# ═════════════════════════════════════════════════════════════════════════
def test_persist_thermal_limits_manifest_creates_file():
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        persist_thermal_limits_manifest_if_missing,
        THERMAL_LIMITS_V1_PATH,
    )
    payload = persist_thermal_limits_manifest_if_missing()
    assert payload["manifest_id"] == "BP135_THERMAL_LIMITS_V1"
    assert payload["n_species"] == 5
    assert len(payload["manifest_sha256"]) == 64
    assert THERMAL_LIMITS_V1_PATH.exists()


# ═════════════════════════════════════════════════════════════════════════
# 4. Anti-générique : refus si aucun hook OWM batch actif
# ═════════════════════════════════════════════════════════════════════════
def test_compute_tsi_rejects_when_no_owm_batch_hook(monkeypatch):
    _ensure_guardrails_enforced()
    from engines.v8_institutional.especes import (
        bp135_thermal_stress_omega as ts_mod,
    )
    monkeypatch.setattr(
        ts_mod, "_load_active_owm_batch_hook",
        lambda: None)
    result = ts_mod.compute_bp135_thermal_stress_index(
        persist=False, enable_drift_audit=False)
    assert result["valid"] is False
    assert result["verdict"] == (
        "TSI_REJECTED_NO_OWM_BATCH_BP135_HOOK_ACTIVE")


# ═════════════════════════════════════════════════════════════════════════
# 5. Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_compute_tsi_blocks_when_guardrails_disabled(monkeypatch):
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega as grd,
    )
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        compute_bp135_thermal_stress_index,
    )
    fake_path = Path("/tmp/__nonexistent_grd_tsi__.json")
    if fake_path.exists():
        fake_path.unlink()
    monkeypatch.setattr(grd, "GUARDRAILS_STATE_PATH", fake_path)
    with pytest.raises(grd.GuardrailsNotEnforcedError):
        compute_bp135_thermal_stress_index(
            persist=False, enable_drift_audit=False)


# ═════════════════════════════════════════════════════════════════════════
# 6. API endpoints
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture
def api_client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.phase_xix_router_omega import router as v30_router
    app = FastAPI()
    app.include_router(v30_router)
    return TestClient(app)


def test_endpoint_tsi_activate_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/bp135-thermal-stress-index-activate",
        json={"reason": "test"})
    assert resp.status_code == 401


def test_endpoint_tsi_status_is_public(api_client):
    resp = api_client.get(
        "/api/v30/super-masters/bp135-thermal-stress-index-status")
    assert resp.status_code == 200
    data = resp.json()
    assert (data["manifest_id"]
            == "BP135_THERMAL_STRESS_INDEX_STATUS_GET_Ω")


def test_endpoint_thermal_limits_manifest_is_public(api_client):
    resp = api_client.get(
        "/api/v30/super-masters/bp135-thermal-limits-manifest")
    assert resp.status_code == 200
    data = resp.json()
    assert data["manifest_id"] == "BP135_THERMAL_LIMITS_V1_GET_Ω"
    assert data["n_species"] == 5
    r = data["result"]
    assert "thermal_limits" in r
    for sp in ("cerf", "orignal", "ours", "dindon", "wapiti"):
        assert sp in r["thermal_limits"]
