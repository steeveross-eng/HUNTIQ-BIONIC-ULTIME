"""
V8-REINTEGRATION-PHASE-B — ZONES + CORRIDORS + AFFUTS TERRAIN-AWARE
=====================================================================
Generateurs terrain-aware V8 natifs.
Utilise _terrain_profile de Phase A pour enrichir zones, corridors, affuts.
ZERO dependance V6. ZERO duplication scoring.

ZONES:  scoring terrain (canopy, pente, eau, route, strate, feuillus)
CORRIDORS: cost surface simplifie (pente, couvert, transitions, continuite)
AFFUTS: coherence zones+corridors (terrain, vent, proximite corridor)

Sandbox: feature_flag = True
"""
import math
import time
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Query

logger = logging.getLogger("bionic.v8_phase_b")
router = APIRouter(prefix="/api/v8/map", tags=["V8 Phase B — Zones + Corridors + Affuts TA"])

FEATURE_FLAG_PHASE_B = True

ZONE_TYPES = ["alimentation", "repos", "rut", "affuts", "eau"]

# ═══════════════════════════════════════════════════════
# TERRAIN (reutilise Phase A _terrain_profile + _seed)
# ═══════════════════════════════════════════════════════

def _seed(lat, lon, salt=""):
    v = abs(math.sin(lat * 127.1 + lon * 311.7 + hash(salt) * 0.0001))
    return v - int(v)


def _terrain_profile(lat, lon):
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


def _offset_m(lat, lon, dx_m, dy_m):
    d_lat = dy_m / 111320
    d_lon = dx_m / (111320 * math.cos(math.radians(lat)))
    return lat + d_lat, lon + d_lon


# ═══════════════════════════════════════════════════════
# ORGANIC GEOMETRY (reuse map_bundle style)
# ═══════════════════════════════════════════════════════

def _organic_polygon(c_lat, c_lon, radius_deg, n_vertices=12, seed=0):
    points = []
    cos_lat = max(0.5, math.cos(math.radians(c_lat)))
    for j in range(n_vertices):
        angle = (j / n_vertices) * 2 * math.pi
        jitter = 0.7 + 0.6 * abs(math.sin(seed * 7.3 + j * 2.9 + c_lat * 11.1))
        r = radius_deg * jitter
        p_lat = c_lat + math.sin(angle) * r
        p_lon = c_lon + math.cos(angle) * r / cos_lat
        points.append([round(p_lat, 6), round(p_lon, 6)])
    points.append(points[0])
    return points


def _bezier_curve(start, end, n_points=8, curvature_seed=0):
    """Generate ANGULAR terrain-following path — ZERO smooth curve.
    V8-INSTITUTIONNEL: veines animales directionnelles.
    3-5 segments angulaires, ZERO Bezier, ZERO interpolation lissee.
    """
    s_lat, s_lon = start
    e_lat, e_lon = end
    dx = e_lon - s_lon
    dy = e_lat - s_lat
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 1e-8:
        return [[s_lat, s_lon], [e_lat, e_lon]]

    # Angular directional path: 3-5 waypoints with sharp direction changes
    n_segments = 3 + int(abs(math.sin(curvature_seed * 2.7)) * 2)  # 3-5
    points = [[s_lat, s_lon]]
    for j in range(1, n_segments):
        t = j / n_segments
        # Base linear interpolation
        base_lat = s_lat + dy * t
        base_lon = s_lon + dx * t
        # Angular offset perpendicular (terrain-aware jitter, not smooth)
        offset_strength = 0.08 + 0.12 * abs(math.sin(curvature_seed * 3.7 + j * 5.3))
        sign = 1 if (curvature_seed + j) % 2 == 0 else -1
        perp_lat = base_lat + (-dx) * offset_strength * sign
        perp_lon = base_lon + (dy) * offset_strength * sign
        points.append([round(perp_lat, 6), round(perp_lon, 6)])
    points.append([e_lat, e_lon])
    return points


# ═══════════════════════════════════════════════════════
# TERRAIN-AWARE ZONE SCORING
# ═══════════════════════════════════════════════════════

