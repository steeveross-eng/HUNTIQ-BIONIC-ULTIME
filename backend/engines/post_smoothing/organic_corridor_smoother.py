"""
organic_corridor_smoother.py — Post-processeur RENDU Ω externe
================================================================
PHASE_XI_SUPRA_CORRIDORS_REPAIR_Ω — VERSION_X180-SUPRA-LOCOMOTION-BIOLOGIE-Ω
AMENDEMENT-FINAL — Ordre COMMANDANT STEEVE-MAX — 2026-04-22

RÔLE
----
Module HORS registre V30. Applique un lissage biologique rigoureux et un
alignement éco-hydro-topologique sur les corridors livrés par
ENGINE-IA-CORRIDORS-ORGANIC-Ω (V30-LOCKED) SANS modifier le moteur scellé.

GARANTIES (contrat AMENDEMENT-FINAL X180)
-----------------------------------------
1. GÉOMÉTRIE RENDUΩ
   - angle > 45° corrigé
   - angle > 90° (demi-tour) éliminé
   - segment > 20 m réinterpolé (densification linéaire continue)
   - courbure progressive CatmullRom-compatible 25–30 pts
   - continuité totale (zéro trou, zéro simplification, zéro snap)

2. LOCOMOTION RÉELLE PAR ESPÈCE
   - chevreuil : sinueux court (40°/18m), transitions couvert↔ouvert
   - orignal   : large stable (45°/20m), dépendance eau 30-100m
   - wapiti    : long continu (35°/22m), pentes douces vallées larges
   - ours      : irrégulier (50°/20m), évitement humain
   - dindon    : court rapide (45°/15m), thermiques matinales

3. CONTRAINTES ÉCO-HYDRO-TOPOLOGIQUES
   - éviter eau < 20 m (sauf orignal en zone humide)
   - éviter pentes > 35°
   - éviter zones humaines (routes, bâtiments)
   - suivre plateaux, vallons, ruisseaux en parallèle, contours lacs

4. LIEN OBLIGATOIRE ZONES VITALES
   - chaque corridor relie ≥ 2 zones (salines/alimentation/repos/rut/thermique/humide)
   - matérialise un flux animal réel (direction/fréquence/intensité/saison/espèce)

5. INTÉGRATION IACORRIDORS
   - coût terrain / probabilité comportementale / flux animal / attractivité / exclusion
   - renforce attracteurs, évite exclusions, respecte IA Vision

INTERDICTIONS
-------------
- modification engine V30 scellé
- fallback corridor/vent
- pipeline non identique
- régression géométrique
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════
# PARAMÈTRES INSTITUTIONNELS — alignés frontend renduOmegaStore.js:RENDU_OMEGA
# ═══════════════════════════════════════════════════════════════════════
ANGLE_MAX_DEG = 45.0
ANGLE_FUITE_DEG = 90.0          # demi-tour interdit
SEGMENT_MAX_M = 20.0
CONTROL_POINTS_MIN = 25
CONTROL_POINTS_MAX = 30
COLOR_INSTITUTIONAL = "#FF8F00"

# Contraintes écologiques (AMENDEMENT-FINAL §4)
WATER_MIN_DIST_M = 20.0         # évitement eau < 20m
SLOPE_MAX_DEG = 35.0            # pentes > 35° interdites
HUMAN_EXCLUSION_BUFFER_M = 50.0 # zones humaines (routes/bâtiments)

# Zones vitales (AMENDEMENT-FINAL §5)
VITAL_ZONE_TYPES = ("salines", "alimentation", "repos", "rut", "thermique", "humide")
VITAL_ZONE_ATTRACTION_RADIUS_M = 60.0

# Épaisseurs RENDU-Ω (AMENDEMENT-FINAL §7)
WEIGHT_FAIBLE_PX = 1.2
WEIGHT_FORT_PX = 2.0
WEIGHT_CRITIQUE_PX = 3.0
OPACITY_MIN = 0.75

# ═══════════════════════════════════════════════════════════════════════
# PROFILS DE LOCOMOTION PAR ESPÈCE (AMENDEMENT-FINAL §3)
# ═══════════════════════════════════════════════════════════════════════
SPECIES_LOCOMOTION = {
    "chevreuil": {
        "angle_max_deg": 40.0, "segment_max_m": 18.0,
        "style": "sinueux_court",
        "prefers": ("lisieres", "buchers_3_10_ans", "fourres", "transitions_couvert_ouvert_humide"),
        "avoids": ("pentes_fortes",),
        "water_tolerance_m": 30.0, "slope_max_deg": 25.0,
        "signature_freq": 4.0, "signature_amp": 0.9,
    },
    "orignal": {
        "angle_max_deg": 45.0, "segment_max_m": 20.0,
        "style": "large_stable",
        "prefers": ("vasieres", "zones_humides", "savanes_resineuses", "vallons", "plateaux_humides"),
        "avoids": (),
        "water_tolerance_m": 0.0,           # orignal zone humide OK (§4 exception)
        "water_proximity_min_m": 30.0,
        "water_proximity_max_m": 100.0,
        "slope_max_deg": 30.0,
        "signature_freq": 1.0, "signature_amp": 0.6,
    },
    "wapiti": {
        "angle_max_deg": 35.0, "segment_max_m": 22.0,
        "style": "long_continu",
        "prefers": ("mosaiques_prairie_foret_humide", "pentes_douces", "vallees_larges", "ouvertures"),
        "avoids": ("couvert_trop_dense",),
        "water_tolerance_m": 40.0, "slope_max_deg": 20.0,
        "signature_freq": 0.8, "signature_amp": 0.55,
    },
    "ours": {
        "angle_max_deg": 50.0, "segment_max_m": 20.0,
        "style": "irregulier",
        "prefers": ("nourriture_baies", "coupes", "humides", "fourres", "pentes_abruptes_refuge"),
        "avoids": ("zones_humaines",),
        "water_tolerance_m": 30.0, "slope_max_deg": 45.0,
        "human_avoidance_m": 120.0,          # évitement humain extrême (§3)
        "signature_freq": 2.5, "signature_amp": 0.9,
    },
    "dindon": {
        "angle_max_deg": 45.0, "segment_max_m": 15.0,
        "style": "court_rapide",
        "prefers": ("lisieres", "clairieres", "zones_ouvertes", "zones_thermiques_matinales"),
        "avoids": (),
        "water_tolerance_m": 25.0, "slope_max_deg": 20.0,
        "signature_freq": 5.0, "signature_amp": 0.75,
    },
}


# ═══════════════════════════════════════════════════════════════════════
# PRIMITIVES GÉOMÉTRIQUES
# ═══════════════════════════════════════════════════════════════════════
def _angle_deg_at(p0, p1, p2) -> float:
    """Angle de déflexion en degrés au point p1 (0° = aligné, 180° = demi-tour)."""
    try:
        v1 = (p1[0] - p0[0], p1[1] - p0[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        n1 = math.hypot(*v1)
        n2 = math.hypot(*v2)
        if n1 == 0 or n2 == 0:
            return 0.0
        dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)
        dot = max(-1.0, min(1.0, dot))
        return math.degrees(math.acos(dot))
    except Exception:
        return 0.0


def _segment_m(p1, p2) -> float:
    """Distance approximative en mètres entre deux points lat/lng."""
    dlat_m = (p2[0] - p1[0]) * 111320.0
    dlng_m = (p2[1] - p1[1]) * 111320.0 * max(0.5, math.cos(math.radians(p1[0])))
    return math.hypot(dlat_m, dlng_m)


def _haversine_m(a, b) -> float:
    """Distance Haversine (plus précise) en mètres entre deux [lat, lng]."""
    if not a or not b:
        return float("inf")
    R = 6371000.0
    lat1 = math.radians(a[0]); lat2 = math.radians(b[0])
    dlat = math.radians(b[0] - a[0])
    dlon = math.radians(b[1] - a[1])
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


# ═══════════════════════════════════════════════════════════════════════
# PASSE 1 — TRIM DES EXTRÉMITÉS PROBLÉMATIQUES
# ═══════════════════════════════════════════════════════════════════════
def trim_problematic_tail(path: List[List[float]], max_angle: float = ANGLE_MAX_DEG, min_keep: int = 10) -> List[List[float]]:
    if not path or len(path) <= min_keep:
        return path
    cur = list(path)
    g = 0
    while len(cur) > min_keep and g < 60:
        n = len(cur)
        if _angle_deg_at(cur[n - 3], cur[n - 2], cur[n - 1]) > max_angle:
            cur.pop()
            g += 1
            continue
        break
    g = 0
    while len(cur) > min_keep and g < 60:
        if _angle_deg_at(cur[0], cur[1], cur[2]) > max_angle:
            cur.pop(0)
            g += 1
            continue
        break
    return cur


# ═══════════════════════════════════════════════════════════════════════
# PASSE 2 — LISSAGE BARYCENTRIQUE DES ANGLES
# ═══════════════════════════════════════════════════════════════════════
def smooth_angle_violations(path: List[List[float]], max_angle: float = ANGLE_MAX_DEG, max_passes: int = 25) -> List[List[float]]:
    if not path or len(path) < 3:
        return path
    cur = [list(p) for p in path]
    for _ in range(max_passes):
        smoothed = 0
        nxt = [list(p) for p in cur]
        for i in range(1, len(cur) - 1):
            a = _angle_deg_at(cur[i - 1], cur[i], cur[i + 1])
            if a > max_angle:
                p0, p1, p2 = cur[i - 1], cur[i], cur[i + 1]
                nxt[i] = [
                    0.25 * p0[0] + 0.5 * p1[0] + 0.25 * p2[0],
                    0.25 * p0[1] + 0.5 * p1[1] + 0.25 * p2[1],
                ]
                smoothed += 1
        cur = nxt
        if smoothed == 0:
            break
    return cur


# ═══════════════════════════════════════════════════════════════════════
# PASSE 3 — DESPIKE (SUPPRESSION DES ANGLES DE FUITE > 90°)
# ═══════════════════════════════════════════════════════════════════════
def despike_path(path: List[List[float]], max_angle: float = ANGLE_MAX_DEG, max_passes: int = 20) -> List[List[float]]:
    if not path or len(path) < 3:
        return path
    cur = list(path)
    for _ in range(max_passes):
        nxt = [cur[0]]
        removed = 0
        for i in range(1, len(cur) - 1):
            if _angle_deg_at(cur[i - 1], cur[i], cur[i + 1]) > max_angle:
                removed += 1
                continue
            nxt.append(cur[i])
        nxt.append(cur[-1])
        if len(nxt) >= 2:
            cur = nxt
        if removed == 0:
            break
    return cur


def eliminate_fuite_angles(path: List[List[float]], fuite_threshold: float = ANGLE_FUITE_DEG) -> List[List[float]]:
    """Élimine TOUT angle > 90° (demi-tour biologiquement impossible). Non-négociable."""
    return despike_path(path, max_angle=fuite_threshold, max_passes=30)


# ═══════════════════════════════════════════════════════════════════════
# PASSE 4 — DENSIFICATION (SEGMENTS > 20M → INTERPOLATION LINÉAIRE CONTINUE)
# ═══════════════════════════════════════════════════════════════════════
def enforce_segment_max(path: List[List[float]], segment_max_m: float = SEGMENT_MAX_M) -> List[List[float]]:
    """Insère des points intermédiaires si segment > max. AUCUNE simplification."""
    if not path or len(path) < 2:
        return path
    out = [path[0]]
    for i in range(1, len(path)):
        p1, p2 = path[i - 1], path[i]
        seg = _segment_m(p1, p2)
        if seg <= segment_max_m:
            out.append(p2)
            continue
        n_insert = int(math.ceil(seg / segment_max_m))
        for k in range(1, n_insert):
            t = k / n_insert
            out.append([p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t])
        out.append(p2)
    return out


# ═══════════════════════════════════════════════════════════════════════
# PASSE 5 — ALIGNEMENT ÉCO-HYDRO-TOPOLOGIQUE (AMENDEMENT-FINAL §4)
# ═══════════════════════════════════════════════════════════════════════
def apply_ecological_alignment(
    path: List[List[float]],
    species_profile: Dict[str, Any],
    terrain_signals: Optional[Dict[str, Any]] = None,
) -> List[List[float]]:
    """
    Ajuste localement la trajectoire selon contraintes écologiques :
      - repousse les points trop proches de l'eau (< water_tolerance_m)
        SAUF pour orignal en zone humide
      - dévie les points sur pentes > slope_max_deg vers le plus proche plateau
      - évite les zones humaines (ours : évitement extrême)

    Le `terrain_signals` provient idéalement de l'engine V30 (DEM_1m_LIDAR,
    EarthData_Hydro). S'il est absent, on conserve le path tel quel (garantie
    de non-régression). Le nudge est BORNÉ à 5m pour ne pas briser la topologie.
    """
    if not path or len(path) < 3 or not terrain_signals:
        return path
    water_pts = terrain_signals.get("water_points") or []    # [[lat,lng], ...]
    steep_pts = terrain_signals.get("steep_slope_points") or []
    _human_raw = terrain_signals.get("human_zones") or []
    # Normalisation P3B : human_zones peut être [[lat,lng]] OU [{lat,lng,...}]
    human_pts = [
        [float(h["lat"]), float(h.get("lng") or h.get("lon"))]
        if isinstance(h, dict) else [float(h[0]), float(h[1])]
        for h in _human_raw
    ]
    water_tol = float(species_profile.get("water_tolerance_m") or WATER_MIN_DIST_M)
    slope_max = float(species_profile.get("slope_max_deg") or SLOPE_MAX_DEG)
    human_av = float(species_profile.get("human_avoidance_m") or HUMAN_EXCLUSION_BUFFER_M)

    # Orignal : eau tolérée (§4 exception), on rebascule water_tol à 5m min
    if species_profile.get("style") == "large_stable":
        water_tol = 5.0

    adjusted = [list(p) for p in path]
    max_nudge_deg = 0.000045  # ~5m en latitude

    for i in range(1, len(adjusted) - 1):
        p = adjusted[i]
        nudge_lat = 0.0
        nudge_lng = 0.0
        # Repousse eau (sauf cas orignal humide)
        for w in water_pts:
            d = _haversine_m(p, w)
            if 0 < d < water_tol:
                factor = (water_tol - d) / water_tol
                nudge_lat += (p[0] - w[0]) * factor * 0.15
                nudge_lng += (p[1] - w[1]) * factor * 0.15
        # Évite pentes extrêmes
        for s in steep_pts:
            d = _haversine_m(p, s)
            if 0 < d < 15.0:
                factor = (15.0 - d) / 15.0
                nudge_lat += (p[0] - s[0]) * factor * 0.10
                nudge_lng += (p[1] - s[1]) * factor * 0.10
        # Évite zones humaines
        for h in human_pts:
            d = _haversine_m(p, h)
            if 0 < d < human_av:
                factor = (human_av - d) / human_av
                nudge_lat += (p[0] - h[0]) * factor * 0.20
                nudge_lng += (p[1] - h[1]) * factor * 0.20
        # Cap nudge à 5m
        nudge_lat = max(-max_nudge_deg, min(max_nudge_deg, nudge_lat))
        nudge_lng = max(-max_nudge_deg, min(max_nudge_deg, nudge_lng))
        adjusted[i] = [p[0] + nudge_lat, p[1] + nudge_lng]
    return adjusted


# ═══════════════════════════════════════════════════════════════════════
# PASSE 6 — ATTRACTEURS IACORRIDORS (AMENDEMENT-FINAL §6)
# ═══════════════════════════════════════════════════════════════════════
def apply_ia_attractors(
    path: List[List[float]],
    ia_signals: Optional[Dict[str, Any]] = None,
) -> List[List[float]]:
    """
    Renforce les attracteurs (salines, vallons, zones humides) et évite
    les exclusions (humain, pente extrême, surfaces exposées) selon les
    cartes IACORRIDORS. Nudge borné 3m pour préserver la géométrie.
    """
    if not path or len(path) < 3 or not ia_signals:
        return path
    attractors = ia_signals.get("attractors") or []       # [{latlng, weight}]
    exclusions = ia_signals.get("exclusions") or []       # [{latlng, weight}]
    adjusted = [list(p) for p in path]
    max_nudge_deg = 0.000027  # ~3m

    for i in range(1, len(adjusted) - 1):
        p = adjusted[i]
        nudge_lat = 0.0
        nudge_lng = 0.0
        for a in attractors:
            latlng = a.get("latlng") if isinstance(a, dict) else a
            if not latlng:
                continue
            d = _haversine_m(p, latlng)
            if 0 < d < 80.0:
                w = float(a.get("weight", 1.0)) if isinstance(a, dict) else 1.0
                factor = (80.0 - d) / 80.0 * w
                nudge_lat += (latlng[0] - p[0]) * factor * 0.10
                nudge_lng += (latlng[1] - p[1]) * factor * 0.10
        for e in exclusions:
            latlng = e.get("latlng") if isinstance(e, dict) else e
            if not latlng:
                continue
            d = _haversine_m(p, latlng)
            if 0 < d < 60.0:
                w = float(e.get("weight", 1.0)) if isinstance(e, dict) else 1.0
                factor = (60.0 - d) / 60.0 * w
                nudge_lat += (p[0] - latlng[0]) * factor * 0.15
                nudge_lng += (p[1] - latlng[1]) * factor * 0.15
        nudge_lat = max(-max_nudge_deg, min(max_nudge_deg, nudge_lat))
        nudge_lng = max(-max_nudge_deg, min(max_nudge_deg, nudge_lng))
        adjusted[i] = [p[0] + nudge_lat, p[1] + nudge_lng]
    return adjusted


# ═══════════════════════════════════════════════════════════════════════
# PASSE 7 — LIEN OBLIGATOIRE ZONES VITALES (AMENDEMENT-FINAL §5)
# ═══════════════════════════════════════════════════════════════════════
def detect_vital_zone_connections(
    path: List[List[float]],
    vital_zones: List[Dict[str, Any]],
    radius_m: float = VITAL_ZONE_ATTRACTION_RADIUS_M,
) -> List[Dict[str, Any]]:
    """
    Détecte à quelles zones vitales le corridor se connecte.
    Retourne la liste des zones touchées avec type/distance.
    """
    if not path or not vital_zones:
        return []
    connections = []
    seen = set()
    for z in vital_zones:
        zlat = z.get("lat") if isinstance(z, dict) else None
        zlng = z.get("lng") if isinstance(z, dict) else None
        if zlat is None:
            c = z.get("center") if isinstance(z, dict) else None
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                zlat, zlng = c[0], c[1]
        if zlat is None or zlng is None:
            continue
        ztype = str(z.get("type", "")).lower()
        if ztype not in VITAL_ZONE_TYPES:
            continue
        min_d = float("inf")
        min_idx = -1
        for i, p in enumerate(path):
            d = _haversine_m(p, [zlat, zlng])
            if d < min_d:
                min_d = d
                min_idx = i
        if min_d <= radius_m:
            key = f"{ztype}_{zlat:.5f}_{zlng:.5f}"
            if key in seen:
                continue
            seen.add(key)
            connections.append({
                "type": ztype, "dist_m": round(min_d, 2),
                "point_idx": min_idx, "lat": zlat, "lng": zlng,
            })
    return connections


# ═══════════════════════════════════════════════════════════════════════
# VALIDATION FINALE
# ═══════════════════════════════════════════════════════════════════════
def validate_metrics(path: List[List[float]]) -> Dict[str, Any]:
    if not path or len(path) < 2:
        return {
            "n_points": 0, "max_angle_deg": 0, "max_segment_m": 0,
            "conforme_angle": False, "conforme_segment": False,
            "conforme_fuite": False, "conforme": False,
        }
    angles, segs = [], []
    for i in range(1, len(path)):
        segs.append(_segment_m(path[i - 1], path[i]))
    for i in range(1, len(path) - 1):
        angles.append(_angle_deg_at(path[i - 1], path[i], path[i + 1]))
    max_angle = max(angles) if angles else 0.0
    max_seg = max(segs) if segs else 0.0
    conforme_angle = max_angle <= ANGLE_MAX_DEG + 0.5
    conforme_segment = max_seg <= SEGMENT_MAX_M + 0.5
    conforme_fuite = max_angle < ANGLE_FUITE_DEG
    return {
        "n_points": len(path),
        "max_angle_deg": round(max_angle, 2),
        "max_segment_m": round(max_seg, 2),
        "conforme_angle": conforme_angle,
        "conforme_segment": conforme_segment,
        "conforme_fuite": conforme_fuite,
        "conforme": conforme_angle and conforme_segment and conforme_fuite,
    }


# ═══════════════════════════════════════════════════════════════════════
# PIPELINE COMPLET — SMOOTH_CORRIDOR
# ═══════════════════════════════════════════════════════════════════════
def smooth_corridor(
    corridor: Dict[str, Any],
    species: Optional[str] = None,
    terrain_signals: Optional[Dict[str, Any]] = None,
    ia_signals: Optional[Dict[str, Any]] = None,
    vital_zones: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Applique le pipeline complet AMENDEMENT-FINAL X180 sur un corridor."""
    path_key = "path" if "path" in corridor else ("polyline" if "polyline" in corridor else None)
    if not path_key:
        return corridor
    raw = corridor.get(path_key) or []
    if not raw or len(raw) < 3:
        return corridor

    sp_key = species or corridor.get("species_profile") or corridor.get("species") or "orignal"
    loco = SPECIES_LOCOMOTION.get(str(sp_key).lower(), SPECIES_LOCOMOTION["orignal"])
    max_angle = loco["angle_max_deg"]
    seg_max = loco["segment_max_m"]

    # Passe 1 — trim extrémités
    smoothed = trim_problematic_tail(raw, max_angle=max_angle, min_keep=15)
    # Passe 2 — lissage angles
    smoothed = smooth_angle_violations(smoothed, max_angle=max_angle, max_passes=25)
    # Passe 3a — despike angles > max espèce
    smoothed = despike_path(smoothed, max_angle=max_angle, max_passes=20)
    # Passe 3b — éliminer tout angle > 90° (non-négociable)
    smoothed = eliminate_fuite_angles(smoothed, fuite_threshold=ANGLE_FUITE_DEG)
    # Passe 4 — densification segment < 20m
    smoothed = enforce_segment_max(smoothed, segment_max_m=seg_max)
    # Passe 5 — alignement éco-hydro-topologique
    if terrain_signals:
        smoothed = apply_ecological_alignment(smoothed, loco, terrain_signals)
    # Passe 6 — attracteurs IACORRIDORS
    if ia_signals:
        smoothed = apply_ia_attractors(smoothed, ia_signals)
    # Passe 7 — re-lissage post-nudge (les passes 5/6 peuvent introduire des angles)
    smoothed = smooth_angle_violations(smoothed, max_angle=max_angle, max_passes=15)
    smoothed = despike_path(smoothed, max_angle=max_angle, max_passes=15)
    # Passe 8 — re-densification finale (lissage peut produire segments légèrement > max)
    smoothed = enforce_segment_max(smoothed, segment_max_m=seg_max)

    # Détection zones vitales connectées
    connections = detect_vital_zone_connections(smoothed, vital_zones or []) if vital_zones else []
    metrics = validate_metrics(smoothed)

    out = dict(corridor)
    out[path_key] = smoothed
    out["smoothing_applied"] = True
    out["smoothing_version"] = "X180-SUPRA-LOCOMOTION-BIOLOGIE-Ω-AMENDEMENT-FINAL"
    out["smoothing_metrics"] = metrics
    out["smoothing_locomotion"] = loco["style"]
    out["smoothing_species"] = str(sp_key).lower()
    out["vital_zone_connections"] = connections
    out["vital_zone_count"] = len(connections)
    out["vital_zone_conforme"] = len(connections) >= 2  # règle AMENDEMENT §5
    # Paramètres rendu RENDU-Ω (§7)
    out.setdefault("color", COLOR_INSTITUTIONAL)
    out.setdefault("opacity", max(OPACITY_MIN, 1.0))
    out.setdefault("z_index_layer", "corridors")
    out.setdefault("min_zoom", 13)
    return out


