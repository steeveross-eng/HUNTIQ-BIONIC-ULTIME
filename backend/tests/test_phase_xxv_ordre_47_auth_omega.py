"""
test_phase_xxv_ordre_47_auth_omega.py — Tests Phase XXV (ORDRE N°47)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°47

Tests anti-régression de :
  · Authentification admin@huntiq.com / Saturn5858* sur /api/auth/login
  · Existence du fichier DASHBOARD_PILOTAGE_BCE_4X_Ω.json
  · Validité JSON du DASHBOARD (anti-bug "Unexpected token <")
  · Manifeste GIS (slot FORET_MFFP_Ω en ABSENT après purge)

Anti-générique strict — V30 INVIOLABLE.
═════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL_ENV = os.environ.get(
    "BACKEND_URL_TEST",
    "http://localhost:8001"
)


# ═══════════════════════════════════════════════════════════════════
# Auth Saturn5858* — ORDRE N°47 P0
# ═══════════════════════════════════════════════════════════════════
def test_auth_admin_huntiq_saturn5858_returns_jwt():
    """L'endpoint /api/auth/login DOIT accepter admin@huntiq.com / Saturn5858*."""
    r = requests.post(
        f"{BASE_URL_ENV}/api/auth/login",
        json={"email": "admin@huntiq.com", "password": "Saturn5858*"},
        timeout=10,
    )
    assert r.status_code == 200, f"Auth failed: {r.text}"
    body = r.json()
    assert body.get("success") is True
    assert "token" in body and len(body["token"]) > 50
    assert body["user"]["email"] == "admin@huntiq.com"


def test_auth_wrong_password_rejected():
    """Mot de passe incorrect → 401 ou 403 ou 400 (refus explicite)."""
    r = requests.post(
        f"{BASE_URL_ENV}/api/auth/login",
        json={"email": "admin@huntiq.com", "password": "WRONG_PASSWORD"},
        timeout=10,
    )
    assert r.status_code in (400, 401, 403), (
        f"Wrong-password should be refused, got {r.status_code}: {r.text}"
    )


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD JSON — anti-bug "Unexpected token <"
# ═══════════════════════════════════════════════════════════════════
DASHBOARD_PATH = Path(
    "/app/frontend/public/reports/purge_master_omega/DASHBOARD_PILOTAGE_BCE_4X_Ω.json"
)


def test_dashboard_json_file_exists():
    assert DASHBOARD_PATH.exists(), (
        f"Le fichier DASHBOARD_PILOTAGE_BCE_4X_Ω.json est absent : {DASHBOARD_PATH}"
    )
    assert DASHBOARD_PATH.stat().st_size > 1000


def test_dashboard_json_valid_structure():
    """Le DASHBOARD JSON DOIT être parseable sans 'Unexpected token <'."""
    raw = DASHBOARD_PATH.read_text(encoding="utf-8")
    assert not raw.lstrip().startswith("<"), (
        "Le DASHBOARD ne doit JAMAIS commencer par '<' (HTML SPA fallback)"
    )
    data = json.loads(raw)
    assert data.get("manifest_id") == "DASHBOARD_PILOTAGE_BCE_4X_Ω"
    assert "ordres" in data and isinstance(data["ordres"], list)
    assert len(data["ordres"]) >= 5  # 5+ ordres documentés


# ═══════════════════════════════════════════════════════════════════
# Manifeste GIS post-purge ORDRE N°46 (slot FORET_MFFP_Ω en ABSENT)
# ═══════════════════════════════════════════════════════════════════
GIS_MANIFEST = Path(
    "/app/backend/data/gis_operational/GIS_RECEPTION_INTAKE_Ω.json"
)


def test_gis_manifest_exists():
    assert GIS_MANIFEST.exists()


def test_gis_foret_mffp_slot_coherent_state():
    """FORET_MFFP_Ω doit avoir un état cohérent (multi_upload=True, status
    cohérent avec files_loaded_count). Évolutif après uploads réels.
    """
    d = json.loads(GIS_MANIFEST.read_text(encoding="utf-8"))
    foret = d["slots"].get("FORET_MFFP_Ω")
    assert foret is not None
    assert foret.get("multi_upload") is True
    files_count = foret.get("files_loaded_count", 0)
    if files_count == 0:
        assert foret["status"] == "ABSENT"
        assert foret.get("composite_sha256") is None
    else:
        assert foret["status"] == "LOADED"
        assert foret.get("composite_sha256") is not None
        assert len(foret["composite_sha256"]) == 64
        assert len(foret.get("uploads", [])) >= files_count


# ═══════════════════════════════════════════════════════════════════
# Anti-régression — Routes API actives
# ═══════════════════════════════════════════════════════════════════
def test_gis_slots_endpoint_returns_six():
    r = requests.get(f"{BASE_URL_ENV}/api/v30/admin-premium/gis/slots", timeout=10)
    assert r.status_code == 200
    data = r.json()
    # ORDRE N°52-EXT VOIE A : 6 originaux + PEE_MAJ_Ω
    assert data["slots_count"] == 7
    foret = next(s for s in data["slots"] if s["slot_id"] == "FORET_MFFP_Ω")
    assert foret["multi_upload"] is True
    assert foret["voie_acquisition"] == "VOIE_B_TUILES_REGIONALES_MFFP"


def test_intake_status_returns_partial_or_empty():
    r = requests.get(
        f"{BASE_URL_ENV}/api/v30/admin-premium/gis/intake-status",
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["stats"]["total_slots"] == 7  # ORDRE N°52-EXT
    assert data["stats"]["global_status"] in ("PARTIAL_OR_EMPTY", "OPERATIONAL")


# ═══════════════════════════════════════════════════════════════════
# Anti-générique strict
# ═══════════════════════════════════════════════════════════════════
def test_no_synthetic_credentials_in_test_credentials_md():
    """Le fichier test_credentials.md ne doit pas contenir de mots-clés mock."""
    p = Path("/app/memory/test_credentials.md")
    if not p.exists():
        pytest.skip("test_credentials.md absent")
    content = p.read_text(encoding="utf-8").lower()
    forbidden = ["fakepassword", "synthetic_user", "mock_admin"]
    for kw in forbidden:
        assert kw not in content, f"Mot-clé '{kw}' interdit dans test_credentials"
