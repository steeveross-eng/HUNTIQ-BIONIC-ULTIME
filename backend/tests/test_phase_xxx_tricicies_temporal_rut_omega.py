"""Tests anti-régression — temporal_rut_data_omega.py (P6).

NOMS NEUTRES : aucun mot dans BCE_4X_EXCLUDED_KEYWORDS.
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
"""
from __future__ import annotations

import json

import pytest


def test_phase_xxx_tricicies_module_imports_clean():
    from engines.v8_institutional.especes import (
        temporal_rut_data_omega as mod)
    assert hasattr(mod, "RUT_SEASONS_DOCTRINAL")
    assert hasattr(mod, "RUT_COMPOSITE_WEIGHTS")
    assert hasattr(mod, "validate_temporal_rut_data_per_site")
    assert hasattr(mod, "activate_temporal_rut_data_hook")
    assert hasattr(mod, "get_temporal_rut_data_hook_status")
    assert hasattr(mod, "get_last_validated_rut_per_site")


def test_phase_xxx_tricicies_seasons_5_species_present():
    """5 espèces canoniques BP135 doivent avoir saisons doctrinales."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        RUT_SEASONS_DOCTRINAL,
    )
    for sp in ("cerf", "orignal", "ours", "dindon", "wapiti"):
        assert sp in RUT_SEASONS_DOCTRINAL
        season = RUT_SEASONS_DOCTRINAL[sp]
        assert "rut_months" in season
        assert "rut_doy_start" in season
        assert "rut_doy_end" in season
        assert "gbif_taxon_key" in season
        assert "primary_reference" in season
        assert season["rut_doy_start"] < season["rut_doy_end"]


def test_phase_xxx_tricicies_composite_weights_sum_to_one():
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        RUT_COMPOSITE_WEIGHTS,
    )
    s = sum(RUT_COMPOSITE_WEIGHTS.values())
    assert abs(s - 1.0) < 1e-9


def test_phase_xxx_tricicies_solar_declination_summer_solstice():
    """Déclinaison ~+23.4° au solstice été (DOY 172, ~21 juin)."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _solar_declination_deg,
    )
    decl = _solar_declination_deg(172)
    assert 22.0 < decl < 24.0


def test_phase_xxx_tricicies_solar_declination_winter_solstice():
    """Déclinaison ~-23.4° au solstice hiver (DOY 355, ~21 déc)."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _solar_declination_deg,
    )
    decl = _solar_declination_deg(355)
    assert -24.0 < decl < -22.0


def test_phase_xxx_tricicies_daylength_quebec_summer():
    """Daylength Québec (lat=46.8) été ≈ 15-16h."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _daylength_hours,
    )
    dl = _daylength_hours(46.8, 172)  # solstice été
    assert 15.0 < dl < 16.5


def test_phase_xxx_tricicies_daylength_equator_constant():
    """Daylength équateur ~12h toute l'année."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _daylength_hours,
    )
    dl_summer = _daylength_hours(0.0, 172)
    dl_winter = _daylength_hours(0.0, 355)
    assert 11.5 < dl_summer < 12.5
    assert 11.5 < dl_winter < 12.5


def test_phase_xxx_tricicies_photoperiod_signal_autumn_decline():
    """Photopériode rut automne (cerf oct-nov) doit montrer decline."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _photoperiod_signal_for_rut_window,
    )
    res = _photoperiod_signal_for_rut_window(46.8, 274, 334)
    assert res["valid"] is True
    # Daylight diminue d'oct à nov à mid-latitude → rate < 0
    assert res["rate_change_h_per_day"] < 0


