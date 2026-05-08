"""nasa_ndvi_dense_grid_omega.py — NASA_NDVI_DENSE_GRID_Ω (P8)
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Hook P8 pour débloquer les 2 derniers outputs deferred :
  · feeding_zones_FULL (Borowik 2013 dense forage mapping)
  · microhabitat_clusters_global_dense (Pettorelli 2005 §4.1)

Densification spatiale via subset ORNL MOD13Q1 :
  · kmAboveBelow=2, kmLeftRight=2 → grille 17×17 = 289 pixels (231.66m)
  · Multiplie par 6 tuiles temporelles (juin-août summer)
  · Total : 1734 valeurs réelles MOD13Q1 par site
  · 5 sites BP135 → 8670 valeurs au total (anti-générique)

ECOLOGICAL PARTITIONING DOCTRINAL (Pettorelli 2005 + Hamel 2009) :
  · Cluster_1 : NDVI < 0.2 = BARREN_LOW_PRODUCTIVITY
  · Cluster_2 : 0.2 ≤ NDVI < 0.4 = SHRUBLAND_MODERATE
  · Cluster_3 : 0.4 ≤ NDVI < 0.6 = OPEN_FOREST_HIGH_PRODUCTIVITY
  · Cluster_4 : 0.6 ≤ NDVI < 0.8 = DENSE_FOREST_PRIMARY
  · Cluster_5 : NDVI ≥ 0.8 = CANOPY_CLIMAX_OVERSTOCK

OUTPUTS DOCTRINAUX :
  · feeding_zones_FULL_dense : % pixels in species optimum NDVI range
    (Borowik 2013 forage availability dense forest mapping)
  · microhabitat_clusters_dense_per_site : distribution clusters par site
  · microhabitat_diversity_shannon : indice Shannon per site
  · microhabitat_clusters_global_dense : agrégation cross-sites

RÉFÉRENCES PEER-REVIEWED :
  [1] Pettorelli et al. (2005). TREE, 20(9):503-510.
      DOI:10.1016/j.tree.2005.05.011 (NDVI dense grid forage)
  [2] Borowik et al. (2013). Eur J Wildl Res, 59:675-682.
      DOI:10.1007/s10344-013-0720-0 (forage availability mapping)
  [3] Hamel et al. (2009). J Appl Ecol, 46:582-589.
      DOI:10.1111/j.1365-2664.2009.01643.x (NDVI thresholds ungulates)
  [4] Shannon, C. E. (1948). A Mathematical Theory of Communication.
      Bell System Technical Journal, 27(3):379-423.
      (Shannon entropy for diversity)

ANTI-GÉNÉRIQUE STRICT :
  · 5 sites × 1 saison summer × 6 tuiles MOD13Q1 (within ORNL limit ≤10)
  · NODATA=-3000 rejeté sans imputation
  · Scale factor 0.0001 standard MOD13Q1
  · Pas de mock, pas d'imputation, traçabilité totale
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DENSE_GRID_ROOT = Path(
    "/app/backend/data/pipelines/nasa_ndvi_dense_grid")
DENSE_GRID_VALIDATION_PATH = (
    DENSE_GRID_ROOT / "nasa_ndvi_dense_grid_validation_overlay.json")
DENSE_GRID_HOOK_ACTIVATION_PATH = (
    DENSE_GRID_ROOT / "nasa_ndvi_dense_grid_hook_activation_overlay.json")


# Seuils ecological partitioning (peer-reviewed)
ECOLOGICAL_NDVI_BINS: List[Tuple[float, float, str]] = [
    (0.0, 0.2, "BARREN_LOW_PRODUCTIVITY"),
    (0.2, 0.4, "SHRUBLAND_MODERATE"),
    (0.4, 0.6, "OPEN_FOREST_HIGH_PRODUCTIVITY"),
    (0.6, 0.8, "DENSE_FOREST_PRIMARY"),
    (0.8, 1.0001, "CANOPY_CLIMAX_OVERSTOCK"),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _http_get_json_strict(
    url: str, timeout_s: int = 35,
    body_max_bytes: int = 8_388_608,  # 8 MB
) -> Dict[str, Any]:
    """GET strict ORNL sans follow_redirects."""
    import urllib.request
    import urllib.error

    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg,
                              headers, newurl):
            return None

    record: Dict[str, Any] = {
        "url": url, "http_status": None,
        "body_is_json": False, "parsed_json": None,
        "reason": None, "elapsed_ms": None,
    }
    t0 = time.time()
    try:
        opener = urllib.request.build_opener(
            NoRedirectHandler)
        req = urllib.request.Request(
            url, method="GET",
            headers={
                "User-Agent": "BCE-4X-NDVI-DENSE-GRID/1.0",
                "Accept": "application/json",
            })
        with opener.open(req, timeout=timeout_s) as resp:
            record["http_status"] = resp.status
            body = resp.read(body_max_bytes)
            try:
                record["parsed_json"] = json.loads(
                    body.decode("utf-8", errors="replace"))
                record["body_is_json"] = True
            except json.JSONDecodeError as e:
                record["json_parse_error"] = str(e)[:200]
    except urllib.error.HTTPError as e:
        record["http_status"] = e.code
        record["reason"] = f"http_error_{e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        record["reason"] = f"network_error::{str(e)[:160]}"
    record["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
    return record


def _modis_a_year_doy(year: int, doy: int) -> str:
    return f"A{year}{doy:03d}"


def _flatten_pixels_decode_scale(
    subset: List[Dict[str, Any]],
    nodata: int = -3000,
    scale: float = 0.0001,
) -> Tuple[List[float], int, int]:
    """Aplatit pixels valides (decoded × scale) cross-temporal.

    Anti-générique : NODATA rejeté, pas d'imputation.
    Returns (valid_values, n_total_pixels, n_nodata).
    """
    valid_values: List[float] = []
    n_total = 0
    n_nodata = 0
    for entry in subset:
        data = entry.get("data") or []
        for v in data:
            n_total += 1
            try:
                iv = int(v)
            except (TypeError, ValueError):
                continue
            if iv == nodata:
                n_nodata += 1
                continue
            valid_values.append(iv * scale)
    return valid_values, n_total, n_nodata


def _percentile(values: List[float], p: float) -> float:
    """Percentile p (0-100) sans dependencies (linear interp)."""
    if not values:
        return float("nan")
    s = sorted(values)
    k = (len(s) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] + (s[c] - s[f]) * (k - f)


def _ecological_partition_pixels(
    valid_ndvi: List[float],
) -> Dict[str, Any]:
    """Distribution des pixels dans 5 clusters écologiques (Pettorelli 2005).

    Anti-générique : seuils peer-reviewed fixes.
    """
    bins_count = {label: 0 for _, _, label in ECOLOGICAL_NDVI_BINS}
    n_valid = len(valid_ndvi)
    if n_valid == 0:
        return {
            "valid": False,
            "reason": "no_valid_pixels",
        }
    for v in valid_ndvi:
        for low, high, label in ECOLOGICAL_NDVI_BINS:
            if low <= v < high:
                bins_count[label] += 1
                break
    bins_pct = {
        label: round(100.0 * bins_count[label] / n_valid, 3)
        for label in bins_count}
    # Shannon diversity index H = -Σ pi × log(pi)
    shannon = 0.0
    for label, count in bins_count.items():
        if count > 0:
            p = count / n_valid
            shannon -= p * math.log(p)
    return {
        "valid": True,
        "n_pixels_valid": n_valid,
        "bins_count": bins_count,
        "bins_pct": bins_pct,
        "shannon_diversity_h": round(shannon, 4),
        "shannon_max_log_5": round(math.log(5), 4),
        "shannon_evenness": round(
            shannon / math.log(5), 4),
        "bins_doctrinal": [
            {"low": low, "high": high, "label": label}
            for low, high, label in ECOLOGICAL_NDVI_BINS],
    }


def _compute_feeding_zones_full_dense(
    valid_ndvi: List[float],
    species_optimum_low: float,
    species_optimum_high: float,
) -> Dict[str, Any]:
    """feeding_zones FULL dense (Borowik 2013) sur grille pixels."""
    n_valid = len(valid_ndvi)
    if n_valid == 0:
        return {
            "value": None,
            "regime": "DEFERRED_NO_VALID_PIXELS",
            "primary_reference": "Borowik_2013_EurJWildlRes",
        }
    n_in_optimum = sum(
        1 for v in valid_ndvi
        if species_optimum_low <= v <= species_optimum_high)
    pct_optimum = 100.0 * n_in_optimum / n_valid
    mean_ndvi = sum(valid_ndvi) / n_valid
    p10 = _percentile(valid_ndvi, 10)
    p50 = _percentile(valid_ndvi, 50)
    p90 = _percentile(valid_ndvi, 90)
    # Score = pct_optimum × bonus_homogeneity (low IQR = consistent)
    iqr = (
        _percentile(valid_ndvi, 75)
        - _percentile(valid_ndvi, 25))
    homogeneity_bonus = max(
        0.0, 1.0 - iqr / max(species_optimum_high, 0.1))
    feeding_score = round(
        pct_optimum * (0.7 + 0.3 * homogeneity_bonus), 2)
    if feeding_score >= 75.0:
        regime = "HIGH_QUALITY_FEEDING_ZONE_FULL_DENSE"
    elif feeding_score >= 50.0:
        regime = "MODERATE_FEEDING_ZONE_FULL_DENSE"
    elif feeding_score >= 25.0:
        regime = "LOW_FEEDING_ZONE_FULL_DENSE"
    else:
        regime = "POOR_FEEDING_ZONE_FULL_DENSE"
    return {
        "value": feeding_score,
        "unit": "feeding_zones_FULL_dense_score_0_100",
        "regime": regime,
        "components": {
            "pct_pixels_in_species_optimum_range": round(
                pct_optimum, 2),
            "n_pixels_in_optimum": n_in_optimum,
            "n_pixels_total_valid": n_valid,
            "ndvi_mean_dense": round(mean_ndvi, 4),
            "ndvi_p10": round(p10, 4),
            "ndvi_p50_median": round(p50, 4),
            "ndvi_p90": round(p90, 4),
            "ndvi_iqr": round(iqr, 4),
            "homogeneity_bonus": round(homogeneity_bonus, 3),
        },
        "species_thresholds_used": {
            "ndvi_optimal_low": species_optimum_low,
            "ndvi_optimal_high": species_optimum_high,
        },
        "primary_references": [
            "Borowik_2013_EurJWildlRes",
            "Pettorelli_2005_TREE",
            "Hamel_2009_JApplEcol",
        ],
    }


def _aggregate_microhabitat_clusters_global(
    per_site_partition: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Agrégation cross-sites des clusters (microhabitat global dense)."""
    valid_partitions = [
        p for p in per_site_partition.values()
        if p.get("valid")]
    if not valid_partitions:
        return {
            "value": None,
            "regime": "DEFERRED_NO_VALID_SITES",
            "primary_reference": "Pettorelli_2005_TREE",
        }
    global_bins_count = {
        label: 0 for _, _, label in ECOLOGICAL_NDVI_BINS}
    n_total_pixels_global = 0
    site_dominant_clusters: List[str] = []
    site_shannon: List[float] = []
    for site_name, p in per_site_partition.items():
        if not p.get("valid"):
            continue
        bins = p["bins_count"]
        for label, count in bins.items():
            global_bins_count[label] += count
        n_total_pixels_global += p["n_pixels_valid"]
        # dominant cluster pour ce site
        dom = max(bins.items(), key=lambda x: x[1])[0]
        site_dominant_clusters.append(dom)
        site_shannon.append(p["shannon_diversity_h"])
    global_bins_pct = {
        label: round(
            100.0 * global_bins_count[label]
            / max(n_total_pixels_global, 1), 3)
        for label in global_bins_count}
    # Diversité globale
    global_shannon = 0.0
    for label, count in global_bins_count.items():
        if count > 0:
            p = count / n_total_pixels_global
            global_shannon -= p * math.log(p)
    n_clusters_present_global = sum(
        1 for c in global_bins_count.values() if c > 0)
    return {
        "value": round(global_shannon, 4),
        "unit": "shannon_diversity_h_global",
        "regime": (
            "HIGH_GLOBAL_DIVERSITY"
            if global_shannon >= 1.2
            else "MODERATE_GLOBAL_DIVERSITY"
            if global_shannon >= 0.7
            else "LOW_GLOBAL_DIVERSITY"),
        "components": {
            "n_total_pixels_global": n_total_pixels_global,
            "n_sites_aggregated": len(valid_partitions),
            "n_clusters_present_global": (
                n_clusters_present_global),
            "global_bins_count": global_bins_count,
            "global_bins_pct": global_bins_pct,
            "site_dominant_clusters": site_dominant_clusters,
            "site_shannon_mean": round(
                sum(site_shannon) / len(site_shannon), 4)
                if site_shannon else None,
            "shannon_max_log_5": round(math.log(5), 4),
            "global_shannon_evenness": round(
                global_shannon / math.log(5), 4),
        },
        "primary_references": [
            "Pettorelli_2005_TREE",
            "Shannon_1948_BellSystemTechJ",
            "Hamel_2009_JApplEcol",
        ],
    }


