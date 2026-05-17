"""Tests anti-régression — habitat_outputs_recompute_v3_omega.py (P5).

NOMS NEUTRES : aucun mot dans BCE_4X_EXCLUDED_KEYWORDS.
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
"""
from __future__ import annotations

import json

import pytest


def test_phase_xxx_octovicies_module_imports_clean():
    """Module V3 importe sans erreur."""
    from engines.v8_institutional.especes import (
        habitat_outputs_recompute_v3_omega as mod)
    assert hasattr(
        mod,
        "recompute_habitat_outputs_with_anthropogenic_pressure_v3")
    assert hasattr(mod, "get_habitat_recompute_v3_status")
    assert hasattr(mod, "HABITAT_RECOMPUTE_V3_PATH")


def test_phase_xxx_octovicies_extract_pressure_per_site_valid():
    """Extraction OK quand composite valide."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        _extract_pressure_per_site,
    )
    fake_validation = {
        "site_results": {
            "espece_a": {
                "composite_index": {
                    "valid": True,
                    "composite_index_0_100": 75.0,
                    "components": {"road_score": 80.0},
                    "raw_inputs": {"road_density_km_per_km2": 4.0},
                },
                "pressure_sensitive_zone_classification": {
                    "regime": "HIGH_PRESSURE_AVOID_ZONE",
                    "is_pressure_sensitive": True,
                },
            },
        },
    }
    out = _extract_pressure_per_site(fake_validation)
    assert out["espece_a"]["valid"] is True
    assert out["espece_a"]["composite_index_0_100"] == 75.0
    assert out["espece_a"]["regime"] == (
        "HIGH_PRESSURE_AVOID_ZONE")


def test_phase_xxx_octovicies_extract_pressure_per_site_invalid():
    """Extraction reporte fail honnêtement (anti-générique)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        _extract_pressure_per_site,
    )
    fake_validation = {
        "site_results": {
            "espece_a": {
                "composite_index": {
                    "valid": False,
                    "reason": "at_least_one_source_invalid",
                },
                "pressure_sensitive_zone_classification": None,
            },
        },
    }
    out = _extract_pressure_per_site(fake_validation)
    assert out["espece_a"]["valid"] is False
    assert "at_least_one_source_invalid" in (
        out["espece_a"]["reason"])


def test_phase_xxx_octovicies_compute_pressure_output_deferred():
    """Pressure output deferred quand data invalide (anti-générique)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        _compute_pressure_sensitive_zones_output,
    )
    out = _compute_pressure_sensitive_zones_output({
        "valid": False,
        "reason": "missing_in_validation",
    })
    assert out["value"] is None
    assert out["regime"] == (
        "DEFERRED_NO_VALID_PRESSURE_DATA")


def test_phase_xxx_octovicies_compute_pressure_output_valid():
    """Pressure output computable quand data valide."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        _compute_pressure_sensitive_zones_output,
    )
    out = _compute_pressure_sensitive_zones_output({
        "valid": True,
        "composite_index_0_100": 47.5,
        "regime": "LOW_PRESSURE_MARGINAL",
        "is_pressure_sensitive": False,
        "components": {"road_score": 50.0},
        "raw_inputs": {"road_density_km_per_km2": 2.5},
    })
    assert out["value"] == 47.5
    assert out["regime"] == "LOW_PRESSURE_MARGINAL"
    assert out["is_pressure_sensitive"] is False
    assert out["unit"] == "anthropogenic_pressure_index_0_100"
    assert "Naidoo_Burton_2010_ConservationLetters" in (
        out["primary_references"])


def test_phase_xxx_octovicies_overlay_v3_path_constant_correct():
    """Path overlay V3 est dans pipelines/habitat_recompute_v3."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        HABITAT_RECOMPUTE_V3_ROOT,
        HABITAT_RECOMPUTE_V3_PATH,
    )
    assert "habitat_recompute_v3" in str(
        HABITAT_RECOMPUTE_V3_ROOT)
    assert HABITAT_RECOMPUTE_V3_PATH.name == (
        "habitat_outputs_recompute_v3_overlay.json")


def test_phase_xxx_octovicies_get_status_doctrinal_keys():
    """get_habitat_recompute_v3_status retourne keys doctrinales."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        get_habitat_recompute_v3_status,
    )
    status = get_habitat_recompute_v3_status()
    assert status.get("v30_lock") == "INVIOLÉ"
    assert status.get("ordre") == (
        "P5_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3")


def test_phase_xxx_octovicies_overlay_v3_state_when_present():
    """Si overlay V3 existe, structure doctrinale conforme."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        HABITAT_RECOMPUTE_V3_PATH,
    )
    if not HABITAT_RECOMPUTE_V3_PATH.exists():
        pytest.skip("Aucun V3 encore exécuté.")
    state = json.loads(
        HABITAT_RECOMPUTE_V3_PATH.read_text(encoding="utf-8"))
    assert state.get("v30_lock") == "INVIOLÉ"
    assert "history" in state
    last = state["history"][-1] if state["history"] else None
    if last is not None:
        # 9_OF_12 si tous hooks chargés
        assert "verdict" in last
        assert last.get("anti_generique_strict") is True
        assert last.get("v30_lock") == "INVIOLÉ"
        assert last.get("fusion_add_only") is True


def test_phase_xxx_octovicies_v3_inheritance_from_v2_present():
    """V3 must inherit V2 manifest sha256 (FUSION ADD-ONLY)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        HABITAT_RECOMPUTE_V3_PATH,
    )
    if not HABITAT_RECOMPUTE_V3_PATH.exists():
        pytest.skip("Aucun V3 encore exécuté.")
    state = json.loads(
        HABITAT_RECOMPUTE_V3_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History V3 vide.")
    last = state["history"][-1]
    v2_inh = last.get("v2_inheritance") or {}
    assert "v2_recompute_sha256" in v2_inh
    assert "v2_verdict" in v2_inh
    assert "v2_hooks_manifests_inherited" in v2_inh


def test_phase_xxx_octovicies_pressure_sensitive_zones_present_per_site():
    """Pour chaque site V3, pressure_sensitive_zones doit exister."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        HABITAT_RECOMPUTE_V3_PATH,
    )
    if not HABITAT_RECOMPUTE_V3_PATH.exists():
        pytest.skip("Aucun V3 encore exécuté.")
    state = json.loads(
        HABITAT_RECOMPUTE_V3_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History V3 vide.")
    last = state["history"][-1]
    per_site = last.get("per_site_outputs_v3") or {}
    if not per_site:
        pytest.skip("Aucun site V3.")
    for site_name, sd in per_site.items():
        outputs = sd.get("computed_outputs") or {}
        assert "pressure_sensitive_zones" in outputs, (
            f"Missing pressure_sensitive_zones in {site_name}")


def test_phase_xxx_octovicies_outputs_deferred_v3_only_3():
    """V3 doit lister 3 outputs encore deferred (vs 4 en V2)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        HABITAT_RECOMPUTE_V3_PATH,
    )
    if not HABITAT_RECOMPUTE_V3_PATH.exists():
        pytest.skip("Aucun V3 encore exécuté.")
    state = json.loads(
        HABITAT_RECOMPUTE_V3_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History V3 vide.")
    last = state["history"][-1]
    deferred = last.get(
        "outputs_still_deferred_anti_generique_strict_v3") or {}
    # rut_zones, feeding_zones, microhabitat_clusters_global_dense
    assert len(deferred) == 3
    assert "rut_zones" in deferred
    assert "feeding_zones" in deferred
    # pressure_sensitive_zones N'EST PLUS deferred en V3
    assert "pressure_sensitive_zones" not in deferred
