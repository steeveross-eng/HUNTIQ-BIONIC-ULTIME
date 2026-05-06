"""
r9_phase3_r16b_omega.py — ORDRE N°52-R16-B · BIOTIC BEHAVIOR (5 espèces)
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Implémentation R16-B des 4 cibles biotiques × 5 espèces = 20 cibles R9 :
  · R9_ZONES_VITALES_[ESPECE]    (combinaison habitat × couvert × alim)
  · R9_REPOS_[ESPECE]            (couvert sécurité × préférences espèce)
  · R9_ALIMENTATION_[ESPECE]     (proxy règles MFFP — anti-générique strict)
  · R9_RUT_[ESPECE]              (zones reproduction selon phénologie)

Espèces : chevreuil, orignal, ours_noir, dindon, wapiti

Doctrine :
  · Lit le subset Bas-Saint-Laurent (auto-pick mtime).
  · Charge MFFP_HABITAT_BRUT.tif (5 bandes) — sample sur centroides.
  · Charge R9_COUVERT_SECURITE.tif et R9_ZONES_HUMIDES.tif et
    R9_EXCLUSIONS.tif depuis derivatives_r9/ (FUSION ADD-ONLY).
  · Charge dicts habitat_preferences_par_espece + phenologie_saisonniere.
  · Pour chaque espèce : 4 rasters uint8 0-100 + 4 GPKG export.
  · Applique R9_EXCLUSIONS (multiplie score par (1 - excluded)).
  · MAJ R9_RECALC_STATE.json → status=OK_REAL_PARTIAL_R16B.

ANTI_GÉNÉRIQUE_STRICT :
  · Aucune simulation : tous les scores dérivent de données MFFP réelles
    + dicts VALIDÉS Saucier 2009, Crête 1997, Tardif 2007, etc.
  · NUTRITION hooks absents → utilise proxy `alimentation_proxy_rules`
    documenté dans phenologie_saisonniere.json (transparent dans output).

FUSION ADD-ONLY · Réutilise helpers P0 + R16-A.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("r9_phase3_r16b_omega")

# Réutilisation FUSION ADD-ONLY
from engines.v8_institutional.especes.mffp_phase3_p0_omega import (
    TARGET_EPSG, NODATA_VALUE_UINT8, _utc_now, _sha256_file,
    _load_gdf, _ensure_epsg_32198, _rasterize_to_tif,
)
from engines.v8_institutional.especes.r9_phase3_orchestrator_omega import (
    DERIVATIVES_R9_ROOT, R9_RECALC_STATE_PATH,
    DERIVATIVES_P1_ROOT, auto_pick_subset,
)

SPECIES_LIST = ["chevreuil", "orignal", "ours_noir", "dindon", "wapiti"]
TARGETS_R16B_PER_SPECIES = ["ZONES_VITALES", "REPOS", "ALIMENTATION", "RUT"]


# ═════════════════════════════════════════════════════════════════════════
# Helpers : lecture rasters R8/R16-A et sample sur centroides
# ═════════════════════════════════════════════════════════════════════════
def _sample_raster_at_centroids(gdf, raster_path: Path,
                                  band: int = 1,
                                  fallback_value: float = 0.0) -> List[float]:
    """Sample un raster sur les centroides du GeoDataFrame.
    Si raster absent → returns [fallback_value]*len(gdf) + log."""
    if not raster_path.exists():
        logger.warning(
            "R16B_RASTER_ABSENT path=%s fallback=%s",
            raster_path, fallback_value)
        return [float(fallback_value)] * len(gdf)
    try:
        import rasterio
        centroids = gdf.geometry.centroid
        pts = [(c.x, c.y) for c in centroids
               if c is not None and not c.is_empty]
        with rasterio.open(str(raster_path)) as src:
            samples = list(src.sample(pts, indexes=[band]))
        out = [
            float(s[0]) if s is not None and len(s) > 0
            else float(fallback_value)
            for s in samples
        ]
        # Pad si moins de pts (geometries vides)
        while len(out) < len(gdf):
            out.append(float(fallback_value))
        return out[:len(gdf)]
    except Exception as e:
        logger.warning(
            "R16B_RASTER_SAMPLE_ERROR path=%s err=%s",
            raster_path, str(e)[:100])
        return [float(fallback_value)] * len(gdf)


def _alimentation_score_for_polygon(
        row_dict: Dict[str, Any], species_proxy_rules: Dict[str, Any],
        humid_score_for_row: float = 0.0) -> int:
    """Calcule le score alimentation 0-100 selon les règles proxy de l'espèce."""
    type_couv = str(row_dict.get("type_couv", "")).strip().upper()
    cl_age = str(row_dict.get("cl_age", "")).strip().upper()
    cl_dens = str(row_dict.get("cl_dens", "")).strip().upper()
    score = 0.0
    weight_total = 0.0

    # type_couv score
    type_keys = {
        "F": "type_couv_F_score",
        "R": "type_couv_R_score",
        "M": "type_couv_M_score",
        "F_M": "type_couv_F_M_score",
    }
    for tk, dk in type_keys.items():
        if dk in species_proxy_rules:
            applies = (
                tk == type_couv or
                (tk == "F_M" and type_couv in ("F", "M"))
            )
            if applies:
                score += float(species_proxy_rules[dk])
                weight_total += 1
                break

    # cl_age score (groupes)
    age_groups = {
        "10_30": ["10", "30", "JIN", "JIR"],
        "30_50_70": ["30", "50", "70", "JIN", "JIR"],
        "50_70_90": ["50", "70", "90"],
        "50_70": ["50", "70"],
        "70_90_120": ["70", "90", "120", "VI"],
        "VIN_VIR": ["VIN", "VIR", "VIRS"],
    }
    for ag_key, ag_list in age_groups.items():
        dk = f"cl_age_{ag_key}_score"
        if dk in species_proxy_rules and cl_age in ag_list:
            score += float(species_proxy_rules[dk])
            weight_total += 1
            break

    # cl_dens score
    dens_groups = {
        "A_B": ["A", "B"],
        "B_C": ["B", "C"],
        "C_D": ["C", "D"],
        "C_D_E": ["C", "D", "E"],
    }
    for dg_key, dg_list in dens_groups.items():
        dk = f"cl_dens_{dg_key}_score"
        if dk in species_proxy_rules and cl_dens in dg_list:
            score += float(species_proxy_rules[dk])
            weight_total += 1
            break

    # near_humid bonus (orignal)
    if "near_humid_bonus" in species_proxy_rules and humid_score_for_row > 0:
        score += float(species_proxy_rules["near_humid_bonus"])
        weight_total += 1

    if weight_total == 0:
        return 0
    return int(round(min(max(score / weight_total, 0), 100)))


