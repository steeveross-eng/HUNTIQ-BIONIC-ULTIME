"""
test_x200_p5_renduomega.py
==========================
Phase : PHASE_X200_P5_RENDUΩ_INTEGRATION_ULTIME_Ω
Commandant STEEVE-MAX
"""
import math

import pytest


def _enable_p5(monkeypatch):
    monkeypatch.setenv("P5_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P5_COMMANDANT_TOKEN", "STEEVE-MAX-X200-P5-EXPLICIT")


def _valid_path(center=(48.206657, -68.382422), n_points=27, length_m=500.0):
    """Génère un path méandrique conforme : n points, longueur projetée ~500 m,
    angles < 45°, segments ~15 m, d'un bearing principal avec oscillation
    latérale pour éviter détection radiale."""
    import math
    lat0, lng0 = center
    # Bearing principal 30° (NE), oscillation latérale ±25 m (méandre doux)
    main_bearing_rad = math.radians(30.0)
    amp_m = 25.0
    pts = []
    # step projeté principal pour longueur totale ≈ length_m
    step_m = (length_m / (n_points - 1)) * 0.97
    for i in range(n_points):
        t = i / (n_points - 1)
        # Avance selon bearing principal
        s = i * step_m
        # Oscillation latérale douce (1 période sur le path)
        lat_offset_m = amp_m * math.sin(t * 1.5 * math.pi)
        # Vecteur avance
        dx_main = s * math.sin(main_bearing_rad)
        dy_main = s * math.cos(main_bearing_rad)
        # Vecteur latéral (perpendiculaire)
        dx_lat = lat_offset_m * math.cos(main_bearing_rad)
        dy_lat = -lat_offset_m * math.sin(main_bearing_rad)
        dx = dx_main + dx_lat
        dy = dy_main + dy_lat
        dlat = dy / 111320.0
        dlng = dx / (111320.0 * math.cos(math.radians(lat0)))
        pts.append([round(lat0 + dlat, 7), round(lng0 + dlng, 7)])
    return pts


# ─────────────────────────────────────────────────────────────────────
# TRIPLE VERROU P5
# ─────────────────────────────────────────────────────────────────────
def test_p5_flag_on_by_default():
    from engines.post_smoothing.renduomega import P5_RENDUOMEGA_ENABLED
    assert P5_RENDUOMEGA_ENABLED is True


def test_p5_auth_fails_without_token(monkeypatch):
    monkeypatch.setenv("P5_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P5_COMMANDANT_TOKEN", "WRONG")
    from engines.post_smoothing.renduomega import is_p5_authorized
    assert is_p5_authorized()["authorized"] is False


def test_p5_auth_ok_with_token(monkeypatch):
    _enable_p5(monkeypatch)
    from engines.post_smoothing.renduomega import is_p5_authorized
    assert is_p5_authorized()["authorized"] is True


# ─────────────────────────────────────────────────────────────────────
# CONSTANTES INSTITUTIONNELLES
# ─────────────────────────────────────────────────────────────────────
def test_constants_base_color_ambre():
    from engines.post_smoothing.renduomega import (
        BASE_COLOR_ORANGE_AMBRE, OPACITY_MIN, MIN_ZOOM, WIDTHS_ALLOWED,
        ZINDEX_INSTITUTIONNEL,
    )
    assert BASE_COLOR_ORANGE_AMBRE == "#FF8F00"
    assert OPACITY_MIN >= 0.75
    assert MIN_ZOOM == 13
    assert WIDTHS_ALLOWED == (1.2, 2.0, 3.0)
    # Ordre institutionnel strict
    z = ZINDEX_INSTITUTIONNEL
    assert z["zones"] < z["hydrologie"] < z["terrain"] < z["corridors"] \
           < z["salines"] < z["affuts"] < z["hotspots"] < z["vent"]


def test_species_palette_derived_from_base():
    from engines.post_smoothing.renduomega import SPECIES_COLOR_PALETTE
    assert SPECIES_COLOR_PALETTE["orignal"] == "#FF8F00"
    for sp in ("cerf", "chevreuil", "ours", "dindon", "wapiti"):
        col = SPECIES_COLOR_PALETTE[sp]
        assert col.startswith("#") and len(col) == 7


# ─────────────────────────────────────────────────────────────────────
# §2 — GÉOMÉTRIE
# ─────────────────────────────────────────────────────────────────────
def test_geometry_valid_path_accepted():
    from engines.post_smoothing.renduomega import validate_geometry
    path = _valid_path(n_points=27, length_m=520.0)
    g = validate_geometry(path)
    assert g["ok"] is True
    assert g["points_count"] == 27
    assert g["length_m"] >= 100
    assert g["max_segment_m"] <= 20.0 + 0.01
    assert g["max_angle_deg"] <= 45.0


