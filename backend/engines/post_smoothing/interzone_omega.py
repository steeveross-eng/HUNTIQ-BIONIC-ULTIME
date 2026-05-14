"""
interzone_omega.py — PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_INTERZONE_GENERATION
=============================================================================
Phase     : PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_INTERZONE_GENERATION
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

GÉNÉRATEUR DE CORRIDORS INTER-ZONES POST-V30.

Objectif : corriger la violation §2.3 (liaison obligatoire des zones vitales)
observée sur le pipeline V30 qui produit une topologie RADIAL SPOKE-WHEEL
(corridors partant tous du waypoint, aucune liaison inter-zones réelle).

Ce module AJOUTE des corridors veineux :
  (a) entre les centroïdes des zones vitales différentes (matrice d'affinité
      biologique adaptée par espèce),
  (b) entre les salines et leurs zones d'attraction,
  (c) des corridors ENTRANTS depuis 800-1500 m en dehors du rayon fonctionnel
      vers les zones vitales (migration/déplacement longue distance).

V30 reste strictement LOCKED : ce module ne MUTE pas le V30, il PRODUIT de
nouveaux corridors qui sont ensuite passés à veineux_omega pour lissage puis
à RenduΩ pour validation institutionnelle.
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════
# Verrou institutionnel
# ═══════════════════════════════════════════════════════════════════════
INTERZONE_ENABLED = True
INTERZONE_ENV_FLAG = "INTERZONE_OMEGA_AUTHORIZED_BY_COMMANDANT"
INTERZONE_TOKEN_ENV = "INTERZONE_OMEGA_COMMANDANT_TOKEN"
INTERZONE_EXPECTED_TOKEN = "STEEVE-MAX-XII-INTERZONE-EXPLICIT"


def is_interzone_authorized() -> Dict[str, Any]:
    env_ok = os.environ.get(INTERZONE_ENV_FLAG, "").strip().lower() == "true"
    token_ok = os.environ.get(INTERZONE_TOKEN_ENV, "").strip() == INTERZONE_EXPECTED_TOKEN
    return {
        "authorized": bool(INTERZONE_ENABLED and env_ok and token_ok),
        "flag_enabled": INTERZONE_ENABLED,
        "env_flag_ok": env_ok,
        "token_ok": token_ok,
    }


# ═══════════════════════════════════════════════════════════════════════
# Matrice d'affinité biologique (par espèce)
# Chaque affinité = poids [0.0, 1.0]. Seulement si >= 0.3 → corridor généré.
# ═══════════════════════════════════════════════════════════════════════
AFFINITY_MATRIX: Dict[str, Dict[Tuple[str, str], float]] = {
    # Orignal (Alces alces) : herbivore, rut automne, eau essentielle
    "orignal": {
        ("rut", "alimentation"): 0.90,
        ("alimentation", "eau"): 0.85,
        ("repos", "alimentation"): 0.80,
        ("thermique", "repos"): 0.70,
        ("saline", "alimentation"): 0.75,
        ("saline", "rut"): 0.65,
        ("saline", "eau"): 0.55,
        ("rut", "eau"): 0.50,
        ("alimentation", "thermique"): 0.45,
        ("repos", "eau"): 0.40,
    },
    # Cerf de Virginie (Odocoileus virginianus) : plus petit, mobile, rut intense
    "cerf": {
        ("rut", "alimentation"): 0.92,
        ("alimentation", "eau"): 0.75,
        ("repos", "alimentation"): 0.85,
        ("thermique", "repos"): 0.70,
        ("saline", "alimentation"): 0.80,
        ("saline", "rut"): 0.70,
        ("rut", "repos"): 0.60,
        ("alimentation", "thermique"): 0.50,
    },
    # Ours noir (Ursus americanus) : omnivore, pré-hibernation automne
    "ours": {
        ("alimentation", "repos"): 0.90,
        ("alimentation", "eau"): 0.75,
        ("thermique", "repos"): 0.80,
        ("saline", "alimentation"): 0.40,  # moins pour ours
        ("alimentation", "alimentation"): 0.50,  # nomadisme alimentaire
        ("repos", "eau"): 0.55,
    },
    # Dindon sauvage (Meleagris gallopavo) : pas de rut en automne, perchage+alim
    "dindon": {
        ("alimentation", "repos"): 0.88,   # perchage nocturne
        ("alimentation", "eau"): 0.70,
        ("alimentation", "alimentation"): 0.60,  # multi-sites gagnage
        ("thermique", "repos"): 0.55,
        ("saline", "alimentation"): 0.30,
    },
}

# Corridors ENTRANTS (migration longue distance depuis l'extérieur)
# Activé pour espèces mobiles uniquement
ENTERING_CORRIDORS_ENABLED: Dict[str, bool] = {
    "orignal": True,    # grands déplacements en rut
    "cerf": True,       # déplacements inter-territoires
    "ours": False,      # territoire local
    "dindon": False,    # volaille sédentaire
}
# ═══ COMMANDE OFFICIELLE STEEVE-MAX §3 — RÈGLE INSTITUTIONNELLE 540-780 m ═══
# Les corridors entrants doivent être visuellement rendus depuis l'extérieur du
# rayon fonctionnel (zone 540-780 m) afin d'assurer une continuité organique
# complète entre l'extérieur et le waypoint central. Aucun clipping visuel
# n'est autorisé dans la zone 600-780 m.
#
# Conséquences :
#   - ENTERING_DISTANCE_MIN_M = 540 m (entrée naturelle)
#   - ENTERING_DISTANCE_MAX_M = 778 m (juste sous 780 m strict §3.1 RenduΩ)
#   - INTERZONE_FUNCTIONAL_RADIUS_MAX_M = 778 m (équivaut au max RenduΩ)
#   - Validation RenduΩ : un corridor tronqué AVANT 780 m est rejeté
#     comme « clipping_intra_radius » (cf. _detect_clipping_violation).
ENTERING_DISTANCE_MIN_M = 540.0
ENTERING_DISTANCE_MAX_M = 778.0
ENTERING_NB_BEARINGS = 6  # N, NE, E, SE, S, SO, O, NO → 6 bearings pour densité

# Clip institutionnel (§2.4) : 778 m (1 m de marge sous la borne max RenduΩ
# pour éviter les rejets à cause des erreurs flottantes).
INTERZONE_FUNCTIONAL_RADIUS_MAX_M = 778.0

# Paramètres géométriques (alignés RenduΩ)
INTERZONE_POINTS_OUT = 30
INTERZONE_SEG_MAX_M = 18.0
INTERZONE_ANGLE_MAX_DEG = 40.0
INTERZONE_MIN_LENGTH_M = 150.0   # zones vitales peuvent être proches
INTERZONE_MAX_LENGTH_M = 1400.0  # autorisé avant clip au rayon fonctionnel


# ═══════════════════════════════════════════════════════════════════════
# Géométrie
# ═══════════════════════════════════════════════════════════════════════
def _distance_m(a: List[float], b: List[float]) -> float:
    R = 6371000.0
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    h = (math.sin((la2 - la1) / 2) ** 2 +
         math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(min(1.0, math.sqrt(h)))


def _meters_to_latlng(lat: float, d_lat_m: float, d_lng_m: float) -> Tuple[float, float]:
    dlat = d_lat_m / 111320.0
    cos_lat = math.cos(math.radians(lat))
    dlng = d_lng_m / (111320.0 * max(1e-6, cos_lat))
    return dlat, dlng


def _centroid(points: List[List[float]]) -> Optional[List[float]]:
    if not points:
        return None
    lat = sum(float(p[0]) for p in points) / len(points)
    lng = sum(float(p[1]) for p in points) / len(points)
    return [lat, lng]


def _polygon_centroid(polygon: List[List[float]]) -> Optional[List[float]]:
    """Centroïde simple (moyenne) pour polygon de zone."""
    return _centroid(polygon)


def _bearing_deg(a: List[float], b: List[float]) -> float:
    lat1 = math.radians(a[0])
    lat2 = math.radians(b[0])
    dlon = math.radians(b[1] - a[1])
    y = math.sin(dlon) * math.cos(lat2)
    x = (math.cos(lat1) * math.sin(lat2)
         - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
    brng = math.degrees(math.atan2(y, x))
    return (brng + 360.0) % 360.0


def _point_at_bearing(origin: List[float], bearing_deg: float, distance_m: float) -> List[float]:
    R = 6371000.0
    brng = math.radians(bearing_deg)
    lat1 = math.radians(origin[0])
    lon1 = math.radians(origin[1])
    ang = distance_m / R
    lat2 = math.asin(math.sin(lat1) * math.cos(ang)
                     + math.cos(lat1) * math.sin(ang) * math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(ang) * math.cos(lat1),
                              math.cos(ang) - math.sin(lat1) * math.sin(lat2))
    return [math.degrees(lat2), math.degrees(lon2)]


def _clip_path_to_functional_radius(path: List[List[float]], center: List[float],
                                     max_radius_m: float) -> List[List[float]]:
    """Tronque le chemin pour qu'aucun point ne dépasse max_radius_m du centre.
    Si le premier point est déjà au-delà, on interpole à l'entrée de la sphère.
    """
    if not path:
        return path
    # Trouver le premier point IN et le dernier point IN
    in_flags = [_distance_m(p, center) <= max_radius_m for p in path]
    if not any(in_flags):
        return []  # aucun point dans le rayon → rejet
    # premier index IN
    first_in = in_flags.index(True)
    # dernier index IN
    last_in = len(in_flags) - 1 - in_flags[::-1].index(True)
    out = list(path[first_in:last_in + 1])
    # interpoler si le point d'avant first_in était OUT
    if first_in > 0:
        p_out = path[first_in - 1]
        p_in = path[first_in]
        # dichotomie simple : avancer de p_out vers p_in jusqu'à entrer
        for _ in range(12):
            mid = [(p_out[0] + p_in[0]) / 2, (p_out[1] + p_in[1]) / 2]
            if _distance_m(mid, center) <= max_radius_m:
                p_in = mid
            else:
                p_out = mid
        out.insert(0, p_in)
    # interpoler si le point d'après last_in était OUT
    if last_in < len(path) - 1:
        p_in = path[last_in]
        p_out = path[last_in + 1]
        for _ in range(12):
            mid = [(p_out[0] + p_in[0]) / 2, (p_out[1] + p_in[1]) / 2]
            if _distance_m(mid, center) <= max_radius_m:
                p_in = mid
            else:
                p_out = mid
        out.append(p_in)
    return out


def _resample_uniform_n(path: List[List[float]], n: int) -> List[List[float]]:
    """Resampling linéaire uniforme à N points (duplicata minimal)."""
    if len(path) < 2 or n < 2:
        return list(path)
    cum = [0.0]
    for i in range(1, len(path)):
        cum.append(cum[-1] + _distance_m(path[i - 1], path[i]))
    total = cum[-1]
    if total <= 0:
        return [list(path[0])] * n
    step = total / (n - 1)
    out: List[List[float]] = []
    seg = 0
    for i in range(n):
        target = i * step
        while seg < len(cum) - 2 and cum[seg + 1] < target:
            seg += 1
        d0, d1 = cum[seg], cum[seg + 1]
        t = 0.0 if d1 == d0 else (target - d0) / (d1 - d0)
        t = max(0.0, min(1.0, t))
        p0 = path[seg]
        p1 = path[seg + 1]
        out.append([p0[0] + (p1[0] - p0[0]) * t,
                    p0[1] + (p1[1] - p0[1]) * t])
    return out


def _build_straight_path(a: List[float], b: List[float], n_pts: int = INTERZONE_POINTS_OUT) -> List[List[float]]:
    """Trace un chemin droit entre A et B avec n_pts points équidistants."""
    if n_pts < 2:
        return [list(a), list(b)]
    out: List[List[float]] = []
    for i in range(n_pts):
        t = i / (n_pts - 1)
        out.append([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t])
    return out


def _add_biological_curvature(path: List[List[float]], seed: int = 0,
                               amplitude_m: float = 12.0) -> List[List[float]]:
    """Ajoute une ondulation biologique (arc naturel, pas une ligne droite)."""
    if len(path) < 4:
        return list(path)
    out: List[List[float]] = [list(path[0])]
    N = len(path) - 1
    for i in range(1, N):
        p_prev = path[i - 1]
        p_curr = path[i]
        p_next = path[i + 1]
        tx = p_next[0] - p_prev[0]
        ty = p_next[1] - p_prev[1]
        norm = math.hypot(tx, ty)
        if norm < 1e-9:
            out.append(list(p_curr))
            continue
        nx, ny = -ty / norm, tx / norm
        # arc principal (1/2 sinusoïde sur toute la longueur) + micro-oscillation
        phase = (i / N) * math.pi
        arc = math.sin(phase)
        micro = math.sin(phase * 5 + seed * 0.7) * 0.25
        amp_m = amplitude_m * (arc + micro)
        d_lat, d_lng = _meters_to_latlng(p_curr[0], nx * amp_m, ny * amp_m)
        out.append([p_curr[0] + d_lat, p_curr[1] + d_lng])
    out.append(list(path[-1]))
    return out


# ═══════════════════════════════════════════════════════════════════════
# Construction des ancrages (zones + salines)
# ═══════════════════════════════════════════════════════════════════════
def _extract_zone_anchors(zones: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Retourne {zone_type: [{id, center:[lat,lng]}, ...]}."""
    anchors: Dict[str, List[Dict[str, Any]]] = {}
    for z in zones or []:
        ztype = str(z.get("type") or "").lower()
        poly = z.get("polygon") or []
        if not ztype or not poly:
            continue
        c = _polygon_centroid(poly)
        if c is None:
            continue
        anchors.setdefault(ztype, []).append({
            "id": z.get("id") or f"zone_{ztype}",
            "center": c,
            "type": ztype,
        })
    return anchors


