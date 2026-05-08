"""Tests anti-régression — anthropogenic_pressure_omega.py (P4).

NOMS NEUTRES : aucun mot dans BCE_4X_EXCLUDED_KEYWORDS.
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest


def test_phase_xxx_septvicies_module_imports_clean():
    """Module importe sans erreur."""
    from engines.v8_institutional.especes import (
        anthropogenic_pressure_omega as mod)
    assert hasattr(mod, "PRESSURE_DOCTRINE")
    assert hasattr(mod, "validate_anthropogenic_pressure_per_site")
    assert hasattr(mod, "activate_anthropogenic_pressure_hook")
    assert hasattr(mod, "get_anthropogenic_pressure_hook_status")
    assert hasattr(mod, "get_last_validated_pressure_per_site")


def test_phase_xxx_septvicies_doctrine_weights_sum_to_one():
    """Les poids composite Naidoo & Burton 2010 doivent sommer à 1.0."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        PRESSURE_DOCTRINE,
    )
    s = (PRESSURE_DOCTRINE["weight_roads"]
         + PRESSURE_DOCTRINE["weight_population"]
         + PRESSURE_DOCTRINE["weight_buildings"]
         + PRESSURE_DOCTRINE["weight_residential_share"])
    assert abs(s - 1.0) < 1e-9, (
        f"Sum of weights must be 1.0, got {s}")


def test_phase_xxx_septvicies_classification_thresholds_monotonic():
    """Seuils HIGH > MODERATE > LOW (monotonie stricte)."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        PRESSURE_DOCTRINE,
    )
    high = PRESSURE_DOCTRINE["high_pressure_threshold"]
    moderate = PRESSURE_DOCTRINE["moderate_pressure_threshold"]
    low = PRESSURE_DOCTRINE["low_pressure_threshold"]
    assert high > moderate > low > 0


def test_phase_xxx_septvicies_haversine_meters_known_pair():
    """Haversine pour 1° lat ≈ 111 km (sanity check)."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _haversine_length_meters,
    )
    coords = [[-71.0, 46.0], [-71.0, 47.0]]
    d = _haversine_length_meters(coords)
    # Doit être ~ 111 km ± 1%
    assert 110000 < d < 112000


def test_phase_xxx_septvicies_overpass_query_includes_3_filters():
    """Query Overpass doit inclure highway + building + landuse."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _build_overpass_query,
    )
    q = _build_overpass_query(46.5, -71.5, 5000)
    assert '"highway"' in q
    assert '"building"' in q
    assert '"landuse"="residential"' in q
    assert "around:5000,46.5,-71.5" in q
    assert "out:json" in q


def test_phase_xxx_septvicies_classify_pressure_regime_high():
    """Score 90 → HIGH_PRESSURE_AVOID_ZONE."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _classify_pressure_sensitive_zone,
    )
    res = _classify_pressure_sensitive_zone(90.0)
    assert res["regime"] == "HIGH_PRESSURE_AVOID_ZONE"
    assert res["is_pressure_sensitive"] is True


def test_phase_xxx_septvicies_classify_pressure_regime_refuge():
    """Score 10 → REFUGE_FROM_ANTHROPOGENIC_DISTURBANCE."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _classify_pressure_sensitive_zone,
    )
    res = _classify_pressure_sensitive_zone(10.0)
    assert res["regime"] == (
        "REFUGE_FROM_ANTHROPOGENIC_DISTURBANCE")
    assert res["is_pressure_sensitive"] is False


def test_phase_xxx_septvicies_classify_pressure_regime_moderate():
    """Score 60 → MODERATE_PRESSURE_CAUTION."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _classify_pressure_sensitive_zone,
    )
    res = _classify_pressure_sensitive_zone(60.0)
    assert res["regime"] == "MODERATE_PRESSURE_CAUTION"
    assert res["is_pressure_sensitive"] is True


def test_phase_xxx_septvicies_classify_pressure_regime_low():
    """Score 35 → LOW_PRESSURE_MARGINAL."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _classify_pressure_sensitive_zone,
    )
    res = _classify_pressure_sensitive_zone(35.0)
    assert res["regime"] == "LOW_PRESSURE_MARGINAL"
    assert res["is_pressure_sensitive"] is False


def test_phase_xxx_septvicies_composite_invalid_when_one_source_invalid():
    """Composite refuse si une source est invalide (anti-générique)."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _compute_anthropogenic_pressure_index,
    )
    res = _compute_anthropogenic_pressure_index(
        osm_result={"valid": False, "reason": "timeout"},
        worldpop_result={"valid": True,
                          "population_density_per_km2": 10.0},
        buffer_area_km2=78.5)
    assert res["valid"] is False
    assert res["reason"] == "at_least_one_source_invalid"


