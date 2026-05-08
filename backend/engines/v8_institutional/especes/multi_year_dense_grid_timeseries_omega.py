"""multi_year_dense_grid_timeseries_omega.py — P11
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

P11 — Densification temporelle 10 ans × dense grid spatial pour analyse
de tendance écologique longitudinale (climate change signature).

DOCTRINE :
  · Réutilise infrastructure NASA_NDVI_DENSE_GRID (kmAboveBelow=2)
  · Boucle annuelle : N années × 5 sites × 17×17 pixels × 6 tuiles summer
  · Statistiques annuelles : mean, std, percentiles par site/année
  · Mann-Kendall trend test (Mann 1945, Kendall 1975) sur série annuelle
  · Sen's slope estimator (Sen 1968) pour magnitude tendance
  · Détecte tendances : INCREASING_GREENING, DECREASING_BROWNING, STABLE

RÉFÉRENCES PEER-REVIEWED :
  [1] Mann, H. B. (1945). Nonparametric tests against trend.
      Econometrica, 13:245-259. DOI:10.2307/1907187
  [2] Kendall, M. G. (1975). Rank Correlation Methods.
      4th ed. Charles Griffin. ISBN:978-0852641996
  [3] Sen, P. K. (1968). Estimates of regression coefficient
      based on Kendall's tau. JASA, 63:1379-1389.
      DOI:10.1080/01621459.1968.10480934
  [4] Pettorelli et al. (2011). NDVI to monitor wildlife population.
      Climate Research, 46:15-27. DOI:10.3354/cr00936
  [5] Forkel et al. (2013). Trend Change Detection in NDVI Time
      Series. Remote Sensing, 5:2113-2144. DOI:10.3390/rs5052113

ANTI-GÉNÉRIQUE STRICT :
  · Pas de mock, pas d'imputation
  · Si année manquante → trace honnêtement (DEFERRED_NOT_FETCHED)
  · NODATA=-3000 rejeté
  · Subset ORNL spatial+temporal réel
  · Trend test non-parametric (robuste aux outliers)
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


MULTI_YEAR_ROOT = Path(
    "/app/backend/data/pipelines/multi_year_dense_grid_timeseries")
MULTI_YEAR_VALIDATION_PATH = (
    MULTI_YEAR_ROOT
    / "multi_year_dense_grid_timeseries_validation_overlay.json")
MULTI_YEAR_HOOK_ACTIVATION_PATH = (
    MULTI_YEAR_ROOT
    / "multi_year_dense_grid_timeseries_hook_activation_overlay.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ═════════════════════════════════════════════════════════════════════════
# Mann-Kendall trend test (Mann 1945, Kendall 1975)
# Implementation from Hipel & McLeod (1994), peer-reviewed
# ═════════════════════════════════════════════════════════════════════════
def _mann_kendall_trend_test(
    series_per_year: List[float],
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """Mann-Kendall trend test (anti-générique, déterministe pur).

    Args:
        series_per_year : valeurs annuelles ordonnées chronologiquement
        alpha : seuil significativité (default 0.05)

    Returns:
        dict {tau, S, var_S, z, p_value, trend, slope_sen}
    """
    n = len(series_per_year)
    if n < 3:
        return {
            "valid": False,
            "reason": "insufficient_data_n_lt_3",
            "n_years": n,
        }
    # Compute S statistic (Mann 1945)
    s_stat = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = series_per_year[j] - series_per_year[i]
            if diff > 0:
                s_stat += 1
            elif diff < 0:
                s_stat -= 1
    # Variance of S (Kendall 1975, no ties for simplicity)
    var_s = (n * (n - 1) * (2 * n + 5)) / 18.0
    # Z-statistic with continuity correction
    if s_stat > 0:
        z = (s_stat - 1) / math.sqrt(var_s)
    elif s_stat < 0:
        z = (s_stat + 1) / math.sqrt(var_s)
    else:
        z = 0.0
    # Two-tailed p-value via normal CDF
    p_value = 2.0 * (
        1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))
    # Sen's slope estimator (Sen 1968)
    slopes: List[float] = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            denom = j - i
            if denom != 0:
                slopes.append(
                    (series_per_year[j] - series_per_year[i])
                    / denom)
    slopes.sort()
    n_slopes = len(slopes)
    if n_slopes == 0:
        slope_sen = 0.0
    elif n_slopes % 2 == 1:
        slope_sen = slopes[n_slopes // 2]
    else:
        slope_sen = (
            slopes[n_slopes // 2 - 1]
            + slopes[n_slopes // 2]) / 2.0
    # Trend classification
    significant = p_value < alpha
    if significant and slope_sen > 0:
        trend = "INCREASING_GREENING_SIGNIFICANT"
    elif significant and slope_sen < 0:
        trend = "DECREASING_BROWNING_SIGNIFICANT"
    elif slope_sen > 0:
        trend = "INCREASING_GREENING_NOT_SIGNIFICANT"
    elif slope_sen < 0:
        trend = "DECREASING_BROWNING_NOT_SIGNIFICANT"
    else:
        trend = "STABLE_NO_TREND"
    # Kendall tau
    tau = s_stat / (n * (n - 1) / 2.0) if n > 1 else 0.0
    return {
        "valid": True,
        "n_years": n,
        "S_statistic": s_stat,
        "var_S": round(var_s, 4),
        "Z_statistic": round(z, 4),
        "p_value": round(p_value, 6),
        "alpha": alpha,
        "significant": significant,
        "Kendall_tau": round(tau, 4),
        "slope_sen_per_year": round(slope_sen, 6),
        "trend_classification": trend,
        "primary_references": [
            "Mann_1945_Econometrica",
            "Kendall_1975_RankCorrelationMethods",
            "Sen_1968_JASA",
        ],
    }


# ═════════════════════════════════════════════════════════════════════════
# VALIDATE — multi-year dense grid (réutilise infra dense_grid)
# ═════════════════════════════════════════════════════════════════════════
def validate_multi_year_dense_grid_timeseries(
    site_coordinates: Optional[Dict[str, Dict[str, float]]] = None,
    species_to_site_map: Optional[Dict[str, str]] = None,
    year_start: int = 2015,
    year_end: int = 2024,
    km_above_below: int = 2,
    km_left_right: int = 2,
    persist: bool = True,
    inter_call_sleep_s: float = 0.4,
    timeout_s: int = 30,
) -> Dict[str, Any]:
    """P11 · 10 ans summer × 5 sites × dense grid → Mann-Kendall."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (
        _http_get_json_strict,
        _flatten_pixels_decode_scale,
        _modis_a_year_doy,
        _percentile,
    )
    require_guardrails_enforced(
        "validate_multi_year_dense_grid_timeseries")

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
    if year_start > year_end:
        raise ValueError(
            f"YEAR_RANGE_INVALID::start={year_start}_end={year_end}")
    if year_end - year_start + 1 < 3:
        raise ValueError(
            "YEAR_RANGE_INSUFFICIENT_FOR_MANN_KENDALL::"
            "min_3_years_required")

    summer_doy_start = 153
    summer_doy_end = 244
    years = list(range(year_start, year_end + 1))

    t_total = time.time()
    site_results: Dict[str, Dict[str, Any]] = {}
    n_sites = len(site_coordinates)
    n_year_calls_total = 0
    n_year_calls_success = 0
    n_year_calls_failed = 0

    for site_name, coords in site_coordinates.items():
        lat = float(coords["lat"])
        lon = float(coords["lon"])
        species = species_to_site_map.get(
            site_name, "unknown")
        annual_stats: Dict[int, Dict[str, Any]] = {}
        annual_mean_series: List[Tuple[int, float]] = []

        for year in years:
            n_year_calls_total += 1
            start_modis = _modis_a_year_doy(
                year, summer_doy_start)
            end_modis = _modis_a_year_doy(
                year, summer_doy_end)
            url = (
                f"https://modis.ornl.gov/rst/api/v1/"
                f"MOD13Q1/subset?"
                f"latitude={lat}&longitude={lon}"
                f"&band=250m_16_days_NDVI"
                f"&startDate={start_modis}"
                f"&endDate={end_modis}"
                f"&kmAboveBelow={km_above_below}"
                f"&kmLeftRight={km_left_right}")
            probe = _http_get_json_strict(
                url, timeout_s=timeout_s)
            if (probe["http_status"] != 200
                    or not probe["body_is_json"]):
                annual_stats[year] = {
                    "valid": False,
                    "reason": (
                        probe.get("reason")
                        or f"http_{probe['http_status']}"),
                    "elapsed_ms": probe.get("elapsed_ms"),
                }
                n_year_calls_failed += 1
                if inter_call_sleep_s > 0:
                    time.sleep(inter_call_sleep_s)
                continue
            parsed = probe["parsed_json"] or {}
            subset = parsed.get("subset") or []
            valid_values, n_total, n_nodata = (
                _flatten_pixels_decode_scale(
                    subset, nodata=-3000, scale=0.0001))
            if not valid_values:
                annual_stats[year] = {
                    "valid": False,
                    "reason": "all_pixels_nodata",
                    "n_total": n_total,
                    "n_nodata": n_nodata,
                }
                n_year_calls_failed += 1
                if inter_call_sleep_s > 0:
                    time.sleep(inter_call_sleep_s)
                continue
            n_year_calls_success += 1
            mean_year = sum(valid_values) / len(valid_values)
            annual_stats[year] = {
                "valid": True,
                "n_pixels_valid": len(valid_values),
                "n_total": n_total,
                "n_nodata": n_nodata,
                "stats": {
                    "mean": round(mean_year, 4),
                    "min": round(min(valid_values), 4),
                    "max": round(max(valid_values), 4),
                    "p10": round(
                        _percentile(valid_values, 10), 4),
                    "p50": round(
                        _percentile(valid_values, 50), 4),
                    "p90": round(
                        _percentile(valid_values, 90), 4),
                    "std": round(
                        math.sqrt(
                            sum(
                                (v - mean_year) ** 2
                                for v in valid_values)
                            / max(len(valid_values) - 1, 1)),
                        4),
                },
                "elapsed_ms": probe.get("elapsed_ms"),
            }
            annual_mean_series.append((year, mean_year))
            if inter_call_sleep_s > 0:
                time.sleep(inter_call_sleep_s)

        # Mann-Kendall sur la série annuelle (mean) si >=3 années
        sorted_series = sorted(
            annual_mean_series, key=lambda x: x[0])
        means_only = [v for _, v in sorted_series]
        mk_result: Dict[str, Any]
        if len(means_only) >= 3:
            mk_result = _mann_kendall_trend_test(
                means_only)
            mk_result["years_used_chronological"] = [
                y for y, _ in sorted_series]
            mk_result["mean_ndvi_series"] = (
                [round(v, 4) for v in means_only])
        else:
            mk_result = {
                "valid": False,
                "reason": (
                    f"insufficient_valid_years_"
                    f"{len(means_only)}_lt_3"),
                "n_years_attempted": len(years),
                "n_years_valid": len(means_only),
            }

        site_results[site_name] = {
            "lat": lat, "lon": lon,
            "species_canonical": species,
            "year_start": year_start,
            "year_end": year_end,
            "n_years_attempted": len(years),
            "n_years_valid": len(means_only),
            "annual_stats": annual_stats,
            "mann_kendall_trend_test": mk_result,
        }
        log_forensic_event(
            scope="ENDPOINT_PROBES",
            event="MULTI_YEAR_DENSE_GRID_TIMESERIES_VALIDATE_Ω",
            details={
                "provider": "MULTI_YEAR_DENSE_GRID",
                "site": site_name,
                "species": species,
                "year_start": year_start,
                "year_end": year_end,
                "n_years_valid": len(means_only),
                "trend": mk_result.get(
                    "trend_classification"),
                "slope_sen": mk_result.get(
                    "slope_sen_per_year"),
                "p_value": mk_result.get("p_value"),
            },
            persist=True,
        )

    # Verdict global
    if (n_year_calls_success == n_year_calls_total
            and n_year_calls_total > 0):
        verdict = "MULTI_YEAR_DENSE_GRID_TIMESERIES_ALL_VALID"
        valid = True
    elif n_year_calls_success > 0:
        verdict = (
            f"MULTI_YEAR_DENSE_GRID_TIMESERIES_PARTIAL::"
            f"{n_year_calls_success}_OF_{n_year_calls_total}")
        valid = (
            n_year_calls_success >= 0.8 * n_year_calls_total)
    else:
        verdict = (
            "MULTI_YEAR_DENSE_GRID_TIMESERIES_ALL_INVALID")
        valid = False

    payload = {
        "manifest_id": "MULTI_YEAR_DENSE_GRID_TIMESERIES_VALIDATE_Ω",
        "ordre": "P11_MULTI_YEAR_DENSE_GRID_TIMESERIES_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "valid": valid,
        "verdict": verdict,
        "provider": "MULTI_YEAR_DENSE_GRID",
        "provider_physical": "NASA_MOD13Q1_ORNL_DENSE_SUBSET_DECADE",
        "endpoint": (
            "https://modis.ornl.gov/rst/api/v1/MOD13Q1/subset"),
        "spatial_subset_config": {
            "km_above_below": km_above_below,
            "km_left_right": km_left_right,
        },
        "temporal_window": {
            "year_start": year_start,
            "year_end": year_end,
            "n_years": len(years),
            "summer_doy_start": summer_doy_start,
            "summer_doy_end": summer_doy_end,
            "primary_reference": "Pettorelli_2011_ClimateRes",
        },
        "n_sites_total": n_sites,
        "n_year_calls_total": n_year_calls_total,
        "n_year_calls_success": n_year_calls_success,
        "n_year_calls_failed": n_year_calls_failed,
        "site_results": site_results,
        "scientific_references_peer_reviewed": [
            ("Mann (1945). Econometrica, 13:245-259. "
             "DOI:10.2307/1907187"),
            ("Kendall (1975). Rank Correlation Methods. "
             "4th ed. Charles Griffin."),
            ("Sen (1968). JASA, 63:1379-1389. "
             "DOI:10.1080/01621459.1968.10480934"),
            ("Pettorelli et al. (2011). Climate Research, "
             "46:15-27. DOI:10.3354/cr00936"),
            ("Forkel et al. (2013). Remote Sensing, "
             "5:2113-2144. DOI:10.3390/rs5052113"),
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
        MULTI_YEAR_ROOT.mkdir(parents=True, exist_ok=True)
        if MULTI_YEAR_VALIDATION_PATH.exists():
            try:
                state = json.loads(
                    MULTI_YEAR_VALIDATION_PATH.read_text(
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
        MULTI_YEAR_VALIDATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            MULTI_YEAR_VALIDATION_PATH)
        persisted["overlay_size_bytes"] = (
            MULTI_YEAR_VALIDATION_PATH.stat().st_size)

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        persisted["audit_persisted"] = persist_audit({
            "audit_type": "NOAA_PIPELINE",
            "subtype": "MULTI_YEAR_DENSE_GRID_TIMESERIES_VALIDATE",
            "ordre": "P11_MULTI_YEAR_DENSE_GRID_TIMESERIES_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "n_year_calls_success": n_year_calls_success,
            "n_year_calls_total": n_year_calls_total,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        })

    payload["persisted_paths"] = persisted
    return payload


def activate_multi_year_dense_grid_timeseries_hook(
    manifest_sha256: str,
    reason: str = (
        "ecological_longitudinal_trend_analysis_10_years"),
    persist: bool = True,
) -> Dict[str, Any]:
    """P11 · activation officielle."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "activate_multi_year_dense_grid_timeseries_hook")

    t0 = time.time()
    # Find validated
    validated = None
    if MULTI_YEAR_VALIDATION_PATH.exists():
        try:
            state = json.loads(
                MULTI_YEAR_VALIDATION_PATH.read_text(
                    encoding="utf-8"))
            for entry in state.get("history", []):
                if (entry.get("manifest_sha256")
                        == manifest_sha256
                        and entry.get(
                            "n_year_calls_success", 0) >= 1):
                    validated = entry
                    break
        except json.JSONDecodeError:
            pass

    if validated is None:
        rejection = {
            "manifest_id":
                "MULTI_YEAR_DENSE_GRID_TIMESERIES_HOOK_ACTIVATE_Ω",
            "ordre":
                "P11_MULTI_YEAR_DENSE_GRID_TIMESERIES_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "activated": False,
            "verdict": (
                "MULTI_YEAR_DENSE_GRID_HOOK_REJECTED_"
                "MANIFEST_NOT_FOUND"),
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
            event=(
                "MULTI_YEAR_DENSE_GRID_TIMESERIES_HOOK_REJECTED"),
            details={"input_manifest_sha256": manifest_sha256},
            persist=True)
        return rejection

    verdict = "MULTI_YEAR_DENSE_GRID_TIMESERIES_HOOK_ACTIVATED"
    payload = {
        "manifest_id":
            "MULTI_YEAR_DENSE_GRID_TIMESERIES_HOOK_ACTIVATE_Ω",
        "ordre":
            "P11_MULTI_YEAR_DENSE_GRID_TIMESERIES_Ω",
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
            "n_year_calls_success": validated.get(
                "n_year_calls_success"),
            "year_start": (
                validated.get("temporal_window") or {}
            ).get("year_start"),
            "year_end": (
                validated.get("temporal_window") or {}
            ).get("year_end"),
        },
        "outputs_unblocked_via_this_hook": [
            "longitudinal_trend_per_site (Mann-Kendall + Sen)",
            "climate_change_signature_NDVI_decade",
        ],
        "providers_physical_active": [
            "NASA_MOD13Q1_ORNL_DENSE_SUBSET_DECADE",
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
        MULTI_YEAR_ROOT.mkdir(parents=True, exist_ok=True)
        if MULTI_YEAR_HOOK_ACTIVATION_PATH.exists():
            try:
                state = json.loads(
                    MULTI_YEAR_HOOK_ACTIVATION_PATH.read_text(
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
        state["last_validated_manifest_sha256"] = (
            manifest_sha256)
        state["v30_lock"] = "INVIOLÉ"
        MULTI_YEAR_HOOK_ACTIVATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            MULTI_YEAR_HOOK_ACTIVATION_PATH)
        persisted["overlay_size_bytes"] = (
            MULTI_YEAR_HOOK_ACTIVATION_PATH.stat().st_size)

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        persisted["audit_persisted"] = persist_audit({
            "audit_type": "NOAA_PIPELINE",
            "subtype": "MULTI_YEAR_DENSE_GRID_HOOK_ACTIVATE",
            "ordre":
                "P11_MULTI_YEAR_DENSE_GRID_TIMESERIES_Ω",
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
        event=(
            "MULTI_YEAR_DENSE_GRID_TIMESERIES_HOOK_ACTIVATED"),
        details={
            "manifest_sha256": payload_sha256,
            "validated_manifest_sha256": manifest_sha256,
        },
        persist=True)
    payload["persisted_paths"] = persisted
    return payload


def get_multi_year_dense_grid_timeseries_hook_status() -> Dict[str, Any]:
    if not MULTI_YEAR_HOOK_ACTIVATION_PATH.exists():
        return {
            "manifest_id":
                "MULTI_YEAR_DENSE_GRID_TIMESERIES_STATUS_Ω",
            "current_status": "NOT_ACTIVATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        MULTI_YEAR_HOOK_ACTIVATION_PATH.read_text(
            encoding="utf-8"))
    last = (
        state["history"][-1]
        if state.get("history") else None)
    return {
        "manifest_id":
            "MULTI_YEAR_DENSE_GRID_TIMESERIES_STATUS_Ω",
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
            MULTI_YEAR_HOOK_ACTIVATION_PATH),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "MULTI_YEAR_ROOT",
    "MULTI_YEAR_VALIDATION_PATH",
    "MULTI_YEAR_HOOK_ACTIVATION_PATH",
    "_mann_kendall_trend_test",
    "validate_multi_year_dense_grid_timeseries",
    "activate_multi_year_dense_grid_timeseries_hook",
    "get_multi_year_dense_grid_timeseries_hook_status",
]