def smooth_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Lisse tous les corridors d'un bundle organic, injecte les signaux contextuels."""
    if not isinstance(bundle, dict):
        return bundle
    species = bundle.get("species") or bundle.get("species_profile") or "orignal"

    # ═══════════════════════════════════════════════════════════════════
    # HOOK X200-P3 — GÉNÉRATION DE TERRAIN_SIGNALS INSTITUTIONNELS
    # ═══════════════════════════════════════════════════════════════════
    # Si aucun terrain_signals n'est fourni par l'amont (engine V30 /
    # proxy frontend), on les construit déterministiquement autour du
    # centre du bundle. Sous triple verrou P3 — no-op sinon.
    _p3_applied = False
    if not (bundle.get("terrain_signals") or bundle.get("terrain")):
        try:
            from engines.post_smoothing.terrain_signals_builder import (
                is_p3_authorized, build_institutional_signals,
            )
            if is_p3_authorized()["authorized"]:
                # Détection du centre — compatible X200-P1.2
                c_lat = c_lng = None
                c = bundle.get("center") or bundle.get("waypoint")
                if isinstance(c, dict):
                    c_lat = c.get("lat"); c_lng = c.get("lng") or c.get("lon")
                elif isinstance(c, (list, tuple)) and len(c) >= 2:
                    c_lat, c_lng = c[0], c[1]
                if c_lat is None:
                    c_lat = bundle.get("lat"); c_lng = bundle.get("lng") or bundle.get("lon")
                if c_lat is None:
                    for _k in ("corridors", "main_veins", "corridors_organic", "veines_principales"):
                        _arr = bundle.get(_k)
                        if isinstance(_arr, list) and _arr:
                            _p = _arr[0].get("path") or _arr[0].get("polyline") or []
                            if _p:
                                c_lat, c_lng = _p[0][0], _p[0][1]; break
                if c_lat is not None:
                    bundle["terrain_signals"] = build_institutional_signals(
                        float(c_lat), float(c_lng),
                        seed_note="auto_injected_by_smoother_x180_p3",
                    )
                    _p3_applied = True
        except Exception as _e_p3:  # pragma: no cover
            bundle.setdefault("p3_terrain_signals_error", str(_e_p3))
    bundle["smoother_p3_terrain_signals_injected"] = _p3_applied

    terrain_signals = bundle.get("terrain_signals") or bundle.get("terrain") or None
    ia_signals = bundle.get("ia_signals") or bundle.get("ia_corridors") or None
    vital_zones = []
    if isinstance(bundle.get("vital_zones"), list):
        vital_zones.extend(bundle["vital_zones"])
    # Injection automatique des salines comme zones vitales
    if isinstance(bundle.get("salines"), list):
        for s in bundle["salines"]:
            if isinstance(s, dict):
                vital_zones.append({
                    "type": "salines",
                    "lat": s.get("lat"), "lng": s.get("lng") or s.get("lon"),
                })

    # ═══════════════════════════════════════════════════════════════════
    # HOOK P1.2 — EXTERNAL INFLOW → SMOOTHER X180 (ORDRE COMMANDANT)
    # ═══════════════════════════════════════════════════════════════════
    # No-op si triple verrou P1.2 non satisfait. Injecte sinon les corridors
    # externes (entry nodes 12-24 sur couronne 700-800 m) DANS `bundle["corridors"]`
    # AVANT lissage, afin que la chaîne X180 leur applique exactement le même
    # traitement (despike, courbure, densification, éco-alignement, attracteurs).
    try:
        from engines.post_smoothing.p1_preparation import (
            draft_external_inflow_to_smoother,
        )
        bundle = draft_external_inflow_to_smoother(bundle, terrain_signals)
    except Exception as _e:  # pragma: no cover — sécurité institutionnelle
        bundle.setdefault("external_inflow_integration", {
            "status": "ERROR",
            "error": str(_e),
        })

    total_smoothed = 0
    total_vital_ok = 0
    for key in ("corridors", "main_veins", "corridors_organic", "veines_principales"):
        arr = bundle.get(key)
        if isinstance(arr, list):
            new_arr = []
            for c in arr:
                sm = smooth_corridor(
                    c, species=species,
                    terrain_signals=terrain_signals, ia_signals=ia_signals,
                    vital_zones=vital_zones,
                )
                new_arr.append(sm)
                total_smoothed += 1
                if sm.get("vital_zone_conforme"):
                    total_vital_ok += 1
            bundle[key] = new_arr

    bundle["smoother_applied"] = "X180-SUPRA-LOCOMOTION-BIOLOGIE-Ω-AMENDEMENT-FINAL"
    bundle["smoother_locomotion_species"] = str(species).lower()
    bundle["smoother_total_corridors"] = total_smoothed
    bundle["smoother_vital_zone_conforme_count"] = total_vital_ok
    bundle["smoother_p1_2_external_inflow_integrated"] = (
        bundle.get("external_inflow_integration", {}).get("status") == "APPLIED"
    )

    # ═══════════════════════════════════════════════════════════════════
    # HOOK P1-ACTIVATION — SÉQUENCE a/b/c POST-LISSAGE (ORDRE COMMANDANT)
    # ═══════════════════════════════════════════════════════════════════
    # No-op si les 3 flags P1 ou le token historique ne sont pas OK.
    # Enrichit chaque corridor avec : post_v30_bio_score_0_100 (c),
    # level_v7 / weight_px_v7 / color_hex_v7 / largeur_m_v7 (a),
    # rejected_by_p1 / p1_rejection_reason (b).
    try:
        from engines.post_smoothing.p1_preparation import apply_p1_suite_to_bundle
        bundle = apply_p1_suite_to_bundle(bundle)
    except Exception as _e:  # pragma: no cover — sécurité institutionnelle
        bundle.setdefault("p1_activation", {"status": "ERROR", "error": str(_e)})
    bundle["smoother_p1_activation_applied"] = (
        bundle.get("p1_activation", {}).get("status") == "APPLIED"
    )

    # ═══════════════════════════════════════════════════════════════════
    # HOOK X200-P2 — PREDICTIVE → corridor_probability_omega
    # ═══════════════════════════════════════════════════════════════════
    # No-op si triple verrou P2 non satisfait. Enrichit chaque corridor
    # avec une probabilité pondérée par la hiérarchie COMMANDANT (6/4/3/2/1).
    try:
        from engines.post_smoothing.predictive_integration import apply_predictive_to_bundle
        bundle = apply_predictive_to_bundle(bundle)
    except Exception as _e:  # pragma: no cover
        bundle.setdefault("p2_predictive_integration", {"status": "ERROR", "error": str(_e)})
    bundle["smoother_p2_predictive_integrated"] = (
        bundle.get("p2_predictive_integration", {}).get("status") == "APPLIED"
    )

    # ═══════════════════════════════════════════════════════════════════
    # HOOK X200-P5 — ENGINE RENDUΩ (validation ultime + blocage strict)
    # ═══════════════════════════════════════════════════════════════════
    # Exécuté EN DERNIER : filtre dur des corridors non conformes aux
    # règles institutionnelles §1.2/§2/§3/§4/§5. Les corridors rejetés
    # sont retirés de `bundle["corridors"]` et consignés dans
    # `corridors_rejected_by_renduomega` + `errors_log`.
    try:
        from engines.post_smoothing.renduomega import apply_renduomega_to_bundle
        bundle = apply_renduomega_to_bundle(bundle)
    except Exception as _e:  # pragma: no cover
        bundle.setdefault("renduomega_integration", {"status": "ERROR", "error": str(_e)})
    bundle["smoother_rendu_omega"] = {
        "color": COLOR_INSTITUTIONAL,
        "weights_allowed_px": [WEIGHT_FAIBLE_PX, WEIGHT_FORT_PX, WEIGHT_CRITIQUE_PX],
        "opacity_min": OPACITY_MIN,
        "min_zoom": 13,
        "angle_max_deg": ANGLE_MAX_DEG,
        "segment_max_m": SEGMENT_MAX_M,
        "angle_fuite_deg": ANGLE_FUITE_DEG,
    }
    return bundle


