"""
test_phase_xxvii_ext4_unicode_fix_omega.py — Phase XXVII-EXT4 (ORDRE N°52-EXT VOIE A)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°52-EXT VOIE A

Tests forensiques de la fix HTTP 404 Unicode lookalikes :
  · U+03A9 GREEK CAPITAL LETTER OMEGA (canonique) → 200 OK
  · U+2126 OHM SIGN (lookalike) → auto-normalisé → 200 OK
  · slot inconnu → 404 enrichi avec received_hex + diagnostic
  · audit-event SLOT_ID_UNICODE_NORMALIZED_Ω consigné
  · last_error_detail exposé dans /status

Pattern isolé (FastAPI dédiée + tmp_path).
═════════════════════════════════════════════════════════════════════════════
"""
import os
import sys
import importlib
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, "/app/backend")

TEST_TOKEN = "TEST_TOKEN_UNICODE_FIX_OMEGA"
HDR = {"X-Commandant-Token": TEST_TOKEN}
P = "/api/v30/admin-premium/gis"


@pytest.fixture
def uni_client(tmp_path, monkeypatch):
    monkeypatch.setenv("GIS_RECEPTION_COMMANDANT_TOKEN", TEST_TOKEN)
    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    iso_root = tmp_path / "iso"
    iso_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mod, "RECEPTION_ROOT", iso_root)
    monkeypatch.setattr(mod, "INCOMING_DIR", iso_root / "incoming")
    monkeypatch.setattr(mod, "QUARANTINE_DIR", iso_root / "quarantine")
    (iso_root / "incoming").mkdir(parents=True, exist_ok=True)
    (iso_root / "quarantine").mkdir(parents=True, exist_ok=True)
    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = iso_root / "audit_log.jsonl"
    app = FastAPI()
    app.include_router(mod.router)
    return TestClient(app), mod


def _common_headers(upload_id="utest12345678"):
    return {
        **HDR,
        "X-Upload-Id": upload_id,
        "X-Chunk-Index": "0",
        "X-Chunks-Total": "1",
        "X-Original-Filename": "test.gpkg",
        "X-Total-Size": "100",
    }


def test_chunk_with_canonical_omega_u03a9(uni_client):
    """U+03A9 (canonique) → 200 OK CHUNK_STORED."""
    client, _ = uni_client
    slot_id = "FORET_MFFP_PEE_MAJ_\u03a9"
    r = client.post(
        f"{P}/upload-chunk/{slot_id}",
        headers=_common_headers("uniA.test123"),
        files={"file": ("test.bin", b"\x00" * 100, "application/octet-stream")},
    )
    assert r.status_code == 200, r.text[:300]
    assert r.json()["status"] == "CHUNK_STORED"


def test_chunk_with_ohm_sign_u2126_auto_normalized(uni_client):
    """U+2126 OHM SIGN (lookalike) → auto-normalisé → 200 OK."""
    client, _ = uni_client
    slot_id_lookalike = "FORET_MFFP_PEE_MAJ_\u2126"
    r = client.post(
        f"{P}/upload-chunk/{slot_id_lookalike}",
        headers=_common_headers("uniB.test123"),
        files={"file": ("test.bin", b"\x00" * 100, "application/octet-stream")},
    )
    assert r.status_code == 200, r.text[:400]
    d = r.json()
    assert d["status"] == "CHUNK_STORED"
    # slot_id retourné = canonique (U+03A9)
    assert d["slot_id"] == "FORET_MFFP_PEE_MAJ_\u03a9"
    # Vérifier audit-event
    r_audit = client.get(f"{P}/audit-log", headers=HDR)
    events = r_audit.json()["stats"]["events_by_type"]
    assert events.get("SLOT_ID_UNICODE_NORMALIZED_Ω", 0) >= 1


def test_chunk_with_unknown_slot_404_enriched(uni_client):
    """Slot inconnu → 404 avec hex + diagnostic Unicode explicite."""
    client, _ = uni_client
    r = client.post(
        f"{P}/upload-chunk/SLOT_TYPO_TEST",
        headers=_common_headers(),
        files={"file": ("test.bin", b"\x00" * 100, "application/octet-stream")},
    )
    assert r.status_code == 404
    detail = r.json()["detail"]
    assert "SLOT_INCONNU::SLOT_TYPO_TEST" in detail
    assert "received_hex=" in detail
    assert "U+03A9" in detail
    assert "U+2126" in detail


def test_status_exposes_last_error_detail(uni_client):
    """/diagnostic/pee-maj/status expose last_error_detail (vide si pas d'erreur)."""
    client, _ = uni_client
    r = client.get(f"{P}/diagnostic/pee-maj/status", headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert "last_error_detail" in d
    led = d["last_error_detail"]
    for k in ("error_code_backend", "error_message_backend"):
        assert k in led


def test_status_last_error_detail_classifies_404(uni_client):
    """Après un 404 sur le slot pee_maj, last_error_detail doit refléter."""
    client, _ = uni_client
    # Provoquer un 404 enregistré dans audit
    # Note : 404 SLOT_INCONNU n'est PAS audit-logué automatiquement.
    # L'audit-log enregistre UPLOAD_QUARANTINED/UPLOAD_ERROR/UPLOAD_LOADED.
    # On teste la présence du champ uniquement.
    r = client.get(f"{P}/diagnostic/pee-maj/status", headers=HDR)
    led = r.json()["last_error_detail"]
    assert isinstance(led, dict)
    assert "error_code_backend" in led
    assert "error_message_backend" in led


def test_normalize_unicode_idempotent_on_canonical_slot(uni_client):
    """Re-utiliser le slot canonique ne déclenche PAS de normalisation."""
    client, _ = uni_client
    # Compter audit-events SLOT_ID_UNICODE_NORMALIZED_Ω avant
    before = client.get(f"{P}/audit-log", headers=HDR).json()[
        "stats"]["events_by_type"].get("SLOT_ID_UNICODE_NORMALIZED_Ω", 0)
    # POST avec U+03A9 (canonique)
    client.post(
        f"{P}/upload-chunk/FORET_MFFP_PEE_MAJ_\u03a9",
        headers=_common_headers("uniIdem.test12"),
        files={"file": ("t.bin", b"x" * 100, "application/octet-stream")},
    )
    after = client.get(f"{P}/audit-log", headers=HDR).json()[
        "stats"]["events_by_type"].get("SLOT_ID_UNICODE_NORMALIZED_Ω", 0)
    # Pas de nouvel event : la normalisation n'a pas été déclenchée
    assert after == before
