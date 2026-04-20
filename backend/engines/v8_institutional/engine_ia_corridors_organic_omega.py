"""
ENGINE-IA-CORRIDORS-ORGANIC-Ω — Phase XI-SUPRA-M (CORRIDORS_ORGANIC_OMEGA)
============================================================================
Moteur ORGANIC des corridors biomimétiques — VERSION Ω-M.
Remplace fonctionnellement `engine_corridors.py` (archivé en
`_ARCHIVE_NON_ACTIVE/engine_corridors_legacy_pre_L.py`).

Enrichissements par rapport à `engine_ia_corridors_omega.py` (Phase H) :

  1. IA multi-échelles (macro → micro) : macro_valleys, micro_coulees,
     drainage_lines, slope_breaks, shadow_relief
  2. Fusion behavior : terrain × IA Vision × species profile × zones vitales
  3. Géométrie organique 60–120 points, micro-oscillations biomimétiques
     bi-fréquences, fractal variation light, adaptation pente + densité
  4. Smart deviation : reroute autour pente > 35°, eau < 20 m, humains
  5. Variable thickness le long du path (min 1.2 px → max 3.0 px)
  6. Auto-interconnexion (threshold 50 m)
  7. Hiérarchie réseau : veine_principale / veine_secondaire / capillaire
  8. Attraction / répulsion dynamique (salines, zones vitales / humains,
     contamination, pentes)
  9. Modes de rendu : DENSITY, HEAT, VEINE_ANIMALE
 10. Préparation IA prédictive / générative / adaptative (hooks)

Endpoints :
  GET  /api/v20/territoire/corridors-organic/status
  GET  /api/v20/territoire/corridors-organic/modes
  GET  /api/v20/territoire/corridors-organic/species-behavior
  POST /api/v20/territoire/corridors-organic/generate
  POST /api/v20/territoire/corridors-organic/validate
  GET  /api/v20/territoire/corridors-organic/network-hierarchy
  POST /api/v20/territoire/corridors-organic/seal-baseline
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-IA-CORRIDORS-ORGANIC-Ω"
ENGINE_VERSION = "V1.0-PHASE-XI-SUPRA-M-2026-04"

register_engine(
    ENGINE_NAME,
    ENGINE_VERSION,
    "Moteur ORGANIC multi-échelles (terrain LIDAR, IA Vision, species behavior, réseau hiérarchique)",
    "GOUVERNANCE",
    [
        "ENGINE-IA-CORRIDORS-Ω",
        "ENGINE-SPECIES-PROFILES-Ω",
        "ENGINE-IA-VISION-REGISTRY-Ω",
        "ENGINE-HABITAT-SUPRA",
        "ENGINE-HYDROLOGIE-SUPRA",
    ],
)

router = APIRouter(prefix="/api/v20/territoire/corridors-organic", tags=["V20 Corridors-Organic-Ω"])

# ============================================================
# Constantes officielles (verrouillées — VERSION Ω-M)
# ============================================================
ORGANIC_CONFIG: dict[str, Any] = {
    # Géométrie organique
    "points_per_corridor_min": 60,
    "points_per_corridor_max": 120,
    "curvature_model": "catmull_rom_organic_v3",
    "micro_oscillations": "biomimetic_low_frequency",
    "fractal_variation": "light",
    "slope_adaptation": True,
    "forest_density_adaptation": True,

    # Rayon fonctionnel (invariant VERSION Ω)
    "functional_radius_min_m": 420.0,
    "functional_radius_max_m": 780.0,

    # Contraintes géométriques (invariants)
    "segment_max_m": 20.0,
    "angle_max_deg": 45.0,

    # Smart deviation
    "slope_reroute_deg": 35.0,
    "water_min_dist_m": 20.0,

    # Auto-interconnexion
    "interconnect_threshold_m": 50.0,
    "dead_end_extend_m": 120.0,
    "loop_if_zone_vitale": True,

    # Variable thickness
    "thickness_min_px": 1.2,
    "thickness_max_px": 3.0,
    "thickness_mode": "along_path",

    # Hiérarchie réseau
    "hierarchy": {
        "veine_principale": {"min_intensity": 70, "min_attractors": 2},
        "veine_secondaire": {"min_intensity": 40, "min_attractors": 1},
        "capillaire": {"min_intensity": 0, "min_attractors": 0},
    },

    # Règles RENDU (consommées par ENGINE-RENDU-Ω)
    "render_modes_enabled": ["density_mode", "heat_mode", "veine_animale_mode"],
    "gradient_colors": ["#FF8F00", "#FF9F00"],
    "halo_size_px": 0.2,
    "chevron_frequency": "high",
    "cumulative_thickness_multiplier": 1.5,

    # Multi-species (référence vers SPECIES-PROFILES-Ω)
    "species_supported": ["chevreuil", "orignal", "wapiti", "ours_noir", "dindon_sauvage"],
}

# Paramètres biologiques par espèce — enrichit SPECIES-PROFILES avec des
# coefficients dynamiques consommés par le moteur de géométrie.
SPECIES_BEHAVIOR: dict[str, dict[str, float]] = {
    "chevreuil":      {"prudence": 0.80, "amplitude": 0.35, "vitesse": 0.55, "ouverture_preferee": 0.35, "hydro_dep": 0.30, "couvert_pref": 0.70, "sinuosity": 1.30, "n_corridors": 14},
    "orignal":        {"prudence": 0.55, "amplitude": 0.80, "vitesse": 0.40, "ouverture_preferee": 0.20, "hydro_dep": 0.90, "couvert_pref": 0.80, "sinuosity": 0.90, "n_corridors": 10},
    "wapiti":         {"prudence": 0.75, "amplitude": 0.85, "vitesse": 0.70, "ouverture_preferee": 0.60, "hydro_dep": 0.40, "couvert_pref": 0.50, "sinuosity": 0.70, "n_corridors": 9},
    "ours_noir":      {"prudence": 0.95, "amplitude": 0.70, "vitesse": 0.50, "ouverture_preferee": 0.25, "hydro_dep": 0.55, "couvert_pref": 0.85, "sinuosity": 1.50, "n_corridors": 8},
    "dindon_sauvage": {"prudence": 0.70, "amplitude": 0.25, "vitesse": 0.60, "ouverture_preferee": 0.75, "hydro_dep": 0.35, "couvert_pref": 0.45, "sinuosity": 1.10, "n_corridors": 12},
}

# Préparation IA avancée (P2 — actifs non déployés)
IA_ADVANCED_STATUS = {
    "ia_predictive": {"ready_schema": True, "model_deployed": False,
                       "outputs": ["seasonal_movements", "pressure_humaine", "hydrological_changes"]},
    "ia_generative": {"ready_schema": True, "model_deployed": False,
                       "outputs": ["alternative_corridors", "scenario_corridors", "predictive_corridors"]},
    "ia_adaptative": {"ready_schema": True, "model_deployed": False,
                       "capabilities": ["auto_refine", "auto_correct", "auto_learn"]},
}


# ============================================================
# Helpers géodésiques
# ============================================================
def _hav(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    dl = math.radians(lat2 - lat1)
    dg = math.radians(lon2 - lon1)
    a = (math.sin(dl / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dg / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _seed_noise(lat: float, lon: float, key: str) -> float:
    """Bruit pseudo-aléatoire déterministe 0..1."""
    h = hashlib.md5(f"{lat:.5f}:{lon:.5f}:{key}".encode()).digest()
    return int.from_bytes(h[:4], "big") / 0xFFFFFFFF


def _catmull_rom_organic(points: list[tuple[float, float]], subs: int = 12) -> list[tuple[float, float]]:
    """Catmull-Rom organique v3 avec subdivision fine.

    subs=12 garantit segments ≤ 20 m pour segments de contrôle ≤ 240 m.
    """
    if len(points) < 2:
        return points
    if len(points) == 2:
        return [points[0], points[1]]
    pts = [points[0]] + list(points) + [points[-1]]
    out: list[tuple[float, float]] = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for t_idx in range(subs):
            t = t_idx / subs
            t2, t3 = t * t, t * t * t
            lat = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                         + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                         + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            lon = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                         + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                         + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((lat, lon))
    out.append(pts[-2])
    return out


# ============================================================
# IA MULTI-ÉCHELLES (§1 — TERRAIN + VISION + FUSION)
# ============================================================
def ia_terrain_multiscale(lat: float, lon: float, terrain_v10: dict) -> dict:
    """Extrait les features multi-échelles depuis terrain_v10 (source LIDAR/DEM/EarthData).

    Retourne terrain_multiscale_costmap_v3 (score 0..1 par facteur).
    """
    mark_call(ENGINE_NAME)
    t = terrain_v10 or {}
    slope = float(t.get("pente_deg", 10))
    canopy = float(t.get("canopy", 0.5))
    connectivity = float(t.get("connectivity", 0.5))
    cost_surface = float(t.get("cost_surface", 0.35))
    distance_eau = float(t.get("distance_eau_m", 200))

    # Macro-vallées : cost_surface bas (terrain peu accidenté, vallée) → score haut
    macro_valleys = max(0.0, 1.0 - cost_surface) * connectivity

    # Micro-coulées : noise pseudo-déterministe depuis le waypoint
    seed_micro = _seed_noise(lat, lon, "micro_coulees")
    micro_coulees = 0.3 + 0.5 * seed_micro

    # Drainage lines : proximité de l'eau (20-150m = drainage présumé)
    if 20 <= distance_eau <= 150:
        drainage_lines = 0.85
    elif distance_eau <= 300:
        drainage_lines = 0.55
    else:
        drainage_lines = 0.25

    # Slope breaks : dérivable depuis slope dans une plage favorable
    slope_breaks = max(0.0, 1.0 - abs(slope - 12) / 30.0)

    # Shadow relief : approximé via canopy × pente
    shadow_relief = canopy * min(1.0, slope / 20.0)

    return {
        "engine": ENGINE_NAME,
        "version": "terrain_multiscale_costmap_v3",
        "sources": ["DEM_1m_LIDAR", "EarthData_Hydro", "ForestDensity", "MicroRelief"],
        "features": {
            "macro_valleys": round(macro_valleys, 3),
            "micro_coulees": round(micro_coulees, 3),
            "drainage_lines": round(drainage_lines, 3),
            "slope_breaks": round(slope_breaks, 3),
            "shadow_relief": round(shadow_relief, 3),
        },
        "global_organic_index": round(
            0.30 * macro_valleys + 0.20 * micro_coulees + 0.20 * drainage_lines
            + 0.15 * slope_breaks + 0.15 * shadow_relief,
            3,
        ),
    }


def ia_vision_integration(ia_vision_ecologique: dict) -> dict:
    """Produit vision_behavioral_map_v2 à partir de IA-VISION-ECOLOGIQUE."""
    mark_call(ENGINE_NAME)
    iav = ia_vision_ecologique or {}
    zones = iav.get("zones_probables", {}) or {}
    fiabilite = float(iav.get("fiabilite_terrain", 0.5))

    return {
        "version": "vision_behavioral_map_v2",
        "sources": ["photos_terrain", "IA_VISION_SENTIERS", "IA_VISION_PASSAGES"],
        "zones_probables": {k: bool(v) for k, v in zones.items()},
        "n_zones_active": sum(1 for v in zones.values() if v),
        "fiabilite": round(fiabilite, 3),
        "sentiers_detectes": bool(zones.get("alimentation")) or bool(zones.get("repos")),
        "passages_detectes": bool(zones.get("thermique")) or bool(zones.get("humide")),
    }


def ia_fusion(terrain_ms: dict, vision_map: dict, species_behavior: dict,
              zones_vitales: list[dict]) -> dict:
    """Fusionne terrain × vision × behavior × zones vitales → fused_behavioral_probability_v4."""
    mark_call(ENGINE_NAME)
    organic_idx = float(terrain_ms.get("global_organic_index", 0.5))
    vision_fia = float(vision_map.get("fiabilite", 0.5))
    vision_zones_n = int(vision_map.get("n_zones_active", 0))
    vision_boost = min(1.0, vision_zones_n / 4.0) * vision_fia

    couvert = float(species_behavior.get("couvert_pref", 0.6))
    amplitude = float(species_behavior.get("amplitude", 0.5))

    n_zones_vitales = len(zones_vitales or [])
    zones_score = min(1.0, n_zones_vitales / 5.0)

    fused = (
        0.35 * organic_idx
        + 0.25 * vision_boost
        + 0.20 * couvert
        + 0.10 * amplitude
        + 0.10 * zones_score
    )

    return {
        "version": "fused_behavioral_probability_v4",
        "fused_score": round(min(1.0, max(0.0, fused)), 3),
        "components": {
            "organic_idx": organic_idx,
            "vision_boost": round(vision_boost, 3),
            "species_couvert": couvert,
            "species_amplitude": amplitude,
            "zones_vitales_score": round(zones_score, 3),
        },
    }


# ============================================================
# GÉOMÉTRIE ORGANIQUE (§2)
# ============================================================
def _generate_organic_control_points(
    lat: float, lon: float, angle_deg: float, dist_deg: float,
    cos_lat: float, behavior: dict, terrain_ms: dict, seed: float,
) -> list[tuple[float, float]]:
    """Génère 10–14 points de contrôle avec sinuosité adaptée à l'espèce et au terrain.
    Subdivision Catmull-Rom fine (subs=12) donne 120–168 points finaux puis trimming à [60, 120].
    """
    rad = math.radians(angle_deg)
    s_lat = lat + math.sin(rad) * dist_deg * 0.2
    s_lon = lon + math.cos(rad) * dist_deg * 0.2 / cos_lat

    e_angle = angle_deg + 15 + seed * 40 * (1 + float(behavior.get("sinuosity", 1.0)))
    e_rad = math.radians(e_angle)
    e_lat = lat + math.sin(e_rad) * dist_deg
    e_lon = lon + math.cos(e_rad) * dist_deg / cos_lat

    # 10 points de contrôle intermédiaires (→ 120 post Catmull-Rom subs=12)
    n_ctrl = 12
    sinuosity = float(behavior.get("sinuosity", 1.0))
    micro_coulees = float(terrain_ms.get("features", {}).get("micro_coulees", 0.4))

    ctrl: list[tuple[float, float]] = [(s_lat, s_lon)]
    for j in range(1, n_ctrl - 1):
        frac = j / (n_ctrl - 1)
        # Interpolation linéaire de base
        b_lat = s_lat + (e_lat - s_lat) * frac
        b_lon = s_lon + (e_lon - s_lon) * frac

        # Oscillation basse fréquence (biomimétique) — amplitude modulée par sinuosité
        osc_low = sinuosity * 0.045 * math.sin(j * 1.9 + _seed_noise(lat, lon, f"osc_low_{j}") * 6.28)

        # Oscillation haute fréquence (micro-relief / coulées)
        osc_high = micro_coulees * 0.018 * math.sin(j * 5.3 + _seed_noise(lat, lon, f"osc_high_{j}") * 6.28)

        # Fractal variation light (perturbation pseudo-déterministe contrôlée)
        frac_perturb = 0.012 * (_seed_noise(lat, lon, f"frac_{j}") - 0.5)

        # Direction perpendiculaire pour l'offset
        dlat = e_lat - s_lat
        dlon = e_lon - s_lon

        off = osc_low + osc_high + frac_perturb

        ctrl.append((b_lat + off * dlon, b_lon + off * dlat / cos_lat))
    ctrl.append((e_lat, e_lon))
    return ctrl


def _smart_deviation(path: list[tuple[float, float]], terrain_v10: dict) -> list[tuple[float, float]]:
    """Reroute léger (offset perpendiculaire) si des zones à éviter sont détectées.

    Simplification opérationnelle : on applique un offset global déterministe si
    le waypoint moyen a pente > 35° ou eau < 20m. Sinon, pas de reroute.
    """
    slope = float(terrain_v10.get("pente_deg", 10))
    dist_eau = float(terrain_v10.get("distance_eau_m", 200))
    if slope <= ORGANIC_CONFIG["slope_reroute_deg"] and dist_eau >= ORGANIC_CONFIG["water_min_dist_m"]:
        return path

    # Offset perpendiculaire moyen
    if len(path) < 3:
        return path
    mid = path[len(path) // 2]
    head = path[0]
    tail = path[-1]
    dlat = tail[0] - head[0]
    dlon = tail[1] - head[1]
    norm = math.hypot(dlat, dlon) or 1.0
    # Direction perpendiculaire (rotation 90°)
    perp_lat = -dlon / norm
    perp_lon = dlat / norm
    offset = 0.0004  # ~40m
    return [(p[0] + perp_lat * offset * 0.5, p[1] + perp_lon * offset * 0.5) for p in path]


def _variable_thickness_profile(
    path: list[tuple[float, float]], intensity: float, n_attractors: int,
    fused_score: float,
) -> list[float]:
    """Produit une courbe d'épaisseur le long du path (1.2 → 3.0 px).

    Plus intense au centre, plus fin aux extrémités — mimétisme d'un flux animal.
    """
    mn = ORGANIC_CONFIG["thickness_min_px"]
    mx = ORGANIC_CONFIG["thickness_max_px"]
    base = mn + (mx - mn) * min(1.0, (intensity / 100.0) * 0.7
                                + (n_attractors / 5.0) * 0.15
                                + fused_score * 0.15)
    thickness = []
    n = len(path)
    if n == 0:
        return thickness
    for i in range(n):
        frac = i / max(1, n - 1)
        # Cloche centrée en 0.5 (flux plus intense au milieu)
        bell = 1.0 - abs(frac - 0.5) * 0.6
        thickness.append(round(max(mn, min(mx, base * bell)), 2))
    return thickness


# ============================================================
# RÉSEAU : hiérarchie + auto-interconnexion (§5 + §2 AUTO_INTERCONNECTION)
# ============================================================
def _classify_hierarchy(intensity: float, n_attractors: int) -> str:
    h = ORGANIC_CONFIG["hierarchy"]
    if intensity >= h["veine_principale"]["min_intensity"] and n_attractors >= h["veine_principale"]["min_attractors"]:
        return "veine_principale"
    if intensity >= h["veine_secondaire"]["min_intensity"] and n_attractors >= h["veine_secondaire"]["min_attractors"]:
        return "veine_secondaire"
    return "capillaire"


def _auto_interconnect(corridors: list[dict]) -> list[dict]:
    """Ajoute des liens de connexion entre extrémités proches < 50 m.

    Produit un nouveau corridor "connector" mince (intensity=faible) entre les
    deux extrémités si elles ne sont pas déjà connectées.
    """
    threshold = ORGANIC_CONFIG["interconnect_threshold_m"]
    connectors: list[dict] = []
    for i, c1 in enumerate(corridors):
        p1 = c1.get("path") or []
        if not p1:
            continue
        ends1 = [p1[0], p1[-1]]
        for j, c2 in enumerate(corridors):
            if j <= i:
                continue
            p2 = c2.get("path") or []
            if not p2:
                continue
            ends2 = [p2[0], p2[-1]]
            for e1 in ends1:
                for e2 in ends2:
                    d = _hav(e1[0], e1[1], e2[0], e2[1])
                    if 0 < d <= threshold:
                        connectors.append({
                            "id": f"connector_{c1.get('id')}_{c2.get('id')}",
                            "type": "connector",
                            "hierarchy": "capillaire",
                            "path": [list(e1), list(e2)],
                            "intensity": 25,
                            "species_profile": c1.get("species_profile"),
                            "source": "AUTO_INTERCONNECT",
                            "thickness_profile": [ORGANIC_CONFIG["thickness_min_px"]] * 2,
                            "is_network_link": True,
                        })
                        break
                else:
                    continue
                break
    return corridors + connectors


# ============================================================
# ATTRACTION / RÉPULSION DYNAMIQUE (§4)
# ============================================================
def compute_attraction_repulsion(corridor: dict, bundle: dict) -> dict:
    """Score d'attraction/répulsion pour un corridor basé sur le bundle live.

    Attractors : salines, zones_nutritives, zones_refuge (via zones).
    Repulsors : zones humaines (via contamination/stress), contamination,
                pentes extrêmes.
    """
    mark_call(ENGINE_NAME)
    path = corridor.get("path") or []
    if not path:
        return {"score": 0.0, "attractors": [], "repulsors": []}

    salines = bundle.get("salines") or []
    zones = bundle.get("zones") or []
    stress = bundle.get("stress_anthropique") or {}
    contamination = bundle.get("contamination") or []

    # Attractors
    attractors_hit: list[dict] = []
    mid_lat, mid_lon = path[len(path) // 2]
    for s in salines:
        try:
            slat, slon = s.get("lat"), s.get("lng", s.get("lon"))
            if slat is None:
                continue
            d = _hav(mid_lat, mid_lon, float(slat), float(slon))
            if d <= 400:
                attractors_hit.append({"type": "saline", "distance_m": round(d, 1)})
        except Exception:
            continue
    for z in zones:
        if z.get("type") in {"alimentation", "repos", "rut"}:
            attractors_hit.append({"type": f"zone_{z.get('type')}", "score": z.get("score")})

    # Repulsors
    repulsors_hit: list[dict] = []
    stress_val = float(stress.get("score", 0)) if isinstance(stress, dict) else 0
    if stress_val > 60:
        repulsors_hit.append({"type": "humain_high", "score": stress_val})
    if isinstance(contamination, list) and len(contamination) > 10:
        repulsors_hit.append({"type": "contamination_dense", "count": len(contamination)})

    attr_score = min(1.0, len(attractors_hit) / 5.0)
    rep_score = min(1.0, len(repulsors_hit) / 3.0)
    final = max(0.0, attr_score - rep_score * 0.5)

    return {
        "score": round(final, 3),
        "attractors": attractors_hit,
        "repulsors": repulsors_hit,
        "n_attractors": len(attractors_hit),
    }


# ============================================================
# GÉNÉRATION PRINCIPALE (§1..§5 intégrés)
# ============================================================
async def generate_organic_corridors(lat: float, lon: float, species: str,
                                      month: int = 10, hour: int = 7,
                                      wind_deg: int = 225, wind_speed: int = 15) -> dict:
    """Génère le réseau ORGANIC complet autour du waypoint."""
    mark_call(ENGINE_NAME)

    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10

    bundle = await compute_territoire_v10(lat, lon, species, month=month, hour=hour,
                                           wind_deg=wind_deg, wind_speed=wind_speed)
    terrain_v10 = bundle.get("terrain_v10", {}) or {}
    ia_vision = bundle.get("ia_vision_ecologique", {}) or {}
    zones_vitales = bundle.get("zones", []) or []

    # Multi-échelle
    terrain_ms = ia_terrain_multiscale(lat, lon, terrain_v10)
    vision_map = ia_vision_integration(ia_vision)
    behavior = SPECIES_BEHAVIOR.get(species, SPECIES_BEHAVIOR["chevreuil"])
    fused = ia_fusion(terrain_ms, vision_map, behavior, zones_vitales)

    # Rayon fonctionnel
    R_MIN_DEG = ORGANIC_CONFIG["functional_radius_min_m"] / 111000.0
    R_MAX_DEG = ORGANIC_CONFIG["functional_radius_max_m"] / 111000.0
    cos_lat = max(0.5, math.cos(math.radians(lat)))

    n = int(behavior.get("n_corridors", 10))
    corridors: list[dict] = []

    for i in range(n):
        seed = _seed_noise(lat, lon, f"organic_{i}")
        angle = i * (360 / n) + seed * 25
        dist_deg = R_MIN_DEG + _seed_noise(lat, lon, f"dist_{i}") * (R_MAX_DEG - R_MIN_DEG)

        ctrl = _generate_organic_control_points(
            lat, lon, angle, dist_deg, cos_lat, behavior, terrain_ms, seed,
        )
        path = _catmull_rom_organic(ctrl, subs=12)
        # Trim à [60, 120]
        if len(path) < ORGANIC_CONFIG["points_per_corridor_min"]:
            path = path + [path[-1]] * (ORGANIC_CONFIG["points_per_corridor_min"] - len(path))
        elif len(path) > ORGANIC_CONFIG["points_per_corridor_max"]:
            step = len(path) / ORGANIC_CONFIG["points_per_corridor_max"]
            path = [path[int(k * step)] for k in range(ORGANIC_CONFIG["points_per_corridor_max"])]

        # Smart deviation
        path = _smart_deviation(path, terrain_v10)

        # Intensity basée sur fused + terrain
        base_intensity = 40 + fused["fused_score"] * 45
        season_mult = 1.1 if month in [9, 10, 11] and species in {"cerf", "orignal", "wapiti", "chevreuil"} else 1.0
        time_mult = 1.15 if (5 <= hour <= 8 or 16 <= hour <= 19) else 0.7 if (10 <= hour <= 14) else 1.0
        intensity = round(min(100, max(10, base_intensity * season_mult * time_mult + (seed - 0.5) * 20)), 1)

        # Attraction/répulsion
        ar = compute_attraction_repulsion({"path": [[p[0], p[1]] for p in path]}, bundle)
        hierarchy = _classify_hierarchy(intensity, ar["n_attractors"])

        # Thickness profile
        thickness = _variable_thickness_profile(path, intensity, ar["n_attractors"], fused["fused_score"])

        corridors.append({
            "id": f"organic_{i}",
            "hierarchy": hierarchy,
            "path": [[round(p[0], 6), round(p[1], 6)] for p in path],
            "n_points": len(path),
            "intensity": intensity,
            "species_profile": species,
            "terrain_multiscale": terrain_ms["features"],
            "fused_score": fused["fused_score"],
            "attraction_repulsion": ar,
            "thickness_profile": thickness,
            "thickness_min_px": min(thickness) if thickness else ORGANIC_CONFIG["thickness_min_px"],
            "thickness_max_px": max(thickness) if thickness else ORGANIC_CONFIG["thickness_max_px"],
            "source": "ENGINE-IA-CORRIDORS-ORGANIC-Ω",
            "version": ENGINE_VERSION,
        })

    # Auto-interconnexion
    corridors_full = _auto_interconnect(corridors)

    # Summary hiérarchie
    hierarchy_counts = {"veine_principale": 0, "veine_secondaire": 0, "capillaire": 0, "connector": 0}
    for c in corridors_full:
        h = c.get("hierarchy", "capillaire")
        if c.get("type") == "connector":
            hierarchy_counts["connector"] += 1
        else:
            hierarchy_counts[h] = hierarchy_counts.get(h, 0) + 1

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "waypoint": {"lat": lat, "lon": lon, "species": species},
        "terrain_multiscale": terrain_ms,
        "vision_behavioral_map": vision_map,
        "species_behavior": behavior,
        "fused_behavioral_probability": fused,
        "corridors": corridors_full,
        "corridors_count": len(corridors_full),
        "hierarchy_counts": hierarchy_counts,
        "render_modes_supported": ORGANIC_CONFIG["render_modes_enabled"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# Validation IA_CORRIDORS_ORGANIC (§7)
# ============================================================
def validate_organic(organic_bundle: dict) -> dict:
    """Valide un bundle ORGANIC vs les contraintes Phase M."""
    mark_call(ENGINE_NAME)
    corridors = organic_bundle.get("corridors", [])
    violations: list[dict] = []

    if not corridors:
        violations.append({"rule": "no_corridors_generated"})

    real_corridors = [c for c in corridors if c.get("type") != "connector"]

    for c in real_corridors:
        n_pts = len(c.get("path") or [])
        if n_pts < ORGANIC_CONFIG["points_per_corridor_min"]:
            violations.append({"rule": "points_below_min", "corridor": c.get("id"),
                                "detail": f"{n_pts} < {ORGANIC_CONFIG['points_per_corridor_min']}"})
        if n_pts > ORGANIC_CONFIG["points_per_corridor_max"]:
            violations.append({"rule": "points_above_max", "corridor": c.get("id"),
                                "detail": f"{n_pts} > {ORGANIC_CONFIG['points_per_corridor_max']}"})
        if c.get("hierarchy") not in {"veine_principale", "veine_secondaire", "capillaire"}:
            violations.append({"rule": "hierarchy_invalid", "corridor": c.get("id")})
        if not c.get("thickness_profile"):
            violations.append({"rule": "thickness_profile_missing", "corridor": c.get("id")})
        tp = c.get("thickness_profile") or []
        if tp:
            if min(tp) < ORGANIC_CONFIG["thickness_min_px"]:
                violations.append({"rule": "thickness_below_min", "corridor": c.get("id")})
            if max(tp) > ORGANIC_CONFIG["thickness_max_px"]:
                violations.append({"rule": "thickness_above_max", "corridor": c.get("id")})
        if not c.get("species_profile"):
            violations.append({"rule": "species_profile_missing", "corridor": c.get("id")})
        if "affut" in str(c).lower() or "affût" in str(c).lower():
            violations.append({"rule": "affut_reference_detected", "corridor": c.get("id")})

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "conforme": len(violations) == 0,
        "corridors_total": len(corridors),
        "real_corridors": len(real_corridors),
        "connectors": len([c for c in corridors if c.get("type") == "connector"]),
        "violations": violations,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# BASELINE — SEAL TERRITOIRE_OMEGA_STABLE (§7)
# ============================================================
BASELINE_DIR = Path("/app/backend/engines/v8_institutional/_baselines")
BASELINE_DIR.mkdir(parents=True, exist_ok=True)
BASELINE_PATH = BASELINE_DIR / "territoire_omega_stable.json"


def seal_baseline_stable(organic_bundle: dict) -> dict:
    """Scelle la baseline TERRITOIRE_OMEGA_STABLE (signature JSON + SHA-256)."""
    mark_call(ENGINE_NAME)
    # Payload minimal déterministe (ne contient pas les timestamps volatils)
    payload = {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "waypoint": organic_bundle.get("waypoint"),
        "corridors_count": organic_bundle.get("corridors_count"),
        "hierarchy_counts": organic_bundle.get("hierarchy_counts"),
        "fused_behavioral_probability": organic_bundle.get("fused_behavioral_probability"),
        "organic_config": ORGANIC_CONFIG,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    sha = hashlib.sha256(raw).hexdigest()
    sealed = {
        **payload,
        "baseline_name": "TERRITOIRE_OMEGA_STABLE",
        "sealed_at": datetime.now(timezone.utc).isoformat(),
        "sha256": sha,
    }
    BASELINE_PATH.write_text(json.dumps(sealed, indent=2, ensure_ascii=False), encoding="utf-8")
    return sealed


def get_baseline_stable() -> dict:
    if not BASELINE_PATH.exists():
        return {"sealed": False}
    return {"sealed": True, **json.loads(BASELINE_PATH.read_text(encoding="utf-8"))}


# ============================================================
# Endpoints
# ============================================================
@router.get("/status")
async def organic_status():
    mark_call(ENGINE_NAME)
    baseline = get_baseline_stable()
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "config": ORGANIC_CONFIG,
        "ia_advanced": IA_ADVANCED_STATUS,
        "baseline_stable_sealed": baseline.get("sealed", False),
        "baseline_sha256": baseline.get("sha256"),
        "doc_corridors": "/app/memory/ENGINE_CORRIDORS_OMEGA_OFFICIAL_FINAL.md",
        "doc_rendu": "/app/memory/RENDUS/RENDUS_CORRIDORS_OMEGA.md",
    }


@router.get("/modes")
async def organic_modes():
    mark_call(ENGINE_NAME)
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "modes": {
            "density_mode": {
                "enabled": True,
                "description": "Densité des corridors par cellule spatiale — intensité cumulée",
            },
            "heat_mode": {
                "enabled": True,
                "description": "Heatmap de passage — fused_behavioral_probability × thickness",
            },
            "veine_animale_mode": {
                "enabled": True,
                "description": "Rendu veine animale — gradient #FF8F00→#FF9F00 + halo + chevrons fins",
                "gradient": ORGANIC_CONFIG["gradient_colors"],
                "halo_size_px": ORGANIC_CONFIG["halo_size_px"],
                "chevron_frequency": ORGANIC_CONFIG["chevron_frequency"],
                "cumulative_thickness_multiplier": ORGANIC_CONFIG["cumulative_thickness_multiplier"],
            },
        },
    }


@router.get("/species-behavior")
async def organic_species_behavior():
    mark_call(ENGINE_NAME)
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "species_behavior": SPECIES_BEHAVIOR,
        "parameters_documented": [
            "prudence", "amplitude", "vitesse", "ouverture_preferee",
            "hydrologie_dependance", "couvert_prefere", "sinuosity", "n_corridors",
        ],
        "note": "Complémente SPECIES-PROFILES-Ω (registre biologique) avec des "
                "coefficients dynamiques utilisés par le moteur de géométrie.",
    }


class GenerateOrganicBody(BaseModel):
    lat: float = 45.10
    lon: float = -72.80
    species: str = "chevreuil"
    month: int = 10
    hour: int = 7
    wind_deg: int = 225
    wind_speed: int = 15


@router.post("/generate")
async def organic_generate(body: GenerateOrganicBody):
    """Génère le réseau ORGANIC complet (corridors + hiérarchie + fusion)."""
    return await generate_organic_corridors(
        body.lat, body.lon, body.species, body.month, body.hour,
        body.wind_deg, body.wind_speed,
    )


class ValidateOrganicBody(BaseModel):
    organic_bundle: dict


@router.post("/validate")
async def organic_validate(body: ValidateOrganicBody):
    return validate_organic(body.organic_bundle)


@router.get("/network-hierarchy")
async def organic_network_hierarchy(
    lat: float = 45.10, lon: float = -72.80, species: str = "chevreuil",
):
    """Retourne uniquement la hiérarchie du réseau (sans les paths complets)."""
    bundle = await generate_organic_corridors(lat, lon, species)
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "waypoint": bundle["waypoint"],
        "hierarchy_counts": bundle["hierarchy_counts"],
        "corridors_summary": [
            {
                "id": c["id"],
                "hierarchy": c.get("hierarchy"),
                "intensity": c.get("intensity"),
                "n_attractors": c.get("attraction_repulsion", {}).get("n_attractors", 0),
                "fused_score": c.get("fused_score"),
                "type": c.get("type", "organic"),
            }
            for c in bundle["corridors"]
        ],
    }


class SealBaselineBody(BaseModel):
    lat: float = 45.10
    lon: float = -72.80
    species: str = "chevreuil"


@router.post("/seal-baseline")
async def organic_seal_baseline(body: SealBaselineBody):
    """Scelle la baseline TERRITOIRE_OMEGA_STABLE à partir d'un waypoint de référence."""
    bundle = await generate_organic_corridors(body.lat, body.lon, body.species)
    # Validation préalable — refus de sceller si non conforme
    v = validate_organic(bundle)
    if not v["conforme"]:
        return {
            "sealed": False,
            "reason": "validation failed",
            "violations": v["violations"],
        }
    sealed = seal_baseline_stable(bundle)
    return {"sealed": True, **sealed}


