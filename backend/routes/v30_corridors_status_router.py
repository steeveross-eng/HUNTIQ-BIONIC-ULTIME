"""
v30_corridors_status_router.py — PHASE_XII_SUPRA_DIAGNOSTIC_V30_STATUS_Ω
========================================================================
Phase     : PHASE_XII_SUPRA_DIAGNOSTIC_V30_STATUS_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Endpoint LECTURE SEULE exposant le statut ENGINE CORRIDORS V30 couplé à
RenduΩ et à la matrice P6. V30 strictement intact (aucune mutation).

GET /api/v30/corridors/status
    ?species=orignal|cerf|ours|...       (optionnel — snapshot live)
    ?lat=48.206657&lon=-68.382422        (optionnel — waypoint)
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/api/v30/corridors",
    tags=["V30_CORRIDORS_STATUS_Ω"],
)

# Waypoint officiel (validé par l'ordre institutionnel)
OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422

# Seuils institutionnels Section 3
THRESHOLD_NON_CONFORM = 70.0  # < 70 → NON CONFORME
THRESHOLD_CONFORM_OMEGA = 90.0  # >= 90 → CONFORME Ω


# ═══════════════════════════════════════════════════════════════════════
# Helpers géométriques (lecture seule)
# ═══════════════════════════════════════════════════════════════════════
def _haversine_m(a: List[float], b: List[float]) -> float:
    R = 6371000.0
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    h = (math.sin((la2 - la1) / 2) ** 2 +
         math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(min(1.0, math.sqrt(h)))


def _path_length_m(path: List[List[float]]) -> float:
    if not path or len(path) < 2:
        return 0.0
    return sum(_haversine_m(path[i], path[i + 1]) for i in range(len(path) - 1))


def _compute_corridor_metrics(corridor: Dict[str, Any]) -> Dict[str, Any]:
    path = corridor.get("path") or corridor.get("polyline") or []
    length_m = _path_length_m(path)
    rom = corridor.get("renduomega") or {}
    geom = rom.get("geometry") or {}
    terr = rom.get("terrain") or {}
    return {
        "id": corridor.get("id"),
        "points_count": len(path),
        "length_m": round(length_m, 1),
        "accepted": bool(rom.get("accepted")),
        "max_segment_m": geom.get("max_segment_m"),
        "max_angle_deg": geom.get("max_angle_deg"),
        "functional_radius_m": terr.get("functional_radius_m"),
    }


def _classify_rejection_reason(verdict: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    for block in ("geometry", "terrain", "ecology", "species"):
        vs = (verdict.get(block) or {}).get("violations") or []
        for v in vs:
            vstr = str(v).lower()
            if "max_segment_m" in vstr:
                reasons.append("seg_max")
            elif "max_angle_deg" in vstr:
                reasons.append("ang_max")
            elif "length_m" in vstr and "<" in vstr:
                reasons.append("length_short")
            elif "radial_or_straight" in vstr:
                reasons.append("radial_star")
            elif "radius_m" in vstr:
                reasons.append("functional_radius")
            elif "min_dist_water_m" in vstr:
                reasons.append("water_too_close")
            elif "slope_deg" in vstr:
                reasons.append("slope_too_steep")
            elif "human_zone" in vstr:
                reasons.append("human_zone")
            elif "contamination" in vstr:
                reasons.append("contamination_too_close")
            elif "isolated" in vstr or "isolation" in vstr:
                reasons.append("isolation")
    return reasons or ["unknown"]


def _percentile(values: List[float], pct: float) -> Optional[float]:
    if not values:
        return None
    vs = sorted(values)
    k = int(len(vs) * pct / 100)
    k = max(0, min(len(vs) - 1, k))
    return round(vs[k], 2)


# ═══════════════════════════════════════════════════════════════════════
# Alignment score
# ═══════════════════════════════════════════════════════════════════════
def _compute_alignment_score(total: int, accepted: int,
                             points_ok: int, radius_ok: int,
                             species_ok: int) -> float:
    """v30_alignment_score ∈ [0, 100].

    - 60% acceptance_rate (RenduΩ)
    - 15% conformité géométrique (25-30 points)
    - 15% conformité terrainaware (rayon 420-780 m)
    - 10% conformité biologique (profil espèce respecté)
    """
    if total <= 0:
        return 0.0
    acc = accepted / total
    geom = points_ok / total
    terr = radius_ok / total
    spec = species_ok / total
    score = 100.0 * (0.60 * acc + 0.15 * geom + 0.15 * terr + 0.10 * spec)
    return round(score, 2)


def _alignment_label(score: float) -> str:
    if score >= THRESHOLD_CONFORM_OMEGA:
        return "CONFORME_Ω"
    if score >= THRESHOLD_NON_CONFORM:
        return "CONFORME"
    return "NON_CONFORME"


# ═══════════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════════
@router.get("/status")
async def v30_corridors_status(
    species: Optional[str] = Query(None),
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
    month: int = Query(10),
    hour: int = Query(14),
):
    """Statut ENGINE CORRIDORS V30 — couplage RenduΩ + P6 (lecture seule).

    - Sans `species` : agrège 4 espèces institutionnelles (orignal, cerf,
      ours, dindon) au waypoint officiel.
    - Avec `species` : snapshot dédié à l'espèce demandée.
    """
    from engines.v8_institutional.v20_performance_bundle import (
        _cache_get as bundle_cache_get,
        _cache_key,
    )
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.post_smoothing.renduomega import apply_renduomega_to_bundle

    species_list = [species] if species else ["orignal", "cerf", "ours", "dindon"]

    per_species_stats: Dict[str, Any] = {}
    global_total = 0
    global_accepted = 0
    global_points_ok = 0
    global_radius_ok = 0
    global_species_ok = 0
    global_radius_sum = 0.0
    global_radius_count = 0
    global_rejection_counter: Counter = Counter()
    global_length_samples: List[float] = []
    global_points_samples: List[int] = []

    for sp in species_list:
        # 1) cache HIT ?
        key = _cache_key(lat, lon, sp, month, hour, 225.0)
        bundle = bundle_cache_get(key)
        if bundle is None:
            # 2) compute live via RenduΩ pipeline complet
            try:
                raw = await compute_territoire_v10(lat, lon, sp, month, hour, 225.0, 15.0)
                raw["waypoint"] = {"lat": lat, "lng": lon}
                raw["species"] = sp
                # normaliser contamination pour RenduΩ
                contam_norm: List[Dict[str, Any]] = []
                for c in raw.get("contamination") or []:
                    _lat = c.get("lat") or (c.get("affut_source") or {}).get("lat")
                    _lng = c.get("lng") or c.get("lon") or (c.get("affut_source") or {}).get("lng")
                    if _lat is not None and _lng is not None:
                        contam_norm.append({"lat": float(_lat), "lng": float(_lng)})
                raw["contamination_zones"] = contam_norm
                bundle = apply_renduomega_to_bundle(raw)
            except Exception as e:
                per_species_stats[sp] = {"error": str(e), "total": 0}
                continue

        accepted_list = bundle.get("corridors") or []
        rejected_list = bundle.get("corridors_rejected_by_renduomega") or []
        total = len(accepted_list) + len(rejected_list)
        accepted = len(accepted_list)

        # métriques géométriques
        points_ok = 0
        radius_ok = 0
        species_ok = 0
        radius_sum = 0.0
        radius_count = 0
        length_samples: List[float] = []
        points_samples: List[int] = []
        rejection_counter: Counter = Counter()

        for c in accepted_list:
            m = _compute_corridor_metrics(c)
            points_samples.append(m["points_count"])
            length_samples.append(m["length_m"])
            if 25 <= m["points_count"] <= 30:
                points_ok += 1
            r = m.get("functional_radius_m")
            if r is not None:
                try:
                    rv = float(r)
                    radius_sum += rv
                    radius_count += 1
                    if 420.0 <= rv <= 780.0:
                        radius_ok += 1
                except (TypeError, ValueError):
                    pass
            # conformité biologique : corridor.species_profile == bundle species
            sp_profile = c.get("species_profile") or c.get("species")
            if sp_profile in (None, sp, ""):
                species_ok += 1

        for r in rejected_list:
            rom = r.get("renduomega") or {}
            reasons = _classify_rejection_reason(rom)
            for rr in reasons:
                rejection_counter[rr] += 1

        # aggregations globales
        global_total += total
        global_accepted += accepted
        global_points_ok += points_ok
        global_radius_ok += radius_ok
        global_species_ok += species_ok
        global_radius_sum += radius_sum
        global_radius_count += radius_count
        global_length_samples.extend(length_samples)
        global_points_samples.extend(points_samples)
        global_rejection_counter.update(rejection_counter)

        score = _compute_alignment_score(total, accepted, points_ok, radius_ok, species_ok)
        per_species_stats[sp] = {
            "total": total,
            "accepted": accepted,
            "rejected": len(rejected_list),
            "acceptance_rate": round((accepted / total * 100.0) if total else 0.0, 2),
            "rejection_top_reasons": rejection_counter.most_common(3),
            "mean_functional_radius_m": round(radius_sum / radius_count, 1) if radius_count else None,
            "length_m_p50": _percentile(length_samples, 50),
            "length_m_p90": _percentile(length_samples, 90),
            "points_distribution": {
                "in_25_30": sum(1 for p in points_samples if 25 <= p <= 30),
                "below_25": sum(1 for p in points_samples if p < 25),
                "above_30": sum(1 for p in points_samples if p > 30),
            },
            "v30_alignment_score": score,
            "alignment_label": _alignment_label(score),
        }

    # global score
    global_score = _compute_alignment_score(
        global_total, global_accepted,
        global_points_ok, global_radius_ok, global_species_ok,
    )
    overall_label = _alignment_label(global_score)

    # coupler P6
    try:
        from engines.post_smoothing.anti_regression_omega import get_ledger_snapshot
        p6 = get_ledger_snapshot()
    except Exception:
        p6 = {"summary": {}, "sub_normes": {}}

    return JSONResponse({
        "phase": "PHASE_XII_SUPRA_DIAGNOSTIC_V30_STATUS_Ω",
        "waypoint_official": {"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG},
        "query": {"species_requested": species, "lat": lat, "lng": lon,
                  "month": month, "hour": hour},
        "per_species": per_species_stats,
        "global": {
            "total": global_total,
            "accepted": global_accepted,
            "rejected": global_total - global_accepted,
            "acceptance_rate_pct": round(
                (global_accepted / global_total * 100.0) if global_total else 0.0, 2
            ),
            "mean_functional_radius_m": (
                round(global_radius_sum / global_radius_count, 1)
                if global_radius_count else None
            ),
            "length_m_p50": _percentile(global_length_samples, 50),
            "length_m_p90": _percentile(global_length_samples, 90),
            "points_distribution": {
                "in_25_30": sum(1 for p in global_points_samples if 25 <= p <= 30),
                "below_25": sum(1 for p in global_points_samples if p < 25),
                "above_30": sum(1 for p in global_points_samples if p > 30),
            },
            "rejection_top_reasons": global_rejection_counter.most_common(5),
            "v30_alignment_score": global_score,
            "alignment_label": overall_label,
        },
        "thresholds": {
            "non_conform_below": THRESHOLD_NON_CONFORM,
            "conform_omega_above": THRESHOLD_CONFORM_OMEGA,
        },
        "p6_coupling": {
            "summary": p6.get("summary", {}),
            "sub_normes_non_zero": {
                k: v for k, v in (p6.get("sub_normes") or {}).items()
                if isinstance(v, dict) and v.get("violations", 0) > 0
            },
        },
        "v30_locked": True,
        "v30_modified": False,
        "diagnostic_corridors_omega_activated": False,
    })


@router.get("/alignment-score")
async def v30_alignment_score_only(
    species: Optional[str] = Query(None),
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
):
    """Score seulement — usage panneau frontend léger."""
    resp = await v30_corridors_status(
        species=species, lat=lat, lon=lon, month=10, hour=14,
    )
    import json
    d = json.loads(bytes(resp.body).decode("utf-8"))
    return JSONResponse({
        "v30_alignment_score": d["global"]["v30_alignment_score"],
        "alignment_label": d["global"]["alignment_label"],
        "acceptance_rate_pct": d["global"]["acceptance_rate_pct"],
        "thresholds": d["thresholds"],
    })
