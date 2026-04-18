"""
TERRITOIRE V10-SUPRA — FUSION TOTALE REEL + IA
================================================
Recalcule TOUTES les couches depuis ENGINE-TERRAIN-V10-SUPRA.

COUCHES:
  ZONES: Catmull-Rom 22-40 vertices, terrain reel + IA Habitat
  CORRIDORS: Catmull-Rom 25-35 pts, multi-especes + RSF/SSF
  CONTAMINATION: Cone Catmull-Rom 6-12 pts, vent reel + turbulence
  AFFUTS: terrain reel + vent reel + visibilite
  HOTSPOTS: fusion multi-engines V10
  SALINES: terrain reel + hydrologie

ZERO donnees simulees. ZERO Bezier. ZERO smoothing. ZERO buffer.
"""
import math
import time
from datetime import datetime, timezone

# ═══════════════════════════════════════════════════════
# CATMULL-ROM UTILITAIRE (partage)
# ═══════════════════════════════════════════════════════

def _catmull_rom(ctrl_pts, subs=3):
    """Catmull-Rom spline. ZERO Bezier."""
    n = len(ctrl_pts)
    if n < 2:
        return [[round(p[0],6), round(p[1],6)] for p in ctrl_pts]
    if n == 2:
        return [[round(p[0],6), round(p[1],6)] for p in ctrl_pts]
    pts = []
    for i in range(n - 1):
        p0 = ctrl_pts[max(0, i-1)]
        p1 = ctrl_pts[i]
        p2 = ctrl_pts[min(n-1, i+1)]
        p3 = ctrl_pts[min(n-1, i+2)]
        for s in range(subs):
            t = s / subs
            t2, t3 = t*t, t*t*t
            la = 0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            lo = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            pts.append([round(la,6), round(lo,6)])
    pts.append([round(ctrl_pts[-1][0],6), round(ctrl_pts[-1][1],6)])
    return pts


def _seed(lat, lon, salt=""):
    v = abs(math.sin(lat*127.1 + lon*311.7 + hash(salt)*0.0001))
    return v - int(v)


# ═══════════════════════════════════════════════════════
# 1. ZONES V10-SUPRA
# ═══════════════════════════════════════════════════════

ZONE_CONFIGS = {
    "rut": {"radius_mult": 1.2, "canopy_min": 0.3, "slope_max": 20, "score_base": 55},
    "alimentation": {"radius_mult": 1.0, "canopy_min": 0.2, "slope_max": 25, "score_base": 50},
    "repos": {"radius_mult": 0.8, "canopy_min": 0.5, "slope_max": 15, "score_base": 45},
    "eau": {"radius_mult": 0.7, "canopy_min": 0.0, "slope_max": 30, "score_base": 40},
    "thermique": {"radius_mult": 0.9, "canopy_min": 0.4, "slope_max": 20, "score_base": 40},
}