def test_phase_xxx_septvicies_composite_valid_with_both_sources():
    """Composite calcule correctement avec deux sources valides."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _compute_anthropogenic_pressure_index,
    )
    osm = {
        "valid": True,
        "road_density_km_per_km2": 2.5,  # 50% de saturation
        "building_density_per_km2": 100.0,  # 50% sat
        "residential_landuse_count": 5,  # 25%
    }
    wp = {
        "valid": True,
        "population_density_per_km2": 250.0,  # 50% sat
    }
    res = _compute_anthropogenic_pressure_index(
        osm, wp, buffer_area_km2=78.5)
    assert res["valid"] is True
    # 0.4*50 + 0.3*50 + 0.2*50 + 0.1*25 = 20 + 15 + 10 + 2.5 = 47.5
    assert abs(res["composite_index_0_100"] - 47.5) < 0.5


def test_phase_xxx_septvicies_validation_overlay_exists_post_validate():
    """Après validation live, l'overlay doit exister et contenir history."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        ANTHRO_VALIDATION_PATH,
    )
    if not ANTHRO_VALIDATION_PATH.exists():
        pytest.skip("Aucun overlay encore généré (env propre).")
    state = json.loads(
        ANTHRO_VALIDATION_PATH.read_text(encoding="utf-8"))
    assert "history" in state
    assert isinstance(state["history"], list)
    assert state.get("v30_lock") == "INVIOLÉ"


def test_phase_xxx_septvicies_hook_activation_overlay_when_present():
    """Si l'overlay activation existe, sa structure est doctrinale."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        ANTHRO_HOOK_ACTIVATION_PATH,
    )
    if not ANTHRO_HOOK_ACTIVATION_PATH.exists():
        pytest.skip("Aucun hook activé encore.")
    state = json.loads(
        ANTHRO_HOOK_ACTIVATION_PATH.read_text(encoding="utf-8"))
    assert state.get("v30_lock") == "INVIOLÉ"
    assert "history" in state


def test_phase_xxx_septvicies_get_status_returns_doctrinal_keys():
    """get_anthropogenic_pressure_hook_status retourne keys doctrinales."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        get_anthropogenic_pressure_hook_status,
    )
    status = get_anthropogenic_pressure_hook_status()
    assert status.get("v30_lock") == "INVIOLÉ"
    assert "current_status" in status
    assert "manifest_id" in status


def test_phase_xxx_septvicies_get_last_validated_returns_dict_or_none():
    """get_last_validated_pressure_per_site retourne dict ou None."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        get_last_validated_pressure_per_site,
    )
    res = get_last_validated_pressure_per_site()
    assert res is None or isinstance(res, dict)
    if res is not None:
        assert "manifest_sha256" in res


def test_phase_xxx_septvicies_invalid_coords_raises():
    """Coordonnées invalides → ValueError (anti-générique strict)."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        validate_anthropogenic_pressure_per_site,
    )
    with pytest.raises(ValueError):
        validate_anthropogenic_pressure_per_site(
            site_coordinates={
                "espece_a": {"lat": 999.0, "lon": -71.0}},
            persist=False)


def test_phase_xxx_septvicies_empty_coords_raises():
    """Aucun site → ValueError SITE_COORDINATES_REQUIRED."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        validate_anthropogenic_pressure_per_site,
    )
    with pytest.raises(ValueError, match="SITE_COORDINATES_REQUIRED"):
        validate_anthropogenic_pressure_per_site(
            site_coordinates={}, persist=False)


def test_phase_xxx_septvicies_activate_rejects_unknown_sha():
    """Activation refuse SHA fabriqué (anti-générique)."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        activate_anthropogenic_pressure_hook,
    )
    fake_sha = "0" * 64
    res = activate_anthropogenic_pressure_hook(
        manifest_sha256=fake_sha, persist=False)
    assert res["activated"] is False
    assert "REJECTED" in res["verdict"]


def test_phase_xxx_septvicies_haversine_zero_distance():
    """Haversine sur même point = 0."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _haversine_length_meters,
    )
    d = _haversine_length_meters(
        [[-71.0, 46.0], [-71.0, 46.0]])
    assert d == 0.0


def test_phase_xxx_septvicies_bbox_geojson_polygon_url_encoded():
    """Bbox geojson est URL-encodé et contient 5 points (polygon fermé)."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        _bbox_geojson_polygon,
    )
    encoded = _bbox_geojson_polygon(46.5, -71.5, 0.01)
    import urllib.parse
    decoded = urllib.parse.unquote(encoded)
    poly = json.loads(decoded)
    assert poly["type"] == "Polygon"
    coords = poly["coordinates"][0]
    assert len(coords) == 5  # 4 + closing
    assert coords[0] == coords[-1]
