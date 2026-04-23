"""
test_x200_p2_integration.py
===========================
Phase : PHASE_X200_P2_INTEGRATION_Ω
Commandant STEEVE-MAX

Couvre :
  - Axe 1 : synchronisation MFFP 2026 (legal_time_omega) — weapons/subzones.
  - Axe 2 : agrégation predictive_omega → smoother X180
            (corridor_probability_omega + pondération COMMANDANT 6/4/3/2/1).
"""
from datetime import date

import pytest


# ═══════════════════════════════════════════════════════════════════════
# AXE 1 — LEGAL_TIME SYNC MFFP 2026
# ═══════════════════════════════════════════════════════════════════════
def test_mffp_catalogue_version_stamped():
    from engines.legal_time_omega.router import (
        MFFP_CATALOGUE_VERSION, SEASONS_MFFP_2026,
    )
    assert MFFP_CATALOGUE_VERSION == "MFFP_2026_ZONE_2_BSL_X200_P2_SYNC_Ω"
    assert set(SEASONS_MFFP_2026.keys()) == {
        "orignal", "chevreuil", "cerf", "ours", "dindon", "wapiti",
    }


def test_mffp_wapiti_not_admissible_zone_2():
    from engines.legal_time_omega.router import SEASONS_MFFP_2026, is_legal
    assert SEASONS_MFFP_2026["wapiti"] == []
    r = is_legal("wapiti", date(2026, 10, 1))
    assert r["legal"] is False
    assert r["reason"] == "species_not_allowed_in_zone"


def test_mffp_orignal_arc_starts_earlier_than_carabine():
    """L'arc ouvre avant la carabine pour l'orignal en zone 2 BSL."""
    from engines.legal_time_omega.router import is_legal
    # 13 septembre 2026 : arc ouvert, carabine fermée
    d = date(2026, 9, 13)
    r_arc = is_legal("orignal", d, weapon="arc")
    r_car = is_legal("orignal", d, weapon="carabine")
    assert r_arc["legal"] is True
    assert r_car["legal"] is False


def test_mffp_chevreuil_subzone_2a_only_for_carabine():
    """Carabine chevreuil : sous-zone 2A uniquement (subzone "all" n'est pas couverte)."""
    from engines.legal_time_omega.router import is_legal
    d = date(2026, 11, 15)
    r_2a = is_legal("chevreuil", d, weapon="carabine", subzone="2A")
    r_2b = is_legal("chevreuil", d, weapon="carabine", subzone="2B")
    assert r_2a["legal"] is True
    # 2B n'est pas dans la liste autorisée pour la carabine → illégal
    assert r_2b["legal"] is False


def test_mffp_ours_two_windows():
    from engines.legal_time_omega.router import is_legal
    assert is_legal("ours", date(2026, 6, 1),  weapon="carabine")["legal"] is True
    assert is_legal("ours", date(2026, 9, 15), weapon="carabine")["legal"] is True
    assert is_legal("ours", date(2026, 7, 15), weapon="carabine")["legal"] is False


def test_mffp_catalogue_version_embedded_in_response():
    from engines.legal_time_omega.router import is_legal
    r = is_legal("orignal", date(2026, 10, 1))
    assert r["catalogue_version"] == "MFFP_2026_ZONE_2_BSL_X200_P2_SYNC_Ω"


def test_mffp_weapons_allowed_listed_when_legal():
    from engines.legal_time_omega.router import is_legal
    r = is_legal("orignal", date(2026, 9, 20))  # arc+carabine+arbalete actifs
    assert r["legal"] is True
    assert set(r["weapons_allowed"]).issuperset({"arc", "carabine", "arbalete"})


# ═══════════════════════════════════════════════════════════════════════
# AXE 2 — PREDICTIVE INTEGRATION P2
# ═══════════════════════════════════════════════════════════════════════
def _enable_p2(monkeypatch):
    monkeypatch.setenv("P2_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P2_COMMANDANT_TOKEN", "STEEVE-MAX-X200-P2-EXPLICIT")


def test_p2_flag_on_by_default():
    from engines.post_smoothing.predictive_integration import (
        P2_PREDICTIVE_INTEGRATION_ENABLED,
    )
    assert P2_PREDICTIVE_INTEGRATION_ENABLED is True


def test_p2_auth_fails_without_token(monkeypatch):
    monkeypatch.setenv("P2_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P2_COMMANDANT_TOKEN", "WRONG")
    from engines.post_smoothing.predictive_integration import is_p2_authorized
    assert is_p2_authorized()["authorized"] is False


def test_p2_auth_ok_with_token(monkeypatch):
    _enable_p2(monkeypatch)
    from engines.post_smoothing.predictive_integration import is_p2_authorized
    assert is_p2_authorized()["authorized"] is True


def test_commandant_weight_map_6_4_3_2_1():
    from engines.post_smoothing.predictive_integration import (
        COMMANDANT_WEIGHT_MAP, MAX_COMMANDANT_WEIGHT,
    )
    assert COMMANDANT_WEIGHT_MAP == {
        "CRITIQUE": 6, "MAJEUR": 4, "FORT": 3, "MODERE": 2, "FAIBLE": 1,
    }
    assert MAX_COMMANDANT_WEIGHT == 6


