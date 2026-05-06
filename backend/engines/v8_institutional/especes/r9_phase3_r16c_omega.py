"""
r9_phase3_r16c_omega.py — ORDRE N°52-R16-C · CONNECTIVITY (5 espèces + multi)
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Implémentation R16-C des 16 cibles CONNECTIVITY :
  · R9_CORRIDORS_[ESPECE]         × 5 (potential score cost-surface inversé)
  · R9_ZONES_PASSAGE_[ESPECE]     × 5 (liens zones_vitales HIGH + corridors)
  · R9_HOTSPOTS_[ESPECE]          × 5 (top 5 % scores combinés)
  · R9_CORRIDORS_MULTI_ESPECES    × 1 (fusion pondérée 5 espèces + hydrologie)

Doctrine :
  · Lit subset + rasters R8/R16-A/R16-B (FUSION ADD-ONLY).
  · Applique règles `connectivity_rules.json` (VALIDÉ R16-C).
  · Produit GeoTIFF uint8 + GPKG haute valeur + SHA-256.
  · Applique R9_EXCLUSIONS (multiplie score par (1 - excluded)).
  · MAJ R9_RECALC_STATE.json → OK_REAL_PARTIAL_R16C.

ANTI_GÉNÉRIQUE_STRICT :
  · Aucune simulation. Corridors = formule score composite ∈ [0, 100].
  · Fusion multi-espèces pondérée par masse corporelle (écologie landscape).
  · Hooks IA_VISION/DONNEES_CHASSEUR : registry-aware skip si absent.

FUSION ADD-ONLY · Réutilise helpers P0 + R16-A/B.
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

logger = logging.getLogger("r9_phase3_r16c_omega")

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

TARGETS_R16C_PER_SPECIES = ["CORRIDORS", "ZONES_PASSAGE", "HOTSPOTS"]


# ═════════════════════════════════════════════════════════════════════════
# 1. R9_CORRIDORS_[ESPECE] — corridor potential score
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_corridors_species(
    species: str,
    subset_path: str,
    habitat_tif: Path,
    couvert_securite_tif: Path,
    fragmentation_tif: Path,
    exclusions_tif: Path,
    connectivity_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-C · Corridor potential uint8 0-100.

    Score composite selon `connectivity_rules.corridors_rules` :
      0.40 habitat_species + 0.25 couvert_securite +
      0.20 (100 - frag*100) + 0.15 (100 - excl*100)
    · exclusion_penalty_factor=0 → pixel exclu → score=0.
    """
    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / f"R9_CORRIDORS_{species.upper()}.tif"
    out_gpkg = out_root / f"R9_CORRIDORS_{species.upper()}.gpkg"

    rules = connectivity_dict.get("corridors_rules", {})
    w = rules.get("score_formula_weights", {})
    w_h = float(w.get("habitat_brut_per_species", 0.40))
    w_c = float(w.get("couvert_securite", 0.25))
    w_f = float(w.get("inverse_fragmentation", 0.20))
    w_e = float(w.get("inverse_exclusion", 0.15))

    species_idx = SPECIES_LIST.index(species)
    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)

    habitat_vals = _sample_raster_at_centroids(
        gdf, habitat_tif, band=species_idx + 1)
    couvert_vals = _sample_raster_at_centroids(
        gdf, couvert_securite_tif, band=1)
    frag_vals = _sample_raster_at_centroids(
        gdf, fragmentation_tif, band=1, fallback_value=0.0)
    excl_vals = _sample_raster_at_centroids(
        gdf, exclusions_tif, band=1)

    # Pour corridor : exclusion applique un facteur 0 (pixel excluded → 0)
    scores = []
    for i in range(len(gdf)):
        if excl_vals[i] >= 1.0:
            scores.append(0)
            continue
        # Fragmentation peut être 0-1 ou 0-100 selon le raster.
        # MFFP_FRAGMENTATION_INDEX est typiquement 0-1 (Dickson 2017).
        frag_norm = min(max(float(frag_vals[i]), 0.0), 1.0)
        inv_frag = 100.0 * (1.0 - frag_norm)
        inv_excl = 100.0 * (1.0 - float(excl_vals[i]))
        s = (w_h * float(habitat_vals[i])
             + w_c * float(couvert_vals[i])
             + w_f * inv_frag
             + w_e * inv_excl)
        scores.append(int(round(min(max(s, 0), 100))))
    gdf[f"_corr_{species}"] = scores
    gdf[f"_corr_{species}"] = gdf[f"_corr_{species}"].astype("uint8")

    rast_info = _rasterize_to_tif(
        gdf, f"_corr_{species}", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    # Export GPKG : polygones haute valeur corridor ≥ 60
    import geopandas as gpd
    high = gdf[gdf[f"_corr_{species}"] >= 60].copy()
    high = high.rename(columns={f"_corr_{species}": "corridor_score"})
    if len(high) > 0:
        high[["corridor_score", "geometry"]].to_file(
            str(out_gpkg), driver="GPKG",
            layer=f"corridors_{species}")
    else:
        empty = gpd.GeoDataFrame(
            {"corridor_score": [0], "geometry": [gdf.geometry.iloc[0]]},
            crs=gdf.crs)
        empty.to_file(
            str(out_gpkg), driver="GPKG",
            layer=f"corridors_{species}_empty")

    sha_tif = _sha256_file(out_tif)
    sha_gpkg = _sha256_file(out_gpkg) if out_gpkg.exists() else None
    import numpy as np
    arr = np.array(scores, dtype="uint8")
    elapsed = round(time.time() - t0, 2)
    return {
        "manifest_id": f"R9_CORRIDORS_{species.upper()}_COMPUTED_Ω",
        "ordre": "N°52-R16-C",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species": species,
        "weights_applied": {
            "habitat": w_h, "couvert": w_c,
            "inv_frag": w_f, "inv_excl": w_e},
        "output_raster": str(out_tif),
        "output_vector": str(out_gpkg),
        "raster_size_bytes": out_tif.stat().st_size,
        "vector_size_bytes": (out_gpkg.stat().st_size
                              if out_gpkg.exists() else 0),
        "raster_sha256": sha_tif,
        "vector_sha256": sha_gpkg,
        "n_polygons_processed": len(gdf),
        "n_high_corridor_polygons": int((arr >= 60).sum()),
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
# 2. R9_ZONES_PASSAGE_[ESPECE] — buffers zones vitales
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_zones_passage_species(
    species: str,
    subset_path: str,
    zones_vitales_tif: Path,
    corridors_tif: Path,
    exclusions_tif: Path,
    connectivity_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-C · Zones de passage uint8 0-100.

    score = min(zones_vitales*0.6 + corridor_score*0.4, 100)
    Pixel exclu → 0. Pixel où zones_vitales<seuil ET corridor<seuil → 0.
    """
    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / f"R9_ZONES_PASSAGE_{species.upper()}.tif"
    out_gpkg = out_root / f"R9_ZONES_PASSAGE_{species.upper()}.gpkg"

    rules = connectivity_dict.get("zones_passage_rules", {})
    seuil_vitales = float(rules.get("seuil_zones_vitales_high", 70))
    seuil_corridor = float(rules.get("buffer_corridor_score_min", 50))

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)

    vitales_vals = _sample_raster_at_centroids(
        gdf, zones_vitales_tif, band=1)
    corridor_vals = _sample_raster_at_centroids(
        gdf, corridors_tif, band=1)
    excl_vals = _sample_raster_at_centroids(
        gdf, exclusions_tif, band=1)

    scores = []
    for i in range(len(gdf)):
        if excl_vals[i] >= 1.0:
            scores.append(0)
            continue
        v = float(vitales_vals[i])
        c = float(corridor_vals[i])
        # Zone de passage candidate uniquement si vitales OU corridor au-dessus
        if v < seuil_vitales and c < seuil_corridor:
            scores.append(0)
            continue
        s = 0.6 * v + 0.4 * c
        scores.append(int(round(min(max(s, 0), 100))))
    gdf[f"_pass_{species}"] = scores
    gdf[f"_pass_{species}"] = gdf[f"_pass_{species}"].astype("uint8")

    rast_info = _rasterize_to_tif(
        gdf, f"_pass_{species}", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    import geopandas as gpd
    import numpy as np
    high = gdf[gdf[f"_pass_{species}"] >= 60].copy()
    high = high.rename(columns={f"_pass_{species}": "passage_score"})
    if len(high) > 0:
        high[["passage_score", "geometry"]].to_file(
            str(out_gpkg), driver="GPKG",
            layer=f"passage_{species}")
    else:
        empty = gpd.GeoDataFrame(
            {"passage_score": [0], "geometry": [gdf.geometry.iloc[0]]},
            crs=gdf.crs)
        empty.to_file(
            str(out_gpkg), driver="GPKG",
            layer=f"passage_{species}_empty")

    sha_tif = _sha256_file(out_tif)
    sha_gpkg = _sha256_file(out_gpkg) if out_gpkg.exists() else None
    arr = np.array(scores, dtype="uint8")
    elapsed = round(time.time() - t0, 2)
    return {
        "manifest_id": f"R9_ZONES_PASSAGE_{species.upper()}_COMPUTED_Ω",
        "ordre": "N°52-R16-C",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species": species,
        "thresholds_applied": {
            "seuil_vitales": seuil_vitales,
            "seuil_corridor": seuil_corridor},
        "output_raster": str(out_tif),
        "output_vector": str(out_gpkg),
        "raster_size_bytes": out_tif.stat().st_size,
        "vector_size_bytes": (out_gpkg.stat().st_size
                              if out_gpkg.exists() else 0),
        "raster_sha256": sha_tif,
        "vector_sha256": sha_gpkg,
        "n_polygons_processed": len(gdf),
        "n_high_passage_polygons": int((arr >= 60).sum()),
        "mean_score": round(float(arr.mean()), 2),
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 3. R9_HOTSPOTS_[ESPECE] — top percentile
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_hotspots_species(
    species: str,
    subset_path: str,
    habitat_tif: Path,
    productivity_tif: Path,
    structure_tif: Path,
    continuity_tif: Path,
    couvert_securite_tif: Path,
    exclusions_tif: Path,
    connectivity_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-C · Hotspots uint8 binaire 0/1 + GPKG avec score.

    Top-percentile sur score combiné :
      0.35 habitat + 0.20 productivity + 0.15 structure +
      0.15 continuity + 0.15 couvert
    """
    import numpy as np
    import geopandas as gpd

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / f"R9_HOTSPOTS_{species.upper()}.tif"
    out_gpkg = out_root / f"R9_HOTSPOTS_{species.upper()}.gpkg"

    rules = connectivity_dict.get("hotspots_rules", {})
    w = rules.get("score_formula_weights", {})
    w_h = float(w.get("habitat_brut_per_species", 0.35))
    w_p = float(w.get("productivity", 0.20))
    w_s = float(w.get("structure", 0.15))
    w_c = float(w.get("continuity", 0.15))
    w_cv = float(w.get("couvert_securite", 0.15))
    top_pct = float(rules.get("top_percentile", 95))

    species_idx = SPECIES_LIST.index(species)
    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)

    habitat = _sample_raster_at_centroids(
        gdf, habitat_tif, band=species_idx + 1)
    # Productivity est float32 m³/ha (domain 0-500) → normalise à 0-100
    prod = _sample_raster_at_centroids(
        gdf, productivity_tif, band=1)
    prod_norm = [
        min(float(p) / 5.0, 100.0) if p is not None else 0.0
        for p in prod
    ]
    # Structure est uint8 classe 1-7 → normalise à 0-100 (classes moins
    # fragmentées = valeur supérieure)
    struct = _sample_raster_at_centroids(
        gdf, structure_tif, band=1)
    struct_norm = [
        float(s) * (100.0 / 7.0) if s is not None else 0.0
        for s in struct
    ]
    # Continuity est uint8 classe 1-5 → normalise 0-100 avec pondération
    # écologique (classe 4 = vieilles forêts = top, classe 5 = perturbé)
    cont = _sample_raster_at_centroids(
        gdf, continuity_tif, band=1)
    continuity_norm_map = {1: 25, 2: 50, 3: 75, 4: 100, 5: 10}
    cont_norm = [
        float(continuity_norm_map.get(int(c), 0))
        if c is not None else 0.0
        for c in cont
    ]
    couv = _sample_raster_at_centroids(
        gdf, couvert_securite_tif, band=1)
    excl = _sample_raster_at_centroids(
        gdf, exclusions_tif, band=1)

    scores = []
    for i in range(len(gdf)):
        if excl[i] >= 1.0:
            scores.append(0.0)
            continue
        s = (w_h * float(habitat[i])
             + w_p * float(prod_norm[i])
             + w_s * float(struct_norm[i])
             + w_c * float(cont_norm[i])
             + w_cv * float(couv[i]))
        scores.append(min(max(s, 0), 100))

    # Percentile top_pct → binary flag
    scores_arr = np.array(scores, dtype="float32")
    if scores_arr[scores_arr > 0].size > 0:
        threshold_value = float(np.percentile(
            scores_arr[scores_arr > 0], top_pct))
    else:
        threshold_value = 0.0
    hotspot_binary = (scores_arr >= threshold_value).astype("uint8")
    # Si threshold=0, tout polygone à 0 serait flagué → garde seulement > 0
    if threshold_value <= 0:
        hotspot_binary = (scores_arr > 0).astype("uint8")

    gdf[f"_hot_{species}"] = hotspot_binary

    rast_info = _rasterize_to_tif(
        gdf, f"_hot_{species}", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    # GPKG : polygones hotspot avec score (pour cartographie)
    gdf["_hot_score"] = scores_arr.astype("float32")
    hs = gdf[gdf[f"_hot_{species}"] == 1].copy()
    hs = hs.rename(
        columns={"_hot_score": "hotspot_score",
                 f"_hot_{species}": "is_hotspot"})
    if len(hs) > 0:
        hs[["hotspot_score", "is_hotspot", "geometry"]].to_file(
            str(out_gpkg), driver="GPKG",
            layer=f"hotspots_{species}")
    else:
        empty = gpd.GeoDataFrame(
            {"hotspot_score": [0.0], "is_hotspot": [0],
             "geometry": [gdf.geometry.iloc[0]]},
            crs=gdf.crs)
        empty.to_file(
            str(out_gpkg), driver="GPKG",
            layer=f"hotspots_{species}_empty")

    sha_tif = _sha256_file(out_tif)
    sha_gpkg = _sha256_file(out_gpkg) if out_gpkg.exists() else None
    elapsed = round(time.time() - t0, 2)
    n_hot = int(hotspot_binary.sum())
    return {
        "manifest_id": f"R9_HOTSPOTS_{species.upper()}_COMPUTED_Ω",
        "ordre": "N°52-R16-C",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species": species,
        "top_percentile": top_pct,
        "threshold_value_score": round(threshold_value, 2),
        "weights_applied": {
            "habitat": w_h, "productivity": w_p, "structure": w_s,
            "continuity": w_c, "couvert": w_cv},
        "output_raster": str(out_tif),
        "output_vector": str(out_gpkg),
        "raster_size_bytes": out_tif.stat().st_size,
        "vector_size_bytes": (out_gpkg.stat().st_size
                              if out_gpkg.exists() else 0),
        "raster_sha256": sha_tif,
        "vector_sha256": sha_gpkg,
        "n_polygons_processed": len(gdf),
        "n_hotspots": n_hot,
        "hotspot_pct": round(100 * n_hot / max(len(gdf), 1), 2),
        "mean_hotspot_score": round(
            float(scores_arr[hotspot_binary == 1].mean())
            if n_hot else 0.0, 2),
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 4. R9_CORRIDORS_MULTI_ESPECES — fusion pondérée
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_corridors_multi_especes(
    subset_path: str,
    corridors_per_species_tifs: Dict[str, Path],
    zones_humides_tif: Path,
    exclusions_tif: Path,
    connectivity_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
    external_sources_probe: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-C · Corridors multi-espèces (fusion).

    score = Σ(species_weight × corridor_score_species)
            + hydrologie_bonus(10) si pixel proche zone humide
    Applique exclusions.
    """
    import numpy as np
    import geopandas as gpd

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / "R9_CORRIDORS_MULTI_ESPECES.tif"
    out_gpkg = out_root / "R9_CORRIDORS_MULTI_ESPECES.gpkg"

    rules = connectivity_dict.get("corridors_multi_especes_rules", {})
    species_weights = rules.get("species_weights_by_mass", {})
    hydro_bonus = float(rules.get("hydrologie_bonus_pts", 10))

    # Charge subset pour geometry + centroides
    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)

    # Sample tous les corridors de chaque espèce
    species_samples = {}
    for sp, tif_path in corridors_per_species_tifs.items():
        if tif_path and Path(tif_path).exists():
            species_samples[sp] = _sample_raster_at_centroids(
                gdf, Path(tif_path), band=1)
        else:
            logger.warning(
                "R16C_CORR_MULTI_MISSING_SPECIES sp=%s path=%s",
                sp, tif_path)

    humid_vals = _sample_raster_at_centroids(
        gdf, zones_humides_tif, band=1)
    excl_vals = _sample_raster_at_centroids(
        gdf, exclusions_tif, band=1)

    # Normalisation des poids sur espèces présentes
    present_weights = {
        sp: float(species_weights.get(sp, 0))
        for sp in species_samples.keys()
    }
    total_w = sum(present_weights.values()) or 1.0
    present_weights = {sp: w / total_w for sp, w in present_weights.items()}

    scores = []
    for i in range(len(gdf)):
        if excl_vals[i] >= 1.0:
            scores.append(0)
            continue
        s = 0.0
        for sp, vals in species_samples.items():
            s += present_weights[sp] * float(vals[i])
        if humid_vals[i] >= 1.0:
            s += hydro_bonus
        scores.append(int(round(min(max(s, 0), 100))))

    gdf["_corr_multi"] = scores
    gdf["_corr_multi"] = gdf["_corr_multi"].astype("uint8")

    rast_info = _rasterize_to_tif(
        gdf, "_corr_multi", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    arr = np.array(scores, dtype="uint8")
    high = gdf[gdf["_corr_multi"] >= 60].copy()
    high = high.rename(columns={"_corr_multi": "corridor_multi_score"})
    if len(high) > 0:
        high[["corridor_multi_score", "geometry"]].to_file(
            str(out_gpkg), driver="GPKG",
            layer="corridors_multi")
    else:
        empty = gpd.GeoDataFrame(
            {"corridor_multi_score": [0],
             "geometry": [gdf.geometry.iloc[0]]},
            crs=gdf.crs)
        empty.to_file(
            str(out_gpkg), driver="GPKG",
            layer="corridors_multi_empty")

    sha_tif = _sha256_file(out_tif)
    sha_gpkg = _sha256_file(out_gpkg) if out_gpkg.exists() else None
    elapsed = round(time.time() - t0, 2)

    external_sources_status = external_sources_probe or {}

    return {
        "manifest_id": "R9_CORRIDORS_MULTI_ESPECES_COMPUTED_Ω",
        "ordre": "N°52-R16-C",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species_fused": list(species_samples.keys()),
        "species_weights_normalized": present_weights,
        "hydrologie_bonus_pts": hydro_bonus,
        "output_raster": str(out_tif),
        "output_vector": str(out_gpkg),
        "raster_size_bytes": out_tif.stat().st_size,
        "vector_size_bytes": (out_gpkg.stat().st_size
                              if out_gpkg.exists() else 0),
        "raster_sha256": sha_tif,
        "vector_sha256": sha_gpkg,
        "n_polygons_processed": len(gdf),
        "n_high_multi_polygons": int((arr >= 60).sum()),
        "mean_score": round(float(arr.mean()), 2),
        "external_sources_status": external_sources_status,
        "anti_generique_note": (
            "IA_VISION/DONNEES_CHASSEUR hooks consultés via registry. "
            "Si absents (Q3-Q4 attendu), leur contribution est omise "
            "— pas de simulation."),
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# Pipeline R16-C Orchestrator
# ═════════════════════════════════════════════════════════════════════════
def execute_r16c_pipeline(
    subset_path: Optional[str] = None,
    species_subset: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Pipeline R16-C : 3 cibles × 5 espèces + 1 fusion multi-espèces."""
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega import (  # noqa: E501
        load_dictionary,
    )
    from engines.v8_institutional.especes.r9_phase3_orchestrator_omega import (  # noqa: E501
        probe_territoire_ultime_hooks,
    )

    t0 = time.time()
    src = subset_path or auto_pick_subset()
    if not src:
        raise RuntimeError(
            "Aucun subset utilisable. Lancer export-subset VSI.")

    connectivity = load_dictionary("connectivity_rules")
    regles = load_dictionary("regles_territoires_canonical")
    if connectivity is None or regles is None:
        raise RuntimeError(
            "Dictionnaire connectivity_rules ou regles_territoires absent.")

    # Dépendances rasters
    habitat = DERIVATIVES_P1_ROOT / "MFFP_HABITAT_BRUT.tif"
    couvert = DERIVATIVES_R9_ROOT / "R9_COUVERT_SECURITE.tif"
    humides = DERIVATIVES_R9_ROOT / "R9_ZONES_HUMIDES.tif"
    excl = DERIVATIVES_R9_ROOT / "R9_EXCLUSIONS.tif"
    frag = DERIVATIVES_P1_ROOT / "MFFP_FRAGMENTATION_INDEX.tif"
    productivity = DERIVATIVES_P1_ROOT / "MFFP_PRODUCTIVITE.tif"
    structure = DERIVATIVES_P1_ROOT / "MFFP_STRUCTURE.tif"
    continuity = DERIVATIVES_P1_ROOT / "MFFP_CONTINUITE.tif"

    missing = [
        str(p) for p in [habitat, couvert, humides, excl, frag,
                          productivity, structure, continuity]
        if not p.exists()
    ]
    if missing:
        raise RuntimeError(
            f"Dépendances absentes : {missing}. "
            f"Lancer R15 P1 + R16-A au préalable.")

    hooks_probe = probe_territoire_ultime_hooks(regles)

    species_to_run = species_subset or SPECIES_LIST

    results: Dict[str, Any] = {}
    succeeded: List[str] = []

    # 1. CORRIDORS × 5
    for sp in species_to_run:
        target_full = f"R9_CORRIDORS_{sp.upper()}"
        try:
            r = compute_r9_corridors_species(
                sp, src, habitat, couvert, frag, excl, connectivity)
            results[target_full] = r
            succeeded.append(target_full)
        except Exception as e:
            import traceback
            results[target_full] = {
                "manifest_id": f"{target_full}_FAILED_Ω",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            }

    # 2. ZONES_PASSAGE × 5 (dépend corridors et zones_vitales R16-B)
    for sp in species_to_run:
        target_full = f"R9_ZONES_PASSAGE_{sp.upper()}"
        vit = DERIVATIVES_R9_ROOT / f"R9_ZONES_VITALES_{sp.upper()}.tif"
        corr = DERIVATIVES_R9_ROOT / f"R9_CORRIDORS_{sp.upper()}.tif"
        if not vit.exists() or not corr.exists():
            results[target_full] = {
                "manifest_id": f"{target_full}_SKIPPED_Ω",
                "reason": "DEPENDENCY_ABSENT",
                "missing": [
                    str(p) for p in [vit, corr] if not p.exists()
                ],
            }
            continue
        try:
            r = compute_r9_zones_passage_species(
                sp, src, vit, corr, excl, connectivity)
            results[target_full] = r
            succeeded.append(target_full)
        except Exception as e:
            import traceback
            results[target_full] = {
                "manifest_id": f"{target_full}_FAILED_Ω",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            }

    # 3. HOTSPOTS × 5
    for sp in species_to_run:
        target_full = f"R9_HOTSPOTS_{sp.upper()}"
        try:
            r = compute_r9_hotspots_species(
                sp, src, habitat, productivity, structure,
                continuity, couvert, excl, connectivity)
            results[target_full] = r
            succeeded.append(target_full)
        except Exception as e:
            import traceback
            results[target_full] = {
                "manifest_id": f"{target_full}_FAILED_Ω",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            }

    # 4. CORRIDORS_MULTI_ESPECES
    try:
        corr_tifs = {
            sp: DERIVATIVES_R9_ROOT / f"R9_CORRIDORS_{sp.upper()}.tif"
            for sp in species_to_run
        }
        r = compute_r9_corridors_multi_especes(
            src, corr_tifs, humides, excl, connectivity,
            external_sources_probe=hooks_probe)
        results["R9_CORRIDORS_MULTI_ESPECES"] = r
        succeeded.append("R9_CORRIDORS_MULTI_ESPECES")
    except Exception as e:
        import traceback
        results["R9_CORRIDORS_MULTI_ESPECES"] = {
            "manifest_id": "R9_CORRIDORS_MULTI_ESPECES_FAILED_Ω",
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
                "ordre": "N°52-R16-C",
                "completed_at_utc": _utc_now(),
                "output_raster": results[full].get("output_raster"),
                "output_vector": results[full].get("output_vector"),
                "raster_sha256": results[full].get("raster_sha256"),
                "elapsed_s": results[full].get("elapsed_s"),
            }
        state["last_r16c_run_id"] = f"R16C_{int(time.time())}"
        state["last_r16c_run_completed_at_utc"] = _utc_now()
        state["last_r16c_subset_used"] = src
        state["last_r16c_targets_succeeded"] = succeeded
        state["last_r16c_external_sources_status"] = hooks_probe
        if len(succeeded) >= 13:  # >=80% des 16 cibles
            state["status"] = "OK_REAL_PARTIAL_R16C"
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
        "manifest_id": "R9_PHASE3_R16C_PIPELINE_COMPLETED_Ω",
        "ordre": "N°52-R16-C",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "subset_used": src,
        "species_executed": species_to_run,
        "n_targets_total": len(species_to_run) * 3 + 1,
        "n_targets_succeeded": len(succeeded),
        "targets_succeeded": succeeded,
        "results": results,
        "territoire_ultime_hooks_status": hooks_probe,
        "r9_recalc_state_update": state_update,
        "elapsed_total_s": elapsed_total,
        "v30_lock": "INVIOLÉ",
    }


__all__ = [
    "execute_r16c_pipeline",
    "compute_r9_corridors_species",
    "compute_r9_zones_passage_species",
    "compute_r9_hotspots_species",
    "compute_r9_corridors_multi_especes",
    "TARGETS_R16C_PER_SPECIES",
]
