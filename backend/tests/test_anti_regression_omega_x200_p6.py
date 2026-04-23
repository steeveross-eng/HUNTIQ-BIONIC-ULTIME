"""
tests/test_anti_regression_omega_x200_p6.py — PHASE_X200_P6_ANTI_RÉGRESSION_Ω
=============================================================================
Verrous :
- triple verrou P6 fonctionnel
- classification violations -> 12 sous-normes X150
- métriques continues déterministes
- audit matrix cohérente
- reset sous token Commandant uniquement
- V30 non modifié (hook non intrusif)
"""
from __future__ import annotations

import os
import sys

# Chemin module backend
sys.path.insert(0, "/app/backend")

# S'assurer que l'autorisation est ON pour les tests
os.environ.setdefault("P6_ANTI_REGRESSION_AUTHORIZED_BY_COMMANDANT", "true")
os.environ.setdefault(
    "P6_ANTI_REGRESSION_COMMANDANT_TOKEN",
    "STEEVE-MAX-X200-P6-EXPLICIT",
)

from engines.post_smoothing import anti_regression_omega as ar  # noqa: E402


def _verdict(accepted: bool, violations_per_block):
    return {
        "accepted": accepted,
        "geometry": {"violations": violations_per_block.get("geometry", [])},
        "terrain":  {"violations": violations_per_block.get("terrain",  [])},
        "ecology":  {"violations": violations_per_block.get("ecology",  [])},
        "species":  {"violations": violations_per_block.get("species",  [])},
    }


def test_triple_verrou_p6_authorized():
    auth = ar.is_p6_authorized()
    assert auth["authorized"] is True
    assert auth["flag_enabled"] is True
    assert auth["env_flag_ok"] is True
    assert auth["token_ok"] is True


def test_12_sub_normes_declared():
    # Contrat frontend runtimeBeaconOmega.js : 12 sous-normes nommées
    assert len(ar.SUB_NORMES_X150) == 12
    expected_keys = {
        "geometry_catmullrom_25_30", "segment_max_20m", "angle_max_45deg",
        "curvature_progressive", "no_simplification",
        "no_artificial_interpolation", "no_radial_star_shape",
        "terrainaware_functional_radius", "no_water_below_20m",
        "no_slope_above_35deg", "ecological_mosaic_respected",
        "human_zones_avoided",
    }
    assert set(ar.SUB_NORMES_X150.keys()) == expected_keys


def test_classification_matches_real_renduomega_strings():
    # Les chaînes exactes produites par engines/post_smoothing/renduomega.py
    assert "segment_max_20m" in ar._classify_violation_text("max_segment_m=23.5 > 20.0")
    assert "angle_max_45deg" in ar._classify_violation_text("max_angle_deg=106.1 > 45.0")
    assert "no_radial_star_shape" in ar._classify_violation_text("radial_or_straight_shape_detected")
    assert "no_simplification" in ar._classify_violation_text("length_m=13.4 < 100.0")
    assert "no_slope_above_35deg" in ar._classify_violation_text("slope_deg=40.0 > 35.0")
    assert "no_water_below_20m" in ar._classify_violation_text("min_dist_water_m=12.5 < 20.0")
    assert "human_zones_avoided" in ar._classify_violation_text("human_zone_violation penalty=0.7")
    assert "ecological_mosaic_respected" in ar._classify_violation_text("contamination_violation min_dist=80")
    assert "terrainaware_functional_radius" in ar._classify_violation_text("functional_radius_m=313.5 hors [420.0-780.0]")


def test_unknown_violation_goes_to_uncategorized():
    assert ar._classify_violation_text("totally_unknown_thing") == ["_uncategorized"]


def test_record_and_metrics_end_to_end():
    ar.reset_ledger()
    # 2 corridors, violations multiples
    ar.record_corridor_verdict(
        {"id": "c1"},
        _verdict(False, {"geometry": ["max_segment_m=25 > 20.0",
                                      "max_angle_deg=60 > 45.0"]}),
    )
    ar.record_corridor_verdict(
        {"id": "c2"},
        _verdict(False, {"terrain": ["min_dist_water_m=12.5 < 20.0"],
                         "ecology": ["human_zone_violation penalty=0.8"]}),
    )
    ar.record_corridor_verdict(
        {"id": "c3"},
        _verdict(True, {}),  # aucun vice -> accepté, rien à compter
    )

    snap = ar.get_ledger_snapshot()
    assert snap["summary"]["total_corridors_observed"] == 3
    assert snap["summary"]["total_accepted"] == 1
    assert snap["summary"]["total_rejected"] == 2
    sn = snap["sub_normes"]
    assert sn["segment_max_20m"]["violations"] == 1
    assert sn["angle_max_45deg"]["violations"] == 1
    assert sn["no_water_below_20m"]["violations"] == 1
    assert sn["human_zones_avoided"]["violations"] == 1


def test_path_entry_touched_counted_once_per_sub_norme():
    ar.reset_ledger()
    ar.record_corridor_verdict(
        {"id": "cX"},
        _verdict(False, {"geometry": [
            "max_segment_m=25 > 20.0", "max_segment_m=30 > 20.0",
        ]}),
    )
    snap = ar.get_ledger_snapshot()
    assert snap["sub_normes"]["segment_max_20m"]["violations"] == 2
    assert snap["sub_normes"]["segment_max_20m"]["corridors_touched"] == 1


def test_audit_matrix_per_item():
    ar.reset_ledger()
    ar.record_corridor_verdict(
        {"id": "cA"},
        _verdict(False, {"geometry": ["max_angle_deg=55 > 45.0"]}),
    )
    ar.record_corridor_verdict(
        {"id": "cB"},
        _verdict(False, {"geometry": ["max_angle_deg=80 > 45.0"],
                         "ecology": ["human_zone_violation penalty=0.9"]}),
    )
    m = ar.build_audit_matrix()
    assert m["corridors_count"] == 2
    assert m["matrix"]["cA"] == {"angle_max_45deg": 1}
    assert m["matrix"]["cB"]["angle_max_45deg"] == 1
    assert m["matrix"]["cB"]["human_zones_avoided"] == 1


def test_events_limit_respected():
    ar.reset_ledger()
    # On dépasse largement 2000
    for i in range(ar._MAX_EVENTS + 50):
        ar.record_corridor_verdict(
            {"id": f"c{i}"},
            _verdict(False, {"geometry": ["max_angle_deg=50 > 45.0"]}),
        )
    assert len(ar._EVENTS) == ar._MAX_EVENTS


def test_reset_ledger_clears_everything():
    ar.reset_ledger()
    ar.record_corridor_verdict(
        {"id": "tmp"},
        _verdict(False, {"geometry": ["max_segment_m=21 > 20.0"]}),
    )
    assert ar.get_ledger_snapshot()["summary"]["total_corridors_observed"] == 1
    ar.reset_ledger()
    snap = ar.get_ledger_snapshot()
    assert snap["summary"]["total_corridors_observed"] == 0
    assert snap["events_kept"] == 0


def test_v30_not_modified_by_hook():
    # Le hook ne doit accéder à aucun engine verrouillé. On vérifie que
    # le registre V30 est inchangé avant / après un record.
    from engines.v8_institutional import registry_lock_omega as r
    before = r._registry_hash()
    ar.record_corridor_verdict(
        {"id": "cV30"},
        _verdict(False, {"geometry": ["max_angle_deg=60 > 45.0"]}),
    )
    after = r._registry_hash()
    assert before == after