def test_phase_xxx_tricicies_score_gbif_count_zero():
    """GBIF count=0 → score=0, regime=ABSENT."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _score_gbif_rut_count,
    )
    res = _score_gbif_rut_count(0)
    assert res["score_0_100"] == 0.0
    assert res["regime"] == "ABSENT_NO_GBIF_RUT_OBSERVATIONS"


def test_phase_xxx_tricicies_score_gbif_count_high_saturation():
    """GBIF count=100 → score>=99 (log saturation)."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _score_gbif_rut_count,
    )
    res = _score_gbif_rut_count(100)
    assert res["score_0_100"] >= 99.0
    assert res["regime"] == "HIGH_RUT_PRESENCE_DOCUMENTED"


def test_phase_xxx_tricicies_composite_invalid_when_all_pillars_invalid():
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _compute_rut_zones_composite,
    )
    res = _compute_rut_zones_composite(
        photoperiod={"valid": False},
        ndvi_fall={"valid": False},
        gbif_presence={"valid": False},
    )
    assert res["valid"] is False
    assert res["reason"] == "all_three_pillars_invalid"


def test_phase_xxx_tricicies_composite_with_3_valid_pillars():
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _compute_rut_zones_composite,
    )
    res = _compute_rut_zones_composite(
        photoperiod={
            "valid": True,
            "score_0_100": 80.0,
            "regime": "OPTIMAL_PHOTOPERIOD_DECLINE_AUTUMNAL",
        },
        ndvi_fall={
            "valid": True,
            "ndvi_fall_score_0_100": 70.0,
            "regime": "OPTIMAL_RUT_PRE_PHENOLOGY",
        },
        gbif_presence={
            "valid": True,
            "total_count_in_window": 30,
        },
    )
    assert res["valid"] is True
    assert res["n_pillars_valid"] == 3
    assert 0 < res["composite_score_0_100"] <= 100


def test_phase_xxx_tricicies_composite_with_partial_pillars_renormalize():
    """Composite avec 2/3 piliers : weights renormalisés, valide."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        _compute_rut_zones_composite,
    )
    res = _compute_rut_zones_composite(
        photoperiod={
            "valid": True,
            "score_0_100": 60.0,
            "regime": "TEST",
        },
        ndvi_fall={"valid": False},
        gbif_presence={
            "valid": True,
            "total_count_in_window": 50,
        },
    )
    assert res["valid"] is True
    assert res["n_pillars_valid"] == 2
    # Weights renormalisés (0.25 + 0.35 = 0.60)
    assert (
        abs(res["weights_doctrinal_renormalized"] - 0.60)
        < 0.001)


def test_phase_xxx_tricicies_activate_rejects_unknown_sha():
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        activate_temporal_rut_data_hook,
    )
    fake = "f" * 64
    res = activate_temporal_rut_data_hook(
        manifest_sha256=fake, persist=False)
    assert res["activated"] is False
    assert "REJECTED" in res["verdict"]


def test_phase_xxx_tricicies_get_status_returns_keys():
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        get_temporal_rut_data_hook_status,
    )
    s = get_temporal_rut_data_hook_status()
    assert s.get("v30_lock") == "INVIOLÉ"
    assert "current_status" in s


def test_phase_xxx_tricicies_overlays_when_present():
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        RUT_VALIDATION_PATH,
        RUT_HOOK_ACTIVATION_PATH,
    )
    if RUT_VALIDATION_PATH.exists():
        state = json.loads(
            RUT_VALIDATION_PATH.read_text(encoding="utf-8"))
        assert state.get("v30_lock") == "INVIOLÉ"
        assert "history" in state
    if RUT_HOOK_ACTIVATION_PATH.exists():
        state = json.loads(
            RUT_HOOK_ACTIVATION_PATH.read_text(
                encoding="utf-8"))
        assert state.get("v30_lock") == "INVIOLÉ"
        assert "history" in state


def test_phase_xxx_tricicies_get_last_validated_returns_dict_or_none():
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        get_last_validated_rut_per_site,
    )
    res = get_last_validated_rut_per_site()
    assert res is None or isinstance(res, dict)
    if res is not None:
        assert "manifest_sha256" in res