def _extract_saline_anchors(salines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for i, s in enumerate(salines or []):
        lat = s.get("lat")
        lng = s.get("lng") or s.get("lon")
        if lat is None or lng is None:
            continue
        out.append({
            "id": s.get("id") or f"saline_{i}",
            "center": [float(lat), float(lng)],
            "type": "saline",
        })
    return out


# ═══════════════════════════════════════════════════════════════════════
# Génération inter-zones
# ═══════════════════════════════════════════════════════════════════════
def _build_interzone_corridor(a: Dict[str, Any], b: Dict[str, Any],
                               species: str, affinity: float,
                               seed: int,
                               waypoint: Optional[List[float]] = None) -> Optional[Dict[str, Any]]:
    """Construit un corridor veineux entre deux ancres, clippé au rayon fonctionnel.

    §2.4 RenduΩ : functional_radius ∈ [420, 780] m. Si le segment direct A→B
    reste dans le cercle intérieur (max_r < 430 m), on introduit un DÉTOUR
    veineux biologique (point intermédiaire perpendiculaire à 430-500 m du
    waypoint) pour respecter la borne minimale du rayon fonctionnel.
    """
    c_a, c_b = a["center"], b["center"]
    length = _distance_m(c_a, c_b)
    if length < INTERZONE_MIN_LENGTH_M or length > INTERZONE_MAX_LENGTH_M:
        return None

    # Construction de base (A → B direct) ou avec détour veineux biologique
    if waypoint is not None:
        max_r_straight = max(_distance_m(c_a, waypoint), _distance_m(c_b, waypoint))
        # Si les deux ancres sont dans le cercle intérieur < 430 m du WP,
        # on impose un détour via un point à ≥ 440 m (garantit borne min 420 m
        # même après amplitude organique et lissage veineux).
        if max_r_straight < 430.0:
            mid_ab = [(c_a[0] + c_b[0]) / 2, (c_a[1] + c_b[1]) / 2]
            # Vecteur (lat,lng) mid_ab → WP
            vx = mid_ab[0] - waypoint[0]
            vy = mid_ab[1] - waypoint[1]
            # Direction AB normalisée
            dx = c_b[0] - c_a[0]
            dy = c_b[1] - c_a[1]
            norm = math.hypot(dx, dy)
            if norm < 1e-9:
                return None
            # Normale unitaire en coord. lat/lng
            nx, ny = -dy / norm, dx / norm
            # Choisir signe qui éloigne du WP
            sign = 1.0 if (nx * vx + ny * vy) >= 0 else -1.0
            # Convertir mid_ab en coord locales mètres depuis WP
            mid_x_m = vx * 111320.0
            mid_y_m = vy * 111320.0 * math.cos(math.radians(mid_ab[0]))
            d_mid_m = math.hypot(mid_x_m, mid_y_m)
            # Pousser perpendiculairement assez pour que max_r ≥ 480 m (marge)
            target_r_m = 500.0
            if d_mid_m < target_r_m:
                push_m = math.sqrt(max(0.0, target_r_m ** 2 - d_mid_m ** 2)) + 50.0
            else:
                push_m = 100.0
            # Conversion du push en lat/lng selon la normale
            d_lat_push, d_lng_push = _meters_to_latlng(
                mid_ab[0], nx * push_m * sign, ny * push_m * sign,
            )
            detour_point = [mid_ab[0] + d_lat_push, mid_ab[1] + d_lng_push]
            # Construction A → detour → B avec lissage CatmullRom pour éviter
            # un angle aigu au point de jonction (§1.4 angle ≤ 45°).
            # Points de contrôle : A, midpoint_A-detour, detour, midpoint_detour-B, B
            m1 = [(c_a[0] + detour_point[0]) / 2, (c_a[1] + detour_point[1]) / 2]
            m2 = [(detour_point[0] + c_b[0]) / 2, (detour_point[1] + c_b[1]) / 2]
            ctrl = [c_a, m1, detour_point, m2, c_b]
            # Extension virtuelle pour CatmullRom
            ext = [ctrl[0]] + ctrl + [ctrl[-1]]
            smoothed: List[List[float]] = []
            segs = len(ext) - 3
            for k in range(INTERZONE_POINTS_OUT):
                u = (k / (INTERZONE_POINTS_OUT - 1)) * segs
                seg_i = int(min(segs - 1, max(0, math.floor(u))))
                t = u - seg_i
                p0, p1, p2, p3 = ext[seg_i], ext[seg_i + 1], ext[seg_i + 2], ext[seg_i + 3]
                # CatmullRom centripète simplifiée (alpha=0.5)
                t2 = t * t
                t3 = t2 * t
                pt_lat = 0.5 * ((2 * p1[0])
                                + (-p0[0] + p2[0]) * t
                                + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                                + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                pt_lng = 0.5 * ((2 * p1[1])
                                + (-p0[1] + p2[1]) * t
                                + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                                + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                smoothed.append([pt_lat, pt_lng])
            smoothed[0] = list(c_a)
            smoothed[-1] = list(c_b)
            straight = smoothed
        else:
            straight = _build_straight_path(c_a, c_b, INTERZONE_POINTS_OUT)
    else:
        straight = _build_straight_path(c_a, c_b, INTERZONE_POINTS_OUT)

    amp = min(18.0, max(5.0, length * 0.018))   # réduite pour préserver angles
    curved = _add_biological_curvature(straight, seed=seed, amplitude_m=amp)

    # Clip au rayon fonctionnel institutionnel (§2.4)
    if waypoint is not None:
        curved = _clip_path_to_functional_radius(
            curved, waypoint, INTERZONE_FUNCTIONAL_RADIUS_MAX_M,
        )
        if len(curved) < 4:
            return None
        curved = _resample_uniform_n(curved, INTERZONE_POINTS_OUT)

    final_len = 0.0
    for i in range(1, len(curved)):
        final_len += _distance_m(curved[i - 1], curved[i])
    if final_len < INTERZONE_MIN_LENGTH_M:
        return None

    cid = f"interzone_{species}_{a['type']}_{str(a['id'])[:12]}__{b['type']}_{str(b['id'])[:12]}"
    return {
        "id": cid,
        "path": curved,
        "species": species,
        "species_profile": species,
        "interzone_generated": True,
        "interzone_pair": [a["type"], b["type"]],
        "interzone_affinity": affinity,
        "interzone_length_m": round(final_len, 1),
        "hierarchy": "interzone_vital",
    }


def _build_entering_corridors(zone_anchors: Dict[str, List[Dict[str, Any]]],
                                waypoint: List[float],
                                species: str) -> List[Dict[str, Any]]:
    """Génère des corridors 'entrants' depuis 800-1500 m vers les zones vitales
    (migration/déplacement longue distance)."""
    if not ENTERING_CORRIDORS_ENABLED.get(species, False):
        return []
    # priorité : alimentation, rut, repos (cibles migratoires)
    targets: List[Dict[str, Any]] = []
    for ztype in ("alimentation", "rut", "repos"):
        for a in zone_anchors.get(ztype, []):
            targets.append(a)
    if not targets:
        return []
    out: List[Dict[str, Any]] = []
    mid_dist = (ENTERING_DISTANCE_MIN_M + ENTERING_DISTANCE_MAX_M) / 2  # ≈ 665 m
    for bi in range(ENTERING_NB_BEARINGS):
        bearing = (360.0 / ENTERING_NB_BEARINGS) * bi  # 0, 90, 180, 270
        origin = _point_at_bearing(waypoint, bearing, mid_dist)
        # cible = zone vitale la plus alignée dans ce bearing
        best_target = None
        best_align = -999.0
        for t in targets:
            br = _bearing_deg(origin, t["center"])
            align = math.cos(math.radians(br - (bearing + 180) % 360))  # veut aller vers centre
            if align > best_align:
                best_align = align
                best_target = t
        if best_target is None:
            continue
        seed = bi * 31 + hash(species) % 97
        corridor = _build_interzone_corridor(
            {"id": f"extern_{bearing:.0f}", "center": origin, "type": "migration"},
            best_target,
            species,
            affinity=0.60,
            seed=seed,
            waypoint=waypoint,
        )
        if corridor is not None:
            corridor["id"] = f"entering_{species}_brg{int(bearing)}_to_{best_target['type']}"
            corridor["entering_corridor"] = True
            corridor["entering_bearing_deg"] = bearing
            corridor["entering_distance_m"] = round(mid_dist, 0)
            corridor["hierarchy"] = "migration_entrante"
            out.append(corridor)
    return out


def generate_interzone_corridors(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Génère les corridors inter-zones + entrants pour le bundle.

    Retourne la LISTE des nouveaux corridors à fusionner avec ceux de V30.
    Ne mute PAS le bundle.
    """
    # P22ΩSPECIES_LAYER_DIVERGENCEΩ_V2 · 2026-05-13 · STEEVE-MAX
    # Normalisation alias → canon interzone (4 entrées natives + 5 alias) :
    #   chevreuil      → cerf
    #   ours_noir      → ours
    #   dindon_sauvage → dindon
    #   coyote, wapiti → orignal (fallback générique mais explicite)
    _SP_RAW = str(bundle.get("species") or "orignal").lower()
    _SP_ALIAS = {
        "cerf": "cerf", "chevreuil": "cerf",
        "orignal": "orignal", "wapiti": "orignal",
        "ours": "ours", "ours_noir": "ours",
        "dindon": "dindon", "dindon_sauvage": "dindon",
        "coyote": "orignal",  # canidé fallback explicite (pas natif AFFINITY_MATRIX)
    }
    species = _SP_ALIAS.get(_SP_RAW, "orignal")
    affinity_map = AFFINITY_MATRIX.get(species) or AFFINITY_MATRIX["orignal"]
    zones = bundle.get("zones") or []
    salines = bundle.get("salines") or []
    waypoint = bundle.get("waypoint") or {}
    wp = [float(waypoint.get("lat") or 0.0), float(waypoint.get("lng") or waypoint.get("lon") or 0.0)]

    zone_anchors = _extract_zone_anchors(zones)
    saline_anchors = _extract_saline_anchors(salines)
    # incorporer salines dans la map d'ancrages typés
    if saline_anchors:
        zone_anchors["saline"] = saline_anchors

    out_corridors: List[Dict[str, Any]] = []
    seed_counter = 0

    # 1) Connexions inter-zones selon matrice d'affinité
    for (type_a, type_b), affinity in affinity_map.items():
        if affinity < 0.30:
            continue
        anchors_a = zone_anchors.get(type_a, [])
        anchors_b = zone_anchors.get(type_b, [])
        if not anchors_a or not anchors_b:
            continue
        for a in anchors_a:
            for b in anchors_b:
                if a is b:
                    continue
                # éviter doublons symétriques si même type
                if type_a == type_b and str(a["id"]) >= str(b["id"]):
                    continue
                corridor = _build_interzone_corridor(
                    a, b, species, affinity, seed_counter, waypoint=wp,
                )
                seed_counter += 1
                if corridor is not None:
                    out_corridors.append(corridor)

    # 2) Corridors entrants depuis l'extérieur (migration)
    entering = _build_entering_corridors(zone_anchors, wp, species)
    out_corridors.extend(entering)

    return out_corridors


def apply_interzone_omega_to_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Ajoute les corridors inter-zones au bundle.

    Pipeline :  V30_corridors  +  interzone_corridors  →  veineux_omega  →  renduomega

    Fail-soft : si autorisation absente, passe inchangé.
    """
    if not isinstance(bundle, dict):
        return bundle
    if not is_interzone_authorized()["authorized"]:
        bundle["interzone_omega_applied"] = False
        return bundle

    new_corridors = generate_interzone_corridors(bundle)

    existing = bundle.get("corridors") or []
    bundle["corridors"] = list(existing) + new_corridors
    bundle["interzone_omega_applied"] = True
    bundle["interzone_omega_stats"] = {
        "existing_v30": len(existing),
        "interzone_added": sum(1 for c in new_corridors if not c.get("entering_corridor")),
        "entering_added": sum(1 for c in new_corridors if c.get("entering_corridor")),
        "total_after": len(bundle["corridors"]),
        "species": bundle.get("species"),
    }
    return bundle
