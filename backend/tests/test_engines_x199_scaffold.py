"""
Tests structurels X199/X200 — post-activation P0
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path("/app/backend")))

import pytest

# Engines P0 ACTIVÉS (feature flag ON) — X200-P0-ACTIVATION
ENGINES_P0_ACTIVE = [
    ("wildlife_behavior_omega",  "/api/v7-ultime/wildlife-behavior"),
    ("eco_zones_omega",          "/api/v7-ultime/eco-zones"),
    ("hydro_topo_omega",         "/api/v7-ultime/hydro-topo"),
    ("reseau_veineux_omega",     "/api/v7-ultime/reseau-veineux"),
    ("bio_scoring_omega",        "/api/v7-ultime/bio-scoring"),
]
# Engines X199 étendus qui DOIVENT rester OFF
ENGINES_X199_OFF = [
    ("ecoforestry_omega",        "/api/v7-ultime/ecoforestry/compute"),
    ("terrain_3d_omega",         "/api/v7-ultime/terrain-3d/compute"),
    ("legal_time_omega",         "/api/v7-ultime/legal-time/compute"),
    ("predictive_omega",         "/api/v7-ultime/predictive/compute"),
    ("advanced_geospatial_omega","/api/v7-ultime/advanced-geospatial/compute"),
]


@pytest.mark.parametrize("slug,prefix", ENGINES_P0_ACTIVE + ENGINES_X199_OFF)
def test_engine_package_importable(slug, prefix):
    mod = __import__(f"engines.{slug}", fromlist=["router", "FEATURE_FLAG_ACTIVE"])
    assert hasattr(mod, "router")
    assert hasattr(mod, "FEATURE_FLAG_ACTIVE")


@pytest.mark.parametrize("slug,prefix", ENGINES_P0_ACTIVE)
def test_p0_feature_flag_on(slug, prefix):
    mod = __import__(f"engines.{slug}", fromlist=["FEATURE_FLAG_ACTIVE"])
    assert mod.FEATURE_FLAG_ACTIVE is True, f"{slug} MUST be ON (X200-P0)"


@pytest.mark.parametrize("slug,prefix", ENGINES_X199_OFF)
def test_x199_extended_stay_off(slug, prefix):
    """Post PHASE_X199_ACTIVATION_Ω : les 5 moteurs étendus sont maintenant ON.

    Ce test conserve son nom historique pour ne pas briser la collection pytest
    mais vérifie l'invariant courant (MUST_BE_ON).
    """
    mod = __import__(f"engines.{slug}", fromlist=["FEATURE_FLAG_ACTIVE"])
    assert mod.FEATURE_FLAG_ACTIVE is True, (
        f"{slug} MUST be ON post-PHASE_X199_ACTIVATION_Ω"
    )


@pytest.mark.parametrize("slug,prefix", ENGINES_P0_ACTIVE + ENGINES_X199_OFF)
def test_router_prefix_matches_spec(slug, prefix):
    mod = __import__(f"engines.{slug}", fromlist=["router"])
    assert mod.router.prefix == prefix


def test_all_10_engines_on_disk():
    root = Path("/app/backend/engines")
    for slug, _ in ENGINES_P0_ACTIVE + ENGINES_X199_OFF:
        assert (root / slug / "router.py").exists()


# ═══════════════════════════════════════════════════════════════════════
# FAÇADE V30 MIROIR
# ═══════════════════════════════════════════════════════════════════════
def test_v30_mirror_module_importable():
    from engines.bio_scoring_omega import v30_mirror_read_only as m
    assert hasattr(m, "FEATURE_FLAG_ACTIVE")
    assert hasattr(m, "V30_EXPECTED_SHA256")
    assert hasattr(m, "mirror_read")


def test_v30_mirror_sha256_invariant():
    from engines.bio_scoring_omega import v30_mirror_read_only as m
    status = m.assert_v30_integrity()
    assert status["invariant"] is True, (
        f"V30 INTEGRITY BREACH: {status}"
    )


def test_v30_file_not_modified_by_mirror_call():
    from engines.bio_scoring_omega import v30_mirror_read_only as m
    before = m._compute_v30_sha256()
    _ = m.mirror_read("cost_surface", 48.2, -68.4, "orignal")
    _ = m.mirror_read("ecl", 48.2, -68.4, "orignal")
    _ = m.mirror_read("canopy_density", 48.2, -68.4, "orignal")
    after = m._compute_v30_sha256()
    assert before == after


# ═══════════════════════════════════════════════════════════════════════
# AUDIT CONTINU
# ═══════════════════════════════════════════════════════════════════════
def test_audit_continu_all_green():
    """Exécute l'audit read-only et vérifie que tous les gates sont verts."""
    sys.path.insert(0, "/app/backend/tools")
    from audit_engines_x199_x200 import run_audit
    result = run_audit()
    assert result["overall_ok"] is True, result
    assert result["gates"]["v30_integrity"]["ok"] is True
    assert result["gates"]["feature_flags"]["ok"] is True
    assert result["gates"]["zero_doublon_omega"]["ok"] is True


