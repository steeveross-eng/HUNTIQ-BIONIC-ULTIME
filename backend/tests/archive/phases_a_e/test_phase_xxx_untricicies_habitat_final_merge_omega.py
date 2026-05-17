"""Tests anti-régression — habitat_outputs_final_merge_omega.py (P7).

NOMS NEUTRES : aucun mot dans BCE_4X_EXCLUDED_KEYWORDS.
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
"""
from __future__ import annotations

import json

import pytest


def test_phase_xxx_untricicies_module_imports_clean():
    from engines.v8_institutional.especes import (
        habitat_outputs_final_merge_omega as mod)
    assert hasattr(mod, "merge_habitat_outputs_final")
    assert hasattr(mod, "get_habitat_final_merge_status")
    assert hasattr(mod, "HABITAT_FINAL_PATH")


def test_phase_xxx_untricicies_extract_rut_per_site_valid():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        _extract_rut_per_site,
    )
    fake = {
        "site_results": {
            "espece_a": {
                "rut_zones_composite": {
                    "valid": True,
                    "composite_score_0_100": 75.0,
                    "regime": "RUT_ZONE_HIGH_PROBABILITY",
                    "components": {"photoperiod_score": 80.0},
                    "n_pillars_valid": 3,
                    "doctrinal_caveat": "TEST",
                },
            },
        },
    }
    out = _extract_rut_per_site(fake)
    assert out["espece_a"]["valid"] is True
    assert out["espece_a"]["composite_score_0_100"] == 75.0
    assert out["espece_a"]["regime"] == (
        "RUT_ZONE_HIGH_PROBABILITY")


def test_phase_xxx_untricicies_extract_rut_per_site_invalid():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        _extract_rut_per_site,
    )
    fake = {
        "site_results": {
            "espece_a": {
                "rut_zones_composite": {
                    "valid": False,
                    "reason": "all_three_pillars_invalid",
                },
            },
        },
    }
    out = _extract_rut_per_site(fake)
    assert out["espece_a"]["valid"] is False
    assert "all_three_pillars_invalid" in (
        out["espece_a"]["reason"])


def test_phase_xxx_untricicies_compute_rut_output_deferred():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        _compute_rut_zones_output,
    )
    out = _compute_rut_zones_output({
        "valid": False,
        "reason": "missing",
    })
    assert out["value"] is None
    assert out["regime"] == "DEFERRED_NO_VALID_RUT_DATA"


def test_phase_xxx_untricicies_compute_rut_output_valid():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        _compute_rut_zones_output,
    )
    out = _compute_rut_zones_output({
        "valid": True,
        "composite_score_0_100": 88.7,
        "regime": "RUT_ZONE_HIGH_PROBABILITY",
        "n_pillars_valid": 3,
        "doctrinal_caveat": (
            "TEMPORAL PROXY composite (Bronson + "
            "Hebblewhite + Bowyer)"),
        "components": {"photoperiod_score": 80.0},
    })
    assert out["value"] == 88.7
    assert out["regime"] == "RUT_ZONE_HIGH_PROBABILITY"
    assert out["unit"] == (
        "rut_zones_temporal_proxy_score_0_100")
    assert "Bronson_1989_MammalianReprod" in (
        out["primary_references"])


def test_phase_xxx_untricicies_overlay_path_correct():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        HABITAT_FINAL_PATH,
        HABITAT_FINAL_ROOT,
    )
    assert "habitat_final_merge" in str(HABITAT_FINAL_ROOT)
    assert HABITAT_FINAL_PATH.name == (
        "habitat_outputs_final_merge_overlay.json")


def test_phase_xxx_untricicies_status_doctrinal_keys():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        get_habitat_final_merge_status,
    )
    s = get_habitat_final_merge_status()
    assert s.get("v30_lock") == "INVIOLÉ"
    assert s.get("ordre") == (
        "P7_HABITAT_OUTPUTS_FINAL_MERGE_Ω")


def test_phase_xxx_untricicies_overlay_state_when_present():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        HABITAT_FINAL_PATH,
    )
    if not HABITAT_FINAL_PATH.exists():
        pytest.skip("Aucun final merge encore exécuté.")
    state = json.loads(
        HABITAT_FINAL_PATH.read_text(encoding="utf-8"))
    assert state.get("v30_lock") == "INVIOLÉ"
    assert "history" in state


def test_phase_xxx_untricicies_v3_inheritance_present():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        HABITAT_FINAL_PATH,
    )
    if not HABITAT_FINAL_PATH.exists():
        pytest.skip("Aucun final merge encore exécuté.")
    state = json.loads(
        HABITAT_FINAL_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History final vide.")
    last = state["history"][-1]
    v3_inh = last.get("v3_inheritance") or {}
    assert "v3_recompute_v3_sha256" in v3_inh
    assert "v3_v2_recompute_sha256" in v3_inh
    assert "v3_v2_hooks_manifests_inherited" in v3_inh


def test_phase_xxx_untricicies_rut_zones_present_per_site():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        HABITAT_FINAL_PATH,
    )
    if not HABITAT_FINAL_PATH.exists():
        pytest.skip("Aucun final merge encore exécuté.")
    state = json.loads(
        HABITAT_FINAL_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History final vide.")
    last = state["history"][-1]
    per_site = last.get("per_site_outputs_final") or {}
    if not per_site:
        pytest.skip("Aucun site final.")
    for site_name, sd in per_site.items():
        outputs = sd.get("computed_outputs") or {}
        assert "rut_zones" in outputs
        assert "pressure_sensitive_zones" in outputs


def test_phase_xxx_untricicies_outputs_deferred_only_2():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        HABITAT_FINAL_PATH,
    )
    if not HABITAT_FINAL_PATH.exists():
        pytest.skip("Aucun final merge encore exécuté.")
    state = json.loads(
        HABITAT_FINAL_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History final vide.")
    last = state["history"][-1]
    deferred = last.get(
        "outputs_still_deferred_anti_generique_strict_final"
    ) or {}
    assert len(deferred) == 2
    assert "feeding_zones_FULL" in deferred
    assert "rut_zones" not in deferred
    assert "pressure_sensitive_zones" not in deferred


def test_phase_xxx_untricicies_verdict_when_full():
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        HABITAT_FINAL_PATH,
    )
    if not HABITAT_FINAL_PATH.exists():
        pytest.skip("Aucun final merge encore exécuté.")
    state = json.loads(
        HABITAT_FINAL_PATH.read_text(encoding="utf-8"))
    if not state.get("history"):
        pytest.skip("History final vide.")
    last = state["history"][-1]
    verdict = last.get("verdict") or ""
    assert (
        "10_OF_12" in verdict
        or "PARTIAL" in verdict
        or "REJECTED" in verdict
        or "INSUFFICIENT" in verdict)
    if "10_OF_12" in verdict:
        assert last.get("anti_generique_strict") is True
        assert last.get("fusion_add_only") is True
        assert last.get("v30_lock") == "INVIOLÉ"