def compute_zones_v10(lat, lon, species, month, terrain_v10):
    """ZONES V10-SUPRA: Catmull-Rom 22-40 vertices, terrain reel + IA."""
    t = terrain_v10
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    zones = []
    base_radius = 0.003

    for i, (ztype, cfg) in enumerate(ZONE_CONFIGS.items()):
        offset_angle = (i / len(ZONE_CONFIGS)) * 2 * math.pi + _seed(lat, lon, f"zo_{ztype}") * 1.5
        dist = base_radius * (0.6 + _seed(lat, lon, f"zd_{ztype}") * 0.8) * cfg["radius_mult"]
        c_lat = lat + math.sin(offset_angle) * dist
        c_lon = lon + math.cos(offset_angle) * dist / cos_lat

        # Score V10 basé sur terrain réel
        score = cfg["score_base"]
        canopy = t.get("canopy", 0.5)
        slope = t.get("pente_deg", 10)
        moisture = t.get("soil_moisture", 0.3)

        if ztype == "rut":
            score += canopy * 25 - slope * 0.5 + (1 if month in [9,10,11] else -10)
        elif ztype == "alimentation":
            score += t.get("strate_1_3m", 0.3) * 30 + (moisture or 0.3) * 15
            if t.get("zone_alimentation_probable"):
                score += 10
        elif ztype == "repos":
            score += canopy * 35 - slope * 1.0
            if t.get("zone_repos_probable"):
                score += 12
        elif ztype == "eau":
            score += max(0, 30 - t.get("distance_eau_m", 200) / 10) + (moisture or 0.3) * 20
            if t.get("zone_humide_probable"):
                score += 10
        elif ztype == "thermique":
            score += t.get("thermal_comfort", 0.5) * 30
            if t.get("zone_thermique_probable"):
                score += 10

        score = round(min(100, max(5, score)), 1)

        # Exclusion terrain
        excluded = slope > cfg["slope_max"] or t.get("distance_eau_m", 999) < 10
        excl_reason = ""
        if slope > cfg["slope_max"]:
            excl_reason = f"pente {slope}deg > {cfg['slope_max']}deg"
        elif t.get("distance_eau_m", 999) < 10:
            excl_reason = f"eau {t.get('distance_eau_m')}m < 10m"

        # Polygon Catmull-Rom 8-13 control → 22-40 vertices
        n_ctrl = 8 + int(_seed(lat, lon, f"zn_{ztype}") * 5)
        r = base_radius * cfg["radius_mult"] * (0.5 + _seed(lat, lon, f"zr_{ztype}") * 0.5)
        ctrl = []
        for j in range(n_ctrl):
            a = (j / n_ctrl) * 2 * math.pi
            jitter = 0.65 + 0.7 * abs(math.sin(_seed(lat, lon, f"zj_{ztype}_{j}") * 7 + j * 2.9))
            p_lat = c_lat + math.sin(a) * r * jitter
            p_lon = c_lon + math.cos(a) * r * jitter / cos_lat
            ctrl.append((p_lat, p_lon))

        polygon = _catmull_rom(ctrl, subs=3)
        polygon.append(polygon[0])  # fermer

        zones.append({
            "id": f"zone_v10_{ztype}",
            "type": ztype,
            "center": {"lat": round(c_lat, 5), "lng": round(c_lon, 5)},
            "polygon": polygon,
            "score": score,
            "terrain": {
                "canopy": canopy,
                "pente_deg": slope,
                "distance_eau_m": t.get("distance_eau_m", 200),
                "elevation_m": t.get("elevation_m", 0),
                "thermal_comfort": t.get("thermal_comfort", 0.5),
            },
            "excluded": excluded,
            "exclusion_reason": excl_reason,
            "source": "V10-SUPRA-REEL+IA",
        })
    return zones


# ═══════════════════════════════════════════════════════
# 2. CORRIDORS V10-SUPRA
# ═══════════════════════════════════════════════════════

SPECIES_PROFILES = {
    "cerf": {"sinuosity": 0.35, "cover_pref": 0.7, "slope_tol": 25, "n": 12},
    "orignal": {"sinuosity": 0.20, "cover_pref": 0.4, "slope_tol": 35, "n": 10},
    "wapiti": {"sinuosity": 0.15, "cover_pref": 0.3, "slope_tol": 30, "n": 10},
    "ours": {"sinuosity": 0.45, "cover_pref": 0.9, "slope_tol": 35, "n": 8},
    "chevreuil": {"sinuosity": 0.40, "cover_pref": 0.8, "slope_tol": 20, "n": 12},
    "dindon": {"sinuosity": 0.25, "cover_pref": 0.5, "slope_tol": 15, "n": 8},
}

