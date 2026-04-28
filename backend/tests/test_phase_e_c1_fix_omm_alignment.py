"""
test_phase_e_c1_fix_omm_alignment.py — FIX C1 (PHASE-E)
═══════════════════════════════════════════════════════════════════════════
Phase     : PHASE-E / FIX C1 VENT/CONTAM/SENSORIEL
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests de l'alignement institutionnel des engines C1 sur la convention
OMM/Open-Meteo "FROM" (wind_deg = origine du vent).

Référence canonique : engine_sensoriel_vent_odeurs_omega.cone_axis_deg
                       (= wind_deg + 180° = downwind propagation).
"""
from __future__ import annotations

import hashlib
import math
import sys

import pytest

sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_vent import (
    compute_scent_cone,
    compute_wind_vectors,
    _downwind_deg,
    WIND_DOWNWIND_OFFSET_DEG,
)
from engines.v8_institutional.engine_sensoriel_vent_odeurs_omega import (
    compute_sensoriel_vent_odeurs,
)

WAYPOINTS = [
    ("BSL_OFFICIEL", 48.206657, -68.382422),
    ("ESTRIE", 45.0, -72.8),
    ("MONTREAL", 45.7, -73.6),
]
WIND_DEG_TESTS = [0.0, 45.0, 90.0, 141.0, 180.0, 225.0, 270.0, 315.0]
WIND_SPEED = 12.0


# ─────────────────────────────────────────────────────────────────────────
# 1. Helper _downwind_deg conforme OMM
# ─────────────────────────────────────────────────────────────────────────
def test_downwind_helper_returns_plus_180_modulo_360():
    assert WIND_DOWNWIND_OFFSET_DEG == 180.0
    assert _downwind_deg(0) == 180.0
    assert _downwind_deg(90) == 270.0
    assert _downwind_deg(180) == 0.0
    assert _downwind_deg(270) == 90.0
    assert _downwind_deg(141) == 321.0


# ─────────────────────────────────────────────────────────────────────────
# 2. compute_scent_cone est aligné DOWNWIND (engine_sensoriel)
# ─────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("wind_deg", WIND_DEG_TESTS)
def test_scent_cone_aligned_with_sensoriel(wind_deg):
    sc = compute_scent_cone(48.0, -68.0, wind_deg, WIND_SPEED)
    sens = compute_sensoriel_vent_odeurs(
        {"terrain": {"olfactive_diffusion": 0.6, "canopy": 0.5}}, wind_deg, WIND_SPEED
    )
    assert sc["direction_deg"] == pytest.approx(sens["cone_axis_deg"], abs=0.5), \
        f"scent_cone et sensoriel doivent pointer downwind ensemble (wind={wind_deg})"
    assert sc["convention"].startswith("downwind_TO")
    assert sc["parent_truth_from_deg"] == pytest.approx(wind_deg % 360.0, abs=0.5)


# ─────────────────────────────────────────────────────────────────────────
# 3. compute_wind_vectors central pointe DOWNWIND
# ─────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("wind_deg", WIND_DEG_TESTS)
def test_wind_vectors_central_aligned_downwind(wind_deg):
    wv = compute_wind_vectors(48.0, -68.0, wind_deg, WIND_SPEED)
    central = next(v for v in wv if v["is_central"])
    expected_downwind = (wind_deg + 180.0) % 360.0
    assert central["direction_deg"] == pytest.approx(expected_downwind, abs=0.5)
    assert central["downwind_axis_deg"] == pytest.approx(expected_downwind, abs=0.5)
    # parent_truth conserve la convention OMM "FROM"
    assert central["parent_truth_deg"] == pytest.approx(wind_deg % 360.0, abs=0.5)
    assert central["parent_truth_convention"] == "FROM"


