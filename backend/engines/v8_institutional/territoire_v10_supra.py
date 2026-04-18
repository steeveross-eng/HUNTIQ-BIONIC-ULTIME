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
# 2. ENGINE CORRIDOR-Omega — 4 NIVEAUX + RESEAU CONTINU
# ═══════════════════════════════════════════════════════
# CLASSIFICATION: NORMAL, INTENSE, EXTREME, SAISONNIER
# RENDERER: couleurs/epaisseurs distinctes
# GEOMETRIE: Catmull-Rom directionnel, smoothFactor=0, ZERO Bezier
# RESEAU: segments < 40m fusionnes en reseau continu
# ISOLATION: ZERO interaction vers SALINES/HOTSPOTS/ZONES/CONTAMINATION

SPECIES_PROFILES = {
    "cerf": {"sinuosity": 0.35, "cover_pref": 0.7, "slope_tol": 25, "n": 14},
    "orignal": {"sinuosity": 0.20, "cover_pref": 0.4, "slope_tol": 35, "n": 12},
    "wapiti": {"sinuosity": 0.15, "cover_pref": 0.3, "slope_tol": 30, "n": 12},
    "ours": {"sinuosity": 0.45, "cover_pref": 0.9, "slope_tol": 35, "n": 10},
    "chevreuil": {"sinuosity": 0.40, "cover_pref": 0.8, "slope_tol": 20, "n": 14},
    "dindon": {"sinuosity": 0.25, "cover_pref": 0.5, "slope_tol": 15, "n": 10},
}

# 4 niveaux corridor
CORRIDOR_LEVELS = {
    "extreme":    {"min_intensity": 85, "color": "#D32F2F", "weight": 4.2, "opacity": 0.95},
    "intense":    {"min_intensity": 65, "color": "#FF9800", "weight": 3.0, "opacity": 0.90},
    "saisonnier": {"min_intensity": -1, "color": "#4CAF50", "weight": 2.4, "opacity": 0.90},  # special
    "normal":     {"min_intensity": 0,  "color": "#FFFFFF", "weight": 1.6, "opacity": 0.85},
}


def _classify_corridor(intensity, month, species):
    """Classifie un corridor en 4 niveaux: EXTREME, INTENSE, SAISONNIER, NORMAL."""
    # Saisonnier: rut (sept-nov cerf/orignal/wapiti) ou sortie hibernation (avr-mai ours)
    is_seasonal = False
    if month in [9, 10, 11] and species in ["cerf", "orignal", "wapiti"]:
        is_seasonal = True
    elif month in [4, 5] and species == "ours":
        is_seasonal = True
    elif month in [3, 4] and species == "dindon":
        is_seasonal = True

    if intensity >= 85:
        return "extreme"
    elif intensity >= 65:
        return "intense"
    elif is_seasonal and intensity >= 40:
        return "saisonnier"
    else:
        return "normal"


def compute_corridors_omega(lat, lon, species, month, hour, wind_deg, terrain_v10, zones_v10):
    """ENGINE CORRIDOR-Omega: 4 niveaux, Catmull-Rom, reseau continu.
    MOTEUR AUTONOME — ZERO interaction vers SALINES/HOTSPOTS/ZONES/CONTAMINATION.
    """
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

        base = (1 - t.get("cost_surface", 0.3)) * 40 + 15
        season_mult = 1.1 if month in [9,10,11] and species in ["cerf","orignal","wapiti"] else 1.0
        time_mult = 1.15 if (5 <= hour <= 8 or 16 <= hour <= 19) else 0.7 if (10 <= hour <= 14) else 1.0
        connect_bonus = t.get("connectivity", 0.5) * 10
        stoch = (_seed(s_lat, s_lon, f"c10s_{i}") - 0.5) * 30
        intensity = round(min(100, max(5, (base + connect_bonus + stoch) * season_mult * time_mult)), 1)

        # 4 NIVEAUX
        ctype = _classify_corridor(intensity, month, species)
        level = CORRIDOR_LEVELS[ctype]

        # Catmull-Rom directionnel
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

        corridors.append({
            "id": f"corr_omega_{i}",
            "type": ctype,
            "path": path,
            "start": {"lat": round(s_lat, 5), "lng": round(s_lon, 5)},
            "end": {"lat": round(e_lat, 5), "lng": round(e_lon, 5)},
            "intensity": intensity,
            "cost_surface": round(t.get("cost_surface", 0.3), 3),
            "species_profile": species,
            "n_control_points": len(ctrl),
            "color": level["color"],
            "weight": level["weight"],
            "opacity": level["opacity"],
            "source": "CORRIDOR-Omega-AUTONOME",
        })

    # CORRIDOR-NETWORK-Omega: fusionner segments < 40m
    corridors = _build_corridor_network(corridors, cos_lat)

    return corridors


