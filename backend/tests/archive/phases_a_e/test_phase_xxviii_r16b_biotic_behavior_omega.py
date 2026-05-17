"""
Phase XXVIII · ORDRE N°52-R16-B — Tests anti-régressifs R9 BIOTIC BEHAVIOR
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Valide 4 fonctions × 5 espèces = 20 cibles R9 R16-B :
  · compute_r9_zones_vitales × 5
  · compute_r9_repos × 5
  · compute_r9_alimentation × 5
  · compute_r9_rut × 5
+ pipeline orchestrator + cohérence multi-espèces + non-régression
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
def r16b():
    import engines.v8_institutional.especes.r9_phase3_r16b_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def fake_subset_with_rasters(tmp_path):
    """Crée subset + 4 rasters dépendances (habitat, couvert, humides, excl)."""
    import geopandas as gpd
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds
    from shapely.geometry import Polygon

    base_x, base_y = 8000, 467000
    rows = []
    for i in range(10):
        x = base_x + (i % 5) * 1000
        y = base_y + (i // 5) * 1000
        rows.append({
            "type_couv": ["R", "F", "M", "R", "F"][i % 5],
            "gr_ess": ["R", "F", "M", "R", "F"][i % 5],
            "cl_age": ["30", "50", "70", "90", "VIN"][i % 5],
            "cl_dens": ["A", "B", "C", "B", "A"][i % 5],
            "cl_haut": ["3", "4", "5", "5", "6"][i % 5],
            "cl_pent": ["3", "2", "1", "3", "2"][i % 5],
            "cl_drai": ["3", "5", "6", "3", "2"][i % 5],
            "type_eco": ["RB1", "MJ1", "RC1", "FE2", "RA1"][i % 5],
            "geometry": Polygon([
                (x, y), (x + 1000, y),
                (x + 1000, y + 1000), (x, y + 1000)]),
        })
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32198")
    subset_p = tmp_path / "fake_subset.gpkg"
    gdf.to_file(str(subset_p), driver="GPKG", layer="pee_maj")

    # 4 rasters dépendances simples 50×50 pixels couvrant la zone
    width, height = 50, 50
    transform = from_bounds(
        base_x, base_y, base_x + 5000, base_y + 2000, width, height)

    rasters_root = tmp_path / "rasters"
    rasters_root.mkdir(exist_ok=True)

    # MFFP_HABITAT_BRUT (5 bandes uint8, scores variés)
    habitat_p = rasters_root / "MFFP_HABITAT_BRUT.tif"
    habitat_data = np.zeros((5, height, width), dtype="uint8")
    for b in range(5):
        habitat_data[b, :, :] = 60 + b * 5  # 60, 65, 70, 75, 80
    with rasterio.open(
        str(habitat_p), "w", driver="GTiff", count=5,
        height=height, width=width, dtype="uint8",
        crs="EPSG:32198", transform=transform,
        nodata=255,
    ) as dst:
        for b in range(5):
            dst.write(habitat_data[b], b + 1)

    # R9_COUVERT_SECURITE (uint8, score moyen 70)
    couvert_p = rasters_root / "R9_COUVERT_SECURITE.tif"
    with rasterio.open(
        str(couvert_p), "w", driver="GTiff", count=1,
        height=height, width=width, dtype="uint8",
        crs="EPSG:32198", transform=transform, nodata=255,
    ) as dst:
        dst.write(np.full((height, width), 70, dtype="uint8"), 1)

    # R9_ZONES_HUMIDES (binaire, 50% humide)
    humides_p = rasters_root / "R9_ZONES_HUMIDES.tif"
    humid_arr = np.zeros((height, width), dtype="uint8")
    humid_arr[:, :width // 2] = 1
    with rasterio.open(
        str(humides_p), "w", driver="GTiff", count=1,
        height=height, width=width, dtype="uint8",
        crs="EPSG:32198", transform=transform, nodata=255,
    ) as dst:
        dst.write(humid_arr, 1)

    # R9_EXCLUSIONS (binaire, 0% exclu pour les tests classiques)
    excl_p = rasters_root / "R9_EXCLUSIONS.tif"
    with rasterio.open(
        str(excl_p), "w", driver="GTiff", count=1,
        height=height, width=width, dtype="uint8",
        crs="EPSG:32198", transform=transform, nodata=255,
    ) as dst:
        dst.write(np.zeros((height, width), dtype="uint8"), 1)

    return {
        "subset": str(subset_p),
        "habitat": habitat_p,
        "couvert": couvert_p,
        "humides": humides_p,
        "exclusions": excl_p,
        "rasters_root": rasters_root,
    }


# ═════════════════════════════════════════════════════════════════════════
# 1. API publique + dictionnaires R16-B
# ═════════════════════════════════════════════════════════════════════════
def test_r16b_module_exports_4_functions(r16b):
    assert hasattr(r16b, "compute_r9_zones_vitales")
    assert hasattr(r16b, "compute_r9_repos")
    assert hasattr(r16b, "compute_r9_alimentation")
    assert hasattr(r16b, "compute_r9_rut")
    assert hasattr(r16b, "execute_r16b_pipeline")
    assert "execute_r16b_pipeline" in r16b.__all__
    assert r16b.SPECIES_LIST == [
        "chevreuil", "orignal", "ours_noir", "dindon", "wapiti"]
    assert r16b.TARGETS_R16B_PER_SPECIES == [
        "ZONES_VITALES", "REPOS", "ALIMENTATION", "RUT"]


def test_loader_phenologie_dict_registered(loader):
    assert "phenologie_saisonniere" in loader.DICTIONARY_FILES


def test_loader_all_validated_for_r16b(loader):
    assert loader.all_validated_for_r16b() is True


def test_phenologie_dict_contains_5_species(loader):
    d = loader.load_dictionary("phenologie_saisonniere")
    assert d["status"] == "VALIDÉ"
    cal = d["calendar"]
    for sp in ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"]:
        assert sp in cal
        assert "rut_peak_months" in cal[sp]
        assert "vital_zone_weights" in cal[sp]
        weights = cal[sp]["vital_zone_weights"]
        assert sum(weights.values()) == pytest.approx(1.0)


def test_phenologie_alim_proxy_per_species(loader):
    d = loader.load_dictionary("phenologie_saisonniere")
    rules = d["alimentation_proxy_rules"]["rules_per_species"]
    for sp in ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"]:
        assert sp in rules


# ═════════════════════════════════════════════════════════════════════════
# 2. compute_r9_zones_vitales × 5 espèces
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("species",
    ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"])
def test_zones_vitales_executes_per_species(
        r16b, loader, fake_subset_with_rasters, tmp_path, species):
    pheno = loader.load_dictionary("phenologie_saisonniere")
    out = tmp_path / "r16b_out"
    r = r16b.compute_r9_zones_vitales(
        species=species,
        subset_path=fake_subset_with_rasters["subset"],
        habitat_tif=fake_subset_with_rasters["habitat"],
        couvert_securite_tif=fake_subset_with_rasters["couvert"],
        zones_humides_tif=fake_subset_with_rasters["humides"],
        exclusions_tif=fake_subset_with_rasters["exclusions"],
        phenologie_dict=pheno,
        output_root=out,
    )
    assert r["manifest_id"] == \
        f"R9_ZONES_VITALES_{species.upper()}_COMPUTED_Ω"
    assert r["species"] == species
    assert 0 <= r["mean_score"] <= 100
    assert Path(r["output_raster"]).exists()
    assert len(r["raster_sha256"]) == 64
    assert r["habitat_band_used"] in [1, 2, 3, 4, 5]


# ═════════════════════════════════════════════════════════════════════════
# 3. compute_r9_repos × 5 espèces
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("species",
    ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"])
def test_repos_executes_per_species(
        r16b, loader, fake_subset_with_rasters, tmp_path, species):
    pheno = loader.load_dictionary("phenologie_saisonniere")
    out = tmp_path / "r16b_repos"
    r = r16b.compute_r9_repos(
        species=species,
        subset_path=fake_subset_with_rasters["subset"],
        couvert_securite_tif=fake_subset_with_rasters["couvert"],
        exclusions_tif=fake_subset_with_rasters["exclusions"],
        phenologie_dict=pheno,
        output_root=out,
    )
    assert r["manifest_id"] == \
        f"R9_REPOS_{species.upper()}_COMPUTED_Ω"
    assert 0 <= r["mean_score"] <= 100
    assert Path(r["output_raster"]).exists()


# ═════════════════════════════════════════════════════════════════════════
# 4. compute_r9_alimentation × 5 espèces
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("species",
    ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"])
def test_alimentation_executes_per_species(
        r16b, loader, fake_subset_with_rasters, tmp_path, species):
    pheno = loader.load_dictionary("phenologie_saisonniere")
    out = tmp_path / "r16b_alim"
    r = r16b.compute_r9_alimentation(
        species=species,
        subset_path=fake_subset_with_rasters["subset"],
        zones_humides_tif=fake_subset_with_rasters["humides"],
        exclusions_tif=fake_subset_with_rasters["exclusions"],
        phenologie_dict=pheno,
        output_root=out,
    )
    assert r["manifest_id"] == \
        f"R9_ALIMENTATION_{species.upper()}_COMPUTED_Ω"
    assert 0 <= r["mean_score"] <= 100
    # Confirme note ANTI_GÉNÉRIQUE explicite
    assert "anti_generique_note" in r
    assert "NUTRITION" in r["anti_generique_note"]


# ═════════════════════════════════════════════════════════════════════════
# 5. compute_r9_rut × 5 espèces
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("species",
    ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"])
def test_rut_executes_per_species(
        r16b, loader, fake_subset_with_rasters, tmp_path, species):
    pheno = loader.load_dictionary("phenologie_saisonniere")
    out = tmp_path / "r16b_rut"
    r = r16b.compute_r9_rut(
        species=species,
        subset_path=fake_subset_with_rasters["subset"],
        habitat_tif=fake_subset_with_rasters["habitat"],
        couvert_securite_tif=fake_subset_with_rasters["couvert"],
        exclusions_tif=fake_subset_with_rasters["exclusions"],
        phenologie_dict=pheno,
        output_root=out,
    )
    assert r["manifest_id"] == \
        f"R9_RUT_{species.upper()}_COMPUTED_Ω"
    assert 0 <= r["mean_score"] <= 100
    assert "rut_peak_months" in r
    assert isinstance(r["rut_peak_months"], list)


# ═════════════════════════════════════════════════════════════════════════
# 6. Cohérence multi-espèces
# ═════════════════════════════════════════════════════════════════════════
def test_rut_peak_months_distinct_across_species(loader):
    """Les 5 espèces n'ont pas tous le rut au même mois."""
    d = loader.load_dictionary("phenologie_saisonniere")
    cal = d["calendar"]
    peaks = {sp: cal[sp]["rut_peak_months"] for sp in cal}
    # Au moins 2 mois distincts dans l'union
    all_peaks = set()
    for v in peaks.values():
        all_peaks.update(v)
    assert len(all_peaks) >= 3