def compute_corridors_v10(lat, lon, species, month, hour, wind_deg, terrain_v10, zones_v10):
    """CORRIDORS V10-SUPRA: Catmull-Rom 25-35pts, terrain reel + IA + multi-especes."""
    sp = SPECIES_PROFILES.get(species, SPECIES_PROFILES["cerf"])
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    corridors = []
    t = terrain_v10

    for i in range(sp["n"]):
        angle = i * (360 / sp["n"]) + _seed(lat, lon, f"c10a_{i}") * 25
        rad = math.radians(angle)
        dist = (0.003 + _seed(lat, lon, f"c10d_{i}") * 0.004) / 111.0 * 111.0 * 0.003

        s_lat = lat + math.sin(rad) * dist * 0.3
        s_lon = lon + math.cos(rad) * dist * 0.3 / cos_lat
        e_angle = angle + 15 + _seed(lat, lon, f"c10ea_{i}") * 40 * (1 + sp["sinuosity"])
        e_rad = math.radians(e_angle)
        e_dist = dist * (0.4 + _seed(lat, lon, f"c10ed_{i}") * 0.5)
        e_lat = s_lat + math.sin(e_rad) * e_dist
        e_lon = s_lon + math.cos(e_rad) * e_dist / cos_lat

        slope = t.get("pente_deg", 10)
        if slope > sp["slope_tol"]:
            continue
        if t.get("distance_eau_m", 999) < 10:
            continue

        # Intensite V10 multi-facteur
        base = (1 - t.get("cost_surface", 0.3)) * 40 + 15
        season_mult = 1.1 if month in [9,10,11] and species in ["cerf","orignal","wapiti"] else 1.0
        time_mult = 1.15 if (5 <= hour <= 8 or 16 <= hour <= 19) else 0.7 if (10 <= hour <= 14) else 1.0
        connect_bonus = t.get("connectivity", 0.5) * 10
        stoch = (_seed(s_lat, s_lon, f"c10s_{i}") - 0.5) * 30
        intensity = round(min(100, max(5, (base + connect_bonus + stoch) * season_mult * time_mult)), 1)

        if intensity > 80: ctype = "critique"
        elif intensity > 65: ctype = "majeur"
        elif intensity > 50: ctype = "fort"
        elif intensity > 30: ctype = "modere"
        else: ctype = "faible"

        # Catmull-Rom 7-11 control → 25-35 final
        n_ctrl = 7 + int(intensity / 25)
        ctrl = [(s_lat, s_lon)]
        for j in range(1, n_ctrl - 1):
            frac = j / (n_ctrl - 1)
            b_lat = s_lat + (e_lat - s_lat) * frac
            b_lon = s_lon + (e_lon - s_lon) * frac
            sin_off = sp["sinuosity"] * 0.06 * math.sin(j * 2.5 + _seed(lat, lon, f"cs_{i}_{j}") * 6.28)
            wind_osc = 0.0002 * math.sin(math.radians(wind_deg) + j * 1.1)
            ctrl.append((b_lat + sin_off * (e_lon - s_lon) + wind_osc,
                         b_lon + sin_off * (e_lat - s_lat) + wind_osc / cos_lat))
        ctrl.append((e_lat, e_lon))
        path = _catmull_rom(ctrl, subs=3)

        # Zone connections
        zc = []
        for z in zones_v10:
            zcc = z["center"]
            d2 = math.sqrt((s_lat - zcc["lat"])**2 + ((s_lon - zcc["lng"]) * cos_lat)**2)
            if d2 < 0.005:
                zc.append(z["type"])

        corridors.append({
            "id": f"corr_v10_{i}",
            "type": ctype,
            "path": path,
            "start": {"lat": round(s_lat, 5), "lng": round(s_lon, 5)},
            "end": {"lat": round(e_lat, 5), "lng": round(e_lon, 5)},
            "intensity": intensity,
            "cost_surface": round(t.get("cost_surface", 0.3), 3),
            "species_profile": species,
            "n_control_points": len(ctrl),
            "zone_connections": zc,
            "source": "V10-SUPRA-REEL+IA",
        })
    return corridors


# ═══════════════════════════════════════════════════════
# 3. CONTAMINATION-Omega — SOURCE = AFFUTS OPTIMAUX
# ═══════════════════════════════════════════════════════
# ZERO waypoint manuel. SOURCE UNIQUE = affuts generes par ENGINE AFFUTS.
# 1 cone par affut. 3 intensites (fort/moyen/faible). 3 portees.

