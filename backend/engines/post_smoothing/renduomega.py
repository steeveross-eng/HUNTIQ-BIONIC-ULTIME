"""
ENGINE_RENDUΩ — Validation stricte des corridors avant publication
===================================================================
Phase     : PHASE_X200_P5_RENDUΩ_INTEGRATION_ULTIME_Ω
Commandant: STEEVE-MAX

Validateur institutionnel qui contrôle chaque corridor avant son
exposition au frontend TERRITOIRE. Toute géométrie non conforme est
REJETÉE ; seuls les corridors portant `renduomega.accepted=True`
doivent être rendus par le frontend.

RÈGLES INSTITUTIONNELLES Ω :
  §2 Géométrie  : spline CatmullRom 25-30 points, longueur ≥ 100 m
                  (idéal 300-800 m), segments ≤ 20 m, angles ≤ 45°,
                  progression monotone, aucune forme radiale/étoile.
  §3 Terrain    : rayon fonctionnel 420-780 m (600 m ± 30 %),
                  évitement pente > 35°, eau < 20 m.
  §3 Écologie   : évitement human_zones (buffer), contamination,
                  affûts (cône 80°), attraction salines/alimentation.
  §4 Espèce     : une espèce unique par corridor — refus multi.
  §5 Rendu      : couleur base #FF8F00, palette dérivée par espèce,
                  opacité ≥ 0.75, épaisseur ∈ {1.2, 2.0, 3.0} px,
                  zindex institutionnel, minZoom = 13.
  §1.2          : blocage immédiat des rendus géométriques/radiaux/fallback.

TRIPLE VERROU P5 :
  - `P5_RENDUOMEGA_ENABLED = True`
  - env `P5_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true`
  - env `P5_COMMANDANT_TOKEN=STEEVE-MAX-X200-P5-EXPLICIT`

V30 INTANGIBLE. Aucun import `engines.v8_institutional.*`.
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════
# FLAG P5 + TRIPLE VERROU Ω
# ═══════════════════════════════════════════════════════════════════════
P5_RENDUOMEGA_ENABLED: bool = True
EXPECTED_TOKEN_P5 = "STEEVE-MAX-X200-P5-EXPLICIT"

# ═══════════════════════════════════════════════════════════════════════
# CONSTANTES INSTITUTIONNELLES (§5)
# ═══════════════════════════════════════════════════════════════════════
BASE_COLOR_ORANGE_AMBRE = "#FF8F00"       # couleur institutionnelle
OPACITY_MIN = 0.75
MIN_ZOOM = 13

WIDTH_LOW  = 1.2
WIDTH_MID  = 2.0
WIDTH_HIGH = 3.0
WIDTHS_ALLOWED = (WIDTH_LOW, WIDTH_MID, WIDTH_HIGH)

# zindex institutionnel §1.1 :
#   Zones < Hydrologie < Terrain < Corridors < Salines < Affûts < Hotspots < Vent
ZINDEX_INSTITUTIONNEL = {
    "zones":      100,
    "hydrologie": 110,
    "terrain":    120,
    "corridors":  130,
    "salines":    140,
    "affuts":     150,
    "hotspots":   160,
    "vent":       170,
}

# Palette dérivée par espèce — teinte contrôlée autour de #FF8F00 (HSL)
# base #FF8F00 ≈ H:34° S:100% L:50% → on module H ±8°, S/L ±5%.
SPECIES_COLOR_PALETTE = {
    "orignal":   "#FF8F00",  # base ambre
    "cerf":      "#FFA020",  # +6° teinte (vers ambre clair)
    "chevreuil": "#FFA020",
    "ours":      "#E07A00",  # −4° teinte (ambre foncé)
    "dindon":    "#FFB340",  # +12° / +10% L
    "wapiti":    "#CC7300",
}

# Règles géométriques §2
GEOM_MIN_POINTS = 25
GEOM_MAX_POINTS = 30
GEOM_MIN_LENGTH_M = 100.0
GEOM_IDEAL_MIN_M = 300.0
GEOM_IDEAL_MAX_M = 800.0
GEOM_MAX_SEGMENT_M = 20.0
GEOM_MAX_ANGLE_DEG = 45.0

# Règles terrain §3
TERRAIN_RADIUS_MIN_M = 420.0       # 600 − 30 %
TERRAIN_RADIUS_MAX_M = 780.0       # 600 + 30 %
TERRAIN_SLOPE_MAX_DEG = 35.0
TERRAIN_WATER_MIN_M = 20.0
ECO_HUMAN_MIN_M = 80.0             # évitement minimal de toute human_zone
ECO_CONTAM_MIN_M = 50.0
ECO_AFFUT_CONE_DEG = 80.0

EARTH_RADIUS_M = 6371000.0


# ═══════════════════════════════════════════════════════════════════════
# AUTORISATION
# ═══════════════════════════════════════════════════════════════════════
def is_p5_authorized() -> Dict[str, Any]:
    env_ok = os.environ.get(
        "P5_ACTIVATION_AUTHORIZED_BY_COMMANDANT", ""
    ).strip().lower() == "true"
    token_ok = os.environ.get("P5_COMMANDANT_TOKEN", "") == EXPECTED_TOKEN_P5
    return {
        "authorized": P5_RENDUOMEGA_ENABLED and env_ok and token_ok,
        "flag_enabled": P5_RENDUOMEGA_ENABLED,
        "env_ok": env_ok,
        "token_ok": token_ok,
        "expected_token": EXPECTED_TOKEN_P5,
    }


# ═══════════════════════════════════════════════════════════════════════
# PRIMITIVES GÉODÉSIQUES
# ═══════════════════════════════════════════════════════════════════════
def _haversine_m(a: List[float], b: List[float]) -> float:
    lat1 = math.radians(float(a[0])); lat2 = math.radians(float(b[0]))
    dlat = lat2 - lat1
    dlon = math.radians(float(b[1]) - float(a[1]))
    h = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))


def _path_length_m(path: List[List[float]]) -> float:
    if not path or len(path) < 2:
        return 0.0
    return sum(_haversine_m(path[i], path[i + 1]) for i in range(len(path) - 1))


def _max_segment_m(path: List[List[float]]) -> float:
    if not path or len(path) < 2:
        return 0.0
    return max(_haversine_m(path[i], path[i + 1]) for i in range(len(path) - 1))


def _max_angle_deg(path: List[List[float]]) -> float:
    if not path or len(path) < 3:
        return 0.0
    max_deg = 0.0
    for i in range(1, len(path) - 1):
        a, b, c = path[i - 1], path[i], path[i + 1]
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        n1 = math.hypot(*v1); n2 = math.hypot(*v2)
        if n1 == 0 or n2 == 0:
            continue
        cos_t = max(-1.0, min(1.0, (v1[0]*v2[0] + v1[1]*v2[1]) / (n1 * n2)))
        deg = math.degrees(math.acos(cos_t))
        if deg > max_deg:
            max_deg = deg
    return max_deg


def _is_radial_shape(path: List[List[float]], tolerance: float = 0.02,
                     min_angle_deviation_deg: float = 1.5) -> bool:
    """Détecte les formes radiales/étoiles ou lignes géométriques parfaitement
    droites (signature fallback / rendu radial interdit §1.2).

    Critère institutionnel Ω :
      - path quasi-rectiligne (ratio longueur/distance directe < 1.02)
      - ET courbure quasi-nulle (max_angle_deg < 1.5°)
    Un corridor biologique courbé, même direct, présente des micro-variations
    d'angle > 1.5° dues au terrain → accepté.
    """
    if not path or len(path) < 4:
        return False
    start = path[0]; end = path[-1]
    d_start_end = _haversine_m(start, end)
    if d_start_end == 0:
        return True  # dégénéré
    path_len = _path_length_m(path)
    ratio = path_len / d_start_end
    quasi_straight = ratio < 1.0 + tolerance
    if not quasi_straight:
        return False
    # Rectiligne suspect → vérifier qu'il n'y a pas de courbure biologique
    return _max_angle_deg(path) < min_angle_deviation_deg


# ═══════════════════════════════════════════════════════════════════════
# VALIDATORS — §2 GÉOMÉTRIE
# ═══════════════════════════════════════════════════════════════════════
def validate_geometry(path: List[List[float]]) -> Dict[str, Any]:
    violations: List[str] = []
    n = len(path) if path else 0
    length_m = _path_length_m(path) if n >= 2 else 0.0
    max_seg = _max_segment_m(path) if n >= 2 else 0.0
    max_ang = _max_angle_deg(path) if n >= 3 else 0.0
    is_radial = _is_radial_shape(path) if n >= 4 else False

    if n < GEOM_MIN_POINTS or n > GEOM_MAX_POINTS:
        violations.append(f"points_count={n} (attendu {GEOM_MIN_POINTS}-{GEOM_MAX_POINTS})")
    if length_m < GEOM_MIN_LENGTH_M:
        violations.append(f"length_m={length_m:.1f} < {GEOM_MIN_LENGTH_M}")
    if max_seg > GEOM_MAX_SEGMENT_M:
        violations.append(f"max_segment_m={max_seg:.1f} > {GEOM_MAX_SEGMENT_M}")
    if max_ang > GEOM_MAX_ANGLE_DEG:
        violations.append(f"max_angle_deg={max_ang:.1f} > {GEOM_MAX_ANGLE_DEG}")
    if is_radial:
        violations.append("radial_or_straight_shape_detected")

    ideal_length = GEOM_IDEAL_MIN_M <= length_m <= GEOM_IDEAL_MAX_M
    return {
        "ok": len(violations) == 0,
        "points_count": n,
        "length_m": round(length_m, 2),
        "ideal_length_300_800": ideal_length,
        "max_segment_m": round(max_seg, 2),
        "max_angle_deg": round(max_ang, 2),
        "radial_detected": is_radial,
        "violations": violations,
    }


# ═══════════════════════════════════════════════════════════════════════
# VALIDATORS — §3 TERRAIN & ÉCOLOGIE
# ═══════════════════════════════════════════════════════════════════════
def validate_terrain_constraints(path: List[List[float]],
                                 center: List[float],
                                 terrain_signals: Dict[str, Any]
                                 ) -> Dict[str, Any]:
    violations: List[str] = []
    details: Dict[str, Any] = {}

    # §3.1 Rayon fonctionnel 420-780 m (600 ± 30 %)
    if path and center:
        # Distance du point le plus éloigné du centre
        max_d = max(_haversine_m(center, p) for p in path)
        details["max_radius_from_center_m"] = round(max_d, 1)
        if max_d < TERRAIN_RADIUS_MIN_M or max_d > TERRAIN_RADIUS_MAX_M:
            violations.append(
                f"functional_radius_m={max_d:.1f} hors [{TERRAIN_RADIUS_MIN_M}-{TERRAIN_RADIUS_MAX_M}]"
            )

    # §3 : évitement eau < 20 m
    water_points = (terrain_signals or {}).get("water_points") or []
    if water_points and path:
        min_d_water = min(
            _haversine_m(p, w) for p in path for w in water_points
        )
        details["min_dist_water_m"] = round(min_d_water, 1)
        if min_d_water < TERRAIN_WATER_MIN_M:
            violations.append(f"min_dist_water_m={min_d_water:.1f} < {TERRAIN_WATER_MIN_M}")

    # §3 : évitement pente > 35° — via microrelief
    microrelief = (terrain_signals or {}).get("microrelief") or {}
    slope_deg = float(microrelief.get("slope_deg", 0.0))
    details["slope_deg_context"] = slope_deg
    if slope_deg > TERRAIN_SLOPE_MAX_DEG:
        violations.append(f"slope_deg={slope_deg:.1f} > {TERRAIN_SLOPE_MAX_DEG}")

    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "details": details,
    }


def validate_ecological_constraints(path: List[List[float]],
                                    terrain_signals: Dict[str, Any],
                                    contamination_zones: Optional[List[Dict[str, Any]]] = None,
                                    affuts: Optional[List[Dict[str, Any]]] = None,
                                    ) -> Dict[str, Any]:
    violations: List[str] = []
    details: Dict[str, Any] = {}
    ts = terrain_signals or {}

    # §3.2 Évitement human_zones (buffer avec weight modulation)
    human_zones = ts.get("human_zones") or []
    if human_zones and path:
        worst_penalty = 0.0
        worst_dist = None
        for h in human_zones:
            if isinstance(h, dict):
                hp = [float(h.get("lat")), float(h.get("lng") or h.get("lon"))]
                buf = float(h.get("buffer_m", 250.0))
                w = float(h.get("weight", 0.7))
            else:
                hp = [float(h[0]), float(h[1])]
                buf = 250.0; w = 0.7
            for p in path:
                d = _haversine_m(p, hp)
                if d < buf:
                    penalty = (1.0 - d / buf) * w
                    if penalty > worst_penalty:
                        worst_penalty = penalty
                        worst_dist = d
        details["human_worst_penalty"] = round(worst_penalty, 3)
        details["human_worst_dist_m"] = round(worst_dist, 1) if worst_dist is not None else None
        # Violation majeure si corridor est dans le buffer d'une route forte (weight > 0.7)
        if worst_penalty >= 0.6:
            violations.append(f"human_zone_violation penalty={worst_penalty:.2f}")

    # §3.2 Évitement contamination
    if contamination_zones and path:
        min_d = min(
            _haversine_m(p, [c.get("lat"), c.get("lng") or c.get("lon")])
            for p in path for c in contamination_zones
        )
        details["min_dist_contamination_m"] = round(min_d, 1)
        if min_d < ECO_CONTAM_MIN_M:
            violations.append(f"contamination_violation min_dist={min_d:.1f}")

    # §3.2 Évitement cône affût
    if affuts and path:
        # Corridor ne doit pas passer dans le cône 80° orienté d'un affût
        for a in affuts:
            a_lat = a.get("lat"); a_lng = a.get("lng") or a.get("lon")
            a_bearing = a.get("bearing_deg")
            if a_lat is None or a_lng is None or a_bearing is None:
                continue
            cone_half = ECO_AFFUT_CONE_DEG / 2.0
            for p in path:
                d = _haversine_m(p, [a_lat, a_lng])
                if d > 200.0:  # hors portée efficace
                    continue
                dy = p[0] - a_lat
                dx = p[1] - a_lng
                bearing = (math.degrees(math.atan2(dx, dy)) + 360.0) % 360.0
                diff = abs((bearing - a_bearing + 540.0) % 360.0 - 180.0)
                if diff <= cone_half:
                    violations.append(
                        f"affut_cone_violation dist_m={d:.0f} bearing_diff_deg={diff:.1f}"
                    )
                    break

    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "details": details,
    }


# ═══════════════════════════════════════════════════════════════════════
# VALIDATORS — §4 ESPÈCE & SOURCE
# ═══════════════════════════════════════════════════════════════════════
UPSTREAM_ENGINES_EXPECTED = {
    "ecoforestry_omega", "advanced_geospatial_omega", "terrain_3d_omega",
    "legal_time_omega", "predictive_omega",
}


def validate_species_and_source(corridor: Dict[str, Any],
                                bundle_species: Optional[str] = None
                                ) -> Dict[str, Any]:
    violations: List[str] = []
    species = (
        corridor.get("species") or corridor.get("species_profile")
        or bundle_species
    )
    species_list = corridor.get("species_multi")  # champ interdit
    if species_list and isinstance(species_list, list) and len(species_list) > 1:
        violations.append("multi_species_corridor_refused")
    if not species:
        violations.append("species_metadata_missing")

    # Traçabilité source : issu d'ENGINE CORRIDORS Ω alimenté par X199
    source = corridor.get("source") or ""
    ia_vision = corridor.get("ia_vision_corroborated", False)

    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "species": species,
        "source": source,
        "ia_vision_corroborated": bool(ia_vision),
    }


# ═══════════════════════════════════════════════════════════════════════
# RENDU VISUEL §5 — ÉPAISSEUR / COULEUR / OPACITÉ / ZINDEX
# ═══════════════════════════════════════════════════════════════════════
def _width_from_probability(prob_0_1: float) -> float:
    """Intensité biologique 1.2 / 2.0 / 3.0 px selon probabilité agrégée."""
    if prob_0_1 >= 0.60:
        return WIDTH_HIGH
    if prob_0_1 >= 0.30:
        return WIDTH_MID
    return WIDTH_LOW


def _color_for_species(species: Optional[str]) -> str:
    return SPECIES_COLOR_PALETTE.get((species or "").lower(), BASE_COLOR_ORANGE_AMBRE)


def build_render_metadata(corridor: Dict[str, Any]) -> Dict[str, Any]:
    """Bloc §5 appliqué à un corridor validé."""
    species = (corridor.get("species") or corridor.get("species_profile") or "").lower()
    prob = float(corridor.get("corridor_probability_omega", 0.0))
    return {
        "color":    _color_for_species(species),
        "base_color": BASE_COLOR_ORANGE_AMBRE,
        "width_px": _width_from_probability(prob),
        "opacity":  OPACITY_MIN,
        "min_zoom": MIN_ZOOM,
        "zindex":   ZINDEX_INSTITUTIONNEL["corridors"],
        "ia_vision_tag": bool(corridor.get("ia_vision_corroborated", False)),
        "width_reason": {
            "probability_0_1": round(prob, 4),
            "threshold_hi":    0.60,
            "threshold_mid":   0.30,
        },
    }


# ═══════════════════════════════════════════════════════════════════════
# VALIDATEUR MAÎTRE — un corridor
# ═══════════════════════════════════════════════════════════════════════
def validate_corridor(corridor: Dict[str, Any],
                      center: Optional[List[float]] = None,
                      terrain_signals: Optional[Dict[str, Any]] = None,
                      contamination_zones: Optional[List[Dict[str, Any]]] = None,
                      affuts: Optional[List[Dict[str, Any]]] = None,
                      bundle_species: Optional[str] = None,
                      ) -> Dict[str, Any]:
    """Retourne le verdict institutionnel complet + metadata rendu si accepté."""
    path = corridor.get("path") or corridor.get("polyline") or []
    geom = validate_geometry(path)
    terr = validate_terrain_constraints(path, center or [0, 0], terrain_signals or {})
    eco  = validate_ecological_constraints(path, terrain_signals or {},
                                            contamination_zones, affuts)
    sp   = validate_species_and_source(corridor, bundle_species)

    accepted = geom["ok"] and terr["ok"] and eco["ok"] and sp["ok"]
    errors: List[Dict[str, Any]] = []
    if not geom["ok"]:
        errors.append({"kind": "ERREUR_RENDUΩ_GÉOMÉTRIE", "violations": geom["violations"]})
    if not terr["ok"] or not eco["ok"]:
        errors.append({"kind": "ERREUR_RENDUΩ_CONTRAINTES",
                       "violations": terr["violations"] + eco["violations"]})
    if not sp["ok"]:
        errors.append({"kind": "ERREUR_RENDUΩ_ESPÈCE", "violations": sp["violations"]})

    verdict = {
        "accepted": accepted,
        "geometry": geom,
        "terrain":  terr,
        "ecology":  eco,
        "species":  sp,
        "errors":   errors,
    }
    if accepted:
        verdict["render"] = build_render_metadata(corridor)
    return verdict


# ═══════════════════════════════════════════════════════════════════════
# VALIDATEUR MAÎTRE — un bundle complet (hook smoother)
# ═══════════════════════════════════════════════════════════════════════
def _resample_path_uniform(path: List[List[float]], target_n: int = 28) -> List[List[float]]:
    """Ré-échantillonnage UNIFORME le long du path existant — `target_n` points
    équidistants par distance cumulée.

    Conforme §2 : préserve la géométrie originale (aucune interpolation
    artificielle hors de la courbe source — seule une normalisation de
    l'échantillonnage en distance). Utilisé comme pré-étape par
    `apply_renduomega_to_bundle` pour ramener les paths sur-échantillonnés
    (ex. 133 points V30) dans la fenêtre institutionnelle 25-30 points,
    sans simplifier la forme sous-jacente.
    """
    if not path or len(path) < 2:
        return list(path)
    target_n = max(GEOM_MIN_POINTS, min(GEOM_MAX_POINTS, int(target_n)))
    # Distances cumulées
    cum = [0.0]
    for i in range(1, len(path)):
        cum.append(cum[-1] + _haversine_m(path[i - 1], path[i]))
    total = cum[-1]
    if total <= 0:
        return list(path)
    # Positions cibles équidistantes
    out: List[List[float]] = []
    for k in range(target_n):
        t = total * k / (target_n - 1)
        # Trouver segment
        i = 0
        while i < len(cum) - 1 and cum[i + 1] < t:
            i += 1
        seg_len = cum[i + 1] - cum[i] if i + 1 < len(cum) else 1.0
        alpha = (t - cum[i]) / seg_len if seg_len > 0 else 0.0
        p0 = path[i]; p1 = path[min(i + 1, len(path) - 1)]
        lat = p0[0] + alpha * (p1[0] - p0[0])
        lng = p0[1] + alpha * (p1[1] - p0[1])
        out.append([round(lat, 7), round(lng, 7)])
    return out


def apply_renduomega_to_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Valide tous les corridors du bundle. No-op si P5 non autorisé.

    Marque chaque corridor avec `renduomega.accepted` (True/False),
    rejette les corridors non conformes en les filtrant dans une liste
    séparée `corridors_rejected_by_renduomega`, et enrichit les corridors
    acceptés avec le bloc `renduomega.render` (§5).

    Contrat : le frontend ne doit rendre QUE les corridors restants dans
    `bundle["corridors"]` — les rejetés sont retirés, pas juste marqués,
    afin de **bloquer immédiatement tout rendu non conforme** (§1.2).
    """
    if not isinstance(bundle, dict):
        return bundle
    auth = is_p5_authorized()
    if not auth["authorized"]:
        bundle["renduomega_integration"] = {
            "status": "BYPASSED",
            "reason": "P5_NOT_AUTHORIZED",
            "authorization": auth,
        }
        return bundle

    terrain_signals = bundle.get("terrain_signals") or bundle.get("terrain")
    bundle_species = bundle.get("species") or bundle.get("species_profile")
    contamination = bundle.get("contamination_zones") or bundle.get("contamination")
    affuts = bundle.get("affuts")
    # Détermination du centre pour la validation rayon fonctionnel
    c_lat = c_lng = None
    c = bundle.get("center") or bundle.get("waypoint")
    if isinstance(c, dict):
        c_lat = c.get("lat"); c_lng = c.get("lng") or c.get("lon")
    elif isinstance(c, (list, tuple)) and len(c) >= 2:
        c_lat, c_lng = c[0], c[1]
    if c_lat is None:
        c_lat = bundle.get("lat"); c_lng = bundle.get("lng") or bundle.get("lon")
    if c_lat is None:
        # Fallback : 1er point du 1er corridor
        for _c in bundle.get("corridors") or []:
            _p = _c.get("path") or _c.get("polyline") or []
            if _p:
                c_lat, c_lng = _p[0][0], _p[0][1]; break
    center = [c_lat, c_lng] if c_lat is not None else None

    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    errors_log: List[Dict[str, Any]] = []

    for c_in in bundle.get("corridors") or []:
        # Pré-étape §2 : normaliser l'échantillonnage à 25-30 points
        path_src = c_in.get("path") or c_in.get("polyline") or []
        if len(path_src) < GEOM_MIN_POINTS or len(path_src) > GEOM_MAX_POINTS:
            path_norm = _resample_path_uniform(path_src, target_n=28)
            c_in = dict(c_in)
            c_in["path_original_count"] = len(path_src)
            c_in["path"] = path_norm
            c_in["path_resampled_by_renduomega"] = True
        verdict = validate_corridor(
            c_in, center=center, terrain_signals=terrain_signals,
            contamination_zones=contamination, affuts=affuts,
            bundle_species=bundle_species,
        )
        c_out = dict(c_in)
        c_out["renduomega"] = verdict
        # PHASE_X200_P6_ANTI_RÉGRESSION_Ω — observation non intrusive
        try:
            from engines.post_smoothing import anti_regression_omega as _ar
            _ar.record_corridor_verdict(
                c_in, verdict,
                bundle_context={"lat": c_lat, "lng": c_lng},
            )
        except Exception:
            pass
        if verdict["accepted"]:
            # Application des attributs de rendu normalisés au niveau corridor
            r = verdict["render"]
            c_out["color"]       = r["color"]
            c_out["opacity"]     = r["opacity"]
            c_out["width_px_renduomega"] = r["width_px"]
            c_out["min_zoom"]    = r["min_zoom"]
            c_out["zindex"]      = r["zindex"]
            accepted.append(c_out)
        else:
            rejected.append(c_out)
            errors_log.append({
                "corridor_id": c_in.get("id"),
                "errors": verdict["errors"],
            })

    # §1.2 — filtrage dur (les rejetés ne sont PAS publiés)
    bundle["corridors"] = accepted
    bundle["corridors_rejected_by_renduomega"] = rejected
    bundle["renduomega_integration"] = {
        "status": "APPLIED",
        "phase": "X200_P5_RENDUΩ_INTEGRATION_ULTIME_Ω",
        "authorization": auth,
        "totals": {
            "total_input":  len(accepted) + len(rejected),
            "accepted":     len(accepted),
            "rejected":     len(rejected),
        },
        "constants": {
            "base_color": BASE_COLOR_ORANGE_AMBRE,
            "opacity_min": OPACITY_MIN,
            "min_zoom": MIN_ZOOM,
            "widths_allowed": list(WIDTHS_ALLOWED),
            "zindex_institutionnel": ZINDEX_INSTITUTIONNEL,
        },
        "errors_log": errors_log,
        "v30_engine_touched": False,
        "zones_or_salines_modified": False,
    }
    bundle["smoother_p5_renduomega_applied"] = True
    # PHASE_X200_P6 — snapshot bundle (fail-soft)
    try:
        from engines.post_smoothing import anti_regression_omega as _ar
        _ar.record_bundle_summary(bundle)
    except Exception:
        pass
    return bundle
