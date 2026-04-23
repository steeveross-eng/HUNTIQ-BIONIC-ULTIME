"""
test_x200_p3b_human_predictive.py
==================================
Phase : PHASE_X200_P3B_HUMAN_PREDICTIVE_Ω
Commandant STEEVE-MAX

Vérifie :
  - AXE 1 : injection des `human_zones` (OSM-like, signature
            `_p3b_source=HUMAN_ZONES_Ω_X200_P3B`) dans le builder P3,
            effet modulateur sur `pressure_human`.
  - AXE 2 : échantillonnage multi-points déterministe (1/3/5 selon
            longueur) de `predictive_omega` + moyenne pondérée kernel
            centré + traçabilité `samples`.
"""
import pytest


# ═══════════════════════════════════════════════════════════════════════
# AXE 1 — HUMAN_ZONES
# ═══════════════════════════════════════════════════════════════════════
def test_human_zones_present_and_signed():
    from engines.post_smoothing.terrain_signals_builder import build_institutional_signals
    s = build_institutional_signals(48.206657, -68.382422)
    assert s["_p3b_source"] == "HUMAN_ZONES_Ω_X200_P3B"
    hz = s["human_zones"]
    assert 5 <= len(hz) <= 8
    for z in hz:
        assert z["kind"] in ("road", "building", "infrastructure")
        assert z["buffer_m"] > 0
        assert 0.0 <= z["weight"] <= 1.0
        assert "lat" in z and "lng" in z


def test_human_zones_deterministic():
    from engines.post_smoothing.terrain_signals_builder import build_institutional_signals
    s1 = build_institutional_signals(48.206657, -68.382422)
    s2 = build_institutional_signals(48.206657, -68.382422)
    assert s1["human_zones"] == s2["human_zones"]


def test_pressure_human_declines_near_road(monkeypatch):
    """Un path traversant le buffer d'une route voit sa pression humaine chuter."""
    from engines.post_smoothing.terrain_signals_builder import (
        build_institutional_signals, derive_corridor_subscores,
    )
    s = build_institutional_signals(48.206657, -68.382422)
    road = [z for z in s["human_zones"] if z["kind"] == "road"][0]
    far_path  = {"id": "far",  "path": [[48.200, -68.370], [48.201, -68.371], [48.202, -68.372]]}
    near_path = {"id": "near", "path": [
        [road["lat"], road["lng"]],
        [road["lat"] + 0.0002, road["lng"] + 0.0002],
        [road["lat"] + 0.0004, road["lng"] + 0.0004],
    ]}
    ss_far  = derive_corridor_subscores(far_path, s)
    ss_near = derive_corridor_subscores(near_path, s)
    assert ss_near["pressure_human"] < ss_far["pressure_human"]


def test_human_zones_modulation_affects_level_distribution(monkeypatch):
    """Les corridors exposés à des zones humaines doivent pouvoir être déclassés."""
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_HISTORICAL_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXPLICIT")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXTERNAL-INFLOW")
    monkeypatch.setenv("P3_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P3_COMMANDANT_TOKEN", "STEEVE-MAX-X200-P3-EXPLICIT")
    from engines.post_smoothing.terrain_signals_builder import build_institutional_signals
    from engines.post_smoothing.p1_preparation import apply_p1_suite_to_bundle
    ts = build_institutional_signals(48.206657, -68.382422)
    # Corridor A loin des zones humaines
    a = {"id": "far_a", "path": [[48.210, -68.390], [48.211, -68.391], [48.212, -68.392]],
         "vital_zone_connections": [{"type": "salines"}, {"type": "repos"}]}
    # Corridor B traversant une route
    road = [z for z in ts["human_zones"] if z["kind"] == "road"][0]
    b = {"id": "near_b", "path": [
            [road["lat"], road["lng"]],
            [road["lat"] + 0.0001, road["lng"] + 0.0001],
            [road["lat"] + 0.0002, road["lng"] + 0.0002],
        ],
        "vital_zone_connections": [{"type": "salines"}, {"type": "repos"}]}
    bundle = {"terrain_signals": ts, "corridors": [a, b]}
    out = apply_p1_suite_to_bundle(bundle)
    # Le corridor B (proche route) doit avoir un score post-V30 strictement ≤ à A
    score_a = out["corridors"][0]["post_v30_bio_score_0_100"]
    score_b = out["corridors"][1]["post_v30_bio_score_0_100"]
    assert score_b <= score_a


# ═══════════════════════════════════════════════════════════════════════
# AXE 2 — PREDICTIVE MULTI-POINTS
# ═══════════════════════════════════════════════════════════════════════
def _enable_p2(monkeypatch):
    monkeypatch.setenv("P2_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P2_COMMANDANT_TOKEN", "STEEVE-MAX-X200-P2-EXPLICIT")


