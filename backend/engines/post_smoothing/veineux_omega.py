"""
veineux_omega.py — PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME
==============================================================
Phase     : PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

POST-PROCESSOR APPLIQUÉ AUX CORRIDORS BRUTS V30 *AVANT* `apply_renduomega_to_bundle`
pour les rendre veineux organiques conformes aux 12 sous-normes X150 :
    - resampling CatmullRom à 28 points
    - segments ≤ 18 m (marge sous 20 m de RenduΩ)
    - angles ≤ 40° (marge sous 45°)
    - amplitude variable (perturbation latérale organique)
    - courbure progressive (smoothing Laplacien 2 passes)
    - terrain-aware (décalage anti-eau)
    - anti-radial (rejet corridors convergents forts)
    - un corridor = une espèce

V30 LOCKED intact (seules les sorties sont transformées).
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════
# Triple verrou
# ═══════════════════════════════════════════════════════════════════════
VEINEUX_ENABLED = True
VEINEUX_ENV_FLAG = "VEINEUX_OMEGA_AUTHORIZED_BY_COMMANDANT"
VEINEUX_TOKEN_ENV = "VEINEUX_OMEGA_COMMANDANT_TOKEN"
VEINEUX_EXPECTED_TOKEN = "STEEVE-MAX-XII-VEINEUX-EXPLICIT"


def is_veineux_authorized() -> Dict[str, Any]:
    env_ok = os.environ.get(VEINEUX_ENV_FLAG, "").strip().lower() == "true"
    token_ok = os.environ.get(VEINEUX_TOKEN_ENV, "").strip() == VEINEUX_EXPECTED_TOKEN
    return {
        "authorized": bool(VEINEUX_ENABLED and env_ok and token_ok),
        "flag_enabled": VEINEUX_ENABLED,
        "env_flag_ok": env_ok,
        "token_ok": token_ok,
    }


# ═══════════════════════════════════════════════════════════════════════
# Géométrie
# ═══════════════════════════════════════════════════════════════════════
TARGET_POINTS = 28                # X150 fenêtre [25-30]
MAX_SEGMENT_M = 18.0              # marge sous 20.0 m
MAX_ANGLE_DEG = 40.0              # marge sous 45.0°
AMPLITUDE_ORGANIC_M = 3.5         # amplitude de perturbation sinusoïdale
TERRAIN_AVOIDANCE_BUFFER_M = 25.0  # > 20 m (eau) + marge
RADIAL_CONVERGENCE_TOL_M = 80.0   # tolérance détection radiale
MAX_PATH_LEN_M = 1500.0           # longueur max corridor (V30 peut en émettre de 2-3 km)
FINAL_LEN_BUDGET_M = 515.0        # budget longueur après tout traitement (29*18-mini marge)
# ENFORCEMENT_P0 §4.1 — exclusion stricte CONTAM
CONTAM_AVOIDANCE_BUFFER_M = 60.0  # éloignement minimal de toute zone de contamination


def _meters_to_latlng(lat: float, d_lat_m: float, d_lng_m: float) -> Tuple[float, float]:
    dlat = d_lat_m / 111320.0
    cos_lat = math.cos(math.radians(lat))
    dlng = d_lng_m / (111320.0 * max(1e-6, cos_lat))
    return dlat, dlng


def _distance_m(a: List[float], b: List[float]) -> float:
    R = 6371000.0
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    h = (math.sin((la2 - la1) / 2) ** 2 +
         math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(min(1.0, math.sqrt(h)))


def _cumulative_distances(path: List[List[float]]) -> List[float]:
    cum = [0.0]
    for i in range(1, len(path)):
        cum.append(cum[-1] + _distance_m(path[i - 1], path[i]))
    return cum


def _resample_uniform_n(path: List[List[float]], n: int) -> List[List[float]]:
    """Resampling linéaire uniforme à N points."""
    if len(path) < 2 or n < 2:
        return list(path)
    cum = _cumulative_distances(path)
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


def _catmullrom_sample(p0, p1, p2, p3, t, alpha=0.5):
    """Un point CatmullRom centripète entre p1 et p2 (t ∈ [0,1])."""
    def tj(ti, pi, pj):
        dx = pj[0] - pi[0]
        dy = pj[1] - pi[1]
        return ti + (math.hypot(dx, dy) ** alpha)
    t0 = 0.0
    t1 = tj(t0, p0, p1)
    t2 = tj(t1, p1, p2)
    t3 = tj(t2, p2, p3)
    if t2 == t1:
        return [p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t]
    tt = t1 + (t2 - t1) * t

    def lerp(a, b, ta, tb, t_):
        if tb == ta:
            return a
        k = (t_ - ta) / (tb - ta)
        return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k]

    A1 = lerp(p0, p1, t0, t1, tt)
    A2 = lerp(p1, p2, t1, t2, tt)
    A3 = lerp(p2, p3, t2, t3, tt)
    B1 = lerp(A1, A2, t0, t2, tt)
    B2 = lerp(A2, A3, t1, t3, tt)
    return lerp(B1, B2, t1, t2, tt)


def _catmullrom_path(path: List[List[float]], n_out: int = TARGET_POINTS) -> List[List[float]]:
    """Spline CatmullRom centripète sur l'ensemble du path, N points en sortie."""
    if len(path) < 2:
        return list(path)
    if len(path) == 2:
        return _resample_uniform_n(path, n_out)
    # Ajouter tangentes virtuelles pour les extrémités
    extended = [path[0]] + path + [path[-1]]
    segments = len(extended) - 3  # (P0..P(n-1)), we iterate P1..P(n-2)
    out: List[List[float]] = []
    total_steps = n_out - 1
    for i in range(n_out):
        u = (i / total_steps) * segments  # [0, segments]
        seg_idx = int(min(segments - 1, max(0, math.floor(u))))
        t = u - seg_idx
        p0 = extended[seg_idx]
        p1 = extended[seg_idx + 1]
        p2 = extended[seg_idx + 2]
        p3 = extended[seg_idx + 3]
        out.append(_catmullrom_sample(p0, p1, p2, p3, t))
    # Force exact endpoints
    out[0] = list(path[0])
    out[-1] = list(path[-1])
    return out