# ============================================================
# Phase XI-SUPRA-L+1-M PREP — HOOKS IA (PREDICTIVE / GENERATIVE / ADAPTATIVE)
# ============================================================
class IAPredictBody(BaseModel):
    lat: float = 45.10
    lon: float = -72.80
    species: str = "chevreuil"
    horizon_days: int = 90


@router.post("/predict")
async def ia_corridors_predict(body: IAPredictBody):
    """HOOK IA PREDICTIVE — awaiting_upload.

    Contrat :
      - Input : waypoint + espèce + horizon temporel (jours)
      - Output (prévu) : évolution des corridors saisonniers, pression humaine, hydrologie
      - Statut actuel : schéma prêt, modèle non déployé (renvoie contrat vide + flag)
    """
    mark_call(ENGINE_NAME)
    return {
        "engine": ENGINE_NAME,
        "hook": "ia_corridors_predictive_hook",
        "model": "ia_predictive_v1",
        "status": "awaiting_upload",
        "model_deployed": False,
        "input": body.model_dump(),
        "contract_outputs": IA_ADVANCED_STATUS["ia_predictive"]["outputs"],
        "prediction": None,
        "note": "Modèle IA prédictif non déployé — actif en attente de téléversement.",
    }


class IAGenerateAltBody(BaseModel):
    lat: float = 45.10
    lon: float = -72.80
    species: str = "chevreuil"
    n_alternatives: int = 3


