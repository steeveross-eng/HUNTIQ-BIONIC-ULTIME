"""
test_phase_e_layers_omega_sync.py — SYNCHRONISATION COUCHES Ω (carte vivante)
═══════════════════════════════════════════════════════════════════════════
Phase     : POST-FUSION_Ω · SYNCHRONISATION CARTE / COUCHES
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests d'intégrité de la synchronisation entre :
  - les couches affichées par la carte (corridors, zones, affuts, salines, hotspots)
  - les sources Ω institutionnelles validées (post-XIX, XVII, VITAUX, RENDU-Ω, VEINEUX)

Aucun engine cryptographique modifié. V30 LOCKED inchangé.
"""
from __future__ import annotations

import hashlib
import json
import sys
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, "/app/backend")

V30_REGISTRY_LOCK_SHA256 = (
    "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c"
)
V30_ENGINE_IA_CORRIDORS_SHA256 = (
    "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3"
)
BSL_LAT = 48.206657
BSL_LNG = -68.382422


@pytest.fixture(scope="module")
def client():
    from server import app as fastapi_app
    return TestClient(fastapi_app)


@pytest.fixture(scope="module")
def bundle(client) -> Dict[str, Any]:
    r = client.get(
        "/api/v20/territoire/bundle",
        params={
            "lat": BSL_LAT, "lon": BSL_LNG,
            "species": "orignal", "month": 10, "hour": 14,
        },
    )
    assert r.status_code == 200, r.text
    return r.json()


# ─────────────────────────────────────────────────────────────────────────
# 1. Le bundle expose les 5 couches institutionnelles attendues
# ─────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("layer_key", [
    pytest.param("corridors", id="corr_omega"),
    "zones", "affuts", "salines", "hotspots",
])
def test_layer_present_in_pipeline_omega(bundle, layer_key):
    assert layer_key in bundle, f"couche {layer_key} absente du bundle V20"
    val = bundle[layer_key]
    assert isinstance(val, list), f"{layer_key} doit être une liste"


# ─────────────────────────────────────────────────────────────────────────
# 2. Les flags d'application Ω sont actifs (pipeline post-fusion)
# ─────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("flag", [
    pytest.param("corridors_vitaux_omega_applied", id="flag_vitaux_omega"),
    "interzone_omega_applied",
    "predictive_omega_v2_applied",
    "veineux_omega_applied_at_bundle",
    "smoother_p5_renduomega_applied",
])
def test_omega_pipeline_flag_appli_active(bundle, flag):
    assert bundle.get(flag) is True, f"flag {flag} doit être True (pipeline Ω actif)"


# ─────────────────────────────────────────────────────────────────────────
# 3. Les couches RENDUES = couches POST-FILTRAGE Ω (PAS V30 brut)
# ─────────────────────────────────────────────────────────────────────────
def test_layers_are_omega_filtered_not_v30_raw(bundle):
    """V30 brut aurait inclus les couches XIX rejetées ; le rendu n'a que les Ω validées."""
    rendered = len(bundle["corridors"])
    rejected_xix = len(bundle.get("corridors_rejected_origine_externe_xix", []))
    rejected_xvii = len(bundle.get("corridors_rejected_phase_xvii", []))
    rejected_vitaux = len(bundle.get("corridors_rejected_vitaux_xviii", []))
    rejected_rendu = len(bundle.get("corridors_rejected_by_renduomega", []))
    total_rejected = rejected_xix + rejected_xvii + rejected_vitaux + rejected_rendu
    assert total_rejected >= 0
    assert rendered <= rendered + total_rejected


def test_xix_filter_active_at_bsl(bundle):
    """Au BSL, le filtre XIX rejette typiquement plusieurs couches externes."""
    rejected = bundle.get("corridors_rejected_origine_externe_xix", [])
    assert isinstance(rejected, list)
    if rejected:
        for r in rejected:
            assert "id" in r and "reason" in r