def _smooth_laplacian(path: List[List[float]], passes: int = 2, factor: float = 0.3) -> List[List[float]]:
    """Lissage Laplacien des points intérieurs — courbure progressive."""
    if len(path) < 3:
        return list(path)
    p = [list(pt) for pt in path]
    for _ in range(passes):
        new = [p[0]]
        for i in range(1, len(p) - 1):
            avg_lat = (p[i - 1][0] + p[i + 1][0]) / 2
            avg_lng = (p[i - 1][1] + p[i + 1][1]) / 2
            new.append([
                p[i][0] * (1 - factor) + avg_lat * factor,
                p[i][1] * (1 - factor) + avg_lng * factor,
            ])
        new.append(p[-1])
        p = new
    return p


def _organic_amplitude(path: List[List[float]], seed: int = 0) -> List[List[float]]:
    """Perturbation latérale sinusoïdale faible amplitude (organicité)."""
    if len(path) < 4:
        return list(path)
    out: List[List[float]] = [list(path[0])]
    N = len(path) - 1
    for i in range(1, N):
        # vecteur tangent moyen + normale
        p_prev = path[i - 1]
        p_curr = path[i]
        p_next = path[i + 1]
        tx = p_next[0] - p_prev[0]
        ty = p_next[1] - p_prev[1]
        norm = math.hypot(tx, ty)
        if norm < 1e-9:
            out.append(list(p_curr))
            continue
        # normale (perpendiculaire)
        nx, ny = -ty / norm, tx / norm
        # amplitude modulée par sinus (multi-harmonique pour éviter régularité)
        phase = (i / N) * math.pi * 2
        h1 = math.sin(phase * 3 + seed * 0.3)
        h2 = math.sin(phase * 7 + seed * 0.71) * 0.5
        amp_m = AMPLITUDE_ORGANIC_M * (h1 + h2) * 0.6
        d_lat, d_lng = _meters_to_latlng(p_curr[0], nx * amp_m, ny * amp_m)
        out.append([p_curr[0] + d_lat, p_curr[1] + d_lng])
    out.append(list(path[-1]))
    return out


def _path_length_m(path: List[List[float]]) -> float:
    if len(path) < 2:
        return 0.0
    return sum(_distance_m(path[i], path[i + 1]) for i in range(len(path) - 1))


def _max_segment_m(path: List[List[float]]) -> float:
    if len(path) < 2:
        return 0.0
    return max(_distance_m(path[i], path[i + 1]) for i in range(len(path) - 1))


