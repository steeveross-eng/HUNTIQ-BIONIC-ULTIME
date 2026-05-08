"""Tests anti-régression — P14 (merkle_tree_anchor) + Premium V7.

NOMS NEUTRES : aucun mot dans BCE_4X_EXCLUDED_KEYWORDS.
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
"""
from __future__ import annotations

import hashlib
import json

import pytest


# ═════════════════════════════════════════════════════════════════════════
# P14 MERKLE_TREE_ANCHOR
# ═════════════════════════════════════════════════════════════════════════
def test_phase_xxx_quintricicies_p14_module_imports():
    from engines.v8_institutional.especes import (
        merkle_tree_anchor_omega as mod)
    assert hasattr(mod, "build_merkle_tree")
    assert hasattr(mod, "compute_merkle_audit_path")
    assert hasattr(mod, "verify_merkle_audit_path")
    assert hasattr(mod, "build_and_anchor_merkle_tree")
    assert hasattr(mod, "activate_merkle_tree_anchor_hook")


def test_phase_xxx_quintricicies_merkle_single_leaf():
    """1 leaf → root = leaf (cas dégénéré)."""
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        build_merkle_tree,
    )
    leaf = "a" * 64
    res = build_merkle_tree([leaf])
    assert res["valid"] is True
    assert res["merkle_root_hex"] == leaf
    assert res["n_leaves"] == 1


def test_phase_xxx_quintricicies_merkle_two_leaves():
    """2 leaves → root = SHA256(leaf1 || leaf2)."""
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        build_merkle_tree,
    )
    leaf_a = "0" * 64
    leaf_b = "1" * 64
    res = build_merkle_tree([leaf_a, leaf_b])
    expected = hashlib.sha256(
        bytes.fromhex(leaf_a) + bytes.fromhex(leaf_b)
    ).hexdigest()
    assert res["valid"] is True
    assert res["merkle_root_hex"] == expected


def test_phase_xxx_quintricicies_merkle_invalid_leaf():
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        build_merkle_tree,
    )
    res = build_merkle_tree(["short"])
    assert res["valid"] is False
    assert "leaf_invalid_length" in res["reason"]


def test_phase_xxx_quintricicies_merkle_empty():
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        build_merkle_tree,
    )
    res = build_merkle_tree([])
    assert res["valid"] is False
    assert res["reason"] == "empty_leaves"


def test_phase_xxx_quintricicies_merkle_audit_path_verifiable():
    """Build tree + audit path + verify → True."""
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        build_merkle_tree, compute_merkle_audit_path,
        verify_merkle_audit_path,
    )
    leaves = [hashlib.sha256(
        f"leaf_{i}".encode()).hexdigest()
        for i in range(7)]
    tree = build_merkle_tree(leaves)
    for i in range(len(leaves)):
        ap = compute_merkle_audit_path(i, tree["leaves_hex"])
        assert ap["valid"] is True
        valid = verify_merkle_audit_path(
            leaf_hex=leaves[i],
            audit_path=ap["audit_path"],
            expected_root_hex=tree["merkle_root_hex"])
        assert valid is True, f"Audit path failed for leaf {i}"


def test_phase_xxx_quintricicies_merkle_audit_path_tampered_rejected():
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        build_merkle_tree, compute_merkle_audit_path,
        verify_merkle_audit_path,
    )
    leaves = [hashlib.sha256(
        f"leaf_{i}".encode()).hexdigest()
        for i in range(4)]
    tree = build_merkle_tree(leaves)
    ap = compute_merkle_audit_path(0, tree["leaves_hex"])
    # Tamper sibling hash
    tampered_path = list(ap["audit_path"])
    tampered_path[0] = {
        **tampered_path[0],
        "sibling_hex": "f" * 64,
    }
    valid = verify_merkle_audit_path(
        leaf_hex=leaves[0],
        audit_path=tampered_path,
        expected_root_hex=tree["merkle_root_hex"])
    assert valid is False


def test_phase_xxx_quintricicies_resolve_ots_binary():
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        _resolve_ots_binary,
    )
    binary = _resolve_ots_binary()
    assert binary is None or binary.endswith("ots")


def test_phase_xxx_quintricicies_collect_doctrinal_leaves():
    """collect_doctrinal_sha256_leaves doit retourner liste."""
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        collect_doctrinal_sha256_leaves,
    )
    leaves = collect_doctrinal_sha256_leaves()
    assert isinstance(leaves, list)
    for le in leaves:
        assert "logical_key" in le
        assert "sha256_hex" in le
        assert len(le["sha256_hex"]) == 64


def test_phase_xxx_quintricicies_p14_activate_unknown_sha():
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        activate_merkle_tree_anchor_hook,
    )
    fake = "0" * 64
    res = activate_merkle_tree_anchor_hook(
        manifest_sha256=fake, persist=False)
    assert res["activated"] is False
    assert "REJECTED" in res["verdict"]


def test_phase_xxx_quintricicies_p14_overlay_when_present():
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        MERKLE_VALIDATION_PATH,
    )
    if not MERKLE_VALIDATION_PATH.exists():
        pytest.skip("Aucun overlay P14.")
    state = json.loads(
        MERKLE_VALIDATION_PATH.read_text(encoding="utf-8"))
    assert state.get("v30_lock") == "INVIOLÉ"