def test_sample_indices_deterministic_1_3_5():
    from engines.post_smoothing.predictive_integration import _sample_indices
    assert _sample_indices(10, 1) == [5]
    assert _sample_indices(10, 3) == [2, 5, 7]
    assert _sample_indices(10, 5) == [1, 3, 5, 6, 8]


def test_choose_n_samples_by_path_length():
    from engines.post_smoothing.predictive_integration import _choose_n_samples
    short = [[48.0, -68.0], [48.0001, -68.0001]]  # très court
    mid   = [[48.0, -68.0], [48.002, -68.002]]    # ~300 m
    long  = [[48.0, -68.0], [48.006, -68.006]]    # ~900 m
    assert _choose_n_samples(short) == 1
    assert _choose_n_samples(mid)   == 3
    assert _choose_n_samples(long)  == 5


def test_multipoint_weights_sum_to_1():
    from engines.post_smoothing.predictive_integration import MULTIPOINT_WEIGHTS
    for n, ws in MULTIPOINT_WEIGHTS.items():
        assert len(ws) == n
        assert abs(sum(ws) - 1.0) < 1e-9


def test_short_path_uses_single_sample(monkeypatch):
    _enable_p2(monkeypatch)
    from engines.post_smoothing.predictive_integration import apply_predictive_to_corridor
    c = {"id": "c", "path": [[48.206, -68.382], [48.2061, -68.3821]]}
    out = apply_predictive_to_corridor(c, species="orignal", hour=7, iso_date="2026-10-01")
    comp = out["corridor_probability_components"]
    assert comp["n_samples"] == 1
    assert comp["aggregation_method"].startswith("weighted_mean")
    assert len(comp["samples"]) == 1


def test_long_path_uses_five_samples(monkeypatch):
    _enable_p2(monkeypatch)
    from engines.post_smoothing.predictive_integration import apply_predictive_to_corridor
    # Path linéaire de ~1 km
    path = [[48.0 + i * 0.001, -68.0] for i in range(10)]
    c = {"id": "c_long", "path": path}
    out = apply_predictive_to_corridor(c, species="orignal", hour=7, iso_date="2026-10-01")
    comp = out["corridor_probability_components"]
    assert comp["n_samples"] == 5
    assert comp["path_length_m"] > 800
    samples = comp["samples"]
    assert len(samples) == 5
    # Traçabilité stricte : ordres 0..4, weights cohérents avec la table
    for i, s in enumerate(samples):
        assert s["order"] == i
        assert 0 <= s["path_index"] < len(path)


def test_multipoint_aggregation_matches_weighted_mean(monkeypatch):
    """L'agrégat doit égaler la moyenne pondérée des échantillons."""
    _enable_p2(monkeypatch)
    from engines.post_smoothing.predictive_integration import apply_predictive_to_corridor
    path = [[48.0 + i * 0.0006, -68.0] for i in range(8)]
    c = {"id": "c", "path": path}
    out = apply_predictive_to_corridor(c, species="orignal", hour=7, iso_date="2026-10-01")
    comp = out["corridor_probability_components"]
    probs = [s["probability_0_1"] for s in comp["samples"]]
    ws    = [s["weight"]          for s in comp["samples"]]
    expected = sum(p * w for p, w in zip(probs, ws)) / sum(ws)
    # `predictive_raw_0_1` (arrondi 4 décimales) doit être proche
    assert abs(comp["predictive_raw_0_1"] - round(expected, 4)) < 1e-3


def test_multipoint_reproducibility(monkeypatch):
    _enable_p2(monkeypatch)
    from engines.post_smoothing.predictive_integration import apply_predictive_to_corridor
    path = [[48.0 + i * 0.00075, -68.0] for i in range(10)]
    c = {"id": "c", "path": path}
    a = apply_predictive_to_corridor(c, species="orignal", hour=7, iso_date="2026-10-01")
    b = apply_predictive_to_corridor(c, species="orignal", hour=7, iso_date="2026-10-01")
    assert a["corridor_probability_omega"] == b["corridor_probability_omega"]
    assert a["corridor_probability_components"]["samples"] == b["corridor_probability_components"]["samples"]


def test_p3b_does_not_import_v30(monkeypatch):
    _enable_p2(monkeypatch)
    import sys
    before = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    from engines.post_smoothing.predictive_integration import apply_predictive_to_corridor
    path = [[48.0 + i * 0.0005, -68.0] for i in range(10)]
    apply_predictive_to_corridor({"id": "c", "path": path},
                                  species="orignal", hour=7, iso_date="2026-10-01")
    after = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    assert before == after
