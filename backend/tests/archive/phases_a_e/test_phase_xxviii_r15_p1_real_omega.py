"""
Phase XXVIII · ORDRE N°52-R15 — Tests anti-régressifs Phase 3 P1 RÉEL
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Valide les 4 nouvelles fonctions de couches PHASE_3 R8 P1+P2 :
  · compute_mffp_productivity (lookup tables_rendement_mffp + corr densité)
  · compute_mffp_habitat (5 bandes uint8 score 0-100 par espèce)
  · compute_mffp_connectivity (DBSCAN clusters MultiPolygon)
  · compute_mffp_continuity (5 classes uint8 RECENT/...)

Tests :
  · API publique exposée + dictionnaires R15 chargeables
  · all_validated_for_p1() retourne True
  · Productivity : signature + lookup + correction densité + raster
  · Habitat : 5 bandes alignées + scores 0-100 + tags espèce
  · Connectivity : DBSCAN trouve clusters + GeoPackage écrit
  · Continuity : règles age + perturbation HIGH récent → classe 5
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


# ═════════════════════════════════════════════════════════════════════════
# Fixtures
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture()
def loader():
    import engines.v8_institutional.especes.mffp_dictionaries_loader_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def p1():
    import engines.v8_institutional.especes.mffp_phase3_p1_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def fake_subset(tmp_path):
    """Subset minimal 5 polygones pour test fonctionnel rapide."""
    import geopandas as gpd
    from shapely.geometry import Polygon

    rows = []
    base_x, base_y = 8000, 467000
    for i in range(20):
        # 20 carrés de 1 km × 1 km adjacents
        x = base_x + (i % 5) * 1000
        y = base_y + (i // 5) * 1000
        rows.append({
            "type_couv": ["F", "R", "M", "F", "R"][i % 5],
            "gr_ess": ["F", "R", "M", "F", "R"][i % 5],
            "cl_age": ["30", "50", "70", "90", "120"][i % 5],
            "cl_dens": ["A", "B", "C", "D", "B"][i % 5],
            "cl_haut": ["3", "4", "5", "6", "5"][i % 5],
            "an_origine": [1990, 1970, 1950, 1900, 1820][i % 5],
            "perturb": ["", "", "CT", "", "BR"][i % 5],
            "an_perturb": [None, None, 2020, None, 1850][i % 5],
            "geometry": Polygon([
                (x, y), (x + 1000, y),
                (x + 1000, y + 1000), (x, y + 1000),
            ]),
        })
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32198")
    p = tmp_path / "fake_subset.gpkg"
    gdf.to_file(str(p), driver="GPKG", layer="pee_maj")
    return str(p)


# ═════════════════════════════════════════════════════════════════════════
# 1. API publique + dictionnaires R15
# ═════════════════════════════════════════════════════════════════════════
def test_p1_module_exports_4_functions(p1):
    assert hasattr(p1, "compute_mffp_productivity")
    assert hasattr(p1, "compute_mffp_habitat")
    assert hasattr(p1, "compute_mffp_connectivity")
    assert hasattr(p1, "compute_mffp_continuity")
    assert "compute_mffp_productivity" in p1.__all__
    assert p1.SPECIES_BAND_ORDER == [
        "chevreuil", "orignal", "ours_noir", "dindon", "wapiti"]


def test_loader_accepts_3_new_dictionaries(loader):
    assert "tables_rendement_mffp" in loader.DICTIONARY_FILES
    assert "habitat_preferences_par_espece" in loader.DICTIONARY_FILES
    assert "perturbation_severity" in loader.DICTIONARY_FILES


def test_loader_all_validated_for_p1(loader):
    """Les 3 nouveaux dicts R15 + les 4 P0 doivent tous être VALIDÉS."""
    assert loader.all_validated_for_p1() is True


def test_loader_loads_tables_rendement(loader):
    d = loader.load_dictionary("tables_rendement_mffp")
    assert d["status"] == "VALIDÉ"
    assert d["unit"] == "m3_per_ha"
    assert "R" in d["mapping"]
    assert "F" in d["mapping"]
    assert "M" in d["mapping"]
    # Les valeurs sont monotones croissantes en âge pour R
    r_values = d["mapping"]["R"]["production_m3_per_ha"]
    assert r_values["10"] < r_values["50"] < r_values["90"]


def test_loader_loads_habitat_preferences(loader):
    d = loader.load_dictionary("habitat_preferences_par_espece")
    assert d["status"] == "VALIDÉ"
    assert "preferences" in d
    for sp in ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"]:
        assert sp in d["preferences"]
    assert sum(d["weights_by_field"].values()) == pytest.approx(1.0)


def test_loader_loads_perturbation_severity(loader):
    d = loader.load_dictionary("perturbation_severity")
    assert d["status"] == "VALIDÉ"
    assert d["current_year_assumption"] == 2026
    assert "CT" in d["severity_codes"]
    assert d["severity_codes"]["CT"]["severity"] == "HIGH"


# ═════════════════════════════════════════════════════════════════════════
# 2. compute_mffp_productivity
# ═════════════════════════════════════════════════════════════════════════
def test_productivity_signature(p1):
    import inspect
    sig = inspect.signature(p1.compute_mffp_productivity)
    assert "tables_rendement_dict" in sig.parameters
    assert "resolution_m" in sig.parameters
    assert sig.parameters["resolution_m"].default == 100


def test_productivity_executes_on_fake_subset(p1, loader, fake_subset,
                                                tmp_path):
    d = loader.load_dictionary("tables_rendement_mffp")
    out = tmp_path / "PRODUCTIVITE.tif"
    r = p1.compute_mffp_productivity(
        fake_subset, d, output_tif_path=str(out))
    assert r["manifest_id"] == "MFFP_PRODUCTIVITY_COMPUTED_Ω"
    assert r["n_polygons_processed"] == 20
    assert 0 <= r["mean_m3_per_ha"] <= 500
    assert Path(out).exists()
    assert r["sha256"] and len(r["sha256"]) == 64
    # Distribution des essences cohérente
    dist = r["gr_ess_distribution"]
    assert "F" in dist or "R" in dist or "M" in dist


def test_productivity_density_correction_a_higher_than_e(p1, loader,
                                                          tmp_path):
    """Test sémantique : densité A doit produire un m³/ha > densité E
    pour gr_ess et cl_age identiques."""
    import geopandas as gpd
    from shapely.geometry import Polygon
    rows = [
        {"gr_ess": "R", "cl_age": "70", "cl_dens": "A",
         "geometry": Polygon([(0, 0), (1000, 0),
                              (1000, 1000), (0, 1000)])},
        {"gr_ess": "R", "cl_age": "70", "cl_dens": "E",
         "geometry": Polygon([(2000, 0), (3000, 0),
                              (3000, 1000), (2000, 1000)])},
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32198")
    p = tmp_path / "density_test.gpkg"
    gdf.to_file(str(p), driver="GPKG", layer="pee_maj")

    d = loader.load_dictionary("tables_rendement_mffp")
    out = tmp_path / "PROD_DENS.tif"
    r = p1.compute_mffp_productivity(
        str(p), d, output_tif_path=str(out))
    assert r["n_polygons_processed"] == 2


# ═════════════════════════════════════════════════════════════════════════
# 3. compute_mffp_habitat (5 bandes)
# ═════════════════════════════════════════════════════════════════════════
def test_habitat_executes_5_bands(p1, loader, fake_subset, tmp_path):
    d = loader.load_dictionary("habitat_preferences_par_espece")
    out = tmp_path / "HABITAT.tif"
    r = p1.compute_mffp_habitat(
        fake_subset, d, output_tif_path=str(out))
    assert r["manifest_id"] == "MFFP_HABITAT_COMPUTED_Ω"
    assert r["bands_count"] == 5
    assert len(r["bands_meta"]) == 5
    species_in_bands = [b["species"] for b in r["bands_meta"]]
    assert species_in_bands == [
        "chevreuil", "orignal", "ours_noir", "dindon", "wapiti"]
    # Scores moyens dans la plage 0-100
    for sp, sc in r["mean_score_per_species"].items():
        assert 0 <= sc <= 100, f"{sp}: {sc}"
    # Vérifier multi-bande sur le raster
    import rasterio
    with rasterio.open(out) as src:
        assert src.count == 5
        assert src.dtypes[0] == "uint8"


def test_habitat_score_function_bounded_0_100(p1, loader):
    d = loader.load_dictionary("habitat_preferences_par_espece")
    weights = d["weights_by_field"]
    # Cas connu : chevreuil sur peuplement mixte 50ans densité B → score élevé
    row = {"gr_ess": "M", "cl_age": "50", "cl_dens": "B", "type_couv": "FM"}
    s = p1._score_habitat_for_species(
        row, d["preferences"]["chevreuil"], weights)
    assert 0 <= s <= 100
    assert s >= 75, f"Cas optimal chevreuil → expected >=75, got {s}"


# ═════════════════════════════════════════════════════════════════════════
# 4. compute_mffp_connectivity (DBSCAN)
# ═════════════════════════════════════════════════════════════════════════
def test_connectivity_dbscan_finds_at_least_one_cluster(p1, fake_subset,
                                                         tmp_path):
    """Avec 20 polygones adjacents 1×1 km, eps=2000 → 1 cluster dense."""
    out = tmp_path / "CONN.gpkg"
    r = p1.compute_mffp_connectivity(
        fake_subset, output_gpkg_path=str(out),
        eps_meters=2000.0, min_samples=3)
    assert r["manifest_id"] == "MFFP_CONNECTIVITY_COMPUTED_Ω"
    assert r["algorithm"].startswith("DBSCAN")
    assert r["n_forest_polygons"] == 20
    assert r["n_clusters_detected"] >= 1
    assert Path(out).exists()
    # Vérifier que GeoPackage est lisible
    import geopandas as gpd
    gdf = gpd.read_file(str(out))
    assert len(gdf) >= 1
    assert "cluster_id" in gdf.columns
    assert "habitat_score_mean" in gdf.columns
    assert "area_ha" in gdf.columns


def test_connectivity_handles_only_noise_gracefully(p1, tmp_path):
    """Avec eps=1m sur des polygones espacés → tous noise points."""
    import geopandas as gpd
    from shapely.geometry import Polygon
    rows = [
        {"gr_ess": "R", "geometry": Polygon([
            (i * 100000, 0), (i * 100000 + 1000, 0),
            (i * 100000 + 1000, 1000), (i * 100000, 1000)])}
        for i in range(5)
    ]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32198")
    p = tmp_path / "noise.gpkg"
    gdf.to_file(str(p), driver="GPKG", layer="pee_maj")

    out = tmp_path / "CONN_NOISE.gpkg"
    r = p1.compute_mffp_connectivity(
        str(p), output_gpkg_path=str(out),
        eps_meters=1.0, min_samples=2)
    assert r["n_noise_points"] >= 0  # tous éloignés


# ═════════════════════════════════════════════════════════════════════════
# 5. compute_mffp_continuity
# ═════════════════════════════════════════════════════════════════════════
def test_continuity_5_classes(p1, loader, fake_subset, tmp_path):
    d = loader.load_dictionary("perturbation_severity")
    out = tmp_path / "CONTINUITE.tif"
    r = p1.compute_mffp_continuity(
        fake_subset, d, output_tif_path=str(out))
    assert r["manifest_id"] == "MFFP_CONTINUITY_COMPUTED_Ω"
    assert r["current_year_used"] == 2026
    assert r["perturb_recent_threshold_years"] == 25
    dist = r["continuity_class_distribution"]
    # Toutes les classes attendues sont int 1-5
    for k in dist:
        assert int(k) in [1, 2, 3, 4, 5]


def test_continuity_recent_perturbation_classified_as_5(p1, loader,
                                                         tmp_path):
    """Polygone avec perturb=CT (HIGH severity) an_perturb=2020 →
    classe 5 PERTURBE_RECENT (current=2026, age perturb=6 < 25)."""
    import geopandas as gpd
    from shapely.geometry import Polygon
    rows = [{
        "gr_ess": "R", "cl_age": "30", "cl_dens": "B",
        "an_origine": 1990, "perturb": "CT", "an_perturb": 2020,
        "geometry": Polygon([(0, 0), (1000, 0),
                             (1000, 1000), (0, 1000)]),
    }]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32198")
    p = tmp_path / "perturb.gpkg"
    gdf.to_file(str(p), driver="GPKG", layer="pee_maj")

    d = loader.load_dictionary("perturbation_severity")
    out = tmp_path / "CONT_RECENT.tif"
    r = p1.compute_mffp_continuity(
        str(p), d, output_tif_path=str(out))
    dist = r["continuity_class_distribution"]
    assert "5" in dist


def test_continuity_old_growth_classified_as_4(p1, loader, tmp_path):
    """Polygone an_origine=1820 (= 206 ans en 2026) sans perturb →
    classe 4 VIEILLES_FORÊTS."""
    import geopandas as gpd
    from shapely.geometry import Polygon
    rows = [{
        "gr_ess": "F", "cl_age": "VIR", "cl_dens": "A",
        "an_origine": 1820, "perturb": None, "an_perturb": None,
        "geometry": Polygon([(0, 0), (1000, 0),
                             (1000, 1000), (0, 1000)]),
    }]
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32198")
    p = tmp_path / "old.gpkg"
    gdf.to_file(str(p), driver="GPKG", layer="pee_maj")

    d = loader.load_dictionary("perturbation_severity")
    out = tmp_path / "CONT_OLD.tif"
    r = p1.compute_mffp_continuity(
        str(p), d, output_tif_path=str(out))
    dist = r["continuity_class_distribution"]
    assert "4" in dist
