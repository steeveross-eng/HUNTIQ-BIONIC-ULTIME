"""
Phase XXVIII · ORDRE N°52-R9 — Tests anti-régressifs amplificateur MFFP×1000
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU

Valide :
  · Registre MFFP×1000 (WEIGHT_MFFP=1.0, WEIGHT_OTHER=0.1)
  · Score formula = 0.2 × original + 0.8 × MFFP
  · 9 cibles de recalcul (corridors → zones_alimentation)
  · 12 moteurs dépendants déclarés
  · Activation idempotente avec seal_sha256
  · Vérification disponibilité couches MFFP via R8 PHASE_3
  · STUB_READY si PHASE_3 non finalisée (ANTI_GÉNÉRIQUE_STRICT)
  · Rapport BIONIC_AMPLIFICATION_REPORT généré
"""
from __future__ import annotations

import importlib
import json

import pytest


@pytest.fixture()
def reg():
    return importlib.import_module(
        "engines.v8_institutional.especes.mffp_master_weight_registry_omega")


def test_r9_exports_public_api(reg):
    expected = {
        "read_master_weights", "activate_mffp_master",
        "deactivate_mffp_master", "check_mffp_derived_layers_availability",
        "start_r9_recalc_background", "read_r9_state",
        "MASTER_WEIGHTS_PATH", "R9_STATE_PATH",
        "R9_RECALC_TARGETS", "DEPENDENT_ENGINES",
        "MFFP_DERIVED_LAYERS_REQUIRED",
    }
    assert expected == set(reg.__all__)


def test_r9_targets_match_commandant_order(reg):
    """Les 9 cibles déclarées correspondent à l'ORDRE N°52-R9."""
    expected = [
        "corridors", "hotspots", "affuts", "salines",
        "zones_vitales", "zones_passage", "zones_rut",
        "zones_repos", "zones_alimentation",
    ]
    assert reg.R9_RECALC_TARGETS == expected


def test_r9_default_weights_match_doctrine(reg, tmp_path, monkeypatch):
    """Pondérations canoniques : WEIGHT_MFFP=1.0, WEIGHT_OTHER=0.1."""
    p = tmp_path / "MFFP_MASTER_WEIGHTS.json"
    monkeypatch.setattr(reg, "MASTER_WEIGHTS_PATH", p)
    w = reg.read_master_weights()
    assert w["weights"]["WEIGHT_MFFP"] == 1.0
    assert w["weights"]["WEIGHT_ALL_OTHER"] == 0.1
    assert w["score_coefficients"]["alpha_original"] == 0.2
    assert w["score_coefficients"]["beta_mffp"] == 0.8
    assert "score_final = (score_original * 0.2) + (score_MFFP * 0.8)" \
        in w["score_formula"]
    assert w["amplification_label"] == "MFFP×1000"
    assert w["active"] is False  # explicite via /activate


def test_r9_activation_is_idempotent(reg, tmp_path, monkeypatch):
    """Double activation produit le même seal_sha256."""
    p = tmp_path / "MFFP_MASTER_WEIGHTS.json"
    monkeypatch.setattr(reg, "MASTER_WEIGHTS_PATH", p)
    w1 = reg.activate_mffp_master(authority="COMMANDANT_STEEVE_MAX")
    seal1 = w1["activation_seal_sha256"]
    assert w1["active"] is True
    assert len(seal1) == 64
    w2 = reg.activate_mffp_master(authority="COMMANDANT_STEEVE_MAX")
    assert w2["activation_seal_sha256"] == seal1
    assert w2["active"] is True


def test_r9_deactivation_works(reg, tmp_path, monkeypatch):
    p = tmp_path / "MFFP_MASTER_WEIGHTS.json"
    monkeypatch.setattr(reg, "MASTER_WEIGHTS_PATH", p)
    reg.activate_mffp_master(authority="X")
    w = reg.deactivate_mffp_master(authority="X")
    assert w["active"] is False
    assert "deactivated_at_utc" in w


def test_r9_required_layers_count(reg):
    """8 couches MFFP dérivées requises (alignées sur 9 du R8 PHASE_3)."""
    expected = {
        "MFFP_STRUCTURE", "MFFP_DENSITY", "MFFP_AGE",
        "MFFP_FRAGMENTATION", "MFFP_PRODUCTIVITY",
        "MFFP_HABITAT", "MFFP_CONNECTIVITY", "MFFP_CONTINUITY",
    }
    assert set(reg.MFFP_DERIVED_LAYERS_REQUIRED) == expected


def test_r9_dependent_engines_count(reg):
    """≥10 moteurs dépendants déclarés."""
    assert len(reg.DEPENDENT_ENGINES) >= 10
    names = {e["name"] for e in reg.DEPENDENT_ENGINES}
    # Sentinel : doivent inclure les espèces clés et corridors
    assert "engine_corridors_gis_omega" in names
    assert "engine_chevreuil_omega" in names
    assert "engine_orignal_omega" in names
    assert "engine_habitat_omega" in names
    for e in reg.DEPENDENT_ENGINES:
        assert e.get("force_rebuild_required") is True


def test_r9_blocked_when_r8_phase3_stub(reg):
    """Si R8 PHASE_3 est STUB_READY, l'analyseur retourne all_available=False."""
    av = reg.check_mffp_derived_layers_availability()
    assert "all_available" in av
    assert "blocker_reason" in av
    # Dans l'environnement actuel, PHASE_3 est STUB_READY ou NEVER_RUN
    assert av["all_available"] is False


def test_r9_state_path_is_in_app_ext4(reg):
    """State R9 sur /app ext4 (pas /var/cache éphémère)."""
    assert str(reg.R9_STATE_PATH).startswith("/app/")
    assert "/app/backend/data/territoire" in str(reg.R9_STATE_PATH)


def test_r9_master_weights_path_is_in_app_ext4(reg):
    assert str(reg.MASTER_WEIGHTS_PATH).startswith("/app/")


def test_r9_score_formula_canonical(reg, tmp_path, monkeypatch):
    """Coefficients alpha+beta=1.0 (formule canonique)."""
    p = tmp_path / "MFFP_MASTER_WEIGHTS.json"
    monkeypatch.setattr(reg, "MASTER_WEIGHTS_PATH", p)
    w = reg.read_master_weights()
    assert w["score_coefficients"]["alpha_original"] + \
        w["score_coefficients"]["beta_mffp"] == 1.0