def test_apply_predictive_to_single_path_produces_probability(monkeypatch):
    _enable_p2(monkeypatch)
    from engines.post_smoothing.predictive_integration import apply_predictive_to_corridor
    c = {
        "id": "c1",
        "path": [[48.206, -68.382], [48.207, -68.383], [48.208, -68.384]],
        "level_commandant": "FORT",
    }
    out = apply_predictive_to_corridor(c, species="orignal", hour=7, iso_date="2026-10-01")
    assert 0.0 <= out["corridor_probability_omega"] <= 1.0
    comp = out["corridor_probability_components"]
    assert comp["commandant_level"] == "FORT"
    assert comp["commandant_weight"] == 3
    assert comp["hierarchical_factor"] == round(3 / 6, 4)


def test_hierarchical_weighting_ordering(monkeypatch):
    """Deux corridors identiques sauf niveau → CRITIQUE > FAIBLE."""
    _enable_p2(monkeypatch)
    from engines.post_smoothing.predictive_integration import apply_predictive_to_corridor
    path = [[48.206, -68.382], [48.207, -68.383], [48.208, -68.384]]
    crit = apply_predictive_to_corridor(
        {"id": "crit", "path": path, "level_commandant": "CRITIQUE"},
        species="orignal", hour=7, iso_date="2026-10-01",
    )
    faible = apply_predictive_to_corridor(
        {"id": "faible", "path": path, "level_commandant": "FAIBLE"},
        species="orignal", hour=7, iso_date="2026-10-01",
    )
    assert crit["corridor_probability_omega"] > faible["corridor_probability_omega"]
    # Ratio hiérarchique = 6/1 = 6
    comp_c = crit["corridor_probability_components"]
    comp_f = faible["corridor_probability_components"]
    assert comp_c["commandant_weight"] == 6
    assert comp_f["commandant_weight"] == 1


def test_apply_predictive_to_bundle_diagnostic(monkeypatch):
    _enable_p2(monkeypatch)
    from engines.post_smoothing.predictive_integration import apply_predictive_to_bundle
    bundle = {
        "species": "orignal", "hour": 7, "date": "2026-10-01",
        "corridors": [
            {"id": "c1", "path": [[48.206, -68.382], [48.207, -68.383]], "level_commandant": "CRITIQUE"},
            {"id": "c2", "path": [[48.206, -68.382], [48.207, -68.383]], "level_commandant": "FORT"},
            {"id": "c3", "path": [[48.206, -68.382], [48.207, -68.383]], "level_v7":        "FAIBLE"},
        ],
    }
    out = apply_predictive_to_bundle(bundle)
    diag = out["p2_predictive_integration"]
    assert diag["status"] == "APPLIED"
    assert diag["totals"]["corridors_processed"] == 3
    assert 0.0 <= diag["totals"]["mean_probability_omega"] <= 1.0
    assert diag["v30_engine_touched"] is False
    assert diag["zones_or_salines_modified"] is False
    for c in out["corridors"]:
        assert "corridor_probability_omega" in c


def test_p2_bypass_when_not_authorized(monkeypatch):
    monkeypatch.setenv("P2_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "false")
    monkeypatch.delenv("P2_COMMANDANT_TOKEN", raising=False)
    from engines.post_smoothing.predictive_integration import apply_predictive_to_bundle
    bundle = {
        "corridors": [{"id": "c1", "path": [[48.2, -68.3], [48.21, -68.31]]}]
    }
    out = apply_predictive_to_bundle(bundle)
    assert out["p2_predictive_integration"]["status"] == "BYPASSED"
    assert "corridor_probability_omega" not in out["corridors"][0]


def test_smoother_exposes_p2_integrated(monkeypatch):
    _enable_p2(monkeypatch)
    # P1 déjà ON par env + token (scaffold test_credentials)
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_HISTORICAL_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXPLICIT")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXTERNAL-INFLOW")
    from engines.post_smoothing.organic_corridor_smoother import smooth_bundle
    bundle = {
        "species": "orignal", "hour": 7, "date": "2026-10-01",
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [{
            "id": "c1",
            "path": [
                [48.2065, -68.3820], [48.2070, -68.3828], [48.2076, -68.3835],
            ],
        }],
    }
    out = smooth_bundle(bundle)
    assert out["smoother_p2_predictive_integrated"] is True
    assert out["p2_predictive_integration"]["status"] == "APPLIED"
    for c in out["corridors"]:
        assert 0.0 <= c["corridor_probability_omega"] <= 1.0


def test_p2_does_not_modify_zones_or_salines(monkeypatch):
    _enable_p2(monkeypatch)
    from engines.post_smoothing.predictive_integration import apply_predictive_to_bundle
    bundle = {
        "corridors": [{"id": "c1", "path": [[48.2, -68.3], [48.21, -68.31]]}],
        "vital_zones": [{"type": "salines", "lat": 48.2, "lng": -68.3}],
        "salines":     [{"lat": 48.21, "lng": -68.31}],
    }
    import copy
    vz_before = copy.deepcopy(bundle["vital_zones"])
    sa_before = copy.deepcopy(bundle["salines"])
    out = apply_predictive_to_bundle(bundle)
    assert out["vital_zones"] == vz_before
    assert out["salines"] == sa_before


def test_p2_does_not_import_v30(monkeypatch):
    _enable_p2(monkeypatch)
    import sys
    before = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    from engines.post_smoothing.predictive_integration import apply_predictive_to_bundle
    apply_predictive_to_bundle({
        "corridors": [{"id": "c1", "path": [[48.2, -68.3], [48.21, -68.31]]}]
    })
    after = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    assert before == after
