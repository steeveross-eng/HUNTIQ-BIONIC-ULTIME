"""
test_x199_activation_engines.py
================================
Phase : PHASE_X199_ACTIVATION_Ω — 5 engines
Commandant STEEVE-MAX

Tests institutionnels MANUELS (aucun testing agent) pour l'activation
séquencée des 5 moteurs X199 sous triple verrou Ω.
"""
from datetime import date

import pytest


# ─────────────────────────────────────────────────────────────────────
# COMMONS — Triple verrou X199
# ─────────────────────────────────────────────────────────────────────
def test_x199_commons_module_importable():
    from engines.x199_commons import (
        is_x199_authorized, unauthorized_response, EXPECTED_TOKEN_X199,
    )
    assert EXPECTED_TOKEN_X199 == "STEEVE-MAX-X199-EXPLICIT"


def test_x199_auth_fails_without_flag():
    from engines.x199_commons import is_x199_authorized
    a = is_x199_authorized(False)
    assert a["authorized"] is False
    assert a["flag_enabled"] is False


def test_x199_auth_ok_with_env_and_token(monkeypatch):
    monkeypatch.setenv("X199_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("X199_COMMANDANT_TOKEN", "STEEVE-MAX-X199-EXPLICIT")
    from engines.x199_commons import is_x199_authorized
    a = is_x199_authorized(True)
    assert a["authorized"] is True
    assert a["env_ok"] is True
    assert a["token_ok"] is True


def test_x199_auth_fails_with_wrong_token(monkeypatch):
    monkeypatch.setenv("X199_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("X199_COMMANDANT_TOKEN", "WRONG")
    from engines.x199_commons import is_x199_authorized
    a = is_x199_authorized(True)
    assert a["authorized"] is False


# ─────────────────────────────────────────────────────────────────────
# #1 — ECOFORESTRY_Ω
# ─────────────────────────────────────────────────────────────────────
def test_ecoforestry_flag_on():
    from engines.ecoforestry_omega.router import FEATURE_FLAG_ACTIVE
    assert FEATURE_FLAG_ACTIVE is True


def test_ecoforestry_compute_official_point():
    from engines.ecoforestry_omega.router import compute_ecoforestry
    r = compute_ecoforestry(48.206657, -68.382422, 10)
    assert r["engine_id"] == "ENGINE_ECOFORESTRY_Ω"
    assert r["forest_type"] in (
        "coniferous_boreal", "mixed_boreal", "deciduous_temperate",
        "wetland_forested", "clearing_wet",
    )
    assert 0.0 <= r["canopy_fraction"] <= 1.0
    assert r["succession_stage"] in ("pioneer", "intermediate", "mature", "climax")
    assert r["v30_engine_touched"] is False


def test_ecoforestry_season_reduces_canopy_on_deciduous():
    from engines.ecoforestry_omega.router import compute_ecoforestry
    # Point hors boréale (lat < 48.10) → deciduous_temperate
    summer = compute_ecoforestry(47.50, -68.40, 7)["canopy_fraction"]
    winter = compute_ecoforestry(47.50, -68.40, 1)["canopy_fraction"]
    assert winter < summer


# ─────────────────────────────────────────────────────────────────────
# #2 — ADVANCED_GEOSPATIAL_Ω
# ─────────────────────────────────────────────────────────────────────
def test_advanced_geospatial_flag_on():
    from engines.advanced_geospatial_omega.router import FEATURE_FLAG_ACTIVE
    assert FEATURE_FLAG_ACTIVE is True


def test_utm_official_point_zone_19n():
    from engines.advanced_geospatial_omega.router import latlng_to_utm
    utm = latlng_to_utm(48.206657, -68.382422)
    assert utm["zone"] == 19
    assert utm["hemisphere"] == "N"
    assert utm["epsg"] == 32619
    # Le waypoint BSL tombe autour de 545-550 km E / 5339-5340 km N zone 19N
    assert 540000 < utm["easting"] < 555000
    assert 5335000 < utm["northing"] < 5345000


def test_haversine_accuracy_known_pair():
    from engines.advanced_geospatial_omega.router import haversine_m
    # 1° de latitude ≈ 111 320 m
    d = haversine_m((48.0, -68.0), (49.0, -68.0))
    assert abs(d - 111320) < 2000  # tolérance < 2 km pour la formule


def test_fusion_multi_source():
    from engines.advanced_geospatial_omega.router import multi_source_fusion_score
    r = multi_source_fusion_score([
        {"kind": "hydro", "value": 0.8},
        {"kind": "dem",   "value": 0.6},
        {"kind": "ndvi",  "value": 0.7},
    ])
    assert 0.0 <= r["fusion_score"] <= 1.0
    assert r["sources_used"] == 3


# ─────────────────────────────────────────────────────────────────────
# #3 — TERRAIN_3D_Ω
# ─────────────────────────────────────────────────────────────────────
def test_terrain_3d_flag_on():
    from engines.terrain_3d_omega.router import FEATURE_FLAG_ACTIVE
    assert FEATURE_FLAG_ACTIVE is True


def test_slope_aspect_known_plane_no_slope():
    from engines.terrain_3d_omega.router import slope_aspect_from_triangle
    # Plan horizontal : 3 points même altitude
    r = slope_aspect_from_triangle(
        [48.0, -68.0, 200.0],
        [48.001, -68.0, 200.0],
        [48.0, -67.999, 200.0],
    )
    assert r["slope_deg"] < 0.5


def test_slope_aspect_known_north_facing():
    from engines.terrain_3d_omega.router import slope_aspect_from_triangle
    # Élévation qui monte vers le sud (lat plus basse) → pente exposée sud-nord
    # Notre triangle : p0 origine, p1 au nord plus haut, p2 à l'est même altitude
    r = slope_aspect_from_triangle(
        [48.0, -68.0, 200.0],
        [48.001, -68.0, 210.0],   # nord plus haut
        [48.0, -67.999, 200.0],
    )
    assert r["slope_deg"] > 0
    # descendant vers le sud → aspect sud (S, SE ou SW)
    assert r["aspect_cardinal"] in ("S", "SE", "SW")


def test_slope_classification():
    from engines.terrain_3d_omega.router import classify_slope
    assert classify_slope(1) == "flat"
    assert classify_slope(5) == "gentle"
    assert classify_slope(15) == "moderate"
    assert classify_slope(25) == "steep"
    assert classify_slope(40) == "very_steep"


# ─────────────────────────────────────────────────────────────────────
# #4 — LEGAL_TIME_Ω
# ─────────────────────────────────────────────────────────────────────
def test_legal_time_flag_on():
    from engines.legal_time_omega.router import FEATURE_FLAG_ACTIVE
    assert FEATURE_FLAG_ACTIVE is True


def test_orignal_in_season_october_1():
    from engines.legal_time_omega.router import is_legal
    r = is_legal("orignal", date(2026, 10, 1))
    assert r["legal"] is True


def test_orignal_out_of_season_december():
    from engines.legal_time_omega.router import is_legal
    r = is_legal("orignal", date(2026, 12, 15))
    assert r["legal"] is False
    assert r["reason"] == "out_of_season"


def test_wapiti_not_allowed_zone_2():
    from engines.legal_time_omega.router import is_legal
    r = is_legal("wapiti", date(2026, 10, 1))
    assert r["legal"] is False
    assert r["reason"] == "species_not_allowed_in_zone"


def test_ours_two_windows_spring_and_fall():
    from engines.legal_time_omega.router import is_legal
    assert is_legal("ours", date(2026, 6, 1))["legal"] is True
    assert is_legal("ours", date(2026, 9, 15))["legal"] is True
    assert is_legal("ours", date(2026, 7, 15))["legal"] is False


# ─────────────────────────────────────────────────────────────────────
# #5 — PREDICTIVE_Ω (dépend 1+3+4)
# ─────────────────────────────────────────────────────────────────────
def test_predictive_flag_on():
    from engines.predictive_omega.router import FEATURE_FLAG_ACTIVE
    assert FEATURE_FLAG_ACTIVE is True


def test_predictive_probability_high_in_season_active_hour():
    from engines.predictive_omega.router import compute_predictive
    r = compute_predictive(48.206657, -68.382422, "orignal", "2026-10-01", 7)
    assert 0.0 <= r["probability_0_1"] <= 1.0
    # Saison légale + heure d'activité → multiplicateur 1.0 et composantes élevées
    assert r["components"]["legal"] == 1.0
    assert r["components"]["activity"] == 1.0
    assert r["probability_0_1"] > 0.5


def test_predictive_probability_penalized_out_of_season():
    from engines.predictive_omega.router import compute_predictive
    r_in  = compute_predictive(48.206657, -68.382422, "orignal", "2026-10-01", 7)
    r_out = compute_predictive(48.206657, -68.382422, "orignal", "2026-12-15", 7)
    assert r_out["legal_multiplier"] == 0.3
    assert r_out["probability_0_1"] < r_in["probability_0_1"]


def test_predictive_depends_on_upstream_engines():
    from engines.predictive_omega.router import compute_predictive
    r = compute_predictive(48.206657, -68.382422, "orignal", "2026-10-01", 7)
    assert set(r["upstream_engines"]) == {"ECOFORESTRY_Ω", "3D_TERRAIN_Ω", "LEGAL_TIME_Ω"}


# ─────────────────────────────────────────────────────────────────────
# V30 INTANGIBLE
# ─────────────────────────────────────────────────────────────────────
def test_x199_engines_do_not_import_v30():
    import sys
    before = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    from engines.ecoforestry_omega.router import compute_ecoforestry
    from engines.advanced_geospatial_omega.router import compute_advanced_geospatial
    from engines.terrain_3d_omega.router import compute_terrain_3d
    from engines.legal_time_omega.router import compute_legal_time
    from engines.predictive_omega.router import compute_predictive
    compute_ecoforestry(48.2, -68.3, 10)
    compute_advanced_geospatial(48.2, -68.3)
    compute_terrain_3d([])
    compute_legal_time("orignal", "2026-10-01")
    compute_predictive(48.2, -68.3, "orignal", "2026-10-01", 7)
    after = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    assert before == after


# ─────────────────────────────────────────────────────────────────────
# AUDIT CONTINU Ω — tous les engines reportent ready/authorized
# ─────────────────────────────────────────────────────────────────────
def test_audit_all_5_engines_authorized(monkeypatch):
    monkeypatch.setenv("X199_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("X199_COMMANDANT_TOKEN", "STEEVE-MAX-X199-EXPLICIT")
    from engines.x199_commons import is_x199_authorized
    from engines.ecoforestry_omega.router import FEATURE_FLAG_ACTIVE as f1
    from engines.advanced_geospatial_omega.router import FEATURE_FLAG_ACTIVE as f2
    from engines.terrain_3d_omega.router import FEATURE_FLAG_ACTIVE as f3
    from engines.legal_time_omega.router import FEATURE_FLAG_ACTIVE as f4
    from engines.predictive_omega.router import FEATURE_FLAG_ACTIVE as f5
    for flag, name in [(f1, "eco"), (f2, "geo"), (f3, "3d"), (f4, "leg"), (f5, "pred")]:
        assert is_x199_authorized(flag)["authorized"] is True, f"{name} non autorisé"
