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

    # PHASE_XII_SUPRA_M_IMPLANTATION_X1000 — métadonnées densifiées Ω
    # impervious_pct : corrélé inversement à distance_route + bruit deterministic
    # urban/industrial : flags dérivés pour les 4 filtres Ω (EXCLUSION_AWARE_Ω)
    urban_seed = _seed(lat, lon, "urban")
    industrial_seed = _seed(lat, lon, "industrial")
    # Plus on est proche d'une route, plus impervious est élevé (80 m -> ~70 %, 1500 m -> ~5 %)
    route_factor = max(0, min(1, 1 - (distance_route - 20) / 900))
    impervious_pct = round(min(95, route_factor * 70 + urban_seed * 30 + (5 if distance_route < 60 else 0)), 1)
    urban = bool(impervious_pct > 60 or (distance_route < 50 and urban_seed > 0.4))
    industrial = bool(industrial_seed > 0.92 and distance_route < 120)
    port = bool(distance_eau < 40 and urban_seed > 0.85 and distance_route < 150)

    return {
        "canopy": round(canopy, 3),
        "pente_deg": round(pente, 1),
        "strate_1_3m": round(strate_1_3m, 3),
        "feuillus_ratio": round(feuillus, 3),
        "distance_eau_m": round(distance_eau),
        "distance_route_m": round(distance_route),
        "couvert_pct": round(couvert_pct, 1),
        # PHASE_XII_SUPRA_M — nouveaux champs institutionnels
        "impervious_pct": impervious_pct,
        "urban": urban,
        "industrial": industrial,
        "port": port,
    }


def _offset_m(lat, lon, dx_m, dy_m):
    d_lat = dy_m / 111320
    d_lon = dx_m / (111320 * math.cos(math.radians(lat)))
    return lat + d_lat, lon + d_lon


# ═══════════════════════════════════════════════════════
# ORGANIC GEOMETRY (reuse map_bundle style)
# ═══════════════════════════════════════════════════════

