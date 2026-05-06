"""
mffp_phase3_p0_omega.py — ORDRE N°52-R13 · IMPLÉMENTATION P0 RÉELLE
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Implémentation effective des 4 couches P0 PHASE_3 R8 autorisées par R13 :
  1. compute_mffp_density          (LOW · 4h)
  2. compute_mffp_age              (LOW · 4h)
  3. compute_mffp_structure        (MEDIUM · 12h)
  4. compute_mffp_fragmentation    (HIGH · 24h)

Doctrine :
  · Lit le subset 100 Mo (ou pee_maj.gpkg complet) via pyogrio.
  · Reprojete EPSG:32198 (NAD83 Québec) si nécessaire.
  · Applique les dictionnaires VALIDÉS (R12 → status='VALIDÉ' R13).
  · Persiste GeoTIFF/GeoPackage sur /app/backend/data/gis_archive/derivatives/.
  · Calcule SHA-256 du output pour reproductibilité institutionnelle.
  · ANTI_GÉNÉRIQUE_STRICT : aucune simulation, exécution réelle uniquement.

Modules requis (déjà présents sur pod) :
  · pyogrio 0.12.1, geopandas 1.1.3, rasterio 1.4.4
  · shapely 2.1.2, pyproj 3.7.2, scipy 1.17.0, numpy 2.4.0
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("mffp_phase3_p0_omega")

# ═════════════════════════════════════════════════════════════════════════
# Constantes
# ═════════════════════════════════════════════════════════════════════════
DERIVATIVES_OUTPUT_ROOT = Path("/app/backend/data/gis_archive/derivatives")
DERIVATIVES_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

TARGET_EPSG = 32198
NODATA_VALUE_UINT8 = 0
NODATA_VALUE_FLOAT32 = -9999.0


# ═════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            blk = fh.read(8 << 20)
            if not blk:
                break
            h.update(blk)
    return h.hexdigest()


def _load_gdf(input_path: str, layer: Optional[str] = None,
               bbox: Optional[Tuple[float, ...]] = None):
    """Charge un GeoDataFrame avec pyogrio (streaming arrow).

    Sélection canonique du layer :
      1. layer explicite (param)
      2. 'pee_maj' (MFFP 2025)
      3. 'peuplement_ecoforestier' (legacy)
      4. Premier (Multi)Polygon disponible
      5. Premier layer (fallback)
    """
    import pyogrio  # noqa: PLC0415
    layers = pyogrio.list_layers(input_path)
    if hasattr(layers, "shape"):
        layer_names = list(layers[:, 0])
        layer_geoms = list(layers[:, 1])
    else:
        layer_names = [L[0] for L in layers]
        layer_geoms = [L[1] if len(L) > 1 else None for L in layers]
    if not layer_names:
        raise RuntimeError(f"NO_LAYERS_IN_GPKG :: {input_path}")
    if layer:
        layer_name = layer
    else:
        layer_name = None
        for canonical in ("pee_maj", "peuplement_ecoforestier"):
            if canonical in layer_names:
                layer_name = canonical
                break
        if layer_name is None:
            for n, g in zip(layer_names, layer_geoms):
                if g and "Polygon" in str(g):
                    layer_name = n
                    break
        if layer_name is None:
            layer_name = layer_names[0]
    df = pyogrio.read_dataframe(
        input_path, layer=layer_name, bbox=bbox, use_arrow=True)
    return df, layer_name


def _ensure_epsg_32198(gdf):
    """Reprojette le GeoDataFrame vers EPSG:32198 si nécessaire."""
    if gdf.crs is None:
        # Présume EPSG:32198 si CRS absent (cas par défaut MFFP)
        gdf.set_crs(epsg=TARGET_EPSG, inplace=True)
        return gdf
    try:
        current_epsg = gdf.crs.to_epsg()
    except Exception:
        current_epsg = None
    if current_epsg != TARGET_EPSG:
        logger.info("REPROJECT_TO_EPSG_32198 from=%s", current_epsg)
        gdf = gdf.to_crs(epsg=TARGET_EPSG)
    return gdf


def _rasterize_to_tif(gdf, value_column: str, output_path: Path,
                       resolution_m: int, dtype: str,
                       nodata: float, all_touched: bool = True
                       ) -> Dict[str, Any]:
    """Rasterise un GDF vers un GeoTIFF EPSG:32198."""
    import numpy as np
    import rasterio
    from rasterio import features
    from rasterio.transform import from_bounds

    minx, miny, maxx, maxy = gdf.total_bounds
    # Snap aux multiples de resolution_m pour éviter offsets
    minx = (minx // resolution_m) * resolution_m
    miny = (miny // resolution_m) * resolution_m
    maxx = ((maxx // resolution_m) + 1) * resolution_m
    maxy = ((maxy // resolution_m) + 1) * resolution_m
    width = int((maxx - minx) / resolution_m)
    height = int((maxy - miny) / resolution_m)
    transform = from_bounds(minx, miny, maxx, maxy, width, height)

    # Construire (geom, value) shapes
    shapes = (
        (geom, value)
        for geom, value in zip(gdf.geometry, gdf[value_column])
        if geom is not None and value is not None
    )

    np_dtype = getattr(np, dtype)
    raster = features.rasterize(
        shapes=shapes,
        out_shape=(height, width),
        transform=transform,
        fill=nodata,
        all_touched=all_touched,
        dtype=np_dtype,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        str(output_path), "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=dtype,
        crs=f"EPSG:{TARGET_EPSG}",
        transform=transform,
        nodata=nodata,
        compress="lzw",
        tiled=True,
    ) as dst:
        dst.write(raster, 1)

    return {
        "width": width,
        "height": height,
        "resolution_m": resolution_m,
        "bounds": [float(minx), float(miny),
                    float(maxx), float(maxy)],
        "n_pixels": int(width * height),
        "n_pixels_burned": int((raster != nodata).sum()),
    }


# ═════════════════════════════════════════════════════════════════════════
# 1. MFFP_DENSITY (LOW · 4h)
# ═════════════════════════════════════════════════════════════════════════
def compute_mffp_density(
    pee_maj_gpkg_path: str,
    cl_dens_to_pct_dict: Dict[str, Any],
    output_tif_path: Optional[str] = None,
    feuillus_correction: float = 1.0,
    resineux_correction: float = 1.05,
    mixte_correction: float = 1.025,
) -> Dict[str, Any]:
    """ORDRE N°52-R13 · MFFP_DENSITY (couvert canopée 0-100, raster 100m).

    Args:
      pee_maj_gpkg_path : Chemin local pee_maj.gpkg ou subset.
      cl_dens_to_pct_dict : Dict R12 validé (cl_dens_to_pct.json) avec
        clé 'mapping' → {A:{pct_canopy_midpoint:90, ...}, ...}.
      output_tif_path : Si None, auto sous DERIVATIVES_OUTPUT_ROOT.

    Returns:
      dict {output_path, sha256, mean_pct, n_polygons, distribution, elapsed_s}.
    """
    t0 = time.time()
    logger.info("MFFP_DENSITY_START path=%s", pee_maj_gpkg_path)

    out_path = Path(
        output_tif_path or
        (DERIVATIVES_OUTPUT_ROOT / "MFFP_COUVERT_FORESTIER_DENSITY.tif"))

    gdf, layer = _load_gdf(pee_maj_gpkg_path)
    gdf = _ensure_epsg_32198(gdf)

    # Mapping CL_DENS → pct (extraction depuis dict R12 validé)
    cl_dens_pct: Dict[str, int] = {
        code: int(spec["pct_canopy_midpoint"])
        for code, spec in cl_dens_to_pct_dict.get("mapping", {}).items()
    }
    if not cl_dens_pct:
        raise ValueError("cl_dens_to_pct_dict.mapping est vide ou invalide")

    cols_lower = {c.lower(): c for c in gdf.columns}
    cl_dens_col = cols_lower.get("cl_dens")
    gr_ess_col = cols_lower.get("gr_ess")
    if cl_dens_col is None:
        raise ValueError(f"Colonne CL_DENS absente. Colonnes: {list(gdf.columns)}")

    gdf = gdf.dropna(subset=[cl_dens_col]).copy()
    gdf["_pct_canopy"] = gdf[cl_dens_col].astype(str).str.strip().map(
        cl_dens_pct).fillna(0).astype("uint8")

    # Correction GR_ESS (résineux +5%, mixte +2.5%)
    if gr_ess_col is not None:
        def _apply_corr(row):
            ge = str(row[gr_ess_col]).strip().upper()
            base = int(row["_pct_canopy"])
            if ge == "R":
                return min(int(base * resineux_correction), 100)
            if ge == "M":
                return min(int(base * mixte_correction), 100)
            return min(int(base * feuillus_correction), 100)
        gdf["_pct_canopy"] = gdf.apply(_apply_corr, axis=1).astype("uint8")

    rast_info = _rasterize_to_tif(
        gdf, "_pct_canopy", out_path,
        resolution_m=100, dtype="uint8", nodata=NODATA_VALUE_UINT8)

    sha256 = _sha256_file(out_path)
    distribution = dict(Counter(gdf[cl_dens_col].astype(str)))
    mean_pct = float(gdf["_pct_canopy"].mean())

    elapsed = round(time.time() - t0, 2)
    logger.info(
        "MFFP_DENSITY_DONE elapsed=%ss n_poly=%d mean_pct=%.2f sha=%s",
        elapsed, len(gdf), mean_pct, sha256[:16])
    return {
        "manifest_id": "MFFP_DENSITY_COMPUTED_Ω",
        "ordre": "N°52-R13",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_path": str(out_path),
        "output_size_bytes": out_path.stat().st_size,
        "sha256": sha256,
        "n_polygons_processed": len(gdf),
        "mean_pct_canopy": round(mean_pct, 2),
        "cl_dens_distribution": distribution,
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 2. MFFP_AGE (LOW · 4h)
# ═════════════════════════════════════════════════════════════════════════
def compute_mffp_age(
    pee_maj_gpkg_path: str,
    classes_age_dict: Dict[str, Any],
    output_tif_path: Optional[str] = None,
    current_year: int = 2026,
) -> Dict[str, Any]:
    """ORDRE N°52-R13 · MFFP_AGE (raster classes 1-8, 250m)."""
    t0 = time.time()
    logger.info("MFFP_AGE_START path=%s", pee_maj_gpkg_path)
    out_path = Path(
        output_tif_path or
        (DERIVATIVES_OUTPUT_ROOT / "MFFP_CLASSES_AGE.tif"))

    gdf, layer = _load_gdf(pee_maj_gpkg_path)
    gdf = _ensure_epsg_32198(gdf)

    # Mappings depuis le dict R12 validé
    regular = classes_age_dict.get("regular_age_classes", {})
    inequienne = classes_age_dict.get("inequienne_age_classes", {})
    cl_age_to_class: Dict[str, int] = {}
    for code, spec in regular.items():
        cl_age_to_class[str(code)] = int(spec["raster_class_id"])
    for code, spec in inequienne.items():
        cl_age_to_class[str(code).upper()] = int(spec["raster_class_id"])

    fallback = classes_age_dict.get("fallback_age_from_an_origine", {})
    use_fallback = bool(fallback.get("use_when_cl_age_missing", True))
    fallback_year_bounds = [
        (str(c), int(spec["year_bounds"][0]), int(spec["year_bounds"][1]),
         int(spec["raster_class_id"]))
        for c, spec in regular.items()
    ]

    cols_lower = {c.lower(): c for c in gdf.columns}
    cl_age_col = cols_lower.get("cl_age")
    an_origine_col = cols_lower.get("an_origine")

    def _resolve_class(row) -> int:
        if cl_age_col and row[cl_age_col] is not None:
            code = str(row[cl_age_col]).strip().upper()
            if code in cl_age_to_class:
                return cl_age_to_class[code]
        if use_fallback and an_origine_col and row[an_origine_col]:
            try:
                age_years = current_year - int(row[an_origine_col])
                for _code, lo, hi, raster_id in fallback_year_bounds:
                    if lo <= age_years < hi:
                        return raster_id
            except (TypeError, ValueError):
                pass
        return 0  # NoData

    gdf["_age_class"] = gdf.apply(_resolve_class, axis=1).astype("uint8")
    gdf = gdf[gdf["_age_class"] > 0]

    rast_info = _rasterize_to_tif(
        gdf, "_age_class", out_path,
        resolution_m=250, dtype="uint8", nodata=NODATA_VALUE_UINT8)
    sha256 = _sha256_file(out_path)
    distribution = dict(Counter(gdf["_age_class"].astype(int)))
    elapsed = round(time.time() - t0, 2)
    logger.info("MFFP_AGE_DONE elapsed=%ss n=%d sha=%s",
                elapsed, len(gdf), sha256[:16])
    return {
        "manifest_id": "MFFP_AGE_COMPUTED_Ω",
        "ordre": "N°52-R13",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_path": str(out_path),
        "output_size_bytes": out_path.stat().st_size,
        "sha256": sha256,
        "n_polygons_processed": len(gdf),
        "age_class_distribution": {str(k): int(v)
                                     for k, v in distribution.items()},
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 3. MFFP_STRUCTURE (MEDIUM · 12h)
# ═════════════════════════════════════════════════════════════════════════
def compute_mffp_structure(
    pee_maj_gpkg_path: str,
    structure_rules_dict: Dict[str, Any],
    output_tif_path: Optional[str] = None,
) -> Dict[str, Any]:
    """ORDRE N°52-R13 · MFFP_STRUCTURE (raster catégoriel 1-7, 100m).

    Applique l'arbre de décision défini dans
    structure_classification_rules.json (R12 validé) :
      step_1 : si CL_AGE inéquienne (JIN/JIR/VIN/VIR) → 5 ou 6
      step_2 : si CL_AGE='10' AND CL_DENS in (D,E) → 7 (RECRUE_OUVERT)
      step_3 : combinaisons CL_HAUT × CL_DENS → 1/2/3/4
      fallback : 1 (REGULIERE_MONOSTRATE)
    """
    t0 = time.time()
    logger.info("MFFP_STRUCTURE_START path=%s", pee_maj_gpkg_path)
    out_path = Path(
        output_tif_path or
        (DERIVATIVES_OUTPUT_ROOT / "MFFP_STRUCTURE.tif"))

    gdf, layer = _load_gdf(pee_maj_gpkg_path)
    gdf = _ensure_epsg_32198(gdf)

    cols_lower = {c.lower(): c for c in gdf.columns}
    cl_age_col = cols_lower.get("cl_age")
    cl_haut_col = cols_lower.get("cl_haut")
    cl_dens_col = cols_lower.get("cl_dens")
    if not cl_age_col or not cl_dens_col:
        raise ValueError(
            f"Colonnes CL_AGE/CL_DENS absentes : {list(gdf.columns)}")

    decision_tree = structure_rules_dict["decision_tree"]
    step_1 = decision_tree["step_1_check_inequienne"]["true_branch"]
    fallback = decision_tree["step_3_check_haut_dens"]["fallback_rule"]
    fallback_id = int(fallback["result"]["raster_class_id"])

    def _classify(row) -> int:
        cl_age = str(row[cl_age_col]).strip().upper() if row[cl_age_col] else ""
        cl_dens = str(row[cl_dens_col]).strip().upper() if row[cl_dens_col] else ""
        cl_haut = None
        if cl_haut_col and row[cl_haut_col] is not None:
            try:
                cl_haut = int(row[cl_haut_col])
            except (TypeError, ValueError):
                cl_haut = None

        # Step 1 : inéquienne
        if cl_age in step_1:
            return int(step_1[cl_age]["raster_class_id"])
        # Step 2 : recrue_ouvert
        if cl_age == "10" and cl_dens in ("D", "E"):
            return 7
        # Step 3 : combinaisons CL_HAUT × CL_DENS
        if cl_haut in (1, 2) and cl_dens == "A":
            return 2  # REGULIERE_BISTRATE
        if cl_haut in (1, 2) and cl_dens in ("B", "C"):
            return 3  # IRREGULIERE_ETAGEE
        if cl_haut in (3, 4) and cl_dens in ("A", "B"):
            return 1  # REGULIERE_MONOSTRATE
        if cl_haut == 5:
            return 1
        if cl_dens in ("D", "E") and cl_haut in (3, 4, 5):
            return 4  # IRREGULIERE_JARDINEE
        return fallback_id

    gdf["_struct"] = gdf.apply(_classify, axis=1).astype("uint8")
    gdf = gdf[gdf["_struct"] > 0]

    rast_info = _rasterize_to_tif(
        gdf, "_struct", out_path,
        resolution_m=100, dtype="uint8", nodata=NODATA_VALUE_UINT8)
    sha256 = _sha256_file(out_path)
    distribution = dict(Counter(gdf["_struct"].astype(int)))
    elapsed = round(time.time() - t0, 2)
    logger.info("MFFP_STRUCTURE_DONE elapsed=%ss n=%d sha=%s",
                elapsed, len(gdf), sha256[:16])
    return {
        "manifest_id": "MFFP_STRUCTURE_COMPUTED_Ω",
        "ordre": "N°52-R13",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_path": str(out_path),
        "output_size_bytes": out_path.stat().st_size,
        "sha256": sha256,
        "n_polygons_processed": len(gdf),
        "structure_distribution": {str(k): int(v)
                                      for k, v in distribution.items()},
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 4. MFFP_FRAGMENTATION (HIGH · 24h) — Dickson 2017
# ═════════════════════════════════════════════════════════════════════════
def compute_forest_binary_raster(
    pee_maj_gpkg_path: str,
    ty_couv_to_forest_binary_dict: Dict[str, Any],
    output_tif_path: Optional[str] = None,
    resolution_m: int = 50,
) -> Dict[str, Any]:
    """Helper : rasterise TY_COUV → forêt binaire (0/1) à 50m.

    Prérequis pour MFFP_FRAGMENTATION (Dickson 2017).
    """
    t0 = time.time()
    out_path = Path(
        output_tif_path or
        (DERIVATIVES_OUTPUT_ROOT / "GIS_COUVERT_FORESTIER_BINARY_50M.tif"))

    gdf, layer = _load_gdf(pee_maj_gpkg_path)
    gdf = _ensure_epsg_32198(gdf)

    forest_codes = ty_couv_to_forest_binary_dict.get("forest_codes", {})
    non_forest_codes = ty_couv_to_forest_binary_dict.get(
        "non_forest_codes", {})
    ambiguous = ty_couv_to_forest_binary_dict.get(
        "ambiguous_codes_default_decision", {})
    fallback_unknown = int(ty_couv_to_forest_binary_dict.get(
        "fallback_unknown_code", {}).get("binary", 0))

    code_to_binary: Dict[str, int] = {}
    for code, spec in forest_codes.items():
        code_to_binary[code.upper()] = int(spec["binary"])
    for code, spec in non_forest_codes.items():
        code_to_binary[code.upper()] = int(spec["binary"])
    for code, spec in ambiguous.items():
        code_to_binary[code.upper()] = int(spec["binary"])

    cols_lower = {c.lower(): c for c in gdf.columns}
    # Canonical MFFP 2025 = 'type_couv', legacy = 'ty_couv'
    ty_couv_col = cols_lower.get("type_couv") or cols_lower.get("ty_couv")
    if ty_couv_col is None:
        raise ValueError(
            f"Colonne type_couv/ty_couv absente. "
            f"Colonnes disponibles : {list(gdf.columns)[:15]}")
    gdf["_forest"] = gdf[ty_couv_col].astype(str).str.strip().str.upper().map(
        code_to_binary).fillna(fallback_unknown).astype("uint8")
    rast_info = _rasterize_to_tif(
        gdf, "_forest", out_path,
        resolution_m=resolution_m, dtype="uint8", nodata=255)
    sha256 = _sha256_file(out_path)
    elapsed = round(time.time() - t0, 2)
    logger.info("FOREST_BINARY_DONE elapsed=%ss sha=%s",
                elapsed, sha256[:16])
    return {
        "manifest_id": "GIS_COUVERT_FORESTIER_BINARY_COMPUTED_Ω",
        "output_path": str(out_path),
        "sha256": sha256,
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "src_layer": layer,
    }


def compute_mffp_fragmentation(
    forest_binary_tif_path: str,
    output_tif_path: Optional[str] = None,
    base_resolution_m: int = 50,
    aggregation_resolution_m: int = 250,
) -> Dict[str, Any]:
    """ORDRE N°52-R13 · MFFP_FRAGMENTATION (Dickson 2017, raster float32 250m).

    Algorithme :
      1. Lit le raster forêt binaire 50m.
      2. Pf = uniform_filter (window 5x5) sur binaire = proportion forêt.
      3. Pff = convolution voisinage 4-connectivité (forêt-forêt adjacent).
      4. FRAG_INDEX = Pff / max(Pf, eps)
      5. Resample mean à 250m (aggregation_factor = 5).
      6. Persiste GeoTIFF float32.
    """
    import numpy as np
    import rasterio
    from rasterio.enums import Resampling
    from scipy import ndimage

    t0 = time.time()
    out_path = Path(
        output_tif_path or
        (DERIVATIVES_OUTPUT_ROOT / "MFFP_FRAGMENTATION_INDEX.tif"))

    with rasterio.open(forest_binary_tif_path) as src:
        binary = src.read(1)
        nodata_val = src.nodata if src.nodata is not None else 255
        # Convertir en float32 0/1 (NaN pour nodata)
        forest_f = np.where(binary == nodata_val, np.nan,
                              binary.astype("float32"))

    # 1. Pf = proportion forêt dans window 5×5 (50m base → 250m fenêtre)
    nan_mask = np.isnan(forest_f)
    forest_zeros = np.where(nan_mask, 0.0, forest_f)
    weights = np.ones((5, 5), dtype="float32") / 25.0
    pf = ndimage.convolve(
        forest_zeros, weights, mode="constant", cval=0.0)

    # 2. Pff = adjacences forêt-forêt (4-connectivité)
    # Pour chaque cellule forêt, compter les voisins forêt / max possible
    kernel_4 = np.array([[0, 1, 0],
                          [1, 0, 1],
                          [0, 1, 0]], dtype="float32")
    n_forest_neighbors = ndimage.convolve(
        forest_zeros, kernel_4, mode="constant", cval=0.0)
    # Pff brute : moyenne (n_forest_neighbors / 4) sur fenêtre 5x5
    pff_per_cell = n_forest_neighbors / 4.0
    pff = ndimage.convolve(
        pff_per_cell, weights, mode="constant", cval=0.0)

    # 3. FRAG_INDEX = Pff / max(Pf, eps) (Dickson 2017)
    eps = 1e-6
    frag_index = np.where(
        pf > eps, pff / pf, NODATA_VALUE_FLOAT32).astype("float32")
    # Re-masquer les zones initialement NoData
    frag_index = np.where(nan_mask, NODATA_VALUE_FLOAT32, frag_index)

    # 4. Aggregate à 250m (factor=5 si base=50m)
    factor = aggregation_resolution_m // base_resolution_m
    if factor < 1:
        raise ValueError("aggregation_resolution_m < base_resolution_m")
    if factor > 1:
        # Mean aggregation (en ignorant NoData)
        h, w = frag_index.shape
        new_h = h // factor
        new_w = w // factor
        truncated = frag_index[:new_h * factor, :new_w * factor]
        reshaped = truncated.reshape(new_h, factor, new_w, factor)
        # Masquer NoData pour le calcul de moyenne
        valid_mask = (reshaped != NODATA_VALUE_FLOAT32)
        sums = np.where(valid_mask, reshaped, 0.0).sum(axis=(1, 3))
        counts = valid_mask.sum(axis=(1, 3))
        agg = np.where(counts > 0, sums / counts,
                        NODATA_VALUE_FLOAT32).astype("float32")
    else:
        agg = frag_index
        new_h, new_w = h, w

    # 5. Persistance
    with rasterio.open(forest_binary_tif_path) as src:
        src_transform = src.transform
        src_crs = src.crs
    new_transform = rasterio.transform.Affine(
        src_transform.a * factor, src_transform.b, src_transform.c,
        src_transform.d, src_transform.e * factor, src_transform.f)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        str(out_path), "w",
        driver="GTiff",
        height=agg.shape[0],
        width=agg.shape[1],
        count=1,
        dtype="float32",
        crs=src_crs,
        transform=new_transform,
        nodata=NODATA_VALUE_FLOAT32,
        compress="lzw",
        tiled=True,
    ) as dst:
        dst.write(agg, 1)
    sha256 = _sha256_file(out_path)

    valid_pixels = agg[agg != NODATA_VALUE_FLOAT32]
    mean_frag = float(valid_pixels.mean()) if valid_pixels.size > 0 else 0.0
    n_valid = int(valid_pixels.size)
    n_total = int(agg.size)
    elapsed = round(time.time() - t0, 2)
    logger.info(
        "MFFP_FRAGMENTATION_DONE elapsed=%ss valid=%d/%d mean=%.3f sha=%s",
        elapsed, n_valid, n_total, mean_frag, sha256[:16])
    return {
        "manifest_id": "MFFP_FRAGMENTATION_COMPUTED_Ω",
        "ordre": "N°52-R13",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "algorithm": "Dickson_Roemer_Boyce_2017",
        "output_path": str(out_path),
        "output_size_bytes": out_path.stat().st_size,
        "sha256": sha256,
        "base_resolution_m": base_resolution_m,
        "aggregation_resolution_m": aggregation_resolution_m,
        "n_pixels_total": n_total,
        "n_pixels_valid": n_valid,
        "mean_frag_index": round(mean_frag, 4),
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


__all__ = [
    "compute_mffp_density",
    "compute_mffp_age",
    "compute_mffp_structure",
    "compute_forest_binary_raster",
    "compute_mffp_fragmentation",
    "DERIVATIVES_OUTPUT_ROOT",
    "TARGET_EPSG",
]
