"""
Phase XXVIII VOIE B · S3/B2 Upload Router — Tests unitaires anti-régressifs
════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · FUSION ADD-ONLY

Ces tests valident la contrat structurel de `gis_s3_upload_router_omega`
sans téléverser réellement vers Backblaze B2. Le test E2E live (15 Mo
vers B2) est géré par le script `/tmp/test_s3_e2e_15mb.py`.

Portée :
  · Présence des 5 endpoints publics
  · Helper `_ensure_slot_in_manifest` ANTI-KeyError (regression
    fix du test E2E T3 RETRY2)
  · Helper `_read_manifest_raw` auto-sync SLOT_BY_ID (FUSION ADD-ONLY)
  · Idempotence de _finalize_manifest_from_b2 (flag session["manifest_finalized"])
  · Intégration SLOT_BY_ID : FORET_MFFP_PEE_MAJ_Ω référencé
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def s3_router():
    """Charge le module router S3/B2."""
    return importlib.import_module("routes.gis_s3_upload_router_omega")


def test_router_has_five_endpoints(s3_router):
    """Les 5 endpoints attendus sont enregistrés sur le router FastAPI."""
    paths = {r.path for r in s3_router.router.routes}
    expected = {
        "/api/v30/admin-premium/gis/diagnostic/pee-maj/probe-s3-credentials",
        "/api/v30/admin-premium/gis/upload-chunk-s3/{slot_id}",
        "/api/v30/admin-premium/gis/upload-chunk-s3/{slot_id}/resume/{upload_id}",
        "/api/v30/admin-premium/gis/upload-chunk-s3/{slot_id}/abort/{upload_id}",
        "/api/v30/admin-premium/gis/pee-maj/s3-finalize/{upload_id}",
        "/api/v30/admin-premium/gis/s3/status/{slot_id}",
    }
    missing = expected - paths
    assert not missing, f"Endpoints manquants : {missing}"


def test_ensure_slot_anti_keyerror(s3_router):
    """_ensure_slot_in_manifest ne lève JAMAIS KeyError pour un slot
    référencé dans SLOT_BY_ID même si absent du manifest (fix T3 RETRY2)."""
    manifest = {"manifest_id": "TEST", "slots": {}}
    slot = s3_router._ensure_slot_in_manifest("FORET_MFFP_PEE_MAJ_Ω", manifest)
    assert slot["slot_id"] == "FORET_MFFP_PEE_MAJ_Ω"
    assert slot["status"] == "ABSENT"
    assert slot["uploads"] == []
    # Second appel : idempotent (ne réécrase pas)
    slot["status"] = "LOADED"
    slot_again = s3_router._ensure_slot_in_manifest(
        "FORET_MFFP_PEE_MAJ_Ω", manifest)
    assert slot_again["status"] == "LOADED", (
        "_ensure_slot_in_manifest doit être idempotent")


def test_ensure_slot_unknown_slot(s3_router):
    """Slot non référencé → init avec label=slot_id, priority=P? (pas crash)."""
    manifest = {"slots": {}}
    slot = s3_router._ensure_slot_in_manifest("UNKNOWN_SLOT_Ω", manifest)
    assert slot["slot_id"] == "UNKNOWN_SLOT_Ω"
    assert slot["priority"] == "P?"


def test_read_manifest_raw_auto_sync(s3_router, tmp_path, monkeypatch):
    """_read_manifest_raw auto-ajoute les slots SLOT_BY_ID absents."""
    fake_manifest = tmp_path / "GIS_RECEPTION_INTAKE_Ω.json"
    fake_manifest.write_text(
        json.dumps({"manifest_id": "TEST", "slots": {}}),
        encoding="utf-8")
    monkeypatch.setattr(s3_router, "MANIFEST_PATH", fake_manifest)
    m = s3_router._read_manifest_raw()
    assert "FORET_MFFP_PEE_MAJ_Ω" in m["slots"], (
        "Auto-sync doit ajouter FORET_MFFP_PEE_MAJ_Ω")
    assert m["slots"]["FORET_MFFP_PEE_MAJ_Ω"]["status"] == "ABSENT"


def test_slot_by_id_integration(s3_router):
    """SLOT_BY_ID expose bien FORET_MFFP_PEE_MAJ_Ω avec voie_acquisition VOIE_A."""
    from engines.v8_institutional.especes.gis_reception_validators_omega import (
        SLOT_BY_ID,
    )
    assert "FORET_MFFP_PEE_MAJ_Ω" in SLOT_BY_ID
    spec = SLOT_BY_ID["FORET_MFFP_PEE_MAJ_Ω"]
    assert spec["priority"] == "P0"
    assert spec["formats_acceptes"] == ["gpkg"]


def test_write_manifest_atomic(s3_router, tmp_path, monkeypatch):
    """_write_manifest écrit atomiquement (rename via .partial)."""
    fake_manifest = tmp_path / "GIS_RECEPTION_INTAKE_Ω.json"
    monkeypatch.setattr(s3_router, "MANIFEST_PATH", fake_manifest)
    data = {"manifest_id": "X", "slots": {"A": {"status": "LOADED"}}}
    s3_router._write_manifest(data)
    assert fake_manifest.exists()
    reloaded = json.loads(fake_manifest.read_text(encoding="utf-8"))
    assert reloaded["slots"]["A"]["status"] == "LOADED"
    assert "last_updated_utc" in reloaded
    # Aucun fichier .partial résiduel
    assert not (tmp_path / "GIS_RECEPTION_INTAKE_Ω.partial").exists()


def test_safe_upload_id_regex(s3_router):
    """Validation du regex de sécurité sur upload_id."""
    assert s3_router.SAFE_UPLOAD_ID.match("abc12345")  # 8 chars min
    assert s3_router.SAFE_UPLOAD_ID.match("e2e.abcd1234efgh")
    assert not s3_router.SAFE_UPLOAD_ID.match("short")  # < 8 chars
    assert not s3_router.SAFE_UPLOAD_ID.match("a" * 65)  # > 64 chars
    assert not s3_router.SAFE_UPLOAD_ID.match("bad/path")  # "/" interdit


def test_safe_filename_regex(s3_router):
    """Validation du regex de sécurité sur filename."""
    assert s3_router.SAFE_FILENAME.match("pee_maj.gpkg")
    assert not s3_router.SAFE_FILENAME.match("../etc/passwd")
    assert not s3_router.SAFE_FILENAME.match("file name with spaces.gpkg")


def test_finalize_idempotence_marker(s3_router):
    """_finalize_manifest_from_b2 doit sortir early si manifest_finalized=True."""
    # Simulation : session déjà finalisée
    session = {
        "slot_id": "FORET_MFFP_PEE_MAJ_Ω",
        "b2_key": "pee_maj/test/x.gpkg",
        "filename": "x.gpkg",
        "upload_id_ui": "test.abcd1234",
        "b2_upload_id": "fake-upload-id",
        "manifest_finalized": True,
        "sha256_global": "a" * 64,
        "final_size_bytes": 1024,
        "composite_sha256": "b" * 64,
        "files_loaded_count": 1,
        "slot_status": "LOADED",
    }
    # s3=None, bucket="" : ne doit PAS être utilisés car idempotent_skip
    result = s3_router._finalize_manifest_from_b2(session, s3=None, bucket="")
    assert result["idempotent_skip"] is True
    assert result["sha256_global"] == "a" * 64
    assert result["size_bytes"] == 1024


def test_session_dir_persistent(s3_router):
    """S3_SESSIONS_DIR est bien sur /app (ext4 persistant, survit au pod restart)."""
    assert str(s3_router.S3_SESSIONS_DIR).startswith("/app/"), (
        "Sessions S3 DOIVENT être sur /app ext4, pas /var/cache éphémère")
    assert s3_router.S3_SESSIONS_DIR.exists()


def test_manifest_path_canonical(s3_router):
    """MANIFEST_PATH pointe vers le manifest institutionnel canonique."""
    assert str(s3_router.MANIFEST_PATH) == (
        "/app/backend/data/gis_operational/GIS_RECEPTION_INTAKE_Ω.json")
