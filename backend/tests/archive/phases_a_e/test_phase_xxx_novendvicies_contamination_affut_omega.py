"""Tests anti-régression — contamination_affut_dependency_omega.py (V12).

NOMS NEUTRES : aucun mot dans BCE_4X_EXCLUDED_KEYWORDS.
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
"""
from __future__ import annotations

import json
import hashlib

import pytest


def test_phase_xxx_novendvicies_module_imports_clean():
    from engines.v8_institutional.especes import (
        contamination_affut_dependency_omega as mod)
    assert hasattr(mod, "DOCTRINE_V12_MASTER")
    assert hasattr(mod, "URBAN_INDUSTRIAL_CATEGORIES_R5")
    assert hasattr(mod, "evaluate_affut_potentiel_for_tile")
    assert hasattr(mod, "detect_anomaly_a3")
    assert hasattr(mod, "audit_tiles_dependency")
    assert hasattr(mod,
                    "activate_contamination_affut_dependency_hook")
    assert hasattr(mod,
                    "get_contamination_affut_dependency_hook_status")


def test_phase_xxx_novendvicies_doctrine_v12_master_complete():
    """Doctrine V12 doit contenir R1-R6 + audit A1-A4 + M1-M2."""
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        DOCTRINE_V12_MASTER,
    )
    assert DOCTRINE_V12_MASTER["version"] == "V12-MAÎTRE"
    assert DOCTRINE_V12_MASTER["auteur"] == (
        "Commandant Steeve-Max")
    for key in ("R1", "R2", "R3", "R4", "R5", "R6"):
        assert key in DOCTRINE_V12_MASTER["regles"]
    for key in ("A1", "A2", "A3", "A4"):
        assert key in DOCTRINE_V12_MASTER["audit"]
    for key in ("M1", "M2"):
        assert key in DOCTRINE_V12_MASTER["messages_frontend"]


def test_phase_xxx_novendvicies_checksum_v12_doctrinal_correct():
    """SHA256(CONTAMINATION_AFFUT_DEPENDENCY_V12) doit matcher constant."""
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        DOCTRINE_V12_MASTER,
    )
    expected = DOCTRINE_V12_MASTER["checksum_expected_sha256"]
    actual = hashlib.sha256(
        b"CONTAMINATION_AFFUT_DEPENDENCY_V12").hexdigest()
    assert actual == expected


def test_phase_xxx_novendvicies_r5_urban_forces_false():
    """R5 : landuse=urban force AFFUT_POTENTIEL=False."""
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        evaluate_affut_potentiel_for_tile,
    )
    res = evaluate_affut_potentiel_for_tile({
        "landuse_categories": ["urban", "residential"],
    })
    assert res["affut_potentiel"] is False
    assert res["rule_triggered"] == "R5"
    assert res["contamination_layer"]["visible"] is False


def test_phase_xxx_novendvicies_r5_industrial_forces_false():
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        evaluate_affut_potentiel_for_tile,
    )
    res = evaluate_affut_potentiel_for_tile({
        "landuse_categories": ["industrial", "factory"],
    })
    assert res["affut_potentiel"] is False
    assert res["rule_triggered"] == "R5"


def test_phase_xxx_novendvicies_r5_motorway_forces_false():
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        evaluate_affut_potentiel_for_tile,
    )
    res = evaluate_affut_potentiel_for_tile({
        "landuse_categories": ["motorway"],
    })
    assert res["affut_potentiel"] is False
    assert res["rule_triggered"] == "R5"


def test_phase_xxx_novendvicies_r3_forest_continuity_passes():
    """R3 : forest continuity high + biological mask + low buildings."""
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        evaluate_affut_potentiel_for_tile,
    )
    res = evaluate_affut_potentiel_for_tile({
        "landuse_categories": ["forest"],
        "forest_continuity_score": 0.85,
        "building_density_per_km2": 5.0,
        "habitat_favorable_distance_m": 500,
        "biological_mask_active": True,
        "fragmentation_index_0_1": 0.7,
    })
    assert res["affut_potentiel"] is True
    assert res["rule_triggered"] == "R3"
    assert res["contamination_layer"]["visible"] is True