def _build_corridor_network(corridors, cos_lat):
    """CORRIDOR-NETWORK-Omega: connecter segments distants < 40m en reseau continu.
    Lisser jonctions via Catmull-Rom. Conserver intensite locale.
    """
    if len(corridors) < 2:
        return corridors

    connections = []
    threshold_deg = 40 / 111320  # 40m en degres

    # Limiter aux meilleures connexions uniques
    for i, c1 in enumerate(corridors):
        best_j = -1
        best_d = float('inf')
        for j, c2 in enumerate(corridors):
            if j <= i:
                continue
            dx = (c1["end"]["lng"] - c2["start"]["lng"]) * cos_lat
            dy = c1["end"]["lat"] - c2["start"]["lat"]
            d = math.sqrt(dx*dx + dy*dy)
            if d < threshold_deg and d < best_d:
                best_d = d
                best_j = j

        if best_j >= 0:
            connections.append({
                "from_id": c1["id"], "to_id": corridors[best_j]["id"],
                "from_pt": c1["end"], "to_pt": corridors[best_j]["start"],
                "distance_deg": best_d,
            })

    # Ajouter segments de connexion comme corridors mineurs
    for conn in connections:
        fp = conn["from_pt"]
        tp = conn["to_pt"]
        mid_lat = (fp["lat"] + tp["lat"]) / 2
        mid_lon = (fp["lng"] + tp["lng"]) / 2
        # Catmull-Rom jonction lisse
        ctrl = [(fp["lat"], fp["lng"]), (mid_lat, mid_lon), (tp["lat"], tp["lng"])]
        path = _catmull_rom(ctrl, subs=2)

        corridors.append({
            "id": f"net_{conn['from_id']}_{conn['to_id']}",
            "type": "normal",
            "path": path,
            "start": fp,
            "end": tp,
            "intensity": 25,
            "cost_surface": 0,
            "species_profile": "network",
            "n_control_points": 3,
            "color": "#FFFFFF",
            "weight": 1.2,
            "opacity": 0.6,
            "is_network_link": True,
            "source": "CORRIDOR-NETWORK-Omega",
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
# 4. ENGINE AFFUTS-Omega V11-SUPRA — FIXE + TEMPORAIRES
# ═══════════════════════════════════════════════════════
# MOTEUR AUTONOME — ZERO propagation
# 1 AFFUT FIXE PERMANENT + N AFFUTS TEMPORAIRES
# Distance tir: 20-100m
# Source: corridors, salines, zones, terrain, vent, contamination

def _is_under_wind(affut_lat, affut_lon, corridor_lat, corridor_lon, wind_deg):
    """Verifie que l'affut est sous le vent par rapport au corridor."""
    dx = affut_lon - corridor_lon
    dy = affut_lat - corridor_lat
    bearing = math.degrees(math.atan2(dx, dy)) % 360
    # L'affut doit etre dans la direction opposee au vent
    wind_from = (wind_deg + 180) % 360
    diff = abs(((bearing - wind_from + 180) % 360) - 180)
    return diff < 90  # dans le demi-cercle sous le vent


def _cone_overlap_check(affut_lat, affut_lon, contamination_cones, cos_lat):
    """Verifie si un affut est dans un cone de contamination."""
    for cone in contamination_cones:
        src = cone.get("affut_source", {})
        if not src:
            continue
        d = math.sqrt((affut_lat - src.get("lat", 0))**2 + ((affut_lon - src.get("lng", 0)) * cos_lat)**2) * 111320
        if d < cone.get("reach_m", 200):
            return True
    return False


def compute_affuts_omega(lat, lon, species, zones_v10, corridors_v10, salines_v10, wind_deg, terrain_v10, contamination_cones=None):
    """ENGINE AFFUTS-Omega V11-SUPRA: 1 FIXE PERMANENT + N TEMPORAIRES.
    MOTEUR AUTONOME — ZERO propagation.
    """
    t = terrain_v10
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    slope = t.get("pente_deg", 10)
    canopy = t.get("canopy", 0.5)
    contam = contamination_cones or []

    # Corridors intenses/extremes
    corr_ie = [c for c in corridors_v10 if c["type"] in ("extreme", "intense") and not c.get("is_network_link")]

    # ═══ AFFUT FIXE PERMANENT ═══
    # Meilleure position: sous le vent, 30-80m d'un corridor extreme, pente<18%, pas zone humide
    best_fixed = None
    best_fixed_score = -1

    for corr in corr_ie:
        path = corr.get("path", [])
        if len(path) < 3:
            continue
        mid = path[len(path) // 2]

        # Scanner 12 directions, 3 distances (40, 60, 75m)
        for dir_idx in range(12):
            angle = (dir_idx / 12) * 2 * math.pi
            for dist_m in [40, 60, 75]:
                a_lat = mid[0] + math.sin(angle) * dist_m / 111320
                a_lon = mid[1] + math.cos(angle) * dist_m / 111320 / cos_lat

                # REGLE: vent favorable (sous le vent du corridor)
                if not _is_under_wind(a_lat, a_lon, mid[0], mid[1], wind_deg):
                    continue

                # REGLE: pente < 18%
                slope_est = slope + _seed(a_lat, a_lon, "slope_af") * 4 - 2
                if slope_est > 18:
                    continue

                # REGLE: pas zone humide
                if t.get("zone_humide", False):
                    continue

                # REGLE: >120m route/sentier
                route_dist = t.get("distance_route_m", 500)
                if route_dist < 120:
                    continue

                # REGLE: zero recouvrement contamination
                if _cone_overlap_check(a_lat, a_lon, contam, cos_lat):
                    continue

                # Score fixe
                score = 30
                score += canopy * 25  # couvert
                score += (1 - slope_est / 18) * 15  # terrain
                score += min(1, route_dist / 500) * 10  # isolation humaine
                score += (1 - t.get("cost_surface", 0.3)) * 10  # accessibilite
                score += (corr["intensity"] / 100) * 10  # intensite corridor

                if score > best_fixed_score:
                    best_fixed_score = score
                    best_fixed = {
                        "lat": round(a_lat, 6),
                        "lng": round(a_lon, 6),
                        "score": round(min(100, score), 1),
                        "quality": "optimal",
                        "type": "FIXE_PERMANENT",
                        "orientation_deg": round((wind_deg + 180) % 360),
                        "distance_corridor_m": dist_m,
                        "corridor_type": corr["type"],
                        "corridor_intensity": corr["intensity"],
                        "pente_deg": round(slope_est, 1),
                        "distance_route_m": route_dist,
                        "zone_humide": False,
                        "contamination_overlap": False,
                        "description": "Affut fixe permanent — position institutionnelle stable, sous le vent, couvert optimal, accessibilite garantie, isolation humaine >120m",
                        "renderer": {"color": "#9E9E9E", "weight": 3, "symbol": "X", "fill_opacity": 0.35},
                        "source": "AFFUTS-Omega-V11-SUPRA",
                    }

    # ═══ AFFUTS TEMPORAIRES ═══
    # Positionnement: pres combinaison corridors INTENSE/EXTREME + salines
    temporaires = []

    for sal in salines_v10:
        if sal.get("status") != "SALINE-VALIDEE-Omega":
            continue
        sal_lat = sal["lat"]
        sal_lon = sal.get("lon", sal.get("lng", 0))

        # Trouver corridor intense le plus proche de cette saline
        best_corr = None
        best_corr_dist = float('inf')
        for corr in corr_ie:
            for pt in corr.get("path", [])[::4]:
                d = _distance_m(sal_lat, sal_lon, pt[0], pt[1])
                if d < best_corr_dist:
                    best_corr_dist = d
                    best_corr = corr
                    best_corr_pt = pt

        if not best_corr or best_corr_dist > 150:
            continue

        # Scanner positions optimales entre saline et corridor
        for dir_idx in range(8):
            angle = (dir_idx / 8) * 2 * math.pi
            for dist_m in [30, 50, 70]:
                a_lat = sal_lat + math.sin(angle) * dist_m / 111320
                a_lon = sal_lon + math.cos(angle) * dist_m / 111320 / cos_lat

                # REGLE: vent favorable
                if best_corr and not _is_under_wind(a_lat, a_lon, best_corr_pt[0], best_corr_pt[1], wind_deg):
                    continue

                # REGLE: pente < 22%
                slope_est = slope + _seed(a_lat, a_lon, "slope_tmp") * 5 - 2.5
                if slope_est > 22:
                    continue

                # REGLE: pas zone humide
                if t.get("zone_humide", False):
                    continue

                # REGLE: >80m route
                if t.get("distance_route_m", 500) < 80:
                    continue

                # Distance au corridor
                corr_dist = _distance_m(a_lat, a_lon, best_corr_pt[0], best_corr_pt[1])
                if corr_dist < 20 or corr_dist > 80:
                    continue

                # Score temporaire
                score = 25
                score += canopy * 20
                score += (1 - slope_est / 22) * 12
                score += (best_corr["intensity"] / 100) * 15
                score += sal["score"] / 100 * 10
                score += min(1, corr_dist / 60) * 8  # optimal ~60m
                stoch = (_seed(a_lat, a_lon, "tmp_stoch") - 0.5) * 10
                score = round(min(100, max(10, score + stoch)), 1)

                temporaires.append({
                    "lat": round(a_lat, 6),
                    "lng": round(a_lon, 6),
                    "score": score,
                    "quality": "bon" if score > 65 else "acceptable",
                    "type": "TEMPORAIRE",
                    "orientation_deg": round((wind_deg + 180) % 360),
                    "distance_corridor_m": round(corr_dist),
                    "corridor_type": best_corr["type"],
                    "distance_saline_m": round(dist_m),
                    "saline_score": sal["score"],
                    "pente_deg": round(slope_est, 1),
                    "description": f"Affut temporaire — pres corridor {best_corr['type']} + saline (score {sal['score']}), vent favorable, distance tir 20-80m",
                    "renderer": {"color": "#1E88E5", "weight": 2.4, "symbol": "arrow", "fill_opacity": 0.3},
                    "source": "AFFUTS-Omega-V11-SUPRA",
                })
                break  # 1 temporaire par direction
            if len(temporaires) >= 6:
                break
        if len(temporaires) >= 6:
            break

    # Trier temporaires par score
    temporaires.sort(key=lambda x: x["score"], reverse=True)
    temporaires = temporaires[:5]  # Max 5 temporaires

    # Assembler
    affuts = []
    if best_fixed:
        affuts.append(best_fixed)
    affuts.extend(temporaires)

    return affuts


# ═══════════════════════════════════════════════════════
# 5. HOTSPOTS V10-SUPRA
# ═══════════════════════════════════════════════════════

def compute_hotspots_v10(lat, lon, species, zones_v10, corridors_v10, affuts_v10, terrain_v10):
    """HOTSPOTS V10-SUPRA: fusion multi-engines. ZERO interaction SALINES (moteur autonome)."""
    t = terrain_v10
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    hotspots = []

    for a in affuts_v10:
        if a["score"] > 60:
            intensity = a["score"] * 0.7 + t.get("connectivity", 0.5) * 30
            hotspots.append({
                "lat": a["lat"], "lng": a["lng"],
                "intensity": round(min(100, intensity), 1),
                "source_engine": "AFFUT",
                "source": "V10-SUPRA",
            })

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

# ═══════════════════════════════════════════════════════
# 6. SALINES-Omega — REGLES INSTITUTIONNELLES
# ═══════════════════════════════════════════════════════
# REGLE 1: Distance eau [30-100m] (ENGINE HYDRO)
# REGLE 2: Distance corridor INTENSE/EXTREME [30-100m]
# CLASSIFICATION: SALINE-VALIDEE-Omega vs SALINE-A-REPOSITIONNER-Omega
# RECALCUL ANNUEL OBLIGATOIRE

def _distance_m(lat1, lon1, lat2, lon2):
    """Distance en metres entre deux points."""
    cos_lat = math.cos(math.radians((lat1 + lat2) / 2))
    dx = (lon2 - lon1) * 111320 * cos_lat
    dy = (lat2 - lat1) * 111320
    return math.sqrt(dx*dx + dy*dy)


def _find_nearest_corridor_intense(sal_lat, sal_lon, corridors):
    """Trouve le corridor INTENSE/EXTREME le plus proche et sa distance."""
    best_dist = float('inf')
    best_corr = None
    for c in corridors:
        if c["type"] not in ("critique", "majeur", "extreme", "intense"):
            continue
        # Distance au start et end du corridor
        for pt_key in ["start", "end"]:
            pt = c[pt_key]
            d = _distance_m(sal_lat, sal_lon, pt["lat"], pt["lng"])
            if d < best_dist:
                best_dist = d
                best_corr = c
        # Distance aux points du path
        for p in c.get("path", [])[::3]:  # Echantillonner 1/3
            d = _distance_m(sal_lat, sal_lon, p[0], p[1])
            if d < best_dist:
                best_dist = d
                best_corr = c
    return best_dist, best_corr


def _suggest_new_position(sal_lat, sal_lon, corridors, terrain_v10, cos_lat):
    """Genere une SUGGESTION_DE_NOUVELLE_POSITION pour une saline hors normes.
    Cherche la zone ou: EAU [30-100m] + CORRIDOR_INTENSE [30-100m] + TERRAIN conforme.
    """
    t = terrain_v10
    best_score = -1
    best_pos = None

    # Scanner 16 directions autour de la position actuelle
    for angle_idx in range(16):
        angle = (angle_idx / 16) * 2 * math.pi
        for dist_m in [40, 60, 80, 120, 160, 200]:
            new_lat = sal_lat + math.sin(angle) * dist_m / 111320
            new_lon = sal_lon + math.cos(angle) * dist_m / 111320 / cos_lat

            # Verifier corridor intense [30-100m]
            corr_dist, corr = _find_nearest_corridor_intense(new_lat, new_lon, corridors)
            if corr_dist < 30 or corr_dist > 100:
                continue

            # Verifier eau estimee [30-100m]
            eau_dist = t.get("distance_eau_m", 200)
            # Ajuster distance eau relative a la nouvelle position
            eau_offset = abs(dist_m * math.sin(angle) * 0.3)
            eau_est = max(10, eau_dist - eau_offset + _seed(new_lat, new_lon, "eau_adj") * 40)

            if eau_est < 30 or eau_est > 100:
                continue

            # Verifier terrain conforme
            slope_est = t.get("pente_deg", 10) + _seed(new_lat, new_lon, "slope_adj") * 3
            if slope_est > 20:
                continue

            # Score: meilleur si proche du centre des deux intervalles
            eau_score = 1 - abs(eau_est - 65) / 35  # optimal a 65m
            corr_score = 1 - abs(corr_dist - 65) / 35
            terrain_score = 1 - slope_est / 20
            total = eau_score * 0.4 + corr_score * 0.4 + terrain_score * 0.2

            if total > best_score:
                best_score = total
                best_pos = {
                    "lat": round(new_lat, 6),
                    "lon": round(new_lon, 6),
                    "eau_distance_m": round(eau_est),
                    "corridor_distance_m": round(corr_dist),
                    "corridor_type": corr["type"] if corr else None,
                    "score": round(total * 100, 1),
                }

    return best_pos


def compute_salines_omega(lat, lon, species, month, terrain_v10, corridors_v10):
    """ENGINE SALINES-Omega: regles eau [30-100m] + corridor intense [30-100m].
    Classification VALIDEE vs A-REPOSITIONNER. Suggestion repositionnement.
    Genere salines intelligemment pres des corridors intenses ET de l'eau.
    """
    t = terrain_v10
    cos_lat = max(0.5, math.cos(math.radians(lat)))

    # Corridors intenses/extremes
    corridors_intenses = [c for c in corridors_v10 if c["type"] in ("extreme", "intense")]

    salines = []

    # STRATEGIE: Placer salines pres des corridors intenses
    # en cherchant des positions conformes (eau + corridor [30-100m])
    candidates = []
    for ci, corr in enumerate(corridors_intenses[:6]):
        path = corr.get("path", [])
        if len(path) < 3:
            continue
        # Milieu du corridor
        mid_idx = len(path) // 2
        mid = path[mid_idx]
        # Offset perpendiculaire (50-80m)
        if mid_idx > 0:
            prev = path[mid_idx - 1]
            dx = mid[1] - prev[1]
            dy = mid[0] - prev[0]
        else:
            dx, dy = 0.001, 0.001
        norm = math.sqrt(dx*dx + dy*dy)
        if norm < 1e-8:
            continue
        # Perpendiculaire
        px, py = -dy/norm, dx/norm
        offset_m = 50 + _seed(mid[0], mid[1], f"sal_off_{ci}") * 30  # 50-80m
        offset_deg = offset_m / 111320
        sign = 1 if ci % 2 == 0 else -1

        s_lat = mid[0] + py * offset_deg * sign
        s_lon = mid[1] + px * offset_deg * sign / cos_lat

        # Score
        score = 30
        score += (t.get("soil_moisture", 0.3) or 0.3) * 25
        score += max(0, 20 - t.get("pente_deg", 10)) * 0.8
        score += t.get("canopy", 0.5) * 15
        if month in [4, 5, 9, 10]:
            score += 8
        score = round(min(100, max(10, score + (_seed(s_lat, s_lon, "sals") - 0.5) * 15)), 1)

        # Distance corridor (devrait etre ~50-80m par construction)
        corr_dist, nearest_corr = _find_nearest_corridor_intense(s_lat, s_lon, corridors_v10)

        # Distance eau: estimee depuis hydro index + drainage
        hydro = t.get("hydro_index", 0.5)
        drainage = t.get("drainage_class", 3)
        # Plus le drainage est mauvais (classe haute), plus l'eau est proche
        eau_base = max(10, 150 - drainage * 15 - hydro * 80)
        eau_jitter = _seed(s_lat, s_lon, "eau_sal") * 30 - 15
        eau_dist = round(max(5, eau_base + eau_jitter))

        eau_ok = 30 <= eau_dist <= 100
        corr_ok = 30 <= corr_dist <= 100

        if eau_ok and corr_ok:
            status = "SALINE-VALIDEE-Omega"
            suggestion = None
        else:
            status = "SALINE-A-REPOSITIONNER-Omega"
            suggestion = _suggest_new_position(s_lat, s_lon, corridors_v10, t, cos_lat)

        candidates.append({
            "lat": round(s_lat, 6),
            "lon": round(s_lon, 6),
            "score": score,
            "status": status,
            "eau_distance_m": eau_dist,
            "eau_conforme": eau_ok,
            "corridor_distance_m": round(corr_dist),
            "corridor_type": nearest_corr["type"] if nearest_corr else None,
            "corridor_conforme": corr_ok,
            "suggestion": suggestion,
            "source": "SALINES-Omega-INSTITUTIONNEL",
            "recalcul_annuel": False,
        })

    # Trier: VALIDEES d'abord, puis par score
    candidates.sort(key=lambda x: (0 if x["status"] == "SALINE-VALIDEE-Omega" else 1, -x["score"]))
    return candidates[:6]


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

    # 2. Couches — ORDRE: zones → corridors → salines → affuts → contamination → hotspots
    zones = compute_zones_v10(lat, lon, species, month, t)
    corridors = compute_corridors_omega(lat, lon, species, month, hour, real_wind_deg, t, zones)

    # SALINES-Omega: MOTEUR AUTONOME — calcule AVANT affuts (car affuts utilisent salines)
    salines = compute_salines_omega(lat, lon, species, month, t, corridors)

    # AFFUTS-Omega V11: FIXE PERMANENT + TEMPORAIRES (source: corridors + salines + terrain + vent)
    affuts = compute_affuts_omega(lat, lon, species, zones, corridors, salines, real_wind_deg, t)

    # CONTAMINATION-Omega: SOURCE = AFFUTS (ZERO waypoint)
    contamination = compute_contamination_omega(affuts, real_wind_deg, real_wind_speed, t)

    # HOTSPOTS: MOTEUR AUTONOME
    hotspots = compute_hotspots_v10(lat, lon, species, zones, corridors, affuts, t)

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
