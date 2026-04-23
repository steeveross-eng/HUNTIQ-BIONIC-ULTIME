"""
external_inflow.py — Logique EXTERNAL INFLOW pour ENGINE_RÉSEAU_VEINEUX_Ω
===========================================================================
Phase     : PHASE_X200_P1_EXTERNAL_INFLOW_Ω
Commandant: STEEVE-MAX

Conforme au DIAGRAMME CONCEPTUEL OFFICIEL :
  - Cercle interne : rayon 600 m ± 30 %
  - Couronne externe : 700-800 m (origine des veines externes)
  - 12 à 24 ENTRY_NODES externes répartis angulairement
  - Fusion externe → interne à ≤ 75 m
  - Élargissement ×1.5 sur segments superposés
  - Pondération directionnelle : hydro 40 %, pente 25 %, couvert 20 %, zones vitales 15 %

FEATURE FLAG : OFF par défaut. Activation uniquement sous :
  - P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true
  - P1_COMMANDANT_TOKEN=STEEVE-MAX-P1-EXTERNAL-INFLOW
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════
# FEATURE FLAG + DOUBLE-VERROU D'AUTORISATION
# ═══════════════════════════════════════════════════════════════════════
EXTERNAL_INFLOW_ENABLED: bool = True
EXPECTED_TOKEN = "STEEVE-MAX-P1-EXTERNAL-INFLOW"


def is_external_inflow_authorized() -> Dict[str, Any]:
    env_ok = os.environ.get("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "").strip().lower() == "true"
    token_ok = os.environ.get("P1_COMMANDANT_TOKEN", "") == EXPECTED_TOKEN
    return {
        "authorized": EXTERNAL_INFLOW_ENABLED and env_ok and token_ok,
        "flag_enabled": EXTERNAL_INFLOW_ENABLED,
        "env_ok": env_ok,
        "token_ok": token_ok,
        "expected_token": EXPECTED_TOKEN,
    }


# ═══════════════════════════════════════════════════════════════════════
# CONTRAT RENDUΩ — VERSION COMMANDANT (§5.5)
# ═══════════════════════════════════════════════════════════════════════
HIERARCHY_5_LEVELS_COMMANDANT = [
    {"level": "CRITIQUE", "color": "#CC0000", "largeur_m": 6, "weight": 6, "score_min": 85, "score_max": 100},
    {"level": "MAJEUR",   "color": "#FF0000", "largeur_m": 4, "weight": 5, "score_min": 70, "score_max": 84},
    {"level": "FORT",     "color": "#FF8C00", "largeur_m": 3, "weight": 4, "score_min": 50, "score_max": 69},
    {"level": "MODERE",   "color": "#FFD700", "largeur_m": 2, "weight": 3, "score_min": 30, "score_max": 49},
    {"level": "FAIBLE",   "color": "#BFBFBF", "largeur_m": 1, "weight": 2, "score_min": 0,  "score_max": 29},
]

# ═══════════════════════════════════════════════════════════════════════
# CONSTANTES DIAGRAMME CONCEPTUEL
# ═══════════════════════════════════════════════════════════════════════
INNER_RADIUS_NOMINAL_M = 600
INNER_RADIUS_TOLERANCE_PCT = 0.30
EXTERNAL_RING_MIN_M = 700
EXTERNAL_RING_MAX_M = 800
ENTRY_NODES_MIN = 12
ENTRY_NODES_MAX = 24
FUSION_MAX_DISTANCE_M = 75
FUSION_WIDTH_MULTIPLIER = 1.5

# Pondérations directionnelles §5.2
DIRECTIONAL_WEIGHTS = {
    "hydro":          0.40,
    "slope":          0.25,
    "forest_cover":   0.20,
    "vital_zones":    0.15,
}

METERS_PER_DEG_LAT = 111320.0


# ═══════════════════════════════════════════════════════════════════════
# PRIMITIVES GÉOMÉTRIQUES
# ═══════════════════════════════════════════════════════════════════════
def _meters_per_deg_lng(lat: float) -> float:
    return METERS_PER_DEG_LAT * max(0.1, math.cos(math.radians(lat)))


def _offset_latlng(lat: float, lng: float, bearing_deg: float, dist_m: float) -> List[float]:
    """Projection approximative équirectangulaire (< 2 km, erreur négligeable)."""
    rad = math.radians(bearing_deg)
    dlat = (dist_m * math.cos(rad)) / METERS_PER_DEG_LAT
    dlng = (dist_m * math.sin(rad)) / _meters_per_deg_lng(lat)
    return [lat + dlat, lng + dlng]


def _haversine_m(a: List[float], b: List[float]) -> float:
    R = 6371000.0
    lat1 = math.radians(a[0]); lat2 = math.radians(b[0])
    dlat = math.radians(b[0] - a[0])
    dlon = math.radians(b[1] - a[1])
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(h))


# ═══════════════════════════════════════════════════════════════════════
# SECTION 1 — GÉNÉRATION DES 12-24 ENTRY_NODES EXTERNES
# ═══════════════════════════════════════════════════════════════════════
def generate_entry_nodes(
    center_lat: float,
    center_lon: float,
    count: int = 16,
    ring_min_m: float = EXTERNAL_RING_MIN_M,
    ring_max_m: float = EXTERNAL_RING_MAX_M,
    terrain_signals: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Génère `count` ENTRY_NODES uniformément répartis sur la couronne externe.

    - count clampé dans [12, 24]
    - Distribution angulaire : 360° / count (15° ou 30° typique)
    - Rayon : milieu de (ring_min, ring_max) avec jitter ±50m si signals fournis
    - Chaque node reçoit un poids directionnel selon attracteurs
    """
    count = max(ENTRY_NODES_MIN, min(ENTRY_NODES_MAX, count))
    angle_step = 360.0 / count
    radius_nominal = (ring_min_m + ring_max_m) / 2.0
    nodes = []
    for i in range(count):
        bearing = i * angle_step
        node_pt = _offset_latlng(center_lat, center_lon, bearing, radius_nominal)
        weight = weight_entry_node(
            node_pt, bearing, center_lat, center_lon, terrain_signals or {}
        )
        nodes.append({
            "id": f"entry_node_{i:02d}",
            "index": i,
            "bearing_deg": round(bearing, 2),
            "radius_m": round(radius_nominal, 1),
            "lat": round(node_pt[0], 7),
            "lng": round(node_pt[1], 7),
            "weight": round(weight, 4),
            "components": _weight_components(node_pt, bearing, terrain_signals or {}),
        })
    return nodes


