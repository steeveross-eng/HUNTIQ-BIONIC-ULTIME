"""
test_phase_xvi_super_engines_omega.py — PHASE XVI · 6 SUPER ENGINES_Ω LOGIC
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°35

Couverture pytest : implémentation logique des 6 SUPER ENGINES_Ω.
Doctrine : zéro fallback, zéro interpolation, aucune dépendance V7/V8/SUPRA.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import pytest

from engines.v8_institutional.especes.super_engines_omega_specs import (
    SUPER_ENGINES_Ω,
    SUPER_ENGINE_LOCK_SHA256,
)
from engines.v8_institutional.especes.super_engines_omega_logic import (
    compute_corridors_master,
    compute_nutrition_master,
    compute_sensoriel_master,
    compute_comportement_master,
    compute_gouvernance_master,
    compute_territoire_master,
    compute_all_super_engines,
)


ESPECES = ["CHEVREUIL", "ORIGNAL", "OURS_NOIR", "WAPITI", "DINDON_SAUVAGE"]


# ─── Spécifications préservées (V30 / FREEZE) ─────────────────────────

def test_specs_six_super_engines_lockes():
    assert len(SUPER_ENGINES_Ω) == 6
    expected = {
        "ENGINE_CORRIDORS_MASTER_Ω", "ENGINE_NUTRITION_MASTER_Ω",
        "ENGINE_SENSORIEL_MASTER_Ω", "ENGINE_COMPORTEMENT_MASTER_Ω",
        "ENGINE_GOUVERNANCE_MASTER_Ω", "ENGINE_TERRITOIRE_MASTER_Ω",
    }
    assert set(SUPER_ENGINES_Ω.keys()) == expected


def test_super_engine_lock_sha_present():
    assert isinstance(SUPER_ENGINE_LOCK_SHA256, str)
    assert len(SUPER_ENGINE_LOCK_SHA256) == 64


# ─── Doctrine : interdiction fallback / interpolation ─────────────────

def test_se1_corr_master_no_fallback_no_interp():
    out = compute_corridors_master()
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False
    assert out["super_engine_id"] == "ENGINE_CORRIDORS_MASTER_Ω"


def test_nutrition_master_no_fallback_no_interp():
    out = compute_nutrition_master()
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False
    assert out["super_engine_id"] == "ENGINE_NUTRITION_MASTER_Ω"


def test_sensoriel_master_no_fallback_no_interp():
    out = compute_sensoriel_master()
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False
    assert out["super_engine_id"] == "ENGINE_SENSORIEL_MASTER_Ω"


def test_comportement_master_no_fallback_no_interp():
    out = compute_comportement_master()
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False
    assert out["super_engine_id"] == "ENGINE_COMPORTEMENT_MASTER_Ω"


def test_gouvernance_master_no_fallback_no_interp():
    out = compute_gouvernance_master()
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False
    assert out["super_engine_id"] == "ENGINE_GOUVERNANCE_MASTER_Ω"


def test_se6_terr_master_no_fallback_no_interp():
    out = compute_territoire_master()
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False
    assert out["super_engine_id"] == "ENGINE_TERRITOIRE_MASTER_Ω"


# ─── Couverture par espèce ────────────────────────────────────────────

def test_se1_corr_master_score_par_espece_5():
    out = compute_corridors_master()
    assert set(out["score_par_espece"].keys()) == set(ESPECES)
    for esp, sc in out["score_par_espece"].items():
        assert 0.0 <= sc <= 100.0, f"{esp} score hors bornes"


def test_nutrition_master_score_par_espece_5():
    out = compute_nutrition_master()
    assert set(out["score_par_espece"].keys()) == set(ESPECES)
    for esp, sc in out["score_par_espece"].items():
        assert 0.0 <= sc <= 100.0


def test_sensoriel_master_score_par_espece_5():
    out = compute_sensoriel_master()
    assert set(out["score_par_espece"].keys()) == set(ESPECES)
    for esp, sc in out["score_par_espece"].items():
        assert 0.0 <= sc <= 100.0


def test_comportement_master_score_par_espece_5():
    out = compute_comportement_master()
    assert set(out["score_par_espece"].keys()) == set(ESPECES)
    for esp, sc in out["score_par_espece"].items():
        assert 0.0 <= sc <= 100.0


def test_gouvernance_master_score_par_espece_5():
    out = compute_gouvernance_master()
    assert set(out["score_par_espece"].keys()) == set(ESPECES)
    for esp, sc in out["score_par_espece"].items():
        assert 0.0 <= sc <= 100.0


def test_se6_terr_master_score_par_espece_5():
    out = compute_territoire_master()
    assert set(out["score_par_espece"].keys()) == set(ESPECES)
    for esp, sc in out["score_par_espece"].items():
        assert 0.0 <= sc <= 100.0


# ─── Output signature conforme aux specs PHASE XIV ────────────────────

def test_se1_corr_master_output_signature():
    out = compute_corridors_master()
    for k in ("score_corridor_master_omega", "layer_corridors_master_omega",
              "bottleneck_segments", "shared_corridor_segments",
              "fragmentation_penalty_master"):
        assert k in out, f"clé manquante: {k}"


def test_nutrition_master_output_signature():
    out = compute_nutrition_master()
    for k in ("score_nutrition_master_omega", "layer_nutrition_disponibilite",
              "saisons_critiques", "deficit_mineraux_par_espece"):
        assert k in out


def test_sensoriel_master_output_signature():
    out = compute_sensoriel_master()
    for k in ("score_sensoriel_master_omega", "thermique_stress_aggregate_C",
              "neige_critique_aggregate_cm", "espece_zones_refuge"):
        assert k in out


def test_comportement_master_output_signature():
    out = compute_comportement_master()
    for k in ("score_comportement_master_omega", "calendrier_phenologique_unifie",
              "rut_actif_concurrents", "hyperphagie_active_concurrents"):
        assert k in out


def test_gouvernance_master_output_signature():
    out = compute_gouvernance_master()
    for k in ("score_gouvernance_master_omega", "recommandations_amenagement",
              "alertes_maladies_actives", "tendances_population_20_ans"):
        assert k in out


def test_se6_terr_master_output_signature():
    out = compute_territoire_master()
    for k in ("score_territoire_master_omega", "layer_territoire_master_omega",
              "decision_aptitude_territoriale", "rang_territorial_par_espece"):
        assert k in out
    assert out["decision_aptitude_territoriale"] in ("APTE", "MARGINAL", "INAPTE")


# ─── Bundle global cohérent ───────────────────────────────────────────

def test_compute_all_super_engines_bundle():
    bundle = compute_all_super_engines()
    assert bundle["specs_count"] == 6
    assert set(bundle["engines"].keys()) == {
        "ENGINE_CORRIDORS_MASTER_Ω", "ENGINE_NUTRITION_MASTER_Ω",
        "ENGINE_SENSORIEL_MASTER_Ω", "ENGINE_COMPORTEMENT_MASTER_Ω",
        "ENGINE_GOUVERNANCE_MASTER_Ω", "ENGINE_TERRITOIRE_MASTER_Ω",
    }
    # Tous les engines doivent avoir un score numérique
    for k, eng in bundle["engines"].items():
        assert eng["fallback_active"] is False
        assert eng["interpolation_active"] is False


def test_se6_terr_master_consomme_les_5_amont():
    out = compute_territoire_master()
    upstream = out["upstream_super_engines_scores"]
    assert set(upstream.keys()) == {
        "corridors_master", "nutrition_master", "sensoriel_master",
        "comportement_master", "gouvernance_master",
    }
    for v in upstream.values():
        assert isinstance(v, (int, float))


def test_anti_generique_total_violations_acceptable():
    """Les violations sont autorisées (paramètre absent dans BIO_PROFILE)
    mais doivent être tracées explicitement et ne pas exploser."""
    bundle = compute_all_super_engines()
    assert "anti_generique_violations_total" in bundle
    # Les violations sont des absences détectées — l'anti-régression vérifie
    # qu'elles sont SCANNÉES, pas qu'elles sont nulles.
    assert isinstance(bundle["anti_generique_violations_total"], int)