# ═══════════════════════════════════════════════════════════════════════
# FONCTIONNEL P0
# ═══════════════════════════════════════════════════════════════════════
def test_p0_cerf_restored():
    """P0 #1 : CERF doit être présent dans wildlife_behavior (restauration V7)."""
    from engines.wildlife_behavior_omega.router import get_species_profile
    res = get_species_profile("CERF")
    assert res["available"] is True
    assert res["species"] == "cerf"
    assert res["profile"]["nom_scientifique"] == "Odocoileus virginianus"
    assert res["profile"]["affinite_hydro"] == 0.60
    assert res["profile"]["pente_max_deg"] == 15


def test_p0_chevreuil_alias_to_cerf():
    """L'alias chevreuil doit pointer vers le profil CERF V7."""
    from engines.wildlife_behavior_omega.router import get_species_profile
    res = get_species_profile("chevreuil")
    assert res["available"] is True
    assert res["species"] == "cerf"


def test_p0_20_salines_hierarchized():
    """P0 #2 : ECO_ZONES doit exposer 20 sources salines hiérarchisées."""
    from engines.eco_zones_omega.router import get_20_saline_sources
    sources = get_20_saline_sources()
    assert len(sources) == 20
    # Score décroissant (trié)
    for i in range(len(sources) - 1):
        assert sources[i]["score"] >= sources[i + 1]["score"]


def test_p0_inversion_hydro_corrected():
    """P0 #3 : HYDRO_TOPO doit produire un BONUS positif pour proximité eau (inversion corrigée)."""
    from engines.hydro_topo_omega.router import hydro_attraction_bonus
    point = [48.206657, -68.382422]
    water = [[48.2067, -68.38215]]   # très proche
    bonus_orignal = hydro_attraction_bonus(point, water, affinity_hydro=0.85)
    bonus_dindon  = hydro_attraction_bonus(point, water, affinity_hydro=0.40)
    assert bonus_orignal > 0, "V7 ATTRACTION hydro attendue (>0)"
    assert bonus_dindon > 0
    assert bonus_orignal > bonus_dindon, "Orignal (aff 0.85) doit être plus attiré que dindon (0.40)"


def test_p0_reseau_veineux_5_levels_v7():
    """Support : 5 niveaux V7 canoniques avec couleurs distinctes."""
    from engines.reseau_veineux_omega.router import CORRIDOR_LEVELS_V7, classify_corridor
    assert len(CORRIDOR_LEVELS_V7) == 5
    assert [l["level"] for l in CORRIDOR_LEVELS_V7] == [
        "CRITIQUE", "MAJEUR", "FORT", "MODERE", "FAIBLE"
    ]
    assert classify_corridor(90)["level"] == "CRITIQUE"
    assert classify_corridor(75)["level"] == "MAJEUR"
    assert classify_corridor(60)["level"] == "FORT"
    assert classify_corridor(35)["level"] == "MODERE"
    assert classify_corridor(10)["level"] == "FAIBLE"


def test_p0_bio_scoring_8_factors_weight_sum():
    """Support : somme des 7 facteurs additifs V7 = 100 pts."""
    from engines.bio_scoring_omega.router import FACTOR_WEIGHTS_V7, score_8_factors
    additive = ["ecl", "canopy", "pressure_human", "food_refuge",
                "topo_hydro", "regeneration", "cost"]
    total = sum(FACTOR_WEIGHTS_V7[f] for f in additive)
    assert total == 100, f"Somme poids V7 additifs = {total} (attendu 100)"

    # Score maximal avec tous facteurs parfaits + bonus diversité
    perfect = {f: 1.0 for f in additive}
    perfect.update({"from_type": "salines", "to_type": "repos", "n_cells": 15})
    out = score_8_factors(perfect)
    assert 95.0 <= out["score_0_100"] <= 100.0
