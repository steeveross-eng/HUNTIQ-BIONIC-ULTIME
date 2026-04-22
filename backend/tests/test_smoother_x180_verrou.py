"""
test_smoother_x180_verrou.py — VERROU INSTITUTIONNEL PYTEST X195 §5
====================================================================
AMENDEMENT-ABSOLU COMMANDANT STEEVE-MAX :
  Ces tests NE VALIDENT PAS les corridors courants.
  Ils verrouillent UNIQUEMENT la stabilité du pipeline smoother X180
  pendant le rapatriement de TERRITOIRE V7 ULTIME.
  Toute interprétation contraire = violation BCE-4X.

Couvre les 9 passes du pipeline `organic_corridor_smoother.py` :
  1. trim_problematic_tail
  2. smooth_angle_violations
  3a. despike_path
  3b. eliminate_fuite_angles (> 90°)
  4. enforce_segment_max
  5. apply_ecological_alignment
  6. apply_ia_attractors
  7. re-smooth + re-despike (contrat idempotence)
  8. validate_metrics + smooth_corridor + smooth_bundle
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

# Assure l'import depuis /app/backend
sys.path.insert(0, str(Path("/app/backend")))

import pytest

from engines.post_smoothing.organic_corridor_smoother import (
    ANGLE_MAX_DEG,
    ANGLE_FUITE_DEG,
    SEGMENT_MAX_M,
    SPECIES_LOCOMOTION,
    _angle_deg_at,
    _segment_m,
    trim_problematic_tail,
    smooth_angle_violations,
    despike_path,
    eliminate_fuite_angles,
    enforce_segment_max,
    apply_ecological_alignment,
    apply_ia_attractors,
    detect_vital_zone_connections,
    validate_metrics,
    smooth_corridor,
    smooth_bundle,
)


# ═══════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════
def _pathological_path():
    """Path synthétique avec demi-tour médian ~178° et queue aberrante."""
    pts = []
    for i in range(15):
        pts.append([46.0 + i * 0.0001, -71.0 + i * 0.0001])
    # Demi-tour
    pts.append([46.0 + 13 * 0.0001, -71.0 + 13 * 0.0001])
    pts.append([46.0 + 11 * 0.0001, -71.0 + 11 * 0.0001])
    pts.append([46.0 + 9 * 0.0001, -71.0 + 9 * 0.0001])
    for i in range(15, 25):
        pts.append([46.0 + (i + 5) * 0.0001, -71.0 + (i + 5) * 0.0001])
    # Queue aberrante
    pts.append([46.0 + 28 * 0.0001, -71.0 + 20 * 0.0001])
    pts.append([46.0 + 25 * 0.0001, -71.0 + 24 * 0.0001])
    return pts


def _straight_long_path():
    """Path avec segment long (>20 m)."""
    # ~ 50 m lat delta entre points consécutifs
    return [[48.20 + i * 0.00045, -68.38] for i in range(8)]


# ═══════════════════════════════════════════════════════════════════════
# PASSE 1 — trim_problematic_tail
# ═══════════════════════════════════════════════════════════════════════
class TestPasse1TrimProblematicTail:
    def test_retourne_liste(self):
        out = trim_problematic_tail(_pathological_path(), ANGLE_MAX_DEG, 10)
        assert isinstance(out, list)

    def test_preserve_min_keep(self):
        out = trim_problematic_tail(_pathological_path(), ANGLE_MAX_DEG, 10)
        assert len(out) >= 10

    def test_identity_si_trop_court(self):
        short = [[0, 0], [0.001, 0.001]]
        assert trim_problematic_tail(short, ANGLE_MAX_DEG, 10) == short


# ═══════════════════════════════════════════════════════════════════════
# PASSE 2 — smooth_angle_violations
# ═══════════════════════════════════════════════════════════════════════
class TestPasse2SmoothAngleViolations:
    def test_preserve_length(self):
        p = _pathological_path()
        out = smooth_angle_violations(p, ANGLE_MAX_DEG, max_passes=20)
        assert len(out) == len(p)

    def test_reduit_angle_max(self):
        p = _pathological_path()
        out = smooth_angle_violations(p, ANGLE_MAX_DEG, max_passes=25)
        metrics_before = validate_metrics(p)
        metrics_after = validate_metrics(out)
        assert metrics_after["max_angle_deg"] <= metrics_before["max_angle_deg"]


# ═══════════════════════════════════════════════════════════════════════
# PASSE 3a — despike_path
# ═══════════════════════════════════════════════════════════════════════
class TestPasse3aDespikePath:
    def test_retourne_liste(self):
        out = despike_path(_pathological_path(), ANGLE_MAX_DEG)
        assert isinstance(out, list)

    def test_longueur_diminue_ou_egale(self):
        p = _pathological_path()
        out = despike_path(p, ANGLE_MAX_DEG, max_passes=20)
        assert len(out) <= len(p)


# ═══════════════════════════════════════════════════════════════════════
# PASSE 3b — eliminate_fuite_angles (> 90°)
# ═══════════════════════════════════════════════════════════════════════
class TestPasse3bEliminateFuiteAngles:
    def test_aucun_angle_fuite_residuel(self):
        p = _pathological_path()
        out = eliminate_fuite_angles(p, ANGLE_FUITE_DEG)
        # Après élimination, aucun angle ne doit dépasser 90°
        for i in range(1, len(out) - 1):
            ang = _angle_deg_at(out[i - 1], out[i], out[i + 1])
            assert ang < ANGLE_FUITE_DEG, f"angle {ang:.2f}° > 90° résiduel en i={i}"


# ═══════════════════════════════════════════════════════════════════════
# PASSE 4 — enforce_segment_max
# ═══════════════════════════════════════════════════════════════════════
class TestPasse4EnforceSegmentMax:
    def test_aucun_segment_hors_limite(self):
        p = _straight_long_path()
        out = enforce_segment_max(p, SEGMENT_MAX_M)
        for i in range(1, len(out)):
            seg = _segment_m(out[i - 1], out[i])
            assert seg <= SEGMENT_MAX_M + 0.5, f"segment {seg:.2f} m > {SEGMENT_MAX_M}"

    def test_densification_monotone(self):
        p = _straight_long_path()
        out = enforce_segment_max(p, SEGMENT_MAX_M)
        assert len(out) >= len(p)

    def test_continuite_preservee(self):
        p = _straight_long_path()
        out = enforce_segment_max(p, SEGMENT_MAX_M)
        # Extrémités identiques à l'entrée
        assert out[0] == p[0]
        assert out[-1] == p[-1]


# ═══════════════════════════════════════════════════════════════════════
# PASSE 5 — apply_ecological_alignment
# ═══════════════════════════════════════════════════════════════════════
class TestPasse5EcologicalAlignment:
    def test_non_regression_sans_signaux(self):
        p = _pathological_path()
        loco = SPECIES_LOCOMOTION["orignal"]
        out = apply_ecological_alignment(p, loco, terrain_signals=None)
        assert out == p  # identité sans signaux

    def test_nudge_bornee_5m(self):
        p = [[48.20, -68.38], [48.2001, -68.3801], [48.2002, -68.3802]]
        loco = SPECIES_LOCOMOTION["chevreuil"]
        # Point d'eau à 1 m du milieu
        signals = {"water_points": [[48.2001, -68.3801]]}
        out = apply_ecological_alignment(p, loco, signals)
        # Nudge borné ≤ ~5m (0.000045 deg lat)
        from engines.post_smoothing.organic_corridor_smoother import _haversine_m
        d = _haversine_m(p[1], out[1])
        assert d <= 6.0, f"nudge {d:.2f} m > 5 m borne"


# ═══════════════════════════════════════════════════════════════════════
# PASSE 6 — apply_ia_attractors
# ═══════════════════════════════════════════════════════════════════════
class TestPasse6IaAttractors:
    def test_non_regression_sans_signaux(self):
        p = _pathological_path()
        assert apply_ia_attractors(p, ia_signals=None) == p

    def test_nudge_bornee_3m(self):
        p = [[48.20, -68.38], [48.2001, -68.3801], [48.2002, -68.3802]]
        signals = {"attractors": [{"latlng": [48.2001, -68.38005], "weight": 1.0}]}
        out = apply_ia_attractors(p, signals)
        from engines.post_smoothing.organic_corridor_smoother import _haversine_m
        d = _haversine_m(p[1], out[1])
        assert d <= 4.0, f"nudge attracteur {d:.2f} m > 3 m borne"


# ═══════════════════════════════════════════════════════════════════════
# PASSE 7 — idempotence re-smooth + re-despike
# ═══════════════════════════════════════════════════════════════════════
class TestPasse7Idempotence:
    def test_idempotence_double_passage(self):
        p = _pathological_path()
        first = smooth_angle_violations(despike_path(p, ANGLE_MAX_DEG), ANGLE_MAX_DEG)
        second = smooth_angle_violations(despike_path(first, ANGLE_MAX_DEG), ANGLE_MAX_DEG)
        # Un second passage ne doit pas dégrader la conformité
        m1 = validate_metrics(first)
        m2 = validate_metrics(second)
        assert m2["max_angle_deg"] <= m1["max_angle_deg"] + 0.5


# ═══════════════════════════════════════════════════════════════════════
# PASSE 8 — validate_metrics + smooth_corridor + smooth_bundle
# ═══════════════════════════════════════════════════════════════════════
class TestPasse8ValidationComplete:
    def test_validate_metrics_shape(self):
        m = validate_metrics(_pathological_path())
        assert "max_angle_deg" in m
        assert "max_segment_m" in m
        assert "conforme_angle" in m
        assert "conforme_segment" in m
        assert "conforme_fuite" in m

    def test_smooth_pipeline_complet_passe8(self):
        c = {"path": _pathological_path(), "species": "orignal"}
        out = smooth_corridor(c)
        assert out.get("smoothing_applied") is True
        assert "X180" in out.get("smoothing_version", "")
        m = out.get("smoothing_metrics", {})
        # Contrat institutionnel : conformité géométrique après pipeline
        assert m.get("max_angle_deg", 999) <= ANGLE_MAX_DEG + 0.5, m
        assert m.get("max_segment_m", 999) <= SPECIES_LOCOMOTION["orignal"]["segment_max_m"] + 0.5, m
        assert m.get("conforme_fuite", False) is True

    def test_smooth_bundle_integrity(self):
        bundle = {
            "species": "chevreuil",
            "corridors": [{"path": _pathological_path()}],
            "salines": [{"lat": 46.0015, "lng": -71.0015}],
        }
        out = smooth_bundle(bundle)
        assert out.get("smoother_applied", "").startswith("X180")
        assert out.get("smoother_total_corridors") == 1
        assert "smoother_rendu_omega" in out
        r = out["smoother_rendu_omega"]
        assert r["color"] == "#FF8F00"
        assert r["weights_allowed_px"] == [1.2, 2.0, 3.0]
        assert r["angle_max_deg"] == ANGLE_MAX_DEG
        assert r["segment_max_m"] == SEGMENT_MAX_M
        assert r["angle_fuite_deg"] == ANGLE_FUITE_DEG

    def test_non_regression_bundle_sans_signal(self):
        """Sans terrain_signals/ia_signals, le smoother ne doit pas déformer
        au-delà des contraintes géométriques."""
        bundle = {"species": "orignal", "corridors": [{"path": _pathological_path()}]}
        out = smooth_bundle(bundle)
        c = out["corridors"][0]
        m = c["smoothing_metrics"]
        assert m["conforme"] is True

    def test_species_profiles_5_especes(self):
        """Verrou : 5 profils exactement, noms canoniques."""
        expected = {"chevreuil", "orignal", "wapiti", "ours", "dindon"}
        assert set(SPECIES_LOCOMOTION.keys()) == expected


# ═══════════════════════════════════════════════════════════════════════
# PASSE 9 — detection zones vitales (AMENDEMENT-FINAL §5)
# ═══════════════════════════════════════════════════════════════════════
class TestPasse9VitalZones:
    def test_detect_salines_proches(self):
        path = [[48.200, -68.380], [48.201, -68.381], [48.202, -68.382]]
        zones = [{"type": "salines", "lat": 48.2015, "lng": -68.3815}]
        conns = detect_vital_zone_connections(path, zones, radius_m=200.0)
        assert len(conns) == 1
        assert conns[0]["type"] == "salines"

    def test_ignore_types_inconnus(self):
        path = [[48.200, -68.380], [48.201, -68.381]]
        zones = [{"type": "objet_non_vital", "lat": 48.2005, "lng": -68.3805}]
        conns = detect_vital_zone_connections(path, zones)
        assert conns == []


# ═══════════════════════════════════════════════════════════════════════
# VERROU RENDU-Ω (AMENDEMENT-FINAL §7)
# ═══════════════════════════════════════════════════════════════════════
class TestVerrouRenduOmega:
    def test_rendu_omega_params_pipeline(self):
        c = {"path": _pathological_path(), "species": "orignal"}
        out = smooth_corridor(c)
        assert out.get("color") == "#FF8F00"
        assert out.get("opacity", 0) >= 0.75
        assert out.get("min_zoom") == 13
        assert out.get("z_index_layer") == "corridors"