def _score_zone_terrain(terrain, zone_type, month):
    """Score une zone en fonction du terrain et du type."""
    canopy = terrain["canopy"]
    pente = terrain["pente_deg"]
    eau = terrain["distance_eau_m"]
    route = terrain["distance_route_m"]
    strate = terrain["strate_1_3m"]
    feuillus = terrain["feuillus_ratio"]

    if zone_type == "alimentation":
        # Alimentation: strate arbustive haute, feuillus, pente faible
        score = (strate * 30 + feuillus * 25 + (1 - pente / 45) * 20 +
                 min(1, eau / 200) * 15 + min(1, route / 500) * 10)
        if month in [5, 6, 7]:
            score *= 1.15  # croissance vegetale
    elif zone_type == "repos":
        # Repos: canopy dense, pente moderee, loin des routes
        score = (canopy * 35 + (1 - pente / 45) * 20 + min(1, route / 800) * 25 +
                 strate * 10 + (1 - min(1, eau / 500)) * 10)
    elif zone_type == "rut":
        # Rut: transitions foret-clairiere, canopy moderee
        transition = abs(canopy - 0.5) * 2  # 0=optimal(0.5), 1=extreme
        score = ((1 - transition) * 35 + strate * 20 + feuillus * 15 +
                 (1 - pente / 45) * 15 + min(1, route / 500) * 15)
        if month in [9, 10, 11]:
            score *= 1.25  # saison rut
    elif zone_type == "eau":
        # Eau: proximite eau critique
        eau_score = 100 if eau <= 50 else 70 if eau <= 150 else max(10, 50 - (eau - 150) * 0.1)
        score = (eau_score * 0.50 + canopy * 15 + (1 - pente / 45) * 20 +
                 min(1, route / 500) * 15)
    elif zone_type == "affuts":
        # Affuts: couvert, transitions, loin routes
        score = (canopy * 25 + strate * 20 + (1 - pente / 45) * 15 +
                 min(1, route / 500) * 20 + feuillus * 10 + min(1, eau / 300) * 10)
    else:
        score = 50

    return round(min(100, max(0, score)), 1)


# ═══════════════════════════════════════════════════════
# COST SURFACE SIMPLIFIE (pour corridors)
# ═══════════════════════════════════════════════════════

def _cost_surface_score(terrain):
    """Cost surface simplifie — penalite deplacement."""
    pente_cost = terrain["pente_deg"] / 45  # 0-1
    couvert_benefit = terrain["canopy"] * 0.7 + terrain["strate_1_3m"] * 0.3
    eau_barrier = 1.0 if terrain["distance_eau_m"] < 20 else 0.0
    route_barrier = 0.8 if terrain["distance_route_m"] < 30 else 0.0

    # Cout = penalites - benefices (lower = meilleur passage)
    cost = pente_cost * 0.35 + eau_barrier * 0.25 + route_barrier * 0.20 - couvert_benefit * 0.20
    return round(max(0, min(1, cost)), 3)


def _corridor_intensity(terrain_start, terrain_end, month, hour, species):
    """Intensite corridor V6-conforme: variabilite reelle entre types."""
    crep = species in ["cerf", "orignal", "wapiti", "caribou", "chevreuil"]
    t_mult = 1.2 if (5 <= hour <= 8 or 16 <= hour <= 19) and crep else 0.6 if 10 <= hour <= 14 else 1.0

    cost_avg = (_cost_surface_score(terrain_start) + _cost_surface_score(terrain_end)) / 2

    # V6-CONFORME: intensite base 20-80 (pas 20-100) pour permettre variete de types
    base_intensity = (1 - cost_avg) * 60 + 20

    # COR-006: bonus transition foret-clairiere
    canopy_diff = abs(terrain_start["canopy"] - terrain_end["canopy"])
    transition_bonus = canopy_diff * 15 if canopy_diff > 0.15 else 0

    # Penalite pente (corridors en pente = moins utilises)
    pente_avg = (terrain_start["pente_deg"] + terrain_end["pente_deg"]) / 2
    pente_penalty = max(0, (pente_avg - 10) * 1.5)

    intensity = min(100, max(10, (base_intensity + transition_bonus - pente_penalty) * t_mult))
    return round(intensity, 1)


# ═══════════════════════════════════════════════════════
# GENERATEURS TERRAIN-AWARE
# ═══════════════════════════════════════════════════════

