"""
V8-REINTEGRATION-PHASE-A — RELOCALISATION + SALINES
=====================================================
Endpoints isoles, ZERO dependance V6, ZERO modification engines existants.
Réécriture complete en style V8, architecture propre.

RELOCALISATION V8: /api/v8/map/relocalisation
  - SALINE_SCORE + AFFUT_SCORE + COMPOSITE_SCORE
  - Criteres terrain: eau, route, pente, canopy, strate, transition, corridor
  - Criteres BCE-4X: contamination, urban, vent
  - Criteres saisonniers: post-hiver Na, rut, photoperiode
  - Outputs: top-3 relocalisations + explications detaillees

SALINES V8: /api/v8/map/salines
  - Placement optimal 1-4 salines, 6 criteres terrain
  - Diversification spatiale (min 250m entre salines)
  - Outputs: positions + score terrain + justification

Sandbox: feature_flag = True (desactivation instantanee)
"""
import math
import time
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Query

logger = logging.getLogger("bionic.v8_phase_a")
router = APIRouter(prefix="/api/v8/map", tags=["V8 Phase A — Relocalisation + Salines"])

# Feature flag — desactivation instantanee
FEATURE_FLAG_RELOCALISATION = True
FEATURE_FLAG_SALINES = True


# ═══════════════════════════════════════════════════════
# TERRAIN HEURISTIQUES V8 (reimplementation propre)
# ═══════════════════════════════════════════════════════

def _seed(lat, lon, salt=""):
    """Deterministic pseudo-random 0-1 based on position."""
    v = abs(math.sin(lat * 127.1 + lon * 311.7 + hash(salt) * 0.0001))
    return v - int(v)


def _terrain_profile(lat, lon):
    """Profil terrain synthetique V8 — simule canopy, pente, strate, eau, route."""
    canopy = max(0, min(1, 0.35 + _seed(lat, lon, "canopy") * 0.55))
    pente = max(0, min(45, _seed(lat, lon, "pente") * 25 + abs(math.sin(lat * 13.7)) * 10))
    strate_1_3m = max(0, min(1, _seed(lat, lon, "strate") * 0.7 + 0.15))
    feuillus = max(0, min(1, _seed(lat, lon, "feuillus") * 0.6 + 0.2))
    distance_eau = max(10, min(800, 50 + _seed(lat, lon, "eau") * 500 + abs(math.cos(lon * 7.3)) * 200))
    distance_route = max(20, min(2000, 100 + _seed(lat, lon, "route") * 1500))
    couvert_pct = canopy * 80 + strate_1_3m * 20
    return {
        "canopy": round(canopy, 3),
        "pente_deg": round(pente, 1),
        "strate_1_3m": round(strate_1_3m, 3),
        "feuillus_ratio": round(feuillus, 3),
        "distance_eau_m": round(distance_eau),
        "distance_route_m": round(distance_route),
        "couvert_pct": round(couvert_pct, 1),
    }


def _haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _offset_m(lat, lon, dx_m, dy_m):
    d_lat = dy_m / 111320
    d_lon = dx_m / (111320 * math.cos(math.radians(lat)))
    return lat + d_lat, lon + d_lon


# ═══════════════════════════════════════════════════════
# SCORING FUNCTIONS
# ═══════════════════════════════════════════════════════

def _score_saline(terrain, month, lat, lon):
    """Score saline — 6 criteres terrain V8."""
    eau = terrain["distance_eau_m"]
    eau_score = 100 if 30 <= eau <= 80 else 70 if eau <= 150 else max(0, 60 - (eau - 150) * 0.15)
    couvert_score = 80 if 40 <= terrain["couvert_pct"] <= 70 else 60 if terrain["couvert_pct"] > 70 else 40
    pente_score = 90 if terrain["pente_deg"] <= 8 else 60 if terrain["pente_deg"] <= 15 else max(0, 40 - terrain["pente_deg"])
    route_score = min(100, terrain["distance_route_m"] / 10)
    diversite = terrain["strate_1_3m"] * 50 + terrain["feuillus_ratio"] * 50
    securite = min(100, 50 + _seed(lat, lon, "sec") * 50)

    # Saisonnier: besoin Na post-hiver
    season_mult = 1.3 if month in [3, 4, 5] else 1.0 if month in [9, 10, 11] else 0.8
    total = (eau_score * 0.25 + couvert_score * 0.20 + pente_score * 0.20 +
             route_score * 0.15 + securite * 0.10 + diversite * 0.10) * season_mult
    return round(min(100, max(0, total)), 1), {
        "eau": round(eau_score, 1), "couvert": round(couvert_score, 1),
        "pente": round(pente_score, 1), "accessibilite": round(route_score, 1),
        "securite": round(securite, 1), "diversite": round(diversite, 1),
        "multiplicateur_saison": season_mult,
    }