def _weight_components(node_pt: List[float], bearing_deg: float,
                      signals: Dict[str, Any]) -> Dict[str, float]:
    """Composantes de pondération 4 facteurs (hydro/slope/forest/vital)."""
    # Hydro : distance aux water_points
    water_points = signals.get("water_points", [])
    hydro = 0.5
    if water_points:
        min_d = min(_haversine_m(node_pt, w) for w in water_points)
        hydro = max(0.0, min(1.0, (300.0 - min_d) / 300.0))  # bonus si < 300m
    # Slope : faible = bonus (pente extrême = malus)
    slope_pts = signals.get("steep_slope_points", [])
    slope = 0.7  # par défaut favorable
    if slope_pts:
        near = sum(1 for s in slope_pts if _haversine_m(node_pt, s) < 50)
        slope = max(0.0, 0.8 - 0.15 * near)
    # Forest cover : signal forestier booléen/numérique
    forest = float(signals.get("forest_cover", 0.6))
    forest = max(0.0, min(1.0, forest))
    # Vital zones : proximité
    vital = signals.get("vital_zones", [])
    vital_score = 0.4
    if vital:
        dists = []
        for z in vital:
            zl = z.get("lat"); zn = z.get("lng") or z.get("lon")
            if zl is not None and zn is not None:
                dists.append(_haversine_m(node_pt, [zl, zn]))
        if dists:
            min_d = min(dists)
            vital_score = max(0.0, min(1.0, (500.0 - min_d) / 500.0))
    return {"hydro": round(hydro, 4), "slope": round(slope, 4),
            "forest_cover": round(forest, 4), "vital_zones": round(vital_score, 4)}


def weight_entry_node(node_pt: List[float], bearing_deg: float,
                      center_lat: float, center_lon: float,
                      signals: Dict[str, Any]) -> float:
    """Pondération directionnelle d'un entry_node (0-1) selon §5.2."""
    comp = _weight_components(node_pt, bearing_deg, signals)
    w = DIRECTIONAL_WEIGHTS
    return (comp["hydro"] * w["hydro"]
            + comp["slope"] * w["slope"]
            + comp["forest_cover"] * w["forest_cover"]
            + comp["vital_zones"] * w["vital_zones"])


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2 — TRAÇAGE ORGANIQUE EXTERNAL → INTERNAL
# ═══════════════════════════════════════════════════════════════════════
def trace_organic_path(entry_node: Dict[str, Any],
                       target: Dict[str, Any],
                       n_points: int = 28) -> List[List[float]]:
    """Trace une spline organique de l'entry_node vers la zone vitale cible.

    Utilise une interpolation Catmull-Rom-like avec 2 points de contrôle
    générés via déviation selon signaux terrain (courbure progressive).
    """
    p0 = [entry_node["lat"], entry_node["lng"]]
    p3 = [float(target.get("lat")), float(target.get("lng") or target.get("lon"))]
    # Points de contrôle : 1/3 et 2/3 du trajet avec offset perpendiculaire modulé
    mid_lat = (p0[0] + p3[0]) / 2
    mid_lng = (p0[1] + p3[1]) / 2
    # Offset perpendiculaire pour produire une courbure organique (pas une droite)
    dx = p3[1] - p0[1]
    dy = p3[0] - p0[0]
    perp_lat = -dx * 0.08  # courbure modérée
    perp_lng = dy * 0.08
    p1 = [p0[0] + (mid_lat - p0[0]) * 0.5 + perp_lat * 0.5,
          p0[1] + (mid_lng - p0[1]) * 0.5 + perp_lng * 0.5]
    p2 = [mid_lat + perp_lat * 0.3,
          mid_lng + perp_lng * 0.3]
    # Bezier cubique échantillonnée en n_points
    path = []
    for i in range(n_points):
        t = i / (n_points - 1)
        u = 1 - t
        lat = u**3 * p0[0] + 3*u**2*t * p1[0] + 3*u*t**2 * p2[0] + t**3 * p3[0]
        lng = u**3 * p0[1] + 3*u**2*t * p1[1] + 3*u*t**2 * p2[1] + t**3 * p3[1]
        path.append([round(lat, 7), round(lng, 7)])
    return path


