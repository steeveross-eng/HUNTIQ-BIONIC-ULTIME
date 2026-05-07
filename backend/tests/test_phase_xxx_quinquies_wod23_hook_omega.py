"""
test_phase_xxx_quinquies_wod23_hook_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
ACTIVATION_HOOK_NOAA_WOD23

Pytest forensique pour l'activation du hook NOAA WOD23 sur Backblaze B2.
Ce fichier est nommé strictement neutre (aucun mot-clé exclu par
conftest.py BCE_4X_EXCLUDED_KEYWORDS).

Couvre :
  · probe_wod23_b2_dedicated (signature, env vars dédiées B2_WOD23_*)
  · activate_wod23_hook (manifest SHA-256, persistance overlay+audit)
  · get_wod23_hook_status (read-only, V30_LOCK respecté)
  · _classify_wod23_key (signatures NOAA WOD23)
  · API endpoints noaa-wod23-activate / noaa-wod23-hook-status
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import os
import json
import hashlib
from pathlib import Path

import pytest

# Charger .env au démarrage du module pour que pytest CLI dispose
# des credentials B2_WOD23_* + GIS_RECEPTION_COMMANDANT_TOKEN.
try:
    from dotenv import load_dotenv
    _BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"
    if _BACKEND_ENV.exists():
        load_dotenv(_BACKEND_ENV, override=False)
except ImportError:
    pass


# ═════════════════════════════════════════════════════════════════════════
# 1. Tests unitaires sur classification (anti-générique)
# ═════════════════════════════════════════════════════════════════════════
def test_classify_known_wod23_signatures_returns_correct_code():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _classify_wod23_key,
    )
    cases = {
        "ocldb1778153836.685480_APB.nc.gz": "APB",
        "ocldb1778153836.685480_CTD.nc.gz": "CTD",
        "ocldb1778153836.685480_CTD2.nc.gz": "CTD",
        "ocldb1778153836.685480_DRB.nc.gz": "DRB",
        "ocldb1778153836.685480_GLD.nc.gz": "GLD",
        "ocldb_test_PFL.nc": "PFL",
        "ocldb_test_OSD.nc": "OSD",
        "subdir/ocldb_test_XBT.nc.gz": "XBT",
    }
    for key, expected in cases.items():
        sig = _classify_wod23_key(key)
        assert sig == expected, (
            f"key={key} expected={expected} got={sig}")


def test_classify_unrecognized_key_returns_none_anti_generique():
    """Anti-générique : refuse de classifier un fichier inconnu."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        _classify_wod23_key,
    )
    assert _classify_wod23_key("random_file.nc") is None
    assert _classify_wod23_key("totally_unknown.bin") is None
    assert _classify_wod23_key("") is None


# ═════════════════════════════════════════════════════════════════════════
# 2. Tests config + structure du module (sans réseau)
# ═════════════════════════════════════════════════════════════════════════
def test_wod23_hook_overlay_config_doctrinal_invariants():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        WOD23_HOOK_OVERLAY_CONFIG,
    )
    assert WOD23_HOOK_OVERLAY_CONFIG["v30_lock"] == "INVIOLÉ"
    assert WOD23_HOOK_OVERLAY_CONFIG["fusion_add_only"] is True
    assert WOD23_HOOK_OVERLAY_CONFIG["anti_generique_strict"] is True
    assert "PHYSIOLOGIE" in WOD23_HOOK_OVERLAY_CONFIG[
        "consumed_by_modules"]
    sigs = WOD23_HOOK_OVERLAY_CONFIG["wod23_signatures_recognized"]
    for required in ["APB", "CTD", "DRB", "GLD", "PFL", "XBT"]:
        assert required in sigs, f"Missing WOD23 signature: {required}"


def test_module_exports_all_required_symbols():
    import engines.v8_institutional.especes.noaa_pipeline_omega as mod
    required = [
        "WOD23_HOOK_OVERLAY_CONFIG",
        "WOD23_HOOK_ACTIVATION_PATH",
        "probe_wod23_b2_dedicated",
        "activate_wod23_hook",
        "get_wod23_hook_status",
    ]
    for sym in required:
        assert hasattr(mod, sym), f"Missing export: {sym}"
        assert sym in mod.__all__, f"Missing in __all__: {sym}"


# ═════════════════════════════════════════════════════════════════════════
# 3. Tests probe RÉEL B2 (réseau requis — credentials valides en env)
# ═════════════════════════════════════════════════════════════════════════
def _has_b2_wod23_env() -> bool:
    return all(os.environ.get(k) for k in [
        "B2_WOD23_KEY_ID",
        "B2_WOD23_APPLICATION_KEY",
        "B2_WOD23_ENDPOINT_URL",
        "B2_WOD23_BUCKET",
    ])


@pytest.mark.skipif(
    not _has_b2_wod23_env(),
    reason="B2_WOD23_* env vars not set — skipping live probe")
