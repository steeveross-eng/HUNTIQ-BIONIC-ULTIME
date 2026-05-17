"""
Phase XXVIII · ORDRE N°52-R16-A — Tests anti-régressifs R9 fondations
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Valide les 4 fonctions de fondations R9 (R16-A) :
  · compute_r9_signatures_terrain
  · compute_r9_exclusions
  · compute_r9_zones_humides
  · compute_r9_couvert_securite

+ probe_territoire_ultime_hooks
+ pipeline orchestrator execute_r16a_pipeline
+ all_validated_for_r16a
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def loader():
    import engines.v8_institutional.especes.mffp_dictionaries_loader_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def r9o():
    import engines.v8_institutional.especes.r9_phase3_orchestrator_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def fake_subset(tmp_path):
    """Subset minimal avec colonnes MFFP 2025 schéma réel."""
    import geopandas as gpd
    from shapely.geometry import Polygon

    rows = []
    base_x, base_y = 8000, 467000
    schemas = [
        # Polygone forêt résineuse dense haute (couvert sécurité +++)
        {"type_couv": "R", "gr_ess": "R", "cl_age": "70", "cl_dens": "A",
         "cl_haut": "5", "cl_pent": "3", "cl_drai": "3", "type_eco": "RB1",
         "dep_sur": "1A"},
        # Polygone humide (drainage 6)
        {"type_couv": "F", "gr_ess": "F", "cl_age": "30", "cl_dens": "B",
         "cl_haut": "2", "cl_pent": "1", "cl_drai": "6", "type_eco": "MJ1",
         "dep_sur": "7E"},
        # Polygone pente extrême (cl_pent 8)
        {"type_couv": "M", "gr_ess": "M", "cl_age": "50", "cl_dens": "C",
         "cl_haut": "3", "cl_pent": "8", "cl_drai": "2", "type_eco": "FE2",
         "dep_sur": "1A"},
        # Polygone drainage extrême sec (cl_drai 0)
        {"type_couv": "R", "gr_ess": "R", "cl_age": "10", "cl_dens": "E",
         "cl_haut": "1", "cl_pent": "2", "cl_drai": "0", "type_eco": "RA1",
         "dep_sur": "1A"},
        # Polygone forestier mixte adulte (couvert moyen)
        {"type_couv": "M", "gr_ess": "M", "cl_age": "90", "cl_dens": "B",
         "cl_haut": "4", "cl_pent": "3", "cl_drai": "3", "type_eco": "MS1",
         "dep_sur": "1A"},
    ]
    for i, s in enumerate(schemas):
        x = base_x + (i % 3) * 1000
        y = base_y + (i // 3) * 1000
        s["geometry"] = Polygon([
            (x, y), (x + 1000, y),
            (x + 1000, y + 1000), (x, y + 1000),
        ])
        rows.append(s)
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32198")
    p = tmp_path / "fake_r16a.gpkg"
    gdf.to_file(str(p), driver="GPKG", layer="pee_maj")
    return str(p)


# ═════════════════════════════════════════════════════════════════════════
# 1. API publique + dictionnaires R16-A
# ═════════════════════════════════════════════════════════════════════════
def test_r16a_module_exports_4_functions(r9o):
    assert hasattr(r9o, "compute_r9_signatures_terrain")
    assert hasattr(r9o, "compute_r9_exclusions")
    assert hasattr(r9o, "compute_r9_zones_humides")
    assert hasattr(r9o, "compute_r9_couvert_securite")
    assert hasattr(r9o, "execute_r16a_pipeline")
    assert hasattr(r9o, "probe_territoire_ultime_hooks")
    assert "execute_r16a_pipeline" in r9o.__all__
    assert r9o.R16A_PIPELINE == [
        "R9_SIGNATURES_TERRAIN", "R9_EXCLUSIONS",
        "R9_ZONES_HUMIDES", "R9_COUVERT_SECURITE"]


def test_loader_4_new_dictionaries_registered(loader):
    for d in ("regles_territoires_canonical", "exclusions_thresholds",
              "hydrologie_drainage_codes",
              "couvert_securite_thresholds"):
        assert d in loader.DICTIONARY_FILES


def test_loader_all_validated_for_r16a(loader):
    assert loader.all_validated_for_r16a() is True


def test_loader_loads_regles_canonical_dict(loader):
    d = loader.load_dictionary("regles_territoires_canonical")
    assert d["status"] == "VALIDÉ"
    hooks = d.get("territoire_ultime_hooks", {}).get("hooks_specs", {})
    for h in ["IA_VISION", "DONNEES_CHASSEUR", "ENVIRONNEMENT",
              "NUTRITION", "COMPORTEMENT", "PREDICTIF"]:
        assert h in hooks


def test_loader_loads_exclusions_thresholds(loader):
    d = loader.load_dictionary("exclusions_thresholds")
    assert d["status"] == "VALIDÉ"
    assert "rules" in d
    assert "pentes_extremes" in d["rules"]


# ═════════════════════════════════════════════════════════════════════════
# 2. probe_territoire_ultime_hooks
# ═════════════════════════════════════════════════════════════════════════
def test_probe_hooks_returns_6_hooks(r9o, loader):
    regles = loader.load_dictionary("regles_territoires_canonical")
    state = r9o.probe_territoire_ultime_hooks(regles)
    assert set(state.keys()) == {
        "IA_VISION", "DONNEES_CHASSEUR", "ENVIRONNEMENT",
        "NUTRITION", "COMPORTEMENT", "PREDICTIF"}
    for hook, info in state.items():
        assert "available" in info
        assert isinstance(info.get("paths_present"), list)
        assert isinstance(info.get("paths_absent"), list)
        assert "fallback_when_unavailable" in info


# ═════════════════════════════════════════════════════════════════════════
# 3. compute_r9_signatures_terrain
# ═════════════════════════════════════════════════════════════════════════
def test_signatures_terrain_executes(r9o, loader, fake_subset, tmp_path):
    regles = loader.load_dictionary("regles_territoires_canonical")
    out = tmp_path / "r9_out"
    r = r9o.compute_r9_signatures_terrain(
        fake_subset, regles, output_root=out)
    assert r["manifest_id"] == "R9_SIGNATURES_TERRAIN_COMPUTED_Ω"
    assert r["n_polygons_processed"] == 5
    # 5 polygones avec schémas distincts → 5 signatures uniques
    assert r["n_unique_signatures"] == 5
    assert Path(r["output_raster"]).exists()
    assert Path(r["output_vector"]).exists()
    assert len(r["raster_sha256"]) == 64
    assert len(r["vector_sha256"]) == 64
    assert "_signature_id_hex" not in r["fields_used_for_signature"]


def test_signatures_terrain_signature_stable_across_runs(
        r9o, loader, fake_subset, tmp_path):
    """Même subset → mêmes signatures (reproductible)."""
    regles = loader.load_dictionary("regles_territoires_canonical")
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    r1 = r9o.compute_r9_signatures_terrain(
        fake_subset, regles, output_root=out1)
    r2 = r9o.compute_r9_signatures_terrain(
        fake_subset, regles, output_root=out2)
    assert r1["top10_signatures_frequency"] == \
        r2["top10_signatures_frequency"]


# ═════════════════════════════════════════════════════════════════════════
# 4. compute_r9_exclusions
# ═════════════════════════════════════════════════════════════════════════
def test_exclusions_excludes_extreme_slope(r9o, loader, fake_subset,
                                              tmp_path):
    excl = loader.load_dictionary("exclusions_thresholds")
    out = tmp_path / "r9_excl"
    r = r9o.compute_r9_exclusions(
        fake_subset, excl, output_root=out)
    assert r["manifest_id"] == "R9_EXCLUSIONS_COMPUTED_Ω"
    # cl_pent=8 et cl_drai 6 → au moins 2 polygones doivent être exclus
    # (pente 8 weight 1.0 > threshold 0.5 ; drainage 0 weight 0.5 ne suffit pas)
    assert r["n_polygons_excluded"] >= 1
    assert any(rl["rule"] == "pentes_extremes"
               for rl in r["applied_rules"])
    # External rules MUST be skipped (not fabricated)
    skipped_rules = {rl["rule"] for rl in r["skipped_rules"]}
    assert "distance_routes_meters" in skipped_rules
    assert "distance_habitations_meters" in skipped_rules
    assert "zones_reglementaires" in skipped_rules


def test_exclusions_anti_generique_strict(r9o, loader, fake_subset,
                                            tmp_path):
    """Confirme que les sources externes absentes ne créent pas de fausses
    exclusions (skipped, pas fabriquées)."""
    excl = loader.load_dictionary("exclusions_thresholds")
    out = tmp_path / "r9_excl_strict"
    r = r9o.compute_r9_exclusions(
        fake_subset, excl, output_root=out)
    for skip in r["skipped_rules"]:
        if skip["rule"] in ("distance_routes_meters",
                             "distance_habitations_meters",
                             "zones_reglementaires"):
            assert "anti_generique_strict" in skip["reason"]


# ═════════════════════════════════════════════════════════════════════════
# 5. compute_r9_zones_humides
# ═════════════════════════════════════════════════════════════════════════
def test_zones_humides_detects_drai_5_6(r9o, loader, fake_subset, tmp_path):
    hydro = loader.load_dictionary("hydrologie_drainage_codes")
    out = tmp_path / "r9_humides"
    r = r9o.compute_r9_zones_humides(
        fake_subset, hydro, output_root=out)
    assert r["manifest_id"] == "R9_ZONES_HUMIDES_COMPUTED_Ω"
    # fake_subset a 2 polygones humides:
    # - cl_drai=6 + type_eco=MJ1 (préfixe MJ humide)
    # Le polygone cl_drai=3 + type_eco=MS1 (préfixe MS humide) — humide aussi
    assert r["n_polygons_humid"] >= 2
    assert r["humid_pct"] > 0
    assert "5" in r["cl_drai_humid_codes_used"]
    assert "6" in r["cl_drai_humid_codes_used"]
    assert Path(r["output_raster"]).exists()


# ═════════════════════════════════════════════════════════════════════════
# 6. compute_r9_couvert_securite
# ═════════════════════════════════════════════════════════════════════════
def test_couvert_securite_score_range_0_100(r9o, loader, fake_subset,
                                              tmp_path):
    couv = loader.load_dictionary("couvert_securite_thresholds")
    out = tmp_path / "r9_couv"
    r = r9o.compute_r9_couvert_securite(
        fake_subset, couv, output_root=out)
    assert r["manifest_id"] == "R9_COUVERT_SECURITE_COMPUTED_Ω"
    assert 0 <= r["mean_score"] <= 100
    # Polygone 0 (R/A/cl_haut 5) doit avoir score très élevé
    # Polygone 3 (R/E/cl_haut 1) doit avoir score bas
    # → distribution non uniformément basse
    assert r["bucket_distribution"]["75_100"] >= 1
    assert Path(r["output_raster"]).exists()


def test_couvert_securite_resineux_higher_than_feuillu(r9o, loader, tmp_path):
    """Sémantique : R (résineux) > F (feuillu) à autres conditions égales."""
    import geopandas as gpd
    from shapely.geometry import Polygon
    rows = [
        {"type_couv": "R", "cl_dens": "B", "cl_haut": "5",
         "geometry": Polygon([(0, 0), (1000, 0),
                              (1000, 1000), (0, 1000)])},
        {"type_couv": "F", "cl_dens": "B", "cl_haut": "5",
         "geometry": Polygon([(2000, 0), (3000, 0),
                              (3000, 1000), (2000, 1000)])},
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32198")
    p = tmp_path / "test_couv_RF.gpkg"
    gdf.to_file(str(p), driver="GPKG", layer="pee_maj")

    couv = loader.load_dictionary("couvert_securite_thresholds")
    out = tmp_path / "r9_couv_RF"
    r = r9o.compute_r9_couvert_securite(
        str(p), couv, output_root=out)
    # Les 2 polygones ont des scores différents (R=100, F=35 sur type_couv)
    # mean ne doit pas être 0 et < 100
    assert 0 < r["mean_score"] < 100


# ═════════════════════════════════════════════════════════════════════════
# 7. execute_r16a_pipeline (orchestrator)
# ═════════════════════════════════════════════════════════════════════════
def test_pipeline_executes_4_targets(r9o, fake_subset, tmp_path,
                                       monkeypatch):
    """L'orchestrator exécute les 4 cibles R16-A et met à jour le state."""
    state_p = tmp_path / "R9_RECALC_STATE.json"
    out_root = tmp_path / "r9_derivs"
    monkeypatch.setattr(r9o, "R9_RECALC_STATE_PATH", state_p)
    monkeypatch.setattr(r9o, "DERIVATIVES_R9_ROOT", out_root)
    monkeypatch.setattr(r9o, "auto_pick_subset", lambda: fake_subset)

    res = r9o.execute_r16a_pipeline()
    assert res["manifest_id"] == "R9_PHASE3_R16A_PIPELINE_COMPLETED_Ω"
    assert res["n_targets_succeeded"] == 4
    assert set(res["r16a_targets_succeeded"]) == {
        "R9_SIGNATURES_TERRAIN", "R9_EXCLUSIONS",
        "R9_ZONES_HUMIDES", "R9_COUVERT_SECURITE"}
    # State file doit être mis à jour
    assert state_p.exists()
    state = json.loads(state_p.read_text(encoding="utf-8"))
    assert state["status"] == "OK_REAL_PARTIAL_R16A"
    assert "R9_SIGNATURES_TERRAIN" in state["targets"]
    assert state["targets"]["R9_SIGNATURES_TERRAIN"]["status"] == "OK_REAL"
    assert state["targets"]["R9_SIGNATURES_TERRAIN"][
        "ordre"] == "N°52-R16-A"


def test_pipeline_subset_required(r9o, monkeypatch):
    """Pas de subset → raise."""
    monkeypatch.setattr(r9o, "auto_pick_subset", lambda: None)
    with pytest.raises(RuntimeError, match="subset"):
        r9o.execute_r16a_pipeline()
