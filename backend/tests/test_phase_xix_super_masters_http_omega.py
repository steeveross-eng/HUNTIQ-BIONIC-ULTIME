"""
test_phase_xix_super_masters_http_omega.py — PHASE XIX
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°39

Tests : routes HTTP /api/v30/super-masters/* + intégrité du sceau institutionnel.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from routes.phase_xix_router_omega import router, MASTER_ID_MAP

# Création d'une app FastAPI minimale pour tester le router de manière isolée
from fastapi import FastAPI

_app = FastAPI()
_app.include_router(router)
_client = TestClient(_app)


SIX_MASTERS_PATH = Path("/app/frontend/public/reports/purge_master_omega/SIX_MASTERS_Ω_OPTIMISÉS.json")
SCEAU_PATH = Path("/app/backend/institution/sceaux/SCEAU_INSTITUTIONNEL_X4_FINAL_Ω.sha256")


# ─── ROUTES /list et /sceau/status ────────────────────────────────────

def test_xix_route_list_returns_200():
    r = _client.get("/api/v30/super-masters/list")
    assert r.status_code == 200
    j = r.json()
    assert j["doctrine"] == "BCE-4X_ULTIME_ABSOLU_x3"
    assert j["ordre"] == "n°39"
    assert set(j["masters_disponibles"]) == set(MASTER_ID_MAP.keys())


def test_xix_route_sceau_status_returns_200():
    r = _client.get("/api/v30/super-masters/sceau/status")
    assert r.status_code == 200
    j = r.json()
    assert "sceau" in j
    assert "territoire_master_x4_score" in j
    assert j["decision"] in ("APTE", "MARGINAL")


# ─── 6 ROUTES master_id/optimised ─────────────────────────────────────

@pytest.mark.parametrize("alias_master", [
    ("nutri", "nutrition"),
    ("corr_m", "corridors"),
    ("senso", "sensoriel"),
    ("compo", "comportement"),
    ("gouv", "gouvernance"),
    ("terr_m", "territoire"),
])
def test_xix_route_each_master_optimised(alias_master):
    _, master_id = alias_master
    r = _client.get(f"/api/v30/super-masters/{master_id}/optimised")
    assert r.status_code == 200, f"FAIL {master_id} : {r.text}"
    j = r.json()
    assert j["master_id"] == master_id
    assert "score_optimise" in j
    assert "score_baseline" in j
    assert 0.0 <= j["score_optimise"] <= 100.0
    # Le mode ADD-ONLY garantit score_optimise >= score_baseline
    assert j["score_optimise"] >= j["score_baseline"]
    assert "score_par_espece" in j


def test_xix_route_invalid_master_returns_404():
    r = _client.get("/api/v30/super-masters/INVALID/optimised")
    assert r.status_code == 404


# ─── INTÉGRITÉ SCEAU ──────────────────────────────────────────────────

def test_xix_sceau_file_exists():
    assert SCEAU_PATH.exists(), f"SCEAU_INSTITUTIONNEL_X4_FINAL_Ω.sha256 manquant : {SCEAU_PATH}"


def test_xix_sceau_is_valid_sha256():
    txt = SCEAU_PATH.read_text(encoding="utf-8").strip()
    # Doit contenir un SHA-256 hexadécimal (64 chars)
    assert len(txt) >= 64
    sha_only = txt[:64]
    int(sha_only, 16)  # raise ValueError si non hex


def test_xix_sceau_referenced_in_routes():
    """Le sceau doit apparaître dans /list et /sceau/status."""
    r1 = _client.get("/api/v30/super-masters/list")
    r2 = _client.get("/api/v30/super-masters/sceau/status")
    j1 = r1.json()
    j2 = r2.json()
    assert "sceau" in j1
    assert "sceau" in j2


# ─── RÈGLE ADD-ONLY ───────────────────────────────────────────────────

def test_xix_rule_addonly_max_preserve():
    """Pour les 6 masters, le score optimisé est >= baseline (règle ADD-ONLY)."""
    with open(SIX_MASTERS_PATH, encoding="utf-8") as f:
        d = json.load(f)
    for canonical, payload in d["masters_optimises"].items():
        assert payload["score_optimise_max"] >= payload["score_baseline_n36"], \
            f"{canonical} viole ADD-ONLY"


def test_xix_six_masters_all_at_100():
    """Confirmation : les 6 masters atteignent 100/100 après n°38."""
    with open(SIX_MASTERS_PATH, encoding="utf-8") as f:
        d = json.load(f)
    for canonical, payload in d["masters_optimises"].items():
        assert payload["score_optimise_max"] == 100.0


# ─── COHÉRENCE TERRITOIRE_MASTER_X4 ───────────────────────────────────

def test_xix_x4_above_apte_threshold_70():
    fp = Path("/app/frontend/public/reports/purge_master_omega/TERRITOIRE_MASTER_Ω_FUSION_X4.json")
    with open(fp, encoding="utf-8") as f:
        d = json.load(f)
    assert d["territoire_master_x4_score"] >= 70.0
    assert d["decision_globale"] == "APTE"
