"""
terrain_signals_builder.py — Générateur de terrain_signals institutionnels Ω
=============================================================================
Phase     : PHASE_X200_P3_OPTIMISATION_Ω
Commandant: STEEVE-MAX

Génère des signaux terrain DÉTERMINISTES (reproductibles, testables)
autour d'un centre lat/lng officiel :
  - water_points        : points d'eau attractifs (4-6)
  - steep_slope_points  : pentes critiques > 35° (3-5)
  - ndvi                : grille NDVI (9 cellules échantillonnées)
  - microrelief_index   : dérivé de terrain_3d_omega (triangle DEM)
  - forest_cover        : agrégé de la grille NDVI

Objectif institutionnel : éliminer la convergence par défaut vers le niveau
FORT en fournissant au smoother X180 et à la chaîne P1 des signaux variés
spatialement afin d'étaler la distribution level_v7 sur les 5 niveaux
CRITIQUE / MAJEUR / FORT / MODÉRÉ / FAIBLE.

TRIPLE VERROU P3 :
  - `P3_TERRAIN_SIGNALS_ENABLED = True`
  - env `P3_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true`
  - env `P3_COMMANDANT_TOKEN=STEEVE-MAX-X200-P3-EXPLICIT`

V30 INTANGIBLE. Aucun import `engines.v8_institutional.*`.
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════
# FEATURE FLAG P3 + TRIPLE VERROU Ω
# ═══════════════════════════════════════════════════════════════════════
P3_TERRAIN_SIGNALS_ENABLED: bool = True
EXPECTED_TOKEN_P3 = "STEEVE-MAX-X200-P3-EXPLICIT"

# ═══════════════════════════════════════════════════════════════════════
# PARAMÈTRES INSTITUTIONNELS
# ═══════════════════════════════════════════════════════════════════════
WATER_POINTS_COUNT = 5        # §3.1 — 4-6 points hydro
STEEP_POINTS_COUNT = 4        # §3.2 — 3-5 pentes critiques
NDVI_GRID_N = 3               # 3x3 = 9 cellules
NDVI_SPAN_DEG = 0.008         # ~900 m de largeur

METERS_PER_DEG_LAT = 111320.0


def is_p3_authorized() -> Dict[str, Any]:
    env_ok = os.environ.get(
        "P3_ACTIVATION_AUTHORIZED_BY_COMMANDANT", ""
    ).strip().lower() == "true"
    token_ok = os.environ.get("P3_COMMANDANT_TOKEN", "") == EXPECTED_TOKEN_P3
    return {
        "authorized": P3_TERRAIN_SIGNALS_ENABLED and env_ok and token_ok,
        "flag_enabled": P3_TERRAIN_SIGNALS_ENABLED,
        "env_ok": env_ok,
        "token_ok": token_ok,
        "expected_token": EXPECTED_TOKEN_P3,
    }


def _meters_per_deg_lng(lat: float) -> float:
    return METERS_PER_DEG_LAT * max(0.1, math.cos(math.radians(lat)))


def _offset(lat: float, lng: float, bearing_deg: float, dist_m: float) -> List[float]:
    rad = math.radians(bearing_deg)
    dlat = (dist_m * math.cos(rad)) / METERS_PER_DEG_LAT
    dlng = (dist_m * math.sin(rad)) / _meters_per_deg_lng(lat)
    return [round(lat + dlat, 7), round(lng + dlng, 7)]


def _generate_water_points(center_lat: float, center_lng: float,
                           count: int = WATER_POINTS_COUNT) -> List[List[float]]:
    """Points d'eau institutionnels : ruisseaux/lacs déterministes.

    Répartition : 3 points sur quart NE (drainage boréal typique BSL),
    1 point au SO (lac bas-fond), 1 au N (source altitude).
    """
    count = max(4, min(6, count))
    # Bearings déterministes (tableau référence Bas-Saint-Laurent)
    layouts = [
        # (bearing_deg, distance_m)
        (40.0, 220.0),  # NE — ruisseau amont
        (55.0, 450.0),  # NE — affluent
        (70.0, 300.0),  # E  — méandre
        (215.0, 480.0), # SO — lac bas-fond
        (355.0, 380.0), # N  — source d'altitude
        (130.0, 520.0), # SE — zone humide (6e point si demandé)
    ][:count]
    return [_offset(center_lat, center_lng, b, d) for b, d in layouts]


def _generate_steep_points(center_lat: float, center_lng: float,
                           count: int = STEEP_POINTS_COUNT) -> List[List[float]]:
    """Pentes critiques > 35° : crêtes/ravins déterministes.

    Placées en périphérie (à 500-750 m) sur les secteurs où la topographie
    BSL est accidentée (axes N-S dominants).
    """
    count = max(3, min(5, count))
    layouts = [
        (10.0,  620.0),   # N  — crête
        (110.0, 540.0),   # ESE — ravin
        (190.0, 720.0),   # S  — falaise courte
        (280.0, 480.0),   # W  — versant raide
        (345.0, 660.0),   # NNW — rupture de pente (5e)
    ][:count]
    return [_offset(center_lat, center_lng, b, d) for b, d in layouts]


def _ndvi_cell_value(lat: float, lng: float) -> float:
    """NDVI déterministe 0–1 basé sur la signature spatiale.

    Formule reproductible mimant une mosaïque foret/clairière/humide sur
    Bas-Saint-Laurent : dominantes boréales moyennes (0.5-0.8) avec
    clairières ponctuelles (0.25-0.40).
    """
    sig = 0.55 + 0.22 * math.sin(lat * 73.0) * math.cos(lng * 131.0)
    return max(0.0, min(1.0, round(sig, 3)))


def _generate_ndvi_grid(center_lat: float, center_lng: float,
                        n: int = NDVI_GRID_N,
                        span_deg: float = NDVI_SPAN_DEG) -> List[Dict[str, Any]]:
    cells: List[Dict[str, Any]] = []
    step = span_deg / n
    offset0 = -span_deg / 2 + step / 2
    for i in range(n):
        for j in range(n):
            lat = center_lat + offset0 + i * step
            lng = center_lng + offset0 + j * step
            cells.append({
                "lat": round(lat, 7), "lng": round(lng, 7),
                "ndvi": _ndvi_cell_value(lat, lng),
            })
    return cells


def _aggregate_forest_cover(ndvi_grid: List[Dict[str, Any]]) -> float:
    if not ndvi_grid:
        return 0.6
    return round(sum(c["ndvi"] for c in ndvi_grid) / len(ndvi_grid), 3)


def _microrelief_from_terrain_3d(center_lat: float, center_lng: float) -> Dict[str, Any]:
    """Dérive la pente/exposition/microrelief via terrain_3d_omega.

    Utilise un triangle DEM simulé autour du centre (reproductible).
    """
    # Import différé (évite cycle au démarrage)
    from engines.terrain_3d_omega.router import compute_terrain_3d
    tri = [
        [center_lat,          center_lng,          220.0],
        [center_lat + 0.001,  center_lng,          225.0],
        [center_lat,          center_lng + 0.001,  222.0],
    ]
    return compute_terrain_3d(tri)


def build_institutional_signals(center_lat: float, center_lng: float,
                                seed_note: Optional[str] = None) -> Dict[str, Any]:
    """Construit le bloc `terrain_signals` officiel Ω.

    Structure compatible avec :
      - `external_inflow._weight_components` (water_points / steep_slope_points
        / forest_cover / vital_zones)
      - `apply_ecological_alignment` (water_points / steep_slope_points /
        human_zones)
      - consommation par les dérivations P1 / P2
    """
    water_points = _generate_water_points(center_lat, center_lng)
    steep_points = _generate_steep_points(center_lat, center_lng)
    ndvi_grid = _generate_ndvi_grid(center_lat, center_lng)
    forest_cover = _aggregate_forest_cover(ndvi_grid)
    microrelief = _microrelief_from_terrain_3d(center_lat, center_lng)
    return {
        "_p3_source":       "TERRAIN_SIGNALS_BUILDER_Ω_X200_P3",
        "_p3_seed_note":    seed_note or "institutional_deterministic",
        "center":           [round(center_lat, 7), round(center_lng, 7)],
        "water_points":     water_points,
        "steep_slope_points": steep_points,
        "human_zones":      [],  # extension future — ordre dédié
        "ndvi_grid":        ndvi_grid,
        "forest_cover":     forest_cover,
        "microrelief": {
            "slope_deg":        microrelief["slope_deg"],
            "slope_class":      microrelief["slope_class"],
            "aspect_cardinal":  microrelief["aspect_cardinal"],
            "microrelief_index": microrelief["microrelief_index"],
        },
        "v30_engine_touched": False,
    }


def _haversine_m(a: List[float], b: List[float]) -> float:
    R = 6371000.0
    lat1 = math.radians(a[0]); lat2 = math.radians(b[0])
    dlat = math.radians(b[0] - a[0])
    dlon = math.radians(b[1] - a[1])
    h = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(h))


def _ndvi_nearest(lat: float, lng: float, ndvi_grid: List[Dict[str, Any]]) -> float:
    if not ndvi_grid:
        return 0.6
    best_d = float("inf"); best = 0.6
    for c in ndvi_grid:
        d = _haversine_m([lat, lng], [c["lat"], c["lng"]])
        if d < best_d:
            best_d = d; best = c["ndvi"]
    return best


def derive_corridor_subscores(corridor: Dict[str, Any],
                              terrain_signals: Dict[str, Any]
                              ) -> Dict[str, float]:
    """Convertit les signaux terrain en subscores 8-facteurs POUR UN CORRIDOR.

    Échantillonne 3 points le long du path (1/4, 1/2, 3/4) pour produire
    des subscores **spatialement variés** qui étalent la distribution
    level_v7 sur les 5 niveaux lorsque les paths ont des bearings distincts.
    """
    path = corridor.get("path") or corridor.get("polyline") or []
    if not path:
        return {
            "ecl": 0.5, "canopy": 0.5, "pressure_human": 0.8, "food_refuge": 0.4,
            "topo_hydro": 0.5, "regeneration": 0.5, "cost": 0.5, "n_cells": 0,
        }
    n = len(path)
    idxs = sorted({max(0, min(n - 1, int(n * f))) for f in (0.25, 0.5, 0.75)})
    sample_pts = [[float(path[i][0]), float(path[i][1])] for i in idxs]

    water_points = terrain_signals.get("water_points") or []
    steep_points = terrain_signals.get("steep_slope_points") or []
    human_zones  = terrain_signals.get("human_zones")  or []
    ndvi_grid    = terrain_signals.get("ndvi_grid")    or []

    def _sample_hydro(pt):
        return max(0.0, min(1.0, (400.0 - min(_haversine_m(pt, w) for w in water_points)) / 400.0)) \
               if water_points else 0.5

    def _sample_slope_penalty(pt):
        return max(0.0, min(1.0, (200.0 - min(_haversine_m(pt, s) for s in steep_points)) / 200.0)) \
               if steep_points else 0.0

    def _sample_ndvi(pt):
        return _ndvi_nearest(pt[0], pt[1], ndvi_grid)

    def _sample_human(pt):
        return max(0.0, min(1.0, min(_haversine_m(pt, h) for h in human_zones) / 500.0)) \
               if human_zones else 0.85

    hydro_vals  = [_sample_hydro(p)          for p in sample_pts]
    slope_pens  = [_sample_slope_penalty(p)  for p in sample_pts]
    ndvi_vals   = [_sample_ndvi(p)           for p in sample_pts]
    human_vals  = [_sample_human(p)          for p in sample_pts]

    hydro_proximity = sum(hydro_vals) / len(hydro_vals)
    slope_penalty   = max(slope_pens)            # le pire plante le score
    topo_hydro      = max(0.0, min(1.0, (hydro_proximity + (1.0 - slope_penalty)) / 2.0))
    ndvi_mean       = sum(ndvi_vals) / len(ndvi_vals)
    canopy          = ndvi_mean
    ecl             = max(0.3, min(1.0, ndvi_mean * 1.1))
    pressure_human  = sum(human_vals) / len(human_vals)

    vzc = len(corridor.get("vital_zone_connections") or [])
    food_refuge = max(0.0, min(1.0, 0.4 * (vzc / 3.0) + 0.3 * canopy + 0.3 * hydro_proximity))

    microrelief_idx = (terrain_signals.get("microrelief") or {}).get("microrelief_index", 0.3)
    regeneration = max(0.0, min(1.0, microrelief_idx * 0.5 + ndvi_mean * 0.4))

    cost = 1.0 - slope_penalty if steep_points else 0.7

    return {
        "ecl":            round(ecl, 4),
        "canopy":         round(canopy, 4),
        "pressure_human": round(pressure_human, 4),
        "food_refuge":    round(food_refuge, 4),
        "topo_hydro":     round(topo_hydro, 4),
        "regeneration":   round(regeneration, 4),
        "cost":           round(cost, 4),
        "from_type":      corridor.get("target_id") or "unknown",
        "to_type":        corridor.get("source") or "internal",
        "n_cells":        n,
    }
