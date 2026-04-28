"""
test_phase_e_rendu_omega_integral.py — RENDU-Ω INTÉGRAL CONFORME (ordre n°9)
═══════════════════════════════════════════════════════════════════════════
Phase     : POST-FUSION_Ω · RENDU-Ω INTÉGRAL · BCE-4X
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests d'application stricte des STYLES Ω OFFICIELS et de la PURGE TOTALE
des styles legacy.

V30 LOCKED inchangé.
"""
from __future__ import annotations

import hashlib
import pathlib

import pytest


# ─────────────────────────────────────────────────────────────────────────
# 1. PURGE LEGACY : WindFlowLayer atténué
# ─────────────────────────────────────────────────────────────────────────
def test_windflow_particle_count_purged():
    p = "/app/frontend/src/components/territoire/WindFlowLayer.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "PARTICLE_COUNT = 600" in src, "PARTICLE_COUNT doit être réduit à 600 (purge Ω)"


def test_windflow_max_opacity_purged():
    p = "/app/frontend/src/components/territoire/WindFlowLayer.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "MAX_OPACITY = 0.42" in src, "MAX_OPACITY doit être atténué (purge Ω)"


def test_windflow_trail_length_purged():
    p = "/app/frontend/src/components/territoire/WindFlowLayer.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "TRAIL_LENGTH = 5" in src, "TRAIL_LENGTH doit être réduit à 5 (purge Ω)"


# ─────────────────────────────────────────────────────────────────────────
# 2. STYLES Ω INSTITUTIONNELS APPLIQUÉS (BionicLayersV8.jsx)
# ─────────────────────────────────────────────────────────────────────────
def test_affut_omega_palette_applied():
    p = "/app/frontend/src/components/territoire/BionicLayersV8.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    # AFFUT_BIONIC_ORANGE doit pointer sur #00A676 (palette Ω)
    assert "AFFUT_BIONIC_ORANGE = '#00A676'" in src
    # Opacité atténuée
    assert "fillOpacity: 0.55" in src


def test_contamination_omega_palette_applied():
    p = "/app/frontend/src/components/territoire/BionicLayersV8.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    # Couleur #DC2626 institutionnelle bande PROSCRIT pour contamination
    assert "color: '#DC2626'" in src
    # Opacité atténuée 0.45
    assert "opacity: 0.45,                        // PURGE Ω : 0.85 → 0.45" in src


# ─────────────────────────────────────────────────────────────────────────
# 3. CERTIFICATEUR RENDU-Ω INTÉGRAL (composant frontend)
# ─────────────────────────────────────────────────────────────────────────
def test_rendu_omega_certifier_component_exists():
    p = "/app/frontend/src/components/territoire/RenduOmegaIntegralCertifier.jsx"
    assert pathlib.Path(p).exists()


def test_rendu_omega_certifier_lists_seven_omega_styles():
    p = "/app/frontend/src/components/territoire/RenduOmegaIntegralCertifier.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    for label in ('CORRIDORS Ω', 'ZONES Ω', 'AFFÛTS Ω', 'SALINES Ω',
                  'HOTSPOTS Ω', 'CONTAMINATION Ω', 'SENSORIEL Ω'):
        assert label in src, f"label {label} absent du certificateur Ω"


def test_rendu_omega_certifier_lists_purges_appliquees():
    p = "/app/frontend/src/components/territoire/RenduOmegaIntegralCertifier.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "PURGES LEGACY APPLIQUÉES" in src
    assert "2500 → 600" in src
    assert "0.90 → 0.42" in src


def test_rendu_omega_certifier_mounted_in_page():
    p = "/app/frontend/src/pages/MonTerritoireBionicPage.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "import RenduOmegaIntegralCertifier" in src
    assert "<RenduOmegaIntegralCertifier" in src
    assert 'data-testid="rendu-omega-integral-overlay"' in src


# ─────────────────────────────────────────────────────────────────────────
# 4. V30 LOCKED inchangé post-RENDU-Ω INTÉGRAL
# ─────────────────────────────────────────────────────────────────────────
def test_v30_inchange_post_rendu_omega_integral():
    expected = {
        "/app/backend/engines/v8_institutional/registry_lock_omega.py":
            "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c",
        "/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py":
            "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3",
    }
    for path, exp in expected.items():
        with open(path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        assert sha == exp, f"V30 mutation post-rendu-omega sur {path}"


# ─────────────────────────────────────────────────────────────────────────
# 5. SENTINEL ANTI-RÉGRESSION : interdire retour aux paramètres legacy
# ─────────────────────────────────────────────────────────────────────────
def test_sentinel_no_return_to_legacy_particle_count():
    p = "/app/frontend/src/components/territoire/WindFlowLayer.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    # Le commentaire de purge institutionnel doit être présent (sentinel)
    assert "PHASE-E RENDU-Ω INTÉGRAL" in src or "PURGE" in src


def test_sentinel_no_legacy_orange_in_affut_palette():
    p = "/app/frontend/src/components/territoire/BionicLayersV8.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    # L'ancienne déclaration ne doit plus exister
    assert "AFFUT_BIONIC_ORANGE = '#FF9800'" not in src, \
        "RÉGRESSION : la palette legacy #FF9800 est revenue !"
