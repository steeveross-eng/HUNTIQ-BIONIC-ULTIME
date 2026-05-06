"""
Phase XXVIII · ORDRE N°52-R16-D — Tests anti-régressifs R9 TACTICAL GROUND
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Tests des 3 cibles tactiques R16-D (noms NEUTRES — aucun mot-clé exclu) :
  · R9_SALINES                (raster + GPKG)
  · R9_AFFUTS                 (raster + GPKG)
  · R9_TACTICAL_ZONES         (vecteur uniquement)
+ Probe registry-aware des 6 hooks TERRITOIRE_ULTIME.

Naming policy: aucun keyword exclu BCE-4X (territoire, ..., bionic_zone).
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
def r16d():
    import engines.v8_institutional.especes.r9_phase3_r16d_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def fake_r16d_inputs(tmp_path):
    """Subset + rasters dépendances pour tester R16-D."""
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
            "type_couv": ["R", "F", "M", "FE", "RE"][i % 5],
            "gr_ess": ["R", "F", "M", "R", "F"][i % 5],
            "cl_age": ["30", "50", "70", "90", "VIN"][i % 5],
            "cl_dens": ["A", "B", "C", "B", "A"][i % 5],
            "cl_haut": ["3", "4", "5", "5", "6"][i % 5],
            "cl_pent": ["3", "2", "1", "3", "2"][i % 5],
            "cl_drai": ["3", "5", "4", "3", "2"][i % 5],
            "type_eco": ["RB1", "MJ1", "RC1", "FE2", "RA1"][i % 5],
            "geometry": Polygon([
                (x, y), (x + 1000, y),
                (x + 1000, y + 1000), (x, y + 1000)]),
        })
    gdf = gpd.GeoDataFrame(rows, crs="EPSG:32198")
    subset_p = tmp_path / "fake_subset.gpkg"
    gdf.to_file(str(subset_p), driver="GPKG", layer="pee_maj")

    width, height = 50, 50
    transform = from_bounds(
        base_x, base_y, base_x + 5000, base_y + 2000, width, height)

    rasters = tmp_path / "rasters"
    rasters.mkdir(exist_ok=True)

    def _write(name, data, count=1, dtype="uint8", nodata=255):
        p = rasters / name
        with rasterio.open(
            str(p), "w", driver="GTiff", count=count,
            height=height, width=width, dtype=dtype,
            crs="EPSG:32198", transform=transform, nodata=nodata,
        ) as dst:
            if count == 1:
                dst.write(data, 1)
            else:
                for b in range(count):
                    dst.write(data[b], b + 1)
        return p

    # zones humides (binaire)
    humides = _write(
        "R9_ZONES_HUMIDES.tif",
        np.where(
            np.arange(width)[None, :] < width // 2, 1, 0
        ).astype("uint8"))

    # productivité m³/ha
    productivity = _write(
        "MFFP_PRODUCTIVITE.tif",
        np.full((height, width), 200.0, dtype="float32"),
        dtype="float32", nodata=-9999)

    # habitat brut 5 espèces (5 bandes)
    habitat = _write(
        "MFFP_HABITAT_BRUT.tif",
        np.tile(
            np.arange(60, 90, 5)[:5, None, None],
            (1, height, width)).astype("uint8"),
        count=5)

    # link multi (corridors_multi)
    corr_multi = _write(
        "R9_LINK_MULTI.tif",
        np.full((height, width), 80, dtype="uint8"))

    # exclusions (toutes à 0)
    excl = _write(
        "R9_EXCLUSIONS.tif",
        np.zeros((height, width), dtype="uint8"))

    # couvert sécurité (modéré=60, dans la fourchette 40-70)
    couvert = _write(
        "R9_COUVERT_SECURITE.tif",
        np.full((height, width), 60, dtype="uint8"))

    # alimentation par espèce (5 fichiers)
    alim_tifs = {}
    for sp, val in (
            ("chevreuil", 75),
            ("orignal", 80),
            ("ours_noir", 70),
            ("dindon", 65),
            ("wapiti", 78)):
        alim_tifs[sp] = _write(
            f"R9_ALIM_{sp.upper()}.tif",
            np.full((height, width), val, dtype="uint8"))

    # zones vitales par espèce (utilisé pour aggregat tactical)
    zv_tifs = {}
    for sp, val in (
            ("chevreuil", 80),
            ("orignal", 85),
            ("ours_noir", 70),
            ("dindon", 60),
            ("wapiti", 75)):
        zv_tifs[sp] = _write(
            f"R9_ZV_{sp.upper()}.tif",
            np.full((height, width), val, dtype="uint8"))

    # link_score per species
    link_tifs = {}
    for sp, val in (
            ("chevreuil", 70),
            ("orignal", 75),
            ("ours_noir", 65),
            ("dindon", 60),
            ("wapiti", 72)):
        link_tifs[sp] = _write(
            f"R9_LK_{sp.upper()}.tif",
            np.full((height, width), val, dtype="uint8"))

    # hotspot binaire per species (0/1)
    hot_tifs = {}
    for sp in ("chevreuil", "orignal", "ours_noir", "dindon", "wapiti"):
        arr = np.zeros((height, width), dtype="uint8")
        arr[:height // 2, :] = 1  # top half = hotspot
        hot_tifs[sp] = _write(
            f"R9_HOT_{sp.upper()}.tif", arr)

    # repos per species
    repos_tifs = {}
    for sp, val in (
            ("chevreuil", 70),
            ("orignal", 72),
            ("ours_noir", 68),
            ("dindon", 55),
            ("wapiti", 70)):
        repos_tifs[sp] = _write(
            f"R9_RP_{sp.upper()}.tif",
            np.full((height, width), val, dtype="uint8"))

    return {
        "subset": str(subset_p),
        "humides": humides,
        "productivity": productivity,
        "habitat": habitat,
        "corr_multi": corr_multi,
        "exclusions": excl,
        "couvert": couvert,
        "alim_tifs": alim_tifs,
        "zv_tifs": zv_tifs,
        "link_tifs": link_tifs,
        "hot_tifs": hot_tifs,
        "repos_tifs": repos_tifs,
        "rasters_root": rasters,
    }


# ═════════════════════════════════════════════════════════════════════════
# 1. API + dictionnaire
# ═════════════════════════════════════════════════════════════════════════
def test_r16d_module_exports(r16d):
    assert hasattr(r16d, "compute_r9_salines")
    assert hasattr(r16d, "compute_r9_affuts")
    assert hasattr(r16d, "compute_r9_tactical_zones")
    assert hasattr(r16d, "probe_all_six_hooks")
    assert hasattr(r16d, "execute_r16d_pipeline")
    assert "execute_r16d_pipeline" in r16d.__all__


def test_loader_tactical_dict_registered(loader):
    assert "tactical_ground_rules" in loader.DICTIONARY_FILES


def test_loader_all_validated_for_r16d(loader):
    assert loader.all_validated_for_r16d() is True


def test_tactical_dict_structure(loader):
    d = loader.load_dictionary("tactical_ground_rules")
    assert d["status"] == "VALIDÉ"
    for sec in ("salines_rules", "affuts_rules", "territoires_rules",
                "hooks_integration"):
        assert sec in d
    # Sum salines weights = 1.0
    w_s = d["salines_rules"]["score_formula_weights"]
    assert sum(w_s.values()) == pytest.approx(1.0)
    # Sum affuts weights = 1.0
    w_a = d["affuts_rules"]["score_formula_weights"]
    assert sum(w_a.values()) == pytest.approx(1.0)
    # Sum tactical layer weights = 1.0
    w_t = d["territoires_rules"]["score_formula_weights_per_layer"]
    assert sum(w_t.values()) == pytest.approx(1.0)
    # Sum species weights = 1.0
    sw = d["territoires_rules"]["species_weights_by_mass"]
    assert sum(sw.values()) == pytest.approx(1.0)


# ═════════════════════════════════════════════════════════════════════════
# 2. probe_all_six_hooks (registry-aware)
# ═════════════════════════════════════════════════════════════════════════
def test_probe_six_hooks_returns_six(r16d):
    res = r16d.probe_all_six_hooks()
    assert res["manifest_id"] == "R16D_HOOKS_PROBE_Ω"
    assert res["n_hooks_total"] == 6
    for h in ("IA_VISION", "DONNEES_CHASSEUR", "ENVIRONNEMENT",
              "NUTRITION", "COMPORTEMENT", "PREDICTIF"):
        assert h in res["hooks"]


def test_probe_six_hooks_fallback_anti_generique(r16d):
    res = r16d.probe_all_six_hooks()
    # ENVIRONNEMENT est un stub R16-D-PREP → is_stub True, available False
    # (aucun fichier source, ANTI_GÉNÉRIQUE_STRICT)
    env = res["hooks"]["ENVIRONNEMENT"]
    assert env.get("is_stub") is True
    assert env.get("available") is False
    assert env.get("anti_generique_strict") is True
    assert env.get("expected_paths_count", 0) > 0
    assert env.get("paths_present") == []


# ═════════════════════════════════════════════════════════════════════════
# 3. compute_r9_salines
# ═════════════════════════════════════════════════════════════════════════
def test_salines_executes(r16d, loader, fake_r16d_inputs, tmp_path):
    tactical = loader.load_dictionary("tactical_ground_rules")
    out = tmp_path / "salines_out"
    r = r16d.compute_r9_salines(
        subset_path=fake_r16d_inputs["subset"],
        zones_humides_tif=fake_r16d_inputs["humides"],
        productivity_tif=fake_r16d_inputs["productivity"],
        habitat_tif=fake_r16d_inputs["habitat"],
        corridors_multi_tif=fake_r16d_inputs["corr_multi"],
        exclusions_tif=fake_r16d_inputs["exclusions"],
        tactical_dict=tactical,
        output_root=out,
    )
    assert r["manifest_id"] == "R9_SALINES_COMPUTED_Ω"
    assert r["ordre"] == "N°52-R16-D"
    assert 0 <= r["mean_score"] <= 100
    assert Path(r["output_raster"]).exists()
    assert Path(r["output_vector"]).exists()
    assert len(r["raster_sha256"]) == 64
    # weights cohérents
    assert sum(r["weights_applied"].values()) == pytest.approx(1.0)


def test_salines_excluded_zone_score_zero(
        r16d, loader, fake_r16d_inputs, tmp_path):
    """R9_EXCLUSIONS=1 → score=0 partout."""
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds
    base_x, base_y = 8000, 467000
    width, height = 50, 50
    transform = from_bounds(
        base_x, base_y, base_x + 5000, base_y + 2000, width, height)
    excl_full = tmp_path / "EXCL_FULL.tif"
    with rasterio.open(
        str(excl_full), "w", driver="GTiff", count=1,
        height=height, width=width, dtype="uint8",
        crs="EPSG:32198", transform=transform, nodata=255,
    ) as dst:
        dst.write(np.ones((height, width), dtype="uint8"), 1)

    tactical = loader.load_dictionary("tactical_ground_rules")
    out = tmp_path / "sal_excluded"
    r = r16d.compute_r9_salines(
        subset_path=fake_r16d_inputs["subset"],
        zones_humides_tif=fake_r16d_inputs["humides"],
        productivity_tif=fake_r16d_inputs["productivity"],
        habitat_tif=fake_r16d_inputs["habitat"],
        corridors_multi_tif=fake_r16d_inputs["corr_multi"],
        exclusions_tif=excl_full,
        tactical_dict=tactical,
        output_root=out,
    )
    assert r["mean_score"] == 0.0
    assert r["n_high_saline_polygons"] == 0


def test_salines_drainage_transitionnel_score_boost(
        r16d, loader, fake_r16d_inputs, tmp_path):
    """Polygones avec cl_drai ∈ {4,5} → boost via drainage_transitionnel."""
    tactical = loader.load_dictionary("tactical_ground_rules")
    out = tmp_path / "sal_drai"
    r = r16d.compute_r9_salines(
        subset_path=fake_r16d_inputs["subset"],
        zones_humides_tif=fake_r16d_inputs["humides"],
        productivity_tif=fake_r16d_inputs["productivity"],
        habitat_tif=fake_r16d_inputs["habitat"],
        corridors_multi_tif=fake_r16d_inputs["corr_multi"],
        exclusions_tif=fake_r16d_inputs["exclusions"],
        tactical_dict=tactical,
        output_root=out,
    )
    assert r["drainage_transitionnel_codes"] == ["4", "5"]
    # mean_score doit être > 0 (score réel calculé)
    assert r["mean_score"] > 0


# ═════════════════════════════════════════════════════════════════════════
# 4. compute_r9_affuts
# ═════════════════════════════════════════════════════════════════════════
def test_affuts_executes(r16d, loader, fake_r16d_inputs, tmp_path):
    tactical = loader.load_dictionary("tactical_ground_rules")
    out = tmp_path / "affut_out"
    r = r16d.compute_r9_affuts(
        subset_path=fake_r16d_inputs["subset"],
        corridors_multi_tif=fake_r16d_inputs["corr_multi"],
        alimentation_tifs=fake_r16d_inputs["alim_tifs"],
        couvert_securite_tif=fake_r16d_inputs["couvert"],
        exclusions_tif=fake_r16d_inputs["exclusions"],
        tactical_dict=tactical,
        output_root=out,
    )
    assert r["manifest_id"] == "R9_AFFUTS_COMPUTED_Ω"
    assert r["ordre"] == "N°52-R16-D"
    assert 0 <= r["mean_score"] <= 100
    assert Path(r["output_raster"]).exists()
    assert Path(r["output_vector"]).exists()
    assert len(r["raster_sha256"]) == 64
    # 4 couches alimentation utilisées (chevreuil, orignal, ours_noir, dindon)
    assert r["n_alimentation_layers_used"] == 4


def test_affuts_high_score_with_couvert_modere(
        r16d, loader, fake_r16d_inputs, tmp_path):
    """Couvert sécurité = 60 (∈ [40,70]) → score couvert maximal."""
    tactical = loader.load_dictionary("tactical_ground_rules")
    out = tmp_path / "aff_modere"
    r = r16d.compute_r9_affuts(
        subset_path=fake_r16d_inputs["subset"],
        corridors_multi_tif=fake_r16d_inputs["corr_multi"],
        alimentation_tifs=fake_r16d_inputs["alim_tifs"],
        couvert_securite_tif=fake_r16d_inputs["couvert"],
        exclusions_tif=fake_r16d_inputs["exclusions"],
        tactical_dict=tactical,
        output_root=out,
    )
    # Couvert 60 ∈ [40,70] → cv_score = 100 → score moyen élevé (>50)
    assert r["mean_score"] >= 50


def test_affuts_excluded_zone_score_zero(
        r16d, loader, fake_r16d_inputs, tmp_path):
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds
    base_x, base_y = 8000, 467000
    width, height = 50, 50
    transform = from_bounds(
        base_x, base_y, base_x + 5000, base_y + 2000, width, height)
    excl_full = tmp_path / "EXCL_F.tif"
    with rasterio.open(
        str(excl_full), "w", driver="GTiff", count=1,
        height=height, width=width, dtype="uint8",
        crs="EPSG:32198", transform=transform, nodata=255,
    ) as dst:
        dst.write(np.ones((height, width), dtype="uint8"), 1)

    tactical = loader.load_dictionary("tactical_ground_rules")
    out = tmp_path / "aff_excluded"
    r = r16d.compute_r9_affuts(
        subset_path=fake_r16d_inputs["subset"],
        corridors_multi_tif=fake_r16d_inputs["corr_multi"],
        alimentation_tifs=fake_r16d_inputs["alim_tifs"],
        couvert_securite_tif=fake_r16d_inputs["couvert"],
        exclusions_tif=excl_full,
        tactical_dict=tactical,
        output_root=out,
    )
    assert r["mean_score"] == 0.0
    assert r["n_high_affut_polygons"] == 0


# ═════════════════════════════════════════════════════════════════════════
# 5. compute_r9_tactical_zones (vecteur uniquement)
# ═════════════════════════════════════════════════════════════════════════
def test_tactical_zones_executes(
        r16d, loader, fake_r16d_inputs, tmp_path):
    tactical = loader.load_dictionary("tactical_ground_rules")
    out = tmp_path / "tac_out"
    layers_per_species = {}
    for sp in ("chevreuil", "orignal", "ours_noir", "dindon", "wapiti"):
        layers_per_species[sp] = {
            "zones_vitales": fake_r16d_inputs["zv_tifs"][sp],
            "link_score": fake_r16d_inputs["link_tifs"][sp],
            "hotspot_binary": fake_r16d_inputs["hot_tifs"][sp],
            "repos": fake_r16d_inputs["repos_tifs"][sp],
            "alimentation": fake_r16d_inputs["alim_tifs"][sp],
        }
    r = r16d.compute_r9_tactical_zones(
        subset_path=fake_r16d_inputs["subset"],
        layers_per_species_tifs=layers_per_species,
        exclusions_tif=fake_r16d_inputs["exclusions"],
        tactical_dict=tactical,
        output_root=out,
    )
    assert r["manifest_id"] == "R9_TACTICAL_ZONES_COMPUTED_Ω"
    assert r["ordre"] == "N°52-R16-D"
    assert r["vector_only_no_raster"] is True
    # vecteur uniquement → pas d'output_raster
    assert "output_raster" not in r
    assert Path(r["output_vector"]).exists()
    assert len(r["vector_sha256"]) == 64
    # poids espèces normalisés somment à 1.0
    weights = r["species_weights_normalized"]
    assert sum(weights.values()) == pytest.approx(1.0, abs=0.01)
    # 5 espèces utilisées
    assert len(r["layers_used_per_species"]) == 5


def test_tactical_zones_no_raster_output_doctrinal(
        r16d, loader, fake_r16d_inputs, tmp_path):
    """ANTI_GÉNÉRIQUE_STRICT : R9_TERRITOIRES = vecteur uniquement,
    aucun .tif émis."""
    tactical = loader.load_dictionary("tactical_ground_rules")
    out = tmp_path / "no_raster_zone"
    layers_per_species = {
        "chevreuil": {
            "zones_vitales": fake_r16d_inputs["zv_tifs"]["chevreuil"],
            "link_score": fake_r16d_inputs["link_tifs"]["chevreuil"],
            "hotspot_binary": fake_r16d_inputs["hot_tifs"]["chevreuil"],
            "repos": fake_r16d_inputs["repos_tifs"]["chevreuil"],
            "alimentation": fake_r16d_inputs["alim_tifs"]["chevreuil"],
        }
    }
    r = r16d.compute_r9_tactical_zones(
        subset_path=fake_r16d_inputs["subset"],
        layers_per_species_tifs=layers_per_species,
        exclusions_tif=fake_r16d_inputs["exclusions"],
        tactical_dict=tactical,
        output_root=out,
    )
    assert r["manifest_id"] == "R9_TACTICAL_ZONES_COMPUTED_Ω"
    # Aucun .tif n'a été écrit dans out
    tif_files = list(Path(out).glob("*.tif"))
    assert len(tif_files) == 0
    # GPKG bien présent
    gpkg_files = list(Path(out).glob("*.gpkg"))
    assert len(gpkg_files) >= 1


def test_tactical_zones_excluded_full_returns_zero(
        r16d, loader, fake_r16d_inputs, tmp_path):
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds
    base_x, base_y = 8000, 467000
    width, height = 50, 50
    transform = from_bounds(
        base_x, base_y, base_x + 5000, base_y + 2000, width, height)
    excl_full = tmp_path / "EXCL_F.tif"
    with rasterio.open(
        str(excl_full), "w", driver="GTiff", count=1,
        height=height, width=width, dtype="uint8",
        crs="EPSG:32198", transform=transform, nodata=255,
    ) as dst:
        dst.write(np.ones((height, width), dtype="uint8"), 1)

    tactical = loader.load_dictionary("tactical_ground_rules")
    out = tmp_path / "tac_excluded"
    layers_per_species = {}
    for sp in ("chevreuil", "orignal", "ours_noir", "dindon", "wapiti"):
        layers_per_species[sp] = {
            "zones_vitales": fake_r16d_inputs["zv_tifs"][sp],
            "link_score": fake_r16d_inputs["link_tifs"][sp],
            "hotspot_binary": fake_r16d_inputs["hot_tifs"][sp],
            "repos": fake_r16d_inputs["repos_tifs"][sp],
            "alimentation": fake_r16d_inputs["alim_tifs"][sp],
        }
    r = r16d.compute_r9_tactical_zones(
        subset_path=fake_r16d_inputs["subset"],
        layers_per_species_tifs=layers_per_species,
        exclusions_tif=excl_full,
        tactical_dict=tactical,
        output_root=out,
    )
    # Toutes zones exclues → 0 polygones haute valeur
    assert r["n_high_value_zones"] == 0
    assert r["mean_fusion_score"] == 0.0


# ═════════════════════════════════════════════════════════════════════════
# 6. Pipeline orchestrator R16-D
# ═════════════════════════════════════════════════════════════════════════
def test_pipeline_executes_full_three_targets(
        r16d, fake_r16d_inputs, tmp_path, monkeypatch):
    """Pipeline complet R16-D → 3 cibles succedeed."""
    import shutil
    state_p = tmp_path / "R9_STATE.json"
    out_root = tmp_path / "r16d_derivs"
    p1_root = tmp_path / "p1_derivs"
    out_root.mkdir()
    p1_root.mkdir()

    monkeypatch.setattr(r16d, "R9_RECALC_STATE_PATH", state_p)
    monkeypatch.setattr(r16d, "DERIVATIVES_R9_ROOT", out_root)
    monkeypatch.setattr(r16d, "DERIVATIVES_P1_ROOT", p1_root)

    # Copie des dépendances dans les bons dossiers
    shutil.copy(fake_r16d_inputs["humides"],
                out_root / "R9_ZONES_HUMIDES.tif")
    shutil.copy(fake_r16d_inputs["productivity"],
                p1_root / "MFFP_PRODUCTIVITE.tif")
    shutil.copy(fake_r16d_inputs["habitat"],
                p1_root / "MFFP_HABITAT_BRUT.tif")
    shutil.copy(fake_r16d_inputs["corr_multi"],
                out_root / "R9_CORRIDORS_MULTI_ESPECES.tif")
    shutil.copy(fake_r16d_inputs["exclusions"],
                out_root / "R9_EXCLUSIONS.tif")
    shutil.copy(fake_r16d_inputs["couvert"],
                out_root / "R9_COUVERT_SECURITE.tif")
    # Alimentation per species
    for sp, src in fake_r16d_inputs["alim_tifs"].items():
        shutil.copy(src, out_root / f"R9_ALIMENTATION_{sp.upper()}.tif")
    # zones vitales / link / hotspots / repos per species
    for sp, src in fake_r16d_inputs["zv_tifs"].items():
        shutil.copy(src, out_root / f"R9_ZONES_VITALES_{sp.upper()}.tif")
    for sp, src in fake_r16d_inputs["link_tifs"].items():
        shutil.copy(src, out_root / f"R9_CORRIDORS_{sp.upper()}.tif")
    for sp, src in fake_r16d_inputs["hot_tifs"].items():
        shutil.copy(src, out_root / f"R9_HOTSPOTS_{sp.upper()}.tif")
    for sp, src in fake_r16d_inputs["repos_tifs"].items():
        shutil.copy(src, out_root / f"R9_REPOS_{sp.upper()}.tif")

    monkeypatch.setattr(
        r16d, "auto_pick_subset",
        lambda: fake_r16d_inputs["subset"])

    res = r16d.execute_r16d_pipeline()
    assert res["manifest_id"] == "R9_PHASE3_R16D_PIPELINE_COMPLETED_Ω"
    assert res["ordre"] == "N°52-R16-D"
    # 3 cibles succedeed
    assert res["n_targets_succeeded"] == 3
    for t in ("R9_SALINES", "R9_AFFUTS", "R9_TERRITOIRES"):
        assert t in res["targets_succeeded"]
    # Hooks probe présent
    probe = res["territoire_ultime_six_hooks_probe"]
    assert probe["n_hooks_total"] == 6
    # State persisté
    assert state_p.exists()
    state = json.loads(state_p.read_text(encoding="utf-8"))
    for t in ("R9_SALINES", "R9_AFFUTS", "R9_TERRITOIRES"):
        assert state["targets"][t]["status"] == "OK_REAL"
        assert state["targets"][t]["ordre"] == "N°52-R16-D"
    assert state["status"] == "OK_REAL_PARTIAL_R16D"


def test_pipeline_subset_targets(
        r16d, fake_r16d_inputs, tmp_path, monkeypatch):
    """Subset = ['R9_SALINES'] → 1 cible succedeed."""
    import shutil
    state_p = tmp_path / "R9_STATE.json"
    out_root = tmp_path / "r16d_one"
    p1_root = tmp_path / "p1_one"
    out_root.mkdir()
    p1_root.mkdir()

    monkeypatch.setattr(r16d, "R9_RECALC_STATE_PATH", state_p)
    monkeypatch.setattr(r16d, "DERIVATIVES_R9_ROOT", out_root)
    monkeypatch.setattr(r16d, "DERIVATIVES_P1_ROOT", p1_root)

    shutil.copy(fake_r16d_inputs["humides"],
                out_root / "R9_ZONES_HUMIDES.tif")
    shutil.copy(fake_r16d_inputs["productivity"],
                p1_root / "MFFP_PRODUCTIVITE.tif")
    shutil.copy(fake_r16d_inputs["habitat"],
                p1_root / "MFFP_HABITAT_BRUT.tif")
    shutil.copy(fake_r16d_inputs["corr_multi"],
                out_root / "R9_CORRIDORS_MULTI_ESPECES.tif")
    shutil.copy(fake_r16d_inputs["exclusions"],
                out_root / "R9_EXCLUSIONS.tif")
    shutil.copy(fake_r16d_inputs["couvert"],
                out_root / "R9_COUVERT_SECURITE.tif")

    monkeypatch.setattr(
        r16d, "auto_pick_subset",
        lambda: fake_r16d_inputs["subset"])

    res = r16d.execute_r16d_pipeline(
        targets_subset=["R9_SALINES"])
    assert res["n_targets_succeeded"] == 1
    assert res["targets_succeeded"] == ["R9_SALINES"]


def test_pipeline_missing_dependencies_raises(
        r16d, fake_r16d_inputs, tmp_path, monkeypatch):
    """Si dépendances absentes → RuntimeError."""
    out_root = tmp_path / "no_deps"
    p1_root = tmp_path / "no_p1"
    out_root.mkdir()
    p1_root.mkdir()
    monkeypatch.setattr(r16d, "DERIVATIVES_R9_ROOT", out_root)
    monkeypatch.setattr(r16d, "DERIVATIVES_P1_ROOT", p1_root)
    monkeypatch.setattr(
        r16d, "auto_pick_subset",
        lambda: fake_r16d_inputs["subset"])
    with pytest.raises(RuntimeError, match="Dépendances"):
        r16d.execute_r16d_pipeline()


def test_pipeline_no_subset_raises(r16d, monkeypatch):
    """Si auto_pick_subset retourne None → RuntimeError."""
    monkeypatch.setattr(r16d, "auto_pick_subset", lambda: None)
    with pytest.raises(RuntimeError, match="subset"):
        r16d.execute_r16d_pipeline()


# ═════════════════════════════════════════════════════════════════════════
# 7. Anti-régression : intégration dictionnaire + validation
# ═════════════════════════════════════════════════════════════════════════
def test_r16d_validation_chain_strict(loader):
    """R16-D requiert R16-D-PREP (R16-C ⟶ R16-B ⟶ R16-A ⟶ P1) +
    tactical_ground_rules tous validés."""
    assert loader.all_validated_for_p0() is True
    assert loader.all_validated_for_p1() is True
    assert loader.all_validated_for_r16a() is True
    assert loader.all_validated_for_r16b() is True
    assert loader.all_validated_for_r16c() is True
    assert loader.all_validated_for_r16dprep() is True
    assert loader.all_validated_for_r16d() is True


def test_r16d_dict_ordre_correct(loader):
    d = loader.load_dictionary("tactical_ground_rules")
    assert d["ordre"] == "N°52-R16-D"
    assert d["doctrine"] == "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT"
    assert d["v30_lock"] == "INVIOLÉ"


def test_hooks_integration_section_in_dict(loader):
    d = loader.load_dictionary("tactical_ground_rules")
    h = d["hooks_integration"]
    assert h["anti_generique_strict"] is True
    assert h["fallback_if_unavailable"] == \
        "skip_with_log_no_score_modification"
    assert len(h["hooks_to_probe"]) == 6
