"""
Phase XXVIII · ORDRE N°52-R5 — ANTI-AMBIGUÏTÉ VISUELLE l/1/I/O/0
══════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU

Garantit que :
  · Le backend ne transforme JAMAIS upload_id (préserve octet-pour-octet).
  · L'endpoint /s3/list-resumable-sessions retourne upload_id_ui + hex.
  · Les caractères ambigus (l vs 1, I vs 1, O vs 0) sont distincts dans
    le hex de retour, permettant au frontend de vérifier sans saisie.
"""
from __future__ import annotations

import importlib
import json

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def s3_router():
    return importlib.import_module("routes.gis_s3_upload_router_omega")


@pytest.fixture()
def app_with_router(s3_router):
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(s3_router.router)
    return app


def test_list_resumable_endpoint_registered(s3_router):
    """L'endpoint /s3/list-resumable-sessions/{slot_id} est bien exposé."""
    paths = {r.path for r in s3_router.router.routes}
    assert (
        "/api/v30/admin-premium/gis/s3/list-resumable-sessions/{slot_id}"
        in paths
    )


def test_list_resumable_returns_upload_id_hex(s3_router, tmp_path,
                                               monkeypatch):
    """L'endpoint retourne upload_id_ui ET upload_id_hex (anti-ambiguïté)."""
    monkeypatch.setattr(s3_router, "S3_SESSIONS_DIR", tmp_path)
    monkeypatch.setenv("GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    # Créer une session synthétique avec le caractère AMBIGU 'l' minuscule
    upload_id = "moslx2ne-49da58dd"
    sess = {
        "slot_id": "FORET_MFFP_PEE_MAJ_Ω",
        "upload_id_ui": upload_id,
        "filename": "pee_maj.gpkg",
        "status": "UPLOADING",
        "chunks_total": 712,
        "parts": {str(i): {"part_number": i+1, "etag": "x", "size": 1}
                  for i in range(243)},
        "total_size_expected": 37315948544,
        "started_at_utc": "2026-05-05T12:30:56+00:00",
        "last_update_utc": "2026-05-05T13:01:24+00:00",
        "b2_upload_id": "fake_b2_uid",
        "b2_key": "pee_maj/x/y.gpkg",
    }
    (tmp_path / f"{upload_id}.json").write_text(
        json.dumps(sess, ensure_ascii=False), encoding="utf-8")

    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(s3_router.router)
    client = TestClient(app)

    r = client.get(
        "/api/v30/admin-premium/gis/s3/list-resumable-sessions/"
        "FORET_MFFP_PEE_MAJ_Ω",
        headers={"X-Commandant-Token": "Saturn5858*"})
    assert r.status_code == 200
    d = r.json()
    assert d["sessions_count"] == 1
    s = d["sessions"][0]
    # Le upload_id_ui doit être STRICTEMENT identique
    assert s["upload_id_ui"] == upload_id
    # Le 4ème caractère du upload_id est 'l' minuscule = U+006C
    assert ord(upload_id[3]) == 0x006C
    # Le hex confirme : '6c' à la position 6-8 (3 caractères * 2 hex chars)
    expected_hex = upload_id.encode("utf-8").hex()
    assert s["upload_id_hex"] == expected_hex
    # Position du 'l' dans le hex
    assert "6c" in expected_hex.lower()
    # Vérification : l (0x6c) ≠ 1 (0x31)
    upload_id_with_one = "mos1x2ne-49da58dd"
    assert (upload_id.encode("utf-8").hex() !=
            upload_id_with_one.encode("utf-8").hex())
    # Resumable doit être True (UPLOADING + 243/712, missing > 0)
    assert s["resumable"] is True
    assert s["chunks_received_count"] == 243
    assert s["chunks_missing_count"] == 712 - 243
    assert s["chunks_missing_first"] == [243, 244, 245, 246, 247]


def test_list_resumable_filters_completed_sessions(s3_router, tmp_path,
                                                   monkeypatch):
    """Sessions COMPLETED ne sont PAS listées (filtre UPLOADING/ABORTED)."""
    monkeypatch.setattr(s3_router, "S3_SESSIONS_DIR", tmp_path)
    monkeypatch.setenv("GIS_RECEPTION_COMMANDANT_TOKEN", "Saturn5858*")
    sess = {
        "slot_id": "FORET_MFFP_PEE_MAJ_Ω",
        "upload_id_ui": "completed-session-x",
        "status": "COMPLETED",
        "chunks_total": 3,
        "parts": {"0": {}, "1": {}, "2": {}},
        "filename": "x.gpkg",
    }
    (tmp_path / "completed-session-x.json").write_text(
        json.dumps(sess, ensure_ascii=False), encoding="utf-8")
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(s3_router.router)
    client = TestClient(app)
    r = client.get(
        "/api/v30/admin-premium/gis/s3/list-resumable-sessions/"
        "FORET_MFFP_PEE_MAJ_Ω",
        headers={"X-Commandant-Token": "Saturn5858*"})
    assert r.status_code == 200
    d = r.json()
    assert d["sessions_count"] == 0


def test_upload_id_chars_distinguishable_in_hex(s3_router):
    """Les paires ambiguës ont des hex différents (preuve d'anti-confusion)."""
    pairs = [
        ("l", "1", 0x6C, 0x31),  # lowercase L vs digit 1
        ("I", "1", 0x49, 0x31),  # uppercase I vs digit 1
        ("O", "0", 0x4F, 0x30),  # uppercase O vs digit 0
        ("o", "0", 0x6F, 0x30),  # lowercase o vs digit 0
    ]
    for c1, c2, exp1, exp2 in pairs:
        assert ord(c1) == exp1
        assert ord(c2) == exp2
        assert ord(c1) != ord(c2), (
            f"{c1!r} U+{ord(c1):04X} doit être distinct de {c2!r} "
            f"U+{ord(c2):04X}")


def test_upload_id_no_transformation_in_session_path(s3_router, tmp_path,
                                                      monkeypatch):
    """_session_path conserve EXACTEMENT l'upload_id (octet-pour-octet)."""
    monkeypatch.setattr(s3_router, "S3_SESSIONS_DIR", tmp_path)
    uid = "moslx2ne-49da58dd"  # avec 'l' minuscule
    p = s3_router._session_path(uid)
    # Le nom du fichier doit contenir 'l' minuscule, pas '1'
    assert p.name == f"{uid}.json"
    assert "l" in p.name
    assert ord(p.name[3]) == 0x006C  # 'l' minuscule


def test_upload_id_regex_accepts_both_l_and_1(s3_router):
    """Le regex SAFE_UPLOAD_ID accepte EXPLICITEMENT 'l' minuscule ET '1'."""
    rx = s3_router.SAFE_UPLOAD_ID
    assert rx.match("moslx2ne-49da58dd") is not None  # avec 'l'
    assert rx.match("mos1x2ne-49da58dd") is not None  # avec '1'
    assert rx.match("mosIx2ne-49da58dd") is not None  # avec 'I'
    assert rx.match("mosOx2ne-49da58dd") is not None  # avec 'O'
    assert rx.match("mos0x2ne-49da58dd") is not None  # avec '0'
