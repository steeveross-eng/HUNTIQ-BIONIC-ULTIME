"""
r9_phase3_orchestrator_omega.py — ORDRE N°52-R16-A · R9 BUSINESS LOGIC
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Implémentation R16-A (fondations R9) — 4 targets :
  · R9_SIGNATURES_TERRAIN  (signature unique 8-tuple par polygone)
  · R9_EXCLUSIONS          (zones interdites pentes/drainage/fragmentation)
  · R9_ZONES_HUMIDES       (cl_drai 5/6 OU type_eco humide)
  · R9_COUVERT_SECURITE    (densité × hauteur × type_couv)

Doctrine :
  · Lit le subset Bas-Saint-Laurent (auto-pick par mtime).
  · Charge les 4 dictionnaires VALIDÉS R16-A.
  · Probe les 6 hooks territoire_ultime (registry-aware).
  · Persiste artefacts (raster GeoTIFF + GPKG + SHA-256) sur
    /app/backend/data/gis_archive/derivatives_r9/.
  · Met à jour R9_RECALC_STATE.json → status=OK_REAL pour les 4 targets.
  · ANTI_GÉNÉRIQUE_STRICT : aucune fabrication. Sources externes absentes
    → skip_with_log. Toutes les sorties tracables au subset MFFP réel.

FUSION ADD-ONLY — Réutilise les helpers P0/P1.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import logging
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("r9_phase3_orchestrator_omega")

# Réutilisation FUSION ADD-ONLY
from engines.v8_institutional.especes.mffp_phase3_p0_omega import (
    TARGET_EPSG, NODATA_VALUE_UINT8, NODATA_VALUE_FLOAT32,
    _utc_now, _sha256_file, _load_gdf, _ensure_epsg_32198,
    _rasterize_to_tif,
)


# ═════════════════════════════════════════════════════════════════════════
# Constants & Paths
# ═════════════════════════════════════════════════════════════════════════
DERIVATIVES_R9_ROOT = Path("/app/backend/data/gis_archive/derivatives_r9")
R9_RECALC_STATE_PATH = Path(
    "/app/backend/data/territoire/R9_RECALC_STATE.json")
DERIVATIVES_P1_ROOT = Path(
    "/app/backend/data/gis_archive/derivatives")
SUBSETS_ROOT = Path("/app/backend/data/gis_archive/subsets")

# Pipeline R16-A targets (ordre canonique du Commandant)
R16A_PIPELINE = [
    "R9_SIGNATURES_TERRAIN",
    "R9_EXCLUSIONS",
    "R9_ZONES_HUMIDES",
    "R9_COUVERT_SECURITE",
]


# ═════════════════════════════════════════════════════════════════════════
# Registry-aware probe des hooks territoire_ultime
# ═════════════════════════════════════════════════════════════════════════
def probe_territoire_ultime_hooks(
        regles_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Probe l'état réel des 6 hooks documentés dans
    regles_territoires_canonical.territoire_ultime_hooks.

    Returns dict {hook_name: {available: bool, paths_present: [...],
                              paths_absent: [...], interface_loadable: bool}}.
    AUCUN PATH N'EST FABRIQUÉ : on lit le dict, on test l'existence.
    """
    hooks_specs = regles_dict.get(
        "territoire_ultime_hooks", {}).get("hooks_specs", {})
    out: Dict[str, Any] = {}
    for hook_name, spec in hooks_specs.items():
        present, absent = [], []
        for p in spec.get("expected_paths", []):
            (present if Path(p).exists() else absent).append(p)
        # Interface python loadable ?
        iface = spec.get("interface")
        iface_loadable = False
        if iface:
            try:
                __import__(iface)
                iface_loadable = True
            except Exception:
                iface_loadable = False
        out[hook_name] = {
            "available": (
                len(present) > 0 if spec.get("expected_paths")
                else iface_loadable
            ),
            "expected_paths_count": len(spec.get("expected_paths", [])),
            "paths_present": present,
            "paths_absent": absent,
            "interface": iface,
            "interface_loadable": iface_loadable,
            "fallback_when_unavailable": spec.get(
                "fallback_when_unavailable",
                spec.get("fallback_when_absent", "skip_with_log")),
            "consumed_by_targets": spec.get("consumed_by_targets", []),
        }
    return out


