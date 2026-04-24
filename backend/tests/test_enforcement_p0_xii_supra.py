"""
test_enforcement_p0_xii_supra.py
================================================================================
PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME_ENFORCEMENT_P0
Tests institutionnels pour la correction des 8 violations critiques.

NO TESTING AGENT. Manual pytest only.
"""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

# Autoriser le post-processor veineux
os.environ["VEINEUX_OMEGA_AUTHORIZED_BY_COMMANDANT"] = "true"
os.environ["VEINEUX_OMEGA_COMMANDANT_TOKEN"] = "STEEVE-MAX-XII-VEINEUX-EXPLICIT"

from engines.post_smoothing import baseline_registry_omega as brg  # noqa: E402
from engines.post_smoothing import veineux_omega as vo  # noqa: E402


# ═══════════════════════════════════════════════════════════════════════
# §1 — BASELINE REGISTRY (IMMUABLE + SHA-256)
# ═══════════════════════════════════════════════════════════════════════
def test_baseline_is_frozen_at_3670():
    b = brg.get_baseline()
    assert b["v30_alignment_score_baseline"] == 36.70
    assert b["alignment_label_baseline"] == "NON_CONFORME"
    assert b["accepted_baseline"] == 19
    assert b["total_baseline"] == 44
    assert b["acceptance_rate_baseline_pct"] == 43.18


def test_baseline_sha256_is_deterministic_and_stable():
    b1 = brg.get_baseline()
    b2 = brg.get_baseline()
    assert b1["sha256"] == b2["sha256"]
    assert len(b1["sha256"]) == 64
    assert b1["immutable"] is True


def test_baseline_thresholds_match_directive():
    b = brg.get_baseline()
    t = b["thresholds"]
    assert t["conform_min"] == 70.0
    assert t["conform_omega_min"] == 90.0


# ═══════════════════════════════════════════════════════════════════════
# §6.1/§6.2 — GRILLE INSTITUTIONNELLE + INTERDICTION "BON"
# ═══════════════════════════════════════════════════════════════════════
def test_label_partial_below_70():
    assert brg.alignment_label_institutional(0.0) == "PARTIEL"
    assert brg.alignment_label_institutional(36.70) == "PARTIEL"
    assert brg.alignment_label_institutional(60.56) == "PARTIEL"
    assert brg.alignment_label_institutional(69.99) == "PARTIEL"


def test_label_conforme_at_70_to_89():
    assert brg.alignment_label_institutional(70.0) == "CONFORME"
    assert brg.alignment_label_institutional(85.0) == "CONFORME"
    assert brg.alignment_label_institutional(89.99) == "CONFORME"


def test_label_conforme_omega_at_90_and_above():
    assert brg.alignment_label_institutional(90.0) == "CONFORME_Ω"
    assert brg.alignment_label_institutional(100.0) == "CONFORME_Ω"


def test_label_bon_is_forbidden():
    import pytest
    for forbidden in ("BON", "MODERE", "FAIBLE", "EXCELLENT", "MOYEN"):
        with pytest.raises(ValueError):
            brg.assert_label_institutional(forbidden)


def test_label_authorized_passes():
    for ok in ("PARTIEL", "CONFORME", "CONFORME_Ω"):
        # ne doit pas lever
        brg.assert_label_institutional(ok)


# ═══════════════════════════════════════════════════════════════════════
# §7.2 — ROLLBACK AUTOMATIQUE si score < baseline
# ═══════════════════════════════════════════════════════════════════════
def test_rollback_required_when_below_baseline():
    v = brg.compare_to_baseline(20.0)
    assert v["below_baseline"] is True
    assert v["rollback_required"] is True
    assert v["delta_score"] < 0


def test_rollback_not_required_when_above_baseline():
    v = brg.compare_to_baseline(100.0)
    assert v["below_baseline"] is False
    assert v["rollback_required"] is False
    assert v["delta_score"] == 63.30


def test_rollback_at_exact_baseline_is_not_triggered():
    v = brg.compare_to_baseline(36.70)
    # À l'égalité stricte, pas de rollback (dégradation = STRICTEMENT sous)
    assert v["below_baseline"] is False
    assert v["rollback_required"] is False


# ═══════════════════════════════════════════════════════════════════════
# §4.1/§4.2 — EXCLUSION CONTAM STRICTE
# ═══════════════════════════════════════════════════════════════════════
def test_avoid_contamination_zones_pushes_points_outside_buffer():
    path = [
        [48.2000, -68.3800],
        [48.2001, -68.3800],  # proche mais pas sur le centre
        [48.2010, -68.3800],
    ]
    contam = [{"lat": 48.2005, "lng": -68.3800}]
    out = vo._avoid_contamination_zones(path, contam, buffer_m=60.0)
    assert len(out) == len(path)
    # Le point central doit être repoussé hors de la sphère d'exclusion
    dist = vo._distance_m(out[1], [48.2005, -68.3800])
    assert dist >= 59.0, f"contam point non repoussé suffisamment : d={dist}"


def test_avoid_contamination_empty_list_noop():
    path = [[48.2, -68.38], [48.21, -68.38]]
    out = vo._avoid_contamination_zones(path, [], buffer_m=60.0)
    assert out == path


def test_bundle_exposes_contam_stats():
    bundle = {
        "corridors": [
            {"id": "c1", "path": [[48.200, -68.380], [48.205, -68.380], [48.208, -68.378]]},
        ],
        "contamination_zones": [{"lat": 48.205, "lng": -68.380}],
        "species": "orignal",
    }
    out = vo.apply_veineux_omega_to_bundle(bundle)
    stats = out.get("veineux_omega_stats", {})
    assert stats.get("contam_avoidance_buffer_m") == vo.CONTAM_AVOIDANCE_BUFFER_M
    assert stats.get("contam_zones_considered") == 1


# ═══════════════════════════════════════════════════════════════════════
# §2.1/§2.2 — COULEUR UNIQUE #FF8F00 (backend-side)
# ═══════════════════════════════════════════════════════════════════════
def test_veineux_corridors_do_not_inject_color_field():
    """Les corridors veineux ne doivent JAMAIS porter de champ 'color' legacy
    (qui pourrait court-circuiter RENDU_OMEGA.color = '#FF8F00')."""
    bundle = {
        "corridors": [
            {"id": "c", "path": [[48.200, -68.380], [48.205, -68.380], [48.208, -68.378]]},
        ],
        "species": "orignal",
    }
    out = vo.apply_veineux_omega_to_bundle(bundle)
    for c in out.get("corridors", []):
        assert "color" not in c or c.get("color") in (None, "#FF8F00"), \
            f"corridor {c.get('id')} porte color={c.get('color')} (legacy)"
