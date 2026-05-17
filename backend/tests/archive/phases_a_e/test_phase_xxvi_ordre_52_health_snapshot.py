"""
test_phase_xxvi_ordre_52_health_snapshot.py — Pytest Phase XXVI (ORDRE N°52, VOIE B)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°52 SUSPENSIF

Tests du nouvel endpoint :
  GET /api/v30/admin-premium/gis/health-snapshot

Pattern isolé (n'importe pas server.py pour éviter la pollution
load_dotenv() qui casse les tests xxiv via setdefault).

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

# Path setup
sys.path.insert(0, "/app/backend")

TEST_TOKEN_XXVI = "TEST_TOKEN_HEALTH_SNAPSHOT_OMEGA"


@pytest.fixture(scope="module")
def health_client(tmp_path_factory):
    """Client isolé : manifest + incoming + audit-log redirigés en tmp."""
    tmp_root = tmp_path_factory.mktemp("gis_health_xxvi")
    os.environ["GIS_RECEPTION_COMMANDANT_TOKEN"] = TEST_TOKEN_XXVI

    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    mod.RECEPTION_ROOT = Path(tmp_root) / "gis_operational"
    mod.INCOMING_DIR = mod.RECEPTION_ROOT / "incoming"
    mod.QUARANTINE_DIR = mod.RECEPTION_ROOT / "quarantine"
    mod.MANIFEST_PATH = mod.RECEPTION_ROOT / "GIS_RECEPTION_INTAKE_Ω.json"
    mod.INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    mod.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = mod.RECEPTION_ROOT / "audit_log.jsonl"
    audit_mod.AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    app = FastAPI()
    app.include_router(mod.router)
    yield TestClient(app)


HDR_OK = {"X-Commandant-Token": TEST_TOKEN_XXVI}
HDR_KO = {"X-Commandant-Token": "WRONG_TOKEN_INVALID"}
ENDPOINT = "/api/v30/admin-premium/gis/health-snapshot"


def test_health_snapshot_requires_token(health_client):
    r = health_client.get(ENDPOINT)
    assert r.status_code == 401, f"got {r.status_code}: {r.text[:200]}"


def test_health_snapshot_rejects_wrong_token(health_client):
    r = health_client.get(ENDPOINT, headers=HDR_KO)
    assert r.status_code == 401


def test_health_snapshot_returns_200_ok(health_client):
    r = health_client.get(ENDPOINT, headers=HDR_OK)
    assert r.status_code == 200, r.text[:300]
    d = r.json()
    assert d["manifest_id"] == "GIS_HEALTH_SNAPSHOT_Ω"
    assert d["doctrine"] == "BCE-4X_ULTIME_ABSOLU_x3"
    assert d["ordre"] == "n°52"
    assert d["anti_generique"] == "STRICT"


def test_health_snapshot_intake_summary_keys(health_client):
    r = health_client.get(ENDPOINT, headers=HDR_OK)
    d = r.json()
    s = d["intake_summary"]
    # ORDRE N°52-EXT VOIE A : 6 originaux + PEE_MAJ_Ω
    assert s["total_slots"] == 7
    for k in ("loaded", "absent", "quarantined"):
        assert k in s


def test_health_snapshot_slots_per_slot_keys(health_client):
    r = health_client.get(ENDPOINT, headers=HDR_OK)
    d = r.json()
    expected_slots = {
        "FORET_MFFP_Ω", "SOL_IRDA_Ω", "CHASSE_ZEC_SEPAQ_Ω",
        "ROUTES_MTQ_SECONDAIRES_Ω", "LIMITES_TERRITORIALES_FINES_Ω",
        "PRESSION_HUMAINE_Ω",
        "FORET_MFFP_PEE_MAJ_Ω",  # ORDRE N°52-EXT VOIE A
    }
    assert set(d["slots"].keys()) == expected_slots
    for slot_id, st in d["slots"].items():
        for k in (
            "manifest_status", "manifest_files_count", "manifest_cumulative_bytes",
            "manifest_composite_sha256",
            "physical_files_count", "physical_cumulative_bytes", "physical_files",
            "consistent_manifest_vs_physical",
        ):
            assert k in st, f"{slot_id} missing {k}"


def test_health_snapshot_engine_layers(health_client):
    r = health_client.get(ENDPOINT, headers=HDR_OK)
    d = r.json()
    eng = d["engine_layers"]
    assert eng["layers_total"] == 9
    assert eng["global_status"] in ("STUB_READY", "OPERATIONAL")
    assert "layers" in eng and len(eng["layers"]) == 9


def test_health_snapshot_v30_lock_inviolated(health_client):
    r = health_client.get(ENDPOINT, headers=HDR_OK)
    d = r.json()
    assert d["v30_lock"]["status"] == "INVIOLÉ"
    assert d["v30_lock"]["engines_locked_count"] >= 30


def test_health_snapshot_audit_log_keys(health_client):
    """Le bloc audit_log_stats doit exposer les clés institutionnelles."""
    r = health_client.get(ENDPOINT, headers=HDR_OK)
    d = r.json()
    s = d["audit_log_stats"]
    for k in ("total_events", "events_by_type", "events_by_slot",
              "retention_days", "log_path", "log_exists", "log_size_bytes"):
        assert k in s, f"audit_log_stats missing {k}"


def test_health_snapshot_no_side_effect(health_client):
    """Deux appels successifs ne doivent pas générer d'audit-event supplémentaire."""
    r1 = health_client.get(ENDPOINT, headers=HDR_OK)
    r2 = health_client.get(ENDPOINT, headers=HDR_OK)
    assert r1.status_code == r2.status_code == 200
    s1 = r1.json()["audit_log_stats"]["total_events"]
    s2 = r2.json()["audit_log_stats"]["total_events"]
    assert s1 == s2, f"divergence audit events {s1} vs {s2}"


def test_health_snapshot_divergences_field_present(health_client):
    r = health_client.get(ENDPOINT, headers=HDR_OK)
    d = r.json()
    assert "divergences_manifest_vs_physical" in d
    assert isinstance(d["divergences_count"], int)


def test_health_snapshot_flags(health_client):
    r = health_client.get(ENDPOINT, headers=HDR_OK)
    d = r.json()
    f = d["flags"]
    for k in ("prep_only_mode", "incoming_root", "quarantine_root", "manifest_path"):
        assert k in f