def test_exclusions_zero_score_when_excluded(
        r16b, loader, fake_subset_with_rasters, tmp_path):
    """Si R9_EXCLUSIONS=1 partout, alors score zones_vitales = 0 partout."""
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds
    base_x, base_y = 8000, 467000
    width, height = 50, 50
    transform = from_bounds(
        base_x, base_y, base_x + 5000, base_y + 2000, width, height)
    excl_full_p = tmp_path / "EXCL_FULL.tif"
    with rasterio.open(
        str(excl_full_p), "w", driver="GTiff", count=1,
        height=height, width=width, dtype="uint8",
        crs="EPSG:32198", transform=transform, nodata=255,
    ) as dst:
        dst.write(np.ones((height, width), dtype="uint8"), 1)

    pheno = loader.load_dictionary("phenologie_saisonniere")
    out = tmp_path / "zv_excluded"
    r = r16b.compute_r9_zones_vitales(
        species="chevreuil",
        subset_path=fake_subset_with_rasters["subset"],
        habitat_tif=fake_subset_with_rasters["habitat"],
        couvert_securite_tif=fake_subset_with_rasters["couvert"],
        zones_humides_tif=fake_subset_with_rasters["humides"],
        exclusions_tif=excl_full_p,
        phenologie_dict=pheno,
        output_root=out,
    )
    assert r["mean_score"] == 0.0
    assert r["n_high_value_polygons"] == 0


