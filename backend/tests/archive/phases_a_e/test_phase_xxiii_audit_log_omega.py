"""
test_phase_xxiii_audit_log_omega.py — Tests Phase XXIII (ORDRE N°44)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°44

Tests anti-régression de l'AUDIT_LOG_GIS_Ω + endpoint promote.

Scope :
  · Module audit (append, read, stats, purge)
  · Endpoint GET /audit-log (auth, filtres, limites)
  · Endpoint POST /promote (état GIS, transition vers SCEAU_X5_FINAL)
  · Persistance JSONL append-only
  · Anti-régression : aucun champ synthétique

V30 INVIOLABLE.
═════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def isolate_audit_log(tmp_path, monkeypatch):
    """Isole le fichier audit log dans un tmp_path par test."""
    from engines.v8_institutional.especes import gis_audit_log_omega as audit
    log_file = tmp_path / "audit_log.jsonl"
    monkeypatch.setattr(audit, "AUDIT_LOG_PATH", log_file)
    yield log_file


# ═══════════════════════════════════════════════════════════════════
# Module audit — append / read / stats / purge
# ═══════════════════════════════════════════════════════════════════
def test_append_event_creates_jsonl_entry(isolate_audit_log):
    from engines.v8_institutional.especes import gis_audit_log_omega as audit

    res = audit.append_event(
        event="UPLOAD_LOADED", slot_id="CHASSE_ZEC_SEPAQ_Ω",
        filename="x.geojson", sha256="a" * 64, size_bytes=1024,
        http_code=200, client_ip="127.0.0.1",
        user_agent="pytest", validators=[
            {"name": "check_format", "passed": True, "extra": "ignored"},
        ],
    )
    assert res["appended"]["slot_id"] == "CHASSE_ZEC_SEPAQ_Ω"
    assert res["appended"]["validators_summary"] == [
        {"name": "check_format", "passed": True}
    ]
    assert isolate_audit_log.exists()
    entries = audit.read_entries()
    assert len(entries) == 1
    assert entries[0]["sha256"] == "a" * 64


def test_append_multiple_and_stats(isolate_audit_log):
    from engines.v8_institutional.especes import gis_audit_log_omega as audit

    audit.append_event(event="UPLOAD_LOADED", slot_id="A", filename="a",
                        sha256=None, size_bytes=10, http_code=200,
                        client_ip="1.1.1.1", user_agent="ua")
    audit.append_event(event="UPLOAD_QUARANTINED", slot_id="A", filename="b",
                        sha256=None, size_bytes=20, http_code=422,
                        client_ip="1.1.1.1", user_agent="ua")
    audit.append_event(event="UPLOAD_ERROR", slot_id="B", filename="c",
                        sha256=None, size_bytes=0, http_code=404,
                        client_ip="2.2.2.2", user_agent="ua")
    s = audit.stats()
    assert s["total_events"] == 3
    assert s["events_by_type"]["UPLOAD_LOADED"] == 1
    assert s["events_by_type"]["UPLOAD_QUARANTINED"] == 1
    assert s["events_by_type"]["UPLOAD_ERROR"] == 1
    assert s["events_by_slot"]["A"] == 2
    assert s["events_by_slot"]["B"] == 1


def test_filter_by_slot_id_and_event(isolate_audit_log):
    from engines.v8_institutional.especes import gis_audit_log_omega as audit

    for sid, ev in [("A", "UPLOAD_LOADED"), ("B", "UPLOAD_LOADED"),
                     ("A", "UPLOAD_QUARANTINED")]:
        audit.append_event(event=ev, slot_id=sid, filename="x",
                            sha256=None, size_bytes=10, http_code=200,
                            client_ip="1.1.1.1", user_agent="ua")

    only_a = audit.read_entries(slot_id="A")
    assert len(only_a) == 2
    assert all(e["slot_id"] == "A" for e in only_a)

    only_loaded = audit.read_entries(event="UPLOAD_LOADED")
    assert len(only_loaded) == 2
    assert all(e["event"] == "UPLOAD_LOADED" for e in only_loaded)

    a_loaded = audit.read_entries(slot_id="A", event="UPLOAD_LOADED")
    assert len(a_loaded) == 1


def test_limit_truncates_results(isolate_audit_log):
    from engines.v8_institutional.especes import gis_audit_log_omega as audit
    for i in range(10):
        audit.append_event(event="UPLOAD_LOADED", slot_id=f"S{i}", filename=f"f{i}",
                            sha256=None, size_bytes=1, http_code=200,
                            client_ip="1.1.1.1", user_agent="ua")
    rows = audit.read_entries(limit=3)
    assert len(rows) == 3


def test_purge_removes_expired_entries(isolate_audit_log, monkeypatch):
    """Une entrée datant de >90 jours doit être purgée à l'append suivant."""
    from engines.v8_institutional.especes import gis_audit_log_omega as audit

    # Force rétention courte pour test (1 jour)
    monkeypatch.setenv("GIS_AUDIT_RETENTION_DAYS", "1")

    # Crée manuellement une vieille entrée
    old_ts = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(timespec="seconds")
    old_entry = json.dumps({
        "ts_utc": old_ts, "event": "UPLOAD_LOADED",
        "slot_id": "OLD", "filename": "old.bin",
        "sha256": None, "size_bytes": 0, "http_code": 200,
        "client_ip": "x", "user_agent": "x", "validators_summary": [],
    })
    isolate_audit_log.write_text(old_entry + "\n", encoding="utf-8")

    # Append nouvelle entrée → déclenche purge
    res = audit.append_event(event="UPLOAD_LOADED", slot_id="NEW",
                                filename="new.geojson", sha256=None,
                                size_bytes=10, http_code=200,
                                client_ip="x", user_agent="x")
    assert res["purged_count"] >= 1
    rows = audit.read_entries()
    assert all(r["slot_id"] != "OLD" for r in rows)
    assert len(rows) == 1


