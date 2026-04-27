#!/usr/bin/env python3
"""
collect_xix_p1_diagnostic.py — PHASE_XIX_P1_DIAGNOSTIC_Ω
================================================================================
Collecte READ-ONLY des métriques institutionnelles XIX-P1 + XIX-P2.

Aucun recalcul, aucune modification de seuils — diagnostic strict.
"""
from __future__ import annotations
import asyncio
import json
import os
import statistics
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

sys.path.insert(0, "/app/backend")
from fastapi import Response  # noqa: E402

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422
SPECIES_LIST = ["chevreuil", "orignal", "wapiti", "ours_noir", "dindon_sauvage"]
# Aliases acceptés par le moteur backend
SPECIES_API_ALIASES = {
    "chevreuil": "chevreuil",
    "orignal": "orignal",
    "wapiti": "wapiti",
    "ours_noir": "ours",
    "dindon_sauvage": "dindon",
}


def _quantiles(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"min": None, "q1": None, "median": None, "q3": None, "max": None, "n": 0}
    s = sorted(values)
    n = len(s)
    return {
        "min": round(s[0], 4),
        "q1": round(s[max(0, n // 4)], 4),
        "median": round(s[n // 2], 4),
        "q3": round(s[min(n - 1, (3 * n) // 4)], 4),
        "max": round(s[-1], 4),
        "n": n,
    }


async def collect_per_species(species_canon: str, month: int = 10, hour: int = 16) -> Dict[str, Any]:
    """Collecte les métriques d'une espèce via le pipeline complet."""
    # purge cache
    pkl = "/app/backend/cache/territoire_bundle.pkl"
    if os.path.exists(pkl):
        os.remove(pkl)
    from engines.v8_institutional import v20_performance_bundle as vp
    vp._CACHE.clear()
    from engines.v8_institutional.predictive_omega_v2 import reset_dataset_cache
    from engines.v8_institutional.ecological_orchestrator_omega import reset_heatmap_cache
    reset_dataset_cache()
    reset_heatmap_cache()

    species_api = SPECIES_API_ALIASES.get(species_canon, species_canon)
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
    r = Response()
    bundle = await v20_territoire_bundle(
        response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species=species_api,
        month=month, hour=hour, wind_deg=225.0, wind_speed=15.0,
    )

    # ─── XIX-P1 stats
    xix1 = bundle.get("origine_externe_filter_stats") or {}
    xix2 = bundle.get("origine_externe_inversion_stats") or {}

    # Distributions GPS sur l'ensemble des corridors (kept + rejected)
    all_corridors = (bundle.get("corridors") or []) \
        + [c for c in (bundle.get("corridors_rejected_origine_externe_xix") or [])]
    # Note : rejected_audit ne contient pas les paths complets, on reconstruit depuis predictive_v2
    densities = []
    weighted_hits = []
    for c in (bundle.get("corridors") or []):
        pv2 = c.get("predictive_omega_v2") or {}
        m = pv2.get("metrics") or {}
        if m.get("gps_density_ratio") is not None:
            densities.append(float(m["gps_density_ratio"]))
        if m.get("gps_weighted_hits") is not None:
            weighted_hits.append(float(m["gps_weighted_hits"]))
    # Aussi extraire des rejected XIX-P1 (qui ont les valeurs)
    for r_obj in (bundle.get("corridors_rejected_origine_externe_xix") or []):
        if r_obj.get("gps_density_ratio") is not None:
            densities.append(float(r_obj["gps_density_ratio"]))
        if r_obj.get("gps_weighted_hits") is not None:
            weighted_hits.append(float(r_obj["gps_weighted_hits"]))

    rejected_reasons = xix1.get("rejected_reasons") or {}

    return {
        "species_canonical": species_canon,
        "species_api": species_api,
        "month": month,
        "hour": hour,
        "total_corridors_v30": xix1.get("total_input"),
        "origin_external_passed_count": xix1.get("total_kept"),
        "origin_external_failed_count": xix1.get("total_rejected"),
        "origin_external_failed_outside_crown": rejected_reasons.get("OUTSIDE_CROWN", 0),
        "origin_external_failed_low_density": rejected_reasons.get("LOW_DENSITY", 0),
        "origin_external_failed_low_hits": rejected_reasons.get("LOW_HITS", 0),
        "origin_external_failed_missing_predictive": rejected_reasons.get("MISSING_PREDICTIVE_V2_METRICS", 0),
        "origin_external_inversion_applied_count": xix2.get("inverted_count"),
        "origin_external_inversion_skipped_count": xix2.get("skipped_count"),
        "rate_pct_xix_p1": xix1.get("rate_pct"),
        "rate_pct_xix_p2_inversion": xix2.get("rate_pct"),
        "config_xix_p1": xix1.get("config"),
        "gps_density_ratio_distribution": _quantiles(densities),
        "gps_weighted_hits_distribution": _quantiles(weighted_hits),
        "downstream_eco_input_after_xix_p1": (bundle.get("ecological_orchestrator_stats") or {}).get("total_input"),
        "downstream_eco_kept": (bundle.get("ecological_orchestrator_stats") or {}).get("total_output"),
        "downstream_vitaux_input": (bundle.get("corridors_vitaux_omega_stats") or {}).get("total_input"),
        "downstream_vitaux_kept": (bundle.get("corridors_vitaux_omega_stats") or {}).get("total_kept"),
        "final_corridors_visible_count": len(bundle.get("corridors") or []),
    }


async def main():
    started = datetime.now(timezone.utc).isoformat()
    per_species: Dict[str, Any] = {}
    global_densities: List[float] = []
    global_hits: List[float] = []
    g_total = g_passed = g_failed = g_outside = g_low_d = g_low_h = g_inv = 0
    for sp in SPECIES_LIST:
        res = await collect_per_species(sp)
        per_species[sp] = res
        d = res.get("gps_density_ratio_distribution") or {}
        h = res.get("gps_weighted_hits_distribution") or {}
        # Global aggregation needs raw values not just quantiles → re-extract
        # We collect from per_species totals
        g_total += int(res.get("total_corridors_v30") or 0)
        g_passed += int(res.get("origin_external_passed_count") or 0)
        g_failed += int(res.get("origin_external_failed_count") or 0)
        g_outside += int(res.get("origin_external_failed_outside_crown") or 0)
        g_low_d += int(res.get("origin_external_failed_low_density") or 0)
        g_low_h += int(res.get("origin_external_failed_low_hits") or 0)
        g_inv += int(res.get("origin_external_inversion_applied_count") or 0)

    config_first = next(iter(per_species.values()), {}).get("config_xix_p1") or {}

    # ─── État API TERRITOIRE_CORRIDORS
    import urllib.request
    api_base = None
    for line in open("/app/frontend/.env").read().splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            api_base = line.split("=", 1)[1].strip()
            break
    api_url = f"{api_base}/api/v20/territoire/bundle?lat={OFFICIAL_LAT}&lon={OFFICIAL_LNG}&species=orignal&month=10&hour=16"
    api_status = {"endpoint": api_url}
    try:
        t0 = time.time()
        req = urllib.request.Request(api_url, headers={"User-Agent": "BCE-4X-Diagnostic/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read()
            api_status["http_status"] = resp.status
            api_status["payload_size_bytes"] = len(payload)
            api_status["latency_ms"] = round((time.time() - t0) * 1000, 1)
            data = json.loads(payload)
            corrs = data.get("corridors") or []
            api_status["corridors_in_response"] = len(corrs)
            api_status["origin_external_passed_in_response"] = sum(
                1 for c in corrs if c.get("origin_external_passed") is True
            )
            # Stats détaillées du pipeline observées via l'API
            xix1_api = data.get("origine_externe_filter_stats") or {}
            xviii_vit_api = data.get("corridors_vitaux_omega_stats") or {}
            eco_api = data.get("ecological_orchestrator_stats") or {}
            api_status["xix_p1_stats_observed_via_api"] = {
                "total_input": xix1_api.get("total_input"),
                "total_kept": xix1_api.get("total_kept"),
                "total_rejected": xix1_api.get("total_rejected"),
                "rejected_reasons": xix1_api.get("rejected_reasons"),
            }
            api_status["downstream_after_xix_p1"] = {
                "ecological_input": eco_api.get("total_input"),
                "ecological_kept": eco_api.get("total_output"),
                "vitaux_input": xviii_vit_api.get("total_input"),
                "vitaux_kept": xviii_vit_api.get("total_kept"),
                "vitaux_rejected_reasons": xviii_vit_api.get("rejected_reasons"),
            }
            api_status["error_message"] = None
    except Exception as e:
        api_status["http_status"] = None
        api_status["payload_size_bytes"] = 0
        api_status["error_message"] = str(e)

    out = {
        "phase": "PHASE_XIX_P1_DIAGNOSTIC_Ω",
        "tag": "BCE-4X ULTIME ABSOLU — TOP-ABSOLU",
        "commandant": "STEEVE-MAX",
        "started_at_utc": started,
        "waypoint": {"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG},
        "config_xix_p1_effective": {
            "thresh_density_origine": config_first.get("thresh_density_origine"),
            "thresh_hits_origine": config_first.get("thresh_hits_origine"),
            "rayon_fonctionnel_nominal_m": config_first.get("rayon_fonctionnel_nominal_m"),
            "origin_radius_min_m": config_first.get("origin_radius_min_m"),
            "origin_radius_max_m": config_first.get("origin_radius_max_m"),
        },
        "per_species": per_species,
        "global": {
            "total_corridors_v30": g_total,
            "origin_external_passed_count": g_passed,
            "origin_external_failed_count": g_failed,
            "origin_external_failed_outside_crown": g_outside,
            "origin_external_failed_low_density": g_low_d,
            "origin_external_failed_low_hits": g_low_h,
            "origin_external_inversion_applied_count": g_inv,
            "global_pass_rate_pct": round(100.0 * g_passed / max(1, g_total), 2),
            "global_inversion_rate_pct": round(100.0 * g_inv / max(1, g_total), 2),
        },
        "api_status_territoire_corridors": api_status,
    }
    out_path = "/app/frontend/public/reports/DIAGNOSTIC_XIX_P1.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"DIAGNOSTIC saved: {out_path}")
    print(json.dumps(out["global"], indent=2))
    print(f"API status: {api_status.get('http_status')} size={api_status.get('payload_size_bytes')}b corridors_in_response={api_status.get('corridors_in_response')} origin_passed={api_status.get('origin_external_passed_in_response')}")


if __name__ == "__main__":
    asyncio.run(main())
