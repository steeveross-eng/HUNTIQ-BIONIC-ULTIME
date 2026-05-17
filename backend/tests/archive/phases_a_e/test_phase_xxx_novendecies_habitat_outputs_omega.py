"""test_phase_xxx_novendecies_habitat_outputs_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME.

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
Aucun appel HTTP réel exécuté ici (probes RÉELS via curl séparément).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("/app/backend")))


# ═════════════════════════════════════════════════════════════════════════
# Section 1 — Module structure + classification doctrinale
# ═════════════════════════════════════════════════════════════════════════
def test_habitat_outputs_module_imports():
    """Le module habitat_outputs_compute_omega doit s'importer."""
    from engines.v8_institutional.especes import (
        habitat_outputs_compute_omega,
    )
    assert hasattr(
        habitat_outputs_compute_omega, "compute_habitat_outputs")
    assert hasattr(
        habitat_outputs_compute_omega, "get_habitat_outputs_status")


def test_outputs_requested_by_commandant_count_12():
    """Le Commandant a demandé exactement 12 outputs."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        OUTPUTS_REQUESTED_BY_COMMANDANT,
    )
    assert len(OUTPUTS_REQUESTED_BY_COMMANDANT) == 12
    expected = {
        "food_availability", "food_quality", "food_deficiency",
        "habitat_suitability", "bedding_zones", "feeding_zones",
        "rut_zones", "refuge_zones", "movement_corridors",
        "saline_optimal_locations", "pressure_sensitive_zones",
        "microhabitat_clusters",
    }
    assert set(OUTPUTS_REQUESTED_BY_COMMANDANT) == expected


def test_outputs_computable_count_4_anti_generique():
    """Exactement 4 outputs sont calculables depuis NDVI/EVI."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        OUTPUTS_COMPUTABLE_FROM_NDVI_EVI,
    )
    assert len(OUTPUTS_COMPUTABLE_FROM_NDVI_EVI) == 4
    expected = {
        "food_availability", "food_quality", "food_deficiency",
        "microhabitat_clusters",
    }
    assert set(OUTPUTS_COMPUTABLE_FROM_NDVI_EVI) == expected


def test_outputs_deferred_count_8_anti_generique():
    """Exactement 8 outputs deferred avec missing_inputs documentés."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        OUTPUTS_DEFERRED_MISSING_INPUTS,
    )
    assert len(OUTPUTS_DEFERRED_MISSING_INPUTS) == 8
    expected = {
        "habitat_suitability", "bedding_zones", "rut_zones",
        "refuge_zones", "movement_corridors",
        "saline_optimal_locations", "pressure_sensitive_zones",
        "feeding_zones",
    }
    assert set(OUTPUTS_DEFERRED_MISSING_INPUTS.keys()) == expected
    # Chaque deferred output doit avoir missing_inputs documentés
    for output_name, info in (
            OUTPUTS_DEFERRED_MISSING_INPUTS.items()):
        assert "missing_inputs" in info, output_name
        assert "directive_extension_required" in info, output_name
        assert "reason_anti_generique" in info, output_name
        assert isinstance(info["missing_inputs"], list)
        assert len(info["missing_inputs"]) >= 1
        assert len(info["reason_anti_generique"]) >= 50


def test_classification_total_equals_12():
    """4 calculables + 8 deferred = 12 demandés (cohérence stricte)."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        OUTPUTS_REQUESTED_BY_COMMANDANT,
        OUTPUTS_COMPUTABLE_FROM_NDVI_EVI,
        OUTPUTS_DEFERRED_MISSING_INPUTS,
    )
    union = (set(OUTPUTS_COMPUTABLE_FROM_NDVI_EVI)
             | set(OUTPUTS_DEFERRED_MISSING_INPUTS.keys()))
    assert union == set(OUTPUTS_REQUESTED_BY_COMMANDANT)
    intersection = (set(OUTPUTS_COMPUTABLE_FROM_NDVI_EVI)
                    & set(OUTPUTS_DEFERRED_MISSING_INPUTS.keys()))
    assert intersection == set()  # disjoints


def test_rut_zones_deferred_with_temporal_trap_documented():
    """rut_zones DOIT être deferred avec le piège temporel documenté."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        OUTPUTS_DEFERRED_MISSING_INPUTS,
    )
    rut = OUTPUTS_DEFERRED_MISSING_INPUTS["rut_zones"]
    reason = rut["reason_anti_generique"]
    # Le piège temporel doit être explicite
    assert "TEMPOREL" in reason or "temporel" in reason
    # Saisons rut documentées
    for keyword in ["oct", "sept", "mai", "avril"]:
        assert keyword in reason.lower()


def test_saline_optimal_locations_deferred_with_thematic_trap():
    """saline DOIT être deferred avec piège thématique NDVI≠Na+."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        OUTPUTS_DEFERRED_MISSING_INPUTS,
    )
    sal = OUTPUTS_DEFERRED_MISSING_INPUTS["saline_optimal_locations"]
    reason = sal["reason_anti_generique"]
    assert "THÉMATIQUE" in reason or "thématique" in reason
    assert "Na" in reason  # sodium référence chimique
    assert "USGS_SOIL_HOOK_ACTIVATE" in (
        sal["directive_extension_required"])