def test_validators_summary_strips_extras(isolate_audit_log):
    from engines.v8_institutional.especes import gis_audit_log_omega as audit
    res = audit.append_event(event="UPLOAD_LOADED", slot_id="A", filename="x",
                              sha256=None, size_bytes=1, http_code=200,
                              client_ip="x", user_agent="x",
                              validators=[
                                  {"name": "check_format", "passed": True,
                                   "extension_detectee": "geojson",
                                   "reason": "OK"},
                              ])
    summary = res["appended"]["validators_summary"]
    assert summary == [{"name": "check_format", "passed": True}]


def test_read_returns_empty_when_no_log(tmp_path, monkeypatch):
    from engines.v8_institutional.especes import gis_audit_log_omega as audit
    monkeypatch.setattr(audit, "AUDIT_LOG_PATH", tmp_path / "missing.jsonl")
    assert audit.read_entries() == []
    assert audit.stats()["total_events"] == 0


# ═══════════════════════════════════════════════════════════════════
# Endpoint /audit-log (HTTP)
# ═══════════════════════════════════════════════════════════════════
@pytest.fixture
def http_client(isolate_audit_log, tmp_path, monkeypatch):
    monkeypatch.setenv("GIS_RECEPTION_COMMANDANT_TOKEN",
                        "TEST_TOKEN_AUDIT_LOG_OMEGA")
    # ─── ORDRE N°52-EXT · Isolation complète du router (manifest, incoming,
    # quarantine, archive) pour éviter de polluer la PROD au pytest ───
    from routes import gis_reception_router_omega as router_mod
    isolated_root = tmp_path / "gis_operational"
    isolated_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(router_mod, "RECEPTION_ROOT", isolated_root)
    monkeypatch.setattr(router_mod, "INCOMING_DIR", isolated_root / "incoming")
    monkeypatch.setattr(router_mod, "QUARANTINE_DIR",
                         isolated_root / "quarantine")
    monkeypatch.setattr(router_mod, "MANIFEST_PATH",
                         isolated_root / "GIS_RECEPTION_INTAKE_Ω.json")
    monkeypatch.setattr(router_mod, "HARDENED_FLAG_PATH",
                         isolated_root / "hardened_mode_omega.json")
    monkeypatch.setattr(router_mod, "DIAG_MARKER_PATH",
                         isolated_root / "diagnostic_marker_omega.json")
    monkeypatch.setattr(router_mod, "ARCHIVE_ROOT",
                         tmp_path / "gis_archive")
    (isolated_root / "incoming").mkdir(parents=True, exist_ok=True)
    (isolated_root / "quarantine").mkdir(parents=True, exist_ok=True)
    (tmp_path / "gis_archive").mkdir(parents=True, exist_ok=True)
    app = FastAPI()
    app.include_router(router_mod.router)
    return TestClient(app)


def test_audit_log_endpoint_no_token_returns_401(http_client):
    r = http_client.get("/api/v30/admin-premium/gis/audit-log")
    assert r.status_code == 401


def test_audit_log_endpoint_invalid_token_returns_401(http_client):
    r = http_client.get(
        "/api/v30/admin-premium/gis/audit-log",
        headers={"X-Commandant-Token": "WRONG"},
    )
    assert r.status_code == 401


