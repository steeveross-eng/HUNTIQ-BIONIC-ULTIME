"""
BCE-4X-MAX — Tests unitaires ULTRA-MAX++ v3.0 RUNTIME LOCKS
Phase ULTRA-MAX++ — Certification structurelle des 7 verrous

AUTORITE: STEEVE-MAX
DATE: 2026-03-28
PROTOCOLE: BCE-4X / MAX ULTRA / GOLDEN BCE
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from modules.bionic_engine_p0.services.zone_engine_core_v2 import (
    # Constantes verrouillees
    ULTRA_MAX_LOCK_ACTIVE,
    ULTRA_MAX_LOCK_VERSION,
    ULTRA_MAX_LOCK_DATE,
    ULTRA_MAX_LOCK_AUTHORITY,
    BCE4X_URBAN_CACHE_SAFE_MODE,
    META_ANALYSIS_RADIUS_M,
    META_URBAN_THRESHOLD,
    URBAN_OVERLAP_THRESHOLD,
    URBAN_CACHE_BUFFER_DEG,
    WATER_OVERLAP_THRESHOLD,
    CIRCLE_RADIUS_M,
    # Systeme de verrouillage
    ULTRA_MAX_REGISTRY,
    _ultra_max_runtime_guard,
    _ultra_max_boot_guard,
    get_ultra_max_lock_status,
    # Fonctions protegees
    _inject_raw_osm_into_urban_cache,
)


# ══════════════════════════════════════════════════════════════
# VERROU 1: Parametres de cache IMMUTABLES
# ══════════════════════════════════════════════════════════════
class TestVerrou1CacheParams:
    """V1: Les parametres de cache ne peuvent PAS etre modifies."""

    def test_safe_mode_is_true(self):
        assert BCE4X_URBAN_CACHE_SAFE_MODE is True

    def test_urban_cache_buffer(self):
        assert URBAN_CACHE_BUFFER_DEG == 0.002

    def test_registry_has_cache_params(self):
        locked = ULTRA_MAX_REGISTRY._LOCKED_VALUES
        assert locked["BCE4X_URBAN_CACHE_SAFE_MODE"] is True
        assert locked["URBAN_CACHE_BUFFER_DEG"] == 0.002


# ══════════════════════════════════════════════════════════════
# VERROU 2: Pipelines d'exclusion IMMUTABLES
# ══════════════════════════════════════════════════════════════
class TestVerrou2ExclusionPipeline:
    """V2: Les seuils d'exclusion ne peuvent PAS etre modifies."""

    def test_urban_overlap_threshold(self):
        assert URBAN_OVERLAP_THRESHOLD == 0.01

    def test_water_overlap_threshold(self):
        assert WATER_OVERLAP_THRESHOLD == 0.25

    def test_registry_has_exclusion_params(self):
        locked = ULTRA_MAX_REGISTRY._LOCKED_VALUES
        assert locked["URBAN_OVERLAP_THRESHOLD"] == 0.01
        assert locked["WATER_OVERLAP_THRESHOLD"] == 0.25


# ══════════════════════════════════════════════════════════════
# VERROU 3: Pipeline legacy V5 BLOQUE
# ══════════════════════════════════════════════════════════════
class TestVerrou3V5LegacyBlocked:
    """V3: Le pipeline V5 legacy ne peut JAMAIS s'executer."""

    def test_v5_blocked_in_registry(self):
        assert ULTRA_MAX_REGISTRY._LOCKED_VALUES["V5_LEGACY_PIPELINE_BLOCKED"] is True

    def test_exclusion_engine_lock_in_registry(self):
        assert ULTRA_MAX_REGISTRY._LOCKED_VALUES["EXCLUSION_ENGINE_VERSION_LOCKED"] is True


# ══════════════════════════════════════════════════════════════
# VERROU 4: Meta-exclusion 2km/8% INCONTOURNABLE
# ══════════════════════════════════════════════════════════════
class TestVerrou4MetaExclusion:
    """V4: Les parametres meta-exclusion ne peuvent PAS etre modifies."""

    def test_meta_radius_2km(self):
        assert META_ANALYSIS_RADIUS_M == 2000

    def test_meta_threshold_8pct(self):
        assert META_URBAN_THRESHOLD == 0.08

    def test_registry_has_meta_params(self):
        locked = ULTRA_MAX_REGISTRY._LOCKED_VALUES
        assert locked["META_ANALYSIS_RADIUS_M"] == 2000
        assert locked["META_URBAN_THRESHOLD"] == 0.08


