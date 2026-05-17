"""
Phase XXVIII · ORDRE N°52-R16-C — Tests anti-régressifs R9 CONNECTIVITY
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT
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
def r16c():
    import engines.v8_institutional.especes.r9_phase3_r16c_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def fake_r16c_inputs(tmp_path):
    """Subset + 9 rasters dépendances pour tester R16-C."""
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

    width, height = 50, 50
    transform = from_bounds(
        base_x, base_y, base_x + 5000, base_y + 2000, width, height)

    rasters = tmp_path / "rasters"
    rasters.mkdir(exist_ok=True)

    def _write(name, data, count=1, dtype="uint8"):
        p = rasters / name
        with rasterio.open(
            str(p), "w", driver="GTiff", count=count,
            height=height, width=width, dtype=dtype,
            crs="EPSG:32198", transform=transform, nodata=255,
        ) as dst:
            if count == 1:
                dst.write(data, 1)
            else:
                for b in range(count):
                    dst.write(data[b], b + 1)
        return p

    habitat = _write(
        "MFFP_HABITAT_BRUT.tif",
        np.tile(
            np.arange(60, 90, 5)[:5, None, None],
            (1, height, width)).astype("uint8"),
        count=5)
    couvert = _write(
        "R9_COUVERT_SECURITE.tif",
        np.full((height, width), 70, dtype="uint8"))
    humides = _write(
        "R9_ZONES_HUMIDES.tif",
        np.where(
            np.arange(width)[None, :] < width // 2, 1, 0
        ).astype("uint8"))
    excl = _write(
        "R9_EXCLUSIONS.tif",
        np.zeros((height, width), dtype="uint8"))
    frag = _write(
        "MFFP_FRAGMENTATION_INDEX.tif",
        np.full((height, width), 0.3, dtype="float32"),
        dtype="float32")
    productivity = _write(
        "MFFP_PRODUCTIVITE.tif",
        np.full((height, width), 100.0, dtype="float32"),
        dtype="float32")
    structure = _write(
        "MFFP_STRUCTURE.tif",
        np.full((height, width), 4, dtype="uint8"))
    continuity = _write(
        "MFFP_CONTINUITE.tif",
        np.full((height, width), 3, dtype="uint8"))
    # zones_vitales high (score=85) pour passage testing
    zv_chevreuil = _write(
        "R9_ZONES_VITALES_CHEVREUIL.tif",
        np.full((height, width), 85, dtype="uint8"))

    return {
        "subset": str(subset_p),
        "habitat": habitat, "couvert": couvert,
        "humides": humides, "exclusions": excl,
        "fragmentation": frag, "productivity": productivity,
        "structure": structure, "continuity": continuity,
        "zv_chevreuil": zv_chevreuil,
        "rasters_root": rasters,
    }


# ═════════════════════════════════════════════════════════════════════════
# 1. API + dict
# ═════════════════════════════════════════════════════════════════════════
def test_r16c_module_exports(r16c):
    assert hasattr(r16c, "compute_r9_corridors_species")
    assert hasattr(r16c, "compute_r9_zones_passage_species")
    assert hasattr(r16c, "compute_r9_hotspots_species")
    assert hasattr(r16c, "compute_r9_corridors_multi_especes")
    assert hasattr(r16c, "execute_r16c_pipeline")
    assert "execute_r16c_pipeline" in r16c.__all__
    assert r16c.TARGETS_R16C_PER_SPECIES == [
        "CORRIDORS", "ZONES_PASSAGE", "HOTSPOTS"]


def test_loader_connectivity_dict_registered(loader):
    assert "connectivity_rules" in loader.DICTIONARY_FILES


def test_loader_all_validated_for_r16c(loader):
    assert loader.all_validated_for_r16c() is True


def test_connectivity_dict_structure(loader):
    d = loader.load_dictionary("connectivity_rules")
    assert d["status"] == "VALIDÉ"
    for sec in ("corridors_rules", "zones_passage_rules",
                "hotspots_rules", "corridors_multi_especes_rules"):
        assert sec in d
    # Sum corridor weights = 1.0
    w = d["corridors_rules"]["score_formula_weights"]
    assert sum(w.values()) == pytest.approx(1.0)
    # Species weights multi sum = 1.0
    sw = d["corridors_multi_especes_rules"]["species_weights_by_mass"]
    assert sum(sw.values()) == pytest.approx(1.0)


# ═════════════════════════════════════════════════════════════════════════
# 2. compute_r9_corridors_species × 5 espèces
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("species",
    ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"])
def test_link_score_species_executes(
        r16c, loader, fake_r16c_inputs, tmp_path, species):
    conn = loader.load_dictionary("connectivity_rules")
    out = tmp_path / f"corr_out_{species}"
    r = r16c.compute_r9_corridors_species(
        species=species,
        subset_path=fake_r16c_inputs["subset"],
        habitat_tif=fake_r16c_inputs["habitat"],
        couvert_securite_tif=fake_r16c_inputs["couvert"],
        fragmentation_tif=fake_r16c_inputs["fragmentation"],
        exclusions_tif=fake_r16c_inputs["exclusions"],
        connectivity_dict=conn,
        output_root=out,
    )
    assert r["manifest_id"] == \
        f"R9_CORRIDORS_{species.upper()}_COMPUTED_Ω"
    assert 0 <= r["mean_score"] <= 100
    assert Path(r["output_raster"]).exists()
    assert Path(r["output_vector"]).exists()
    assert len(r["raster_sha256"]) == 64


def test_link_excluded_polygon_score_zero(
        r16c, loader, fake_r16c_inputs, tmp_path):
    """R9_EXCLUSIONS=1 → cost-link score=0 (anti-générique strict)."""
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

    conn = loader.load_dictionary("connectivity_rules")
    out = tmp_path / "excluded_corr"
    r = r16c.compute_r9_corridors_species(
        species="chevreuil",
        subset_path=fake_r16c_inputs["subset"],
        habitat_tif=fake_r16c_inputs["habitat"],
        couvert_securite_tif=fake_r16c_inputs["couvert"],
        fragmentation_tif=fake_r16c_inputs["fragmentation"],
        exclusions_tif=excl_full,
        connectivity_dict=conn,
        output_root=out,
    )
    assert r["mean_score"] == 0.0


# ═════════════════════════════════════════════════════════════════════════
# 3. compute_r9_zones_passage_species
# ═════════════════════════════════════════════════════════════════════════
def test_zones_passage_chevreuil_executes(
        r16c, loader, fake_r16c_inputs, tmp_path):
    # Génère d'abord corridor chevreuil
    conn = loader.load_dictionary("connectivity_rules")
    out = tmp_path / "passage"
    r_corr = r16c.compute_r9_corridors_species(
        "chevreuil", fake_r16c_inputs["subset"],
        fake_r16c_inputs["habitat"], fake_r16c_inputs["couvert"],
        fake_r16c_inputs["fragmentation"], fake_r16c_inputs["exclusions"],
        conn, output_root=out)
    corr_tif = Path(r_corr["output_raster"])

    r = r16c.compute_r9_zones_passage_species(
        species="chevreuil",
        subset_path=fake_r16c_inputs["subset"],
        zones_vitales_tif=fake_r16c_inputs["zv_chevreuil"],
        corridors_tif=corr_tif,
        exclusions_tif=fake_r16c_inputs["exclusions"],
        connectivity_dict=conn,
        output_root=out,
    )
    assert r["manifest_id"] == \
        "R9_ZONES_PASSAGE_CHEVREUIL_COMPUTED_Ω"
    # zones_vitales 85 partout → tous les polygones sont au-dessus du seuil 70
    assert r["n_high_passage_polygons"] >= 1
    assert r["mean_score"] > 0


# ═════════════════════════════════════════════════════════════════════════
# 4. compute_r9_hotspots_species
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("species",
    ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"])
def test_hotspots_species_executes(
        r16c, loader, fake_r16c_inputs, tmp_path, species):
    conn = loader.load_dictionary("connectivity_rules")
    out = tmp_path / f"hotspots_{species}"
    r = r16c.compute_r9_hotspots_species(
        species=species,
        subset_path=fake_r16c_inputs["subset"],
        habitat_tif=fake_r16c_inputs["habitat"],
        productivity_tif=fake_r16c_inputs["productivity"],
        structure_tif=fake_r16c_inputs["structure"],
        continuity_tif=fake_r16c_inputs["continuity"],
        couvert_securite_tif=fake_r16c_inputs["couvert"],
        exclusions_tif=fake_r16c_inputs["exclusions"],
        connectivity_dict=conn,
        output_root=out,
    )
    assert r["manifest_id"] == \
        f"R9_HOTSPOTS_{species.upper()}_COMPUTED_Ω"
    # Au moins 1 hotspot devrait être trouvé (top 5%)
    assert r["n_hotspots"] >= 1
    assert r["top_percentile"] == 95


def test_hotspots_with_full_exclusion_returns_zero(
        r16c, loader, fake_r16c_inputs, tmp_path):
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

    conn = loader.load_dictionary("connectivity_rules")
    out = tmp_path / "hot_excluded"
    r = r16c.compute_r9_hotspots_species(
        species="chevreuil",
        subset_path=fake_r16c_inputs["subset"],
        habitat_tif=fake_r16c_inputs["habitat"],
        productivity_tif=fake_r16c_inputs["productivity"],
        structure_tif=fake_r16c_inputs["structure"],
        continuity_tif=fake_r16c_inputs["continuity"],
        couvert_securite_tif=fake_r16c_inputs["couvert"],
        exclusions_tif=excl_full,
        connectivity_dict=conn,
        output_root=out,
    )
    assert r["n_hotspots"] == 0


# ═════════════════════════════════════════════════════════════════════════
# 5. compute_r9_corridors_multi_especes
# ═════════════════════════════════════════════════════════════════════════
def test_link_multi_especes_fusion(
        r16c, loader, fake_r16c_inputs, tmp_path):
    """Génère 5 cost-links espèces puis fusion."""
    conn = loader.load_dictionary("connectivity_rules")
    out = tmp_path / "multi"
    out.mkdir()

    # Génère 5 corridors espèces
    corr_tifs = {}
    for sp in ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"]:
        r = r16c.compute_r9_corridors_species(
            sp, fake_r16c_inputs["subset"],
            fake_r16c_inputs["habitat"], fake_r16c_inputs["couvert"],
            fake_r16c_inputs["fragmentation"],
            fake_r16c_inputs["exclusions"],
            conn, output_root=out)
        corr_tifs[sp] = Path(r["output_raster"])

    r = r16c.compute_r9_corridors_multi_especes(
        subset_path=fake_r16c_inputs["subset"],
        corridors_per_species_tifs=corr_tifs,
        zones_humides_tif=fake_r16c_inputs["humides"],
        exclusions_tif=fake_r16c_inputs["exclusions"],
        connectivity_dict=conn,
        output_root=out,
    )
    assert r["manifest_id"] == "R9_CORRIDORS_MULTI_ESPECES_COMPUTED_Ω"
    assert len(r["species_fused"]) == 5
    # Vérifier que les poids normalisés somment à 1.0
    weights = r["species_weights_normalized"]
    assert sum(weights.values()) == pytest.approx(1.0, abs=0.01)
    # Score moyen > 0
    assert r["mean_score"] > 0
    assert "anti_generique_note" in r


def test_link_multi_partial_species(
        r16c, loader, fake_r16c_inputs, tmp_path):
    """Si on ne fournit que 2 espèces sur 5, la fusion fonctionne avec
    poids redistribués."""
    conn = loader.load_dictionary("connectivity_rules")
    out = tmp_path / "multi_partial"
    out.mkdir()
    corr_tifs = {}
    for sp in ["chevreuil", "orignal"]:
        r = r16c.compute_r9_corridors_species(
            sp, fake_r16c_inputs["subset"],
            fake_r16c_inputs["habitat"], fake_r16c_inputs["couvert"],
            fake_r16c_inputs["fragmentation"],
            fake_r16c_inputs["exclusions"],
            conn, output_root=out)
        corr_tifs[sp] = Path(r["output_raster"])

    r = r16c.compute_r9_corridors_multi_especes(
        subset_path=fake_r16c_inputs["subset"],
        corridors_per_species_tifs=corr_tifs,
        zones_humides_tif=fake_r16c_inputs["humides"],
        exclusions_tif=fake_r16c_inputs["exclusions"],
        connectivity_dict=conn,
        output_root=out,
    )
    assert len(r["species_fused"]) == 2
    weights = r["species_weights_normalized"]
    assert sum(weights.values()) == pytest.approx(1.0, abs=0.01)


# ═════════════════════════════════════════════════════════════════════════
# 6. Pipeline orchestrator
# ═════════════════════════════════════════════════════════════════════════
def test_pipeline_executes_subset_species(
        r16c, fake_r16c_inputs, tmp_path, monkeypatch):
    """Pipeline 1 espèce → 3 cibles + 1 multi = 4 succedeed."""
    import shutil
    state_p = tmp_path / "R9_STATE.json"
    out_root = tmp_path / "r16c_derivs"
    p1_root = tmp_path / "p1_derivs"
    out_root.mkdir(); p1_root.mkdir()

    monkeypatch.setattr(r16c, "R9_RECALC_STATE_PATH", state_p)
    monkeypatch.setattr(r16c, "DERIVATIVES_R9_ROOT", out_root)
    monkeypatch.setattr(r16c, "DERIVATIVES_P1_ROOT", p1_root)

    # Copie des dépendances dans les bons dossiers
    shutil.copy(fake_r16c_inputs["habitat"],
                p1_root / "MFFP_HABITAT_BRUT.tif")
    shutil.copy(fake_r16c_inputs["fragmentation"],
                p1_root / "MFFP_FRAGMENTATION_INDEX.tif")
    shutil.copy(fake_r16c_inputs["productivity"],
                p1_root / "MFFP_PRODUCTIVITE.tif")
    shutil.copy(fake_r16c_inputs["structure"],
                p1_root / "MFFP_STRUCTURE.tif")
    shutil.copy(fake_r16c_inputs["continuity"],
                p1_root / "MFFP_CONTINUITE.tif")
    shutil.copy(fake_r16c_inputs["couvert"],
                out_root / "R9_COUVERT_SECURITE.tif")
    shutil.copy(fake_r16c_inputs["humides"],
                out_root / "R9_ZONES_HUMIDES.tif")
    shutil.copy(fake_r16c_inputs["exclusions"],
                out_root / "R9_EXCLUSIONS.tif")
    shutil.copy(fake_r16c_inputs["zv_chevreuil"],
                out_root / "R9_ZONES_VITALES_CHEVREUIL.tif")

    monkeypatch.setattr(
        r16c, "auto_pick_subset",
        lambda: fake_r16c_inputs["subset"])

    res = r16c.execute_r16c_pipeline(
        species_subset=["chevreuil"])
    assert res["manifest_id"] == "R9_PHASE3_R16C_PIPELINE_COMPLETED_Ω"
    # 3 cibles chevreuil + 1 multi
    assert "R9_CORRIDORS_CHEVREUIL" in res["targets_succeeded"]
    assert "R9_HOTSPOTS_CHEVREUIL" in res["targets_succeeded"]
    assert "R9_CORRIDORS_MULTI_ESPECES" in res["targets_succeeded"]
    assert state_p.exists()
    state = json.loads(state_p.read_text(encoding="utf-8"))
    assert state["targets"]["R9_CORRIDORS_CHEVREUIL"]["status"] == \
        "OK_REAL"
    assert state["targets"]["R9_CORRIDORS_CHEVREUIL"]["ordre"] == \
        "N°52-R16-C"


def test_pipeline_missing_dependencies_raises(
        r16c, fake_r16c_inputs, tmp_path, monkeypatch):
    """Si MFFP_HABITAT_BRUT absent → raise."""
    out_root = tmp_path / "no_deps_r16c"
    p1_root = tmp_path / "no_p1_r16c"
    out_root.mkdir(); p1_root.mkdir()
    monkeypatch.setattr(r16c, "DERIVATIVES_R9_ROOT", out_root)
    monkeypatch.setattr(r16c, "DERIVATIVES_P1_ROOT", p1_root)
    monkeypatch.setattr(
        r16c, "auto_pick_subset",
        lambda: fake_r16c_inputs["subset"])
    with pytest.raises(RuntimeError, match="Dépendances"):
        r16c.execute_r16c_pipeline(species_subset=["chevreuil"])
