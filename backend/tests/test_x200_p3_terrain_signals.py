"""
test_x200_p3_terrain_signals.py
================================
Phase : PHASE_X200_P3_OPTIMISATION_Ω
Commandant STEEVE-MAX

Vérifie :
  - Triple verrou P3 (flag + env + token STEEVE-MAX-X200-P3-EXPLICIT).
  - Générateur déterministe de terrain_signals institutionnels (water/
    steep/NDVI/microrelief) depuis le centre officiel.
  - Consommation par `p1_preparation` → subscores spatialement variés par
    corridor → étalement de la distribution level_v7 sur ≥ 2 niveaux.
  - Auto-injection dans `smooth_bundle()` quand amont ne fournit rien.
  - V30 intangible.
"""
import pytest


def _enable_p3(monkeypatch):
    monkeypatch.setenv("P3_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P3_COMMANDANT_TOKEN", "STEEVE-MAX-X200-P3-EXPLICIT")


def _enable_p1_and_p3(monkeypatch):
    _enable_p3(monkeypatch)
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_HISTORICAL_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXPLICIT")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXTERNAL-INFLOW")


# ─────────────────────────────────────────────────────────────────────
# TRIPLE VERROU P3
# ─────────────────────────────────────────────────────────────────────
def test_p3_flag_on_by_default():
    from engines.post_smoothing.terrain_signals_builder import (
        P3_TERRAIN_SIGNALS_ENABLED,
    )
    assert P3_TERRAIN_SIGNALS_ENABLED is True


def test_p3_auth_fails_without_token(monkeypatch):
    monkeypatch.setenv("P3_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P3_COMMANDANT_TOKEN", "WRONG")
    from engines.post_smoothing.terrain_signals_builder import is_p3_authorized
    assert is_p3_authorized()["authorized"] is False


def test_p3_auth_ok_with_env_and_token(monkeypatch):
    _enable_p3(monkeypatch)
    from engines.post_smoothing.terrain_signals_builder import is_p3_authorized
    a = is_p3_authorized()
    assert a["authorized"] is True and a["env_ok"] and a["token_ok"]


# ─────────────────────────────────────────────────────────────────────
# GÉNÉRATEUR INSTITUTIONNEL
# ─────────────────────────────────────────────────────────────────────
def test_build_signals_contains_all_layers():
    from engines.post_smoothing.terrain_signals_builder import build_institutional_signals
    s = build_institutional_signals(48.206657, -68.382422)
    assert set(s.keys()) >= {
        "water_points", "steep_slope_points", "ndvi_grid",
        "forest_cover", "microrelief", "center", "_p3_source",
    }
    assert 4 <= len(s["water_points"]) <= 6
    assert 3 <= len(s["steep_slope_points"]) <= 5
    assert len(s["ndvi_grid"]) == 9
    assert 0.0 <= s["forest_cover"] <= 1.0
    assert s["microrelief"]["slope_class"] in (
        "flat", "gentle", "moderate", "steep", "very_steep",
    )
    assert s["v30_engine_touched"] is False


def test_build_signals_deterministic():
    from engines.post_smoothing.terrain_signals_builder import build_institutional_signals
    s1 = build_institutional_signals(48.206657, -68.382422)
    s2 = build_institutional_signals(48.206657, -68.382422)
    assert s1["water_points"] == s2["water_points"]
    assert s1["ndvi_grid"] == s2["ndvi_grid"]


# ─────────────────────────────────────────────────────────────────────
# DÉRIVATION DES SUBSCORES PAR PATH (variation spatiale)
# ─────────────────────────────────────────────────────────────────────
def test_derive_subscores_varies_by_location():
    from engines.post_smoothing.terrain_signals_builder import (
        build_institutional_signals, derive_corridor_subscores,
    )
    s = build_institutional_signals(48.206657, -68.382422)
    c_near_water = {"id": "near", "path": s["water_points"][:2]}  # path passant par 2 water_points
    c_far = {"id": "far",  "path": [[48.200, -68.370], [48.201, -68.371], [48.202, -68.372]]}
    ss_near = derive_corridor_subscores(c_near_water, s)
    ss_far  = derive_corridor_subscores(c_far, s)
    # Le path qui touche l'eau a un topo_hydro strictement supérieur
    assert ss_near["topo_hydro"] > ss_far["topo_hydro"]