# ══════════════════════════════════════════════════════════════
# VERROU 5: SAFE MODE permanent
# ══════════════════════════════════════════════════════════════
class TestVerrou5SafeModePermanent:
    """V5: SAFE MODE est permanent et ne peut JAMAIS etre desactive."""

    def test_safe_mode_permanent_in_registry(self):
        assert ULTRA_MAX_REGISTRY._LOCKED_VALUES["SAFE_MODE_PERMANENT"] is True

    def test_safe_mode_active(self):
        assert BCE4X_URBAN_CACHE_SAFE_MODE is True

    def test_injection_blocked(self):
        """Verifier que l'injection RAW OSM est TOUJOURS bloquee."""
        # Doit retourner None (pas d'injection) sans lever d'exception
        result = _inject_raw_osm_into_urban_cache([{"type": "urban", "sub_type": "test"}])
        assert result is None


# ══════════════════════════════════════════════════════════════
# VERROU 6: Modules V1-V5 bloques
# ══════════════════════════════════════════════════════════════
class TestVerrou6NoV1V5Modules:
    """V6: Aucun module V1-V5 ne peut etre reintroduit."""

    def test_circle_radius_600m(self):
        assert CIRCLE_RADIUS_M == 600

    def test_registry_geometry_lock(self):
        assert ULTRA_MAX_REGISTRY._LOCKED_VALUES["CIRCLE_RADIUS_M"] == 600


# ══════════════════════════════════════════════════════════════
# VERROU 7: Invariant SCORE=0ELEMENT
# ══════════════════════════════════════════════════════════════
class TestVerrou7ScoreZeroElement:
    """V7: L'invariant SCORE=0ELEMENT est verrouille."""

    def test_score_zero_enforced_in_registry(self):
        assert ULTRA_MAX_REGISTRY._LOCKED_VALUES["SCORE_ZERO_ELEMENT_ENFORCED"] is True


# ══════════════════════════════════════════════════════════════
# SYSTEME DE VERROUILLAGE GLOBAL
# ══════════════════════════════════════════════════════════════
class TestUltraMaxLockSystem:
    """Tests du systeme de verrouillage ULTRA-MAX++ v3.0."""

    def test_lock_active(self):
        assert ULTRA_MAX_LOCK_ACTIVE is True

    def test_lock_version_3(self):
        assert ULTRA_MAX_LOCK_VERSION == "3.0"

    def test_lock_authority(self):
        assert ULTRA_MAX_LOCK_AUTHORITY == "STEEVE-MAX"

    def test_lock_date(self):
        assert ULTRA_MAX_LOCK_DATE == "2026-03-28"

    def test_runtime_guard_passes(self):
        """La garde runtime doit passer sans exception quand tout est intact."""
        result = _ultra_max_runtime_guard()
        assert result is True

    def test_boot_guard_passes(self):
        """Le boot guard doit passer sans exception."""
        _ultra_max_boot_guard()

    def test_lock_status_complete(self):
        """Le statut de verrouillage doit etre complet."""
        status = get_ultra_max_lock_status()
        assert status["ultra_max_version"] == "3.0"
        assert status["ultra_max_authority"] == "STEEVE-MAX"
        assert status["all_locks_active"] is True
        locks = status["locks"]
        assert locks["V1_cache_params_locked"] is True
        assert locks["V2_exclusion_pipeline_locked"] is True
        assert locks["V3_v5_legacy_blocked"] is True
        assert locks["V4_meta_exclusion_2km_8pct"] is True
        assert locks["V5_safe_mode_permanent"] is True
        assert locks["V6_v1v5_module_blocked"] is True
        assert locks["V7_score_zero_element"] is True

    def test_registry_has_12_constants(self):
        """Le registre doit contenir exactement 12 constantes verrouillees."""
        assert len(ULTRA_MAX_REGISTRY._LOCKED_VALUES) == 12

    def test_registry_validate_constant(self):
        """La validation d'une constante intacte doit reussir."""
        assert ULTRA_MAX_REGISTRY.validate_constant("BCE4X_URBAN_CACHE_SAFE_MODE", True) is True

    def test_registry_validate_tampered_constant(self):
        """La validation d'une constante alteree doit echouer."""
        result = ULTRA_MAX_REGISTRY.validate_constant("BCE4X_URBAN_CACHE_SAFE_MODE", False)
        assert result is False

    def test_registry_attempt_modify_when_sealed(self):
        """Toute tentative de modification apres scellement doit lever RuntimeError."""
        # Forcer le scellement si pas deja fait
        if not ULTRA_MAX_REGISTRY.is_sealed():
            ULTRA_MAX_REGISTRY.seal()
        with pytest.raises(RuntimeError, match="ULTRA-MAX\\+\\+ LOCK"):
            ULTRA_MAX_REGISTRY.attempt_modify("BCE4X_URBAN_CACHE_SAFE_MODE", False)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
