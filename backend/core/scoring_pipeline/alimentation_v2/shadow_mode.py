"""
BCE-4X P0-I — SHADOW MODE ENGINE
=================================
ORDONNANCE STEEVE-MAX 2026-04-06
Branche: BIONIC_REWRITE_P0

Execute les moteurs V2 (sanctuarise) et V3 (actif) en parallele,
compare les resultats, et log les differences.

ZERO impact utilisateur — le moteur V3 sert TOUJOURS la reponse.
Le moteur V2 (shadow) est execute uniquement pour comparaison.
"""
import logging
import hashlib
import math
from typing import Dict, List, Optional

logger = logging.getLogger("bionic.shadow_mode")


# ═══════════════════════════════════════════════════════════
# V2 SHADOW ENGINE — Reproduction fidele du moteur V2 sanctuarise
# ═══════════════════════════════════════════════════════════

def _seed_v2(lat, lng, salt=""):
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _haversine_m_v2(lat1, lng1, lat2, lng2):
    R = 6371000
    p = math.pi / 180
    a = (
        math.sin((lat2 - lat1) * p / 2) ** 2
        + math.cos(lat1 * p) * math.cos(lat2 * p)
        * math.sin((lng2 - lng1) * p / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def _score_candidate_v2(terrain, lat, lng, center_lat, center_lng, dist_m, half_m, idx):
    """V2 scoring — hash MD5 pour acces et habitat (SANCTUARISE)."""
    eau_prox = terrain.get("eau", {}).get("score_hydrique", 0.5)
    couvert = terrain.get("foret", {}).get("couvert_pct", 60) / 100
    pente = terrain.get("relief", {}).get("pente_moyenne_pct", 10)

    score_eau = min(1.0, eau_prox * 1.2)
    score_eau *= (0.85 + 0.3 * _seed_v2(lat, lng, "eau_var"))

    if 0.3 < couvert < 0.85:
        score_couvert = 0.7 + 0.3 * _seed_v2(lat, lng, "couv")
    else:
        score_couvert = 0.3 + 0.2 * _seed_v2(lat, lng, "couv")

    score_pente = max(0.2, 1.0 - pente / 25)
    score_pente *= (0.8 + 0.4 * _seed_v2(lat, lng, "pente_var"))

    score_acces = _seed_v2(lat, lng, f"acces_{idx}")

    score_securite = max(0.3, 1.0 - (dist_m / half_m) * 0.5)
    score_securite *= (0.8 + 0.4 * _seed_v2(lat, lng, "sec"))

    score_habitat = _seed_v2(lat, lng, "habitat_div")

    total = (
        score_eau * 0.25
        + score_couvert * 0.20
        + score_pente * 0.20
        + score_acces * 0.15
        + score_securite * 0.10
        + score_habitat * 0.10
    )
    return round(total * 100)


def compute_salines_v2_shadow(center_lat, center_lng, terrain, species="CERF",
                               month=10, side_m=2000.0, max_salines=4,
                               min_distance_m=300.0, max_radius_m=600.0):
    """
    V2 Shadow — Reproduction fidele du moteur sanctuarise.
    Retourne uniquement les scores pour comparaison.
    """
    half = side_m / 2
    max_salines = max(1, min(4, max_salines))
    grid_size = 4
    cell_size = side_m / grid_size
    results = []

    for idx in range(grid_size * grid_size):
        row, col = divmod(idx, grid_size)
        base_lat = center_lat + ((row - 1.5) * cell_size) / 111320
        base_lng = center_lng + ((col - 1.5) * cell_size) / (
            111320 * math.cos(math.radians(center_lat))
        )
        jitter_lat = (_seed_v2(base_lat, base_lng, f"jlat_{idx}") - 0.5) * (cell_size * 0.6) / 111320
        jitter_lng = (_seed_v2(base_lat, base_lng, f"jlng_{idx}") - 0.5) * (cell_size * 0.6) / (
            111320 * math.cos(math.radians(center_lat))
        )
        lat = base_lat + jitter_lat
        lng = base_lng + jitter_lng
        dist = _haversine_m_v2(center_lat, center_lng, lat, lng)
        if dist > max_radius_m or dist < 150:
            continue
        score = _score_candidate_v2(terrain, lat, lng, center_lat, center_lng, dist, half, idx)
        results.append({"id": f"SAL-{idx + 1:02d}", "score_v2": score, "lat": round(lat, 6), "lng": round(lng, 6)})

    results.sort(key=lambda x: x["score_v2"], reverse=True)
    return results


# ═══════════════════════════════════════════════════════════
# SHADOW COMPARATOR
# ═══════════════════════════════════════════════════════════

def run_shadow_comparison(v3_salines: List[Dict], v2_shadow: List[Dict],
                           waypoint: Dict) -> Dict:
    """
    Compare les resultats V2 et V3 et genere un rapport de differences.
    """
    v3_scores = {s["id"]: s["score"] for s in v3_salines}
    v2_scores = {s["id"]: s["score_v2"] for s in v2_shadow}

    common_ids = set(v3_scores.keys()) & set(v2_scores.keys())

    diffs = []
    for sid in sorted(common_ids):
        s_v3 = v3_scores[sid]
        s_v2 = v2_scores[sid]
        delta = s_v3 - s_v2
        diffs.append({
            "id": sid,
            "score_v2": s_v2,
            "score_v3": s_v3,
            "delta": delta,
            "pct_change": round((delta / max(s_v2, 1)) * 100, 1),
        })

    v3_only = set(v3_scores.keys()) - set(v2_scores.keys())
    v2_only = set(v2_scores.keys()) - set(v3_scores.keys())

    avg_v2 = sum(v2_scores.values()) / max(len(v2_scores), 1)
    avg_v3 = sum(v3_scores.values()) / max(len(v3_scores), 1)

    report = {
        "waypoint": waypoint,
        "v2_count": len(v2_shadow),
        "v3_count": len(v3_salines),
        "common_count": len(common_ids),
        "v3_only_ids": list(v3_only),
        "v2_only_ids": list(v2_only),
        "avg_score_v2": round(avg_v2, 1),
        "avg_score_v3": round(avg_v3, 1),
        "avg_delta": round(avg_v3 - avg_v2, 1),
        "diffs": sorted(diffs, key=lambda d: abs(d["delta"]), reverse=True),
        "max_delta": max((abs(d["delta"]) for d in diffs), default=0),
        "regression_detected": avg_v3 < avg_v2 * 0.7,  # Alerte si V3 < 70% de V2
    }

    # Logging
    logger.info(
        f"[SHADOW] Waypoint ({waypoint.get('lat')},{waypoint.get('lng')}): "
        f"V2 avg={avg_v2:.1f} V3 avg={avg_v3:.1f} delta={avg_v3-avg_v2:+.1f} "
        f"common={len(common_ids)} max_delta={report['max_delta']}"
    )

    if report["regression_detected"]:
        logger.warning(
            f"[SHADOW] REGRESSION DETECTEE: V3 ({avg_v3:.1f}) < 70% de V2 ({avg_v2:.1f})"
        )

    return report
