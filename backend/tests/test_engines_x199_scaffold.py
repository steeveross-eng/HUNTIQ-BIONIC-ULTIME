"""
Tests structurels X199 — scaffolding 10 engines + façade V30 miroir
"""
import sys
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path("/app/backend")))

import pytest


ENGINES_X199 = [
    ("reseau_veineux_omega",     "/api/v7-ultime/reseau-veineux/compute"),
    ("eco_zones_omega",          "/api/v7-ultime/eco-zones/compute"),
    ("bio_scoring_omega",        "/api/v7-ultime/bio-scoring/compute"),
    ("hydro_topo_omega",         "/api/v7-ultime/hydro-topo/compute"),
    ("ecoforestry_omega",        "/api/v7-ultime/ecoforestry/compute"),
    ("terrain_3d_omega",         "/api/v7-ultime/terrain-3d/compute"),
    ("wildlife_behavior_omega",  "/api/v7-ultime/wildlife-behavior/compute"),
    ("legal_time_omega",         "/api/v7-ultime/legal-time/compute"),
    ("predictive_omega",         "/api/v7-ultime/predictive/compute"),
    ("advanced_geospatial_omega","/api/v7-ultime/advanced-geospatial/compute"),
]


@pytest.mark.parametrize("slug,prefix", ENGINES_X199)
def test_engine_package_importable(slug, prefix):
    mod = __import__(f"engines.{slug}", fromlist=["router", "FEATURE_FLAG_ACTIVE"])
    assert hasattr(mod, "router"), f"{slug} missing router"
    assert hasattr(mod, "FEATURE_FLAG_ACTIVE"), f"{slug} missing feature flag"


@pytest.mark.parametrize("slug,prefix", ENGINES_X199)
def test_feature_flag_off_by_default(slug, prefix):
    mod = __import__(f"engines.{slug}", fromlist=["FEATURE_FLAG_ACTIVE"])
    assert mod.FEATURE_FLAG_ACTIVE is False, (
        f"{slug} feature flag MUST be OFF in X199-PREPARATOIRE"
    )


@pytest.mark.parametrize("slug,prefix", ENGINES_X199)
def test_router_prefix_matches_spec(slug, prefix):
    mod = __import__(f"engines.{slug}", fromlist=["router"])
    assert mod.router.prefix == prefix


def test_10_engines_generated():
    engines_root = Path("/app/backend/engines")
    for slug, _ in ENGINES_X199:
        p = engines_root / slug
        assert p.is_dir(), f"Engine package {slug} missing"
        assert (p / "__init__.py").exists()
        assert (p / "router.py").exists()


# ═══════════════════════════════════════════════════════════════════════
# FAÇADE V30 MIROIR
# ═══════════════════════════════════════════════════════════════════════
def test_v30_mirror_module_importable():
    from engines.bio_scoring_omega import v30_mirror_read_only as m
    assert hasattr(m, "FEATURE_FLAG_ACTIVE")
    assert hasattr(m, "V30_EXPECTED_SHA256")
    assert hasattr(m, "assert_v30_integrity")
    assert hasattr(m, "mirror_read")


def test_v30_mirror_feature_flag_off():
    from engines.bio_scoring_omega import v30_mirror_read_only as m
    assert m.FEATURE_FLAG_ACTIVE is False


def test_v30_mirror_sha256_invariant():
    """V30 doit être strictement identique au SHA-256 attendu."""
    from engines.bio_scoring_omega import v30_mirror_read_only as m
    status = m.assert_v30_integrity()
    assert status["invariant"] is True, (
        f"V30 INTEGRITY BREACH — expected {status['expected']}, got {status['v30_sha256']}"
    )
    assert status["breach"] is False


def test_v30_mirror_read_blocks_when_flag_off():
    from engines.bio_scoring_omega import v30_mirror_read_only as m
    r = m.mirror_read("cost_surface", 48.206657, -68.382422, "orignal")
    assert r["available"] is False
    assert r["reason"] == "feature_flag_off"


def test_v30_mirror_read_unknown_field():
    from engines.bio_scoring_omega import v30_mirror_read_only as m
    r = m.mirror_read("invalid_field", 48.206657, -68.382422)
    assert r["available"] is False
    assert r["reason"] == "field_not_mirrored"


def test_v30_file_not_modified_by_mirror_call():
    """Même en appelant mirror_read, V30 ne doit jamais être modifié sur disque."""
    from engines.bio_scoring_omega import v30_mirror_read_only as m
    before = m._compute_v30_sha256()
    _ = m.mirror_read("cost_surface", 48.2, -68.4, "orignal")
    _ = m.mirror_read("ecl", 48.2, -68.4, "orignal")
    _ = m.mirror_read("canopy_density", 48.2, -68.4, "orignal")
    after = m._compute_v30_sha256()
    assert before == after, "V30 file was modified during mirror calls — VIOLATION"