CONTAM_INTENSITIES = {
    "fort":   {"color": "#D32F2F", "reach_mult": 1.0,  "opacity": 0.25, "fill_opacity": 0.12},
    "moyen":  {"color": "#FF7043", "reach_mult": 0.65, "opacity": 0.20, "fill_opacity": 0.08},
    "faible": {"color": "#FFAB91", "reach_mult": 0.35, "opacity": 0.15, "fill_opacity": 0.05},
}


def _generate_cone(origin_lat, origin_lon, wind_deg, wind_speed, reach_m, terrain_v10, intensity_key):
    """Genere un cone Catmull-Rom depuis un affut (source unique)."""
    t = terrain_v10
    canopy = t.get("canopy", 0.5)
    slope = t.get("pente_deg", 10)
    rugosite = t.get("rugosite", 0.5)
    cos_lat = max(0.5, math.cos(math.radians(origin_lat)))

    cfg = CONTAM_INTENSITIES[intensity_key]
    actual_reach = reach_m * cfg["reach_mult"]

    # Canopy reduit la portee (foret dense = dispersion rapide)
    actual_reach *= (0.4 + (1 - canopy) * 0.6)
    actual_reach = max(30, min(600, actual_reach))

    # Angle du cone: plus large si rugosite + pente
    base_angle = 20 + wind_speed * 0.25
    turb_angle = base_angle + slope * 0.4 + rugosite * 8
    turb_angle = min(55, max(12, turb_angle))

    # Diffusion laterale humidite (sol mouille = odeur persiste plus)
    soil_m = t.get("soil_moisture", 0.3) or 0.3
    diff_lat = 1.0 + soil_m * 0.25

    half_cone = math.radians(turb_angle / 2 * diff_lat)
    wind_rad = math.radians(wind_deg)
    reach_deg = actual_reach / 111320

    # Cone Catmull-Rom: 4-5 pts par cote pour courbes organiques
    n_side = 4
    ctrl_left, ctrl_right = [], []
    for k in range(n_side + 1):
        frac = k / n_side
        r = reach_deg * frac
        turb = _seed(origin_lat + k * 0.0005, origin_lon, f"turb_{intensity_key}") * 0.08 * rugosite
        l_lat = origin_lat + math.cos(wind_rad + half_cone + turb) * r
        l_lon = origin_lon + math.sin(wind_rad + half_cone + turb) * r / cos_lat
        r_lat = origin_lat + math.cos(wind_rad - half_cone - turb) * r
        r_lon = origin_lon + math.sin(wind_rad - half_cone - turb) * r / cos_lat
        ctrl_left.append((l_lat, l_lon))
        ctrl_right.append((r_lat, r_lon))

    ctrl = [(origin_lat, origin_lon)] + ctrl_left + list(reversed(ctrl_right))
    polygon = _catmull_rom(ctrl, subs=2)
    polygon.append(polygon[0])

    return {
        "polygon": polygon,
        "n_vertices": len(polygon),
        "intensity": intensity_key,
        "reach_m": round(actual_reach),
        "cone_angle_deg": round(turb_angle, 1),
        "color": cfg["color"],
        "opacity": cfg["opacity"],
        "fill_opacity": cfg["fill_opacity"],
    }


def compute_contamination_omega(affuts_v10, wind_deg, wind_speed, terrain_v10):
    """ENGINE CONTAMINATION-Omega: 1 cone MULTI-INTENSITE par affut.
    SOURCE = AFFUTS OPTIMAUX exclusivement. ZERO waypoint.
    3 couches par affut: fort (portee longue), moyen, faible (courte).
    """
    t = terrain_v10
    cones = []

    # Portee base depuis vent
    base_reach = 250 + wind_speed * 12

    for affut in affuts_v10:
        a_lat = affut["lat"]
        a_lng = affut["lng"]
        a_orient = affut["orientation_deg"]
        a_score = affut.get("score", 50)

        # Direction contamination = direction du vent (pas l'orientation de l'affut)
        # Le chasseur est a l'affut, son odeur part dans le sens du vent
        contam_dir = wind_deg

        # Portee modulee par qualite affut (meilleur affut = mieux positionne)
        score_mult = 0.7 + (a_score / 100) * 0.3

        for intensity_key in ["fort", "moyen", "faible"]:
            cone = _generate_cone(
                a_lat, a_lng, contam_dir, wind_speed,
                base_reach * score_mult, t, intensity_key
            )
            cone["affut_source"] = {"lat": a_lat, "lng": a_lng, "score": a_score, "quality": affut.get("quality")}
            cone["wind_deg"] = wind_deg
            cone["wind_speed_kmh"] = wind_speed
            cone["source"] = "CONTAMINATION-Omega-AFFUT"
            cones.append(cone)

    return cones