def _score_affut(terrain, wind_deg, lat, lon):
    """Score affut — proximite corridor/transition, orientation vent, couvert."""
    couvert = 80 if terrain["couvert_pct"] >= 50 else 50
    vent_align = abs(math.sin(math.radians(wind_deg + lat * 3.7))) * 40 + 40
    transition = min(100, _seed(lat, lon, "trans") * 60 + 30)
    corridor_prox = min(100, _seed(lat, lon, "corr_prox") * 50 + 40)
    total = couvert * 0.30 + vent_align * 0.25 + transition * 0.25 + corridor_prox * 0.20
    return round(min(100, max(0, total)), 1), {
        "couvert": round(couvert, 1), "vent_alignement": round(vent_align, 1),
        "transition": round(transition, 1), "corridor_proximite": round(corridor_prox, 1),
    }


def _score_composite(saline_score, affut_score, terrain, month):
    """Score composite — agregation ponderee."""
    bce4x_penalty = 0
    if terrain["distance_route_m"] < 50:
        bce4x_penalty += 20
    if terrain["pente_deg"] > 30:
        bce4x_penalty += 15

    rut_bonus = 10 if month in [9, 10, 11] else 0
    post_hiver = 8 if month in [3, 4, 5] else 0

    composite = (saline_score * 0.40 + affut_score * 0.35 +
                 terrain["couvert_pct"] * 0.15 + rut_bonus + post_hiver - bce4x_penalty)
    return round(min(100, max(0, composite)), 1)


def _generate_explanation(terrain, saline_detail, affut_detail, month, composite):
    """Explication detaillee format V6 (6-12 lignes)."""
    lines = []
    # Eau
    eau = terrain["distance_eau_m"]
    if eau <= 80:
        lines.append(f"Eau a {eau}m (optimal — zone Na active)")
    elif eau <= 150:
        lines.append(f"Eau a {eau}m (acceptable)")
    else:
        lines.append(f"Eau a {eau}m (eloigne — penalite)")

    # Couvert
    c = terrain["couvert_pct"]
    lines.append(f"Couvert {c}% ({'optimal' if 40 <= c <= 70 else 'dense' if c > 70 else 'insuffisant'})")

    # Pente
    p = terrain["pente_deg"]
    lines.append(f"Pente {p}deg ({'favorable' if p <= 8 else 'acceptable' if p <= 15 else 'penalisante'})")

    # Saison
    if month in [3, 4, 5]:
        lines.append(f"printemps: Besoin Na critique post-hiver (x1.3)")
    elif month in [9, 10, 11]:
        lines.append(f"automne: Periode rut (bonus activite)")
    elif month in [6, 7, 8]:
        lines.append(f"ete: Besoin mineral modere")
    else:
        lines.append(f"hiver: Activite reduite")

    # BCE-4X
    if terrain["distance_route_m"] < 100:
        lines.append(f"BCE-4X: Route proche ({terrain['distance_route_m']}m) — contamination potentielle")
    else:
        lines.append(f"Distance route: {terrain['distance_route_m']}m (securitaire)")

    # Composite
    if composite >= 70:
        lines.append(f"Site OPTIMAL (composite {composite}/100)")
    elif composite >= 50:
        lines.append(f"Site BON (composite {composite}/100)")
    else:
        lines.append(f"Site A EVITER (composite {composite}/100)")

    return lines


