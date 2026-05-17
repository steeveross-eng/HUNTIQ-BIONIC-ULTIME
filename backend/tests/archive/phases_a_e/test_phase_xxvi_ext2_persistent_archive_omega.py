"""
test_phase_xxvi_ext2_persistent_archive_omega.py — Phase XXVI-EXT2 (ORDRE N°52-EXT)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°52-EXT

Tests de l'archive persistante (VARIANTE A — 5 slots légers) :
  GET  /diagnostic/persistent-archive/status
  POST /diagnostic/persistent-archive/restore
  + hook d'archivage dans upload-chunk et upload mono
  + auto-restore via /health-snapshot

Pattern isolé (FastAPI dédiée + tmp_path).
Anti-régression strict — doctrine ANTI_GÉNÉRIQUE respectée.
═════════════════════════════════════════════════════════════════════════════
"""
import os
import sys
import importlib
import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, "/app/backend")

TEST_TOKEN = "TEST_TOKEN_ARCHIVE_OMEGA"


@pytest.fixture(scope="module")
def archive_client(tmp_path_factory):
    tmp_root = tmp_path_factory.mktemp("gis_archive_xxvi_ext2")
    os.environ["GIS_RECEPTION_COMMANDANT_TOKEN"] = TEST_TOKEN
    os.environ.pop("BCE4X_HARDENED_PIPELINE_MODE", None)

    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    mod.RECEPTION_ROOT = Path(tmp_root) / "gis_operational"
    mod.INCOMING_DIR = mod.RECEPTION_ROOT / "incoming"
    mod.QUARANTINE_DIR = mod.RECEPTION_ROOT / "quarantine"
    mod.MANIFEST_PATH = mod.RECEPTION_ROOT / "GIS_RECEPTION_INTAKE_Ω.json"
    mod.HARDENED_FLAG_PATH = mod.RECEPTION_ROOT / "hardened_mode_omega.json"
    mod.DIAG_MARKER_PATH = mod.RECEPTION_ROOT / "diagnostic_marker_omega.json"
    mod.ARCHIVE_ROOT = Path(tmp_root) / "gis_archive"
    mod.ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    mod.INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    mod.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = mod.RECEPTION_ROOT / "audit_log.jsonl"
    audit_mod.AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    app = FastAPI()
    app.include_router(mod.router)
    yield TestClient(app), mod


HDR = {"X-Commandant-Token": TEST_TOKEN}
P = "/api/v30/admin-premium/gis"


def _make_valid_geojson(size_target: int = 3000) -> bytes:
    """Génère un GeoJSON valide > 512 octets (minimum slot)."""
    fc = {"type": "FeatureCollection",
          "name": "FIXTURE_TEST",
          "meta": {"test_fixture": True,
                   "description": "pytest ORDRE N°52-EXT archive persistante"},
          "features": []}
    while len(json.dumps(fc)) < size_target:
        fc["features"].append({
            "type": "Feature",
            "properties": {"k": f"fixture_{len(fc['features'])}"},
            "geometry": {"type": "Point",
                          "coordinates": [-68.38, 48.21]},
        })
    return json.dumps(fc).encode()


def test_archive_status_requires_token(archive_client):
    client, _ = archive_client
    r = client.get(f"{P}/diagnostic/persistent-archive/status")
    assert r.status_code == 401


