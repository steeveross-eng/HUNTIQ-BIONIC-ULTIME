"""nasa_ndvi_timeseries_decade_omega.py — NASA_NDVI_TIMESERIES_DECADE_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Validation timeseries multi-season multi-année (décade) NASA NDVI MOD13Q1
pour débloquer :
  · feeding_zones (Borowik 2013 multi-season summer NDVI)
  · rut_phenology_proxy (NDVI fall pre-rut sept-oct cerf, oct-nov orignal)

CONTRAINTE ORNL : max 10 tuiles temporelles MOD13Q1 par call (16 jours/tuile
→ max 160 jours par appel). Solution doctrinale :
  · Fenêtre été = juin-août (92 jours = ~6 tuiles MOD13Q1)
  · Fenêtre rut = sept-oct (~60 jours = 4 tuiles MOD13Q1)
  · 1 call par fenêtre × année × site
  · Total décade 2015-2024 : 5 sites × 2 fenêtres × 10 ans = 100 calls

ANTI-GÉNÉRIQUE STRICT :
  · Réutilisation pure nasa_ndvi_omega helpers (FUSION ADD-ONLY)
  · NODATA=-3000 rejeté sans imputation
  · Aggregate per-year stats : peak_NDVI, mean_NDVI, n_high_threshold_days
  · Phenology indices : peak_NDVI_doy approximation

OUTPUTS PRODUITS (doctrinaux) :
  · feeding_zones_decade_summer (Borowik 2013)
  · rut_phenology_proxy_fall (cerf oct-nov, orignal sept-oct)
  · phenology_consistency_index (variance inter-annuelle)
  · greening_trend_decade (Pettorelli 2005 long-term)

RÉFÉRENCES PEER-REVIEWED :
  [1] Borowik et al. (2013). Eur J Wildl Res, 59:675-682.
      DOI:10.1007/s10344-013-0720-0 (NDVI summer forage ungulates)
  [2] Pettorelli et al. (2005). TREE, 20(9):503-510.
      DOI:10.1016/j.tree.2005.05.011 (NDVI long-term)
  [3] Garroutte et al. (2016). Remote Sensing, 8(5):404.
      DOI:10.3390/rs8050404 (EVI seasonal)
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


NDVI_DECADE_ROOT = Path(
    "/app/backend/data/pipelines/nasa_ndvi_decade")
NDVI_DECADE_VALIDATION_PATH = (
    NDVI_DECADE_ROOT / "nasa_ndvi_timeseries_decade_overlay.json")


# ═════════════════════════════════════════════════════════════════════════
# Saisons doctrinales (peer-reviewed)
# ═════════════════════════════════════════════════════════════════════════
SEASONAL_WINDOWS_DOCTRINAL: Dict[str, Dict[str, Any]] = {
    "summer_growing_peak": {
        "start_month": 6, "end_month": 8,
        "doy_start": 153, "doy_end": 244,  # 1 juin → 31 août
        "max_tiles_mod13q1": 6,
        "primary_reference": "Borowik_2013_EurJWildlRes",
        "use": "feeding_zones_summer_NDVI_peak",
    },
    "fall_pre_rut": {
        "start_month": 9, "end_month": 10,
        "doy_start": 244, "doy_end": 305,  # 1 sept → 31 oct
        "max_tiles_mod13q1": 4,
        "primary_reference": (
            "Hebblewhite_2008_EcolMonogr"),
        "use": "rut_phenology_proxy_fall_NDVI",
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _modis_a_year_doy(year: int, doy: int) -> str:
    """Format MODIS AYYYYDDD strict (anti-générique)."""
    return f"A{year}{doy:03d}"


def _aggregate_yearly_stats(
    bands_results: Dict[int, Dict[str, Any]],
) -> Dict[str, Any]:
    """Agrège stats yearly par bande logique.

    Pour chaque année, on a {NDVI: {valid, stats: {...}}, EVI: ...}
    Output : {peak_NDVI_max, mean_NDVI_decade, n_years_valid,
              years_above_threshold_05, trend_NDVI_decade}
    """
    ndvi_means: List[float] = []
    ndvi_maxs: List[float] = []
    evi_means: List[float] = []
    years_with_data: List[int] = []
    years_high_ndvi: List[int] = []  # NDVI mean >= 0.5 = forêt
    HIGH_THRESHOLD = 0.5
    for year in sorted(bands_results.keys()):
        bands = bands_results[year]
        ndvi = bands.get("NDVI") or {}
        evi = bands.get("EVI") or {}
        if ndvi.get("valid") and ndvi.get("stats"):
            mean = ndvi["stats"].get("mean")
            mx = ndvi["stats"].get("max")
            if mean is not None:
                ndvi_means.append(mean)
                years_with_data.append(year)
                if mean >= HIGH_THRESHOLD:
                    years_high_ndvi.append(year)
            if mx is not None:
                ndvi_maxs.append(mx)
        if evi.get("valid") and evi.get("stats"):
            mean = evi["stats"].get("mean")
            if mean is not None:
                evi_means.append(mean)

    if not ndvi_means:
        return {
            "valid": False,
            "reason": "no_valid_yearly_data",
            "n_years_valid": 0,
        }

    n_years = len(ndvi_means)
    decade_mean_ndvi = sum(ndvi_means) / n_years
    decade_max_ndvi = max(ndvi_maxs) if ndvi_maxs else None
    decade_var_ndvi = (
        sum((v - decade_mean_ndvi) ** 2 for v in ndvi_means)
        / n_years)
    decade_std_ndvi = decade_var_ndvi ** 0.5

    # Trend simple : slope linear regression year vs ndvi_mean
    trend_slope = None
    if n_years >= 3:
        ys = years_with_data
        xs_norm = [y - ys[0] for y in ys]
        x_mean = sum(xs_norm) / len(xs_norm)
        y_mean = decade_mean_ndvi
        num = sum(
            (xs_norm[i] - x_mean) * (ndvi_means[i] - y_mean)
            for i in range(n_years))
        den = sum(
            (xs_norm[i] - x_mean) ** 2 for i in range(n_years))
        if den > 0:
            trend_slope = round(num / den, 6)

    return {
        "valid": True,
        "n_years_valid": n_years,
        "years_with_data": years_with_data,
        "n_years_high_ndvi_threshold_05": len(years_high_ndvi),
        "years_high_ndvi_list": years_high_ndvi,
        "decade_mean_ndvi": round(decade_mean_ndvi, 4),
        "decade_max_ndvi": round(decade_max_ndvi, 4)
        if decade_max_ndvi is not None else None,
        "decade_std_ndvi": round(decade_std_ndvi, 4),
        "decade_mean_evi": (
            round(sum(evi_means) / len(evi_means), 4)
            if evi_means else None),
        "trend_slope_ndvi_per_year": trend_slope,
        "phenology_consistency_index_inverse_std": (
            round(1.0 / max(decade_std_ndvi, 0.01), 2)),
    }


def _compute_feeding_zones_summer(
    summer_decade_stats: Dict[str, Any],
    species_thresholds: Dict[str, Any],
) -> Dict[str, Any]:
    """feeding_zones depuis NDVI summer décade (Borowik 2013).

    Anti-générique : score basé sur n_years avec mean NDVI dans optimum
    espèce (consistency annuelle).
    """
    if not summer_decade_stats.get("valid"):
        return {
            "value": None,
            "regime": "DEFERRED_NO_VALID_SUMMER_DATA",
            "primary_reference": "Borowik_2013_EurJWildlRes",
        }
    opt_low = species_thresholds["ndvi_optimal_low"]
    opt_high = species_thresholds["ndvi_optimal_high"]
    n_years = summer_decade_stats["n_years_valid"]
    decade_mean = summer_decade_stats["decade_mean_ndvi"]
    decade_std = summer_decade_stats["decade_std_ndvi"]

    # Score = position dans optimum × consistency
    if opt_low <= decade_mean <= opt_high:
        position_score = 100.0
        regime_pos = "OPTIMAL_RANGE_DECADE_AVERAGE"
    elif decade_mean < opt_low:
        position_score = (
            decade_mean / opt_low * 100.0 if opt_low > 0
            else 0.0)
        regime_pos = "BELOW_OPTIMAL"
    else:
        position_score = max(
            0.0,
            (1.0 - (decade_mean - opt_high)
             / max(1.0 - opt_high, 0.01)) * 100.0)
        regime_pos = "OVER_OPTIMAL"

    # Consistency : low std = consistent feeding zone
    consistency = max(0.0, 100.0 - decade_std * 200.0)

    feeding_score = round(
        position_score * 0.7 + consistency * 0.3, 2)
    if feeding_score >= 75.0:
        regime = "HIGH_QUALITY_FEEDING_ZONE_DECADE"
    elif feeding_score >= 50.0:
        regime = "MODERATE_FEEDING_ZONE"
    elif feeding_score >= 25.0:
        regime = "LOW_FEEDING_ZONE"
    else:
        regime = "POOR_FEEDING_ZONE"
    return {
        "value": feeding_score,
        "unit": "score_0_100_decade_summer_NDVI",
        "regime": regime,
        "regime_position": regime_pos,
        "components": {
            "position_score": round(position_score, 2),
            "consistency_score": round(consistency, 2),
            "decade_mean_ndvi_input": decade_mean,
            "decade_std_ndvi_input": decade_std,
            "n_years_input": n_years,
        },
        "primary_reference": "Borowik_2013_EurJWildlRes",
    }


def _compute_rut_phenology_proxy(
    fall_decade_stats: Dict[str, Any],
    species_canonical: str,
) -> Dict[str, Any]:
    """rut_phenology_proxy depuis NDVI fall (sept-oct).

    Anti-générique strict : c'est un PROXY (pas le rut zones complet
    qui requiert GPS breeding behavior multi-year).
    NDVI fall capture la sénescence prè-rut (Hebblewhite 2008).
    """
    if not fall_decade_stats.get("valid"):
        return {
            "value": None,
            "regime": "DEFERRED_NO_VALID_FALL_DATA",
            "primary_reference": "Hebblewhite_2008_EcolMonogr",
        }
    decade_mean = fall_decade_stats["decade_mean_ndvi"]
    decade_std = fall_decade_stats["decade_std_ndvi"]
    n_years = fall_decade_stats["n_years_valid"]

    # Doctrine : rut optimal phenology = NDVI fall mid-range 0.3-0.5
    # (forage encore disponible mais sénescence avancée)
    if 0.3 <= decade_mean <= 0.5:
        score = 100.0
        regime = "OPTIMAL_RUT_PRE_PHENOLOGY"
    elif decade_mean < 0.3:
        score = max(0.0, decade_mean / 0.3 * 100.0)
        regime = "DORMANT_LATE_RUT_PROXY"
    else:
        score = max(
            0.0, 100.0 - (decade_mean - 0.5) / 0.5 * 80.0)
        regime = "EARLY_FALL_HIGH_GREENNESS"

    # Adjustment : consistency
    consistency = max(0.0, 100.0 - decade_std * 200.0)
    final_score = round(score * 0.7 + consistency * 0.3, 2)
    return {
        "value": final_score,
        "unit": "score_0_100_PROXY_fall_NDVI",
        "regime": regime,
        "doctrinal_caveat": (
            "PROXY ONLY: NDVI fall capture sénescence prè-rut, "
            "PAS le rut zones complet (requires GPS breeding "
            "behavior multi-year). Anti-générique strict."),
        "species_canonical": species_canonical,
        "components": {
            "decade_mean_ndvi_fall": decade_mean,
            "decade_std_ndvi_fall": decade_std,
            "n_years_input": n_years,
            "consistency_score": round(consistency, 2),
        },
        "primary_reference": "Hebblewhite_2008_EcolMonogr",
    }


# ═════════════════════════════════════════════════════════════════════════
# Orchestrateur principal — multi-fenêtre × multi-année × multi-site
# ═════════════════════════════════════════════════════════════════════════
def validate_nasa_ndvi_timeseries_decade(
    site_coordinates: Dict[str, Dict[str, float]],
    end_year: Optional[int] = None,
    years_lookback: int = 5,
    seasonal_windows: Optional[List[str]] = None,
    bands_logical: Optional[List[str]] = None,
    persist: bool = True,
    inter_call_sleep_s: float = 0.3,
    timeout_s: int = 30,
) -> Dict[str, Any]:
    """NASA_NDVI_TIMESERIES_DECADE_Ω · multi-window décade.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412)
      2. Validation coords + bands + seasonal_windows
      3. Pour chaque (site × season × year) : probe MOD13Q1 subset
         (réutilise nasa_ndvi_omega helpers — FUSION ADD-ONLY)
      4. Agrégation yearly stats per band (mean, std, trend)
      5. Calcul feeding_zones_summer + rut_phenology_proxy_fall
      6. Manifest signé SHA-256
      7. Forensic log + persistance + audit
      8. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        _http_get_json_strict_with_redirect_block,
        _compute_band_stats_from_modis_subset,
        NDVI_LOGICAL_TO_BAND,
    )
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        SPECIES_FORAGE_THRESHOLDS_V1,
    )
    require_guardrails_enforced(
        "validate_nasa_ndvi_timeseries_decade")

    if not site_coordinates:
        raise ValueError("SITE_COORDINATES_REQUIRED::empty")
    for sname, coords in site_coordinates.items():
        lat = coords.get("lat") if isinstance(
            coords, dict) else None
        lon = coords.get("lon") if isinstance(
            coords, dict) else None
        if (lat is None or lon is None
                or not (-90.0 <= float(lat) <= 90.0)
                or not (-180.0 <= float(lon) <= 180.0)):
            raise ValueError(
                f"COORDS_INVALID::{sname}::lat={lat},lon={lon}")

    if end_year is None:
        end_year = datetime.now(timezone.utc).year - 1
    start_year = end_year - max(years_lookback, 1) + 1

    seasonal_windows = seasonal_windows or [
        "summer_growing_peak", "fall_pre_rut"]
    seasonal_validated = [
        w for w in seasonal_windows
        if w in SEASONAL_WINDOWS_DOCTRINAL]
    seasonal_unknown = [
        w for w in seasonal_windows
        if w not in SEASONAL_WINDOWS_DOCTRINAL]

    bands_logical = bands_logical or ["NDVI", "EVI"]
    bands_validated = [
        b for b in bands_logical if b in NDVI_LOGICAL_TO_BAND]
    bands_unknown = [
        b for b in bands_logical
        if b not in NDVI_LOGICAL_TO_BAND]

    # Filtre : on ne probe que MOD13Q1 bands (NDVI, EVI, VI_QUALITY)
    bands_mod13q1_only = [
        b for b in bands_validated
        if NDVI_LOGICAL_TO_BAND[b]["product"] == "MOD13Q1"]
    bands_other_product = [
        b for b in bands_validated
        if NDVI_LOGICAL_TO_BAND[b]["product"] != "MOD13Q1"]

    t_total = time.time()
    site_results: Dict[str, Dict[str, Any]] = {}
    n_calls_made = 0
    n_calls_success = 0
    n_calls_failed = 0
    species_to_site_map = {
        "espece_a": "cerf", "espece_b": "orignal",
        "espece_c": "ours", "espece_d": "dindon",
        "espece_e": "wapiti",
    }

    for site_name, coords in site_coordinates.items():
        lat = float(coords["lat"])
        lon = float(coords["lon"])
        species_canonical = species_to_site_map.get(
            site_name, "unknown")
        thresholds = SPECIES_FORAGE_THRESHOLDS_V1.get(
            species_canonical)
        seasons_data: Dict[str, Any] = {}

        for season_name in seasonal_validated:
            window = SEASONAL_WINDOWS_DOCTRINAL[season_name]
            yearly_results: Dict[int, Dict[str, Any]] = {}
            for year in range(start_year, end_year + 1):
                yearly_bands: Dict[str, Any] = {}
                start_modis = _modis_a_year_doy(
                    year, window["doy_start"])
                end_modis = _modis_a_year_doy(
                    year, window["doy_end"])
                for band_logical in bands_mod13q1_only:
                    n_calls_made += 1
                    band_canonical = (
                        NDVI_LOGICAL_TO_BAND[band_logical][
                            "band"])
                    url = (
                        f"https://modis.ornl.gov/rst/api/v1/"
                        f"MOD13Q1/subset?"
                        f"latitude={lat}&longitude={lon}"
                        f"&band={band_canonical}"
                        f"&startDate={start_modis}"
                        f"&endDate={end_modis}"
                        f"&kmAboveBelow=0&kmLeftRight=0")
                    probe = (
                        _http_get_json_strict_with_redirect_block(
                            url, timeout_s=timeout_s))
                    if (probe["http_status"] != 200
                            or not probe["body_is_json"]):
                        yearly_bands[band_logical] = {
                            "valid": False,
                            "reason": (
                                probe.get("reason")
                                or f"http_{probe['http_status']}"),
                        }
                        n_calls_failed += 1
                        continue
                    parsed = probe["parsed_json"] or {}
                    stats = (
                        _compute_band_stats_from_modis_subset(
                            parsed.get("subset", []),
                            scale_factor=0.0001,
                            nodata_value=-3000))
                    if stats.get("interpretation") == (
                            "no_valid_values"):
                        yearly_bands[band_logical] = {
                            "valid": False,
                            "reason": "all_nodata",
                            "stats": stats,
                        }
                        n_calls_failed += 1
                    else:
                        yearly_bands[band_logical] = {
                            "valid": True,
                            "stats": stats,
                        }
                        n_calls_success += 1
                    if inter_call_sleep_s > 0:
                        time.sleep(inter_call_sleep_s)
                yearly_results[year] = yearly_bands

            # Aggregate
            decade_stats = _aggregate_yearly_stats(yearly_results)
            seasons_data[season_name] = {
                "window_metadata": window,
                "yearly_results": yearly_results,
                "decade_aggregated_stats": decade_stats,
            }

        # Compute outputs derived
        feeding_decade = None
        rut_proxy = None
        if (seasons_data.get("summer_growing_peak")
                and thresholds is not None):
            summer_stats = seasons_data[
                "summer_growing_peak"]["decade_aggregated_stats"]
            feeding_decade = _compute_feeding_zones_summer(
                summer_stats, thresholds)
        if seasons_data.get("fall_pre_rut"):
            fall_stats = seasons_data[
                "fall_pre_rut"]["decade_aggregated_stats"]
            rut_proxy = _compute_rut_phenology_proxy(
                fall_stats, species_canonical)

        site_results[site_name] = {
            "lat": lat, "lon": lon,
            "species_canonical": species_canonical,
            "seasons_data": seasons_data,
            "computed_outputs_decade": {
                "feeding_zones_summer_decade": feeding_decade,
                "rut_phenology_proxy_fall": rut_proxy,
            },
        }
        log_forensic_event(
            scope="ENDPOINT_PROBES",
            event="NASA_NDVI_TIMESERIES_DECADE_Ω",
            details={
                "provider": "NASA_NDVI_DECADE",
                "endpoint": (
                    "https://modis.ornl.gov/rst/api/v1/"
                    "MOD13Q1/subset"),
                "site": site_name,
                "species": species_canonical,
                "n_seasons": len(seasonal_validated),
                "n_years": years_lookback,
                "n_bands": len(bands_mod13q1_only),
                "feeding_score": (
                    feeding_decade.get("value")
                    if feeding_decade else None),
                "rut_proxy_score": (
                    rut_proxy.get("value")
                    if rut_proxy else None),
            },
            persist=True,
        )

    # Verdict
    if (n_calls_success == n_calls_made and n_calls_made > 0):
        verdict = "NASA_NDVI_TIMESERIES_ALL_VALID"
        valid = True
    elif n_calls_success > n_calls_failed:
        verdict = (
            f"NASA_NDVI_TIMESERIES_MAJORITY_VALID::"
            f"{n_calls_success}_of_{n_calls_made}")
        valid = True
    elif n_calls_success > 0:
        verdict = (
            f"NASA_NDVI_TIMESERIES_PARTIAL::"
            f"{n_calls_success}_of_{n_calls_made}")
        valid = False
    else:
        verdict = "NASA_NDVI_TIMESERIES_ALL_INVALID"
        valid = False

    payload = {
        "manifest_id": "NASA_NDVI_TIMESERIES_DECADE_Ω",
        "ordre": "P3_NASA_NDVI_TIMESERIES_DECADE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "valid": valid,
        "verdict": verdict,
        "provider": "NASA_NDVI_DECADE",
        "provider_physical": "NASA_MOD13Q1_ORNL_MULTISEASON",
        "endpoint": (
            "https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset"),
        "temporal_range": {
            "start_year": start_year,
            "end_year": end_year,
            "n_years": end_year - start_year + 1,
        },
        "seasonal_windows_validated": seasonal_validated,
        "seasonal_windows_unknown": seasonal_unknown,
        "bands_mod13q1_used": bands_mod13q1_only,
        "bands_deferred_other_product": bands_other_product,
        "bands_unknown": bands_unknown,
        "n_sites_total": len(site_coordinates),
        "n_calls_made": n_calls_made,
        "n_calls_success": n_calls_success,
        "n_calls_failed": n_calls_failed,
        "site_results": site_results,
        "outputs_unblocked_via_this_validation": [
            "feeding_zones_summer_decade (Borowik 2013)",
            "rut_phenology_proxy_fall (Hebblewhite 2008 PROXY)",
        ],
        "outputs_still_deferred": [
            "rut_zones_FULL_requires_GPS_breeding_behavior",
            "pressure_sensitive_zones_anthropogenic_required",
        ],
        "scientific_references_peer_reviewed": [
            ("Borowik et al. (2013). Eur J Wildl Res, 59:675-682. "
             "DOI:10.1007/s10344-013-0720-0"),
            ("Pettorelli et al. (2005). TREE, 20(9):503-510. "
             "DOI:10.1016/j.tree.2005.05.011"),
            ("Garroutte et al. (2016). Remote Sensing, 8(5):404. "
             "DOI:10.3390/rs8050404"),
            ("Hebblewhite et al. (2008). Ecol Monogr, 78:141-166. "
             "DOI:10.1890/06-1708.1"),
        ],
        "anti_generique_strict": True,
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
        NDVI_DECADE_ROOT.mkdir(parents=True, exist_ok=True)
        if NDVI_DECADE_VALIDATION_PATH.exists():
            try:
                state = json.loads(
                    NDVI_DECADE_VALIDATION_PATH.read_text(
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
        NDVI_DECADE_VALIDATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            NDVI_DECADE_VALIDATION_PATH)
        persisted["overlay_size_bytes"] = (
            NDVI_DECADE_VALIDATION_PATH.stat().st_size)
        persisted["n_validations_history"] = state["n_validations"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "NASA_NDVI_TIMESERIES_DECADE",
            "ordre": "P3_NASA_NDVI_TIMESERIES_DECADE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": "NASA_NDVI_DECADE",
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "n_sites_total": len(site_coordinates),
            "n_calls_success": n_calls_success,
            "n_calls_failed": n_calls_failed,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    return payload


def get_ndvi_decade_status() -> Dict[str, Any]:
    """État actuel du timeseries décade (read-only)."""
    if not NDVI_DECADE_VALIDATION_PATH.exists():
        return {
            "manifest_id": "NASA_NDVI_TIMESERIES_DECADE_STATUS_Ω",
            "current_status": "NOT_VALIDATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        NDVI_DECADE_VALIDATION_PATH.read_text(encoding="utf-8"))
    last = state["history"][-1] if state.get("history") else None
    return {
        "manifest_id": "NASA_NDVI_TIMESERIES_DECADE_STATUS_Ω",
        "current_status": (
            "VALIDATED_OPERATIONAL" if last
            and last.get("valid") else "NOT_VALIDATED"),
        "n_validations_history": state.get("n_validations", 0),
        "last_manifest_sha256": state.get("last_manifest_sha256"),
        "last_verdict": state.get("last_verdict"),
        "last_updated_utc": state.get("last_updated_utc"),
        "last_summary": (
            {
                "verdict": last.get("verdict"),
                "n_sites_total": last.get("n_sites_total"),
                "n_calls_success": last.get("n_calls_success"),
                "temporal_range": last.get("temporal_range"),
            } if last else None),
        "overlay_path": str(NDVI_DECADE_VALIDATION_PATH),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "NDVI_DECADE_ROOT",
    "NDVI_DECADE_VALIDATION_PATH",
    "SEASONAL_WINDOWS_DOCTRINAL",
    "validate_nasa_ndvi_timeseries_decade",
    "get_ndvi_decade_status",
]