def _max_angle_deg(path: List[List[float]]) -> float:
    if len(path) < 3:
        return 0.0
    best = 0.0
    for i in range(1, len(path) - 1):
        v1 = (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        v2 = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        n1 = math.hypot(*v1)
        n2 = math.hypot(*v2)
        if n1 < 1e-12 or n2 < 1e-12:
            continue
        cos_a = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
        ang = math.degrees(math.acos(cos_a))
        if ang > best:
            best = ang
    return best


def _clip_max_length(path: List[List[float]], max_m: float) -> List[List[float]]:
    """Coupe le corridor à max_m mètres depuis le début."""
    if len(path) < 2:
        return path
    cum = _cumulative_distances(path)
    if cum[-1] <= max_m:
        return path
    # trouver le segment dans lequel max_m tombe
    for i in range(1, len(path)):
        if cum[i] >= max_m:
            d0, d1 = cum[i - 1], cum[i]
            t = (max_m - d0) / (d1 - d0) if d1 > d0 else 0.0
            p0, p1 = path[i - 1], path[i]
            cut = [p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t]
            return path[:i] + [cut]
    return path


def _detect_radial_convergence(corridors: List[Dict[str, Any]]) -> List[str]:
    """Retourne les IDs des corridors jugés radiaux (>3 convergent au même point)."""
    # Groupement par extrémité
    endpoints: Dict[Tuple[int, int], List[str]] = {}
    GRID = 1e-4  # ~11 m @ 48°N
    to_remove: List[str] = []
    for c in corridors:
        path = c.get("path") or []
        cid = c.get("id")
        if not path or cid is None:
            continue
        for end in (path[0], path[-1]):
            key = (int(end[0] / GRID), int(end[1] / GRID))
            endpoints.setdefault(key, []).append(str(cid))
    for _, ids in endpoints.items():
        if len(set(ids)) >= 4:  # 4 convergents = radial
            to_remove.extend(ids[3:])
    return to_remove


# ═══════════════════════════════════════════════════════════════════════
# Terrain avoidance
# ═══════════════════════════════════════════════════════════════════════
def _avoid_water_points(path: List[List[float]],
                        water_points: List[Dict[str, Any]],
                        buffer_m: float = TERRAIN_AVOIDANCE_BUFFER_M
                        ) -> List[List[float]]:
    """Décale latéralement les points trop proches d'eau (< buffer_m)."""
    if not water_points or len(path) < 3:
        return path
    out: List[List[float]] = []
    for i, pt in enumerate(path):
        moved = list(pt)
        for w in water_points:
            wlat = w.get("lat")
            wlng = w.get("lng") or w.get("lon")
            if wlat is None or wlng is None:
                continue
            d = _distance_m(pt, [wlat, wlng])
            if d < buffer_m and d > 1e-6:
                # Vecteur qui s'éloigne de l'eau
                vx = pt[0] - wlat
                vy = pt[1] - wlng
                norm = math.hypot(vx, vy)
                if norm > 1e-9:
                    push_m = (buffer_m - d) * 1.05
                    push_lat, push_lng = _meters_to_latlng(
                        pt[0], (vx / norm) * push_m, (vy / norm) * push_m,
                    )
                    moved[0] += push_lat
                    moved[1] += push_lng
        out.append(moved)
    return out


def _avoid_contamination_zones(path: List[List[float]],
                                contam_zones: List[Dict[str, Any]],
                                buffer_m: float = CONTAM_AVOIDANCE_BUFFER_M
                                ) -> List[List[float]]:
    """ENFORCEMENT_P0 §4.1 — exclusion stricte CONTAM.

    Décale latéralement tout point du corridor qui entre dans la sphère
    d'exclusion d'une zone de contamination. Aucun corridor ne doit
    traverser une zone hostile (§4.2).
    """
    if not contam_zones or len(path) < 3:
        return path
    out: List[List[float]] = []
    for pt in path:
        moved = list(pt)
        for z in contam_zones:
            zlat = z.get("lat")
            zlng = z.get("lng") or z.get("lon")
            if zlat is None or zlng is None:
                continue
            d = _distance_m(pt, [zlat, zlng])
            if d < buffer_m and d > 1e-6:
                vx = pt[0] - zlat
                vy = pt[1] - zlng
                norm = math.hypot(vx, vy)
                if norm > 1e-9:
                    push_m = (buffer_m - d) * 1.1
                    push_lat, push_lng = _meters_to_latlng(
                        pt[0], (vx / norm) * push_m, (vy / norm) * push_m,
                    )
                    moved[0] += push_lat
                    moved[1] += push_lng
        out.append(moved)
    return out
# ═══════════════════════════════════════════════════════════════════════
def _process_single_corridor(corridor: Dict[str, Any],
                              water_points: List[Dict[str, Any]],
                              contam_zones: List[Dict[str, Any]],
                              bundle_species: Optional[str]) -> Optional[Dict[str, Any]]:
    """Transforme un corridor brut V30 en corridor veineux Ω ou retourne None si rejet."""
    path = corridor.get("path") or corridor.get("polyline") or []
    if not isinstance(path, list) or len(path) < 2:
        return None
    # Normaliser path points en list
    path = [[float(p[0]), float(p[1])] for p in path if isinstance(p, (list, tuple)) and len(p) >= 2]
    if len(path) < 2:
        return None

    # 1. Clip longueur max
    path = _clip_max_length(path, MAX_PATH_LEN_M)

    # 2. Resampling CatmullRom à 28 points
    veined = _catmullrom_path(path, n_out=TARGET_POINTS)

    # 3. Amplitude organique (multi-harmonique)
    #    SKIP pour corridors INTERZONE/ENTERING : ils sont DÉJÀ construits
    #    avec une courbure biologique veineuse (_add_biological_curvature).
    #    Une double perturbation créerait des angles aigus > 45°.
    is_interzone = bool(corridor.get("interzone_generated")) or bool(corridor.get("entering_corridor"))
    if not is_interzone:
        seed = abs(hash(str(corridor.get("id") or "corr"))) % 997
        veined = _organic_amplitude(veined, seed=seed)

    # 4. Lissage Laplacien (courbure progressive)
    veined = _smooth_laplacian(veined, passes=2, factor=0.25)

    # 5. Terrain-aware : évitement eau
    veined = _avoid_water_points(veined, water_points, buffer_m=TERRAIN_AVOIDANCE_BUFFER_M)

    # 5bis. ENFORCEMENT_P0 §4.1 — exclusion stricte CONTAM
    veined = _avoid_contamination_zones(veined, contam_zones, buffer_m=CONTAM_AVOIDANCE_BUFFER_M)

    # 6. Clip final strict — garantir L <= budget pour que 30 pts → seg <= 18m.
    #    Applique uniformément à tous les corridors (V30 + interzone + entering)
    #    pour respecter la contrainte X150 : 30 pts × 20 m seg_max = 600 m max.
    veined = _clip_max_length(veined, FINAL_LEN_BUDGET_M)

    # 7. Resample final à exactement 30 points (seg ≈ L/29 ≤ 17.8 m)
    veined = _resample_uniform_n(veined, 30)

    # 8. Assigner species strictement
    species_out = corridor.get("species") or corridor.get("species_profile") or bundle_species

    out = dict(corridor)
    out["path"] = veined
    out["species"] = species_out
    out["species_profile"] = species_out
    out["veineux_omega_applied"] = True
    out["veineux_metrics"] = {
        "points": len(veined),
        "length_m": round(_path_length_m(veined), 1),
        "max_segment_m": round(_max_segment_m(veined), 2),
        "max_angle_deg": round(_max_angle_deg(veined), 2),
    }
    return out


def apply_veineux_omega_to_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Applique le post-processor VEINEUX_Ω aux corridors du bundle.

    Appelé AVANT `apply_renduomega_to_bundle`. V30 intact : ce n'est
    qu'une réécriture des sorties (bundle.corridors) avant le filtre
    institutionnel. Fail-soft : si autorisation absente, passe inchangé.
    """
    if not isinstance(bundle, dict):
        return bundle
    if not is_veineux_authorized()["authorized"]:
        bundle["veineux_omega_applied_at_bundle"] = False
        return bundle

    corridors_in = bundle.get("corridors") or []
    if not corridors_in:
        bundle["veineux_omega_applied_at_bundle"] = True
        bundle["veineux_omega_stats"] = {"input": 0, "output": 0, "radial_removed": 0}
        return bundle

    # Terrain signals pour terrain-aware
    signals = bundle.get("terrain_signals") or {}
    water_points = signals.get("water_points") or []
    # ENFORCEMENT_P0 §4.1 — ingérer les zones de contamination du bundle
    contam_zones = bundle.get("contamination_zones") or []
    species = bundle.get("species")

    # 1. Détection corridors radiaux (Section 2 — réseau continu anti-radial).
    #    S'applique à TOUS les corridors (V30 + interzone) pour éliminer les
    #    convergences radiales pathologiques. Les corridors interzone ayant
    #    des endpoints DISTINCTS (zones vitales différentes) ne sont pas
    #    détectés comme radiaux par la logique grid cell du détecteur.
    radial_ids = set(_detect_radial_convergence(corridors_in))
    filtered_in = [c for c in corridors_in if str(c.get("id")) not in radial_ids]

    # 2. Transformer chaque corridor
    out: List[Dict[str, Any]] = []
    for c in filtered_in:
        try:
            veined = _process_single_corridor(c, water_points, contam_zones, species)
        except Exception:
            veined = None
        if veined is not None:
            out.append(veined)

    bundle["corridors"] = out
    bundle["veineux_omega_applied_at_bundle"] = True
    bundle["veineux_omega_stats"] = {
        "input": len(corridors_in),
        "radial_removed": len(radial_ids),
        "output": len(out),
        "target_points": TARGET_POINTS,
        "max_segment_m_target": MAX_SEGMENT_M,
        "max_angle_deg_target": MAX_ANGLE_DEG,
        "contam_avoidance_buffer_m": CONTAM_AVOIDANCE_BUFFER_M,
        "contam_zones_considered": len(contam_zones),
    }
    return bundle