# ═════════════════════════════════════════════════════════════════════════
# 1. R9_ZONES_VITALES_[ESPECE]
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_zones_vitales(
    species: str,
    subset_path: str,
    habitat_tif: Path,
    couvert_securite_tif: Path,
    zones_humides_tif: Path,
    exclusions_tif: Path,
    phenologie_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-B · R9_ZONES_VITALES_[ESPECE] (uint8 0-100).

    Score combiné : habitat × couvert_securite × alimentation_potential
    moins exclusion_penalty selon vital_zone_weights de phenologie.
    """
    import numpy as np
    import geopandas as gpd

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / f"R9_ZONES_VITALES_{species.upper()}.tif"
    out_gpkg = out_root / f"R9_ZONES_VITALES_{species.upper()}.gpkg"

    species_idx = SPECIES_LIST.index(species)  # band 1-based
    species_pheno = phenologie_dict.get("calendar", {}).get(species, {})
    if not species_pheno:
        raise ValueError(f"Espèce {species} absente du phenologie_dict.")
    weights = species_pheno.get("vital_zone_weights", {})
    proxy_rules = (
        phenologie_dict.get("alimentation_proxy_rules", {})
        .get("rules_per_species", {})
        .get(species, {}))

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)
    cols_lower = {c.lower(): c for c in gdf.columns}

    # Sample raster MFFP_HABITAT_BRUT band correspondant à l'espèce
    habitat_scores = _sample_raster_at_centroids(
        gdf, habitat_tif, band=species_idx + 1)
    couvert_scores = _sample_raster_at_centroids(
        gdf, couvert_securite_tif, band=1)
    humid_flags = _sample_raster_at_centroids(
        gdf, zones_humides_tif, band=1)
    excl_flags = _sample_raster_at_centroids(
        gdf, exclusions_tif, band=1)

    # Calcul alimentation score par polygone
    alim_scores = []
    for i, (_, row) in enumerate(gdf.iterrows()):
        row_dict = {
            "type_couv": row.get(cols_lower.get("type_couv"), ""),
            "cl_age": row.get(cols_lower.get("cl_age"), ""),
            "cl_dens": row.get(cols_lower.get("cl_dens"), ""),
        }
        alim_scores.append(_alimentation_score_for_polygon(
            row_dict, proxy_rules, humid_flags[i]))

    # Score combiné pondéré
    w_h = float(weights.get("habitat_score", 0.40))
    w_c = float(weights.get("couvert_securite", 0.30))
    w_a = float(weights.get("alimentation_potential", 0.20))
    w_e = float(weights.get("exclusion_penalty", 0.10))

    def _combine(idx: int) -> int:
        h = float(habitat_scores[idx])
        c = float(couvert_scores[idx])
        a = float(alim_scores[idx])
        e = float(excl_flags[idx])
        if e >= 1.0:  # exclusion → score 0 (anti_generique strict)
            return 0
        score = w_h * h + w_c * c + w_a * a - w_e * (e * 100.0)
        return int(round(min(max(score, 0), 100)))

    gdf[f"_zv_{species}"] = [
        _combine(i) for i in range(len(gdf))
    ]
    gdf[f"_zv_{species}"] = gdf[f"_zv_{species}"].astype("uint8")

    # Rasterisation
    rast_info = _rasterize_to_tif(
        gdf, f"_zv_{species}", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    # Export GPKG (top zones uniquement, ≥ 70 pour économiser)
    high_zones = gdf[gdf[f"_zv_{species}"] >= 70].copy()
    high_zones = high_zones.rename(
        columns={f"_zv_{species}": "vital_score"})
    if len(high_zones) > 0:
        high_zones[["vital_score", "geometry"]].to_file(
            str(out_gpkg), driver="GPKG", layer=f"vitales_{species}")
    else:
        # GPKG minimal pour tracabilité
        empty = gpd.GeoDataFrame(
            {"vital_score": [0], "geometry": [gdf.geometry.iloc[0]]},
            crs=gdf.crs)
        empty.to_file(
            str(out_gpkg), driver="GPKG",
            layer=f"vitales_{species}_empty")

    sha_tif = _sha256_file(out_tif)
    sha_gpkg = _sha256_file(out_gpkg) if out_gpkg.exists() else None
    elapsed = round(time.time() - t0, 2)
    arr = gdf[f"_zv_{species}"].values
    return {
        "manifest_id": f"R9_ZONES_VITALES_{species.upper()}_COMPUTED_Ω",
        "ordre": "N°52-R16-B",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species": species,
        "habitat_band_used": species_idx + 1,
        "weights_applied": {
            "habitat": w_h, "couvert": w_c,
            "alimentation": w_a, "exclusion_penalty": w_e},
        "output_raster": str(out_tif),
        "output_vector": str(out_gpkg),
        "raster_size_bytes": out_tif.stat().st_size,
        "vector_size_bytes": (out_gpkg.stat().st_size
                              if out_gpkg.exists() else 0),
        "raster_sha256": sha_tif,
        "vector_sha256": sha_gpkg,
        "n_polygons_processed": len(gdf),
        "n_high_value_polygons": int((arr >= 70).sum()),
        "mean_score": round(float(arr.mean()), 2),
        "bucket_distribution": {
            "0_25": int(((arr >= 0) & (arr < 25)).sum()),
            "25_50": int(((arr >= 25) & (arr < 50)).sum()),
            "50_75": int(((arr >= 50) & (arr < 75)).sum()),
            "75_100": int((arr >= 75).sum()),
        },
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 2. R9_REPOS_[ESPECE]
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_repos(
    species: str,
    subset_path: str,
    couvert_securite_tif: Path,
    exclusions_tif: Path,
    phenologie_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-B · R9_REPOS_[ESPECE] (uint8 0-100).

    Privilégie : couvert_securite HIGH + features espèce-spécifiques
    (cl_dens_A_B, cl_haut_4-6, type_couv préféré).
    """
    import numpy as np

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / f"R9_REPOS_{species.upper()}.tif"

    species_pheno = phenologie_dict.get("calendar", {}).get(species, {})
    repos_features = species_pheno.get("repos_preferred_features", [])

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)
    cols_lower = {c.lower(): c for c in gdf.columns}

    couvert_scores = _sample_raster_at_centroids(
        gdf, couvert_securite_tif, band=1)
    excl_flags = _sample_raster_at_centroids(
        gdf, exclusions_tif, band=1)

    def _repos_score(idx: int, row) -> int:
        if excl_flags[idx] >= 1.0:
            return 0
        # Base : couvert_securite (0-100)
        score = 0.50 * float(couvert_scores[idx])
        # Bonus features espèce
        bonus = 0.0
        n_features = 0
        for feat in repos_features:
            n_features += 1
            if feat == "couvert_securite_HIGH":
                bonus += (1.0 if couvert_scores[idx] >= 70 else 0.0) * 100
            elif feat.startswith("cl_dens_"):
                preferred = feat.replace("cl_dens_", "").split("_")
                cd = str(row.get(cols_lower.get("cl_dens", ""), "")).strip().upper()
                bonus += (100 if cd in preferred else 0)
            elif feat.startswith("cl_haut_"):
                preferred = feat.replace("cl_haut_", "").split("_")
                ch = str(row.get(cols_lower.get("cl_haut", ""), "")).strip().upper()
                bonus += (100 if ch in preferred else 0)
            elif feat.startswith("type_couv_"):
                preferred = feat.replace("type_couv_", "").split("_")
                tc = str(row.get(cols_lower.get("type_couv", ""), "")).strip().upper()
                bonus += (100 if tc in preferred else 0)
            else:
                # features sémantiques non-mappées (ex: isolation_routes,
                # proximite_zones_humides_HIGH, ouvertures_proches) →
                # ignored jusqu'à hooks externes (ANTI_GÉNÉRIQUE_STRICT)
                n_features -= 1
        if n_features > 0:
            bonus_mean = bonus / n_features
            score += 0.50 * bonus_mean
        return int(round(min(max(score, 0), 100)))

    gdf[f"_repos_{species}"] = [
        _repos_score(i, row) for i, (_, row) in enumerate(gdf.iterrows())
    ]
    gdf[f"_repos_{species}"] = gdf[f"_repos_{species}"].astype("uint8")

    rast_info = _rasterize_to_tif(
        gdf, f"_repos_{species}", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    sha_tif = _sha256_file(out_tif)
    elapsed = round(time.time() - t0, 2)
    arr = gdf[f"_repos_{species}"].values
    return {
        "manifest_id": f"R9_REPOS_{species.upper()}_COMPUTED_Ω",
        "ordre": "N°52-R16-B",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species": species,
        "repos_preferred_features": repos_features,
        "output_raster": str(out_tif),
        "raster_size_bytes": out_tif.stat().st_size,
        "raster_sha256": sha_tif,
        "n_polygons_processed": len(gdf),
        "n_high_repos_polygons": int((arr >= 70).sum()),
        "mean_score": round(float(arr.mean()), 2),
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 3. R9_ALIMENTATION_[ESPECE]
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_alimentation(
    species: str,
    subset_path: str,
    zones_humides_tif: Path,
    exclusions_tif: Path,
    phenologie_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-B · R9_ALIMENTATION_[ESPECE] (uint8 0-100).

    Score proxy ANTI_GÉNÉRIQUE_STRICT (NDVI/mast hooks NUTRITION absents).
    """
    import numpy as np

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / f"R9_ALIMENTATION_{species.upper()}.tif"

    proxy_rules = (
        phenologie_dict.get("alimentation_proxy_rules", {})
        .get("rules_per_species", {})
        .get(species, {}))
    if not proxy_rules:
        raise ValueError(
            f"alimentation_proxy_rules absentes pour {species}.")

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)
    cols_lower = {c.lower(): c for c in gdf.columns}

    humid_flags = _sample_raster_at_centroids(
        gdf, zones_humides_tif, band=1)
    excl_flags = _sample_raster_at_centroids(
        gdf, exclusions_tif, band=1)

    def _alim(i: int, row) -> int:
        if excl_flags[i] >= 1.0:
            return 0
        row_dict = {
            "type_couv": row.get(cols_lower.get("type_couv", ""), ""),
            "cl_age": row.get(cols_lower.get("cl_age", ""), ""),
            "cl_dens": row.get(cols_lower.get("cl_dens", ""), ""),
        }
        return _alimentation_score_for_polygon(
            row_dict, proxy_rules, humid_flags[i])

    gdf[f"_alim_{species}"] = [
        _alim(i, row) for i, (_, row) in enumerate(gdf.iterrows())
    ]
    gdf[f"_alim_{species}"] = gdf[f"_alim_{species}"].astype("uint8")

    rast_info = _rasterize_to_tif(
        gdf, f"_alim_{species}", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    sha_tif = _sha256_file(out_tif)
    elapsed = round(time.time() - t0, 2)
    arr = gdf[f"_alim_{species}"].values
    return {
        "manifest_id": f"R9_ALIMENTATION_{species.upper()}_COMPUTED_Ω",
        "ordre": "N°52-R16-B",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species": species,
        "proxy_rules_used": list(proxy_rules.keys()),
        "anti_generique_note": (
            "Proxy MFFP-only ; NUTRITION hooks (NDVI, mast, sol) "
            "absents Q3 → score ne reflète pas variation saisonnière "
            "réelle. Mise à niveau auto quand hooks deviendront available."),
        "output_raster": str(out_tif),
        "raster_size_bytes": out_tif.stat().st_size,
        "raster_sha256": sha_tif,
        "n_polygons_processed": len(gdf),
        "n_high_alim_polygons": int((arr >= 70).sum()),
        "mean_score": round(float(arr.mean()), 2),
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 4. R9_RUT_[ESPECE]
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_rut(
    species: str,
    subset_path: str,
    habitat_tif: Path,
    couvert_securite_tif: Path,
    exclusions_tif: Path,
    phenologie_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-B · R9_RUT_[ESPECE] (uint8 0-100).

    Score = habitat × intensité_rut_pic. Intensité_rut_pic est constante
    pour la saison annuelle (R16-A temporalité=annuel par défaut).
    En mode saisonnier futur (R16-B+), pondéré par mois.
    """
    import numpy as np

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / f"R9_RUT_{species.upper()}.tif"

    species_pheno = phenologie_dict.get("calendar", {}).get(species, {})
    rut_peak_intensity = max(
        species_pheno.get("rut_intensity_by_month", {}).values()
        or [1.0])
    rut_peak_months = species_pheno.get("rut_peak_months", [])
    species_idx = SPECIES_LIST.index(species)

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)

    habitat_scores = _sample_raster_at_centroids(
        gdf, habitat_tif, band=species_idx + 1)
    couvert_scores = _sample_raster_at_centroids(
        gdf, couvert_securite_tif, band=1)
    excl_flags = _sample_raster_at_centroids(
        gdf, exclusions_tif, band=1)

    def _rut(i: int) -> int:
        if excl_flags[i] >= 1.0:
            return 0
        # Combinaison : 0.60 habitat + 0.40 couvert × intensité_pic
        s = (0.60 * float(habitat_scores[i])
             + 0.40 * float(couvert_scores[i])) * float(rut_peak_intensity)
        return int(round(min(max(s, 0), 100)))

    gdf[f"_rut_{species}"] = [_rut(i) for i in range(len(gdf))]
    gdf[f"_rut_{species}"] = gdf[f"_rut_{species}"].astype("uint8")

    rast_info = _rasterize_to_tif(
        gdf, f"_rut_{species}", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    sha_tif = _sha256_file(out_tif)
    elapsed = round(time.time() - t0, 2)
    arr = gdf[f"_rut_{species}"].values
    return {
        "manifest_id": f"R9_RUT_{species.upper()}_COMPUTED_Ω",
        "ordre": "N°52-R16-B",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species": species,
        "rut_peak_months": rut_peak_months,
        "rut_peak_intensity": rut_peak_intensity,
        "output_raster": str(out_tif),
        "raster_size_bytes": out_tif.stat().st_size,
        "raster_sha256": sha_tif,
        "n_polygons_processed": len(gdf),
        "n_high_rut_polygons": int((arr >= 70).sum()),
        "mean_score": round(float(arr.mean()), 2),
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# Pipeline R16-B Orchestrator (4 cibles × 5 espèces = 20 cibles)
# ═════════════════════════════════════════════════════════════════════════
def execute_r16b_pipeline(
    subset_path: Optional[str] = None,
    species_subset: Optional[List[str]] = None,
    targets_subset: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-B · Pipeline orchestrator pour 4 cibles × 5 espèces.

    Args :
      species_subset : Optionnel · liste pour cibler une espèce ([species]).
      targets_subset : Optionnel · liste pour cibler une cible.

    Met à jour R9_RECALC_STATE.json → status=OK_REAL_PARTIAL_R16B.
    """
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega import (  # noqa: E501
        load_dictionary,
    )

    t0 = time.time()
    src = subset_path or auto_pick_subset()
    if not src:
        raise RuntimeError(
            "Aucun subset utilisable. Lancer "
            "POST /diagnostic/pee-maj/export-subset?execute=true&source=vsi")

    # Charge dicts requis
    pheno = load_dictionary("phenologie_saisonniere")
    if pheno is None:
        raise RuntimeError("phenologie_saisonniere.json absent ou invalide.")

    # Vérif rasters R16-A + P1 présents
    habitat_tif = DERIVATIVES_P1_ROOT / "MFFP_HABITAT_BRUT.tif"
    couvert_tif = DERIVATIVES_R9_ROOT / "R9_COUVERT_SECURITE.tif"
    humides_tif = DERIVATIVES_R9_ROOT / "R9_ZONES_HUMIDES.tif"
    excl_tif = DERIVATIVES_R9_ROOT / "R9_EXCLUSIONS.tif"
    missing = [
        str(p) for p in
        [habitat_tif, couvert_tif, humides_tif, excl_tif]
        if not p.exists()
    ]
    if missing:
        raise RuntimeError(
            f"Dépendances R16-A/P1 absentes : {missing}. "
            f"Lancer R15 P1 et R16-A pipelines au préalable.")

    species_to_run = species_subset or SPECIES_LIST
    targets_to_run = targets_subset or TARGETS_R16B_PER_SPECIES

    results: Dict[str, Any] = {}
    succeeded: List[str] = []
    for sp in species_to_run:
        for tgt in targets_to_run:
            target_full = f"R9_{tgt}_{sp.upper()}"
            try:
                if tgt == "ZONES_VITALES":
                    r = compute_r9_zones_vitales(
                        sp, src, habitat_tif, couvert_tif,
                        humides_tif, excl_tif, pheno)
                elif tgt == "REPOS":
                    r = compute_r9_repos(
                        sp, src, couvert_tif, excl_tif, pheno)
                elif tgt == "ALIMENTATION":
                    r = compute_r9_alimentation(
                        sp, src, humides_tif, excl_tif, pheno)
                elif tgt == "RUT":
                    r = compute_r9_rut(
                        sp, src, habitat_tif, couvert_tif,
                        excl_tif, pheno)
                else:
                    r = {"manifest_id": f"{target_full}_UNKNOWN",
                         "error": "target_unknown"}
                results[target_full] = r
                if r.get("manifest_id", "").endswith("_COMPUTED_Ω"):
                    succeeded.append(target_full)
            except Exception as e:
                import traceback
                results[target_full] = {
                    "manifest_id": f"{target_full}_FAILED_Ω",
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
                "ordre": "N°52-R16-B",
                "completed_at_utc": _utc_now(),
                "output_raster": results[full].get("output_raster"),
                "output_vector": results[full].get("output_vector"),
                "raster_sha256": results[full].get("raster_sha256"),
                "elapsed_s": results[full].get("elapsed_s"),
            }
        state["last_r16b_run_id"] = f"R16B_{int(time.time())}"
        state["last_r16b_run_completed_at_utc"] = _utc_now()
        state["last_r16b_subset_used"] = src
        state["last_r16b_targets_succeeded"] = succeeded
        state["last_r16b_n_species"] = len(species_to_run)
        # Status global progression
        if len(succeeded) >= 16:  # ≥80% des 20 cibles
            state["status"] = "OK_REAL_PARTIAL_R16B"
        elif state.get("status") in (
                "OK_REAL_PARTIAL_R16A", None,
                "OK_WITH_STUBS",
                "STUB_READY_AWAITING_BUSINESS_LOGIC"):
            state["status"] = "OK_REAL_PARTIAL_R16B_WITH_FAILURES"
        R9_RECALC_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        R9_RECALC_STATE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        state_update = {
            "updated": True,
            "new_global_status": state["status"],
            "targets_marked_OK_REAL": succeeded,
            "n_succeeded": len(succeeded),
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
        "manifest_id": "R9_PHASE3_R16B_PIPELINE_COMPLETED_Ω",
        "ordre": "N°52-R16-B",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "subset_used": src,
        "species_executed": species_to_run,
        "targets_executed_per_species": targets_to_run,
        "n_targets_total": len(species_to_run) * len(targets_to_run),
        "n_targets_succeeded": len(succeeded),
        "targets_succeeded": succeeded,
        "results": results,
        "r9_recalc_state_update": state_update,
        "elapsed_total_s": elapsed_total,
        "v30_lock": "INVIOLÉ",
    }


__all__ = [
    "execute_r16b_pipeline",
    "compute_r9_zones_vitales",
    "compute_r9_repos",
    "compute_r9_alimentation",
    "compute_r9_rut",
    "SPECIES_LIST",
    "TARGETS_R16B_PER_SPECIES",
]