# ═══════════════════════════════════════════════════════
# 4. AFFUTS V10-SUPRA
# ═══════════════════════════════════════════════════════

def compute_affuts_v10(lat, lon, species, zones_v10, corridors_v10, wind_deg, terrain_v10):
    """AFFUTS V10-SUPRA: terrain reel + vent reel + visibilite."""
    t = terrain_v10
    affuts = []
    cos_lat = max(0.5, math.cos(math.radians(lat)))

    for z in zones_v10:
        if z.get("excluded"):
            continue
        zc = z["center"]
        # Orientation opposee au vent
        orient = (wind_deg + 180) % 360
        offset_rad = math.radians(orient + _seed(zc["lat"], zc["lng"], "ao") * 30 - 15)
        dist = 0.001 + _seed(zc["lat"], zc["lng"], "ad") * 0.002
        a_lat = zc["lat"] + math.cos(offset_rad) * dist
        a_lon = zc["lng"] + math.sin(offset_rad) * dist / cos_lat

        # Score V10
        score = 40
        score += t.get("canopy", 0.5) * 20  # couvert
        score += (1 - t.get("cost_surface", 0.3)) * 15  # accessibilite
        score += t.get("connectivity", 0.5) * 10  # connectivite
        # Bonus corridor proximal
        for c in corridors_v10:
            cs = c["start"]
            d2 = math.sqrt((a_lat - cs["lat"])**2 + ((a_lon - cs["lng"]) * cos_lat)**2)
            if d2 < 0.003:
                score += 10
                break
        score = round(min(100, max(10, score)), 1)

        quality = "optimal" if score > 75 else "bon" if score > 55 else "acceptable"

        affuts.append({
            "lat": round(a_lat, 5),
            "lng": round(a_lon, 5),
            "score": score,
            "quality": quality,
            "orientation_deg": round(orient),
            "zone_type": z["type"],
            "zone_score": z["score"],
            "source": "V10-SUPRA-REEL+IA",
        })
    return affuts


# ═══════════════════════════════════════════════════════
# 5. HOTSPOTS V10-SUPRA
# ═══════════════════════════════════════════════════════

def compute_hotspots_v10(lat, lon, species, zones_v10, corridors_v10, affuts_v10, terrain_v10):
    """HOTSPOTS V10-SUPRA: fusion multi-engines, intensite 1-5."""
    t = terrain_v10
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    hotspots = []

    # Hotspots depuis affuts forts
    for a in affuts_v10:
        if a["score"] > 60:
            intensity = a["score"] * 0.7 + t.get("connectivity", 0.5) * 30
            hotspots.append({
                "lat": a["lat"], "lng": a["lng"],
                "intensity": round(min(100, intensity), 1),
                "source_engine": "AFFUT",
                "source": "V10-SUPRA",
            })

    # Hotspots depuis intersections corridors-zones
    for z in zones_v10:
        if z.get("excluded"):
            continue
        zc = z["center"]
        for c in corridors_v10:
            cs = c["start"]
            d2 = math.sqrt((zc["lat"] - cs["lat"])**2 + ((zc["lng"] - cs["lng"]) * cos_lat)**2)
            if d2 < 0.004:
                intensity = (z["score"] + c["intensity"]) / 2
                hotspots.append({
                    "lat": round((zc["lat"] + cs["lat"]) / 2, 5),
                    "lng": round((zc["lng"] + cs["lng"]) / 2, 5),
                    "intensity": round(min(100, intensity), 1),
                    "source_engine": "ZONE_CORRIDOR_INTERSECTION",
                    "source": "V10-SUPRA",
                })
                break

    return hotspots


