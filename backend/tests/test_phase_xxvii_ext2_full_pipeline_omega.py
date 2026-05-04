"""
test_phase_xxvii_ext2_full_pipeline_omega.py — Phase XXVII-EXT2
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°52-EXT VOIE A

Tests de l'endpoint composite POST /diagnostic/pee-maj/full-pipeline-execute :
  · Auth requise
  · 409 si pee_maj_canonical_active=False
  · 200 + 3 phases exécutées si canonical actif
  · Audit-event composite PEE_MAJ_FULL_PIPELINE_EXECUTED_Ω
  · Idempotence : phase 3 saute si archive existe déjà
  · Disclosure honnête (no_simulation_executed=True)

Pattern E2E réel avec cleanup automatique.
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

TEST_TOKEN = "TEST_TOKEN_FULL_PIPELINE_OMEGA"
HDR = {"X-Commandant-Token": TEST_TOKEN}
P = "/api/v30/admin-premium/gis"


@pytest.fixture
def fp_client(tmp_path, monkeypatch):
    monkeypatch.setenv("GIS_RECEPTION_COMMANDANT_TOKEN", TEST_TOKEN)
    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    iso_root = tmp_path / "iso_root"
    iso_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mod, "RECEPTION_ROOT", iso_root)
    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = iso_root / "audit_log.jsonl"

    app = FastAPI()
    app.include_router(mod.router)
    return TestClient(app), mod


def test_full_pipeline_requires_token(fp_client):
    client, _ = fp_client
    r = client.post(f"{P}/diagnostic/pee-maj/full-pipeline-execute")
    assert r.status_code == 401


def test_full_pipeline_409_when_canonical_inactive(fp_client):
    """Sans pee_maj.gpkg → 409 honnête + message anti-générique."""
    client, _ = fp_client
    r = client.post(f"{P}/diagnostic/pee-maj/full-pipeline-execute",
                     headers=HDR)
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert "PEE_MAJ_CANONICAL_INACTIVE" in detail
    assert "anti-générique" in detail.lower()


def test_full_pipeline_e2e_real_fixture(tmp_path, monkeypatch):
    """E2E réel : crée pee_maj.gpkg fixture, exécute pipeline, vérifie 3 phases."""
    monkeypatch.setenv("GIS_RECEPTION_COMMANDANT_TOKEN", TEST_TOKEN)

    real_src = Path("/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω/pee_maj.gpkg")
    real_compressed = real_src.with_suffix(".gpkg.zstd")
    real_archive = Path("/app/backend/data/gis_archive/pee_maj.gpkg.zstd")
    if real_src.exists() or real_archive.exists():
        pytest.skip("PROD pee_maj fixtures present, skip to avoid impact")

    real_src.parent.mkdir(parents=True, exist_ok=True)
    # Fixture 5 Mo zéros (ratio compression > 50x)
    real_src.write_bytes(b"SQLite format 3\x00" + b"\x00" * (5 * 1024 * 1024))

    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    iso_root = tmp_path / "iso_root"
    iso_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mod, "RECEPTION_ROOT", iso_root)
    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = iso_root / "audit_log.jsonl"

    try:
        app = FastAPI()
        app.include_router(mod.router)
        client = TestClient(app)

        r = client.post(f"{P}/diagnostic/pee-maj/full-pipeline-execute",
                         headers=HDR)
        assert r.status_code == 200, r.text[:500]
        d = r.json()

        # Manifest cohérence
        assert d["manifest_id"] == "PEE_MAJ_FULL_PIPELINE_EXECUTED_Ω"
        assert d["doctrine"] == "ANTI_GÉNÉRIQUE_STRICT"
        assert d["audit_event_composite"] == "PEE_MAJ_FULL_PIPELINE_EXECUTED_Ω"
        assert d["honest_disclosure"]["no_simulation_executed"] is True
        assert d["honest_disclosure"]["anti_generique_strict"] is True
        assert d["v30_lock"] == "INVIOLÉ"

        # Phase 1 (couches dérivées non calculées → STUB_READY)
        p1 = d["phase1_compute_corridors_gis"]
        assert p1["status"] in ("STUB_READY", "OPERATIONAL")
        assert p1["pee_maj_canonical_active"] is True
        assert p1["pee_maj_substitutes_slot"] == "FORET_MFFP_Ω"
        assert isinstance(p1["elapsed_s"], (int, float))

        # Phase 2 (rien à persister car pas de calcul effectif)
        p2 = d["phase2_persist_derivatives"]
        assert p2["persisted_count"] == 0
        assert p2["skipped_count"] == 9
        assert p2["failed_count"] == 0

        # Phase 3 (compression + archivage 5 Mo zéros → ratio > 50x)
        p3 = d["phase3_compress_and_archive"]
        assert p3["compressed"]["ratio"] > 50
        assert p3["archive_persistent"]["archived"] is True
        assert real_archive.exists()
        assert p3["raw"]["sha256"]
        assert p3["compressed"]["sha256"]

        # Total elapsed cohérent
        assert d["total_elapsed_s"] >= p3["elapsed_s"]
    finally:
        if real_src.exists():
            real_src.unlink()
        if real_compressed.exists():
            real_compressed.unlink()
        if real_archive.exists():
            real_archive.unlink()


def test_full_pipeline_idempotent_phase3(tmp_path, monkeypatch):
    """2ᵉ appel doit sauter phase 3 (archive existante)."""
    monkeypatch.setenv("GIS_RECEPTION_COMMANDANT_TOKEN", TEST_TOKEN)

    real_src = Path("/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω/pee_maj.gpkg")
    real_compressed = real_src.with_suffix(".gpkg.zstd")
    real_archive = Path("/app/backend/data/gis_archive/pee_maj.gpkg.zstd")
    if real_src.exists() or real_archive.exists():
        pytest.skip("PROD pee_maj fixtures present")

    real_src.parent.mkdir(parents=True, exist_ok=True)
    real_src.write_bytes(b"SQLite format 3\x00" + b"\x00" * (3 * 1024 * 1024))

    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    iso_root = tmp_path / "iso_root_idem"
    iso_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mod, "RECEPTION_ROOT", iso_root)
    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = iso_root / "audit_log.jsonl"

    try:
        app = FastAPI()
        app.include_router(mod.router)
        client = TestClient(app)

        r1 = client.post(f"{P}/diagnostic/pee-maj/full-pipeline-execute",
                          headers=HDR)
        assert r1.status_code == 200
        d1 = r1.json()
        assert d1["phase3_compress_and_archive"]["archive_persistent"]["archived"] is True

        # 2ᵉ appel : phase 3 idempotent
        r2 = client.post(f"{P}/diagnostic/pee-maj/full-pipeline-execute",
                          headers=HDR)
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["phase3_compress_and_archive"]["skipped_idempotent"] is True
    finally:
        if real_src.exists():
            real_src.unlink()
        if real_compressed.exists():
            real_compressed.unlink()
        if real_archive.exists():
            real_archive.unlink()


def test_full_pipeline_audit_event_consigned(tmp_path, monkeypatch):
    """Vérifie que PEE_MAJ_FULL_PIPELINE_EXECUTED_Ω est consigné."""
    monkeypatch.setenv("GIS_RECEPTION_COMMANDANT_TOKEN", TEST_TOKEN)

    real_src = Path("/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω/pee_maj.gpkg")
    real_compressed = real_src.with_suffix(".gpkg.zstd")
    real_archive = Path("/app/backend/data/gis_archive/pee_maj.gpkg.zstd")
    if real_src.exists() or real_archive.exists():
        pytest.skip("PROD pee_maj fixtures present")

    real_src.parent.mkdir(parents=True, exist_ok=True)
    real_src.write_bytes(b"SQLite format 3\x00" + b"\x00" * (2 * 1024 * 1024))

    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    iso_root = tmp_path / "iso_root_audit"
    iso_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mod, "RECEPTION_ROOT", iso_root)
    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = iso_root / "audit_log.jsonl"

    try:
        app = FastAPI()
        app.include_router(mod.router)
        client = TestClient(app)
        client.post(f"{P}/diagnostic/pee-maj/full-pipeline-execute",
                     headers=HDR)
        # Vérifier audit-log
        r = client.get(f"{P}/audit-log", headers=HDR)
        events = r.json()["stats"]["events_by_type"]
        assert events.get("PEE_MAJ_FULL_PIPELINE_EXECUTED_Ω", 0) >= 1
    finally:
        if real_src.exists():
            real_src.unlink()
        if real_compressed.exists():
            real_compressed.unlink()
        if real_archive.exists():
            real_archive.unlink()