def test_phase_xxx_novendvicies_r4_no_potential_below_50():
    """R4 : score < 50 → AFFUT_POTENTIEL=False, contamination=NULL."""
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        evaluate_affut_potentiel_for_tile,
    )
    res = evaluate_affut_potentiel_for_tile({
        "landuse_categories": ["meadow"],
        "forest_continuity_score": 0.1,
        "building_density_per_km2": 80,
    })
    assert res["affut_potentiel"] is False
    assert res["rule_triggered"] == "R4"
    assert res["contamination_layer"]["data"] is None


def test_phase_xxx_novendvicies_a3_anomaly_detected():
    """A3 : contamination=visible dans urban = ANOMALY CRITICAL."""
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        detect_anomaly_a3,
    )
    anomaly = detect_anomaly_a3(
        tile_attributes={"landuse_categories": ["urban"]},
        contamination_layer_state={"visible": True},
    )
    assert anomaly is not None
    assert anomaly["anomaly_type"] == (
        "A3_CONTAMINATION_IN_URBAN_SECTOR")
    assert anomaly["severity"] == "CRITICAL"
    assert anomaly["ci_blocking"] is True


def test_phase_xxx_novendvicies_a3_no_anomaly_clean_tile():
    """A3 : contamination=hidden in urban → no anomaly."""
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        detect_anomaly_a3,
    )
    anomaly = detect_anomaly_a3(
        tile_attributes={"landuse_categories": ["urban"]},
        contamination_layer_state={"visible": False},
    )
    assert anomaly is None


def test_phase_xxx_novendvicies_audit_batch_blocks_ci_on_violation():
    """Audit batch détecte violation et persiste bloquant CI."""
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        audit_tiles_dependency,
    )
    result = audit_tiles_dependency(
        tiles=[
            {"tile_id": "tile_clean",
             "attributes": {
                 "landuse_categories": ["forest"],
                 "forest_continuity_score": 0.9,
                 "building_density_per_km2": 0.0,
                 "habitat_favorable_distance_m": 100,
                 "biological_mask_active": True,
                 "fragmentation_index_0_1": 0.8,
             }},
            {"tile_id": "tile_clean_urban",
             "attributes": {
                 "landuse_categories": ["urban"],
             }},
        ],
        persist_violations=False)
    assert result["n_tiles_audited"] == 2
    # Pas de violation A3 ici car évaluations correctes → contam masquée
    assert result["n_violations_a3"] == 0
    assert result["ci_blocking_required"] is False


def test_phase_xxx_novendvicies_activate_rejects_bad_checksum():
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        activate_contamination_affut_dependency_hook,
    )
    res = activate_contamination_affut_dependency_hook(
        activation_input_string="WRONG_INPUT_STRING",
        persist=False)
    assert res["activated"] is False
    assert "REJECTED" in res["verdict"]


def test_phase_xxx_novendvicies_status_keys_doctrinal():
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        get_contamination_affut_dependency_hook_status,
    )
    s = get_contamination_affut_dependency_hook_status()
    assert s.get("v30_lock") == "INVIOLÉ"
    assert "current_status" in s


def test_phase_xxx_novendvicies_overlay_persisted_when_present():
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        CONTAM_AFFUT_HOOK_PATH,
    )
    if not CONTAM_AFFUT_HOOK_PATH.exists():
        pytest.skip("Aucune activation persistée encore.")
    state = json.loads(
        CONTAM_AFFUT_HOOK_PATH.read_text(encoding="utf-8"))
    assert state.get("v30_lock") == "INVIOLÉ"
    assert "history" in state


def test_phase_xxx_novendvicies_urban_categories_r5_not_empty():
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        URBAN_INDUSTRIAL_CATEGORIES_R5,
    )
    for must in ("urban", "residential", "commercial",
                  "industrial", "highway", "motorway"):
        assert must in URBAN_INDUSTRIAL_CATEGORIES_R5