def test_geometry_rejects_too_few_points():
    from engines.post_smoothing.renduomega import validate_geometry
    path = [[48.0, -68.0], [48.001, -68.001], [48.002, -68.002]]
    g = validate_geometry(path)
    assert g["ok"] is False
    assert any("points_count" in v for v in g["violations"])


def test_geometry_rejects_segment_too_long():
    from engines.post_smoothing.renduomega import validate_geometry
    # 27 points mais segments > 20 m
    base = _valid_path(n_points=27, length_m=2000.0)  # step ~77 m
    g = validate_geometry(base)
    assert g["ok"] is False
    assert any("max_segment_m" in v for v in g["violations"])


def test_geometry_rejects_radial_straight_line():
    from engines.post_smoothing.renduomega import validate_geometry
    # Ligne quasi-droite (radial detection)
    base = [[48.0 + i * 0.0001, -68.0 + i * 0.0001] for i in range(27)]
    g = validate_geometry(base)
    # Soit rejetée par radial, soit par longueur. Dans tous les cas : ok=False
    assert g["ok"] is False


# ─────────────────────────────────────────────────────────────────────
# §3 — TERRAIN & ÉCOLOGIE
# ─────────────────────────────────────────────────────────────────────
def test_terrain_rejects_path_too_short_radius():
    from engines.post_smoothing.renduomega import validate_terrain_constraints
    center = [48.206657, -68.382422]
    path = _valid_path(center=tuple(center), n_points=27, length_m=200.0)
    r = validate_terrain_constraints(path, center, {})
    # max_radius_from_center_m < 420 → violation
    assert r["ok"] is False


def test_terrain_accepts_path_in_functional_radius():
    from engines.post_smoothing.renduomega import validate_terrain_constraints
    center = [48.206657, -68.382422]
    # Path dont la distance max au centre est ~500 m (dans [420, 780])
    path = _valid_path(center=tuple(center), n_points=27, length_m=520.0)
    r = validate_terrain_constraints(path, center, {"microrelief": {"slope_deg": 5.0}})
    assert r["ok"] is True


def test_ecology_rejects_path_crossing_road_buffer():
    from engines.post_smoothing.renduomega import validate_ecological_constraints
    # Zone humaine route forte au centre du path
    ts = {"human_zones": [{"lat": 48.2080, "lng": -68.3830, "kind": "road",
                            "buffer_m": 250.0, "weight": 0.85}]}
    path = [[48.2080 + i * 0.0001, -68.3830] for i in range(27)]
    r = validate_ecological_constraints(path, ts)
    assert r["ok"] is False
    assert any("human_zone_violation" in v for v in r["violations"])


def test_ecology_accepts_path_far_from_human_zones():
    from engines.post_smoothing.renduomega import validate_ecological_constraints
    ts = {"human_zones": [{"lat": 48.2500, "lng": -68.4000, "kind": "road",
                            "buffer_m": 250.0, "weight": 0.85}]}
    path = _valid_path(center=(48.206657, -68.382422), n_points=27, length_m=520.0)
    r = validate_ecological_constraints(path, ts)
    assert r["ok"] is True


# ─────────────────────────────────────────────────────────────────────
# §4 — ESPÈCE
# ─────────────────────────────────────────────────────────────────────
def test_species_rejects_multi_species():
    from engines.post_smoothing.renduomega import validate_species_and_source
    r = validate_species_and_source({"species": "orignal",
                                      "species_multi": ["orignal", "chevreuil"]})
    assert r["ok"] is False
    assert any("multi_species" in v for v in r["violations"])


def test_species_requires_metadata():
    from engines.post_smoothing.renduomega import validate_species_and_source
    r = validate_species_and_source({})
    assert r["ok"] is False
    assert any("species_metadata_missing" in v for v in r["violations"])


def test_species_accepts_single_species():
    from engines.post_smoothing.renduomega import validate_species_and_source
    r = validate_species_and_source({"species": "orignal"})
    assert r["ok"] is True


# ─────────────────────────────────────────────────────────────────────
# §5 — RENDU VISUEL
# ─────────────────────────────────────────────────────────────────────
def test_width_selection_by_probability():
    from engines.post_smoothing.renduomega import build_render_metadata
    low  = build_render_metadata({"species": "orignal", "corridor_probability_omega": 0.1})
    mid  = build_render_metadata({"species": "orignal", "corridor_probability_omega": 0.4})
    high = build_render_metadata({"species": "orignal", "corridor_probability_omega": 0.8})
    assert low["width_px"] == 1.2
    assert mid["width_px"] == 2.0
    assert high["width_px"] == 3.0
    # Opacité min strict
    assert low["opacity"] >= 0.75
    # Zindex corridors
    assert low["zindex"] == 130
    # minZoom
    assert low["min_zoom"] == 13


def test_color_fallback_to_base_ambre():
    from engines.post_smoothing.renduomega import build_render_metadata
    r = build_render_metadata({"species": "espece_inconnue",
                                "corridor_probability_omega": 0.3})
    assert r["color"] == "#FF8F00"