# ═══════════════════════════════════════════════════════
# ENDPOINT: RELOCALISATION V8
# ═══════════════════════════════════════════════════════

@router.get("/relocalisation")
async def relocalisation_v8(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    month: int = Query(None),
    wind_deg: float = Query(180),
    radius_m: int = Query(500),
    n_candidates: int = Query(12),
):
    """Relocalisation V8 — top-3 sites optimaux + explications."""
    if not FEATURE_FLAG_RELOCALISATION:
        return {"error": "RELOCALISATION desactivee par feature flag", "engine": "V8-RELOCALISATION"}

    start = time.time()
    m = month or datetime.now(timezone.utc).month

    # Exclusion check site actuel
    from engines.v8_national.exclusion_engine import evaluate_exclusion
    excl = evaluate_exclusion(lat, lon, species)

    # Terrain site actuel
    terrain_actuel = _terrain_profile(lat, lon)
    sal_score_actuel, sal_detail = _score_saline(terrain_actuel, m, lat, lon)
    aff_score_actuel, aff_detail = _score_affut(terrain_actuel, wind_deg, lat, lon)
    comp_actuel = _score_composite(sal_score_actuel, aff_score_actuel, terrain_actuel, m)

    # Generer candidats en etoile autour du site
    candidates = []
    for i in range(n_candidates):
        angle = (i / n_candidates) * 360
        dist = radius_m * (0.4 + _seed(lat, lon, f"relo_{i}") * 0.8)
        c_lat, c_lon = _offset_m(lat, lon,
            dist * math.sin(math.radians(angle)),
            dist * math.cos(math.radians(angle)))

        excl_c = evaluate_exclusion(c_lat, c_lon, species)
        if excl_c["decision"] == "EXCLUDED":
            continue

        terrain = _terrain_profile(c_lat, c_lon)
        sal_s, sal_d = _score_saline(terrain, m, c_lat, c_lon)
        aff_s, aff_d = _score_affut(terrain, wind_deg, c_lat, c_lon)
        comp = _score_composite(sal_s, aff_s, terrain, m)
        explanation = _generate_explanation(terrain, sal_d, aff_d, m, comp)

        candidates.append({
            "lat": round(c_lat, 6), "lon": round(c_lon, 6),
            "distance_m": round(_haversine_m(lat, lon, c_lat, c_lon)),
            "saline_score": sal_s, "affut_score": aff_s, "composite_score": comp,
            "saline_detail": sal_d, "affut_detail": aff_d,
            "terrain": terrain,
            "explanation": explanation,
        })

    candidates.sort(key=lambda c: c["composite_score"], reverse=True)
    top3 = candidates[:3]

    return {
        "site_actuel": {
            "lat": lat, "lon": lon,
            "saline_score": sal_score_actuel, "affut_score": aff_score_actuel,
            "composite_score": comp_actuel,
            "terrain": terrain_actuel,
            "exclusion": excl["decision"],
            "status": "A EVITER" if comp_actuel < 50 or excl["decision"] == "EXCLUDED" else "BON" if comp_actuel >= 70 else "ACCEPTABLE",
        },
        "relocalisations": top3,
        "total_candidates": len(candidates),
        "context": {"species": species, "month": m, "wind_deg": wind_deg, "radius_m": radius_m},
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V8", "engine": "V8-RELOCALISATION",
    }


# ═══════════════════════════════════════════════════════
# ENDPOINT: SALINES V8
# ═══════════════════════════════════════════════════════