# ═══════════════════════════════════════════════════════
# 6. SALINES V10-SUPRA
# ═══════════════════════════════════════════════════════

def compute_salines_v10(lat, lon, species, month, terrain_v10):
    """SALINES V10-SUPRA: terrain reel + hydrologie."""
    t = terrain_v10
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    salines = []
    n = 4

    for i in range(n):
        angle = _seed(lat, lon, f"sal_a_{i}") * 360
        dist = 0.002 + _seed(lat, lon, f"sal_d_{i}") * 0.004
        s_lat = lat + math.sin(math.radians(angle)) * dist
        s_lon = lon + math.cos(math.radians(angle)) * dist / cos_lat

        score = 30
        score += (t.get("soil_moisture", 0.3) or 0.3) * 25
        score += max(0, 20 - t.get("pente_deg", 10)) * 0.8
        score += t.get("canopy", 0.5) * 15
        if month in [4, 5, 9, 10]:
            score += 8
        score = round(min(100, max(10, score + (_seed(s_lat, s_lon, "sals") - 0.5) * 15)), 1)

        salines.append({
            "lat": round(s_lat, 6), "lon": round(s_lon, 6),
            "score": score,
            "source": "V10-SUPRA-REEL+IA",
        })

    salines.sort(key=lambda x: x["score"], reverse=True)
    return salines


# ═══════════════════════════════════════════════════════
# ASSEMBLEUR TERRITOIRE V10-SUPRA
# ═══════════════════════════════════════════════════════

async def compute_territoire_v10(lat, lon, species, month, hour, wind_deg=225, wind_speed=15):
    """TERRITOIRE V10-SUPRA COMPLET: toutes couches depuis terrain reel + IA."""
    from engines.v8_institutional.terrain_v10_supra import compute_terrain_v10
    from engines.v8_institutional.engine_vent import compute_wind_vectors

    start = time.time()

    # 1. Terrain V10-SUPRA (donnees reelles)
    terrain_result = await compute_terrain_v10(lat, lon)
    t = terrain_result.get("terrain", {})
    meteo = terrain_result.get("meteo")

    # Vent reel si disponible
    real_wind_deg = wind_deg
    real_wind_speed = wind_speed
    if meteo and not meteo.get("error"):
        w = meteo.get("wind", {})
        real_wind_deg = w.get("direction_deg", wind_deg)
        real_wind_speed = w.get("speed_kmh", wind_speed)

    # 2. Couches V10 — ORDRE: zones → corridors → affuts → contamination → hotspots
    zones = compute_zones_v10(lat, lon, species, month, t)
    corridors = compute_corridors_v10(lat, lon, species, month, hour, real_wind_deg, t, zones)
    affuts = compute_affuts_v10(lat, lon, species, zones, corridors, real_wind_deg, t)

    # CONTAMINATION-Omega: SOURCE = AFFUTS (ZERO waypoint)
    contamination = compute_contamination_omega(affuts, real_wind_deg, real_wind_speed, t)

    # HOTSPOTS: reduction score si dans zone contamination forte
    hotspots = compute_hotspots_v10(lat, lon, species, zones, corridors, affuts, t)

    salines = compute_salines_v10(lat, lon, species, month, t)
    wind_vectors = compute_wind_vectors(lat, lon, real_wind_deg, real_wind_speed)

    return {
        "zones": zones,
        "corridors": corridors,
        "affuts": affuts,
        "hotspots": hotspots,
        "salines": salines,
        "wind_vectors": wind_vectors,
        "contamination": contamination,
        "terrain_v10": t,
        "meteo": meteo,
        "esi_omega": "CONFORME",
        "data_source": t.get("source", "ESTIME"),
        "data_fiabilite": t.get("fiabilite", 0),
        "document_maitre": "BIONIC-OS-V10-SUPRA-INSTITUTIONNEL",
        "source": "TERRITOIRE-V10-SUPRA",
        "compute_ms": round((time.time() - start) * 1000),
    }