def test_archive_status_initially_empty(archive_client):
    client, _ = archive_client
    r = client.get(f"{P}/diagnostic/persistent-archive/status", headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["variant"] == "A_5_slots_legers"
    assert d["totals"] == {"files": 0, "bytes": 0}
    assert set(d["archivable_slots_whitelist"]) == {
        "SOL_IRDA_Ω", "CHASSE_ZEC_SEPAQ_Ω", "ROUTES_MTQ_SECONDAIRES_Ω",
        "LIMITES_TERRITORIALES_FINES_Ω", "PRESSION_HUMAINE_Ω",
    }


def test_archive_whitelist_excludes_foret_mffp(archive_client):
    client, mod = archive_client
    assert "FORET_MFFP_Ω" not in mod.ARCHIVABLE_SLOTS


def test_upload_mono_triggers_archive_for_archivable_slot(archive_client):
    client, mod = archive_client
    content = _make_valid_geojson(3000)
    r = client.post(f"{P}/upload/SOL_IRDA_Ω",
                     files={"file": ("archive_e2e.geojson", content,
                                      "application/json")},
                     headers=HDR)
    assert r.status_code == 200, r.text[:400]
    d = r.json()
    assert d["passed"] is True
    assert d["persistent_archive"]["archived"] is True
    assert d["persistent_archive"]["sha256"] == d["sha256"]
    # Vérifier inventaire
    s = client.get(f"{P}/diagnostic/persistent-archive/status",
                    headers=HDR).json()
    assert s["inventory"]["SOL_IRDA_Ω"]["files_count"] == 1


def test_upload_foret_mffp_is_not_archived(archive_client):
    """FORET_MFFP_Ω n'est pas archivé (trop volumineux · exclu de la variante A)."""
    client, mod = archive_client
    content = _make_valid_geojson(3000)
    r = client.post(f"{P}/upload/FORET_MFFP_Ω",
                     files={"file": ("foret_test.geojson", content,
                                      "application/json")},
                     headers=HDR)
    assert r.status_code == 200, r.text[:400]
    d = r.json()
    assert d["passed"] is True
    assert d["persistent_archive"]["archived"] is False
    assert d["persistent_archive"]["reason"] == "NOT_APPLICABLE"


def test_auto_restore_via_health_snapshot(archive_client):
    client, mod = archive_client
    # Upload d'un fichier dans SOL_IRDA_Ω (already fait plus tôt)
    content = _make_valid_geojson(3500)
    client.post(f"{P}/upload/SOL_IRDA_Ω",
                 files={"file": ("restore_test.geojson", content,
                                  "application/json")},
                 headers=HDR)

    # Vérifier présence physique initiale
    incoming_file = mod.INCOMING_DIR / "SOL_IRDA_Ω" / "restore_test.geojson"
    assert incoming_file.exists()

    # Simuler perte /var/cache
    incoming_file.unlink()
    assert not incoming_file.exists()

    # /health-snapshot déclenche auto-restore
    r = client.get(f"{P}/health-snapshot", headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["auto_restore_files_count"] >= 1
    # Fichier re-présent
    assert incoming_file.exists()


def test_manual_restore_endpoint_single_slot(archive_client):
    client, mod = archive_client
    # Créer manifest + fichier + archive pour PRESSION_HUMAINE_Ω
    content = _make_valid_geojson(4000)
    r = client.post(f"{P}/upload/PRESSION_HUMAINE_Ω",
                     files={"file": ("manual_test.geojson", content,
                                      "application/json")},
                     headers=HDR)
    assert r.status_code == 200

    # Simuler perte
    incoming_file = mod.INCOMING_DIR / "PRESSION_HUMAINE_Ω" / "manual_test.geojson"
    incoming_file.unlink()

    # Restore manuel
    r = client.post(f"{P}/diagnostic/persistent-archive/restore",
                     json={"slot_id": "PRESSION_HUMAINE_Ω"}, headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["total_restored_files"] >= 1
    assert incoming_file.exists()


def test_manual_restore_all(archive_client):
    client, _ = archive_client
    r = client.post(f"{P}/diagnostic/persistent-archive/restore",
                     json={"restore_all": True}, headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert "results" in d
    assert len(d["results"]) == 5  # 5 slots archivables


def test_manual_restore_rejects_non_archivable(archive_client):
    client, _ = archive_client
    r = client.post(f"{P}/diagnostic/persistent-archive/restore",
                     json={"slot_id": "FORET_MFFP_Ω"}, headers=HDR)
    assert r.status_code == 400
    assert "SLOT_NOT_IN_WHITELIST" in r.json()["detail"]


def test_manual_restore_requires_slot_or_all(archive_client):
    client, _ = archive_client
    r = client.post(f"{P}/diagnostic/persistent-archive/restore",
                     json={}, headers=HDR)
    assert r.status_code == 400


def test_health_snapshot_exposes_archive_flags(archive_client):
    client, _ = archive_client
    r = client.get(f"{P}/health-snapshot", headers=HDR)
    d = r.json()
    f = d["flags"]
    assert f["persistent_archive_enabled"] is True
    assert f["persistent_archive_variant"] == "A_5_slots_legers"
    assert "persistent_archive_root" in f
    assert isinstance(f["archivable_slots"], list)
    assert len(f["archivable_slots"]) == 5


def test_archive_audit_events_consigned(archive_client):
    client, _ = archive_client
    r = client.get(f"{P}/audit-log", headers=HDR)
    d = r.json()
    evs = d["stats"]["events_by_type"]
    # Après les uploads précédents on doit avoir des PHYS_ARCHIVE_PERSISTED_Ω
    assert evs.get("PHYS_ARCHIVE_PERSISTED_Ω", 0) >= 1


def test_archive_idempotent_existing_file(archive_client):
    """Uploader 2 fois le même fichier doit re-archiver (dédup par filename)."""
    client, mod = archive_client
    content = _make_valid_geojson(3200)
    # Premier upload
    r1 = client.post(f"{P}/upload/CHASSE_ZEC_SEPAQ_Ω",
                      files={"file": ("idem_test.geojson", content,
                                       "application/json")},
                      headers=HDR)
    assert r1.json()["persistent_archive"]["archived"] is True
    # Re-upload
    r2 = client.post(f"{P}/upload/CHASSE_ZEC_SEPAQ_Ω",
                      files={"file": ("idem_test.geojson", content,
                                       "application/json")},
                      headers=HDR)
    assert r2.json()["persistent_archive"]["archived"] is True
    # Pas de doublon dans l'inventaire (os.replace écrase atomiquement)
    s = client.get(f"{P}/diagnostic/persistent-archive/status",
                    headers=HDR).json()
    zec_files = s["inventory"]["CHASSE_ZEC_SEPAQ_Ω"]["files"]
    idem = [f for f in zec_files if f["filename"] == "idem_test.geojson"]
    assert len(idem) == 1