# ─────────────────────────────────────────────────────────────────────
# ÉTALEMENT DE LA DISTRIBUTION LEVEL_V7
# ─────────────────────────────────────────────────────────────────────
def test_p1_with_terrain_signals_spreads_levels(monkeypatch):
    """Directive X200-P3 : avec terrain_signals réels, au moins 2 niveaux distincts."""
    _enable_p1_and_p3(monkeypatch)
    from engines.post_smoothing.terrain_signals_builder import build_institutional_signals
    from engines.post_smoothing.p1_preparation import apply_p1_suite_to_bundle

    center_lat, center_lng = 48.206657, -68.382422
    ts = build_institutional_signals(center_lat, center_lng)

    # 8 corridors synthétiques répartis autour du waypoint (bearings)
    import math
    corridors = []
    for i, b_deg in enumerate([0, 45, 90, 135, 180, 225, 270, 315]):
        rad = math.radians(b_deg)
        dlat = 0.005 * math.cos(rad)
        dlng = 0.005 * math.sin(rad)
        corridors.append({
            "id": f"c_{i}",
            "path": [
                [center_lat, center_lng],
                [center_lat + dlat * 0.5, center_lng + dlng * 0.5],
                [center_lat + dlat,       center_lng + dlng],
            ],
            "vital_zone_connections": [{"type": "salines"}, {"type": "repos"}],
            "smoothing_metrics": {"max_segment_m": 18.0},
        })

    bundle = {"terrain_signals": ts, "corridors": corridors}
    out = apply_p1_suite_to_bundle(bundle)
    dist = out["p1_activation"]["density_5_levels_distribution"]
    # Contrat institutionnel P3 : éliminer la convergence unique vers FORT
    assert len(dist) >= 2, f"distribution trop concentrée : {dist}"
    # Source des signaux correctement traçée
    assert out["p1_activation"]["terrain_signals_source"] == "TERRAIN_SIGNALS_BUILDER_Ω_X200_P3"


# ─────────────────────────────────────────────────────────────────────
# AUTO-INJECTION PAR LE SMOOTHER
# ─────────────────────────────────────────────────────────────────────
def test_smoother_auto_injects_terrain_signals_when_absent(monkeypatch):
    _enable_p1_and_p3(monkeypatch)
    from engines.post_smoothing.organic_corridor_smoother import smooth_bundle
    bundle = {
        "species": "orignal",
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [{
            "id": "c1",
            "path": [
                [48.2065, -68.3820], [48.2070, -68.3828], [48.2076, -68.3835],
            ],
        }],
    }
    out = smooth_bundle(bundle)
    assert out["smoother_p3_terrain_signals_injected"] is True
    assert out["terrain_signals"]["_p3_source"] == "TERRAIN_SIGNALS_BUILDER_Ω_X200_P3"


def test_smoother_preserves_caller_terrain_signals(monkeypatch):
    """Si l'amont fournit déjà terrain_signals, le builder P3 ne l'écrase pas."""
    _enable_p1_and_p3(monkeypatch)
    from engines.post_smoothing.organic_corridor_smoother import smooth_bundle
    custom = {
        "_p3_source": "CUSTOM_UPSTREAM",
        "water_points": [[48.21, -68.38]],
        "steep_slope_points": [],
        "ndvi_grid": [],
        "forest_cover": 0.6,
        "microrelief": {"microrelief_index": 0.3, "slope_deg": 5, "slope_class": "gentle", "aspect_cardinal": "N"},
    }
    bundle = {
        "species": "orignal",
        "center": {"lat": 48.206657, "lng": -68.382422},
        "terrain_signals": custom,
        "corridors": [{"id": "c1", "path": [[48.2065, -68.3820], [48.2076, -68.3835]]}],
    }
    out = smooth_bundle(bundle)
    assert out["smoother_p3_terrain_signals_injected"] is False
    assert out["terrain_signals"]["_p3_source"] == "CUSTOM_UPSTREAM"


# ─────────────────────────────────────────────────────────────────────
# V30 INTANGIBLE
# ─────────────────────────────────────────────────────────────────────
def test_p3_does_not_import_v30(monkeypatch):
    _enable_p3(monkeypatch)
    import sys
    before = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    from engines.post_smoothing.terrain_signals_builder import build_institutional_signals
    build_institutional_signals(48.206657, -68.382422)
    after = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    assert before == after