# ═════════════════════════════════════════════════════════════════════════
# 7. Pipeline orchestrator
# ═════════════════════════════════════════════════════════════════════════
def test_pipeline_executes_subset_species(
        r16b, fake_subset_with_rasters, tmp_path, monkeypatch):
    """Pipeline avec 1 espèce + 1 target → 1 cible."""
    state_p = tmp_path / "R9_RECALC_STATE.json"
    out_root = tmp_path / "r16b_derivs"
    monkeypatch.setattr(r16b, "R9_RECALC_STATE_PATH", state_p)
    monkeypatch.setattr(r16b, "DERIVATIVES_R9_ROOT", out_root)
    # Préparer les rasters dépendances dans DERIVATIVES_R9_ROOT et P1_ROOT
    p1_root = tmp_path / "p1_derivs"
    p1_root.mkdir()
    out_root.mkdir()
    monkeypatch.setattr(r16b, "DERIVATIVES_P1_ROOT", p1_root)
    # Copier les rasters fixture
    import shutil
    shutil.copy(fake_subset_with_rasters["habitat"],
                p1_root / "MFFP_HABITAT_BRUT.tif")
    shutil.copy(fake_subset_with_rasters["couvert"],
                out_root / "R9_COUVERT_SECURITE.tif")
    shutil.copy(fake_subset_with_rasters["humides"],
                out_root / "R9_ZONES_HUMIDES.tif")
    shutil.copy(fake_subset_with_rasters["exclusions"],
                out_root / "R9_EXCLUSIONS.tif")
    monkeypatch.setattr(
        r16b, "auto_pick_subset",
        lambda: fake_subset_with_rasters["subset"])

    res = r16b.execute_r16b_pipeline(
        species_subset=["chevreuil"],
        targets_subset=["ZONES_VITALES"])
    assert res["manifest_id"] == "R9_PHASE3_R16B_PIPELINE_COMPLETED_Ω"
    assert res["n_targets_succeeded"] == 1
    assert "R9_ZONES_VITALES_CHEVREUIL" in res["targets_succeeded"]
    assert state_p.exists()
    state = json.loads(state_p.read_text(encoding="utf-8"))
    assert "R9_ZONES_VITALES_CHEVREUIL" in state["targets"]
    assert state["targets"]["R9_ZONES_VITALES_CHEVREUIL"]["status"] == \
        "OK_REAL"
    assert state["targets"]["R9_ZONES_VITALES_CHEVREUIL"]["ordre"] == \
        "N°52-R16-B"


