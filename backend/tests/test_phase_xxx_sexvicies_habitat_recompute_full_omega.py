"""test_phase_xxx_sexvicies_habitat_recompute_full_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME V2 :
intégration CANOPY pour bedding_zones FULL et refuge_zones FULL.

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest  # noqa: F401

sys.path.insert(0, str(Path("/app/backend")))


# ═════════════════════════════════════════════════════════════════════════
# Section 1 — Bedding zones FULL (Mysterud 2001 §3 complete)
# ═════════════════════════════════════════════════════════════════════════
def test_bedding_full_optimal_slope_optimal_canopy():
    """Slope 10° + canopy 70% → FULL_OPTIMAL_BEDDING_HABITAT."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_bedding_zones_FULL_dem_canopy,
    )
    res = _compute_bedding_zones_FULL_dem_canopy(
        slope_mean_deg=10.0, slope_max_deg=20.0,
        tree_cover_pct=70.0)
    # geometric mean(100, 100) = 100
    assert res["value"] == 100.0
    assert res["regime"] == "FULL_OPTIMAL_BEDDING_HABITAT"
    assert res["regime_full_status"] == (
        "FULL_BOTH_INPUTS_AVAILABLE")
    assert "Mysterud" in res["primary_reference"]
    assert "components" in res


def test_bedding_full_open_terrain_no_canopy():
    """Slope optimal mais canopy=0% → FULL_POOR (no cover)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_bedding_zones_FULL_dem_canopy,
    )
    res = _compute_bedding_zones_FULL_dem_canopy(
        slope_mean_deg=10.0, slope_max_deg=20.0,
        tree_cover_pct=0.0)
    # canopy_score=0, slope=100 → geometric mean = 0
    assert res["value"] == 0.0
    assert res["regime"] == "FULL_POOR_BEDDING_HABITAT"
    assert (res["components"]["canopy_regime"]
            == "OPEN_NO_COVER")


def test_bedding_full_dense_overstocked():
    """Canopy >80% → DENSE_OVERSTOCKED (réduit qualité bedding)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_bedding_zones_FULL_dem_canopy,
    )
    res = _compute_bedding_zones_FULL_dem_canopy(
        slope_mean_deg=10.0, slope_max_deg=20.0,
        tree_cover_pct=95.0)
    # canopy_score < 100 (dense décroît), slope=100
    assert (res["components"]["canopy_regime"]
            == "DENSE_OVERSTOCKED")
    assert res["components"]["canopy_score"] < 100.0


def test_bedding_full_degrade_to_partial_no_canopy():
    """Sans canopy, fallback partial."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_bedding_zones_FULL_dem_canopy,
    )
    res = _compute_bedding_zones_FULL_dem_canopy(
        slope_mean_deg=10.0, slope_max_deg=20.0,
        tree_cover_pct=None)
    assert res["regime_full_status"] == (
        "DEGRADED_TO_PARTIAL_MISSING_CANOPY")
    assert res["unit"] == "score_0_100_partial_dem_only"


def test_bedding_full_no_dem_no_canopy_deferred():
    """Aucun input → DEFERRED."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_bedding_zones_FULL_dem_canopy,
    )
    res = _compute_bedding_zones_FULL_dem_canopy(
        slope_mean_deg=None, slope_max_deg=None,
        tree_cover_pct=None)
    assert res["regime_full_status"] == "DEFERRED_NO_INPUTS"


# ═════════════════════════════════════════════════════════════════════════
# Section 2 — Refuge zones FULL (Forman 1986 + Hansen 2003)
# ═════════════════════════════════════════════════════════════════════════
def test_refuge_full_high_ruggedness_dense_canopy():
    """High TRI + canopy 65% → FULL_HIGH_REFUGE_POTENTIAL."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_refuge_zones_FULL_tri_canopy,
    )
    res = _compute_refuge_zones_FULL_tri_canopy(
        elevation_std_m=72.0, slope_max_deg=35.0,
        tree_cover_pct=65.0, nontree_veg_pct=30.0)
    # TRI ≈ 70 × 0.5 + canopy_high × 0.35 + nontree × 0.15
    assert res["value"] >= 60.0
    assert res["regime_full_status"] == "FULL_INPUTS_AVAILABLE"
    assert "Forman" in res["primary_reference"]
    assert "Hansen" in res["primary_reference"]


def test_refuge_full_open_terrain_low_canopy():
    """Low TRI + low canopy → FULL_LOW or FULL_OPEN."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_refuge_zones_FULL_tri_canopy,
    )
    res = _compute_refuge_zones_FULL_tri_canopy(
        elevation_std_m=4.0, slope_max_deg=9.0,
        tree_cover_pct=10.0, nontree_veg_pct=70.0)
    assert res["value"] < 50.0
    assert "FULL" in res["regime"]