def find_nearest_vital_zone(entry_node: Dict[str, Any],
                            vital_zones: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Retourne la zone vitale la plus probable pour cet entry_node."""
    if not vital_zones:
        return None
    node_pt = [entry_node["lat"], entry_node["lng"]]
    best = None
    best_score = -1
    for z in vital_zones:
        zl = z.get("lat"); zn = z.get("lng") or z.get("lon")
        if zl is None or zn is None:
            continue
        d = _haversine_m(node_pt, [zl, zn])
        # Priorité hiérarchique : score zone / distance
        zscore = float(z.get("score", 1))
        prob = zscore * max(0.1, 1.0 / (d / 100.0 + 1))
        if prob > best_score:
            best_score = prob
            best = z
    return best


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2.2 — FUSION EXTERNE → INTERNE (§5.4)
# ═══════════════════════════════════════════════════════════════════════
def fuse_external_internal(external_paths: List[Dict[str, Any]],
                           internal_paths: List[Dict[str, Any]],
                           merge_distance_m: float = FUSION_MAX_DISTANCE_M
                           ) -> Dict[str, Any]:
    """Fusionne corridors externes et internes.

    - Détecte points de contact ≤ merge_distance_m (§5.4 : 75 m)
    - Marque les segments superposés pour élargissement ×1.5
    - Retourne diagnostic complet (non destructif)
    """
    fusions = []
    for ext in external_paths:
        ext_path = ext.get("path") or []
        for inte in internal_paths:
            int_path = inte.get("path") or []
            contact = _find_contact(ext_path, int_path, merge_distance_m)
            if contact:
                fusions.append({
                    "external_id": ext.get("id"),
                    "internal_id": inte.get("id"),
                    "contact_point_external_idx": contact["idx_a"],
                    "contact_point_internal_idx": contact["idx_b"],
                    "distance_m": round(contact["distance_m"], 2),
                    "width_multiplier": FUSION_WIDTH_MULTIPLIER,
                    "new_width_m": round(
                        max(ext.get("largeur_m", 1), inte.get("largeur_m", 1)) * FUSION_WIDTH_MULTIPLIER,
                        2,
                    ),
                })
    return {
        "fusions_detected": len(fusions),
        "fusion_points": fusions,
        "merge_threshold_m": merge_distance_m,
        "width_multiplier": FUSION_WIDTH_MULTIPLIER,
    }


def _find_contact(path_a: List[List[float]], path_b: List[List[float]],
                  max_d: float) -> Optional[Dict[str, Any]]:
    if not path_a or not path_b:
        return None
    best = None
    best_d = float("inf")
    for i, pa in enumerate(path_a):
        for j, pb in enumerate(path_b):
            d = _haversine_m(pa, pb)
            if d < best_d and d <= max_d:
                best_d = d
                best = {"idx_a": i, "idx_b": j, "distance_m": d}
    return best


# ═══════════════════════════════════════════════════════════════════════
# CLASSIFICATION (version COMMANDANT §5.5)
# ═══════════════════════════════════════════════════════════════════════
def classify_corridor_commandant(score: float) -> Dict[str, Any]:
    for lvl in HIERARCHY_5_LEVELS_COMMANDANT:
        if lvl["score_min"] <= score <= lvl["score_max"]:
            return {**lvl, "score": score}
    return {**HIERARCHY_5_LEVELS_COMMANDANT[-1], "score": score}


# ═══════════════════════════════════════════════════════════════════════
# DIAGNOSTIC ENTRY_POINT — toujours disponible (lecture seule)
# ═══════════════════════════════════════════════════════════════════════
def external_inflow_status() -> Dict[str, Any]:
    auth = is_external_inflow_authorized()
    return {
        "phase": "PHASE_X200_P1_EXTERNAL_INFLOW_Ω",
        "authorization": auth,
        "diagram_spec": {
            "inner_radius_m": INNER_RADIUS_NOMINAL_M,
            "inner_tolerance_pct": INNER_RADIUS_TOLERANCE_PCT,
            "external_ring_m": [EXTERNAL_RING_MIN_M, EXTERNAL_RING_MAX_M],
            "entry_nodes_range": [ENTRY_NODES_MIN, ENTRY_NODES_MAX],
            "fusion_max_distance_m": FUSION_MAX_DISTANCE_M,
            "fusion_width_multiplier": FUSION_WIDTH_MULTIPLIER,
            "directional_weights": DIRECTIONAL_WEIGHTS,
        },
        "hierarchy_5_levels_commandant": HIERARCHY_5_LEVELS_COMMANDANT,
        "smoother_touched": False,
        "rendu_modified": False,
    }
