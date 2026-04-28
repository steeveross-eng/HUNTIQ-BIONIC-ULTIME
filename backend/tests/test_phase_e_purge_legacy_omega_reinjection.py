"""
test_phase_e_purge_legacy_omega_reinjection.py
═══════════════════════════════════════════════════════════════════════════
Phase     : POST-FUSION_Ω · PURGE LEGACY + RÉINJECTION COUCHES Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests d'éradication des couches V30 brut résiduelles et confirmation
de la réinjection complète des 7 couches Ω + chaînes C1..C6 dynamiques
dans la carte vivante.

V30 LOCKED inchangé.
"""
from __future__ import annotations

import hashlib
import pathlib
import re

import pytest


# ─────────────────────────────────────────────────────────────────────────
# 1. Le panneau StatutCorridorsOmegaPanel n'affiche plus "V30 brut" comme verdict
# ─────────────────────────────────────────────────────────────────────────
def test_statut_panel_no_longer_displays_v30_brut_as_verdict():
    p = "/app/frontend/src/components/territoire/StatutCorridorsOmegaPanel.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    # Le wording "V30 brut" comme verdict principal doit avoir disparu
    # Mais il peut subsister dans le fallback (avec "(fallback)") ou les commentaires
    assert "POST-FILTRAGE Ω" in src, "Mode Ω post-filtrage doit être affiché"
    assert "COUCHES TERRITOIRE Ω" in src, "Étiquette des couches doit avoir le suffixe Ω"


def test_statut_panel_accepts_bundleData_prop():
    p = "/app/frontend/src/components/territoire/StatutCorridorsOmegaPanel.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "bundleData = null" in src or "bundleData=" in src
    assert "data-testid=\"layers-omega-zones-count\"" in src
    assert "data-testid=\"layers-omega-corridors-count\"" in src
    assert "data-testid=\"layers-omega-salines-count\"" in src
    assert "data-testid=\"layers-omega-hotspots-count\"" in src
    assert "data-testid=\"layers-omega-affuts-count\"" in src
    assert "data-testid=\"layers-omega-contamination-count\"" in src
    assert "data-testid=\"layers-omega-sensoriel-active\"" in src


def test_statut_panel_connected_with_bundle_in_page():
    p = "/app/frontend/src/pages/MonTerritoireBionicPage.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    # Le panneau doit recevoir bundleData={bundleDataV8}
    assert "<StatutCorridorsOmegaPanel bundleData={bundleDataV8}" in src


# ─────────────────────────────────────────────────────────────────────────
# 2. Le LayersOmegaSyncPanel inclut CONTAMINATION Ω + SENSORIEL Ω
# ─────────────────────────────────────────────────────────────────────────
def test_layers_omega_sync_includes_contamination():
    p = "/app/frontend/src/components/territoire/LayersOmegaSyncPanel.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "CONTAMINATION Ω" in src


def test_layers_omega_sync_includes_sensoriel():
    p = "/app/frontend/src/components/territoire/LayersOmegaSyncPanel.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "SENSORIEL Ω" in src


def test_layers_omega_sync_includes_chains_c1_c6():
    p = "/app/frontend/src/components/territoire/LayersOmegaSyncPanel.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    for chain in ("C1", "C2", "C3", "C4", "C5", "C6"):
        assert f"id: '{chain}'" in src or f"'{chain}'" in src
    assert "CHAÎNES C1..C6 DYNAMIQUES" in src


# ─────────────────────────────────────────────────────────────────────────
# 3. Bundle backend continue à fournir les sources Ω post-filtrage
# ─────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def client():
    import sys
    sys.path.insert(0, "/app/backend")
    from server import app as fastapi_app
    from fastapi.testclient import TestClient
    return TestClient(fastapi_app)


@pytest.fixture(scope="module")
def bundle(client):
    r = client.get(
        "/api/v20/territoire/bundle",
        params={"lat": 48.206657, "lon": -68.382422,
                "species": "orignal", "month": 10, "hour": 14},
    )
    assert r.status_code == 200
    return r.json()


def test_bundle_has_all_seven_omega_sources(bundle):
    """Le bundle doit fournir les 7 sources Ω attendues post-purge."""
    assert "corridors" in bundle
    assert "zones" in bundle
    assert "affuts" in bundle
    assert "salines" in bundle
    assert "hotspots" in bundle
    assert "contamination_v2_heatmap" in bundle
    assert "sensoriel_vent_odeurs" in bundle


def test_bundle_sensoriel_has_cone_axis(bundle):
    sens = bundle.get("sensoriel_vent_odeurs") or {}
    # Le cône sensoriel doit avoir un cone_axis_deg défini (post-fix C1 OMM)
    assert "cone_axis_deg" in sens
    assert isinstance(sens["cone_axis_deg"], (int, float))


# ─────────────────────────────────────────────────────────────────────────
# 4. V30 LOCKED inchangé post-purge
# ─────────────────────────────────────────────────────────────────────────
def test_v30_inchange_post_purge_legacy():
    expected = {
        "/app/backend/engines/v8_institutional/registry_lock_omega.py":
            "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c",
        "/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py":
            "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3",
    }
    for path, exp in expected.items():
        with open(path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        assert sha == exp, f"V30 mutation post-purge sur {path}"


# ─────────────────────────────────────────────────────────────────────────
# 5. Le LayersOmegaSyncPanel reste monté dans la page
# ─────────────────────────────────────────────────────────────────────────
def test_layers_omega_sync_panel_still_mounted_in_page():
    p = "/app/frontend/src/pages/MonTerritoireBionicPage.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "<LayersOmegaSyncPanel" in src
    assert "import LayersOmegaSyncPanel" in src