# ─────────────────────────────────────────────────────────────────────
# VALIDATEUR MAÎTRE — un corridor
# ─────────────────────────────────────────────────────────────────────
def test_validate_single_entity_full_accepted():
    from engines.post_smoothing.renduomega import validate_corridor
    center = [48.206657, -68.382422]
    corridor = {
        "id": "c1",
        "species": "orignal",
        "path": _valid_path(center=tuple(center), n_points=27, length_m=520.0),
        "corridor_probability_omega": 0.55,
    }
    v = validate_corridor(corridor, center=center,
                           terrain_signals={"microrelief": {"slope_deg": 5.0}})
    assert v["accepted"] is True
    assert v["render"]["width_px"] == 2.0
    assert v["render"]["color"] == "#FF8F00"
    assert v["errors"] == []


def test_validate_single_entity_records_errors_when_rejected():
    from engines.post_smoothing.renduomega import validate_corridor
    # Path trop court + pas de species
    corridor = {"id": "c_bad", "path": [[48.0, -68.0], [48.001, -68.001]]}
    v = validate_corridor(corridor, center=[48.0, -68.0], terrain_signals={})
    assert v["accepted"] is False
    kinds = {e["kind"] for e in v["errors"]}
    assert "ERREUR_RENDUΩ_GÉOMÉTRIE" in kinds
    assert "ERREUR_RENDUΩ_ESPÈCE" in kinds


# ─────────────────────────────────────────────────────────────────────
# HOOK SMOOTHER — BLOCAGE DUR §1.2
# ─────────────────────────────────────────────────────────────────────
def test_bundle_filters_rejected_entities(monkeypatch):
    _enable_p5(monkeypatch)
    from engines.post_smoothing.renduomega import apply_renduomega_to_bundle
    center = [48.206657, -68.382422]
    good = {
        "id": "good",
        "species": "orignal",
        "path": _valid_path(center=tuple(center), n_points=27, length_m=520.0),
        "corridor_probability_omega": 0.55,
    }
    bad = {
        "id": "bad",
        "species": "orignal",
        "path": [[48.0, -68.0], [48.001, -68.001]],   # trop court
    }
    bundle = {
        "center": {"lat": center[0], "lng": center[1]},
        "species": "orignal",
        "terrain_signals": {"microrelief": {"slope_deg": 5.0}},
        "corridors": [good, bad],
    }
    out = apply_renduomega_to_bundle(bundle)
    # §1.2 — le mauvais est retiré de `corridors`
    assert len(out["corridors"]) == 1
    assert out["corridors"][0]["id"] == "good"
    assert len(out["corridors_rejected_by_renduomega"]) == 1
    assert out["corridors_rejected_by_renduomega"][0]["id"] == "bad"
    ri = out["renduomega_integration"]
    assert ri["status"] == "APPLIED"
    assert ri["totals"] == {"total_input": 2, "accepted": 1, "rejected": 1}
    assert ri["v30_engine_touched"] is False


def test_bundle_bypass_when_not_authorized(monkeypatch):
    monkeypatch.setenv("P5_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "false")
    monkeypatch.delenv("P5_COMMANDANT_TOKEN", raising=False)
    from engines.post_smoothing.renduomega import apply_renduomega_to_bundle
    bundle = {"corridors": [{"id": "c", "path": [[48.0, -68.0]]}]}
    out = apply_renduomega_to_bundle(bundle)
    assert out["renduomega_integration"]["status"] == "BYPASSED"


def test_accepted_entity_carries_render_metadata(monkeypatch):
    _enable_p5(monkeypatch)
    from engines.post_smoothing.renduomega import apply_renduomega_to_bundle
    center = [48.206657, -68.382422]
    c = {
        "id": "c1",
        "species": "orignal",
        "path": _valid_path(center=tuple(center), n_points=27, length_m=520.0),
        "corridor_probability_omega": 0.8,
    }
    bundle = {
        "center": {"lat": center[0], "lng": center[1]},
        "species": "orignal",
        "terrain_signals": {"microrelief": {"slope_deg": 5.0}},
        "corridors": [c],
    }
    out = apply_renduomega_to_bundle(bundle)
    accepted = out["corridors"][0]
    assert accepted["color"] == "#FF8F00"
    assert accepted["opacity"] >= 0.75
    assert accepted["width_px_renduomega"] == 3.0
    assert accepted["min_zoom"] == 13
    assert accepted["zindex"] == 130


# ─────────────────────────────────────────────────────────────────────
# V30 INTANGIBLE
# ─────────────────────────────────────────────────────────────────────
def test_p5_does_not_import_v30(monkeypatch):
    _enable_p5(monkeypatch)
    import sys
    before = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    from engines.post_smoothing.renduomega import apply_renduomega_to_bundle
    apply_renduomega_to_bundle({"corridors": []})
    after = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    assert before == after