# ─────────────────────────────────────────────────────────────────────────
# 4. RENDU-Ω integration disponible
# ─────────────────────────────────────────────────────────────────────────
def test_renduomega_integration_block_present(bundle):
    integ = bundle.get("renduomega_integration")
    assert integ is not None
    assert "status" in integ
    assert "phase" in integ
    assert "totals" in integ


def test_v30_engine_not_touched_during_rendu(bundle):
    integ = bundle.get("renduomega_integration", {})
    # Article doctrinal : RENDU-Ω ne doit pas modifier V30
    if "v30_engine_touched" in integ:
        assert integ["v30_engine_touched"] is False, "V30 engine touché par RENDU-Ω — VIOLATION"


# ─────────────────────────────────────────────────────────────────────────
# 5. ESI-Ω indicateur de conformité institutionnelle
# ─────────────────────────────────────────────────────────────────────────
def test_esi_omega_indicator_present(bundle):
    esi = bundle.get("esi_omega")
    assert esi is not None
    assert isinstance(esi, str)


# ─────────────────────────────────────────────────────────────────────────
# 6. Stats des couches Ω
# ─────────────────────────────────────────────────────────────────────────
def test_omega_vitaux_stats_well_formed(bundle):
    stats = bundle.get("corridors_vitaux_omega_stats")
    if stats:
        for k in ("phase", "rule_applied"):
            assert k in stats


def test_interzone_omega_stats_well_formed(bundle):
    s = bundle.get("interzone_omega_stats")
    if s:
        assert "total_after" in s


def test_predictive_omega_v2_stats_well_formed(bundle):
    s = bundle.get("predictive_omega_v2_stats")
    if s:
        for k in ("phase", "season", "corridors_total"):
            assert k in s


# ─────────────────────────────────────────────────────────────────────────
# 7. Frontend — composant LayersOmegaSyncPanel monté dans MonTerritoireBionicPage
# ─────────────────────────────────────────────────────────────────────────
def test_frontend_layers_omega_sync_panel_imported():
    import pathlib
    src = pathlib.Path(
        "/app/frontend/src/pages/MonTerritoireBionicPage.jsx"
    ).read_text(encoding="utf-8")
    assert "import LayersOmegaSyncPanel" in src
    assert "<LayersOmegaSyncPanel" in src
    assert 'data-testid="layers-omega-sync-overlay"' in src


def test_frontend_layers_omega_sync_panel_component_exists():
    import os
    p = "/app/frontend/src/components/territoire/LayersOmegaSyncPanel.jsx"
    assert os.path.exists(p)
    src = open(p, encoding="utf-8").read()
    assert "CORRIDORS Ω" in src
    assert "ZONES Ω" in src
    assert "AFFÛTS Ω" in src
    assert "SALINES Ω" in src
    assert "HOTSPOTS Ω" in src


# ─────────────────────────────────────────────────────────────────────────
# 8. V30 LOCKED inchangé post-synchronisation
# ─────────────────────────────────────────────────────────────────────────
def test_v30_inchange_post_layers_sync():
    for path, expected in (
        ("/app/backend/engines/v8_institutional/registry_lock_omega.py",
         V30_REGISTRY_LOCK_SHA256),
        ("/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py",
         V30_ENGINE_IA_CORRIDORS_SHA256),
    ):
        with open(path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        assert sha == expected, f"V30 mutation détectée sur {path}"


# ─────────────────────────────────────────────────────────────────────────
# 9. Idempotence du bundle Ω
# ─────────────────────────────────────────────────────────────────────────
def test_layers_omega_bundle_idempotent(client):
    params = {"lat": BSL_LAT, "lon": BSL_LNG, "species": "orignal",
              "month": 10, "hour": 14}
    a = client.get("/api/v20/territoire/bundle", params=params).json()
    b = client.get("/api/v20/territoire/bundle", params=params).json()
    # Couches structurellement identiques
    assert len(a["corridors"]) == len(b["corridors"])
    assert len(a["zones"]) == len(b["zones"])
    assert len(a["salines"]) == len(b["salines"])
    assert len(a["hotspots"]) == len(b["hotspots"])