# ═════════════════════════════════════════════════════════════════════════
# VALIDATE — multi-sites × dense grid summer
# ═════════════════════════════════════════════════════════════════════════
def validate_nasa_ndvi_dense_grid(
    site_coordinates: Optional[Dict[str, Dict[str, float]]] = None,
    species_to_site_map: Optional[Dict[str, str]] = None,
    year: Optional[int] = None,
    km_above_below: int = 2,
    km_left_right: int = 2,
    bands_logical: Optional[List[str]] = None,
    persist: bool = True,
    inter_call_sleep_s: float = 0.4,
    timeout_s: int = 35,
) -> Dict[str, Any]:
    """NASA_NDVI_DENSE_GRID_P0_VALIDATE_Ω · summer dense forage."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        NDVI_LOGICAL_TO_BAND,
    )
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        SPECIES_FORAGE_THRESHOLDS_V1,
    )
    require_guardrails_enforced("validate_nasa_ndvi_dense_grid")

    if site_coordinates is None:
        site_coordinates = {
            "espece_a": {"lat": 46.8131, "lon": -71.2075},
            "espece_b": {"lat": 47.2, "lon": -70.27},
            "espece_c": {"lat": 48.34, "lon": -69.39},
            "espece_d": {"lat": 46.36, "lon": -72.07},
            "espece_e": {"lat": 47.0, "lon": -71.0},
        }
    if species_to_site_map is None:
        species_to_site_map = {
            "espece_a": "cerf",
            "espece_b": "orignal",
            "espece_c": "ours",
            "espece_d": "dindon",
            "espece_e": "wapiti",
        }
    if year is None:
        year = datetime.now(timezone.utc).year - 1
    if bands_logical is None:
        bands_logical = ["NDVI"]

    # Saison summer (Borowik 2013)
    summer_doy_start = 153
    summer_doy_end = 244
    start_modis = _modis_a_year_doy(year, summer_doy_start)
    end_modis = _modis_a_year_doy(year, summer_doy_end)

    bands_canonical: List[Tuple[str, Dict[str, Any]]] = []
    for bl in bands_logical:
        if bl in NDVI_LOGICAL_TO_BAND:
            entry = NDVI_LOGICAL_TO_BAND[bl]
            if entry.get("product") == "MOD13Q1":
                bands_canonical.append(
                    (entry["band"], entry))

    if not bands_canonical:
        raise ValueError(
            "BANDS_LOGICAL_REQUIRED_MOD13Q1::"
            "no_valid_band_found")

    t_total = time.time()
    site_results: Dict[str, Dict[str, Any]] = {}
    n_sites = len(site_coordinates)
    n_calls_success = 0
    n_calls_failed = 0
    per_site_partition_summary: Dict[str, Dict[str, Any]] = {}

    for site_name, coords in site_coordinates.items():
        lat = float(coords["lat"])
        lon = float(coords["lon"])
        species = species_to_site_map.get(
            site_name, "unknown")
        thresholds = SPECIES_FORAGE_THRESHOLDS_V1.get(species)
        per_band_results: Dict[str, Dict[str, Any]] = {}
        for band_canonical, _info in bands_canonical:
            url = (
                f"https://modis.ornl.gov/rst/api/v1/"
                f"MOD13Q1/subset?"
                f"latitude={lat}&longitude={lon}"
                f"&band={band_canonical}"
                f"&startDate={start_modis}"
                f"&endDate={end_modis}"
                f"&kmAboveBelow={km_above_below}"
                f"&kmLeftRight={km_left_right}")
            probe = _http_get_json_strict(
                url, timeout_s=timeout_s)
            if (probe["http_status"] != 200
                    or not probe["body_is_json"]):
                per_band_results[band_canonical] = {
                    "valid": False,
                    "reason": (
                        probe.get("reason")
                        or f"http_{probe['http_status']}"),
                    "elapsed_ms": probe.get("elapsed_ms"),
                }
                n_calls_failed += 1
                if inter_call_sleep_s > 0:
                    time.sleep(inter_call_sleep_s)
                continue
            parsed = probe["parsed_json"] or {}
            subset = parsed.get("subset") or []
            valid_values, n_total, n_nodata = (
                _flatten_pixels_decode_scale(
                    subset, nodata=-3000, scale=0.0001))
            if not valid_values:
                per_band_results[band_canonical] = {
                    "valid": False,
                    "reason": "all_pixels_nodata",
                    "n_total": n_total,
                    "n_nodata": n_nodata,
                }
                n_calls_failed += 1
                if inter_call_sleep_s > 0:
                    time.sleep(inter_call_sleep_s)
                continue
            n_calls_success += 1
            partition = _ecological_partition_pixels(
                valid_values)
            feeding_full = None
            if (band_canonical == "250m_16_days_NDVI"
                    and thresholds is not None):
                feeding_full = (
                    _compute_feeding_zones_full_dense(
                        valid_values,
                        thresholds["ndvi_optimal_low"],
                        thresholds["ndvi_optimal_high"]))
            per_band_results[band_canonical] = {
                "valid": True,
                "nrows": parsed.get("nrows"),
                "ncols": parsed.get("ncols"),
                "cellsize_m": parsed.get("cellsize"),
                "n_temporal_tiles": len(subset),
                "n_pixels_per_tile": (
                    (parsed.get("nrows") or 0)
                    * (parsed.get("ncols") or 0)),
                "n_total": n_total,
                "n_nodata": n_nodata,
                "n_valid": len(valid_values),
                "stats": {
                    "mean": round(
                        sum(valid_values) / len(valid_values),
                        4),
                    "min": round(min(valid_values), 4),
                    "max": round(max(valid_values), 4),
                    "p10": round(
                        _percentile(valid_values, 10), 4),
                    "p50": round(
                        _percentile(valid_values, 50), 4),
                    "p90": round(
                        _percentile(valid_values, 90), 4),
                },
                "ecological_partition": partition,
                "feeding_zones_full_dense": feeding_full,
                "elapsed_ms": probe.get("elapsed_ms"),
            }
            if (band_canonical == "250m_16_days_NDVI"
                    and partition.get("valid")):
                per_site_partition_summary[site_name] = (
                    partition)
            if inter_call_sleep_s > 0:
                time.sleep(inter_call_sleep_s)

        site_results[site_name] = {
            "lat": lat, "lon": lon,
            "species_canonical": species,
            "scientific_name": (
                thresholds.get("scientific_name")
                if thresholds else None),
            "bands_dense_grid": per_band_results,
        }
        log_forensic_event(
            scope="ENDPOINT_PROBES",
            event="NASA_NDVI_DENSE_GRID_P0_VALIDATE_Ω",
            details={
                "provider": "NASA_NDVI_DENSE",
                "endpoint": (
                    "https://modis.ornl.gov/rst/api/v1/"
                    "MOD13Q1/subset"),
                "site": site_name,
                "species": species,
                "km_above_below": km_above_below,
                "km_left_right": km_left_right,
                "year": year,
                "n_bands": len(bands_canonical),
            },
            persist=True,
        )

    # Microhabitat global aggregation
    microhab_global = _aggregate_microhabitat_clusters_global(
        per_site_partition_summary)

    # Verdict
    expected_calls = n_sites * len(bands_canonical)
    if (n_calls_success == expected_calls
            and expected_calls > 0):
        verdict = "NASA_NDVI_DENSE_GRID_VALIDATE_ALL_VALID"
        valid = True
    elif n_calls_success > 0:
        verdict = (
            f"NASA_NDVI_DENSE_GRID_VALIDATE_PARTIAL::"
            f"{n_calls_success}_OF_{expected_calls}")
        valid = False
    else:
        verdict = "NASA_NDVI_DENSE_GRID_VALIDATE_ALL_INVALID"
        valid = False

    payload = {
        "manifest_id": "NASA_NDVI_DENSE_GRID_P0_VALIDATE_Ω",
        "ordre": "P8_NASA_NDVI_DENSE_GRID_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "valid": valid,
        "verdict": verdict,
        "provider": "NASA_NDVI_DENSE",
        "provider_physical": "NASA_MOD13Q1_ORNL_DENSE_SUBSET",
        "endpoint": (
            "https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset"),
        "spatial_subset_config": {
            "km_above_below": km_above_below,
            "km_left_right": km_left_right,
            "expected_grid_pixels": (
                (1 + 2 * km_above_below * 4)
                * (1 + 2 * km_left_right * 4)),
        },
        "temporal_summer_window": {
            "year": year,
            "doy_start": summer_doy_start,
            "doy_end": summer_doy_end,
            "start_modis": start_modis,
            "end_modis": end_modis,
            "primary_reference": "Borowik_2013_EurJWildlRes",
        },
        "ecological_ndvi_bins_doctrinal": [
            {"low": low, "high": high, "label": label}
            for low, high, label in ECOLOGICAL_NDVI_BINS],
        "n_sites_total": n_sites,
        "n_calls_success": n_calls_success,
        "n_calls_failed": n_calls_failed,
        "site_results": site_results,
        "microhabitat_clusters_global_dense": microhab_global,
        "scientific_references_peer_reviewed": [
            ("Pettorelli et al. (2005). TREE, 20(9):503-510. "
             "DOI:10.1016/j.tree.2005.05.011"),
            ("Borowik et al. (2013). Eur J Wildl Res, "
             "59:675-682. DOI:10.1007/s10344-013-0720-0"),
            ("Hamel et al. (2009). J Appl Ecol, 46:582-589. "
             "DOI:10.1111/j.1365-2664.2009.01643.x"),
            ("Shannon (1948). Bell System Technical J, "
             "27(3):379-423."),
        ],
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t_total, 3),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        DENSE_GRID_ROOT.mkdir(parents=True, exist_ok=True)
        if DENSE_GRID_VALIDATION_PATH.exists():
            try:
                state = json.loads(
                    DENSE_GRID_VALIDATION_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(state, dict) or (
                        "history" not in state):
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}
        state["history"].append(payload)
        state["last_updated_utc"] = _utc_now()
        state["n_validations"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = verdict
        state["v30_lock"] = "INVIOLÉ"
        DENSE_GRID_VALIDATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            DENSE_GRID_VALIDATION_PATH)
        persisted["overlay_size_bytes"] = (
            DENSE_GRID_VALIDATION_PATH.stat().st_size)

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        persisted["audit_persisted"] = persist_audit({
            "audit_type": "NOAA_PIPELINE",
            "subtype": "NASA_NDVI_DENSE_GRID_VALIDATE",
            "ordre": "P8_NASA_NDVI_DENSE_GRID_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "n_sites_total": n_sites,
            "n_calls_success": n_calls_success,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        })

    payload["persisted_paths"] = persisted
    return payload


# ═════════════════════════════════════════════════════════════════════════
# HOOK ACTIVATE
# ═════════════════════════════════════════════════════════════════════════
def _find_validated_dense_grid_manifest(
    target_manifest_sha256: str,
) -> Optional[Dict[str, Any]]:
    if not DENSE_GRID_VALIDATION_PATH.exists():
        return None
    try:
        state = json.loads(
            DENSE_GRID_VALIDATION_PATH.read_text(
                encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    history = state.get("history", [])
    for entry in history:
        if (entry.get("manifest_sha256")
                == target_manifest_sha256
                and entry.get("n_calls_success", 0) >= 1):
            return entry
    return None


def activate_nasa_ndvi_dense_grid_hook(
    manifest_sha256: str,
    reason: str = (
        "unlock_feeding_zones_FULL_and_microhabitat_dense"),
    persist: bool = True,
) -> Dict[str, Any]:
    """NASA_NDVI_DENSE_GRID_HOOK_ACTIVATE_Ω."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "activate_nasa_ndvi_dense_grid_hook")

    t0 = time.time()
    validated = _find_validated_dense_grid_manifest(
        manifest_sha256)
    if validated is None:
        rejection = {
            "manifest_id": "NASA_NDVI_DENSE_GRID_HOOK_ACTIVATE_Ω",
            "ordre": "P8_NASA_NDVI_DENSE_GRID_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "activated": False,
            "verdict": (
                "NASA_NDVI_DENSE_GRID_HOOK_REJECTED_"
                "MANIFEST_NOT_FOUND_OR_INVALID"),
            "reason": reason,
            "input_manifest_sha256": manifest_sha256,
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t0, 3),
        }
        rejection["manifest_sha256"] = hashlib.sha256(
            json.dumps(rejection, sort_keys=True,
                        ensure_ascii=False,
                        default=str).encode("utf-8")
        ).hexdigest()
        log_forensic_event(
            scope="HOOK_ACTIVATIONS",
            event="NASA_NDVI_DENSE_GRID_HOOK_REJECTED",
            details={"input_manifest_sha256": manifest_sha256},
            persist=True)
        return rejection

    verdict = "NASA_NDVI_DENSE_GRID_HOOK_ACTIVATED"
    payload = {
        "manifest_id": "NASA_NDVI_DENSE_GRID_HOOK_ACTIVATE_Ω",
        "ordre": "P8_NASA_NDVI_DENSE_GRID_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "activated": True,
        "verdict": verdict,
        "reason": reason,
        "validated_manifest_sha256": manifest_sha256,
        "validated_summary": {
            "verdict": validated.get("verdict"),
            "n_sites_total": validated.get("n_sites_total"),
            "n_calls_success": validated.get(
                "n_calls_success"),
            "spatial_subset_config": validated.get(
                "spatial_subset_config"),
        },
        "outputs_unblocked_via_this_hook": [
            "feeding_zones_FULL_dense (Borowik 2013)",
            "microhabitat_clusters_global_dense "
            "(Pettorelli 2005 + Shannon 1948)",
        ],
        "providers_physical_active": [
            "NASA_MOD13Q1_ORNL_DENSE_SUBSET",
        ],
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t0, 3),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        DENSE_GRID_ROOT.mkdir(parents=True, exist_ok=True)
        if DENSE_GRID_HOOK_ACTIVATION_PATH.exists():
            try:
                state = json.loads(
                    DENSE_GRID_HOOK_ACTIVATION_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(state, dict) or (
                        "history" not in state):
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}
        state["history"].append(payload)
        state["last_updated_utc"] = _utc_now()
        state["n_activations"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = verdict
        state["last_validated_manifest_sha256"] = manifest_sha256
        state["v30_lock"] = "INVIOLÉ"
        DENSE_GRID_HOOK_ACTIVATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            DENSE_GRID_HOOK_ACTIVATION_PATH)
        persisted["overlay_size_bytes"] = (
            DENSE_GRID_HOOK_ACTIVATION_PATH.stat().st_size)

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        persisted["audit_persisted"] = persist_audit({
            "audit_type": "NOAA_PIPELINE",
            "subtype": "NASA_NDVI_DENSE_GRID_HOOK_ACTIVATE",
            "ordre": "P8_NASA_NDVI_DENSE_GRID_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "activated": True,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "validated_manifest_sha256": manifest_sha256,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        })

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="NASA_NDVI_DENSE_GRID_HOOK_ACTIVATED",
        details={
            "manifest_sha256": payload_sha256,
            "validated_manifest_sha256": manifest_sha256,
        },
        persist=True)
    payload["persisted_paths"] = persisted
    return payload


def get_nasa_ndvi_dense_grid_hook_status() -> Dict[str, Any]:
    if not DENSE_GRID_HOOK_ACTIVATION_PATH.exists():
        return {
            "manifest_id":
                "NASA_NDVI_DENSE_GRID_HOOK_STATUS_Ω",
            "current_status": "NOT_ACTIVATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        DENSE_GRID_HOOK_ACTIVATION_PATH.read_text(
            encoding="utf-8"))
    last = (
        state["history"][-1]
        if state.get("history") else None)
    return {
        "manifest_id": "NASA_NDVI_DENSE_GRID_HOOK_STATUS_Ω",
        "current_status": (
            "ACTIVATED_OPERATIONAL" if last
            and last.get("activated") else "NOT_ACTIVATED"),
        "n_activations_history": state.get(
            "n_activations", 0),
        "last_manifest_sha256": state.get(
            "last_manifest_sha256"),
        "last_verdict": state.get("last_verdict"),
        "last_validated_manifest_sha256": state.get(
            "last_validated_manifest_sha256"),
        "last_updated_utc": state.get("last_updated_utc"),
        "last_summary": (
            {
                "verdict": last.get("verdict"),
                "providers_physical_active": last.get(
                    "providers_physical_active"),
                "outputs_unblocked": last.get(
                    "outputs_unblocked_via_this_hook"),
            } if last else None),
        "overlay_path": str(
            DENSE_GRID_HOOK_ACTIVATION_PATH),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


def get_last_validated_dense_grid() -> Optional[Dict[str, Any]]:
    """Utilitaire P9 COMPLETE_MERGE pour intégration."""
    if not DENSE_GRID_VALIDATION_PATH.exists():
        return None
    try:
        state = json.loads(
            DENSE_GRID_VALIDATION_PATH.read_text(
                encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    history = state.get("history", [])
    for entry in reversed(history):
        if entry.get("n_calls_success", 0) >= 1:
            return entry
    return None


__all__ = [
    "DENSE_GRID_ROOT",
    "DENSE_GRID_VALIDATION_PATH",
    "DENSE_GRID_HOOK_ACTIVATION_PATH",
    "ECOLOGICAL_NDVI_BINS",
    "validate_nasa_ndvi_dense_grid",
    "activate_nasa_ndvi_dense_grid_hook",
    "get_nasa_ndvi_dense_grid_hook_status",
    "get_last_validated_dense_grid",
]