# ═════════════════════════════════════════════════════════════════════════
# Premium V7
# ═════════════════════════════════════════════════════════════════════════
def test_phase_xxx_quintricicies_premium_module_imports():
    from engines.v8_institutional.especes import (
        premium_reports_v7_omega as mod)
    assert hasattr(mod, "generate_premium_report")
    assert hasattr(mod, "get_premium_reports_status")
    assert hasattr(mod, "SPECIES_DOCTRINAL")
    assert hasattr(mod, "LAYERS_DOCTRINAL")
    assert hasattr(mod, "MODULES_PREMIUM_15")
    assert hasattr(mod, "BEHAVIOR_MATRIX_LAYER_TO_MODULES")
    assert hasattr(mod, "ULTIMATE_MODULE_BY_LAYER")


def test_phase_xxx_quintricicies_premium_5_species_present():
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        SPECIES_DOCTRINAL,
    )
    for sp in ("cerf", "orignal", "ours", "dindon", "wapiti"):
        assert sp in SPECIES_DOCTRINAL


def test_phase_xxx_quintricicies_premium_6_layers():
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        LAYERS_DOCTRINAL, ULTIMATE_MODULE_BY_LAYER,
        BEHAVIOR_MATRIX_LAYER_TO_MODULES,
    )
    expected = ["saline", "alimentation", "rut",
                "repos", "affut", "corridor"]
    assert LAYERS_DOCTRINAL == expected
    for layer in expected:
        assert layer in ULTIMATE_MODULE_BY_LAYER
        assert layer in BEHAVIOR_MATRIX_LAYER_TO_MODULES


def test_phase_xxx_quintricicies_premium_15_modules():
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        MODULES_PREMIUM_15,
    )
    assert len(MODULES_PREMIUM_15) == 15


def test_phase_xxx_quintricicies_premium_invalid_species():
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        generate_premium_report,
    )
    with pytest.raises(ValueError, match="SPECIES_INVALID"):
        generate_premium_report(
            species="dragon", waypoint_lat=46.0,
            waypoint_lon=-71.0, layer="alimentation",
            season="summer", persist=False)


def test_phase_xxx_quintricicies_premium_invalid_layer():
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        generate_premium_report,
    )
    with pytest.raises(ValueError, match="LAYER_INVALID"):
        generate_premium_report(
            species="cerf", waypoint_lat=46.0,
            waypoint_lon=-71.0, layer="invalid_layer",
            season="summer", persist=False)


def test_phase_xxx_quintricicies_premium_invalid_radius():
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        generate_premium_report,
    )
    with pytest.raises(ValueError, match="RADIUS_INVALID"):
        generate_premium_report(
            species="cerf", waypoint_lat=46.0,
            waypoint_lon=-71.0, layer="alimentation",
            season="summer", radius_m=999, persist=False)


def test_phase_xxx_quintricicies_premium_generates_full_report():
    """Genère rapport complet avec tous les blocs."""
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        generate_premium_report,
    )
    report = generate_premium_report(
        species="cerf",
        waypoint_lat=46.8131, waypoint_lon=-71.2075,
        layer="alimentation", season="summer",
        waypoint_id="WPT_TEST_PYTEST",
        radius_m=500, persist=False)
    assert "RAPPORT PREMIUM" in report["header_dynamic"]
    assert "CERF" in report["header_dynamic"]
    assert report["report_sha256"]
    assert len(report["report_sha256"]) == 64
    assert report["v30_lock"] == "INVIOLÉ"
    # Tous les blocs présents
    for block in (
            "block_1_summary", "block_2_premium_modules",
            "block_3_ultimate_module", "block_4_supra_recipes",
            "block_5_before_after", "block_6_ultimate_action"):
        assert block in report
    # Modules ULTIME présent
    ult = report["block_3_ultimate_module"]
    assert ult["ultimate_module_id"] == "ALIMENTATION_ULTIME"
    assert ult["mini_report_avant_apres"]["phrase_impact"]


def test_phase_xxx_quintricicies_premium_anti_generique_metadata():
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        generate_premium_report,
    )
    report = generate_premium_report(
        species="orignal", waypoint_lat=47.2,
        waypoint_lon=-70.27, layer="rut",
        season="autumn", persist=False)
    assert report["anti_generique_strict"] is True
    assert report["fusion_add_only"] is True
    assert report["drift_zero"] is True
    assert report["no_engine_recompute_triggered"] is True


def test_phase_xxx_quintricicies_premium_status_keys():
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        get_premium_reports_status,
    )
    s = get_premium_reports_status()
    assert s["v30_lock"] == "INVIOLÉ"
    assert s["current_status"] == "OPERATIONAL"
    assert s["n_species_supported"] == 5
    assert s["n_layers_supported"] == 6
    assert s["n_modules_premium"] == 15
    assert s["n_modules_ultime"] == 6


def test_phase_xxx_quintricicies_premium_modules_filtered_by_layer():
    """Couche affut doit avoir AnalyseAffuts dans modules activés."""
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        BEHAVIOR_MATRIX_LAYER_TO_MODULES,
    )
    assert "AnalyseAffuts" in (
        BEHAVIOR_MATRIX_LAYER_TO_MODULES["affut"])
    assert "FenetresRut" in (
        BEHAVIOR_MATRIX_LAYER_TO_MODULES["rut"])
    assert "FenetresAlimentation" in (
        BEHAVIOR_MATRIX_LAYER_TO_MODULES["alimentation"])
    assert "Corridors" in (
        BEHAVIOR_MATRIX_LAYER_TO_MODULES["corridor"])