def test_probe_wod23_b2_dedicated_returns_structured_record():
    """Anti-générique strict : probe RÉEL retourne status réel."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        probe_wod23_b2_dedicated,
    )
    record = probe_wod23_b2_dedicated(max_keys=50, classify=True)
    # Doctrinal invariants
    assert record["manifest_id"] == "WOD23_B2_DEDICATED_PROBE_Ω"
    assert record["v30_lock"] == "INVIOLÉ"
    assert record["anti_generique_strict"] is True
    assert record["bucket"] == os.environ["B2_WOD23_BUCKET"]
    # Probe a réussi
    assert record["bucket_exists"] is True, (
        f"Bucket head failed: {record}")
    assert record["available"] is True, (
        f"No valid objects: {record}")
    assert record["n_objects_valid"] >= 1
    # WOD23 signatures détectées
    assert record["n_objects_recognized_wod23"] >= 1, (
        "No WOD23 signature recognized in real bucket — "
        "anti-generique probe must reflect real classification.")
    assert isinstance(record["classification_counts"], dict)
    assert len(record["classification_counts"]) >= 1


@pytest.mark.skipif(
    not _has_b2_wod23_env(),
    reason="B2_WOD23_* env vars not set — skipping live activation")
def test_activate_wod23_hook_persists_overlay_and_audit():
    """Probe RÉEL → activation → manifest SHA-256 + persistance."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        activate_wod23_hook, WOD23_HOOK_ACTIVATION_PATH,
    )
    result = activate_wod23_hook(persist=True, max_keys=50)
    assert result["manifest_id"] == "WOD23_HOOK_ACTIVATE_Ω"
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["no_engine_recompute_triggered"] is True
    assert result["drift_zero"] is True
    # Verdict
    assert result["activated"] in (True, False)
    assert result["verdict"] in (
        "WOD23_HOOK_ACTIVATED_OPERATIONAL",
        "WOD23_HOOK_FILES_PRESENT_BUT_NO_WOD23_SIGNATURE",
        "WOD23_HOOK_PROBE_FAILED_NOT_ACTIVATED",
    )
    # SHA-256 manifest doit être 64 chars hex
    sha = result["manifest_sha256"]
    assert len(sha) == 64
    assert all(c in "0123456789abcdef" for c in sha)
    # Overlay persisté
    assert WOD23_HOOK_ACTIVATION_PATH.exists()
    overlay_payload = json.loads(
        WOD23_HOOK_ACTIVATION_PATH.read_text(encoding="utf-8"))
    assert overlay_payload["manifest_sha256"] == sha
    # Audit persisté
    audit_meta = result["persisted_paths"]["audit_persisted"]
    assert "audit_sha256" in audit_meta
    assert Path(audit_meta["audit_path"]).exists()


@pytest.mark.skipif(
    not _has_b2_wod23_env(),
    reason="B2_WOD23_* env vars not set — skipping status read")
def test_get_wod23_hook_status_after_activation():
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        get_wod23_hook_status, activate_wod23_hook,
    )
    # S'assurer qu'une activation a eu lieu
    activate_wod23_hook(persist=True, max_keys=20)
    status = get_wod23_hook_status()
    assert status["manifest_id"] == "WOD23_HOOK_STATUS_Ω"
    assert status["v30_lock"] == "INVIOLÉ"
    assert status["status"] in (
        "ACTIVATED", "PROBE_FAILED_NOT_ACTIVATED",
        "NOT_ACTIVATED_YET")
    if status["status"] == "ACTIVATED":
        assert status["manifest"]["activated"] is True
        assert "manifest_sha256" in status["manifest"]


# ═════════════════════════════════════════════════════════════════════════
# 4. Tests anti-générique : credentials manquantes → reason réelle
# ═════════════════════════════════════════════════════════════════════════
def test_probe_with_missing_credentials_returns_real_reason(monkeypatch):
    """Anti-générique : si env manquant, retourner reason réelle."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        probe_wod23_b2_dedicated,
    )
    for k in ["B2_WOD23_KEY_ID", "B2_WOD23_APPLICATION_KEY",
              "B2_WOD23_ENDPOINT_URL", "B2_WOD23_BUCKET"]:
        monkeypatch.delenv(k, raising=False)
    record = probe_wod23_b2_dedicated(max_keys=10)
    assert record["available"] is False
    assert "wod23_credentials_missing_in_env" in record["reason"]
    assert record["v30_lock"] == "INVIOLÉ"
    assert record["anti_generique_strict"] is True


# ═════════════════════════════════════════════════════════════════════════
# 5. Tests endpoints HTTP (FastAPI TestClient)
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture
def api_client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.phase_xix_router_omega import router as v30_router
    app = FastAPI()
    app.include_router(v30_router)
    return TestClient(app)


def test_endpoint_wod23_activate_requires_token(api_client):
    """Sans token → 401."""
    resp = api_client.post(
        "/api/v30/super-masters/noaa-wod23-activate")
    assert resp.status_code == 401


def test_endpoint_wod23_activate_rejects_bad_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/noaa-wod23-activate",
        headers={"X-Commandant-Token": "WRONG_TOKEN"})
    assert resp.status_code == 401


@pytest.mark.skipif(
    not _has_b2_wod23_env(),
    reason="B2_WOD23_* env vars not set — skipping live endpoint")
def test_endpoint_wod23_activate_with_token_returns_manifest(api_client):
    token = os.environ.get(
        "GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    resp = api_client.post(
        "/api/v30/super-masters/noaa-wod23-activate",
        params={"persist": "true", "max_keys": "20"},
        headers={"X-Commandant-Token": token})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert (
        data["manifest_id"] == "WOD23_HOOK_ACTIVATE_EXECUTE_Ω")
    assert data["v30_lock"] == "INVIOLÉ"
    result = data["result"]
    assert result["v30_lock"] == "INVIOLÉ"
    assert result["no_engine_recompute_triggered"] is True
    assert "manifest_sha256" in result
    assert len(result["manifest_sha256"]) == 64


def test_endpoint_wod23_hook_status_is_public(api_client):
    """Read-only public endpoint."""
    resp = api_client.get(
        "/api/v30/super-masters/noaa-wod23-hook-status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["manifest_id"] == "WOD23_HOOK_STATUS_GET_Ω"
    assert data["v30_lock"] == "INVIOLÉ"


def test_endpoint_wod23_probe_only_requires_token(api_client):
    resp = api_client.post(
        "/api/v30/super-masters/noaa-wod23-probe-only")
    assert resp.status_code == 401
