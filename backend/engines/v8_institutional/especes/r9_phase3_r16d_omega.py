"""
r9_phase3_r16d_omega.py — ORDRE N°52-R16-D · TACTICAL GROUND
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Implémentation R16-D des 3 cibles tactiques :
  · R9_SALINES                (raster + GPKG)
  · R9_AFFUTS_SCORE/.gpkg     (raster + GPKG)
  · R9_TERRITOIRES.gpkg       (vecteur uniquement, fusion multi-espèces)

+ Intégration des 6 hooks TERRITOIRE_ULTIME via probe registry-aware :
  IA_VISION, DONNEES_CHASSEUR, ENVIRONNEMENT, NUTRITION, COMPORTEMENT,
  PREDICTIF.

Doctrine :
  · Lit subset + rasters R8/R16-A/B/C (FUSION ADD-ONLY).
  · Applique règles `tactical_ground_rules.json` (VALIDÉ R16-D).
  · Probe les 6 hooks · output transparent (pas de simulation).
  · MAJ R9_RECALC_STATE.json → status=OK_REAL_PARTIAL_R16D.

ANTI_GÉNÉRIQUE_STRICT :
  · Hooks externes absents → skip_with_log (pas d'imputation).
  · Hooks loadable mais sans data → log + return None.

FUSION ADD-ONLY · Réutilise helpers P0 + R16-A/B/C.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("r9_phase3_r16d_omega")

from engines.v8_institutional.especes.mffp_phase3_p0_omega import (
    TARGET_EPSG, NODATA_VALUE_UINT8, _utc_now, _sha256_file,
    _load_gdf, _ensure_epsg_32198, _rasterize_to_tif,
)
from engines.v8_institutional.especes.r9_phase3_orchestrator_omega import (
    DERIVATIVES_R9_ROOT, R9_RECALC_STATE_PATH, DERIVATIVES_P1_ROOT,
    auto_pick_subset,
)
from engines.v8_institutional.especes.r9_phase3_r16b_omega import (
    SPECIES_LIST, _sample_raster_at_centroids,
)


# ═════════════════════════════════════════════════════════════════════════
# Hooks TERRITOIRE_ULTIME — probe registry-aware (6 hooks)
# ═════════════════════════════════════════════════════════════════════════
def probe_all_six_hooks() -> Dict[str, Any]:
    """Probe les 6 hooks TERRITOIRE_ULTIME et retourne leurs statuts.

    IA_VISION + DONNEES_CHASSEUR : interfaces python pré-existantes.
    ENVIRONNEMENT/NUTRITION/COMPORTEMENT/PREDICTIF : stubs R16-D-PREP.

    Aucun appel à load_data — uniquement la disponibilité.
    """
    results: Dict[str, Any] = {}

    # 1. IA_VISION (interface engine_ia_vision_ecologique_omega)
    try:
        import importlib
        m = importlib.import_module(
            "engines.v8_institutional.engine_ia_vision_ecologique_omega")
        iface_loadable = True
        # Probe basique — module loadable = available pour intégration
        results["IA_VISION"] = {
            "available": iface_loadable,
            "interface_loadable": True,
            "is_stub": False,
            "expected_paths_count": 0,
            "fallback": "skip_with_log",
            "note": (
                "Interface engine_ia_vision_ecologique_omega loadable. "
                "Aucune image/détection live consommée (pas d'image source)."),
        }
    except Exception as e:
        results["IA_VISION"] = {
            "available": False,
            "interface_loadable": False,
            "error": str(e)[:120],
        }

    # 2. DONNEES_CHASSEUR (interface gps_loader_omega)
    try:
        import importlib
        m = importlib.import_module(
            "engines.v8_institutional.especes.gps_loader_omega")
        results["DONNEES_CHASSEUR"] = {
            "available": True,
            "interface_loadable": True,
            "is_stub": False,
            "fallback": "skip_with_log",
            "note": (
                "Interface gps_loader_omega loadable. "
                "Aucune trace GPS live consommée (pas de fichier source)."),
        }
    except Exception as e:
        results["DONNEES_CHASSEUR"] = {
            "available": False,
            "interface_loadable": False,
            "error": str(e)[:120],
        }

    # 3-6. Stubs R16-D-PREP (probe directement)
    for hook_name, mod_name in (
            ("ENVIRONNEMENT", "environment_loader_omega"),
            ("NUTRITION", "nutrition_loader_omega"),
            ("COMPORTEMENT", "comportement_loader_omega"),
            ("PREDICTIF", "predictif_loader_omega")):
        try:
            import importlib
            m = importlib.import_module(
                f"engines.v8_institutional.especes.{mod_name}")
            results[hook_name] = m.probe()
        except Exception as e:
            results[hook_name] = {
                "available": False,
                "interface_loadable": False,
                "error": str(e)[:120],
            }

    return {
        "manifest_id": "R16D_HOOKS_PROBE_Ω",
        "ordre": "N°52-R16-D",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "n_hooks_total": len(results),
        "n_hooks_available": sum(
            1 for v in results.values() if v.get("available")),
        "n_hooks_with_external_data_present": sum(
            1 for v in results.values()
            if len(v.get("paths_present", [])) > 0
        ),
        "hooks": results,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 1. R9_SALINES (raster + GPKG)
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_salines(
    subset_path: str,
    zones_humides_tif: Path,
    productivity_tif: Path,
    habitat_tif: Path,
    corridors_multi_tif: Path,
    exclusions_tif: Path,
    tactical_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-D · R9_SALINES (uint8 0-100 + GPKG).

    score = w_h*humides + w_p*productivity + w_c*habitat_cervides_mean
            + w_l*corridors_multi + w_d*drainage_transitionnel
    · R9_EXCLUSIONS=1 → score=0.
    """
    import numpy as np
    import geopandas as gpd

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / "R9_SALINES.tif"
    out_gpkg = out_root / "R9_SALINES.gpkg"

    rules = tactical_dict.get("salines_rules", {})
    w = rules.get("score_formula_weights", {})
    w_h = float(w.get("zones_humides", 0.30))
    w_p = float(w.get("productivity", 0.20))
    w_c = float(w.get("habitat_cervides_mean", 0.25))
    w_l = float(w.get("corridors_multi", 0.15))
    w_d = float(w.get("drainage_transitionnel", 0.10))
    cervides = rules.get("cervides_species",
                          ["chevreuil", "orignal", "wapiti"])
    drai_codes = set(rules.get("drainage_transitionnel_codes", ["4", "5"]))
    threshold = float(rules.get("saline_threshold", 60))
    min_keep = float(rules.get("min_score_keep_in_gpkg", 60))

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)
    cols_lower = {c.lower(): c for c in gdf.columns}
    cl_drai_col = cols_lower.get("cl_drai")

    humid = _sample_raster_at_centroids(gdf, zones_humides_tif, band=1)
    # productivity float32 m³/ha → normalise 0-100
    prod = _sample_raster_at_centroids(gdf, productivity_tif, band=1)
    prod_norm = [
        min(float(p) / 5.0, 100.0) if p is not None else 0.0
        for p in prod
    ]
    # Habitat cervidés moyen (chevreuil + orignal + wapiti)
    hab_cerv = []
    for sp in cervides:
        try:
            band = SPECIES_LIST.index(sp) + 1
            hab_cerv.append(
                _sample_raster_at_centroids(
                    gdf, habitat_tif, band=band))
        except (ValueError, IndexError):
            pass
    if hab_cerv:
        hab_cerv_arr = np.array(hab_cerv, dtype="float32")
        hab_cerv_mean = hab_cerv_arr.mean(axis=0)
    else:
        hab_cerv_mean = np.zeros(len(gdf), dtype="float32")
    corr_multi = _sample_raster_at_centroids(
        gdf, corridors_multi_tif, band=1)
    excl = _sample_raster_at_centroids(gdf, exclusions_tif, band=1)

    scores = []
    for i in range(len(gdf)):
        if excl[i] >= 1.0:
            scores.append(0)
            continue
        # Drainage transitionnel : 100 si cl_drai ∈ {4,5}, sinon 0
        d_score = 0.0
        if cl_drai_col is not None:
            cd = str(gdf.iloc[i][cl_drai_col]).strip()
            if cd in drai_codes:
                d_score = 100.0
        # Humid score (0/1) → x100
        h_score = 100.0 * float(humid[i])
        s = (w_h * h_score
             + w_p * float(prod_norm[i])
             + w_c * float(hab_cerv_mean[i])
             + w_l * float(corr_multi[i])
             + w_d * d_score)
        scores.append(int(round(min(max(s, 0), 100))))

    gdf["_salines"] = scores
    gdf["_salines"] = gdf["_salines"].astype("uint8")

    rast_info = _rasterize_to_tif(
        gdf, "_salines", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    # Export GPKG : polygones haute valeur ≥ min_keep
    high = gdf[gdf["_salines"] >= int(min_keep)].copy()
    high = high.rename(columns={"_salines": "saline_score"})
    if len(high) > 0:
        high[["saline_score", "geometry"]].to_file(
            str(out_gpkg), driver="GPKG", layer="salines")
    else:
        empty = gpd.GeoDataFrame(
            {"saline_score": [0], "geometry": [gdf.geometry.iloc[0]]},
            crs=gdf.crs)
        empty.to_file(
            str(out_gpkg), driver="GPKG", layer="salines_empty")

    sha_tif = _sha256_file(out_tif)
    sha_gpkg = _sha256_file(out_gpkg) if out_gpkg.exists() else None
    arr = np.array(scores, dtype="uint8")
    elapsed = round(time.time() - t0, 2)
    return {
        "manifest_id": "R9_SALINES_COMPUTED_Ω",
        "ordre": "N°52-R16-D",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "weights_applied": {
            "zones_humides": w_h, "productivity": w_p,
            "habitat_cervides_mean": w_c,
            "corridors_multi": w_l,
            "drainage_transitionnel": w_d},
        "cervides_species_used": cervides,
        "drainage_transitionnel_codes": sorted(drai_codes),
        "saline_threshold": threshold,
        "output_raster": str(out_tif),
        "output_vector": str(out_gpkg),
        "raster_size_bytes": out_tif.stat().st_size,
        "vector_size_bytes": (out_gpkg.stat().st_size
                              if out_gpkg.exists() else 0),
        "raster_sha256": sha_tif,
        "vector_sha256": sha_gpkg,
        "n_polygons_processed": len(gdf),
        "n_high_saline_polygons": int((arr >= int(threshold)).sum()),
        "mean_score": round(float(arr.mean()), 2),
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 2. R9_AFFUTS (raster + GPKG)
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_affuts(
    subset_path: str,
    corridors_multi_tif: Path,
    alimentation_tifs: Dict[str, Path],
    couvert_securite_tif: Path,
    exclusions_tif: Path,
    tactical_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-D · R9_AFFUTS_SCORE (uint8 0-100) + R9_AFFUTS.gpkg.

    score = w_l*corridors_multi + w_a*alimentation_target_mean
            + w_c*couvert_moderate_inverted
            + w_s*semi_open_cl_dens + w_e*edge_proxy
    """
    import numpy as np
    import geopandas as gpd

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / "R9_AFFUTS_SCORE.tif"
    out_gpkg = out_root / "R9_AFFUTS.gpkg"

    rules = tactical_dict.get("affuts_rules", {})
    w = rules.get("score_formula_weights", {})
    w_l = float(w.get("corridors_multi", 0.30))
    w_a = float(w.get("alimentation_target_species_mean", 0.25))
    w_cv = float(w.get("couvert_securite_moderate", 0.15))
    w_s = float(w.get("semi_open_structure", 0.15))
    w_e = float(w.get("edge_proximity_proxy", 0.15))
    target_sp = rules.get("target_species_for_affut", [
        "chevreuil", "orignal", "ours_noir", "dindon"])
    semi_open_codes = set(rules.get("semi_open_cl_dens_codes", ["B", "C"]))
    couv_range = rules.get("couvert_moderate_range", [40, 70])
    threshold = float(rules.get("affut_threshold", 60))
    min_keep = float(rules.get("min_score_keep_in_gpkg", 60))

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)
    cols_lower = {c.lower(): c for c in gdf.columns}
    cl_dens_col = cols_lower.get("cl_dens")
    type_couv_col = cols_lower.get("type_couv")

    corr_multi = _sample_raster_at_centroids(
        gdf, corridors_multi_tif, band=1)
    couv = _sample_raster_at_centroids(
        gdf, couvert_securite_tif, band=1)
    excl = _sample_raster_at_centroids(gdf, exclusions_tif, band=1)
    # Alimentation moyenne sur target species
    alim_arrays = []
    for sp in target_sp:
        if sp in alimentation_tifs and alimentation_tifs[sp].exists():
            alim_arrays.append(
                _sample_raster_at_centroids(
                    gdf, alimentation_tifs[sp], band=1))
    if alim_arrays:
        alim_mean = np.array(
            alim_arrays, dtype="float32").mean(axis=0)
    else:
        alim_mean = np.zeros(len(gdf), dtype="float32")

    scores = []
    for i in range(len(gdf)):
        if excl[i] >= 1.0:
            scores.append(0)
            continue
        # Couvert "modéré" : score 100 si dans [40, 70], décroît linéairement
        c_val = float(couv[i])
        if couv_range[0] <= c_val <= couv_range[1]:
            cv_score = 100.0
        else:
            # distance à la zone optimale
            dist = (couv_range[0] - c_val if c_val < couv_range[0]
                    else c_val - couv_range[1])
            cv_score = max(100 - dist * 1.5, 0)
        # Semi-ouvert (cl_dens B ou C)
        s_score = 0.0
        if cl_dens_col is not None:
            cd = str(gdf.iloc[i][cl_dens_col]).strip().upper()
            if cd in semi_open_codes:
                s_score = 100.0
        # Edge proxy : type_couv mixte (M/FE/RE) ou polygone humide proche
        e_score = 0.0
        if type_couv_col is not None:
            tc = str(gdf.iloc[i][type_couv_col]).strip().upper()
            if tc in ("M", "FE", "RE", "MFR", "MRE", "MFE"):
                e_score = 100.0

        s = (w_l * float(corr_multi[i])
             + w_a * float(alim_mean[i])
             + w_cv * cv_score
             + w_s * s_score
             + w_e * e_score)
        scores.append(int(round(min(max(s, 0), 100))))

    gdf["_affut"] = scores
    gdf["_affut"] = gdf["_affut"].astype("uint8")

    rast_info = _rasterize_to_tif(
        gdf, "_affut", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    high = gdf[gdf["_affut"] >= int(min_keep)].copy()
    high = high.rename(columns={"_affut": "affut_score"})
    if len(high) > 0:
        high["centroid_x"] = high.geometry.centroid.x
        high["centroid_y"] = high.geometry.centroid.y
        high[["affut_score", "centroid_x", "centroid_y",
              "geometry"]].to_file(
            str(out_gpkg), driver="GPKG", layer="affuts")
    else:
        empty = gpd.GeoDataFrame(
            {"affut_score": [0], "geometry": [gdf.geometry.iloc[0]]},
            crs=gdf.crs)
        empty.to_file(
            str(out_gpkg), driver="GPKG", layer="affuts_empty")

    sha_tif = _sha256_file(out_tif)
    sha_gpkg = _sha256_file(out_gpkg) if out_gpkg.exists() else None
    arr = np.array(scores, dtype="uint8")
    elapsed = round(time.time() - t0, 2)
    return {
        "manifest_id": "R9_AFFUTS_COMPUTED_Ω",
        "ordre": "N°52-R16-D",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "target_species_for_affut": target_sp,
        "n_alimentation_layers_used": len(alim_arrays),
        "weights_applied": {
            "corridors_multi": w_l,
            "alimentation_target_mean": w_a,
            "couvert_moderate": w_cv,
            "semi_open_structure": w_s,
            "edge_proxy": w_e},
        "couvert_moderate_range": couv_range,
        "semi_open_cl_dens_codes": sorted(semi_open_codes),
        "affut_threshold": threshold,
        "output_raster": str(out_tif),
        "output_vector": str(out_gpkg),
        "raster_size_bytes": out_tif.stat().st_size,
        "vector_size_bytes": (out_gpkg.stat().st_size
                              if out_gpkg.exists() else 0),
        "raster_sha256": sha_tif,
        "vector_sha256": sha_gpkg,
        "n_polygons_processed": len(gdf),
        "n_high_affut_polygons": int((arr >= int(threshold)).sum()),
        "mean_score": round(float(arr.mean()), 2),
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 3. R9_TERRITOIRES (vecteur uniquement)
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_tactical_zones(
    subset_path: str,
    layers_per_species_tifs: Dict[str, Dict[str, Path]],
    exclusions_tif: Path,
    tactical_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-D · R9_TERRITOIRES.gpkg (vecteur fusion multi-espèces).

    Pour chaque polygone, calcule un score territoire-haute-valeur =
    moyenne pondérée par masse des 5 layers (vitales+link+hotspot+repos+alim)
    par espèce. Top percentile → polygones "territoires".

    Args:
      layers_per_species_tifs: dict {species: {layer_key: path}}
        layer_key ∈ {"zones_vitales", "link_score", "hotspot_binary",
                      "repos", "alimentation"}.
    """
    import numpy as np
    import geopandas as gpd

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_gpkg = out_root / "R9_TERRITOIRES.gpkg"

    rules = tactical_dict.get("territoires_rules", {})
    w_per = rules.get("score_formula_weights_per_layer", {})
    sp_w = rules.get("species_weights_by_mass", {})
    high_thresh = float(rules.get("high_value_threshold", 70))
    top_pct = float(rules.get("top_percentile", 90))

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)
    excl = _sample_raster_at_centroids(gdf, exclusions_tif, band=1)

    # Pour chaque espèce, calcul du score combiné par polygone
    species_scores: Dict[str, List[float]] = {}
    layers_used_per_species: Dict[str, List[str]] = {}

    for sp, layers_dict in layers_per_species_tifs.items():
        scores_sp = np.zeros(len(gdf), dtype="float32")
        weight_total = 0.0
        used_layers = []
        for layer_key, weight_key in (
                ("zones_vitales", "zones_vitales"),
                ("link_score", "link_score"),
                ("hotspot_binary", "hotspot_binary"),
                ("repos", "repos"),
                ("alimentation", "alimentation")):
            tif_path = layers_dict.get(layer_key)
            w = float(w_per.get(weight_key, 0))
            if tif_path is None or not Path(tif_path).exists() or w == 0:
                continue
            vals = _sample_raster_at_centroids(
                gdf, Path(tif_path), band=1)
            arr = np.array(vals, dtype="float32")
            # hotspot_binary = 0/1 → multiplier par 100 pour cohérence
            if layer_key == "hotspot_binary":
                arr = arr * 100.0
            scores_sp += w * arr
            weight_total += w
            used_layers.append(layer_key)
        if weight_total > 0:
            scores_sp = scores_sp / weight_total
            scores_sp = np.clip(scores_sp, 0, 100)
        species_scores[sp] = scores_sp.tolist()
        layers_used_per_species[sp] = used_layers

    # Fusion multi-espèces pondérée par masse
    fusion_score = np.zeros(len(gdf), dtype="float32")
    total_w = 0.0
    weights_applied: Dict[str, float] = {}
    for sp, scores in species_scores.items():
        w = float(sp_w.get(sp, 0))
        if w > 0 and scores:
            fusion_score += w * np.array(scores, dtype="float32")
            total_w += w
            weights_applied[sp] = w
    if total_w > 0:
        fusion_score = fusion_score / total_w
    # Apply exclusions
    excl_arr = np.array(excl, dtype="float32")
    fusion_score = np.where(excl_arr >= 1.0, 0.0, fusion_score)

    # Top percentile threshold
    pos_scores = fusion_score[fusion_score > 0]
    if pos_scores.size > 0:
        threshold_value = float(np.percentile(pos_scores, top_pct))
    else:
        threshold_value = 0.0
    threshold_value = max(threshold_value, high_thresh)

    gdf["tactical_value_score"] = fusion_score.astype("float32")
    gdf["is_high_value_zone"] = (
        fusion_score >= threshold_value).astype("uint8")

    high = gdf[gdf["is_high_value_zone"] == 1].copy()
    if len(high) > 0:
        # Conserve fields synthétiques pour cartographie
        cols_lower = {c.lower(): c for c in high.columns}
        keep_cols = ["tactical_value_score", "is_high_value_zone"]
        for f in ("type_couv", "gr_ess", "cl_age", "cl_dens"):
            if cols_lower.get(f):
                keep_cols.append(cols_lower[f])
        keep_cols.append("geometry")
        high[keep_cols].to_file(
            str(out_gpkg), driver="GPKG", layer="tactical_zones")
    else:
        empty = gpd.GeoDataFrame(
            {"tactical_value_score": [0.0],
             "is_high_value_zone": [0],
             "geometry": [gdf.geometry.iloc[0]]},
            crs=gdf.crs)
        empty.to_file(
            str(out_gpkg), driver="GPKG", layer="tactical_zones_empty")

    sha_gpkg = _sha256_file(out_gpkg)
    elapsed = round(time.time() - t0, 2)
    return {
        "manifest_id": "R9_TACTICAL_ZONES_COMPUTED_Ω",
        "ordre": "N°52-R16-D",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "vector_only_no_raster": True,
        "output_vector": str(out_gpkg),
        "vector_size_bytes": out_gpkg.stat().st_size,
        "vector_sha256": sha_gpkg,
        "n_polygons_processed": len(gdf),
        "n_high_value_zones": int(gdf["is_high_value_zone"].sum()),
        "high_value_threshold_used": round(threshold_value, 2),
        "high_value_threshold_min_doctrinal": high_thresh,
        "top_percentile_used": top_pct,
        "species_weights_normalized": weights_applied,
        "layers_used_per_species": layers_used_per_species,
        "mean_fusion_score": round(float(fusion_score.mean()), 2),
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# Pipeline R16-D Orchestrator
# ═════════════════════════════════════════════════════════════════════════
def execute_r16d_pipeline(
    subset_path: Optional[str] = None,
    targets_subset: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-D · Pipeline TACTICAL_GROUND.

    1. Charge dépendances R8 + R16-A/B/C
    2. Génère SALINES, AFFUTS, TERRITOIRES
    3. Probe les 6 hooks TERRITOIRE_ULTIME (registry-aware)
    4. MAJ R9_RECALC_STATE.json → status=OK_REAL_PARTIAL_R16D
    """
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega import (  # noqa: E501
        load_dictionary,
    )

    t0 = time.time()
    src = subset_path or auto_pick_subset()
    if not src:
        raise RuntimeError(
            "Aucun subset utilisable. Lancer export-subset VSI.")

    tactical = load_dictionary("tactical_ground_rules")
    if tactical is None:
        raise RuntimeError("tactical_ground_rules.json absent ou invalide.")

    # Hooks probe (transparence ANTI_GÉNÉRIQUE_STRICT)
    hooks_probe = probe_all_six_hooks()

    # Dépendances rasters
    humides = DERIVATIVES_R9_ROOT / "R9_ZONES_HUMIDES.tif"
    productivity = DERIVATIVES_P1_ROOT / "MFFP_PRODUCTIVITE.tif"
    habitat = DERIVATIVES_P1_ROOT / "MFFP_HABITAT_BRUT.tif"
    corridors_multi = DERIVATIVES_R9_ROOT / "R9_CORRIDORS_MULTI_ESPECES.tif"
    excl = DERIVATIVES_R9_ROOT / "R9_EXCLUSIONS.tif"
    couvert = DERIVATIVES_R9_ROOT / "R9_COUVERT_SECURITE.tif"
    missing = [
        str(p) for p in [humides, productivity, habitat,
                          corridors_multi, excl, couvert]
        if not p.exists()
    ]
    if missing:
        raise RuntimeError(
            f"Dépendances absentes : {missing}. "
            f"Lancer R15 P1 + R16-A/B/C au préalable.")

    pipeline_targets = targets_subset or [
        "R9_SALINES", "R9_AFFUTS", "R9_TERRITOIRES"]

    results: Dict[str, Any] = {}
    succeeded: List[str] = []

    if "R9_SALINES" in pipeline_targets:
        try:
            r = compute_r9_salines(
                src, humides, productivity, habitat,
                corridors_multi, excl, tactical)
            results["R9_SALINES"] = r
            succeeded.append("R9_SALINES")
        except Exception as e:
            import traceback
            results["R9_SALINES"] = {
                "manifest_id": "R9_SALINES_FAILED_Ω",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            }

    if "R9_AFFUTS" in pipeline_targets:
        try:
            alim_tifs = {
                sp: (DERIVATIVES_R9_ROOT
                     / f"R9_ALIMENTATION_{sp.upper()}.tif")
                for sp in SPECIES_LIST
            }
            r = compute_r9_affuts(
                src, corridors_multi, alim_tifs, couvert,
                excl, tactical)
            results["R9_AFFUTS"] = r
            succeeded.append("R9_AFFUTS")
        except Exception as e:
            import traceback
            results["R9_AFFUTS"] = {
                "manifest_id": "R9_AFFUTS_FAILED_Ω",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            }

    if "R9_TERRITOIRES" in pipeline_targets:
        try:
            layers_per_species: Dict[str, Dict[str, Path]] = {}
            for sp in SPECIES_LIST:
                layers_per_species[sp] = {
                    "zones_vitales": (
                        DERIVATIVES_R9_ROOT
                        / f"R9_ZONES_VITALES_{sp.upper()}.tif"),
                    "link_score": (
                        DERIVATIVES_R9_ROOT
                        / f"R9_CORRIDORS_{sp.upper()}.tif"),
                    "hotspot_binary": (
                        DERIVATIVES_R9_ROOT
                        / f"R9_HOTSPOTS_{sp.upper()}.tif"),
                    "repos": (
                        DERIVATIVES_R9_ROOT
                        / f"R9_REPOS_{sp.upper()}.tif"),
                    "alimentation": (
                        DERIVATIVES_R9_ROOT
                        / f"R9_ALIMENTATION_{sp.upper()}.tif"),
                }
            r = compute_r9_tactical_zones(
                src, layers_per_species, excl, tactical)
            results["R9_TERRITOIRES"] = r
            succeeded.append("R9_TERRITOIRES")
        except Exception as e:
            import traceback
            results["R9_TERRITOIRES"] = {
                "manifest_id": "R9_TERRITOIRES_FAILED_Ω",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            }

    # Update R9_RECALC_STATE
    state_update = None
    try:
        state = (
            json.loads(R9_RECALC_STATE_PATH.read_text(encoding="utf-8"))
            if R9_RECALC_STATE_PATH.exists() else {})
        targets_state = state.setdefault("targets", {})
        for full in succeeded:
            targets_state[full] = {
                "status": "OK_REAL",
                "ordre": "N°52-R16-D",
                "completed_at_utc": _utc_now(),
                "output_raster": results[full].get("output_raster"),
                "output_vector": results[full].get("output_vector"),
                "raster_sha256": results[full].get("raster_sha256"),
                "vector_sha256": results[full].get("vector_sha256"),
                "elapsed_s": results[full].get("elapsed_s"),
            }
        state["last_r16d_run_id"] = f"R16D_{int(time.time())}"
        state["last_r16d_run_completed_at_utc"] = _utc_now()
        state["last_r16d_subset_used"] = src
        state["last_r16d_targets_succeeded"] = succeeded
        state["last_r16d_hooks_probe"] = hooks_probe
        if len(succeeded) == 3:
            state["status"] = "OK_REAL_PARTIAL_R16D"
        R9_RECALC_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        R9_RECALC_STATE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        state_update = {
            "updated": True,
            "new_global_status": state["status"],
            "targets_marked_OK_REAL": succeeded,
        }
    except Exception as e:
        import traceback
        state_update = {
            "updated": False,
            "error": str(e)[:300],
            "traceback": traceback.format_exc()[-500:],
        }

    elapsed_total = round(time.time() - t0, 2)
    return {
        "manifest_id": "R9_PHASE3_R16D_PIPELINE_COMPLETED_Ω",
        "ordre": "N°52-R16-D",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "subset_used": src,
        "n_targets_total": len(pipeline_targets),
        "n_targets_succeeded": len(succeeded),
        "targets_succeeded": succeeded,
        "results": results,
        "territoire_ultime_six_hooks_probe": hooks_probe,
        "r9_recalc_state_update": state_update,
        "elapsed_total_s": elapsed_total,
        "v30_lock": "INVIOLÉ",
    }


__all__ = [
    "execute_r16d_pipeline",
    "compute_r9_salines",
    "compute_r9_affuts",
    "compute_r9_tactical_zones",
    "probe_all_six_hooks",
]
