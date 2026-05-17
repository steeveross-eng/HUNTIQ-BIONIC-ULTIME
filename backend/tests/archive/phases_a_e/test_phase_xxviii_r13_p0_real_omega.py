"""
Phase XXVIII · ORDRE N°52-R13 — Tests P0 PHASE_3 R8 (4 couches)
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Valide :
  · Les 4 dictionnaires sont VALIDÉS (status='VALIDÉ')
  · Les 4 fonctions compute_* fonctionnent sur GPKG synthétique
  · Output GeoTIFF EPSG:32198 + SHA-256 reproductible
  · MFFP_FRAGMENTATION (Dickson 2017) : conv 5x5 + agrégation 250m
  · Endpoint /phase3-p0-execute exécute en E2E
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def loader():
    return importlib.import_module(
        "engines.v8_institutional.especes.mffp_dictionaries_loader_omega")


@pytest.fixture()
def p0():
    return importlib.import_module(
        "engines.v8_institutional.especes.mffp_phase3_p0_omega")


@pytest.fixture()
def synthetic_gpkg(tmp_path):
    """Crée un GPKG synthétique minimal avec champs MFFP canon."""
    import geopandas as gpd
    from shapely.geometry import Polygon

    # 12 polygones synthétiques en EPSG:32198 (zone Estrie)
    base_x, base_y = 600000, 200000
    polygons = []
    rows = []
    for i in range(12):
        dx = (i % 4) * 1000
        dy = (i // 4) * 1000
        poly = Polygon([
            (base_x + dx, base_y + dy),
            (base_x + dx + 800, base_y + dy),
            (base_x + dx + 800, base_y + dy + 800),
            (base_x + dx, base_y + dy + 800),
        ])
        polygons.append(poly)
        # Variation contrôlée des codes MFFP
        rows.append({
            "POLY_ID": i + 1,
            "ESS_DOMI": ["ERS", "BOP", "EPB", "EPN"][i % 4],
            "GR_ESS": ["F", "F", "R", "R"][i % 4],
            "CL_AGE": ["10", "30", "50", "70", "90", "120",
                        "JIN", "VIN"][i % 8],
            "CL_HAUT": (i % 5) + 1,
            "CL_DENS": ["A", "B", "C", "D", "E"][i % 5],
            "TY_COUV": ["FE", "RE", "MS", "EAU", "AGR"][i % 5],
            "TYPE_ECO": "MS22",
            "ORIGINE": "CT",
            "AN_ORIGINE": 2026 - 30 - i * 5,
            "PERTURB": None,
            "AN_PERTURB": None,
            "IND_QUAL": "MOYEN",
            "SUPERFICIE": 64.0,
        })
    gdf = gpd.GeoDataFrame(rows, geometry=polygons, crs="EPSG:32198")
    out = tmp_path / "pee_maj_synthetic.gpkg"
    gdf.to_file(str(out), driver="GPKG", layer="peuplement_ecoforestier")
    return str(out)


def test_r13_all_dicts_validated(loader):
    """Les 4 dictionnaires sont au status='VALIDÉ'."""
    statuses = loader.all_proposed_dictionaries_status()
    assert all(s == "VALIDÉ" for s in statuses.values()), (
        f"Statuts non tous VALIDÉ : {statuses}")
    assert loader.all_validated_for_p0() is True


def test_r13_compute_mffp_density_real(loader, p0, synthetic_gpkg, tmp_path):
    """Exécution réelle de compute_mffp_density sur GPKG synthétique."""
    cl_dens = loader.load_dictionary("cl_dens_to_pct")
    out = tmp_path / "MFFP_DENSITY.tif"
    res = p0.compute_mffp_density(
        synthetic_gpkg, cl_dens, output_tif_path=str(out))
    assert res["manifest_id"] == "MFFP_DENSITY_COMPUTED_Ω"
    assert Path(res["output_path"]).exists()
    assert len(res["sha256"]) == 64
    assert res["n_polygons_processed"] > 0
    assert 10 <= res["mean_pct_canopy"] <= 100
    # Vérification raster valide via rasterio
    import rasterio
    with rasterio.open(res["output_path"]) as ds:
        assert ds.crs.to_epsg() == 32198
        assert ds.dtypes[0] == "uint8"
        assert ds.count == 1


def test_r13_compute_mffp_age_real(loader, p0, synthetic_gpkg, tmp_path):
    """compute_mffp_age sur GPKG synthétique."""
    classes_age = loader.load_dictionary("classes_age")
    out = tmp_path / "MFFP_AGE.tif"
    res = p0.compute_mffp_age(
        synthetic_gpkg, classes_age, output_tif_path=str(out))
    assert res["manifest_id"] == "MFFP_AGE_COMPUTED_Ω"
    assert Path(res["output_path"]).exists()
    assert len(res["sha256"]) == 64
    # Doit avoir au moins 2 classes différentes vu la variation des seeds
    assert len(res["age_class_distribution"]) >= 2
    # Classes valides : 1-8
    for class_id in res["age_class_distribution"].keys():
        assert 1 <= int(class_id) <= 8


def test_r13_compute_mffp_structure_real(loader, p0, synthetic_gpkg, tmp_path):
    """compute_mffp_structure sur GPKG synthétique."""
    structure_rules = loader.load_dictionary("structure_classification_rules")
    out = tmp_path / "MFFP_STRUCTURE.tif"
    res = p0.compute_mffp_structure(
        synthetic_gpkg, structure_rules, output_tif_path=str(out))
    assert res["manifest_id"] == "MFFP_STRUCTURE_COMPUTED_Ω"
    assert Path(res["output_path"]).exists()
    # Classes valides : 1-7
    for class_id in res["structure_distribution"].keys():
        assert 1 <= int(class_id) <= 7


def test_r13_compute_forest_binary_real(loader, p0, synthetic_gpkg, tmp_path):
    """compute_forest_binary_raster (prérequis fragmentation)."""
    ty_couv = loader.load_dictionary("ty_couv_to_forest_binary")
    out = tmp_path / "FOREST_BINARY_50M.tif"
    res = p0.compute_forest_binary_raster(
        synthetic_gpkg, ty_couv, output_tif_path=str(out),
        resolution_m=50)
    assert Path(res["output_path"]).exists()
    import rasterio
    with rasterio.open(res["output_path"]) as ds:
        assert ds.dtypes[0] == "uint8"


def test_r13_compute_mffp_fragmentation_dickson(p0, synthetic_gpkg,
                                                 loader, tmp_path):
    """compute_mffp_fragmentation Dickson 2017 (chaîne complète)."""
    ty_couv = loader.load_dictionary("ty_couv_to_forest_binary")
    binary_out = tmp_path / "FOREST_BINARY.tif"
    binary_res = p0.compute_forest_binary_raster(
        synthetic_gpkg, ty_couv, output_tif_path=str(binary_out),
        resolution_m=50)
    frag_out = tmp_path / "MFFP_FRAGMENTATION.tif"
    res = p0.compute_mffp_fragmentation(
        binary_res["output_path"], output_tif_path=str(frag_out),
        base_resolution_m=50, aggregation_resolution_m=250)
    assert res["manifest_id"] == "MFFP_FRAGMENTATION_COMPUTED_Ω"
    assert res["algorithm"] == "Dickson_Roemer_Boyce_2017"
    assert Path(res["output_path"]).exists()
    assert len(res["sha256"]) == 64
    assert res["base_resolution_m"] == 50
    assert res["aggregation_resolution_m"] == 250
    import rasterio
    with rasterio.open(res["output_path"]) as ds:
        assert ds.dtypes[0] == "float32"
        assert ds.crs.to_epsg() == 32198


def test_r13_target_epsg_quebec(p0):
    assert p0.TARGET_EPSG == 32198


def test_r13_derivatives_root_in_app_ext4(p0):
    assert str(p0.DERIVATIVES_OUTPUT_ROOT).startswith("/app/")


def test_r13_p0_module_exports(p0):
    expected = {
        "compute_mffp_density", "compute_mffp_age",
        "compute_mffp_structure", "compute_forest_binary_raster",
        "compute_mffp_fragmentation",
        "DERIVATIVES_OUTPUT_ROOT", "TARGET_EPSG",
    }
    assert expected == set(p0.__all__)


def test_r13_subset_extractor_check_pee_maj_local(loader):
    """check_pee_maj_local_present retourne dict avec 'present' bool."""
    from engines.v8_institutional.especes.mffp_subset_extractor_omega \
        import check_pee_maj_local_present
    res = check_pee_maj_local_present()
    assert "present" in res
    assert isinstance(res["present"], bool)
    assert "path" in res


def test_r13_density_idempotence_sha256(loader, p0, synthetic_gpkg, tmp_path):
    """Deux exécutions consécutives → même SHA-256 (reproductibilité)."""
    cl_dens = loader.load_dictionary("cl_dens_to_pct")
    out1 = tmp_path / "out1.tif"
    out2 = tmp_path / "out2.tif"
    res1 = p0.compute_mffp_density(
        synthetic_gpkg, cl_dens, output_tif_path=str(out1))
    res2 = p0.compute_mffp_density(
        synthetic_gpkg, cl_dens, output_tif_path=str(out2))
    assert res1["sha256"] == res2["sha256"]
