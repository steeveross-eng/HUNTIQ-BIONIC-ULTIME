"""
test_interzone_omega.py — PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_INTERZONE_GENERATION
================================================================================
Tests institutionnels pour la génération de corridors inter-zones multi-espèces.
NO TESTING AGENT. Manual pytest only.
"""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

os.environ["VEINEUX_OMEGA_AUTHORIZED_BY_COMMANDANT"] = "true"
os.environ["VEINEUX_OMEGA_COMMANDANT_TOKEN"] = "STEEVE-MAX-XII-VEINEUX-EXPLICIT"
os.environ["INTERZONE_OMEGA_AUTHORIZED_BY_COMMANDANT"] = "true"
os.environ["INTERZONE_OMEGA_COMMANDANT_TOKEN"] = "STEEVE-MAX-XII-INTERZONE-EXPLICIT"

from engines.post_smoothing import interzone_omega as iz  # noqa: E402


WAYPOINT = [48.206657, -68.382422]


def _bundle_with_zones():
    """Bundle minimal avec 5 zones vitales + 2 salines, représentatif du
    waypoint officiel."""
    return {
        "species": "orignal",
        "waypoint": {"lat": WAYPOINT[0], "lng": WAYPOINT[1]},
        "zones": [
            {"id": "z_rut", "type": "rut",
             "polygon": [[48.2094, -68.3766], [48.2096, -68.3767], [48.2092, -68.3769]]},
            {"id": "z_alim", "type": "alimentation",
             "polygon": [[48.2098, -68.3859], [48.2098, -68.3860], [48.2097, -68.3859]]},
            {"id": "z_repos", "type": "repos",
             "polygon": [[48.2061, -68.3867], [48.2062, -68.3868], [48.2060, -68.3869]]},
            {"id": "z_eau", "type": "eau",
             "polygon": [[48.2046, -68.3834], [48.2047, -68.3835], [48.2045, -68.3834]]},
            {"id": "z_therm", "type": "thermique",
             "polygon": [[48.2045, -68.3789], [48.2046, -68.3790], [48.2044, -68.3788]]},
        ],
        "salines": [
            {"id": "sal_0", "lat": 48.20761, "lng": -68.38099},
            {"id": "sal_1", "lat": 48.20812, "lng": -68.38461},
        ],
        "corridors": [],  # V30 vide pour isoler l'interzone
    }


# ═══════════════════════════════════════════════════════════════════════
# §§ TRIPLE VERROU
# ═══════════════════════════════════════════════════════════════════════
def test_triple_verrou_interzone_authorized():
    auth = iz.is_interzone_authorized()
    assert auth["authorized"] is True
    assert auth["flag_enabled"] is True
    assert auth["env_flag_ok"] is True
    assert auth["token_ok"] is True


def test_interzone_disabled_without_env():
    orig = os.environ.pop("INTERZONE_OMEGA_AUTHORIZED_BY_COMMANDANT", None)
    try:
        assert iz.is_interzone_authorized()["authorized"] is False
    finally:
        if orig:
            os.environ["INTERZONE_OMEGA_AUTHORIZED_BY_COMMANDANT"] = orig


# ═══════════════════════════════════════════════════════════════════════
# §§ MATRICE D'AFFINITÉ MULTI-ESPÈCES
# ═══════════════════════════════════════════════════════════════════════
def test_affinity_matrix_has_4_species():
    for sp in ("orignal", "cerf", "ours", "dindon"):
        assert sp in iz.AFFINITY_MATRIX
        assert len(iz.AFFINITY_MATRIX[sp]) >= 3


def test_affinity_matrix_orignal_complete():
    m = iz.AFFINITY_MATRIX["orignal"]
    assert m[("rut", "alimentation")] >= 0.80
    assert m[("alimentation", "eau")] >= 0.80
    assert m[("saline", "alimentation")] >= 0.60


def test_affinity_matrix_ours_prioritizes_food_over_rut():
    m_ours = iz.AFFINITY_MATRIX["ours"]
    assert m_ours[("alimentation", "repos")] >= 0.80
    # l'ours n'a pas de forte affinité rut/salines → absent ou faible
    assert m_ours.get(("saline", "rut"), 0.0) < 0.50


def test_affinity_matrix_dindon_no_rut():
    m = iz.AFFINITY_MATRIX["dindon"]
    # Dindon : pas de paire rut/* (période hors rut en automne québecois)
    assert all("rut" not in p for p in m.keys())


