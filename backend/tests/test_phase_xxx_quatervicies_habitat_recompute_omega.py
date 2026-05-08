"""test_phase_xxx_quatervicies_habitat_recompute_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME.

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("/app/backend")))


# ═════════════════════════════════════════════════════════════════════════
# Section 1 — Module structure
# ═════════════════════════════════════════════════════════════════════════
def test_module_imports():
    """Module habitat_outputs_recompute_omega doit s'importer."""
    from engines.v8_institutional.especes import (
        habitat_outputs_recompute_omega,
    )
    assert hasattr(habitat_outputs_recompute_omega,
                   "recompute_habitat_outputs_with_all_hooks")
    assert hasattr(habitat_outputs_recompute_omega,
                   "get_habitat_recompute_status")


def test_recompute_path_under_pipelines():
    """Persistance dans data/pipelines/habitat_recompute_v2/."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        HABITAT_RECOMPUTE_ROOT, HABITAT_RECOMPUTE_PATH,
    )
    assert "data/pipelines/habitat_recompute_v2" in str(
        HABITAT_RECOMPUTE_ROOT)
    assert str(HABITAT_RECOMPUTE_PATH).endswith(
        "_overlay.json")


def test_default_species_site_map_5_species():
    """Default mapping 5 sites → 5 espèces BP135."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        SPECIES_TO_SITE_MAP_DEFAULT,
    )
    assert len(SPECIES_TO_SITE_MAP_DEFAULT) == 5
    assert SPECIES_TO_SITE_MAP_DEFAULT["espece_a"] == "cerf"
    assert SPECIES_TO_SITE_MAP_DEFAULT["espece_b"] == "orignal"
    assert SPECIES_TO_SITE_MAP_DEFAULT["espece_c"] == "ours"
    assert SPECIES_TO_SITE_MAP_DEFAULT["espece_d"] == "dindon"
    assert SPECIES_TO_SITE_MAP_DEFAULT["espece_e"] == "wapiti"


# ═════════════════════════════════════════════════════════════════════════
# Section 2 — Calculs anti-générique
# ═════════════════════════════════════════════════════════════════════════
def test_bedding_zones_optimal_range_5_15_deg():
    """Slope 5-15° = OPTIMAL_BEDDING_RANGE (Mysterud 2001)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_bedding_zones_slope_partial,
    )
    res = _compute_bedding_zones_slope_partial(10.0, 20.0)
    assert res["regime"] == "OPTIMAL_BEDDING_RANGE"
    assert res["value"] == 100.0
    assert res["primary_reference"] == (
        "Mysterud_2001_Ecography")


def test_bedding_zones_too_steep_returns_zero():
    """Slope > 25° = TOO_STEEP_NO_BEDDING."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_bedding_zones_slope_partial,
    )
    res = _compute_bedding_zones_slope_partial(30.0, 40.0)
    assert res["regime"] == "TOO_STEEP_NO_BEDDING"
    assert res["value"] == 0.0


def test_bedding_zones_too_flat_drainage_risk():
    """Slope < 2° = TOO_FLAT_DRAINAGE_RISK."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_bedding_zones_slope_partial,
    )
    res = _compute_bedding_zones_slope_partial(1.0, 5.0)
    assert res["regime"] == "TOO_FLAT_DRAINAGE_RISK"
    assert res["value"] < 25.0


def test_bedding_zones_no_dem_returns_deferred():
    """Slope=None → DEFERRED."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_bedding_zones_slope_partial,
    )
    res = _compute_bedding_zones_slope_partial(None, None)
    assert res["regime"] == "DEFERRED_NO_DEM_DATA"
    assert res["value"] is None


def test_refuge_zones_high_ruggedness():
    """High elev_std + slope_max → HIGH_RUGGEDNESS_REFUGE."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_refuge_zones_terrain_ruggedness,
    )
    res = _compute_refuge_zones_terrain_ruggedness(72.0, 35.0)
    assert res["value"] >= 60.0
    assert res["regime"] == "HIGH_RUGGEDNESS_REFUGE_POTENTIAL"
    assert res["primary_reference"] == (
        "Riley_1999_IntermountJSci")


def test_refuge_zones_low_ruggedness():
    """Low std + slope → LOW_RUGGEDNESS."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_refuge_zones_terrain_ruggedness,
    )
    res = _compute_refuge_zones_terrain_ruggedness(4.0, 9.0)
    assert res["value"] < 30.0
    assert res["regime"] == "LOW_RUGGEDNESS_OPEN_TERRAIN"


def test_saline_optimal_acid_high_cec():
    """pH bas + CEC élevée → HIGH_SALINE_POTENTIAL."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_saline_optimal_partial,
    )
    res = _compute_saline_optimal_partial(4.9, 42.0)
    assert res["value"] >= 50.0
    assert res["regime"] == (
        "HIGH_SALINE_POTENTIAL_ACID_HIGH_CEC")
    assert res["primary_reference"] == (
        "Belant_2010_CanJZool")


def test_saline_optimal_alkaline_low_cec():
    """pH haut + CEC basse → LOW_SALINE."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_saline_optimal_partial,
    )
    res = _compute_saline_optimal_partial(7.5, 10.0)
    assert res["value"] < 25.0
    assert res["regime"] == "LOW_SALINE_POTENTIAL"