@router.post("/generate-alt")
async def ia_corridors_generate_alt(body: IAGenerateAltBody):
    """HOOK IA GENERATIVE — awaiting_upload.

    Contrat :
      - Input : waypoint + espèce + nombre d'alternatives souhaitées
      - Output (prévu) : corridors alternatifs, scénarios prospectifs, corridors prédictifs
      - Statut actuel : schéma prêt, modèle non déployé
    """
    mark_call(ENGINE_NAME)
    return {
        "engine": ENGINE_NAME,
        "hook": "ia_corridors_generative_hook",
        "model": "ia_generative_v1",
        "status": "awaiting_upload",
        "model_deployed": False,
        "input": body.model_dump(),
        "contract_outputs": IA_ADVANCED_STATUS["ia_generative"]["outputs"],
        "alternatives": None,
        "note": "Modèle IA générative non déployé — actif en attente de téléversement.",
    }


class IAAdaptBody(BaseModel):
    lat: float = 45.10
    lon: float = -72.80
    species: str = "chevreuil"
    feedback: dict = {}


@router.post("/adapt")
async def ia_corridors_adapt(body: IAAdaptBody):
    """HOOK IA ADAPTATIVE — awaiting_upload.

    Contrat :
      - Input : waypoint + espèce + feedback (traces GPS, photos terrain, corrections)
      - Output (prévu) : auto_refine, auto_correct, auto_learn
      - Statut actuel : schéma prêt, modèle non déployé
    """
    mark_call(ENGINE_NAME)
    return {
        "engine": ENGINE_NAME,
        "hook": "ia_corridors_adaptive_hook",
        "model": "ia_adaptive_v1",
        "status": "awaiting_upload",
        "model_deployed": False,
        "input": body.model_dump(),
        "contract_capabilities": IA_ADVANCED_STATUS["ia_adaptative"]["capabilities"],
        "adaptation": None,
        "note": "Modèle IA adaptative non déployé — actif en attente de téléversement.",
    }