def test_audit_log_endpoint_returns_empty_initially(http_client):
    r = http_client.get(
        "/api/v30/admin-premium/gis/audit-log",
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["manifest_id"] == "AUDIT_LOG_GIS_Ω"
    assert data["stats"]["total_events"] == 0
    assert data["entries"] == []


def test_audit_log_endpoint_records_upload_events(http_client):
    # Upload valide (taille suffisante)
    payload = b"{\"type\":\"FeatureCollection\",\"features\":[" + b"," .join(
        [b"{\"type\":\"Feature\",\"geometry\":null,\"properties\":{}}"
         for _ in range(40)]
    ) + b"]}"
    r = http_client.post(
        "/api/v30/admin-premium/gis/upload/CHASSE_ZEC_SEPAQ_Ω",
        files={"file": ("good.geojson", payload, "application/geo+json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    assert r.status_code == 200

    # Upload trop petit → quarantine
    r2 = http_client.post(
        "/api/v30/admin-premium/gis/upload/CHASSE_ZEC_SEPAQ_Ω",
        files={"file": ("tiny.geojson", b"{}", "application/geo+json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    assert r2.status_code == 422

    # Slot inconnu → 404
    r3 = http_client.post(
        "/api/v30/admin-premium/gis/upload/SLOT_X",
        files={"file": ("x.geojson", payload, "application/geo+json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    assert r3.status_code == 404

    # Audit log doit refléter les 3 événements d'upload, +1 si archive
    # persistante activée (ORDRE N°52-EXT · PHYS_ARCHIVE_PERSISTED_Ω).
    r4 = http_client.get(
        "/api/v30/admin-premium/gis/audit-log",
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    data = r4.json()
    types = data["stats"]["events_by_type"]
    assert types["UPLOAD_LOADED"] == 1
    assert types["UPLOAD_QUARANTINED"] == 1
    assert types["UPLOAD_ERROR"] == 1
    # total = 3 events d'upload + éventuel event d'archive persistante sur CHASSE_ZEC_SEPAQ_Ω
    # (ORDRE N°52-EXT · slot dans ARCHIVABLE_SLOTS)
    expected_min = 3
    assert data["stats"]["total_events"] >= expected_min


def test_audit_log_filter_by_slot(http_client):
    payload = b"{\"type\":\"FeatureCollection\",\"features\":[" + b"," .join(
        [b"{\"type\":\"Feature\",\"geometry\":null,\"properties\":{}}"
         for _ in range(40)]
    ) + b"]}"
    http_client.post(
        "/api/v30/admin-premium/gis/upload/CHASSE_ZEC_SEPAQ_Ω",
        files={"file": ("a.geojson", payload, "application/geo+json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    http_client.post(
        "/api/v30/admin-premium/gis/upload/SLOT_X",
        files={"file": ("a.geojson", payload, "application/geo+json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    r = http_client.get(
        "/api/v30/admin-premium/gis/audit-log",
        params={"slot_id": "CHASSE_ZEC_SEPAQ_Ω"},
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    data = r.json()
    assert all(e["slot_id"] == "CHASSE_ZEC_SEPAQ_Ω" for e in data["entries"])


def test_audit_log_limit_param(http_client):
    r = http_client.get(
        "/api/v30/admin-premium/gis/audit-log",
        params={"limit": 0},
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    # limit=0 violates ge=1 → 422 validation error
    assert r.status_code == 422


# ═══════════════════════════════════════════════════════════════════
# Endpoint /promote
# ═══════════════════════════════════════════════════════════════════
def test_promote_no_token_returns_401(http_client):
    r = http_client.post("/api/v30/admin-premium/gis/promote")
    assert r.status_code == 401


def test_promote_returns_stub_ready_when_no_layers(http_client):
    r = http_client.post(
        "/api/v30/admin-premium/gis/promote",
        headers={"X-Commandant-Token": "TEST_TOKEN_AUDIT_LOG_OMEGA"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["manifest_id"] == "PROMOTE_GIS_OPERATIONAL_Ω"
    assert data["sceau_x5_final_ready"] is False
    assert data["next_action"] == "EN_ATTENTE_DE_COUCHES_RÉELLES_LOADED"
    assert data["compute_corridors_gis"]["status"] in (
        "STUB_READY", "PARTIAL", "OPERATIONAL"
    )


# ═══════════════════════════════════════════════════════════════════
# Garde-fous
# ═══════════════════════════════════════════════════════════════════
def test_no_synthetic_data_in_audit_module():
    import inspect
    from engines.v8_institutional.especes import gis_audit_log_omega as mod
    src = inspect.getsource(mod)
    forbidden = ["random.", "fake_", "synthetic_", "_dummy_"]
    for kw in forbidden:
        assert kw not in src, f"Mot-clé interdit '{kw}'"