# ═════════════════════════════════════════════════════════════════════════
# Section 2 — Espèces-spécifiques peer-reviewed
# ═════════════════════════════════════════════════════════════════════════
def test_species_forage_thresholds_5_species_complete():
    """5 espèces BP135 avec seuils peer-reviewed complets."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        SPECIES_FORAGE_THRESHOLDS_V1,
    )
    expected_species = {
        "cerf", "orignal", "ours", "dindon", "wapiti"}
    assert set(SPECIES_FORAGE_THRESHOLDS_V1.keys()) == expected_species
    required_fields = [
        "scientific_name", "ndvi_optimal_low", "ndvi_optimal_high",
        "ndvi_dormancy_threshold", "evi_optimal_low",
        "evi_optimal_high", "feeding_strategy",
        "primary_reference", "scientific_basis",
    ]
    for sp, thresholds in SPECIES_FORAGE_THRESHOLDS_V1.items():
        for field in required_fields:
            assert field in thresholds, f"{sp} missing {field}"
        # Plages NDVI cohérentes [0, 1]
        assert 0.0 < thresholds["ndvi_optimal_low"] < 1.0
        assert (thresholds["ndvi_optimal_low"]
                < thresholds["ndvi_optimal_high"])
        assert thresholds["ndvi_optimal_high"] <= 1.0
        # Référence primaire doit ressembler à une citation (Author_YYYY)
        assert "_" in thresholds["primary_reference"]


def test_cerf_thresholds_match_hebblewhite_2008():
    """Cerf NDVI 0.4-0.7 (Hebblewhite 2008 hardwood/mixed forest)."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        SPECIES_FORAGE_THRESHOLDS_V1,
    )
    cerf = SPECIES_FORAGE_THRESHOLDS_V1["cerf"]
    assert cerf["ndvi_optimal_low"] == 0.40
    assert cerf["ndvi_optimal_high"] == 0.70
    assert "Hebblewhite_2008" in cerf["primary_reference"]


def test_ours_broad_tolerance_belant_2006():
    """Ours tolérance NDVI large 0.2-0.8 (Belant 2006 omnivore)."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        SPECIES_FORAGE_THRESHOLDS_V1,
    )
    ours = SPECIES_FORAGE_THRESHOLDS_V1["ours"]
    assert ours["ndvi_optimal_low"] == 0.20
    assert ours["ndvi_optimal_high"] == 0.80
    assert "Belant_2006" in ours["primary_reference"]
    assert "omnivore" in ours["feeding_strategy"]


# ═════════════════════════════════════════════════════════════════════════
# Section 3 — Helpers de calcul anti-générique
# ═════════════════════════════════════════════════════════════════════════
def test_normalize_ndvi_to_unit():
    """Normalisation NDVI [-1,1] → [0,1] correcte."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        _normalize_ndvi_to_unit,
    )
    assert _normalize_ndvi_to_unit(-1.0) == 0.0
    assert _normalize_ndvi_to_unit(0.0) == 0.5
    assert _normalize_ndvi_to_unit(1.0) == 1.0
    # Clamping
    assert _normalize_ndvi_to_unit(-2.0) == 0.0
    assert _normalize_ndvi_to_unit(2.0) == 1.0


def test_food_availability_below_dormancy_returns_low():
    """NDVI sous dormancy threshold → score food_avail très bas."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        _compute_food_availability_from_ndvi,
        SPECIES_FORAGE_THRESHOLDS_V1,
    )
    cerf = SPECIES_FORAGE_THRESHOLDS_V1["cerf"]
    # NDVI=0.05 < dormancy 0.10 → SUB_DORMANCY
    res = _compute_food_availability_from_ndvi(0.05, cerf)
    assert res["regime"] == "SUB_DORMANCY_SIGNAL"
    assert res["value"] < 30.0  # nutritional stress range


def test_food_availability_optimal_range():
    """NDVI dans range optimal → regime=OPTIMAL_RANGE."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        _compute_food_availability_from_ndvi,
        SPECIES_FORAGE_THRESHOLDS_V1,
    )
    cerf = SPECIES_FORAGE_THRESHOLDS_V1["cerf"]
    # NDVI=0.55 ∈ [0.4, 0.7]
    res = _compute_food_availability_from_ndvi(0.55, cerf)
    assert res["regime"] == "OPTIMAL_RANGE"
    assert res["score_optimal_match"] == 1.0


