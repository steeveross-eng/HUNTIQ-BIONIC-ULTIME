"""
BCE-4X-MAX — Tests unitaires META-EXCLUSION et exclusions ULTIMES
Phase 3.2-CV v2 — Certification structurelle
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from modules.bionic_engine_p0.services.zone_engine_core_v2 import (
    _circle_on_urban,
    _circle_on_water,
    center_in_urban_meta_zone,
    META_ANALYSIS_RADIUS_M,
    META_URBAN_THRESHOLD,
    URBAN_OVERLAP_THRESHOLD,
    BCE4X_URBAN_CACHE_SAFE_MODE,
)

# ══════════════════════════════════════════════════════════════
# CONSTANTES DE TEST
# ══════════════════════════════════════════════════════════════
# Zone urbaine Quebec centre-ville
URBAN_CENTER = (46.8139, -71.208)
# Zone portuaire Beauport (ancienne breche)
URBAN_BEAUPORT = (46.84, -71.19)
# Zone Beauport Est
URBAN_BEAUPORT_EST = (46.838, -71.175)
# Zone foret profonde Lac Jacques-Cartier
FOREST_DEEP = (47.25, -71.40)
# Zone foret Nord
FOREST_NORD = (47.30, -71.35)


class TestSafeModeInvariant:
    """Verifier que SAFE MODE est un invariant permanent."""

    def test_safe_mode_is_true(self):
        assert BCE4X_URBAN_CACHE_SAFE_MODE is True, "SAFE MODE doit etre TRUE en permanence"

    def test_meta_radius_is_2km(self):
        assert META_ANALYSIS_RADIUS_M == 2000, "Le rayon meta-analyse doit etre 2000m (2km)"

    def test_meta_threshold_is_8_percent(self):
        assert META_URBAN_THRESHOLD == 0.08, "Le seuil meta doit etre 8%"

    def test_urban_overlap_threshold_is_1_percent(self):
        assert URBAN_OVERLAP_THRESHOLD == 0.01, "Le seuil overlap individuel doit etre 1%"


class TestMetaExclusionUrban:
    """Verifier que TOUTES les zones urbaines sont rejetees par la meta-exclusion."""

    def test_quebec_centre_ville_is_urban(self):
        result = center_in_urban_meta_zone(*URBAN_CENTER)
        assert result is True, f"Quebec Centre-Ville ({URBAN_CENTER}) DOIT etre rejete"

    def test_beauport_port_is_urban(self):
        result = center_in_urban_meta_zone(*URBAN_BEAUPORT)
        assert result is True, f"Beauport Port ({URBAN_BEAUPORT}) DOIT etre rejete"

    def test_beauport_est_is_urban(self):
        result = center_in_urban_meta_zone(*URBAN_BEAUPORT_EST)
        assert result is True, f"Beauport Est ({URBAN_BEAUPORT_EST}) DOIT etre rejete"


class TestMetaExclusionForest:
    """Verifier que les zones forestieres ne sont PAS rejetees."""

    def test_lac_jacques_cartier_is_forest(self):
        result = center_in_urban_meta_zone(*FOREST_DEEP)
        assert result is False, f"Lac Jacques-Cartier ({FOREST_DEEP}) ne doit PAS etre rejete"

    def test_foret_nord_is_forest(self):
        result = center_in_urban_meta_zone(*FOREST_NORD)
        assert result is False, f"Foret Nord ({FOREST_NORD}) ne doit PAS etre rejete"


class TestIndividualExclusionUrban:
    """Verifier les exclusions individuelles (600m circle)."""

    def test_circle_on_urban_centre_ville(self):
        result = _circle_on_urban(*URBAN_CENTER)
        assert result is True, f"Circle check centre-ville DOIT retourner True"

    def test_circle_on_urban_forest(self):
        result = _circle_on_urban(*FOREST_DEEP)
        assert result is False, f"Circle check foret DOIT retourner False"


class TestWaterExclusion:
    """Verifier les exclusions eau."""

    def test_circle_on_water_forest(self):
        result = _circle_on_water(*FOREST_DEEP)
        assert result is False, f"Foret ne doit PAS etre consideree comme eau"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
