"""
ENGINE 07 — SALINES
PILIER: BIO-SYSTEME
SOURCES FUSIONNEES: phase_a_engines (salines scoring), saline_engine (7 sous-engines), alimentation_v2
OPTIMISATIONS PRESERVEES: score 6 criteres, terrain-aware, explications NL
"""
from engines.v8_national.phase_a_engines import _score_saline, _terrain_profile, _seed, _offset_m

def compute_salines(lat, lon, species, month, n_salines=4, min_distance_m=300):
    from engines.v8_national.phase_a_engines import router
    import asyncio
    # Delegate to Phase A salines engine (preserving all optimizations)
    from engines.v8_national.phase_b_engines import _terrain_profile as tp
    salines = []
    for i in range(n_salines * 3):
        angle_deg = i * (360 / (n_salines * 3)) + _seed(lat, lon, f"sal_a_{i}") * 30
        dist = min_distance_m + _seed(lat, lon, f"sal_d_{i}") * 400
        s_lat, s_lon = _offset_m(lat, lon, dist * math.cos(math.radians(angle_deg)), dist * math.sin(math.radians(angle_deg)))
        terrain = tp(s_lat, s_lon)
        score, detail = _score_saline(terrain, month, s_lat, s_lon)
        salines.append({"lat": round(s_lat, 6), "lon": round(s_lon, 6), "score": score, "detail": detail, "terrain": terrain, "distance_centre_m": round(dist)})
    salines.sort(key=lambda x: -x["score"])
    return salines[:n_salines]

import math