def test_food_deficiency_inverse_of_availability():
    """Si food_availability >= 30 → deficiency=0."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        _compute_food_deficiency,
        SPECIES_FORAGE_THRESHOLDS_V1,
    )
    cerf = SPECIES_FORAGE_THRESHOLDS_V1["cerf"]
    res = _compute_food_deficiency(50.0, cerf)
    assert res["value"] == 0.0
    assert res["regime"] == "ADEQUATE_FORAGE"

    res2 = _compute_food_deficiency(15.0, cerf)
    assert res2["value"] > 0.0
    assert res2["regime"] == "FORAGE_DEFICIENT"


def test_microhabitat_clusters_ranking_ordinal():
    """Avec 5 sites, ranking ordinal correct (descending composite)."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        _compute_microhabitat_clusters,
    )
    ndvi = {"a": 0.1, "b": 0.5, "c": 0.3, "d": 0.7, "e": 0.2}
    evi = {"a": 0.05, "b": 0.3, "c": 0.2, "d": 0.45, "e": 0.1}
    res = _compute_microhabitat_clusters(ndvi, evi)
    assert res["n_sites"] == 5
    assert "ranking" in res
    # Top rank doit être 'd' (NDVI 0.7 + EVI 0.45 le + haut)
    assert res["ranking"][0]["species_site"] == "d"
    # Doctrinal caveat documenté
    assert "n=5" in res["doctrinal_caveat_anti_generique"]
    assert "Pettorelli" in res["doctrinal_caveat_anti_generique"]


# ═════════════════════════════════════════════════════════════════════════
# Section 4 — Anti-générique : refus manifest fabriqué
# ═════════════════════════════════════════════════════════════════════════
def test_compute_rejects_fabricated_manifest():
    """compute_habitat_outputs sur SHA fabriqué doit être REJETÉ."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        compute_habitat_outputs,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        result = compute_habitat_outputs(
            nasa_ndvi_manifest_sha256="0" * 64,
            persist=False,
        )
        assert result["computed"] is False
        assert result["verdict"] == (
            "HABITAT_OUTPUTS_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
        assert result["anti_generique_strict"] is True
        assert result["v30_lock"] == "INVIOLÉ"
        assert result["no_engine_recompute_triggered"] is True
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_compute_requires_guardrails_enforced():
    """Sans guardrails ENFORCED, lève GuardrailsNotEnforcedError."""
    from engines.v8_institutional.especes import (
        habitat_outputs_compute_omega,
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            habitat_outputs_compute_omega.compute_habitat_outputs(
                nasa_ndvi_manifest_sha256="x" * 64,
                persist=False,
            )
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


# ═════════════════════════════════════════════════════════════════════════
# Section 5 — Forensic scope HABITAT extension (FUSION ADD-ONLY)
# ═════════════════════════════════════════════════════════════════════════
def test_forensic_scope_habitat_added_to_valid_scopes():
    """HABITAT scope ajouté FUSION ADD-ONLY (5 scopes au total)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        VALID_FORENSIC_SCOPES,
    )
    assert "HABITAT" in VALID_FORENSIC_SCOPES
    # FUSION ADD-ONLY : scopes existants préservés
    assert "B2_CREDENTIALS" in VALID_FORENSIC_SCOPES
    assert "ENDPOINT_PROBES" in VALID_FORENSIC_SCOPES
    assert "HOOK_ACTIVATIONS" in VALID_FORENSIC_SCOPES
    assert "CONFIG_CHANGES" in VALID_FORENSIC_SCOPES
    assert len(VALID_FORENSIC_SCOPES) == 5


# ═════════════════════════════════════════════════════════════════════════
# Section 6 — Anti-régression V30_LOCK
# ═════════════════════════════════════════════════════════════════════════
def test_habitat_module_does_not_import_super_engines_logic():
    """Le module habitat ne doit PAS importer super_engines_omega_logic.

    Anti-régression doctrinale : NO_ENGINE_RECOMPUTE_TRIGGERED.
    """
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "habitat_outputs_compute_omega.py").read_text(
            encoding="utf-8")
    assert "super_engines_omega_logic" not in src


def test_v30_lock_bp135_sha256_unchanged_after_habitat_import():
    """BP135 SHA-256 ne doit JAMAIS changer après import habitat."""
    bp135_path = Path(
        "/app/backend/data/registry_docs/bio_profile_omega_135/"
        "BIO_PROFILE_OMEGA_135_OFFICIAL.json")
    if not bp135_path.exists():
        pytest.skip("BP135 official non présent (déploiement minimal)")
    import hashlib
    sha_before = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    from engines.v8_institutional.especes import (
        habitat_outputs_compute_omega,
    )  # noqa: F401
    sha_after = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    assert sha_before == sha_after