def test_pipeline_missing_dependencies_raises(
        r16b, fake_subset_with_rasters, tmp_path, monkeypatch):
    """Si MFFP_HABITAT_BRUT absent → raise."""
    out_root = tmp_path / "no_deps"
    p1_root = tmp_path / "no_p1"
    out_root.mkdir(); p1_root.mkdir()
    monkeypatch.setattr(r16b, "DERIVATIVES_R9_ROOT", out_root)
    monkeypatch.setattr(r16b, "DERIVATIVES_P1_ROOT", p1_root)
    monkeypatch.setattr(
        r16b, "auto_pick_subset",
        lambda: fake_subset_with_rasters["subset"])
    with pytest.raises(RuntimeError, match="Dépendances"):
        r16b.execute_r16b_pipeline(
            species_subset=["chevreuil"],
            targets_subset=["ZONES_VITALES"])


# ═════════════════════════════════════════════════════════════════════════
# 8. ANTI_GÉNÉRIQUE_STRICT — Notes explicites
# ═════════════════════════════════════════════════════════════════════════
def test_alimentation_documents_nutrition_hooks_absence(
        r16b, loader, fake_subset_with_rasters, tmp_path):
    """Le résultat alimentation contient une note explicite sur les hooks
    NUTRITION absents (transparence ANTI_GÉNÉRIQUE_STRICT)."""
    pheno = loader.load_dictionary("phenologie_saisonniere")
    out = tmp_path / "alim_note"
    r = r16b.compute_r9_alimentation(
        species="chevreuil",
        subset_path=fake_subset_with_rasters["subset"],
        zones_humides_tif=fake_subset_with_rasters["humides"],
        exclusions_tif=fake_subset_with_rasters["exclusions"],
        phenologie_dict=pheno,
        output_root=out,
    )
    note = r["anti_generique_note"]
    assert "NUTRITION" in note
    assert "absent" in note.lower() or "Q3" in note