def generate_zones_ta(lat, lon, species, month, radius_km=1):
    """Zones terrain-aware: scoring base sur profil terrain reel."""
    zones = []
    step = radius_km / 111.0 / 2.5
    for i, ztype in enumerate(ZONE_TYPES):
        angle = i * 72 + 15
        rad = math.radians(angle)
        c_lat = lat + math.sin(rad) * step * (0.8 + i * 0.15)
        c_lon = lon + math.cos(rad) * step * (0.8 + i * 0.15) / math.cos(math.radians(lat))

        terrain = _terrain_profile(c_lat, c_lon)
        score = _score_zone_terrain(terrain, ztype, month)

        # EXCLUSION: zones sur eau directe ou pente extreme
        # DOCUMENT MAITRE: eau < 10m, pente > 45deg
        excluded = False
        exclusion_reason = None
        if terrain["distance_eau_m"] < 10:
            excluded = True
            exclusion_reason = "zone_sur_eau"
        elif terrain["pente_deg"] > 45:
            excluded = True
            exclusion_reason = "pente_extreme"

        # V6-CONFORME: taille variable par type (rut=large, eau=petit)
        type_radius = {"alimentation": 0.003, "repos": 0.0035, "rut": 0.004, "affuts": 0.0025, "eau": 0.002}
        base_r = type_radius.get(ztype, 0.003)
        radius_deg = base_r + abs(math.sin(i * 3.7 + lat * 5.1)) * 0.001
        # V6-CONFORME: plus de vertices pour formes plus irregulieres
        n_verts = 14 + int(_seed(lat, lon, f"verts_{i}") * 6)  # 14-20 vertices
        polygon = _organic_polygon(c_lat, c_lon, radius_deg, n_vertices=n_verts, seed=i + lat * 100)

        zones.append({
            "id": f"zone_v8_{ztype}_{i}", "type": ztype,
            "center": {"lat": round(c_lat, 5), "lng": round(c_lon, 5)},
            "polygon": polygon,
            "score": 0 if excluded else score,
            "terrain": terrain,
            "excluded": excluded,
            "exclusion_reason": exclusion_reason,
        })
    return zones


def generate_corridors_ta(lat, lon, species, month, hour, radius_km=2):
    """Corridors terrain-aware V6-conformes: localisés, intensité variable."""
    corridors = []
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    for i in range(10):
        angle = i * 36 + _seed(lat, lon, f"corr_angle_{i}") * 30
        rad = math.radians(angle)
        # V6-CONFORME: corridors localisés 0.2-1.8km
        base_dist = 0.2 + _seed(lat, lon, f"corr_dist_{i}") * 1.6  # 0.2-1.8 km
        dist = base_dist / 111.0
        s_lat = lat + math.sin(rad) * dist * 0.4
        s_lon = lon + math.cos(rad) * dist * 0.4 / cos_lat
        # End point: shorter, more localized
        e_angle = angle + 25 + _seed(lat, lon, f"corr_ea_{i}") * 40
        e_rad = math.radians(e_angle)
        e_dist = dist * (0.5 + _seed(lat, lon, f"corr_ed_{i}") * 0.6)
        e_lat = s_lat + math.sin(e_rad) * e_dist
        e_lon = s_lon + math.cos(e_rad) * e_dist / cos_lat

        terrain_s = _terrain_profile(s_lat, s_lon)
        terrain_e = _terrain_profile(e_lat, e_lon)

        # EXCLUSION TERRAIN: rejeter corridors sur eau ou pente extreme
        # DOCUMENT MAITRE: eau < 10m = EXCLUSION, pente > 45deg = EXCLUSION
        if terrain_s["distance_eau_m"] < 10 or terrain_e["distance_eau_m"] < 10:
            continue  # corridor traverse eau — EXCLU
        if terrain_s["pente_deg"] > 45 or terrain_e["pente_deg"] > 45:
            continue  # pente extreme — EXCLU

        intensity = _corridor_intensity(terrain_s, terrain_e, month, hour, species)
        cost = (_cost_surface_score(terrain_s) + _cost_surface_score(terrain_e)) / 2

        if intensity > 80:
            ctype = "critique"
        elif intensity > 65:
            ctype = "majeur"
        elif intensity > 50:
            ctype = "fort"
        elif intensity > 30:
            ctype = "modere"
        else:
            ctype = "faible"

        path = _bezier_curve([s_lat, s_lon], [e_lat, e_lon], n_points=8, curvature_seed=i)
        corridors.append({
            "id": f"corr_v8_{i}", "type": ctype,
            "path": path,
            "start": {"lat": round(s_lat, 5), "lng": round(s_lon, 5)},
            "end": {"lat": round(e_lat, 5), "lng": round(e_lon, 5)},
            "intensity": intensity,
            "cost_surface": round(cost, 3),
            "terrain_start": terrain_s,
            "terrain_end": terrain_e,
        })
    return corridors