# ═══════════════════════════════════════════════════════════════════════
# §§ CORRIDORS ENTRANTS (MIGRATION)
# ═══════════════════════════════════════════════════════════════════════
def test_entering_enabled_for_mobile_species_only():
    assert iz.ENTERING_CORRIDORS_ENABLED["orignal"] is True
    assert iz.ENTERING_CORRIDORS_ENABLED["cerf"] is True
    assert iz.ENTERING_CORRIDORS_ENABLED["ours"] is False
    assert iz.ENTERING_CORRIDORS_ENABLED["dindon"] is False


def test_entering_distance_within_functional_radius():
    # §2.4 RenduΩ : ≤ 780 m → les entering doivent démarrer ≤ 780 m
    assert iz.ENTERING_DISTANCE_MAX_M <= 780.0
    assert iz.ENTERING_DISTANCE_MIN_M >= 400.0


# ═══════════════════════════════════════════════════════════════════════
# §§ GÉNÉRATION END-TO-END
# ═══════════════════════════════════════════════════════════════════════
def test_generate_interzone_orignal_produces_multiple_corridors():
    bundle = _bundle_with_zones()
    new_corridors = iz.generate_interzone_corridors(bundle)
    assert len(new_corridors) >= 8, f"Attendu ≥ 8 corridors inter-zones, obtenu {len(new_corridors)}"
    # au moins quelques types de paires
    pairs = {tuple(c["interzone_pair"]) for c in new_corridors if c.get("interzone_pair")}
    assert len(pairs) >= 4


def test_generate_produces_entering_corridors_for_orignal():
    bundle = _bundle_with_zones()
    new_corridors = iz.generate_interzone_corridors(bundle)
    entering = [c for c in new_corridors if c.get("entering_corridor")]
    assert len(entering) >= 2, "Corridors entrants orignal insuffisants"
    for e in entering:
        assert e["entering_distance_m"] <= 780.0


def test_ours_no_entering_corridors():
    bundle = _bundle_with_zones()
    bundle["species"] = "ours"
    new_corridors = iz.generate_interzone_corridors(bundle)
    entering = [c for c in new_corridors if c.get("entering_corridor")]
    assert len(entering) == 0, "Ours ne devrait pas avoir de corridors entrants"


def test_dindon_no_rut_pairs():
    bundle = _bundle_with_zones()
    bundle["species"] = "dindon"
    new_corridors = iz.generate_interzone_corridors(bundle)
    for c in new_corridors:
        pair = tuple(c.get("interzone_pair") or [])
        assert "rut" not in pair


# ═══════════════════════════════════════════════════════════════════════
# §§ GEOMETRIC CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════
def test_all_corridors_have_30_points():
    bundle = _bundle_with_zones()
    for sp in ("orignal", "cerf", "ours", "dindon"):
        bundle["species"] = sp
        new_corridors = iz.generate_interzone_corridors(bundle)
        for c in new_corridors:
            assert len(c["path"]) == iz.INTERZONE_POINTS_OUT


def test_no_corridor_point_exceeds_functional_radius_max():
    """Aucun point ne doit dépasser le rayon fonctionnel max interzone."""
    bundle = _bundle_with_zones()
    new_corridors = iz.generate_interzone_corridors(bundle)
    for c in new_corridors:
        for pt in c["path"]:
            d = iz._distance_m(pt, WAYPOINT)
            assert d <= iz.INTERZONE_FUNCTIONAL_RADIUS_MAX_M + 1.0, (
                f"corridor {c['id']} point à {d:.1f} m > {iz.INTERZONE_FUNCTIONAL_RADIUS_MAX_M} m"
            )


def test_apply_interzone_to_bundle_stats():
    bundle = _bundle_with_zones()
    out = iz.apply_interzone_omega_to_bundle(bundle)
    assert out.get("interzone_omega_applied") is True
    stats = out.get("interzone_omega_stats", {})
    assert stats["interzone_added"] >= 5
    assert stats["entering_added"] >= 2  # orignal
    assert stats["total_after"] >= 7


def test_interzone_without_authorization_is_noop():
    orig = os.environ.pop("INTERZONE_OMEGA_AUTHORIZED_BY_COMMANDANT", None)
    try:
        bundle = _bundle_with_zones()
        out = iz.apply_interzone_omega_to_bundle(bundle)
        assert out.get("interzone_omega_applied") is False
        # les corridors sont inchangés (vide ici)
        assert len(out.get("corridors") or []) == 0
    finally:
        if orig:
            os.environ["INTERZONE_OMEGA_AUTHORIZED_BY_COMMANDANT"] = orig
