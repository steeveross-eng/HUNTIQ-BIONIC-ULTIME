"""
test_phase_xxvi_ext_bce4x_hardened_omega.py — Phase XXVI-EXT (ORDRE N°52-EXT)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°52-EXT

Tests des nouveaux endpoints BCE4X_HARDENED_PIPELINE_MODE_Ω :
  POST /diagnostic/hardened/activate
  POST /diagnostic/hardened/deactivate
  GET  /diagnostic/hardened/status
  POST /diagnostic/validate-url
  GET  /upload-chunk/{slot_id}/resume/{upload_id}

Pattern isolé (FastAPI dédiée + tmp_path).
Anti-régression strict — aucune donnée synthétique.
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

TEST_TOKEN = "TEST_TOKEN_HARDENED_OMEGA"


@pytest.fixture(scope="module")
def hardened_client(tmp_path_factory):
    tmp_root = tmp_path_factory.mktemp("gis_hardened_xxvi_ext")
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
    mod.INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    mod.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = mod.RECEPTION_ROOT / "audit_log.jsonl"
    audit_mod.AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    app = FastAPI()
    app.include_router(mod.router)
    yield TestClient(app)


HDR = {"X-Commandant-Token": TEST_TOKEN}
HDR_KO = {"X-Commandant-Token": "WRONG"}
P = "/api/v30/admin-premium/gis"


def test_hardened_status_initially_disabled(hardened_client):
    r = hardened_client.get(f"{P}/diagnostic/hardened/status", headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["enabled"] is False
    assert d["flag_persistant_enabled"] is False
    assert d["env_var_enabled"] is False


def test_hardened_activate_requires_token(hardened_client):
    r = hardened_client.post(f"{P}/diagnostic/hardened/activate",
                              json={"activated_by": "x"})
    assert r.status_code == 401


def test_hardened_activate_rejects_wrong_token(hardened_client):
    r = hardened_client.post(f"{P}/diagnostic/hardened/activate",
                              json={"activated_by": "x"}, headers=HDR_KO)
    assert r.status_code == 401


def test_hardened_activate_then_status_enabled(hardened_client):
    r = hardened_client.post(f"{P}/diagnostic/hardened/activate",
                              json={"activated_by": "TEST_COMMANDANT",
                                    "reason": "pytest_xxvi_ext"},
                              headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["enabled"] is True
    assert d["manifest_id"] == "BCE4X_HARDENED_MODE_ACTIVATED_Ω"
    # Status reflète l'activation
    s = hardened_client.get(f"{P}/diagnostic/hardened/status", headers=HDR).json()
    assert s["enabled"] is True
    assert s["flag_persistant_enabled"] is True
    assert s["history_count"] >= 1
    last = s["history_recent"][-1]
    assert last["action"] == "ACTIVATE"
    assert last["activated_by"] == "TEST_COMMANDANT"


def test_hardened_anti_generique_no_fictive_promise(hardened_client):
    """Pas de promesse '100% réussite' dans le payload."""
    r = hardened_client.post(f"{P}/diagnostic/hardened/activate",
                              json={"activated_by": "x"}, headers=HDR)
    d = r.json()
    promise = d["effective_substitutes"]["100_percent_promise"]
    assert "ASYMPTOTIQUE" in promise.upper()
    # Doctrine ANTI_GÉNÉRIQUE_STRICT exposée
    assert d["doctrine"] == "ANTI_GÉNÉRIQUE_STRICT"
    # Bypass cloudflare remplacé par CLOUDFLARE_CONSTRAINT_HONORED_Ω
    assert "CLOUDFLARE_CONSTRAINT_HONORED" in d["effective_substitutes"]["cloudflare_constraint"]


def test_hardened_deactivate(hardened_client):
    # Réactiver pour s'assurer du baseline
    hardened_client.post(f"{P}/diagnostic/hardened/activate",
                         json={"activated_by": "x"}, headers=HDR)
    r = hardened_client.post(f"{P}/diagnostic/hardened/deactivate",
                              json={"activated_by": "x", "reason": "pytest"},
                              headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["enabled"] is False


def test_validate_url_ok_canonical_slot(hardened_client):
    r = hardened_client.post(f"{P}/diagnostic/validate-url",
                              json={"slot_id": "FORET_MFFP_Ω",
                                    "filename": "CARTE_ECO_MAJ_22I.gpkg",
                                    "upload_id": "retry22I.aaaaa1111"},
                              headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["passed"] is True
    assert d["slot_id_normalized"]["matched_canonical"] == "FORET_MFFP_Ω"
    assert d["filename_check"]["passed"] is True
    assert d["upload_id_check"]["passed"] is True
    assert "FORET_MFFP_%CE%A9" in d["canonical_endpoint"]


def test_validate_url_ko_filename_in_slot_position(hardened_client):
    """Hypothèse #1 du diag forensique : client passe filename comme slot_id."""
    r = hardened_client.post(f"{P}/diagnostic/validate-url",
                              json={"slot_id": "CARTE_ECO_MAJ_22I.gpkg"},
                              headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["passed"] is False
    assert d["slot_id_normalized"]["matched_canonical"] is None
    assert "FORET_MFFP_Ω" in d["slot_id_normalized"]["all_known_slot_ids"]


def test_validate_url_ko_unsafe_filename(hardened_client):
    r = hardened_client.post(f"{P}/diagnostic/validate-url",
                              json={"slot_id": "FORET_MFFP_Ω",
                                    "filename": "bad file with spaces.gpkg"},
                              headers=HDR)
    d = r.json()
    assert d["passed"] is False
    assert d["filename_check"]["passed"] is False


def test_validate_url_ko_invalid_upload_id(hardened_client):
    r = hardened_client.post(f"{P}/diagnostic/validate-url",
                              json={"slot_id": "FORET_MFFP_Ω",
                                    "upload_id": "x"},
                              headers=HDR)
    d = r.json()
    assert d["upload_id_check"]["passed"] is False


def test_resume_inexistant_session(hardened_client):
    r = hardened_client.get(
        f"{P}/upload-chunk/FORET_MFFP_Ω/resume/inexistant.aaa11111",
        headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["chunks_received_count"] == 0
    assert d["chunks_missing"] == []
    assert d["chunks_total"] is None


def test_resume_unknown_slot(hardened_client):
    r = hardened_client.get(
        f"{P}/upload-chunk/SLOT_INEXISTANT/resume/inexistant.aaa11111",
        headers=HDR)
    assert r.status_code == 404


def test_resume_invalid_upload_id(hardened_client):
    r = hardened_client.get(
        f"{P}/upload-chunk/FORET_MFFP_Ω/resume/x",
        headers=HDR)
    assert r.status_code == 400


def test_resume_requires_token(hardened_client):
    r = hardened_client.get(
        f"{P}/upload-chunk/FORET_MFFP_Ω/resume/aaaaaaaa")
    assert r.status_code == 401


def test_health_snapshot_exposes_hardened_flag(hardened_client):
    """Le flag doit apparaître dans /health-snapshot.flags."""
    r = hardened_client.get(f"{P}/health-snapshot", headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert "hardened_pipeline_mode" in d["flags"]
    assert "hardened_pipeline_mode_source" in d["flags"]