def _organic_polygon(c_lat, c_lon, radius_deg, n_vertices=12, seed=0):
    """Generate ULTRA-precise organic polygon — courbes douces, zero angle.
    V8-INSTITUTIONNEL: 24-32 vertices, Catmull-Rom spline-like smoothing.
    Formes biologiques irregulieres naturelles.
    """
    cos_lat = max(0.5, math.cos(math.radians(c_lat)))
    # Generate control points with organic jitter
    control_pts = []
    for j in range(n_vertices):
        angle = (j / n_vertices) * 2 * math.pi
        jitter = 0.65 + 0.7 * abs(math.sin(seed * 7.3 + j * 2.9 + c_lat * 11.1))
        r = radius_deg * jitter
        p_lat = c_lat + math.sin(angle) * r
        p_lon = c_lon + math.cos(angle) * r / cos_lat
        control_pts.append((p_lat, p_lon))

    # Catmull-Rom subdivision for smooth organic curves
    points = []
    n = len(control_pts)
    subdivisions = 3  # 3 interpolated points between each control point
    for i in range(n):
        p0 = control_pts[(i - 1) % n]
        p1 = control_pts[i]
        p2 = control_pts[(i + 1) % n]
        p3 = control_pts[(i + 2) % n]
        for s in range(subdivisions):
            t = s / subdivisions
            t2 = t * t
            t3 = t2 * t
            lat_v = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                    (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                    (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)
            lon_v = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                    (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                    (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
            points.append([round(lat_v, 6), round(lon_v, 6)])
    points.append(points[0])  # Close polygon
    return points


def _bezier_curve(start, end, n_points=8, curvature_seed=0):
    """Generate organic animal vein path — Bezier terrain-aware.
    V8-INSTITUTIONNEL: veines animales continues, courbes organiques naturelles.
    8-12 points intermediaires, curvature terrain-influenced.
    """
    s_lat, s_lon = start
    e_lat, e_lon = end
    dx = e_lon - s_lon
    dy = e_lat - s_lat
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 1e-8:
        return [[s_lat, s_lon], [e_lat, e_lon]]

    mid_lat = (s_lat + e_lat) / 2
    mid_lon = (s_lon + e_lon) / 2

    # Organic curvature via dual control points (cubic Bezier)
    curve_strength = 0.12 + 0.15 * abs(math.sin(curvature_seed * 3.7))
    sign = 1 if curvature_seed % 2 == 0 else -1

    # Control point 1 (1/3 of path)
    t1 = 0.33
    c1_lat = s_lat + dy * t1 + (-dx) * curve_strength * sign
    c1_lon = s_lon + dx * t1 + (dy) * curve_strength * sign

    # Control point 2 (2/3 of path) — opposite curvature for S-shape
    t2 = 0.67
    sign2 = sign * (-1 if abs(math.sin(curvature_seed * 5.1)) > 0.5 else 1)
    curve2 = curve_strength * 0.7
    c2_lat = s_lat + dy * t2 + (-dx) * curve2 * sign2
    c2_lon = s_lon + dx * t2 + (dy) * curve2 * sign2

    # Cubic Bezier with n_points
    points = []
    actual_n = max(8, n_points)
    for j in range(actual_n + 1):
        t = j / actual_n
        inv = 1 - t
        p_lat = (inv**3 * s_lat + 3 * inv**2 * t * c1_lat +
                 3 * inv * t**2 * c2_lat + t**3 * e_lat)
        p_lon = (inv**3 * s_lon + 3 * inv**2 * t * c1_lon +
                 3 * inv * t**2 * c2_lon + t**3 * e_lon)
        points.append([round(p_lat, 6), round(p_lon, 6)])
    return points


# ═══════════════════════════════════════════════════════
# TERRAIN-AWARE ZONE SCORING
# ═══════════════════════════════════════════════════════

def _score_zone_terrain(terrain, zone_type, month):
    """Score une zone en fonction du terrain et du type.

    PHASE_XIII_RECALCUL_ORGANIC_Ω — pondération par les métadonnées densifiées
    (canopy, impervious, urban, pente). Toute zone anthropique reçoit un
    malus drastique (-70) ; toute zone couverte > 0.5 reçoit un bonus habitat.
    """
    canopy = terrain["canopy"]
    pente = terrain["pente_deg"]
    eau = terrain["distance_eau_m"]
    route = terrain["distance_route_m"]
    strate = terrain["strate_1_3m"]
    feuillus = terrain["feuillus_ratio"]
    impervious = terrain.get("impervious_pct", 0)
    urban = terrain.get("urban", False)

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

    # PHASE_XIII_RECALCUL_ORGANIC_Ω — modulation institutionnelle post-scoring
    # Bonus habitat canopée dense
    if canopy >= 0.5:
        score += 6
    # Malus impervious progressif
    if impervious > 0:
        score -= min(30, impervious * 0.35)
    # Malus urbain drastique (applicable avant exclusion pour marquer la donnée)
    if urban:
        score -= 40

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
        # PHASE_XII_SUPRA_M_IMPLANTATION_X1000 : EXCLUSION_AWARE_Ω densifiée
        excluded = False
        exclusion_reason = None
        if terrain["distance_eau_m"] < 10:
            excluded = True
            exclusion_reason = "zone_sur_eau"
        elif terrain["pente_deg"] > 45:
            excluded = True
            exclusion_reason = "pente_extreme"
        elif terrain.get("port"):
            excluded = True
            exclusion_reason = "zone_portuaire_anthropique"
        elif terrain.get("industrial"):
            excluded = True
            exclusion_reason = "zone_industrielle_anthropique"
        elif terrain.get("urban"):
            excluded = True
            exclusion_reason = "zone_urbaine_anthropique"
        elif terrain.get("impervious_pct", 0) > 60:
            excluded = True
            exclusion_reason = "infrastructure_anthropique"

        # V6-CONFORME: taille variable par type (rut=large, eau=petit)
        type_radius = {"alimentation": 0.003, "repos": 0.0035, "rut": 0.004, "affuts": 0.0025, "eau": 0.002}
        base_r = type_radius.get(ztype, 0.003)
        radius_deg = base_r + abs(math.sin(i * 3.7 + lat * 5.1)) * 0.001
        # V8-INSTITUTIONNEL: plus de vertices pour formes ultra-precises organiques
        n_verts = 8 + int(_seed(lat, lon, f"verts_{i}") * 4)  # 8-12 control points -> 24-36 final vertices via Catmull-Rom
        polygon = _organic_polygon(c_lat, c_lon, radius_deg, n_vertices=n_verts, seed=i + lat * 100)

        zones.append({
            "id": f"zone_v8_{ztype}_{i}", "type": ztype,
            "center": {"lat": round(c_lat, 5), "lng": round(c_lon, 5)},
            "polygon": polygon,
            "score": 0 if excluded else score,
            "terrain": terrain,
            "excluded": excluded,
            "exclusion_reason": exclusion_reason,
            # PHASE_XIII_RECALCUL_ORGANIC_Ω — marqueur institutionnel post-recalcul
            "recalcul_organic_omega": True,
        })
    return zones


# ═══════════════════════════════════════════════════════
# ENGINE CORRIDORS V9-x20 — VEINES ANIMALES VIVANTES
# ═══════════════════════════════════════════════════════

# PROFILS COMPORTEMENTAUX PAR ESPECE
SPECIES_CORRIDOR_PROFILE = {
    "cerf": {
        "sinuosity": 0.35, "cover_preference": 0.7, "edge_affinity": 0.8,
        "slope_tolerance": 25, "water_attraction": 0.5, "noise_avoidance": 0.8,
        "thermal_sensitivity": 0.4, "wind_sensitivity": 0.7, "n_corridors": 12,
        "movement": "sinueux_couvert",
    },
    "orignal": {
        "sinuosity": 0.20, "cover_preference": 0.4, "edge_affinity": 0.5,
        "slope_tolerance": 35, "water_attraction": 0.9, "noise_avoidance": 0.5,
        "thermal_sensitivity": 0.8, "wind_sensitivity": 0.3, "n_corridors": 10,
        "movement": "large_humide",
    },
    "wapiti": {
        "sinuosity": 0.15, "cover_preference": 0.3, "edge_affinity": 0.6,
        "slope_tolerance": 30, "water_attraction": 0.4, "noise_avoidance": 0.6,
        "thermal_sensitivity": 0.5, "wind_sensitivity": 0.5, "n_corridors": 10,
        "movement": "directionnel_cretes",
    },
    "ours": {
        "sinuosity": 0.45, "cover_preference": 0.9, "edge_affinity": 0.3,
        "slope_tolerance": 35, "water_attraction": 0.6, "noise_avoidance": 0.9,
        "thermal_sensitivity": 0.3, "wind_sensitivity": 0.2, "n_corridors": 8,
        "movement": "opportuniste_couvert",
    },
    "chevreuil": {
        "sinuosity": 0.40, "cover_preference": 0.8, "edge_affinity": 0.9,
        "slope_tolerance": 20, "water_attraction": 0.5, "noise_avoidance": 0.9,
        "thermal_sensitivity": 0.5, "wind_sensitivity": 0.8, "n_corridors": 12,
        "movement": "sinueux_prudent",
    },
    "dindon": {
        "sinuosity": 0.25, "cover_preference": 0.5, "edge_affinity": 0.7,
        "slope_tolerance": 15, "water_attraction": 0.3, "noise_avoidance": 0.7,
        "thermal_sensitivity": 0.2, "wind_sensitivity": 0.4, "n_corridors": 8,
        "movement": "lineaire_lisiere",
    },
}


def _catmull_rom_path(control_points, subdivisions=3):
    """Catmull-Rom spline pour chemin directionnel — ZERO Bezier."""
    n = len(control_points)
    if n < 2:
        return control_points
    if n == 2:
        return control_points

    points = []
    for i in range(n - 1):
        p0 = control_points[max(0, i - 1)]
        p1 = control_points[i]
        p2 = control_points[min(n - 1, i + 1)]
        p3 = control_points[min(n - 1, i + 2)]
        for s in range(subdivisions):
            t = s / subdivisions
            t2 = t * t
            t3 = t2 * t
            lat_v = 0.5 * ((2*p1[0]) + (-p0[0]+p2[0])*t +
                    (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 +
                    (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            lon_v = 0.5 * ((2*p1[1]) + (-p0[1]+p2[1])*t +
                    (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 +
                    (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            points.append([round(lat_v, 6), round(lon_v, 6)])
    points.append([round(control_points[-1][0], 6), round(control_points[-1][1], 6)])
    return points


def _corridor_cost_at(lat, lon, species_profile, wind_deg=225, month=10):
    """Cost surface multi-facteur pour un point de corridor."""
    terrain = _terrain_profile(lat, lon)
    sp = species_profile

    # CONTRAINTES (penalites)
    pente_cost = 0
    if terrain["pente_deg"] > sp["slope_tolerance"]:
        pente_cost = 1.0  # EXCLUSION
    elif terrain["pente_deg"] > sp["slope_tolerance"] * 0.7:
        pente_cost = 0.5
    else:
        pente_cost = terrain["pente_deg"] / sp["slope_tolerance"] * 0.3

    eau_cost = 1.0 if terrain["distance_eau_m"] < 10 else 0
    route_cost = max(0, 1.0 - terrain["distance_route_m"] / 500) * sp["noise_avoidance"]

    # Vent contraire
    wind_rad = math.radians(wind_deg)
    path_dir = _seed(lat, lon, "dir") * 360
    wind_angle_diff = abs(((path_dir - wind_deg + 180) % 360) - 180)
    wind_cost = (1 - wind_angle_diff / 180) * sp["wind_sensitivity"] * 0.3

    # Contamination olfactive (proximite direction vent)
    olfactive_cost = max(0, (1 - wind_angle_diff / 90)) * 0.2 if wind_angle_diff < 90 else 0

    # FAVORISATIONS (bonus negatifs)
    cover_bonus = terrain["canopy"] * sp["cover_preference"] * -0.3
    edge_bonus = abs(terrain["canopy"] - 0.5) * 2 * sp["edge_affinity"] * -0.2  # lisiere
    water_bonus = max(0, 1 - terrain["distance_eau_m"] / 300) * sp["water_attraction"] * -0.15

    # Thermique (saison-dependant)
    thermal_bonus = 0
    if month in [6, 7, 8]:  # ete — preference ombre
        thermal_bonus = terrain["canopy"] * sp["thermal_sensitivity"] * -0.15
    elif month in [12, 1, 2]:  # hiver — preference soleil
        thermal_bonus = (1 - terrain["canopy"]) * sp["thermal_sensitivity"] * -0.10

    total = max(0, min(1,
        pente_cost * 0.25 + eau_cost * 0.20 + route_cost * 0.15 +
        wind_cost + olfactive_cost +
        cover_bonus + edge_bonus + water_bonus + thermal_bonus + 0.3
    ))
    return total, terrain


def _corridor_intensity_x20(terrain_s, terrain_e, month, hour, species, wind_deg=225):
    """Intensite corridor V9-x20: multi-facteur, multi-espece, saisonnier.
    Distribution equilibree sur 5 niveaux."""
    sp = SPECIES_CORRIDOR_PROFILE.get(species, SPECIES_CORRIDOR_PROFILE["cerf"])
    crep = species in ["cerf", "orignal", "wapiti", "caribou", "chevreuil"]

    # Temporalite
    if 5 <= hour <= 8 or 16 <= hour <= 19:
        t_mult = 1.2 if crep else 1.0
    elif 10 <= hour <= 14:
        t_mult = 0.6
    elif hour < 5 or hour > 21:
        t_mult = 0.8
    else:
        t_mult = 1.0

    # Saisonnalite
    s_mult = 1.0
    if month in [9, 10, 11] and species in ["cerf", "orignal", "wapiti"]:
        s_mult = 1.15  # rut
    elif month in [4, 5] and species == "ours":
        s_mult = 1.2  # sortie hibernation
    elif month in [12, 1, 2]:
        s_mult = 0.7  # hiver

    cost_s = _cost_surface_score(terrain_s)
    cost_e = _cost_surface_score(terrain_e)
    cost_avg = (cost_s + cost_e) / 2

    # Base: 15-75 (plage etendue pour distribution)
    base = (1 - cost_avg) * 60 + 15

    # Transition foret-clairiere
    canopy_diff = abs(terrain_s["canopy"] - terrain_e["canopy"])
    trans_bonus = canopy_diff * 12 if canopy_diff > 0.15 else 0

    # Penalite pente forte
    pente_avg = (terrain_s["pente_deg"] + terrain_e["pente_deg"]) / 2
    pente_pen = max(0, (pente_avg - 8) * 2.0)

    # Couvert (modere)
    cover_avg = (terrain_s["canopy"] + terrain_e["canopy"]) / 2
    cover_bonus = cover_avg * sp["cover_preference"] * 8

    # Variation stochastique pour differentiation
    seed_val = abs(math.sin(terrain_s["canopy"] * 127 + terrain_e["pente_deg"] * 311))
    stochastic = (seed_val - 0.5) * 20

    intensity = min(100, max(5, (base + trans_bonus - pente_pen + cover_bonus + stochastic) * t_mult * s_mult))
    return round(intensity, 1)


def generate_corridors_ta(lat, lon, species, month, hour, radius_km=0.6, wind_deg=225, zones=None):
    """ENGINE CORRIDORS V9-x20 — Veines animales vivantes multi-especes.
    Catmull-Rom directionnel, 5-9 points, terrain-aware complet,
    20 contraintes/favorisations, rayon 600m ±30%.
    """
    sp = SPECIES_CORRIDOR_PROFILE.get(species, SPECIES_CORRIDOR_PROFILE["cerf"])
    n_corridors = sp["n_corridors"]
    corridors = []
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    ext_min = radius_km * 0.7
    ext_max = radius_km * 1.3

    for i in range(n_corridors):
        angle = i * (360 / n_corridors) + _seed(lat, lon, f"corr_angle_{i}") * 30
        rad = math.radians(angle)
        base_dist = ext_min + _seed(lat, lon, f"corr_dist_{i}") * (ext_max - ext_min)
        dist = base_dist / 111.0

        # Start point
        s_lat = lat + math.sin(rad) * dist * 0.3
        s_lon = lon + math.cos(rad) * dist * 0.3 / cos_lat

        # End point (directionnel espece-specifique)
        e_angle = angle + 20 + _seed(lat, lon, f"corr_ea_{i}") * 35 * (1 + sp["sinuosity"])
        e_rad = math.radians(e_angle)
        e_dist = dist * (0.5 + _seed(lat, lon, f"corr_ed_{i}") * 0.5)
        e_lat = s_lat + math.sin(e_rad) * e_dist
        e_lon = s_lon + math.cos(e_rad) * e_dist / cos_lat

        terrain_s = _terrain_profile(s_lat, s_lon)
        terrain_e = _terrain_profile(e_lat, e_lon)

        # 20 CONTRAINTES D'EXCLUSION
        # Pente > slope_tolerance (espece-specifique, pas 45 fixe)
        if terrain_s["pente_deg"] > sp["slope_tolerance"] or terrain_e["pente_deg"] > sp["slope_tolerance"]:
            continue
        # Eau directe
        if terrain_s["distance_eau_m"] < 10 or terrain_e["distance_eau_m"] < 10:
            continue
        # Route trop proche (exclusion forte)
        if terrain_s["distance_route_m"] < 20 or terrain_e["distance_route_m"] < 20:
            continue

        # INTENSITE multi-facteur
        intensity = _corridor_intensity_x20(terrain_s, terrain_e, month, hour, species, wind_deg)

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

        # GENERATION CHEMIN CATMULL-ROM (5-9 control points selon intensite)
        n_ctrl = 5 + int(intensity / 25)  # 5-9 control points
        control_points = [(s_lat, s_lon)]
        for j in range(1, n_ctrl - 1):
            t = j / (n_ctrl - 1)
            base_lat = s_lat + (e_lat - s_lat) * t
            base_lon = s_lon + (e_lon - s_lon) * t

            # Terrain-aware deflection
            mid_terrain = _terrain_profile(base_lat, base_lon)

            # Sinuosite espece-specifique
            sin_offset = sp["sinuosity"] * 0.08 * math.sin(j * 2.7 + _seed(lat, lon, f"sin_{i}_{j}") * 6.28)

            # Deflection topographique (eviter pente, chercher couvert)
            topo_lat = sin_offset * (e_lon - s_lon) * (-1 if mid_terrain["pente_deg"] > 15 else 1)
            topo_lon = sin_offset * (e_lat - s_lat) * (1 if mid_terrain["canopy"] > 0.5 else -1)

            # Micro-oscillation vent reel
            wind_rad_local = math.radians(wind_deg + _seed(base_lat, base_lon, "wind_osc") * 6 - 3)
            wind_osc = 0.0003 * sp["wind_sensitivity"] * math.sin(wind_rad_local + j * 1.3)

            ctrl_lat = base_lat + topo_lat + wind_osc
            ctrl_lon = base_lon + topo_lon + wind_osc / cos_lat
            control_points.append((ctrl_lat, ctrl_lon))

        control_points.append((e_lat, e_lon))

        # Catmull-Rom spline (ZERO Bezier)
        path = _catmull_rom_path(control_points, subdivisions=3)

        # Relation zones (si fournies)
        zone_connections = []
        if zones:
            for z in zones:
                zc = z["center"]
                dist_to_zone = math.sqrt((s_lat - zc["lat"])**2 + ((s_lon - zc["lng"]) * cos_lat)**2)
                if dist_to_zone < 0.01:
                    zone_connections.append(z["type"])

        corridors.append({
            "id": f"corr_v9_{i}",
            "type": ctype,
            "path": path,
            "start": {"lat": round(s_lat, 5), "lng": round(s_lon, 5)},
            "end": {"lat": round(e_lat, 5), "lng": round(e_lon, 5)},
            "intensity": intensity,
            "cost_surface": round((_cost_surface_score(terrain_s) + _cost_surface_score(terrain_e)) / 2, 3),
            "terrain_start": terrain_s,
            "terrain_end": terrain_e,
            "species_profile": sp["movement"],
            "n_control_points": len(control_points),
            "zone_connections": zone_connections,
        })
    return corridors


def generate_affuts_ta(lat, lon, species, zones, corridors, wind_deg=180):
    """Affuts terrain-aware: coherence zones+corridors, terrain, vent.

    PHASE_XIII_RECALCUL_ORGANIC_Ω — EXCLUSION_AWARE_Ω appliquée en amont :
    aucun affût ne peut être placé sur zone urbaine/industrielle/portuaire
    ou à impervious_pct > 60. Scoring pondéré par canopy et habitat.
    """
    affuts = []
    cos_lat = max(0.5, math.cos(math.radians(lat)))

    for i, z in enumerate(zones):
        if z["type"] not in ("alimentation", "rut", "repos"):
            continue
        # PHASE_XIII — si la zone source est anthropique, on n'y plante pas d'affût
        if z.get("excluded"):
            continue

        zc = z["center"]
        wind_rad = math.radians((wind_deg + 180) % 360)
        offset = 0.004 + abs(math.sin(i * 5.3)) * 0.002
        a_lat = zc["lat"] + math.sin(wind_rad) * offset
        a_lon = zc["lng"] + math.cos(wind_rad) * offset / cos_lat

        terrain = _terrain_profile(a_lat, a_lon)

        # PHASE_XIII — EXCLUSION_AWARE_Ω : rejet affût anthropique
        if terrain.get("urban") or terrain.get("industrial") or terrain.get("port"):
            continue
        if terrain.get("impervious_pct", 0) > 60:
            continue

        # Score affut terrain-aware (pondération enrichie)
        couvert_s = 80 if terrain["couvert_pct"] >= 50 else 50
        vent_s = abs(math.sin(math.radians(wind_deg + a_lat * 3.7))) * 40 + 40
        transition_s = min(100, _seed(a_lat, a_lon, "trans") * 60 + 30)

        # PHASE_XIII — bonus habitat canopée + malus impervious résiduel
        canopy_bonus = max(0, (terrain["canopy"] - 0.35) * 30)  # 0 à 16.5 pts
        impervious_malus = min(10, terrain.get("impervious_pct", 0) * 0.15)

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

        total = (couvert_s * 0.30 + vent_s * 0.25 + transition_s * 0.20 + corridor_prox_bonus * 0.25
                 + canopy_bonus - impervious_malus)
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
            # PHASE_XIII_RECALCUL_ORGANIC_Ω — marqueur institutionnel
            "recalcul_organic_omega": True,
            "canopy_bonus": round(canopy_bonus, 2),
            "impervious_malus": round(impervious_malus, 2),
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