# ═════════════════════════════════════════════════════════════════════════
# Auto-pick subset
# ═════════════════════════════════════════════════════════════════════════
def auto_pick_subset() -> Optional[str]:
    """Sélectionne le subset le plus récent (mtime) ≥ 1 Mo."""
    import glob
    candidates = [
        p for p in glob.glob(
            str(SUBSETS_ROOT / "pee_maj_subset_*.gpkg"))
        if Path(p).stat().st_size > 1_000_000
    ]
    candidates.sort(key=lambda p: Path(p).stat().st_mtime)
    return candidates[-1] if candidates else None


# ═════════════════════════════════════════════════════════════════════════
# 1. R9_SIGNATURES_TERRAIN
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_signatures_terrain(
    subset_path: str,
    regles_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-A · R9_SIGNATURES_TERRAIN.

    Une signature = empreinte 8-tuple (cl_drai + cl_pent + type_eco +
    dep_sur + gr_ess + cl_age + cl_dens + cl_haut). Hash MD5 → ID stable.
    Utile comme index spatial pour lookups inter-targets.
    """
    import numpy as np
    import geopandas as gpd

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / "R9_SIGNATURES_TERRAIN.tif"
    out_gpkg = out_root / "R9_SIGNATURES_TERRAIN.gpkg"

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)

    sig_fields = (regles_dict.get("signature_definition", {})
                   .get("fields", []))
    cols_lower = {c.lower(): c for c in gdf.columns}
    fields_present = []
    for f in sig_fields:
        if cols_lower.get(f.lower()):
            fields_present.append(cols_lower[f.lower()])

    if not fields_present:
        raise RuntimeError(
            f"Aucun champ signature ne match les colonnes du subset. "
            f"Demandés: {sig_fields} · Présents: {list(gdf.columns)[:15]}")

    def _make_sig(row) -> str:
        parts = [str(row[c]).strip().upper() for c in fields_present]
        h = hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()
        return h[:8]

    gdf["_signature_id_hex"] = gdf.apply(_make_sig, axis=1)
    # Signature uint32 numérique pour rasterisation (tronque à 7 hex pour <2^31)
    gdf["_signature_uint32"] = gdf["_signature_id_hex"].apply(
        lambda h: int(h[:7], 16)).astype("uint32")

    n_polygons = len(gdf)
    n_unique_signatures = int(gdf["_signature_id_hex"].nunique())

    # Rasterisation (uint32) — pyogrio/rasterio accepte uint32 mais GTiff
    # natif uint32 fonctionne avec dtype='uint32'
    rast_info = _rasterize_to_tif(
        gdf, "_signature_uint32", out_tif,
        resolution_m=resolution_m, dtype="uint32",
        nodata=0)

    # Vector : on conserve juste les colonnes utiles (allège le GPKG)
    keep_cols = ["_signature_id_hex"] + fields_present + ["geometry"]
    gdf_export = gpd.GeoDataFrame(
        gdf[keep_cols].rename(
            columns={"_signature_id_hex": "signature_id_hex"}),
        crs=gdf.crs)
    gdf_export.to_file(
        str(out_gpkg), driver="GPKG", layer="signatures")

    sha_tif = _sha256_file(out_tif)
    sha_gpkg = _sha256_file(out_gpkg)
    elapsed = round(time.time() - t0, 2)

    # Top 10 signatures les plus fréquentes
    top10 = dict(
        Counter(gdf["_signature_id_hex"]).most_common(10))
    logger.info(
        "R9_SIGNATURES_TERRAIN_DONE elapsed=%ss n_pol=%d n_unique=%d",
        elapsed, n_polygons, n_unique_signatures)
    return {
        "manifest_id": "R9_SIGNATURES_TERRAIN_COMPUTED_Ω",
        "ordre": "N°52-R16-A",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_raster": str(out_tif),
        "output_vector": str(out_gpkg),
        "raster_size_bytes": out_tif.stat().st_size,
        "vector_size_bytes": out_gpkg.stat().st_size,
        "raster_sha256": sha_tif,
        "vector_sha256": sha_gpkg,
        "n_polygons_processed": n_polygons,
        "n_unique_signatures": n_unique_signatures,
        "fields_used_for_signature": fields_present,
        "top10_signatures_frequency": top10,
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 2. R9_EXCLUSIONS
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_exclusions(
    subset_path: str,
    exclusions_dict: Dict[str, Any],
    fragmentation_tif: Optional[str] = None,
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-A · R9_EXCLUSIONS (raster binaire 0/1).

    Combine pentes_extremes (cl_pent) + drainage_extreme (cl_drai 0/6) +
    fragmentation_extreme (depuis MFFP_FRAGMENTATION_INDEX.tif).

    Sources externes (routes/habitations/zones réglementaires) :
    skip_with_log si absentes. ANTI_GÉNÉRIQUE_STRICT.
    """
    import numpy as np

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / "R9_EXCLUSIONS.tif"

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)

    rules = exclusions_dict.get("rules", {})
    threshold = float(
        exclusions_dict.get("aggregation_rule", {})
        .get("binary_threshold", 0.5))

    cols_lower = {c.lower(): c for c in gdf.columns}
    cl_pent_col = cols_lower.get("cl_pent")
    cl_drai_col = cols_lower.get("cl_drai")

    skipped_rules: List[Dict[str, str]] = []
    applied_rules: List[Dict[str, Any]] = []

    # Pentes extrêmes
    pente_excluded = set(
        rules.get("pentes_extremes", {}).get("cl_pent_excluded", []))
    pente_w = float(
        rules.get("pentes_extremes", {}).get("weight_in_exclusion", 1.0))
    if cl_pent_col and pente_excluded:
        gdf["_excl_pente"] = (
            gdf[cl_pent_col].astype(str).str.strip().str.upper()
            .isin(pente_excluded).astype("float32") * pente_w)
        applied_rules.append({"rule": "pentes_extremes", "weight": pente_w,
                               "n_match": int((gdf["_excl_pente"] > 0).sum())})
    else:
        gdf["_excl_pente"] = 0.0
        skipped_rules.append({"rule": "pentes_extremes",
                              "reason": "cl_pent_absent_or_no_threshold"})

    # Drainage extrême
    drai_excluded = set(
        rules.get("drainage_extreme", {}).get("cl_drai_excluded", []))
    drai_w = float(
        rules.get("drainage_extreme", {}).get("weight_in_exclusion", 0.5))
    if cl_drai_col and drai_excluded:
        gdf["_excl_drai"] = (
            gdf[cl_drai_col].astype(str).str.strip()
            .isin(drai_excluded).astype("float32") * drai_w)
        applied_rules.append({"rule": "drainage_extreme", "weight": drai_w,
                               "n_match": int((gdf["_excl_drai"] > 0).sum())})
    else:
        gdf["_excl_drai"] = 0.0
        skipped_rules.append({"rule": "drainage_extreme",
                              "reason": "cl_drai_absent"})

    # Fragmentation extrême (lecture du raster MFFP_FRAGMENTATION_INDEX si
    # présent, sample sur centroides)
    frag_w = float(
        rules.get("fragmentation_extreme", {})
        .get("weight_in_exclusion", 0.7))
    frag_thresh = float(
        rules.get("fragmentation_extreme", {})
        .get("fragmentation_threshold", 0.7))
    frag_path = (
        Path(fragmentation_tif) if fragmentation_tif
        else (DERIVATIVES_P1_ROOT / "MFFP_FRAGMENTATION_INDEX.tif"))
    if frag_path.exists():
        try:
            import rasterio
            centroids = gdf.geometry.centroid
            pts = [(c.x, c.y) for c in centroids
                    if c is not None and not c.is_empty]
            with rasterio.open(str(frag_path)) as src:
                samples = list(src.sample(pts))
            frag_values = np.array(
                [float(s[0]) if s is not None else 0.0
                 for s in samples], dtype="float32")
            mask = (frag_values > frag_thresh).astype("float32") * frag_w
            # Si fewer pts than rows (defensive)
            if len(mask) < len(gdf):
                mask = np.concatenate(
                    [mask,
                     np.zeros(len(gdf) - len(mask), dtype="float32")])
            gdf["_excl_frag"] = mask
            applied_rules.append({
                "rule": "fragmentation_extreme",
                "weight": frag_w, "threshold": frag_thresh,
                "n_match": int((gdf["_excl_frag"] > 0).sum()),
                "raster_sampled": str(frag_path),
            })
        except Exception as e:
            logger.warning("FRAGMENTATION_SAMPLING_FAILED err=%s", e)
            gdf["_excl_frag"] = 0.0
            skipped_rules.append({
                "rule": "fragmentation_extreme",
                "reason": f"sampling_error:{str(e)[:60]}"})
    else:
        gdf["_excl_frag"] = 0.0
        skipped_rules.append({"rule": "fragmentation_extreme",
                              "reason": f"raster_absent:{frag_path}"})

    # Sources externes (routes, habitations, zones réglementaires) — pas
    # disponibles localement → skip_with_log
    for ext_rule in ("distance_routes_meters", "distance_habitations_meters",
                     "zones_reglementaires"):
        skipped_rules.append({
            "rule": ext_rule,
            "reason": "external_source_absent_anti_generique_strict"})

    # Aggregation : somme pondérée → binary > threshold
    gdf["_excl_score"] = (
        gdf["_excl_pente"] + gdf["_excl_drai"] + gdf["_excl_frag"]
    )
    gdf["_excl_binary"] = (gdf["_excl_score"] > threshold).astype("uint8")

    n_excluded = int(gdf["_excl_binary"].sum())
    n_total = len(gdf)

    rast_info = _rasterize_to_tif(
        gdf, "_excl_binary", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    sha = _sha256_file(out_tif)
    elapsed = round(time.time() - t0, 2)
    logger.info(
        "R9_EXCLUSIONS_DONE elapsed=%ss n_pol=%d n_excluded=%d (%.1f%%)",
        elapsed, n_total, n_excluded,
        100 * n_excluded / max(n_total, 1))
    return {
        "manifest_id": "R9_EXCLUSIONS_COMPUTED_Ω",
        "ordre": "N°52-R16-A",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_raster": str(out_tif),
        "raster_size_bytes": out_tif.stat().st_size,
        "raster_sha256": sha,
        "n_polygons_total": n_total,
        "n_polygons_excluded": n_excluded,
        "exclusion_pct": round(100 * n_excluded / max(n_total, 1), 2),
        "applied_rules": applied_rules,
        "skipped_rules": skipped_rules,
        "binary_threshold": threshold,
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 3. R9_ZONES_HUMIDES
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_zones_humides(
    subset_path: str,
    hydrologie_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-A · R9_ZONES_HUMIDES (raster binaire 0/1).

    cl_drai ∈ {5, 6} OU type_eco commence par préfixe humide.
    """
    import numpy as np

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / "R9_ZONES_HUMIDES.tif"

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)

    cols_lower = {c.lower(): c for c in gdf.columns}
    cl_drai_col = cols_lower.get("cl_drai")
    type_eco_col = cols_lower.get("type_eco")

    drai_humid = set(
        hydrologie_dict.get("wetland_classification", {})
        .get("by_cl_drai", {})
        .get("wetland_codes", ["5", "6"]))
    type_eco_prefixes = (
        hydrologie_dict.get("wetland_classification", {})
        .get("by_type_eco_prefix", {})
        .get("wetland_prefixes_in_type_eco", []))
    drai_humid_str = {str(c).strip() for c in drai_humid}

    def _is_humid(row) -> int:
        if cl_drai_col is not None:
            cd = str(row.get(cl_drai_col, "")).strip()
            if cd in drai_humid_str:
                return 1
        if type_eco_col is not None:
            te = str(row.get(type_eco_col, "")).strip().upper()
            for prefix in type_eco_prefixes:
                if te.startswith(prefix.upper()):
                    return 1
        return 0

    gdf["_humid_binary"] = gdf.apply(_is_humid, axis=1).astype("uint8")
    n_humid = int(gdf["_humid_binary"].sum())
    n_total = len(gdf)

    rast_info = _rasterize_to_tif(
        gdf, "_humid_binary", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    sha = _sha256_file(out_tif)
    elapsed = round(time.time() - t0, 2)
    logger.info(
        "R9_ZONES_HUMIDES_DONE elapsed=%ss n_pol=%d n_humid=%d (%.1f%%)",
        elapsed, n_total, n_humid,
        100 * n_humid / max(n_total, 1))

    cl_drai_dist = (
        Counter(gdf[cl_drai_col].astype(str).str.strip())
        if cl_drai_col else {})
    return {
        "manifest_id": "R9_ZONES_HUMIDES_COMPUTED_Ω",
        "ordre": "N°52-R16-A",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_raster": str(out_tif),
        "raster_size_bytes": out_tif.stat().st_size,
        "raster_sha256": sha,
        "n_polygons_total": n_total,
        "n_polygons_humid": n_humid,
        "humid_pct": round(100 * n_humid / max(n_total, 1), 2),
        "rule_logic": "OR_cl_drai_humid_codes_OR_type_eco_humid_prefix",
        "cl_drai_humid_codes_used": sorted(drai_humid_str),
        "type_eco_humid_prefixes_used": type_eco_prefixes,
        "cl_drai_distribution_top10": dict(
            cl_drai_dist.most_common(10) if cl_drai_dist else {}),
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 4. R9_COUVERT_SECURITE
# ═════════════════════════════════════════════════════════════════════════
def compute_r9_couvert_securite(
    subset_path: str,
    couvert_dict: Dict[str, Any],
    output_root: Optional[Path] = None,
    resolution_m: int = 100,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-A · R9_COUVERT_SECURITE (uint8 0-100).

    Score combiné : cl_dens × cl_haut × type_couv selon dict R16-A.
    """
    import numpy as np

    t0 = time.time()
    out_root = output_root or DERIVATIVES_R9_ROOT
    out_root.mkdir(parents=True, exist_ok=True)
    out_tif = out_root / "R9_COUVERT_SECURITE.tif"

    gdf, layer = _load_gdf(subset_path)
    gdf = _ensure_epsg_32198(gdf)

    weights = couvert_dict.get("scoring", {}).get("weights", {})
    dens_score = couvert_dict.get(
        "scoring", {}).get("cl_dens_score", {})
    haut_score = couvert_dict.get(
        "scoring", {}).get("cl_haut_score", {})
    couv_score = couvert_dict.get(
        "scoring", {}).get("type_couv_score", {})

    cols_lower = {c.lower(): c for c in gdf.columns}
    dens_col = cols_lower.get("cl_dens")
    haut_col = cols_lower.get("cl_haut")
    couv_col = cols_lower.get("type_couv")

    if not all([dens_col, haut_col, couv_col]):
        raise ValueError(
            f"Colonnes cl_dens|cl_haut|type_couv absentes: "
            f"{list(gdf.columns)[:15]}")

    def _score(row) -> int:
        d = str(row[dens_col]).strip().upper()
        h = str(row[haut_col]).strip().upper()
        c = str(row[couv_col]).strip().upper()
        sd = float(dens_score.get(d, dens_score.get("fallback", 0)))
        sh = float(haut_score.get(h, haut_score.get("fallback", 30)))
        sc = float(couv_score.get(c, couv_score.get("fallback", 0)))
        total = (sd * float(weights.get("cl_dens", 0.4))
                 + sh * float(weights.get("cl_haut", 0.35))
                 + sc * float(weights.get("type_couv", 0.25)))
        return int(round(min(max(total, 0), 100)))

    gdf["_couv_secur"] = gdf.apply(_score, axis=1).astype("uint8")
    mean_score = float(gdf["_couv_secur"].mean())
    n_total = len(gdf)

    rast_info = _rasterize_to_tif(
        gdf, "_couv_secur", out_tif,
        resolution_m=resolution_m, dtype="uint8",
        nodata=NODATA_VALUE_UINT8)

    sha = _sha256_file(out_tif)
    elapsed = round(time.time() - t0, 2)
    # Distribution buckets
    arr = gdf["_couv_secur"].values
    bucket_counts = {
        "0_25": int(((arr >= 0) & (arr < 25)).sum()),
        "25_50": int(((arr >= 25) & (arr < 50)).sum()),
        "50_75": int(((arr >= 50) & (arr < 75)).sum()),
        "75_100": int((arr >= 75).sum()),
    }
    logger.info(
        "R9_COUVERT_SECURITE_DONE elapsed=%ss n_pol=%d mean=%.2f",
        elapsed, n_total, mean_score)
    return {
        "manifest_id": "R9_COUVERT_SECURITE_COMPUTED_Ω",
        "ordre": "N°52-R16-A",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "output_raster": str(out_tif),
        "raster_size_bytes": out_tif.stat().st_size,
        "raster_sha256": sha,
        "n_polygons_processed": n_total,
        "mean_score": round(mean_score, 2),
        "bucket_distribution": bucket_counts,
        "weights_applied": weights,
        "rasterization": rast_info,
        "elapsed_s": elapsed,
        "src_layer": layer,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# Pipeline Orchestrator + R9_RECALC_STATE update
# ═════════════════════════════════════════════════════════════════════════
def execute_r16a_pipeline(
    subset_path: Optional[str] = None,
    targets: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """ORDRE N°52-R16-A · Pipeline orchestrator pour les 4 fondations R9.

    Ordre canonique :
      1. R9_SIGNATURES_TERRAIN
      2. R9_EXCLUSIONS
      3. R9_ZONES_HUMIDES
      4. R9_COUVERT_SECURITE

    Met à jour R9_RECALC_STATE.json → status=OK_REAL pour les 4 targets.
    """
    import json
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega import (  # noqa: E501
        load_dictionary,
    )

    t0 = time.time()
    src = subset_path or auto_pick_subset()
    if not src:
        raise RuntimeError(
            "Aucun subset utilisable. Lancer "
            "POST /diagnostic/pee-maj/export-subset?execute=true&source=vsi")

    # Charge les 4 dicts R16-A
    regles = load_dictionary("regles_territoires_canonical")
    exclusions = load_dictionary("exclusions_thresholds")
    hydrologie = load_dictionary("hydrologie_drainage_codes")
    couvert = load_dictionary("couvert_securite_thresholds")
    if not all([regles, exclusions, hydrologie, couvert]):
        raise RuntimeError(
            "Un ou plusieurs dictionnaires R16-A absents/invalides.")

    # Probe hooks territoire_ultime
    hooks_state = probe_territoire_ultime_hooks(regles)

    pipeline = targets or R16A_PIPELINE
    results: Dict[str, Any] = {}

    for target in pipeline:
        try:
            if target == "R9_SIGNATURES_TERRAIN":
                results[target] = compute_r9_signatures_terrain(src, regles)
            elif target == "R9_EXCLUSIONS":
                results[target] = compute_r9_exclusions(src, exclusions)
            elif target == "R9_ZONES_HUMIDES":
                results[target] = compute_r9_zones_humides(src, hydrologie)
            elif target == "R9_COUVERT_SECURITE":
                results[target] = compute_r9_couvert_securite(src, couvert)
            else:
                results[target] = {
                    "manifest_id": f"{target}_NOT_IMPLEMENTED_R16A",
                    "status": "BACKLOG_R16_B_C_D",
                    "note": (
                        "Implémentation prévue dans R16-B/C/D selon "
                        "stratégie batchée approuvée par Commandant."),
                }
        except Exception as e:
            import traceback
            results[target] = {
                "manifest_id": f"{target}_FAILED_Ω",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            }

    # Targets succeeded R16-A
    r16a_succeeded = [
        t for t in R16A_PIPELINE
        if t in results and "error" not in results[t]
        and results[t].get("manifest_id", "").endswith("_COMPUTED_Ω")
    ]

    # Update R9_RECALC_STATE.json (FUSION ADD-ONLY: ne touche pas au reste)
    state_update = None
    try:
        state = (
            json.loads(R9_RECALC_STATE_PATH.read_text(encoding="utf-8"))
            if R9_RECALC_STATE_PATH.exists() else {})
        targets_state = state.setdefault("targets", {})
        for t in r16a_succeeded:
            targets_state[t] = {
                "status": "OK_REAL",
                "ordre": "N°52-R16-A",
                "completed_at_utc": _utc_now(),
                "output_raster": results[t].get("output_raster"),
                "output_vector": results[t].get("output_vector"),
                "raster_sha256": results[t].get("raster_sha256"),
                "vector_sha256": results[t].get("vector_sha256"),
                "elapsed_s": results[t].get("elapsed_s"),
            }
        state["last_r16a_run_id"] = f"R16A_{int(time.time())}"
        state["last_r16a_run_completed_at_utc"] = _utc_now()
        state["last_r16a_subset_used"] = src
        state["last_r16a_targets_succeeded"] = r16a_succeeded
        state["amplification_label"] = state.get(
            "amplification_label", "MFFP×1000")
        # Préserve status global de R9 (ne pas écraser globalement)
        if not state.get("status"):
            state["status"] = "OK_REAL_PARTIAL_R16A"
        elif state.get("status") in (
                "OK_WITH_STUBS", "STUB_READY_AWAITING_BUSINESS_LOGIC"):
            state["status"] = "OK_REAL_PARTIAL_R16A"
        R9_RECALC_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        R9_RECALC_STATE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        state_update = {
            "updated": True,
            "new_global_status": state["status"],
            "targets_marked_OK_REAL": r16a_succeeded,
            "state_path": str(R9_RECALC_STATE_PATH),
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
        "manifest_id": "R9_PHASE3_R16A_PIPELINE_COMPLETED_Ω",
        "ordre": "N°52-R16-A",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "subset_used": src,
        "subset_size_bytes": Path(src).stat().st_size,
        "pipeline_executed": pipeline,
        "r16a_targets_succeeded": r16a_succeeded,
        "n_targets_succeeded": len(r16a_succeeded),
        "results": results,
        "territoire_ultime_hooks_status": hooks_state,
        "r9_recalc_state_update": state_update,
        "elapsed_total_s": elapsed_total,
        "v30_lock": "INVIOLÉ",
    }


__all__ = [
    "execute_r16a_pipeline",
    "compute_r9_signatures_terrain",
    "compute_r9_exclusions",
    "compute_r9_zones_humides",
    "compute_r9_couvert_securite",
    "probe_territoire_ultime_hooks",
    "auto_pick_subset",
    "R16A_PIPELINE",
    "DERIVATIVES_R9_ROOT",
    "R9_RECALC_STATE_PATH",
]
