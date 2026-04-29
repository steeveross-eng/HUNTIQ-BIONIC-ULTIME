"""
test_phase_xvii_3_engines_omega.py — PHASE XVII · 3 ENGINES SCIENTIFIQUES
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°37

Couverture pytest : ENGINE_HABITAT_Ω + ENGINE_VÉGÉTATION_Ω + ENGINE_PHÉNOLOGIE_Ω.
Doctrine stricte : zéro fallback, zéro interpolation, aucune dépendance legacy.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import pytest

from engines.v8_institutional.especes.datasets_science_omega import (
    ESPECES_CANONICAL, SAISONS_CANONICAL,
    harmonize_nutrition_studies, harmonize_habitat_studies,
    build_unified_sci_referentiel, classify_preuve,
)
from engines.v8_institutional.especes.engine_habitat_omega import (
    compute_habitat_score, compute_habitat_all_especes,
    ENGINE_HABITAT_Ω_LOCK_SHA256,
)
from engines.v8_institutional.especes.engine_vegetation_omega import (
    compute_vegetation_availability, compute_vegetation_all_especes,
    ENGINE_VEGETATION_Ω_LOCK_SHA256,
)
from engines.v8_institutional.especes.engine_phenologie_omega import (
    compute_phenology_seasonal_index, compute_phenology_all_especes,
    ENGINE_PHENOLOGIE_Ω_LOCK_SHA256,
)


# ─── Datasets harmonisés ──────────────────────────────────────────────

def test_dataset_nutrition_harmonise_20_studies():
    nut = harmonize_nutrition_studies()
    assert len(nut) == 20
    for s in nut:
        assert "especes_canoniques" in s
        assert "saisons_canoniques" in s
        assert s["type_preuve"] in ("GOV", "UNI", "PR", "UNKNOWN")


def test_dataset_habitat_harmonise_50_studies():
    hab = harmonize_habitat_studies()
    assert len(hab) == 50
    for s in hab:
        assert s["espece_canonique"] in ESPECES_CANONICAL
        assert s["type_preuve"] in ("GOV", "UNI", "PR", "UNKNOWN")


def test_sci_referentiel_unifie_structure():
    sci = build_unified_sci_referentiel()
    assert sci["totaux"]["nutrition_count"] == 20
    assert sci["totaux"]["habitat_count"] == 50
    assert sci["totaux"]["total_studies"] == 70
    assert sci["totaux"]["especes_canoniques_count"] == 5
    for esp in ESPECES_CANONICAL:
        assert esp in sci["by_espece"]
        assert sci["by_espece"][esp]["habitat_count"] == 10


def test_classify_preuve_known_sources():
    assert classify_preuve("Journal of Wildlife Management") == "PR"
    assert classify_preuve("Colorado Division of Wildlife Tech. Pub.") == "GOV"
    assert classify_preuve("Book chapter") == "UNI"
    assert classify_preuve("Book / Synthesis") == "UNI"


# ─── ENGINE_HABITAT_Ω ─────────────────────────────────────────────────

def test_engine_habitat_lock_sha256_present():
    assert isinstance(ENGINE_HABITAT_Ω_LOCK_SHA256, str)
    assert len(ENGINE_HABITAT_Ω_LOCK_SHA256) == 64


@pytest.mark.parametrize("espece", ESPECES_CANONICAL)
def test_engine_habitat_score_par_espece(espece):
    out = compute_habitat_score(espece)
    assert out["super_engine_id"] == "ENGINE_HABITAT_Ω"
    assert 0.0 <= out["habitat_score_omega"] <= 100.0
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False
    assert out["studies_count"] == 10  # 10 études par espèce


def test_engine_habitat_bundle_master_ge_70():
    """Bundle master score >= 70 avec les 50 études disponibles."""
    bundle = compute_habitat_all_especes()
    assert bundle["manifest_id"] == "ENGINE_HABITAT_Ω_BUNDLE"
    assert bundle["habitat_master_score_omega"] >= 70.0
    assert set(bundle["results_par_espece"].keys()) == set(ESPECES_CANONICAL)


def test_engine_habitat_invalid_espece_raises():
    with pytest.raises(ValueError, match="ESPECE_NON_CANONIQUE"):
        compute_habitat_score("CARIBOU")


# ─── ENGINE_VÉGÉTATION_Ω ──────────────────────────────────────────────

def test_engine_vegetation_lock_sha256_present():
    assert isinstance(ENGINE_VEGETATION_Ω_LOCK_SHA256, str)
    assert len(ENGINE_VEGETATION_Ω_LOCK_SHA256) == 64


@pytest.mark.parametrize("espece", ESPECES_CANONICAL)
def test_engine_vegetation_par_espece(espece):
    out = compute_vegetation_availability(espece)
    assert out["super_engine_id"] == "ENGINE_VÉGÉTATION_Ω"
    assert 0.0 <= out["vegetation_availability_omega"] <= 100.0
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False
    # Chaque espèce doit avoir au moins une étude pertinente
    assert out["studies_count"] >= 1
    assert len(out["consumables_expected"]) > 0


def test_engine_vegetation_bundle_master_ge_60():
    bundle = compute_vegetation_all_especes()
    assert bundle["manifest_id"] == "ENGINE_VÉGÉTATION_Ω_BUNDLE"
    assert bundle["vegetation_master_score_omega"] >= 60.0


def test_engine_vegetation_seasonal_coverage_detected():
    out = compute_vegetation_availability("ORIGNAL")
    # Orignal a des études sur 4 saisons (Courtois 1990s + Peek 1974 toutes saisons)
    assert len(out["seasonal_coverage"]) >= 1


# ─── ENGINE_PHÉNOLOGIE_Ω ──────────────────────────────────────────────

def test_engine_phenologie_lock_sha256_present():
    assert isinstance(ENGINE_PHENOLOGIE_Ω_LOCK_SHA256, str)
    assert len(ENGINE_PHENOLOGIE_Ω_LOCK_SHA256) == 64


@pytest.mark.parametrize("espece", ESPECES_CANONICAL)
def test_engine_phenologie_par_espece(espece):
    out = compute_phenology_seasonal_index(espece)
    assert out["super_engine_id"] == "ENGINE_PHÉNOLOGIE_Ω"
    assert 0.0 <= out["phenology_seasonal_index_omega"] <= 100.0
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False


def test_engine_phenologie_bundle_master_ge_50():
    bundle = compute_phenology_all_especes()
    assert bundle["manifest_id"] == "ENGINE_PHÉNOLOGIE_Ω_BUNDLE"
    assert bundle["phenology_master_score_omega"] >= 50.0


def test_engine_phenologie_critical_seasons_ours_noir():
    """Ours noir : saisons critiques AUTOMNE + HIVER définies."""
    out = compute_phenology_seasonal_index("OURS_NOIR")
    expected = {"AUTOMNE", "HIVER"}
    assert set(out["critical_seasons_expected"]) == expected


def test_engine_phenologie_detects_hyperphagie_ours_noir():
    """Ours noir : hyperphagie doit être détectée dans les études."""
    out = compute_phenology_seasonal_index("OURS_NOIR")
    assert "hyperphagie" in out["phenological_events_detected"]


def test_engine_phenologie_nut_hab_convergence_ge_50():
    for esp in ESPECES_CANONICAL:
        out = compute_phenology_seasonal_index(esp)
        # Chaque espèce a au moins 10 études habitat → convergence min 50
        assert out["nut_hab_convergence_ratio"] >= 50.0


# ─── ENGINE-CROSS : cohérence inter-engines ───────────────────────────

def test_3_engines_all_return_bundle_for_5_especes():
    h = compute_habitat_all_especes()
    v = compute_vegetation_all_especes()
    p = compute_phenology_all_especes()
    for bundle in (h, v, p):
        assert len(bundle["results_par_espece"]) == 5


def test_3_engines_independent_lock_sha256():
    # Les 3 SHA doivent être distincts
    assert ENGINE_HABITAT_Ω_LOCK_SHA256 != ENGINE_VEGETATION_Ω_LOCK_SHA256
    assert ENGINE_VEGETATION_Ω_LOCK_SHA256 != ENGINE_PHENOLOGIE_Ω_LOCK_SHA256
    assert ENGINE_HABITAT_Ω_LOCK_SHA256 != ENGINE_PHENOLOGIE_Ω_LOCK_SHA256
