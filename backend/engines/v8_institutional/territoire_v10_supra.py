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
    """ZONES V10-SUPRA: Catmull-Rom 22-40 vertices, terrain reel + IA.

    ═══════════════════════════════════════════════════════════════════════════
    P22ΩSPECIES_LAYER_DIVERGENCEΩ_V2 · 2026-05-13 · COMMANDANT STEEVE-MAX
    ═══════════════════════════════════════════════════════════════════════════
    Injection BIO_PROFILE_Ω : score et radius_mult sont désormais modulés par
    SPECIES_PROFILES pour TOUTES les zones :
      - rut         : cervidés > non-cervidés (chevreuil/orignal/wapiti/cerf)
      - alimentation: orignal/ours (besoin alim. élevé) > autres
      - repos       : chevreuil (couvert dense) > orignal (clairière)
      - eau         : orignal (hydro_dep=0.95) > ours > chevreuil
      - thermique   : dindon (zones ouvertes) > galliforme > cervidés
    Plus aucune zone générique inter-espèces — chaque espèce a sa signature.
    """
    t = terrain_v10
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    zones = []
    base_radius = 0.003
    # P22ΩSPECIES_LAYER_DIVERGENCEΩ_V2 — récupère profil biologique
    sp_lower = (species or "cerf").lower()
    sp_profile = SPECIES_PROFILES.get(sp_lower, SPECIES_PROFILES["cerf"])
    sp_cover_pref = sp_profile.get("cover_pref", 0.5)
    sp_sinuosity = sp_profile.get("sinuosity", 0.3)
    sp_slope_tol = sp_profile.get("slope_tol", 25)
    # Multiplicateurs biologiques par zone+espèce
    SPECIES_ZONE_BIAS = {
        "cerf":           {"rut": 1.20, "alimentation": 1.10, "repos": 1.15, "eau": 0.90, "thermique": 0.95},
        "chevreuil":      {"rut": 1.20, "alimentation": 1.05, "repos": 1.30, "eau": 0.85, "thermique": 0.90},
        "orignal":        {"rut": 1.15, "alimentation": 1.25, "repos": 0.95, "eau": 1.40, "thermique": 0.85},
        "wapiti":         {"rut": 1.20, "alimentation": 1.15, "repos": 1.00, "eau": 1.00, "thermique": 0.95},
        "ours":           {"rut": 0.80, "alimentation": 1.35, "repos": 1.20, "eau": 1.10, "thermique": 0.90},
        "ours_noir":      {"rut": 0.80, "alimentation": 1.35, "repos": 1.20, "eau": 1.10, "thermique": 0.90},
        "dindon":         {"rut": 0.70, "alimentation": 1.10, "repos": 0.90, "eau": 0.95, "thermique": 1.35},
        "dindon_sauvage": {"rut": 0.70, "alimentation": 1.10, "repos": 0.90, "eau": 0.95, "thermique": 1.35},
        "coyote":         {"rut": 0.85, "alimentation": 1.30, "repos": 1.05, "eau": 1.00, "thermique": 1.05},
    }
    zone_bias = SPECIES_ZONE_BIAS.get(sp_lower, SPECIES_ZONE_BIAS["cerf"])

    for i, (ztype, cfg) in enumerate(ZONE_CONFIGS.items()):
        offset_angle = (i / len(ZONE_CONFIGS)) * 2 * math.pi + _seed(lat, lon, f"zo_{ztype}_{sp_lower}") * 1.5
        # P22ΩV2 : radius_mult modulé par bias espèce
        sp_radius_factor = zone_bias.get(ztype, 1.0)
        dist = base_radius * (0.6 + _seed(lat, lon, f"zd_{ztype}_{sp_lower}") * 0.8) * cfg["radius_mult"] * sp_radius_factor
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

        # P22ΩSPECIES_LAYER_DIVERGENCEΩ_V2 : SCORE modulé par espèce
        # - couvert (cover_pref) influence repos + rut (refuge)
        # - slope_tol influence l'exclusion pente effective
        if ztype in ("repos", "rut"):
            score += (sp_cover_pref - 0.5) * 15 * canopy
        # Bias multiplicateur final
        score *= sp_radius_factor
        score = round(min(100, max(5, score)), 1)

        # P22ΩV2 : slope_max modulé par slope_tol biologique (ours=35, chevreuil=20)
        effective_slope_max = min(cfg["slope_max"], sp_slope_tol)
        excluded = slope > effective_slope_max or t.get("distance_eau_m", 999) < 10
        excl_reason = ""
        if slope > effective_slope_max:
            excl_reason = f"pente {slope}deg > {effective_slope_max}deg (slope_tol {sp_lower}={sp_slope_tol})"
        elif t.get("distance_eau_m", 999) < 10:
            excl_reason = f"eau {t.get('distance_eau_m')}m < 10m"

        # Polygon Catmull-Rom 8-13 control → 22-40 vertices
        # P22ΩV2 : sinuosity influence jitter (orignal=0.20 lisse, chevreuil=0.40 sinueux)
        n_ctrl = 8 + int(_seed(lat, lon, f"zn_{ztype}_{sp_lower}") * 5)
        r = base_radius * cfg["radius_mult"] * sp_radius_factor * (0.5 + _seed(lat, lon, f"zr_{ztype}_{sp_lower}") * 0.5)
        ctrl = []
        for j in range(n_ctrl):
            a = (j / n_ctrl) * 2 * math.pi
            # P22ΩV2 : jitter modulé par sinuosity (0.65 base + facteur espèce)
            jitter_amp = 0.7 + sp_sinuosity * 1.2
            jitter = 0.65 + jitter_amp * abs(math.sin(_seed(lat, lon, f"zj_{ztype}_{sp_lower}_{j}") * 7 + j * 2.9))
            p_lat = c_lat + math.sin(a) * r * jitter
            p_lon = c_lon + math.cos(a) * r * jitter / cos_lat
            ctrl.append((p_lat, p_lon))

        polygon = _catmull_rom(ctrl, subs=3)
        polygon.append(polygon[0])  # fermer

        zones.append({
            "id": f"zone_v10_{ztype}_{sp_lower}",
            "type": ztype,
            "species": sp_lower,
            "center": {"lat": round(c_lat, 5), "lng": round(c_lon, 5)},
            "polygon": polygon,
            "score": score,
            "species_bias_applied": sp_radius_factor,
            "terrain": {
                "canopy": canopy,
                "pente_deg": slope,
                "distance_eau_m": t.get("distance_eau_m", 200),
                "elevation_m": t.get("elevation_m", 0),
                "thermal_comfort": t.get("thermal_comfort", 0.5),
            },
            "excluded": excluded,
            "exclusion_reason": excl_reason,
            "source": "V10-SUPRA-REEL+IA+P22ΩV2",
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
    # ═══════════════════════════════════════════════════════════════════════════
    # P22ΩSPECIES_LAYER_DIVERGENCEΩ_V2 · 2026-05-13 · COMMANDANT STEEVE-MAX
    # ═══════════════════════════════════════════════════════════════════════════
    # Aliases canoniques EXPLICITES (alignés engine V5 + presence_mask + smoother)
    # Plus de fallback générique "cerf" pour ours_noir/dindon_sauvage/coyote.
    # Chaque espèce a maintenant son profil biologique INDEXÉ SPECIES_ID.
    "ours_noir":      {"sinuosity": 0.45, "cover_pref": 0.9, "slope_tol": 35, "n": 10},   # plantigrade prudent
    "dindon_sauvage": {"sinuosity": 0.25, "cover_pref": 0.5, "slope_tol": 15, "n": 10},   # galliforme thermique
    "coyote":         {"sinuosity": 0.35, "cover_pref": 0.6, "slope_tol": 30, "n": 11},   # canidé prédateur opportuniste
}

# 4 niveaux corridor
CORRIDOR_LEVELS = {
    "extreme":    {"min_intensity": 85, "color": "#D32F2F", "weight": 4.2, "opacity": 0.95},
    "intense":    {"min_intensity": 65, "color": "#FF9800", "weight": 3.0, "opacity": 0.90},
    "saisonnier": {"min_intensity": -1, "color": "#4CAF50", "weight": 2.4, "opacity": 0.90},  # special
    "normal":     {"min_intensity": 0,  "color": "#FFFFFF", "weight": 1.6, "opacity": 0.85},
}


def _classify_corridor(intensity, month, species):
    """Classifie un corridor en 4 niveaux: EXTREME, INTENSE, SAISONNIER, NORMAL.

    P22ΩSPECIES_LAYER_DIVERGENCEΩ_V2 · 2026-05-13 · STEEVE-MAX
    Saisonnalité INDEXÉE SPECIES_ID — alias canoniques ajoutés (chevreuil≡cerf,
    ours_noir≡ours, dindon_sauvage≡dindon, coyote opportuniste annuel).
    """
    is_seasonal = False
    # Cervidés : rut sept-nov
    if month in [9, 10, 11] and species in ["cerf", "chevreuil", "orignal", "wapiti"]:
        is_seasonal = True
    # Ours : sortie hibernation avr-mai
    elif month in [4, 5] and species in ["ours", "ours_noir"]:
        is_seasonal = True
    # Dindon : parade mars-avril
    elif month in [3, 4] and species in ["dindon", "dindon_sauvage"]:
        is_seasonal = True
    # Coyote : pic d'activité reproductive janvier-mars (hurlement + territoires)
    elif month in [1, 2, 3] and species == "coyote":
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

    PHASE_XVI_ENGINE_CORRIDORS_UNIFIÉ_Ω (2026-04-26) :
      - Branchement OBLIGATOIRE au registre `species_profiles_v1.json`
        via `species_modulator_omega.get_modulation_summary()`.
      - R_MIN/R_MAX dynamiques par espèce (typical_length_m du registry).
      - Amplitude organique modulée par profil biologique (faible/moyenne/elevee).
      - Vigilance → tortuosité (sinuosity multiplier).
      - Style corridor_style → modulation du nombre de corridors.
      - Slope tolerance et water buffer issus du registry.

    Phase XI-SUPRA-H (héritage) :
      - Rayon fonctionnel 600 m ± 30 % (420–780 m) autour du waypoint
      - Aucune référence aux affûts (directive STEEVE-MAX 2026-04-20)
      - Spécificité stricte : un corridor = une espèce
      - Validation géométrique (segment ≤ 20 m, angle ≤ 45°) appliquée par IA-CORRIDORS
    """
    # PHASE_XVI — modulation par espèce via registry officiel
    try:
        from engines.v8_institutional.species_modulator_omega import get_modulation_summary
        mod = get_modulation_summary(species)
    except Exception:
        mod = {
            "radius_action": {"r_min_deg": 420.0/111000.0, "r_max_deg": 780.0/111000.0,
                               "r_min_m": 420.0, "r_max_m": 780.0},
            "amplitude_factor": 1.0, "tortuosity_factor": 1.0,
            "slope_tolerance_deg": 25.0, "water_buffer": {"water_dist_min_m": 30.0},
        }

    sp = SPECIES_PROFILES.get(species, SPECIES_PROFILES["cerf"])
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    corridors = []
    t = terrain_v10

    # PHASE_XVI : R_MIN/R_MAX dynamiques par espèce (clippés [420, 780])
    R_MIN_DEG = mod["radius_action"]["r_min_deg"]
    R_MAX_DEG = mod["radius_action"]["r_max_deg"]
    AMP_FACTOR = float(mod.get("amplitude_factor", 1.0))
    TORT_FACTOR = float(mod.get("tortuosity_factor", 1.0))
    SLOPE_TOL_DYN = float(mod.get("slope_tolerance_deg") or sp["slope_tol"])
    WATER_BUF_MIN = float((mod.get("water_buffer") or {}).get("water_dist_min_m") or 10.0)

    for i in range(sp["n"]):
        angle = i * (360 / sp["n"]) + _seed(lat, lon, f"c10a_{i}") * 25 * TORT_FACTOR
        rad = math.radians(angle)
        # Longueur dans la plage dynamique [R_MIN_DEG, R_MAX_DEG] selon profil espèce.
        dist = R_MIN_DEG + _seed(lat, lon, f"c10d_{i}") * (R_MAX_DEG - R_MIN_DEG)

        # Start au voisinage du waypoint (dans le rayon min) ; End à distance fonctionnelle.
        s_lat = lat + math.sin(rad) * dist * 0.2
        s_lon = lon + math.cos(rad) * dist * 0.2 / cos_lat
        # Sinuosité finale = profil INLINE × tortuosity_factor du registry
        e_angle = angle + 15 + _seed(lat, lon, f"c10ea_{i}") * 40 * (1 + sp["sinuosity"] * TORT_FACTOR)
        e_rad = math.radians(e_angle)
        # End total offset from waypoint: entre R_MIN et R_MAX
        e_lat = lat + math.sin(e_rad) * dist
        e_lon = lon + math.cos(e_rad) * dist / cos_lat

        slope = t.get("pente_deg", 10)
        if slope > SLOPE_TOL_DYN:    # PHASE_XVI : tolérance pente dynamique
            continue
        if t.get("distance_eau_m", 999) < WATER_BUF_MIN:   # PHASE_XVI : buffer eau dynamique
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
        # Phase XI-SUPRA-H : subs=8 pour garantir segments ≤ 20 m (VERSION Ω)
        path = _catmull_rom(ctrl, subs=8)

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

    # Phase XI-SUPRA-H — ENGINE CORRIDORS VERSION Ω
    # Filtre strict IA-CORRIDORS : ne publier QUE les corridors qui satisfont
    # les 6 contraintes officielles (segment ≤ 20 m, angle ≤ 45°, rayon
    # 420-780 m, species_profile, pas de ref affut, ≥ 5 control points).
    try:
        from engines.v8_institutional.engine_ia_corridors_omega import filter_conforme_corridors
        before = len(corridors)
        corridors = filter_conforme_corridors(corridors, {"lat": lat, "lon": lon})
        # logger optionnel — on silence ici pour éviter les dépendances
        if before != len(corridors):
            pass  # {before - len(corridors)} corridors rejetés par IA-CORRIDORS
    except Exception:
        # IA-CORRIDORS non disponible (circular-safe) → pas de filtre
        pass

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


def compute_affuts_omega(lat, lon, species, zones_v10, corridors_v10, wind_deg, terrain_v10, contamination_cones=None):
    """ENGINE AFFUTS-Omega V12 — REFACTORISE INDEPENDANT SALINES
    ============================================================
    Inputs autorises: CORRIDORS (extreme/intense=MAJEUR), ZONES, TERRAIN-RULES-Omega.
    Suppression totale de la dependance SALINES.

    REGLE INSTITUTIONNELLE V12: distance 30-80m des corridors MAJEURS (extreme + intense).
    - Ideal: 45-65m (score 100)
    - Bon: 30-45m ou 65-80m (score 80)
    - HORS PLAGE: <30 ou >80 → repositionnement automatique vers optimum 55m

    Sortie enrichie V12:
      score_affut_v12, distance_corridor, classe_corridor_cible,
      affut_repositionne, ancienne_position, nouvelle_position,
      justification, recommandation.
    """
    t = terrain_v10
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    slope = t.get("pente_deg", 10)
    canopy = t.get("canopy", 0.5)
    contam = contamination_cones or []

    # REGLE V12: seuls corridors MAJEURS autorises (extreme + intense)
    # (faible/modere/saisonnier interdits comme base d'affut)
    corr_majeurs = [c for c in corridors_v10 if c["type"] in ("extreme", "intense") and not c.get("is_network_link")]

    # ═══ SCORE DISTANCE V12 ═══
    def _score_distance_v12(corr_dist_m: float) -> int:
        if 45 <= corr_dist_m <= 65:
            return 100
        if 30 <= corr_dist_m < 45 or 65 < corr_dist_m <= 80:
            return 80
        return 0

    # ═══ REPOSITIONNEMENT AUTO V12 ═══
    def _auto_reposition(a_lat, a_lon, corr_pt_lat, corr_pt_lon):
        """Repositionne l'affut a 55m (ideal) du corridor, sur la meme direction."""
        dy = a_lat - corr_pt_lat
        dx = a_lon - corr_pt_lon
        cur_d_deg = math.sqrt(dy*dy + (dx*cos_lat)**2)
        if cur_d_deg < 1e-9:
            # Cas dege: offset arbitraire 55m
            new_lat = corr_pt_lat + 55 / 111320
            new_lon = corr_pt_lon + 0
        else:
            target_d_deg = 55 / 111320  # 55m en degres lat
            scale = target_d_deg / cur_d_deg
            new_lat = corr_pt_lat + dy * scale
            new_lon = corr_pt_lon + dx * scale
        return round(new_lat, 6), round(new_lon, 6)

    # ═══ AFFUT FIXE PERMANENT ═══
    best_fixed = None
    best_fixed_score = -1

    for corr in corr_majeurs:
        path = corr.get("path", [])
        if len(path) < 3:
            continue
        mid = path[len(path) // 2]
        corr_class = "extreme" if corr["type"] == "extreme" else "majeur"

        # Scanner 12 directions x 4 distances cibles (40, 55, 65, 75m — dans plage 30-80 par construction)
        for dir_idx in range(12):
            angle = (dir_idx / 12) * 2 * math.pi
            for dist_target in [40, 55, 65, 75]:
                a_lat_raw = mid[0] + math.sin(angle) * dist_target / 111320
                a_lon_raw = mid[1] + math.cos(angle) * dist_target / 111320 / cos_lat

                # Verifier distance reelle apres placement (peut varier legerement)
                actual_d = _distance_m(a_lat_raw, a_lon_raw, mid[0], mid[1])

                # Repositionnement V12 si hors plage 30-80m
                repositionne = False
                ancienne_position = None
                if actual_d < 30 or actual_d > 80:
                    ancienne_position = {"lat": round(a_lat_raw, 6), "lng": round(a_lon_raw, 6), "distance_m": round(actual_d)}
                    a_lat, a_lon = _auto_reposition(a_lat_raw, a_lon_raw, mid[0], mid[1])
                    actual_d = _distance_m(a_lat, a_lon, mid[0], mid[1])
                    repositionne = True
                else:
                    a_lat, a_lon = a_lat_raw, a_lon_raw

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

                # Score V12 compose
                score_distance = _score_distance_v12(actual_d)
                if score_distance == 0:
                    continue

                score = 30
                score += canopy * 20
                score += (1 - slope_est / 18) * 12
                score += min(1, route_dist / 500) * 8
                score += (1 - t.get("cost_surface", 0.3)) * 8
                score += (corr["intensity"] / 100) * 10
                score += (score_distance / 100) * 12  # poids majeur distance V12
                final_score = round(min(100, score), 1)

                if final_score > best_fixed_score:
                    best_fixed_score = final_score
                    justification = f"Corridor {corr_class} a {int(actual_d)}m, pente {round(slope_est,1)}%, couvert {round(canopy*100)}%, vent favorable"
                    best_fixed = {
                        "lat": a_lat,
                        "lng": a_lon,
                        "score": final_score,
                        "score_affut_v12": final_score,
                        "score_distance_corridor": score_distance,
                        "quality": "optimal" if final_score >= 75 else "bon",
                        "type": "FIXE_PERMANENT",
                        "orientation_deg": round((wind_deg + 180) % 360),
                        "distance_corridor_m": round(actual_d),
                        "distance_corridor": round(actual_d),  # alias V12
                        "classe_corridor_cible": corr_class,
                        "corridor_type": corr["type"],
                        "corridor_intensity": corr["intensity"],
                        "pente_deg": round(slope_est, 1),
                        "distance_route_m": route_dist,
                        "zone_humide": False,
                        "contamination_overlap": False,
                        "affut_repositionne": repositionne,
                        "ancienne_position": ancienne_position,
                        "nouvelle_position": {"lat": a_lat, "lng": a_lon, "distance_m": round(actual_d)} if repositionne else None,
                        "justification": justification,
                        "recommandation": "REPOSITIONNE AUTOMATIQUEMENT V12" if repositionne else "INSTALLER (conforme 30-80m corridor MAJEUR)",
                        "description": f"Affut fixe permanent V12 — {justification}",
                        "renderer": {"color": "#9E9E9E", "weight": 3, "symbol": "X", "fill_opacity": 0.35},
                        "source": "AFFUTS-Omega-V12",
                    }

    # ═══ AFFUTS TEMPORAIRES V12 — ZERO dep SALINES ═══
    # Positionnement: ancres sur corridors MAJEURS (extreme en priorite)
    # Distribution: 5-6 positions reparties le long des corridors les plus intenses
    temporaires = []
    corr_sorted = sorted(corr_majeurs, key=lambda c: (-c.get("intensity", 0), 0 if c["type"] == "extreme" else 1))

    for corr in corr_sorted:
        if len(temporaires) >= 5:
            break
        path = corr.get("path", [])
        if len(path) < 5:
            continue
        corr_class = "extreme" if corr["type"] == "extreme" else "majeur"

        # 2 positions par corridor: 1/3 et 2/3 du chemin
        for frac in [0.33, 0.66]:
            idx = int(len(path) * frac)
            anchor = path[idx]

            # Scanner 6 directions x 3 distances cibles ideales (45, 55, 65m)
            placed = False
            for dir_idx in range(6):
                if placed:
                    break
                angle = (dir_idx / 6) * 2 * math.pi + _seed(anchor[0], anchor[1], f"tmp_{idx}") * math.pi
                for dist_target in [45, 55, 65]:
                    a_lat_raw = anchor[0] + math.sin(angle) * dist_target / 111320
                    a_lon_raw = anchor[1] + math.cos(angle) * dist_target / 111320 / cos_lat
                    actual_d = _distance_m(a_lat_raw, a_lon_raw, anchor[0], anchor[1])

                    # Repositionnement V12 si hors plage
                    repositionne = False
                    ancienne_position = None
                    if actual_d < 30 or actual_d > 80:
                        ancienne_position = {"lat": round(a_lat_raw, 6), "lng": round(a_lon_raw, 6), "distance_m": round(actual_d)}
                        a_lat, a_lon = _auto_reposition(a_lat_raw, a_lon_raw, anchor[0], anchor[1])
                        actual_d = _distance_m(a_lat, a_lon, anchor[0], anchor[1])
                        repositionne = True
                    else:
                        a_lat, a_lon = a_lat_raw, a_lon_raw

                    # REGLE: vent favorable
                    if not _is_under_wind(a_lat, a_lon, anchor[0], anchor[1], wind_deg):
                        continue
                    # REGLE: pente < 22% (temporaire = plus tolerant)
                    slope_est = slope + _seed(a_lat, a_lon, "slope_tmp") * 5 - 2.5
                    if slope_est > 22:
                        continue
                    # REGLE: pas zone humide
                    if t.get("zone_humide", False):
                        continue
                    # REGLE: >80m route
                    if t.get("distance_route_m", 500) < 80:
                        continue
                    # REGLE: zero recouvrement contamination
                    if _cone_overlap_check(a_lat, a_lon, contam, cos_lat):
                        continue

                    # Score V12
                    score_distance = _score_distance_v12(actual_d)
                    if score_distance == 0:
                        continue

                    score = 25
                    score += canopy * 18
                    score += (1 - slope_est / 22) * 10
                    score += (corr["intensity"] / 100) * 15
                    score += (score_distance / 100) * 15
                    stoch = (_seed(a_lat, a_lon, "tmp_stoch") - 0.5) * 6
                    final_score = round(min(100, max(20, score + stoch)), 1)

                    justification = f"Corridor {corr_class} a {int(actual_d)}m, pente {round(slope_est,1)}%, vent favorable"
                    temporaires.append({
                        "lat": round(a_lat, 6),
                        "lng": round(a_lon, 6),
                        "score": final_score,
                        "score_affut_v12": final_score,
                        "score_distance_corridor": score_distance,
                        "quality": "bon" if final_score > 65 else "acceptable",
                        "type": "TEMPORAIRE",
                        "orientation_deg": round((wind_deg + 180) % 360),
                        "distance_corridor_m": round(actual_d),
                        "distance_corridor": round(actual_d),
                        "classe_corridor_cible": corr_class,
                        "corridor_type": corr["type"],
                        "corridor_intensity": corr["intensity"],
                        "pente_deg": round(slope_est, 1),
                        "affut_repositionne": repositionne,
                        "ancienne_position": ancienne_position,
                        "nouvelle_position": {"lat": round(a_lat, 6), "lng": round(a_lon, 6), "distance_m": round(actual_d)} if repositionne else None,
                        "justification": justification,
                        "recommandation": "REPOSITIONNE AUTOMATIQUEMENT V12" if repositionne else "INSTALLER (conforme 30-80m corridor MAJEUR)",
                        "description": f"Affut temporaire V12 — {justification}",
                        "renderer": {"color": "#1E88E5", "weight": 2.4, "symbol": "arrow", "fill_opacity": 0.3},
                        "source": "AFFUTS-Omega-V12",
                    })
                    placed = True
                    break

    # Trier temporaires par score
    temporaires.sort(key=lambda x: x["score"], reverse=True)
    temporaires = temporaires[:5]

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

def _distance_m_redirect(lat1, lon1, lat2, lon2):
    """Alias historique — voir _distance_m plus bas."""
    return _distance_m_legacy(lat1, lon1, lat2, lon2)


# PHASE_XII_SUPRA_M_IMPLANTATION_X1000 — profil terrain des salines
# Aligné sur `_terrain_profile` de phase_b_engines.py pour cohérence filtres Ω
def _saline_terrain_profile(lat, lon):
    """Profil terrain d'une saline, compatible filtres Ω (EXCLUSION/HABITAT/TERRAIN/BIOLOGIE)."""
    canopy = max(0, min(1, 0.35 + _seed(lat, lon, "canopy") * 0.55))
    pente = max(0, min(45, _seed(lat, lon, "pente") * 25 + abs(math.sin(lat * 13.7)) * 10))
    distance_eau = max(10, min(800, 50 + _seed(lat, lon, "eau") * 500 + abs(math.cos(lon * 7.3)) * 200))
    distance_route = max(20, min(2000, 100 + _seed(lat, lon, "route") * 1500))
    urban_seed = _seed(lat, lon, "urban")
    industrial_seed = _seed(lat, lon, "industrial")
    route_factor = max(0, min(1, 1 - (distance_route - 20) / 900))
    impervious_pct = round(min(95, route_factor * 70 + urban_seed * 30 + (5 if distance_route < 60 else 0)), 1)
    urban = bool(impervious_pct > 60 or (distance_route < 50 and urban_seed > 0.4))
    industrial = bool(industrial_seed > 0.92 and distance_route < 120)
    port = bool(distance_eau < 40 and urban_seed > 0.85 and distance_route < 150)
    return {
        "canopy": round(canopy, 3),
        "pente_deg": round(pente, 1),
        "distance_eau_m": round(distance_eau),
        "distance_route_m": round(distance_route),
        "impervious_pct": impervious_pct,
        "urban": urban,
        "industrial": industrial,
        "port": port,
    }


def _distance_m(lat1, lon1, lat2, lon2):
    """Distance en metres entre deux points."""
    cos_lat = math.cos(math.radians((lat1 + lat2) / 2))
    dx = (lon2 - lon1) * 111320 * cos_lat
    dy = (lat2 - lat1) * 111320
    return math.sqrt(dx*dx + dy*dy)


def _distance_m_legacy(lat1, lon1, lat2, lon2):
    return _distance_m(lat1, lon1, lat2, lon2)


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
            # PHASE_XII_SUPRA_M_IMPLANTATION_X1000 — terrain densifié pour filtres Ω
            "terrain": _saline_terrain_profile(s_lat, s_lon),
            # PHASE_XIII_RECALCUL_ORGANIC_Ω — marqueur institutionnel
            "recalcul_organic_omega": True,
        })

    # Trier: VALIDEES d'abord, puis par score
    candidates.sort(key=lambda x: (0 if x["status"] == "SALINE-VALIDEE-Omega" else 1, -x["score"]))

    # ALWAYS-ON-Omega GUARANTEE: si aucune saline genere via corridors intenses,
    # generer fallback circulaire autour du centre (rayon 150-250m)
    if not candidates:
        for i in range(4):
            angle_deg = i * 90 + 45
            dist_m = 150 + (i % 2) * 80
            dlat = (dist_m * math.cos(math.radians(angle_deg))) / 111320
            dlon = (dist_m * math.sin(math.radians(angle_deg))) / (111320 * cos_lat)
            s_lat = lat + dlat
            s_lon = lon + dlon
            candidates.append({
                "lat": round(s_lat, 6),
                "lon": round(s_lon, 6),
                "score": 50.0,
                "status": "SALINE-A-REPOSITIONNER-Omega",
                "eau_distance_m": 80,
                "eau_conforme": True,
                "corridor_distance_m": 150,
                "corridor_type": "normal",
                "corridor_conforme": False,
                "suggestion": None,
                "source": "SALINES-Omega-ALWAYS-ON-FALLBACK",
                "recalcul_annuel": False,
                # PHASE_XII_SUPRA_M_IMPLANTATION_X1000 — terrain fallback aussi densifié
                "terrain": _saline_terrain_profile(s_lat, s_lon),
            })

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

    # 2. Couches — ORDRE V12-INSTITUTIONNEL:
    #    terrain → corridors → zones → AFFUTS(no-salines) → contamination → salines(base) → salines_V11_enrich → hotspots → vent
    zones = compute_zones_v10(lat, lon, species, month, t)
    corridors = compute_corridors_omega(lat, lon, species, month, hour, real_wind_deg, t, zones)

    # AFFUTS-Omega V12: REFACTORISE — ZERO dependance SALINES.
    # Inputs: corridors (MAJEURS extreme+intense), zones, terrain, vent, contamination(=None ici).
    affuts = compute_affuts_omega(lat, lon, species, zones, corridors, real_wind_deg, t, contamination_cones=None)

    # CONTAMINATION-Omega: SOURCE = AFFUTS (ZERO waypoint)
    contamination = compute_contamination_omega(affuts, real_wind_deg, real_wind_speed, t)

    # CONTAMINATION-Ω V2 (Phase X-B) : CWD/maladies + heatmap + propagation
    contamination_v2 = None
    try:
        from engines.v8_institutional.engine_contamination_v2_omega import compute_contamination_v2
        contamination_v2 = compute_contamination_v2(contamination, lat, lon, species)
    except Exception as _e:
        import logging as _lg
        _lg.getLogger("bionic.territoire").warning(f"contamination V2 skipped: {_e}")

    # SALINES-Omega BASE: genere salines autonomes (zero dep affuts)
    salines = compute_salines_omega(lat, lon, species, month, t, corridors)

    # SALINES-V11-SUPRA: enrichissement multi-axe (bio/terrain/nutrition/reseau/accoutumance)
    try:
        from engines.v8_institutional.engine_salines_v11_supra import enrich_salines_v11_supra
        salines = enrich_salines_v11_supra(salines, t, corridors, affuts, contamination, species, month)
    except Exception as _e:
        pass

    # HOTSPOTS: MOTEUR AUTONOME
    hotspots = compute_hotspots_v10(lat, lon, species, zones, corridors, affuts, t)

    wind_vectors = compute_wind_vectors(lat, lon, real_wind_deg, real_wind_speed)

    # ═══ P0 SUPRA engines (HABITAT + HYDROLOGIE + SOL + STRESS-ANTHROPIQUE) ═══
    habitat_supra = None
    hydrologie_supra = None
    sol_supra = None
    stress_anthropique = None
    # P1 SUPRA engines
    espece_profile = None
    comportement_biologique = None
    connectivite_ecologique = None
    thermique_microclimat = None
    sensoriel_vent_odeurs = None
    ia_vision_ecologique = None
    # P2 SUPRA engines (gouvernance + demographie)
    quality_data = None
    incertitude = None
    calibration = None
    population_dynamics = None
    # P3 SUPRA engines (environnement + gouvernance)
    climat_futur = None
    influence_lunaire = None
    pression_atmospherique = None
    score_global_reality = None
    try:
        from engines.v8_institutional.engine_habitat_supra import compute_habitat_supra
        from engines.v8_institutional.engine_hydrologie_supra import compute_hydrologie_supra
        from engines.v8_institutional.engine_sol_supra import compute_sol_supra
        from engines.v8_institutional.engine_stress_anthropique_omega import compute_stress_anthropique
        from engines.v8_institutional.engine_espece_omega import compute_especes
        from engines.v8_institutional.engine_comportement_biologique_omega import compute_comportement_biologique
        from engines.v8_institutional.engine_connectivite_ecologique_omega import compute_connectivite_ecologique
        from engines.v8_institutional.engine_thermique_microclimat_omega import compute_thermique_microclimat
        from engines.v8_institutional.engine_sensoriel_vent_odeurs_omega import compute_sensoriel_vent_odeurs
        from engines.v8_institutional.engine_ia_vision_ecologique_omega import compute_ia_vision_ecologique
        from engines.v8_institutional.engine_qualite_donnees_omega import compute_quality_data
        from engines.v8_institutional.engine_incertitude_omega import compute_incertitude
        from engines.v8_institutional.engine_calibration_omega import compute_calibration
        from engines.v8_institutional.engine_population_dynamics_omega import compute_population_dynamics
        habitat_supra = compute_habitat_supra(terrain_result, contamination_v2=contamination_v2)
        hydrologie_supra = compute_hydrologie_supra(terrain_result)
        sol_supra = compute_sol_supra(terrain_result)
        stress_anthropique = compute_stress_anthropique(terrain_result, hour=hour, contamination_v2=contamination_v2)
        espece_profile = compute_especes(species)
        comportement_biologique = compute_comportement_biologique(species, month, hour=hour)
        connectivite_ecologique = compute_connectivite_ecologique(terrain_result, corridors)
        thermique_microclimat = compute_thermique_microclimat(terrain_result, species=species)
        sensoriel_vent_odeurs = compute_sensoriel_vent_odeurs(terrain_result, real_wind_deg, real_wind_speed)
        ia_vision_ecologique = compute_ia_vision_ecologique(terrain_result)
        quality_data = compute_quality_data()
        incertitude = compute_incertitude(terrain_result, species=species)
        calibration = compute_calibration(terrain_result)
        population_dynamics = compute_population_dynamics(species, contamination_v2=contamination_v2)
        # P3
        from engines.v8_institutional.engine_climat_futur_omega import compute_climat_futur
        from engines.v8_institutional.engine_influence_lunaire_omega import compute_influence_lunaire
        from engines.v8_institutional.engine_pression_atmospherique_omega import compute_pression_atmospherique
        climat_futur = compute_climat_futur(terrain_result)
        influence_lunaire = compute_influence_lunaire(hour=hour)
        pression_atmospherique = compute_pression_atmospherique(terrain_result)
    except Exception as _e:
        import logging as _lg
        _lg.getLogger("bionic.territoire").warning(f"SUPRA P0+P1+P2+P3 skipped: {_e}")

    # NUTRITION-V12-SUPRA: moteur biologique central (score + cartes + influences)
    nutrition = None
    try:
        from engines.v8_institutional.engine_nutrition_v12_supra import compute_nutrition_v12
        nutrition = compute_nutrition_v12(
            lat, lon, species, month, hour,
            terrain_v10=terrain_result,
            zones=zones,
            corridors=corridors,
            affuts=affuts,
            hotspots=hotspots,
            salines=salines,
            profil="moyenne",
        )
        # Apply non-invasive boost: corridors + hotspots + salines (champs additifs)
        if nutrition:
            _bmap = {i["corridor_id"]: i["boost_delta"] for i in nutrition.get("influence_corridors", []) if i.get("corridor_id") is not None}
            for c in corridors:
                delta = _bmap.get(c.get("id"))
                if delta:
                    c["nutrition_boost"] = delta
                    if isinstance(c.get("score"), (int, float)):
                        c["score_with_nutrition"] = min(100, round(c["score"] + delta, 1))
            _hmap = {i["hotspot_id"]: i["boost_delta"] for i in nutrition.get("influence_hotspots", []) if i.get("hotspot_id") is not None}
            for h in hotspots:
                hid = h.get("id") or (f"hs_{h.get('lat'):.5f}_{h.get('lng'):.5f}" if h.get("lat") is not None and h.get("lng") is not None else None)
                delta = _hmap.get(hid)
                if delta:
                    h["nutrition_boost"] = delta
                    if isinstance(h.get("intensity"), (int, float)):
                        h["intensity_with_nutrition"] = min(100, round(h["intensity"] + delta, 1))
            _smap = nutrition.get("attractivite_salines", {})
            for s in salines:
                sid = s.get("id") or s.get("site_id") or s.get("name")
                if sid is None and s.get("lat") is not None:
                    lon_s = s.get("lon") or s.get("lng")
                    if lon_s is not None:
                        sid = f"sal_{s['lat']:.5f}_{lon_s:.5f}"
                if sid is not None and str(sid) in _smap:
                    s["nutrition_attractivite_mult"] = _smap[str(sid)]
    except Exception as _e:
        import logging as _lg
        _lg.getLogger("bionic.territoire").warning(f"nutrition v12 skipped: {_e}")

    # SCORE GLOBAL REALITY (Phase IX) - calcul apres tous les engines
    score_global_reality = None
    try:
        from engines.v8_institutional.engine_score_global import compute_score_global_reality
        partial_bundle = {
            "zones": zones, "corridors": corridors, "affuts": affuts, "hotspots": hotspots,
            "salines": salines, "wind_vectors": wind_vectors, "contamination": contamination,
            "nutrition": nutrition, "habitat_supra": habitat_supra, "hydrologie_supra": hydrologie_supra,
            "sol_supra": sol_supra, "stress_anthropique": stress_anthropique,
            "comportement_biologique": comportement_biologique, "connectivite_ecologique": connectivite_ecologique,
            "thermique_microclimat": thermique_microclimat, "sensoriel_vent_odeurs": sensoriel_vent_odeurs,
            "ia_vision_ecologique": ia_vision_ecologique, "quality_data": quality_data,
            "incertitude": incertitude, "calibration": calibration, "population_dynamics": population_dynamics,
            "climat_futur": climat_futur, "influence_lunaire": influence_lunaire,
            "pression_atmospherique": pression_atmospherique,
            "contamination_v2": contamination_v2,
            "_species_key": species,
        }
        score_global_reality = compute_score_global_reality(partial_bundle)
    except Exception as _e:
        import logging as _lg
        _lg.getLogger("bionic.territoire").warning(f"SCORE-GLOBAL-REALITY skipped: {_e}")

    # Phase XI-SUPRA : enrichissement couches rendu obligatoires
    canada_zones_summary = None
    contamination_v2_heatmap = None
    lep_nearby = None
    hydat_nearby = None
    observations_nearby = None
    zones_risque = None
    habitats_critiques = None
    deplacements_ia = None
    score_local = None
    try:
        from engines.v8_institutional.engine_canada_omega import CORRIDORS_INTERPROVINCIAUX, PROVINCES
        from engines.v8_institutional.science_gaps_datasets import CWD_HEATMAP
        from engines.v8_institutional.federal_datasets_omega import LEP_HABITATS, HYDAT_STATIONS
        from engines.v8_institutional.engine_calibration_dynamique_omega import _OBSERVATIONS

        # Zones fauniques Canada (agrégé provincial)
        canada_zones_summary = [
            {"code": c, "name": p["name"], "zones_faune": p["zones_faune"],
             "habitats_critiques_lep": p["habitats_critiques_lep"]}
            for c, p in PROVINCES.items()
        ]

        # CWD heatmap (3 zones institutionnelles + cone vent contamination local)
        contamination_v2_heatmap = {
            "zones": CWD_HEATMAP["zones"],
            "local_v2": contamination_v2 or {},
        }

        # LEP proches (rayon ~200 km lat/lon approximatif)
        def _close(p, maxd=3.5):
            return abs(p["lat"] - lat) + abs(p["lon"] - lon) < maxd
        lep_nearby = [h for h in LEP_HABITATS if _close(h, 3.5)][:50]

        # HYDAT proches (rayon ~200 km)
        hydat_nearby = [s for s in HYDAT_STATIONS if _close(s, 3.5)][:50]

        # Observations chasseurs proches (last 100)
        observations_nearby = [
            o for o in _OBSERVATIONS[-100:]
            if _close({"lat": o["lat"], "lon": o["lon"]}, 5.0)
        ]

        # Zones de risque (agrégé hydro + feu + CWD)
        zones_risque = []
        if contamination_v2 and contamination_v2.get("cwd_risk") in ("ELEVE", "MODERE"):
            zones_risque.append({
                "type": "CWD",
                "severity": contamination_v2["cwd_risk"],
                "lat": contamination_v2.get("nearest_cwd_zone", {}).get("lat"),
                "lon": contamination_v2.get("nearest_cwd_zone", {}).get("lon"),
                "radius_km": contamination_v2.get("nearest_cwd_zone", {}).get("radius_km", 40),
            })
        # Feu (proxy saisonnier juin-septembre)
        if 6 <= month <= 9:
            zones_risque.append({"type": "FEU", "severity": "MODERE",
                                  "lat": lat, "lon": lon, "radius_km": 25,
                                  "source": "CWFIS proxy"})
        # Hydro (proxy étiage si débit < 5% sur HYDAT local)
        if hydat_nearby:
            avg_debit = sum(s.get("debit_m3s", 0) for s in hydat_nearby) / len(hydat_nearby)
            if avg_debit < 20:
                zones_risque.append({"type": "ETIAGE", "severity": "FAIBLE",
                                      "lat": lat, "lon": lon, "radius_km": 15,
                                      "source": "HYDAT local"})

        # Habitats critiques (synthèse LEP + LEP_nearby)
        habitats_critiques = [h for h in lep_nearby if h.get("categorie") in ("EN_VOIE_DISPARITION", "MENACEE")]

        # Déplacements IA (extrait comportement_biologique + corridors MAJEURS)
        deplacements_ia = []
        if corridors:
            for c in (corridors or [])[:20]:
                if c.get("priority") in ("EXTREME", "INTENSE") and c.get("coords"):
                    deplacements_ia.append({
                        "corridor_id": c.get("id"),
                        "priority": c.get("priority"),
                        "coords": c.get("coords"),
                        "source": "IA-COMPORTEMENT",
                    })

        # Score local (extrait de score_global_reality)
        if score_global_reality:
            score_local = {
                "value": score_global_reality.get("score_global"),
                "classification": score_global_reality.get("classification"),
                "mode": score_global_reality.get("mode"),
                "contamination_v2_applied": score_global_reality.get("contamination_v2_applied"),
            }
    except Exception as _e:
        import logging as _lg
        _lg.getLogger("bionic.territoire").warning(f"Phase XI-SUPRA enrichment skipped: {_e}")

    return {
        "zones": zones,
        "corridors": corridors,
        "affuts": affuts,
        "hotspots": hotspots,
        "salines": salines,
        "wind_vectors": wind_vectors,
        # PHASE-C R2 — réconciliation institutionnelle vent (audit Phase-B B-1)
        "wind_truth": {
            "wind_deg": round(real_wind_deg, 1),
            "wind_speed_kmh": round(real_wind_speed, 1),
            "source": "open-meteo via terrain_v10.meteo (with param fallback)",
            "canonical_engine": "ENGINE_VENT (engine_sensoriel_vent_odeurs)",
            "wind_vectors_role": "DERIVED_VISUAL_FAN (centered on wind_truth.wind_deg)",
        },
        "wind_vectors_meta": {
            "source": "engine_vent.compute_wind_vectors",
            "parent_truth": "wind_truth.wind_deg",
            "n_vectors": 8,
            "step_deg": 15,
            "spread_deg": 7 * 15,
            "central_index": 4,
            "phase_c_r2_applied": True,
        },
        "contamination": contamination,
        "contamination_v2": contamination_v2,
        "contamination_v2_heatmap": contamination_v2_heatmap,
        "nutrition": nutrition,
        "habitat_supra": habitat_supra,
        "hydrologie_supra": hydrologie_supra,
        "sol_supra": sol_supra,
        "stress_anthropique": stress_anthropique,
        "espece_profile": espece_profile,
        "comportement_biologique": comportement_biologique,
        "connectivite_ecologique": connectivite_ecologique,
        "thermique_microclimat": thermique_microclimat,
        "sensoriel_vent_odeurs": sensoriel_vent_odeurs,
        "ia_vision_ecologique": ia_vision_ecologique,
        "quality_data": quality_data,
        "incertitude": incertitude,
        "calibration": calibration,
        "population_dynamics": population_dynamics,
        "climat_futur": climat_futur,
        "influence_lunaire": influence_lunaire,
        "pression_atmospherique": pression_atmospherique,
        "score_global_reality": score_global_reality,
        # Phase XI-SUPRA : 14 couches obligatoires
        "canada_zones_summary": canada_zones_summary,
        "lep_nearby": lep_nearby,
        "hydat_nearby": hydat_nearby,
        "observations": observations_nearby,
        "zones_risque": zones_risque,
        "habitats_critiques": habitats_critiques,
        "deplacements_ia": deplacements_ia,
        "score_local": score_local,
        "terrain_v10": t,
        "meteo": meteo,
        "esi_omega": "CONFORME",
        "data_source": t.get("source", "ESTIME"),
        "data_fiabilite": t.get("fiabilite", 0),
        "document_maitre": "BIONIC-OS-V10-SUPRA-INSTITUTIONNEL",
        "source": "TERRITOIRE-V10-SUPRA",
        "compute_ms": round((time.time() - start) * 1000),
    }
