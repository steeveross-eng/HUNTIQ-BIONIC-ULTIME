"""
test_phase_xxvii_ext3_probe_network_omega.py — Phase XXVII-EXT3
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°52-EXT VOIE A

Tests de POST /diagnostic/pee-maj/probe-network :
  · auth requise
  · 200 OK avec proxy_truncated=False quand observed == expected
  · 200 OK avec proxy_truncated=True quand observed ≠ expected (mensonge)
  · 413 si X-Expected-Size > 1 Mo
  · 400 si X-Expected-Size < 16 octets
  · audit-event PEE_MAJ_PROBE_NETWORK_Ω consigné
  · /status expose client_recommended_parameters

Pattern isolé (FastAPI dédiée + tmp_path).
═════════════════════════════════════════════════════════════════════════════
"""
import io
import os
import sys
import importlib
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, "/app/backend")

TEST_TOKEN = "TEST_TOKEN_PROBE_NETWORK_OMEGA"
HDR = {"X-Commandant-Token": TEST_TOKEN}
P = "/api/v30/admin-premium/gis"


@pytest.fixture
def probe_client(tmp_path, monkeypatch):
    monkeypatch.setenv("GIS_RECEPTION_COMMANDANT_TOKEN", TEST_TOKEN)
    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    iso_root = tmp_path / "iso"
    iso_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mod, "RECEPTION_ROOT", iso_root)
    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = iso_root / "audit_log.jsonl"
    app = FastAPI()
    app.include_router(mod.router)
    return TestClient(app), mod


def test_probe_requires_token(probe_client):
    client, _ = probe_client
    payload = b"\x00" * 100
    r = client.post(
        f"{P}/diagnostic/pee-maj/probe-network",
        headers={"X-Expected-Size": "100"},
        files={"file": ("probe.bin", payload, "application/octet-stream")},
    )
    assert r.status_code == 401


def test_probe_ok_proxy_not_truncated(probe_client):
    client, _ = probe_client
    payload = b"\x42" * 1024  # 1 Ko
    r = client.post(
        f"{P}/diagnostic/pee-maj/probe-network",
        headers={**HDR, "X-Expected-Size": "1024",
                  "X-Probe-Id": "probe.test1k"},
        files={"file": ("probe.bin", payload, "application/octet-stream")},
    )
    assert r.status_code == 200, r.text[:300]
    d = r.json()
    assert d["manifest_id"] == "PEE_MAJ_PROBE_NETWORK_Ω"
    assert d["proxy_truncated"] is False
    assert d["observed_size"] == 1024
    assert d["expected_size"] == 1024
    assert d["mismatch_bytes"] == 0
    assert d["diagnostic_phase"] == "PROXY_OK"
    assert d["sha256_received"]
    assert d["ram_cleanup_executed"] is True
    assert d["no_disk_persistence"] is True
    assert d["v30_lock"] == "INVIOLÉ"


def test_probe_proxy_truncated_lying_expected(probe_client):
    client, _ = probe_client
    payload = b"\x00" * 512  # 512 octets reçus
    r = client.post(
        f"{P}/diagnostic/pee-maj/probe-network",
        headers={**HDR, "X-Expected-Size": "1024"},  # mensonge : 1 Ko prétendu
        files={"file": ("probe.bin", payload, "application/octet-stream")},
    )
    assert r.status_code == 200
    d = r.json()
    assert d["proxy_truncated"] is True
    assert d["observed_size"] == 512
    assert d["expected_size"] == 1024
    assert d["mismatch_bytes"] == -512
    assert d["diagnostic_phase"] == "PROXY_TRUNCATED_OR_CLIENT_LIED"


def test_probe_413_too_large(probe_client):
    """X-Expected-Size > 1 Mo → 413 (sécurité)."""
    client, _ = probe_client
    r = client.post(
        f"{P}/diagnostic/pee-maj/probe-network",
        headers={**HDR, "X-Expected-Size": str(2 * 1024 * 1024)},
        files={"file": ("probe.bin", b"x" * 100, "application/octet-stream")},
    )
    assert r.status_code == 413
    assert "PROBE_TOO_LARGE" in r.json()["detail"]


def test_probe_400_too_small(probe_client):
    client, _ = probe_client
    r = client.post(
        f"{P}/diagnostic/pee-maj/probe-network",
        headers={**HDR, "X-Expected-Size": "8"},
        files={"file": ("probe.bin", b"x" * 8, "application/octet-stream")},
    )
    assert r.status_code == 400


def test_probe_audit_event_consigned(probe_client):
    client, _ = probe_client
    payload = b"\x00" * 256
    client.post(
        f"{P}/diagnostic/pee-maj/probe-network",
        headers={**HDR, "X-Expected-Size": "256"},
        files={"file": ("probe.bin", payload, "application/octet-stream")},
    )
    r = client.get(f"{P}/audit-log", headers=HDR)
    events = r.json()["stats"]["events_by_type"]
    assert events.get("PEE_MAJ_PROBE_NETWORK_Ω", 0) >= 1


def test_status_exposes_client_recommended_parameters(probe_client):
    client, _ = probe_client
    r = client.get(f"{P}/diagnostic/pee-maj/status", headers=HDR)
    assert r.status_code == 200
    d = r.json()
    crp = d["client_recommended_parameters"]
    assert crp["chunk_size_max_bytes"] == 50 * 1024 * 1024
    assert crp["client_timeout_s_per_chunk"] == 90
    assert crp["max_retries_5xx"] == 5
    assert crp["backoff_strategy"] == "exponential"
    assert "user_agent_hint" in crp
    assert crp["x_upload_id_regex"] == "^[A-Za-z0-9._-]{8,64}$"
    assert "probe_network_endpoint" in crp


def test_probe_invalid_probe_id_rejected(probe_client):
    client, _ = probe_client
    payload = b"\x00" * 100
    r = client.post(
        f"{P}/diagnostic/pee-maj/probe-network",
        headers={**HDR, "X-Expected-Size": "100",
                  "X-Probe-Id": "x"},  # trop court (< 8 chars)
        files={"file": ("probe.bin", payload, "application/octet-stream")},
    )
    assert r.status_code == 400
    assert "X-Probe-Id" in r.json()["detail"]
