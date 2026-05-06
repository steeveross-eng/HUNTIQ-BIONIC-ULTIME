"""
mffp_phase3_p1_omega.py — ORDRE N°52-R15 · IMPLÉMENTATION P1+P2 RÉELLE
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Implémentation effective des 4 couches restantes PHASE_3 R8 (R15) qui
débloquent R9 hors mode STUB :

  5. compute_mffp_productivity     (P1 · MEDIUM · 16h)
  6. compute_mffp_habitat          (P1 · HIGH · 24h · 5 bandes)
  7. compute_mffp_connectivity     (P2 · HIGH · 32h · GeoPackage)
  8. compute_mffp_continuity       (P2 · MEDIUM · 12h)

Doctrine :
  · Lit le subset 100 Mo (ou pee_maj.gpkg complet) via pyogrio.
  · Reprojete EPSG:32198 (NAD83 Québec) si nécessaire.
  · Applique les dictionnaires VALIDÉS (R15 → status='VALIDÉ').
  · Persiste GeoTIFF/GeoPackage sur /app/backend/data/gis_archive/derivatives/.
  · Calcule SHA-256 du output pour reproductibilité institutionnelle.
  · ANTI_GÉNÉRIQUE_STRICT : aucune simulation, exécution réelle uniquement.

Réutilise les helpers de mffp_phase3_p0_omega.py (FUSION ADD-ONLY).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("mffp_phase3_p1_omega")

# Réutilisation FUSION ADD-ONLY des helpers P0
from engines.v8_institutional.especes.mffp_phase3_p0_omega import (
    DERIVATIVES_OUTPUT_ROOT,
    TARGET_EPSG,
    NODATA_VALUE_UINT8,
    NODATA_VALUE_FLOAT32,
    _utc_now,
    _sha256_file,
    _load_gdf,
    _ensure_epsg_32198,
    _rasterize_to_tif,
)


# ═════════════════════════════════════════════════════════════════════════
# 5. MFFP_PRODUCTIVITY (P1 · MEDIUM · 16h)
# ═════════════════════════════════════════════════════════════════════════
def compute_mffp_productivity(
    pee_maj_gpkg_path: str,
    tables_rendement_dict: Dict[str, Any],
    output_tif_path: Optional[str] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R15 · MFFP_PRODUCTIVITY (m³/ha float32, raster 100 m).

    Algorithme : lookup `tables_rendement_mffp[gr_ess][cl_age]` puis
    correction par `cl_dens` (A→1.10, B→1.00, C→0.85, D→0.65, E→0.45).

    Args :
      tables_rendement_dict : Dict R15 validé (tables_rendement_mffp.json).
      output_tif_path : Si None, MFFP_PRODUCTIVITE.tif sous derivatives/.
      resolution_m : Résolution raster (défaut 100 m).

    Returns dict {output_path, sha256, n_polygons_processed, mean_m3_per_ha,
                  gr_ess_distribution, cl_age_distribution, elapsed_s}.
    """
    import numpy as np

    t0 = time.time()
    logger.info("MFFP_PRODUCTIVITY_START path=%s", pee_maj_gpkg_path)

    out_path = Path(
        output_tif_path
        or (DERIVATIVES_OUTPUT_ROOT / "MFFP_PRODUCTIVITE.tif"))

    gdf, layer = _load_gdf(pee_maj_gpkg_path)
    gdf = _ensure_epsg_32198(gdf)

    mapping = tables_rendement_dict.get("mapping", {})
    if not mapping:
        raise ValueError(
            "tables_rendement_dict.mapping est vide ou invalide")
    density_corr = tables_rendement_dict.get(
        "correction_factors_density", {})
    fallback_unknown_essence = float(
        tables_rendement_dict.get("fallback_unknown_essence", 0))

    # Build (gr_ess, cl_age) → m3/ha lookup table
    prod_lookup: Dict[Tuple[str, str], float] = {}
    for gr_code, gr_spec in mapping.items():
        for age_code, m3 in gr_spec.get(
                "production_m3_per_ha", {}).items():
            prod_lookup[(gr_code.upper(), str(age_code).upper())] = float(m3)

    cols_lower = {c.lower(): c for c in gdf.columns}
    # MFFP 2025 : `gr_ess` contient des codes d'essences détaillés (323
    # codes : EN, SBEB, ESFT, RZ, EV...). Pour le lookup table de
    # rendement Pothier-Savard, on utilise `type_couv` (R/F/M haut niveau)
    # qui correspond aux groupes de tables. Fallback `gr_ess`.
    gr_col = cols_lower.get("type_couv") or cols_lower.get("gr_ess")
    age_col = cols_lower.get("cl_age")
    dens_col = cols_lower.get("cl_dens")
    if gr_col is None or age_col is None:
        raise ValueError(
            f"Colonnes type_couv|gr_ess/cl_age absentes : "
            f"{list(gdf.columns)[:15]}")

    gdf = gdf.dropna(subset=[gr_col, age_col]).copy()

    def _prod(row) -> float:
        ge = str(row[gr_col]).strip().upper()
        ag = str(row[age_col]).strip().upper()
        base = prod_lookup.get((ge, ag), fallback_unknown_essence)
        if dens_col is not None:
            cd = str(row.get(dens_col, "B")).strip().upper()
            corr_key_map = {
                "A": "A_tres_dense", "B": "B_dense", "C": "C_moyenne",
                "D": "D_clairsemee", "E": "E_tres_clairsemee",
            }
            corr_key = corr_key_map.get(cd, "B_dense")
            base = base * float(density_corr.get(corr_key, 1.0))
        return float(min(max(base, 0.0), 500.0))

    gdf["_productivity_m3"] = gdf.apply(_prod, axis=1).astype("float32")
    n_polygons = len(gdf)
    mean_prod = float(gdf["_productivity_m3"].mean())

    rast_info = _rasterize_to_tif(
        gdf, "_productivity_m3", out_path,
        resolution_m=resolution_m, dtype="float32",
        nodata=NODATA_VALUE_FLOAT32)
    sha256 = _sha256_file(out_path)
    elapsed = round(time.time() - t0, 2)

    gr_ess_dist = dict(Counter(
        gdf[gr_col].astype(str).str.strip().str.upper()).most_common(10))
    cl_age_dist = dict(Counter(
        gdf[age_col].astype(str).str.strip().str.upper()).most_common(15))

    logger.info(
        "MFFP_PRODUCTIVITY_DONE elapsed=%ss n_pol=%d mean_m3_ha=%.2f sha=%s",
        elapsed, n_polygons, mean_prod, sha256[:16])
    return {
        "manifest_id": "MFFP_PRODUCTIVITY_COMPUTED_Ω",
        "ordre": "N°52-R15",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_path": str(out_path),
        "output_size_bytes": out_path.stat().st_size,
        "sha256": sha256,
        "n_polygons_processed": n_polygons,
        "mean_m3_per_ha": round(mean_prod, 2),
        "gr_ess_distribution": gr_ess_dist,
        "cl_age_distribution": cl_age_dist,
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 6. MFFP_HABITAT (P1 · HIGH · 24h · 5 bandes)
# ═════════════════════════════════════════════════════════════════════════
SPECIES_BAND_ORDER = ["chevreuil", "orignal", "ours_noir",
                      "dindon", "wapiti"]


def _score_habitat_for_species(row_dict: Dict[str, Any],
                                  species_pref: Dict[str, Any],
                                  weights: Dict[str, float]) -> int:
    """Calcule le score habitat 0-100 pour UNE espèce sur UN polygone."""
    fallback = species_pref.get("fallback_unknown_value", 0)
    score = 0.0
    for field, weight in weights.items():
        val = str(row_dict.get(field, "")).strip().upper()
        score_map = species_pref.get(f"{field}_score", {})
        # Tolérance casse pour les clés
        s = score_map.get(val) or score_map.get(val.lower())
        if s is None:
            s = fallback
        score += float(weight) * float(s)
    return int(round(min(max(score, 0), 100)))


def compute_mffp_habitat(
    pee_maj_gpkg_path: str,
    habitat_pref_dict: Dict[str, Any],
    output_tif_path: Optional[str] = None,
    resolution_m: int = 250,
) -> Dict[str, Any]:
    """ORDRE N°52-R15 · MFFP_HABITAT (5 bandes uint8 0-100, raster 250 m).

    Pour chaque polygone et chaque espèce de gibier, calcule un score 0-100
    pondéré (gr_ess 30%, cl_age 30%, cl_dens 25%, type_couv 15%).

    Args :
      habitat_pref_dict : Dict R15 validé (habitat_preferences_par_espece).
      output_tif_path : Si None, MFFP_HABITAT_BRUT.tif sous derivatives/.

    Returns dict {output_path, sha256, n_polygons_processed,
                  bands_meta, mean_score_per_species, elapsed_s}.
    """
    import numpy as np
    import rasterio
    from rasterio import features
    from rasterio.transform import from_bounds

    t0 = time.time()
    logger.info("MFFP_HABITAT_START path=%s", pee_maj_gpkg_path)

    out_path = Path(
        output_tif_path
        or (DERIVATIVES_OUTPUT_ROOT / "MFFP_HABITAT_BRUT.tif"))

    gdf, layer = _load_gdf(pee_maj_gpkg_path)
    gdf = _ensure_epsg_32198(gdf)

    weights = habitat_pref_dict.get("weights_by_field", {})
    if not weights:
        raise ValueError("habitat_pref_dict.weights_by_field absent")
    preferences = habitat_pref_dict.get("preferences", {})
    if not preferences:
        raise ValueError("habitat_pref_dict.preferences absent")
    species_keys = [s for s in SPECIES_BAND_ORDER if s in preferences]
    if not species_keys:
        raise ValueError(
            f"Aucune espèce reconnue parmi {list(preferences.keys())}")

    cols_lower = {c.lower(): c for c in gdf.columns}
    needed = ["gr_ess", "cl_age", "cl_dens", "type_couv"]
    for f in needed:
        if cols_lower.get(f) is None:
            raise ValueError(
                f"Colonne {f} absente : {list(gdf.columns)[:15]}")

    # MFFP 2025 : gr_ess contient 323 codes d'essences détaillés (EN, SBEB,
    # ESFT...) qui ne matchent pas le dict {R,F,M}. On utilise type_couv
    # (R/F/M haut niveau) pour le lookup gr_ess_score du dict habitat.
    type_couv_col = cols_lower["type_couv"]

    # Calcul des scores par espèce
    mean_scores = {}
    for sp in species_keys:
        sp_pref = preferences[sp]
        scores = []
        for _, row in gdf.iterrows():
            row_dict = {
                # gr_ess du dict mappe sur type_couv R/F/M (et non gr_ess
                # détaillé qui ne fait pas partie du dictionnaire)
                "gr_ess": row[type_couv_col],
                "cl_age": row[cols_lower["cl_age"]],
                "cl_dens": row[cols_lower["cl_dens"]],
                "type_couv": row[type_couv_col],
            }
            s = _score_habitat_for_species(row_dict, sp_pref, weights)
            scores.append(s)
        gdf[f"_hab_{sp}"] = np.array(scores, dtype="uint8")
        mean_scores[sp] = round(float(np.mean(scores)), 2)
    n_polygons = len(gdf)

    # Rasterisation multi-bande sur la même grille
    minx, miny, maxx, maxy = gdf.total_bounds
    minx = (minx // resolution_m) * resolution_m
    miny = (miny // resolution_m) * resolution_m
    maxx = ((maxx // resolution_m) + 1) * resolution_m
    maxy = ((maxy // resolution_m) + 1) * resolution_m
    width = int((maxx - minx) / resolution_m)
    height = int((maxy - miny) / resolution_m)
    transform = from_bounds(minx, miny, maxx, maxy, width, height)

    bands = []
    for sp in species_keys:
        shapes = (
            (geom, value)
            for geom, value in zip(gdf.geometry, gdf[f"_hab_{sp}"])
            if geom is not None and value is not None
        )
        raster = features.rasterize(
            shapes=shapes,
            out_shape=(height, width),
            transform=transform,
            fill=NODATA_VALUE_UINT8,
            all_touched=True,
            dtype="uint8",
        )
        bands.append(raster)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        str(out_path), "w",
        driver="GTiff",
        height=height,
        width=width,
        count=len(bands),
        dtype="uint8",
        crs=f"EPSG:{TARGET_EPSG}",
        transform=transform,
        nodata=NODATA_VALUE_UINT8,
        compress="lzw",
        tiled=True,
    ) as dst:
        for i, raster in enumerate(bands, start=1):
            dst.write(raster, i)
            dst.set_band_description(i, species_keys[i - 1])

    sha256 = _sha256_file(out_path)
    elapsed = round(time.time() - t0, 2)
    logger.info(
        "MFFP_HABITAT_DONE elapsed=%ss n_pol=%d sha=%s",
        elapsed, n_polygons, sha256[:16])
    return {
        "manifest_id": "MFFP_HABITAT_COMPUTED_Ω",
        "ordre": "N°52-R15",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_path": str(out_path),
        "output_size_bytes": out_path.stat().st_size,
        "sha256": sha256,
        "n_polygons_processed": n_polygons,
        "bands_count": len(bands),
        "bands_meta": [
            {"index": i + 1, "species": sp,
             "scientific_name": preferences[sp].get("scientific_name")}
            for i, sp in enumerate(species_keys)
        ],
        "mean_score_per_species": mean_scores,
        "rasterization": {
            "width": width, "height": height,
            "resolution_m": resolution_m,
            "bounds": [float(minx), float(miny),
                       float(maxx), float(maxy)],
            "n_pixels": int(width * height),
            "n_bands": len(bands),
        },
        "weights_applied": weights,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 7. MFFP_CONNECTIVITY (P2 · HIGH · 32h · GeoPackage)
# ═════════════════════════════════════════════════════════════════════════
def compute_mffp_connectivity(
    pee_maj_gpkg_path: str,
    habitat_tif_path: Optional[str] = None,
    output_gpkg_path: Optional[str] = None,
    eps_meters: float = 500.0,
    min_samples: int = 5,
) -> Dict[str, Any]:
    """ORDRE N°52-R15 · MFFP_CONNECTIVITY (clusters DBSCAN sur centroides).

    Algorithme :
      1. Charge polygones forestiers (gr_ess in {R, F, M}).
      2. Calcule le centroide de chaque polygone.
      3. Optionnel : pour chaque polygone, lit le score habitat moyen
         depuis le raster MFFP_HABITAT_BRUT.tif (5 bandes → moyenne).
      4. DBSCAN(eps=eps_meters, min_samples) sur les centroides.
      5. Pour chaque cluster, calcule un MultiPolygon agrégé + statistiques.

    Args :
      eps_meters : Distance maximale (en m) entre 2 polygones d'un même cluster.
      min_samples : Nombre min de polygones par cluster.

    Returns dict avec output_path GeoPackage + statistiques par cluster.
    """
    import numpy as np
    import geopandas as gpd
    from shapely.geometry import MultiPolygon
    from shapely.ops import unary_union
    from sklearn.cluster import DBSCAN

    t0 = time.time()
    logger.info(
        "MFFP_CONNECTIVITY_START path=%s eps=%s min_samples=%d",
        pee_maj_gpkg_path, eps_meters, min_samples)

    out_path = Path(
        output_gpkg_path
        or (DERIVATIVES_OUTPUT_ROOT / "MFFP_CONNECTIVITE.gpkg"))

    gdf, layer = _load_gdf(pee_maj_gpkg_path)
    gdf = _ensure_epsg_32198(gdf)

    cols_lower = {c.lower(): c for c in gdf.columns}
    # Pour le filtre forestier, on utilise type_couv (R/F/M) qui est la
    # classification haut niveau, pas gr_ess (323 codes d'essences détaillés)
    type_couv_col = cols_lower.get("type_couv") or cols_lower.get("ty_couv")
    gr_ess_col = cols_lower.get("gr_ess")
    filter_col = type_couv_col or gr_ess_col
    if filter_col is None:
        raise ValueError(
            f"Colonnes type_couv/gr_ess absentes : "
            f"{list(gdf.columns)[:15]}")
    # Restreint aux peuplements forestiers (R/F/M)
    forest_mask = (
        gdf[filter_col].astype(str).str.strip().str.upper().isin(
            ["R", "F", "M"])
    )
    gdf_forest = gdf[forest_mask].copy()
    n_forest = len(gdf_forest)
    if n_forest == 0:
        raise RuntimeError(
            f"Aucun polygone forestier (R/F/M) trouvé dans {filter_col}.")

    # Centroides EPSG:32198 (mètres)
    centroids = gdf_forest.geometry.centroid
    coords = np.array(
        [[c.x, c.y] for c in centroids if c is not None and not c.is_empty])
    if len(coords) < min_samples:
        raise RuntimeError(
            f"Trop peu de centroides ({len(coords)}) pour DBSCAN "
            f"(min_samples={min_samples}).")

    # DBSCAN
    db = DBSCAN(eps=eps_meters, min_samples=min_samples)
    labels = db.fit_predict(coords)

    # Habitat mean optionnel (depuis le raster 5 bandes)
    habitat_mean_per_polygon = None
    if habitat_tif_path and Path(habitat_tif_path).exists():
        try:
            import rasterio
            from rasterio.sample import sample_gen
            with rasterio.open(habitat_tif_path) as src:
                pts = [(c.x, c.y) for c in centroids
                       if c is not None and not c.is_empty]
                samples = list(src.sample(pts))
                # Moyenne sur les 5 bandes
                habitat_mean_per_polygon = [
                    float(np.mean(s)) if s is not None else 0.0
                    for s in samples
                ]
        except Exception as e:
            logger.warning("HABITAT_SAMPLING_FAILED err=%s", e)
            habitat_mean_per_polygon = None

    # Agrégation par cluster
    gdf_forest = gdf_forest.iloc[:len(coords)].copy()
    gdf_forest["_cluster_id"] = labels
    if habitat_mean_per_polygon is not None:
        gdf_forest["_habitat_mean"] = habitat_mean_per_polygon[:len(coords)]
    else:
        gdf_forest["_habitat_mean"] = 0.0

    cluster_records: List[Dict[str, Any]] = []
    unique_clusters = sorted(set(labels))
    n_noise = int((labels == -1).sum())
    for cid in unique_clusters:
        if cid == -1:
            continue  # noise points
        sub = gdf_forest[gdf_forest["_cluster_id"] == cid]
        n = len(sub)
        try:
            unioned = unary_union(sub.geometry.tolist())
            if unioned.geom_type == "Polygon":
                unioned = MultiPolygon([unioned])
        except Exception:
            unioned = MultiPolygon(
                [g for g in sub.geometry if g is not None])
        cluster_records.append({
            "cluster_id": int(cid),
            "n_polygons": int(n),
            "habitat_score_mean": round(
                float(sub["_habitat_mean"].mean()), 2),
            "area_ha": round(float(unioned.area / 10000.0), 2),
            "forest_type_dominant": str(
                sub[filter_col].astype(str).str.upper().mode().iloc[0]
                if not sub[filter_col].mode().empty else ""),
            "geometry": unioned,
        })

    if not cluster_records:
        # DBSCAN n'a trouvé que du bruit (eps trop petit)
        logger.warning("MFFP_CONNECTIVITY_NO_CLUSTER all_noise=%d",
                       n_noise)
        cluster_records.append({
            "cluster_id": -1,
            "n_polygons": int(n_forest),
            "habitat_score_mean": 0.0,
            "area_ha": 0.0,
            "forest_type_dominant": "NOISE_ONLY",
            "geometry": MultiPolygon([]),
        })

    out_gdf = gpd.GeoDataFrame(
        cluster_records, crs=f"EPSG:{TARGET_EPSG}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_gdf.to_file(str(out_path), driver="GPKG", layer="connectivity")
    sha256 = _sha256_file(out_path)
    elapsed = round(time.time() - t0, 2)

    n_clusters_real = len([r for r in cluster_records if r["cluster_id"] >= 0])
    logger.info(
        "MFFP_CONNECTIVITY_DONE elapsed=%ss n_pol=%d n_clusters=%d "
        "n_noise=%d sha=%s",
        elapsed, n_forest, n_clusters_real, n_noise, sha256[:16])
    return {
        "manifest_id": "MFFP_CONNECTIVITY_COMPUTED_Ω",
        "ordre": "N°52-R15",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "algorithm": "DBSCAN_centroids_eps_min_samples",
        "output_path": str(out_path),
        "output_size_bytes": out_path.stat().st_size,
        "sha256": sha256,
        "n_forest_polygons": n_forest,
        "n_clusters_detected": n_clusters_real,
        "n_noise_points": n_noise,
        "dbscan_params": {"eps_meters": eps_meters,
                          "min_samples": min_samples},
        "cluster_summary_top10": [
            {k: v for k, v in r.items() if k != "geometry"}
            for r in sorted(cluster_records,
                             key=lambda r: r["area_ha"],
                             reverse=True)[:10]
        ],
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 8. MFFP_CONTINUITY (P2 · MEDIUM · 12h)
# ═════════════════════════════════════════════════════════════════════════
def compute_mffp_continuity(
    pee_maj_gpkg_path: str,
    perturbation_severity_dict: Dict[str, Any],
    output_tif_path: Optional[str] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R15 · MFFP_CONTINUITY (5 classes uint8, raster 100 m).

    Algorithme :
      1. Si perturb='HIGH' ET (current_year - an_perturb) <
         perturb_recent_threshold → classe 5 PERTURBE_RECENT.
      2. Sinon, calcul age depuis an_origine (ou cl_age proxy si absent) :
         · < 40 ans → 1 RECENT
         · 40-80 ans → 2 INTERMEDIAIRE
         · 80-150 ans → 3 ANCIEN
         · > 150 ans → 4 VIEILLES_FORÊTS

    Args :
      perturbation_severity_dict : Dict R15 validé (perturbation_severity).
    """
    import numpy as np

    t0 = time.time()
    logger.info("MFFP_CONTINUITY_START path=%s", pee_maj_gpkg_path)

    out_path = Path(
        output_tif_path
        or (DERIVATIVES_OUTPUT_ROOT / "MFFP_CONTINUITE.tif"))

    gdf, layer = _load_gdf(pee_maj_gpkg_path)
    gdf = _ensure_epsg_32198(gdf)

    current_year = int(perturbation_severity_dict.get(
        "current_year_assumption", 2026))
    severity_codes = perturbation_severity_dict.get("severity_codes", {})
    decision = perturbation_severity_dict.get("decision_rules", {})
    recent_thresh = int(decision.get(
        "perturb_recent_threshold_years", 25))
    cl_age_proxy = decision.get("cl_age_proxy_to_continuity", {})
    fallback_cls = int(decision.get("fallback_unknown_class", 1))

    cols_lower = {c.lower(): c for c in gdf.columns}
    an_origine_col = cols_lower.get("an_origine")
    perturb_col = cols_lower.get("perturb")
    an_perturb_col = cols_lower.get("an_perturb")
    cl_age_col = cols_lower.get("cl_age")

    def _classify(row) -> int:
        # 1. Perturbation récente HIGH severity → classe 5
        if perturb_col is not None and an_perturb_col is not None:
            p = row.get(perturb_col)
            ap = row.get(an_perturb_col)
            if p and ap:
                p_str = str(p).strip().upper()
                p_meta = severity_codes.get(p_str, {})
                if p_meta.get("severity") == "HIGH":
                    try:
                        years_since = current_year - int(ap)
                        if 0 <= years_since < recent_thresh:
                            return 5
                    except (TypeError, ValueError):
                        pass
        # 2. Age depuis an_origine
        if an_origine_col is not None:
            ao = row.get(an_origine_col)
            try:
                origin_year = int(ao) if ao else None
            except (TypeError, ValueError):
                origin_year = None
            if origin_year and 1700 <= origin_year <= current_year:
                age = current_year - origin_year
                if age < 40:
                    return 1
                if age < 80:
                    return 2
                if age < 150:
                    return 3
                return 4
        # 3. Fallback : cl_age proxy
        if cl_age_col is not None:
            ca = str(row.get(cl_age_col, "")).strip().upper()
            if ca in cl_age_proxy:
                return int(cl_age_proxy[ca])
        return fallback_cls

    gdf["_continuity_class"] = gdf.apply(_classify, axis=1).astype("uint8")
    n_polygons = len(gdf)
    class_dist = dict(Counter(
        gdf["_continuity_class"].tolist()).most_common())

    rast_info = _rasterize_to_tif(
        gdf, "_continuity_class", out_path,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)
    sha256 = _sha256_file(out_path)
    elapsed = round(time.time() - t0, 2)

    logger.info(
        "MFFP_CONTINUITY_DONE elapsed=%ss n_pol=%d sha=%s",
        elapsed, n_polygons, sha256[:16])
    return {
        "manifest_id": "MFFP_CONTINUITY_COMPUTED_Ω",
        "ordre": "N°52-R15",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_path": str(out_path),
        "output_size_bytes": out_path.stat().st_size,
        "sha256": sha256,
        "n_polygons_processed": n_polygons,
        "continuity_class_distribution": {
            str(k): int(v) for k, v in class_dist.items()
        },
        "rasterization": rast_info,
        "current_year_used": current_year,
        "perturb_recent_threshold_years": recent_thresh,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


__all__ = [
    "compute_mffp_productivity",
    "compute_mffp_habitat",
    "compute_mffp_connectivity",
    "compute_mffp_continuity",
    "SPECIES_BAND_ORDER",
]