# ─────────────────────────────────────────────────────────────────────────
# 4. Δ entre engine_vent et engine_sensoriel doit être < 1° (PLUS d'écart 180°)
# ─────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("name,lat,lon", WAYPOINTS)
def test_no_more_180_deg_drift_on_3_sites(name, lat, lon):
    wind_deg = 90.0
    sc = compute_scent_cone(lat, lon, wind_deg, WIND_SPEED)
    wv = compute_wind_vectors(lat, lon, wind_deg, WIND_SPEED)
    central = next(v for v in wv if v["is_central"])
    sens = compute_sensoriel_vent_odeurs(
        {"terrain": {"olfactive_diffusion": 0.6, "canopy": 0.5}}, wind_deg, WIND_SPEED
    )
    delta_scent = abs((sc["direction_deg"] - sens["cone_axis_deg"] + 360) % 360)
    delta_central = abs((central["direction_deg"] - sens["cone_axis_deg"] + 360) % 360)
    # Convention angulaire : delta doit être proche de 0 (OU 360 = 0).
    delta_scent = min(delta_scent, 360 - delta_scent)
    delta_central = min(delta_central, 360 - delta_central)
    assert delta_scent < 1.0, f"{name}: scent_cone vs sensoriel Δ={delta_scent:.2f}°"
    assert delta_central < 1.0, f"{name}: wind_vectors[central] vs sensoriel Δ={delta_central:.2f}°"


# ─────────────────────────────────────────────────────────────────────────
# 5. Géométrie projection : le bout du cône downwind (lat,lon) déplacé conformément
# ─────────────────────────────────────────────────────────────────────────
def test_cone_polygon_points_downwind_geometrically():
    """Avec wind_deg=90 (vent d'EST → propagation vers OUEST),
    les sommets du cône doivent avoir lon < lon_origine."""
    lat, lon = 48.0, -68.0
    sc = compute_scent_cone(lat, lon, 90.0, 12.0, cone_angle=30, reach_m=500)
    p1 = sc["polygon"][1]  # left vertex
    p2 = sc["polygon"][2]  # right vertex
    # downwind = 270° → pointe ouest → lon doit DIMINUER (vers l'ouest)
    assert p1[1] < lon, f"sommet gauche du cône doit aller vers l'ouest (lon<{lon}), got {p1[1]}"
    assert p2[1] < lon, f"sommet droit du cône doit aller vers l'ouest (lon<{lon}), got {p2[1]}"


def test_wind_vectors_central_endpoint_points_downwind():
    """Avec wind_deg=0 (vent du NORD → propagation vers SUD),
    le vecteur central doit avoir end_lat < lat_origine."""
    lat, lon = 48.0, -68.0
    wv = compute_wind_vectors(lat, lon, 0.0, 12.0)
    central = next(v for v in wv if v["is_central"])
    # downwind = 180° → vers le SUD → lat doit diminuer
    assert central["end"]["lat"] < lat, \
        f"end.lat={central['end']['lat']} doit être < lat origine {lat} (downwind sud)"


# ─────────────────────────────────────────────────────────────────────────
# 6. V30 LOCKED — invariance cryptographique post-fix
# ─────────────────────────────────────────────────────────────────────────
def test_v30_inchange_post_fix_c1():
    expected = {
        "/app/backend/engines/v8_institutional/registry_lock_omega.py":
            "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c",
        "/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py":
            "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3",
    }
    for path, exp in expected.items():
        with open(path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        assert sha == exp, f"V30 mutation post-fix C1 sur {path}"


# ─────────────────────────────────────────────────────────────────────────
# 7. Idempotence du fix : 2 appels identiques produisent même résultat
# ─────────────────────────────────────────────────────────────────────────
def test_fix_c1_idempotent():
    a = compute_scent_cone(48.0, -68.0, 141.0, 12.0)
    b = compute_scent_cone(48.0, -68.0, 141.0, 12.0)
    assert a == b
    c = compute_wind_vectors(48.0, -68.0, 141.0, 12.0)
    d = compute_wind_vectors(48.0, -68.0, 141.0, 12.0)
    assert c == d