def test_refuge_full_components_weights_renormalized():
    """Sans nontree_veg, poids renormalisés."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_refuge_zones_FULL_tri_canopy,
    )
    res = _compute_refuge_zones_FULL_tri_canopy(
        elevation_std_m=50.0, slope_max_deg=25.0,
        tree_cover_pct=50.0, nontree_veg_pct=None)
    assert "weights_renormalized" in res["components"]
    weights = res["components"]["weights_renormalized"]
    # Avec seuls TRI(0.5) + canopy(0.35), total=0.85 → renormalisé
    # tri = 0.5/0.85 ≈ 0.588
    assert abs(weights["tri"] - 0.588) < 0.01
    assert "nontree" not in weights


def test_refuge_full_degrade_to_partial_no_canopy():
    """Sans canopy, fallback partial."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_refuge_zones_FULL_tri_canopy,
    )
    res = _compute_refuge_zones_FULL_tri_canopy(
        elevation_std_m=50.0, slope_max_deg=25.0,
        tree_cover_pct=None, nontree_veg_pct=None)
    assert res["regime_full_status"] == (
        "DEGRADED_TO_PARTIAL_MISSING_CANOPY")
    assert res["unit"] == "score_0_100_TRI_partial"


def test_refuge_full_no_dem_deferred():
    """Sans DEM → DEFERRED."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _compute_refuge_zones_FULL_tri_canopy,
    )
    res = _compute_refuge_zones_FULL_tri_canopy(
        elevation_std_m=None, slope_max_deg=None,
        tree_cover_pct=70.0)
    assert res["regime"] == "DEFERRED_NO_DEM_DATA"
    assert res["value"] is None


# ═════════════════════════════════════════════════════════════════════════
# Section 3 — Helper extraction CANOPY
# ═════════════════════════════════════════════════════════════════════════
def test_extract_canopy_per_site_correct():
    """Extraction tree_cover/nontree_veg/nonveg correcte."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _extract_canopy_per_site,
    )
    canopy_v = {
        "site_results": {
            "espece_a": {
                "bands": {
                    "TREE_COVER": {
                        "valid": True,
                        "stats": {"mean": 14.33}},
                    "NONTREE_VEG": {
                        "valid": True,
                        "stats": {"mean": 65.67}},
                    "NONVEG": {
                        "valid": True,
                        "stats": {"mean": 20.0}},
                },
            },
        },
    }
    out = _extract_canopy_per_site(canopy_v)
    assert "espece_a" in out
    assert out["espece_a"]["tree_cover_pct"] == 14.33
    assert out["espece_a"]["nontree_veg_pct"] == 65.67
    assert out["espece_a"]["nonveg_pct"] == 20.0


def test_extract_canopy_handles_invalid_band():
    """Bande invalide → None (anti-générique)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        _extract_canopy_per_site,
    )
    canopy_v = {
        "site_results": {
            "espece_a": {
                "bands": {
                    "TREE_COVER": {"valid": False},
                    "NONTREE_VEG": {
                        "valid": True,
                        "stats": {"mean": 50.0}},
                    "NONVEG": {"valid": False},
                },
            },
        },
    }
    out = _extract_canopy_per_site(canopy_v)
    assert out["espece_a"]["tree_cover_pct"] is None
    assert out["espece_a"]["nontree_veg_pct"] == 50.0
    assert out["espece_a"]["nonveg_pct"] is None


# ═════════════════════════════════════════════════════════════════════════
# Section 4 — Anti-régression V30_LOCK
# ═════════════════════════════════════════════════════════════════════════
def test_module_does_not_import_super_engines_logic():
    """Anti-régression : NO_ENGINE_RECOMPUTE_TRIGGERED."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "habitat_outputs_recompute_omega.py").read_text(
            encoding="utf-8")
    assert "super_engines_omega_logic" not in src


def test_full_function_exposed():
    """Module expose les nouvelles fonctions FULL."""
    from engines.v8_institutional.especes import (
        habitat_outputs_recompute_omega,
    )
    assert hasattr(
        habitat_outputs_recompute_omega,
        "_compute_bedding_zones_FULL_dem_canopy")
    assert hasattr(
        habitat_outputs_recompute_omega,
        "_compute_refuge_zones_FULL_tri_canopy")
    assert hasattr(
        habitat_outputs_recompute_omega,
        "_extract_canopy_per_site")