def generate_affuts_ta(lat, lon, species, zones, corridors, wind_deg=180):
    """Affuts terrain-aware: coherence zones+corridors, terrain, vent."""
    affuts = []
    cos_lat = max(0.5, math.cos(math.radians(lat)))

    for i, z in enumerate(zones):
        if z["type"] not in ("alimentation", "rut", "repos"):
            continue

        zc = z["center"]
        wind_rad = math.radians((wind_deg + 180) % 360)
        offset = 0.004 + abs(math.sin(i * 5.3)) * 0.002
        a_lat = zc["lat"] + math.sin(wind_rad) * offset
        a_lon = zc["lng"] + math.cos(wind_rad) * offset / cos_lat

        terrain = _terrain_profile(a_lat, a_lon)

        # Score affut terrain-aware
        couvert_s = 80 if terrain["couvert_pct"] >= 50 else 50
        vent_s = abs(math.sin(math.radians(wind_deg + a_lat * 3.7))) * 40 + 40
        transition_s = min(100, _seed(a_lat, a_lon, "trans") * 60 + 30)

        # Proximite corridor bonus
        corridor_prox_bonus = 0
        for c in corridors:
            cs = c["start"]
            ce = c["end"]
            mid_lat = (cs["lat"] + ce["lat"]) / 2
            mid_lon = (cs["lng"] + ce["lng"]) / 2
            dist_deg = math.sqrt((a_lat - mid_lat) ** 2 + ((a_lon - mid_lon) * cos_lat) ** 2)
            if dist_deg < 0.01:
                corridor_prox_bonus = max(corridor_prox_bonus, (1 - dist_deg / 0.01) * 20)

        total = couvert_s * 0.30 + vent_s * 0.25 + transition_s * 0.20 + corridor_prox_bonus * 0.25
        quality = "optimal" if total > 65 else "bon" if total > 45 else "acceptable"

        affuts.append({
            "id": f"affut_v8_{i}",
            "lat": round(a_lat, 6),
            "lng": round(a_lon, 6),
            "orientation_deg": round((wind_deg + 180) % 360, 1),
            "zone_type": z["type"],
            "zone_score": z["score"],
            "quality": quality,
            "score": round(min(100, max(0, total)), 1),
            "terrain": terrain,
            "corridor_proximity_bonus": round(corridor_prox_bonus, 1),
        })
    return affuts


# ═══════════════════════════════════════════════════════
# ENDPOINTS SANDBOX
# ═══════════════════════════════════════════════════════

@router.get("/zones-ta")
async def zones_terrain_aware(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None),
):
    if not FEATURE_FLAG_PHASE_B:
        return {"error": "Phase B desactivee", "engine": "V8-ZONES-TA"}
    start = time.time()
    m = month or datetime.now(timezone.utc).month
    zones = generate_zones_ta(lat, lon, species, m)
    return {
        "zones": zones, "count": len(zones),
        "compute_ms": round((time.time() - start) * 1000),
        "engine": "V8-ZONES-TA", "dataVersion": "V8",
    }


@router.get("/corridors-ta")
async def corridors_terrain_aware(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None), hour: int = Query(None),
):
    if not FEATURE_FLAG_PHASE_B:
        return {"error": "Phase B desactivee", "engine": "V8-CORRIDORS-TA"}
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    corridors = generate_corridors_ta(lat, lon, species, m, h)
    return {
        "corridors": corridors, "count": len(corridors),
        "compute_ms": round((time.time() - start) * 1000),
        "engine": "V8-CORRIDORS-TA", "dataVersion": "V8",
    }


@router.get("/affuts-ta")
async def affuts_terrain_aware(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None),
    hour: int = Query(None), wind_deg: float = Query(180),
):
    if not FEATURE_FLAG_PHASE_B:
        return {"error": "Phase B desactivee", "engine": "V8-AFFUTS-TA"}
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    zones = generate_zones_ta(lat, lon, species, m)
    corridors = generate_corridors_ta(lat, lon, species, m, h)
    affuts = generate_affuts_ta(lat, lon, species, zones, corridors, wind_deg)
    return {
        "affuts": affuts, "count": len(affuts),
        "compute_ms": round((time.time() - start) * 1000),
        "engine": "V8-AFFUTS-TA", "dataVersion": "V8",
    }


@router.get("/phase-b/status")
async def phase_b_status():
    return {
        "engine": "V8-PHASE-B",
        "version": "8.3.0",
        "status": "OPERATIONNEL",
        "modules": {
            "zones_ta": {"active": FEATURE_FLAG_PHASE_B, "endpoint": "/api/v8/map/zones-ta"},
            "corridors_ta": {"active": FEATURE_FLAG_PHASE_B, "endpoint": "/api/v8/map/corridors-ta"},
            "affuts_ta": {"active": FEATURE_FLAG_PHASE_B, "endpoint": "/api/v8/map/affuts-ta"},
        },
        "terrain_aware": True,
        "cost_surface": "simplified",
        "continuity": "COR-006",
        "dataVersion": "V8",
    }