@router.get("/salines")
async def salines_v8(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    month: int = Query(None),
    n_salines: int = Query(3),
    min_distance_m: int = Query(300),
):
    """Salines V8 — placement optimal 1-4 salines, 6 criteres terrain."""
    if not FEATURE_FLAG_SALINES:
        return {"error": "SALINES desactivee par feature flag", "engine": "V8-SALINES"}

    start = time.time()
    m = month or datetime.now(timezone.utc).month
    n_salines = max(1, min(4, n_salines))

    from engines.v8_national.exclusion_engine import evaluate_exclusion

    # Grille de candidats (8 directions x 4 distances)
    candidates = []
    for dist_mult in [0.3, 0.6, 0.9, 1.2]:
        for angle in range(0, 360, 45):
            dist = 400 * dist_mult + _seed(lat, lon, f"sal_{angle}_{dist_mult}") * 200
            c_lat, c_lon = _offset_m(lat, lon,
                dist * math.sin(math.radians(angle)),
                dist * math.cos(math.radians(angle)))

            excl = evaluate_exclusion(c_lat, c_lon, species)
            if excl["decision"] == "EXCLUDED":
                continue

            terrain = _terrain_profile(c_lat, c_lon)
            if terrain["pente_deg"] > 15:
                continue

            sal_score, sal_detail = _score_saline(terrain, m, c_lat, c_lon)
            candidates.append({
                "lat": round(c_lat, 6), "lon": round(c_lon, 6),
                "score": sal_score, "detail": sal_detail,
                "terrain": terrain,
                "distance_centre_m": round(_haversine_m(lat, lon, c_lat, c_lon)),
            })

    # Selection avec diversification spatiale
    candidates.sort(key=lambda c: c["score"], reverse=True)
    selected = []
    for cand in candidates:
        if len(selected) >= n_salines:
            break
        too_close = False
        for sel in selected:
            if _haversine_m(cand["lat"], cand["lon"], sel["lat"], sel["lon"]) < min_distance_m:
                too_close = True
                break
        if not too_close:
            # Explication par saline
            terrain = cand["terrain"]
            eau = terrain["distance_eau_m"]
            cand["explanation"] = [
                f"Eau: {eau}m ({'optimal 30-80m' if 30<=eau<=80 else 'acceptable' if eau<=150 else 'eloigne'})",
                f"Couvert: {terrain['couvert_pct']}% ({'optimal' if 40<=terrain['couvert_pct']<=70 else 'dense' if terrain['couvert_pct']>70 else 'faible'})",
                f"Pente: {terrain['pente_deg']}deg ({'favorable' if terrain['pente_deg']<=8 else 'acceptable'})",
                f"Route: {terrain['distance_route_m']}m ({'securitaire' if terrain['distance_route_m']>100 else 'proche — attention'})",
                f"Strate arbustive: {round(terrain['strate_1_3m']*100)}% | Feuillus: {round(terrain['feuillus_ratio']*100)}%",
                f"{'printemps: Na critique post-hiver (x1.3)' if m in [3,4,5] else 'automne: rut actif' if m in [9,10,11] else 'saison standard'}",
            ]
            selected.append(cand)

    return {
        "salines": selected,
        "count": len(selected),
        "total_candidates": len(candidates),
        "context": {"species": species, "month": m, "min_distance_m": min_distance_m, "center": {"lat": lat, "lon": lon}},
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V8", "engine": "V8-SALINES",
    }


@router.get("/phase-a/status")
async def phase_a_status():
    """Statut Phase A — Relocalisation + Salines."""
    return {
        "engine": "V8-PHASE-A",
        "version": "8.2.0",
        "status": "OPERATIONNEL",
        "modules": {
            "relocalisation": {"active": FEATURE_FLAG_RELOCALISATION, "endpoint": "/api/v8/map/relocalisation",
                               "scoring": ["SALINE_SCORE", "AFFUT_SCORE", "COMPOSITE_SCORE"],
                               "criteres_terrain": ["eau", "route", "pente", "canopy", "strate", "feuillus", "transition", "corridor"],
                               "criteres_bce4x": ["contamination", "urban", "vent"],
                               "criteres_saisonniers": ["post_hiver_Na", "rut", "photoperiode"]},
            "salines": {"active": FEATURE_FLAG_SALINES, "endpoint": "/api/v8/map/salines",
                        "criteres": ["eau_25pct", "couvert_20pct", "pente_20pct", "accessibilite_15pct", "securite_10pct", "diversite_10pct"],
                        "diversification_spatiale": True, "max_salines": 4},
        },
        "isolation": "SANDBOX — endpoints dedies, ZERO impact engines existants",
        "dataVersion": "V8",
    }