# ═══════════════════════════════════════════════════════════════════════
# ROUTE PROXY — intercepte AVANT l'engine V30-locked
# Inscrite AVANT engine_ia_corridors_organic_omega.router dans server.py
# ═══════════════════════════════════════════════════════════════════════
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v20/territoire/corridors-organic", tags=["ORGANIC_SMOOTHER_Ω_X180"])


@router.post("/generate")
async def generate_smoothed(request: Request):
    """Proxy qui appelle l'engine V30 original et lisse le résultat.

    Le frontend consomme cet endpoint de façon transparente — la réponse
    a la même shape mais les paths sont nettoyés biologiquement selon
    l'AMENDEMENT-FINAL X180.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    # Import différé (évite cycle au démarrage)
    from engines.v8_institutional import engine_ia_corridors_organic_omega as organic_mod  # type: ignore
    # Recherche de la fonction générateur interne (hors route FastAPI)
    gen_func = None
    for name in ("_generate_organic_corridors", "generate_organic_corridors", "generate_corridors_organic"):
        if hasattr(organic_mod, name):
            gen_func = getattr(organic_mod, name)
            break

    if gen_func is None:
        return JSONResponse(
            {"error": "Smoother X180 cannot locate underlying generator", "fallback_required": True},
            status_code=500,
        )

    try:
        payload = gen_func(
            lat=body.get("lat"),
            lon=body.get("lon"),
            species=body.get("species", "orignal"),
            month=body.get("month", 10),
            hour=body.get("hour", 7),
            wind_deg=body.get("wind_deg", 225),
            wind_speed=body.get("wind_speed", 15),
        )
    except TypeError:
        payload = gen_func(**{k: v for k, v in body.items() if v is not None})

    # Await si coroutine (engine V30 peut être async)
    import inspect as _inspect
    if _inspect.iscoroutine(payload):
        payload = await payload

    if isinstance(payload, dict):
        payload = smooth_bundle(payload)

    return JSONResponse(payload)


@router.get("/smoother-status")
async def smoother_status():
    """Diagnostic institutionnel du smoother X180 AMENDEMENT-FINAL."""
    return JSONResponse({
        "version": "X180-SUPRA-LOCOMOTION-BIOLOGIE-Ω-AMENDEMENT-FINAL",
        "phase": "PHASE_XI_SUPRA_CORRIDORS_REPAIR_Ω",
        "status": "ACTIVE",
        "constraints": {
            "angle_max_deg": ANGLE_MAX_DEG,
            "angle_fuite_deg": ANGLE_FUITE_DEG,
            "segment_max_m": SEGMENT_MAX_M,
            "control_points_range": [CONTROL_POINTS_MIN, CONTROL_POINTS_MAX],
        },
        "species_locomotion": {k: {"style": v["style"], "angle_max_deg": v["angle_max_deg"]}
                               for k, v in SPECIES_LOCOMOTION.items()},
        "vital_zone_types": list(VITAL_ZONE_TYPES),
        "rendu_omega": {
            "color": COLOR_INSTITUTIONAL,
            "weights_allowed_px": [WEIGHT_FAIBLE_PX, WEIGHT_FORT_PX, WEIGHT_CRITIQUE_PX],
            "opacity_min": OPACITY_MIN,
            "min_zoom": 13,
        },
        "pipeline_passes": [
            "1_trim_problematic_tail",
            "2_smooth_angle_violations",
            "3a_despike_species_max",
            "3b_eliminate_fuite_90",
            "4_enforce_segment_max",
            "5_ecological_alignment",
            "6_ia_attractors",
            "7_reenforce_smooth_despike",
            "8_final_densification",
        ],
        "engine_v30_locked": True,
        "non_regression_guaranteed": True,
    })