def test_saline_optimal_no_data_deferred():
    """No USGS data → DEFERRED."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_saline_optimal_partial,
    )
    res = _compute_saline_optimal_partial(None, None)
    assert res["regime"] == "DEFERRED_NO_USGS_SOIL_DATA"
    assert res["value"] is None


def test_habitat_suitability_4_components_full():
    """Habitat suitability composite avec 4 composantes."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_habitat_suitability_multi_covariate,
    )
    res = _compute_habitat_suitability_multi_covariate(
        envelope_phillips=80.0,
        food_availability_score=70.0,
        bedding_partial=90.0,
        refuge_partial=60.0)
    # Score = 80*0.35 + 70*0.30 + 90*0.20 + 60*0.15 = 76
    assert res["value"] == 76.0
    assert res["regime"] == "HIGH_SUITABILITY"
    assert res["n_components_available"] == 4
    assert res["n_components_total"] == 4


def test_habitat_suitability_partial_renormalized():
    """Si certaines composantes manquent, poids renormalisés."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_habitat_suitability_multi_covariate,
    )
    res = _compute_habitat_suitability_multi_covariate(
        envelope_phillips=80.0,
        food_availability_score=None,
        bedding_partial=None,
        refuge_partial=None)
    # Seul envelope (poids 0.35 → 1.0 renormalisé) → score = 80
    assert res["value"] == 80.0
    assert res["n_components_available"] == 1


def test_habitat_suitability_no_inputs_deferred():
    """Aucun input → DEFERRED."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_habitat_suitability_multi_covariate,
    )
    res = _compute_habitat_suitability_multi_covariate(
        None, None, None, None)
    assert res["value"] is None
    assert res["regime"] == "DEFERRED_NO_INPUTS_AVAILABLE"


# ═════════════════════════════════════════════════════════════════════════
# Section 3 — Corridor inter-sites
# ═════════════════════════════════════════════════════════════════════════
def test_continuity_index_pairs_5C2_10_pairs():
    """5 sites BP135 → 5C2=10 paires."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_corridor_continuity_inter_sites,
    )
    sites_data = {
        f"site_{i}": {
            "nasa_ndvi": {"ndvi_mean": 0.1 + i * 0.05},
            "usgs_soil": {"phh2o": 5.0 + i * 0.2},
            "dem": {"elevation_mean_m": 50.0 + i * 30.0},
        } for i in range(5)
    }
    res = _compute_corridor_continuity_inter_sites(sites_data)
    assert res["n_pairs"] == 10
    # Chaque paire a 3 composantes
    for p in res["pairs_ranked"]:
        assert p["n_components_compared"] == 3
        assert 0 <= p["continuity_score"] <= 100
    # Top pair identifié
    assert "top_corridor_pair" in res


def test_continuity_index_no_components_deferred():
    """Aucune composante → DEFERRED."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_corridor_continuity_inter_sites,
    )
    sites_data = {
        f"site_{i}": {
            "nasa_ndvi": {}, "usgs_soil": {}, "dem": {}}
        for i in range(2)
    }
    res = _compute_corridor_continuity_inter_sites(sites_data)
    assert res["n_pairs"] == 0
    assert res["regime"] == (
        "DEFERRED_NO_COMPONENTS_AVAILABLE")


# ═════════════════════════════════════════════════════════════════════════
# Section 4 — Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_recompute_requires_guardrails_enforced():
    """Sans guardrails ENFORCED, lève GuardrailsNotEnforced."""
    from engines.v8_institutional.especes import (
        habitat_outputs_recompute_omega,
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            habitat_outputs_recompute_omega.recompute_habitat_outputs_with_all_hooks(  # noqa: E501
                persist=False)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_get_status_returns_valid_dict():
    """get_habitat_recompute_status retourne dict valide."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        get_habitat_recompute_status,
    )
    status = get_habitat_recompute_status()
    assert "manifest_id" in status
    assert "current_status" in status
    assert "v30_lock" in status
    assert status["v30_lock"] == "INVIOLÉ"
    assert status["current_status"] in (
        "NOT_RECOMPUTED", "RECOMPUTED_OPERATIONAL")


# ═════════════════════════════════════════════════════════════════════════
# Section 5 — Anti-régression V30_LOCK
# ═════════════════════════════════════════════════════════════════════════
def test_module_does_not_import_super_engines_logic():
    """Anti-régression : NO_ENGINE_RECOMPUTE_TRIGGERED."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "habitat_outputs_recompute_omega.py").read_text(
            encoding="utf-8")
    assert "super_engines_omega_logic" not in src


def test_v30_lock_bp135_sha256_unchanged_after_import():
    """BP135 SHA-256 ne doit JAMAIS changer après import."""
    bp135_path = Path(
        "/app/backend/data/registry_docs/bio_profile_omega_135/"
        "BIO_PROFILE_OMEGA_135_OFFICIAL.json")
    if not bp135_path.exists():
        pytest.skip("BP135 official non présent")
    import hashlib
    sha_before = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    from engines.v8_institutional.especes import (
        habitat_outputs_recompute_omega,
    )  # noqa: F401
    sha_after = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    assert sha_before == sha_after


def test_outputs_still_deferred_4_outputs_traced():
    """4 outputs encore deferred (rut/feeding/pressure/microhabitat)."""
    from engines.v8_institutional.especes import (
        habitat_outputs_recompute_omega,
        pipeline_guardrails_omega,
    )
    original_enf = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        result = (
            habitat_outputs_recompute_omega
            .recompute_habitat_outputs_with_all_hooks(
                persist=False))
        deferred = result[
            "outputs_still_deferred_anti_generique_strict"]
        assert "rut_zones" in deferred
        assert "PIÈGE TEMPOREL" in (
            deferred["rut_zones"]["reason"])
        assert "feeding_zones" in deferred
        assert "pressure_sensitive_zones" in deferred
        assert "microhabitat_clusters_global" in deferred
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enf)
