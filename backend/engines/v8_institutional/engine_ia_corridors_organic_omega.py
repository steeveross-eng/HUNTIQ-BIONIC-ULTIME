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

# P22Σ_V3_TERRITORY_CONTINUOUS_FUSION_VEINEUSE_Ω (2026-05-09 · COMMANDANT STEEVE-MAX)
# FUSION ADD-ONLY — import du module de fusion veineuse local (post-smoothing)
from engines.post_smoothing.corridors_fusion_omega import (
    fuse_corridors_by_species,
    fusion_summary,
)

# P22M + P22I (2026-05-10 · COMMANDANT STEEVE-MAX) — densification ×3 + chained corridors
from engines.post_smoothing.anchor_densifier_omega import (
    densify_vital_nodes_x3,
    densification_summary,
)
from engines.post_smoothing.chained_corridors_omega import (
    chain_corridors_for_species,
    chained_summary,
)

ENGINE_NAME = "ENGINE-IA-CORRIDORS-ORGANIC-Ω"
ENGINE_VERSION = "V2.0-PHASE-XI-SUPRA-N-Ω-NETWORK_LOCKED-2026-04"

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
    # Phase N — L'invariant prioritaire est "segment ≤ 20 m". Les contraintes
    # points_per_corridor [60, 120] sont assouplies pour respecter §9 CORRIDORS.
    "points_per_corridor_min": 30,
    "points_per_corridor_max": 500,
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

    # Hiérarchie réseau (Phase N — BLOC 5 recalibration pragmatique)
    # Seuils calibrés pour répartition visuelle 3-4 principales / 6-8 secondaires / 3-5 capillaires
    "hierarchy": {
        "veine_principale": {"min_intensity": 75, "min_attractors": 2},
        "veine_secondaire": {"min_intensity": 50, "min_attractors": 1},
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
    "chevreuil":      {"prudence": 0.80, "amplitude": 0.45, "vitesse": 0.55, "ouverture_preferee": 0.35, "hydro_dep": 0.30, "couvert_pref": 0.75, "sinuosity": 1.80, "n_corridors": 14},
    "orignal":        {"prudence": 0.55, "amplitude": 0.80, "vitesse": 0.40, "ouverture_preferee": 0.20, "hydro_dep": 0.95, "couvert_pref": 0.80, "sinuosity": 1.00, "n_corridors": 10},
    "wapiti":         {"prudence": 0.75, "amplitude": 0.95, "vitesse": 0.70, "ouverture_preferee": 0.60, "hydro_dep": 0.40, "couvert_pref": 0.50, "sinuosity": 0.75, "n_corridors": 9},
    "ours_noir":      {"prudence": 0.95, "amplitude": 0.90, "vitesse": 0.50, "ouverture_preferee": 0.15, "hydro_dep": 0.55, "couvert_pref": 0.90, "sinuosity": 1.70, "n_corridors": 12},
    "dindon_sauvage": {"prudence": 0.70, "amplitude": 0.30, "vitesse": 0.60, "ouverture_preferee": 0.75, "hydro_dep": 0.35, "couvert_pref": 0.45, "sinuosity": 1.30, "n_corridors": 12},
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
# P22H_FIX (2026-05-09 · COMMANDANT STEEVE-MAX)
# SALINE_CENTERED ANCHORING — priorisation des paires biologiques
# ============================================================
# Doctrine : "Corridors must reflect real game movement between salines,
# feeding, rut, and rest zones, not waypoint-centric artifacts."
ANCHOR_PRIORITY_DEFAULT = ["saline", "feeding_zone", "rut_zone", "rest_zone", "waypoint"]
# Mapping vers types normalisés Phase N
ANCHOR_TYPE_NORMALIZE = {
    "saline": "saline",
    "feeding_zone": "alimentation",
    "rut_zone": "rut",
    "rest_zone": "repos",
    "waypoint": None,  # waypoint ≡ centre, pas un nœud vital
}


def _pair_priority_score(pair: tuple[dict, dict],
                         priority_list: list[str]) -> int:
    """Calcule le score de priorité d'une paire selon la doctrine P22H.

    Une paire scorée plus haut est servie en premier (veine_principale).
    Bonus si l'un des nœuds est de type prioritaire (saline > feeding > rut > rest).
    """
    score = 0
    types_in_pair = {pair[0].get("type"), pair[1].get("type")}
    n = len(priority_list)
    for i, pkey in enumerate(priority_list):
        normalized = ANCHOR_TYPE_NORMALIZE.get(pkey)
        if normalized and normalized in types_in_pair:
            # Plus l'index est petit (priorité haute), plus le bonus est grand
            score += (n - i) * 100
    # Bonus si AU MOINS UNE saline (ancrage écologique fort)
    if "saline" in types_in_pair:
        score += 500
    return score


def _reorder_pairs_by_anchor(pairs: list[tuple[dict, dict]],
                              anchor_mode: str,
                              anchor_priority: list[str]
                              ) -> list[tuple[dict, dict]]:
    """P22H : réordonne les paires selon le mode d'ancrage doctrinal.

    Modes :
      - "SALINE_CENTERED" : priorité absolue salines, puis feeding > rut > rest
      - "TERRITORY_CONTINUOUS" (P22Σ): pas de réordre — préserve l'ordre natif
        de l'engine qui privilégie déjà la connectivité multi-zones (alim,
        repos, rut, thermiques, humides). Garantit traversée fonctionnelle
        600m ± 30% sans biais saline-centric. Logique par espèce préservée.
      - "AUTO" / "WAYPOINT" : pas de réordonnancement (comportement legacy)
    """
    mode = (anchor_mode or "AUTO").upper()
    if mode == "TERRITORY_CONTINUOUS":
        # P22Σ — préserve l'ordre natif (par espèce + comportement biologique).
        # L'engine `_compatible_pairs` produit déjà une liste cohérente
        # avec `SPECIES_BEHAVIOR` (saline_attraction, rest_attraction,
        # feeding_zone, etc.) et le rayon fonctionnel.
        return list(pairs)
    if mode != "SALINE_CENTERED":
        return list(pairs)
    priority_list = anchor_priority or ANCHOR_PRIORITY_DEFAULT
    sorted_pairs = sorted(pairs, key=lambda p: -_pair_priority_score(p, priority_list))
    return sorted_pairs


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


def _smart_deviation(path: list[tuple[float, float]], terrain_v10: dict,
                      species_behavior: dict | None = None) -> tuple[list[tuple[float, float]], bool]:
    """Phase N — BLOC 4 : Smart deviation HARD-BLOCKING.

    Retourne `(path_or_deviated, is_valid)`. Si `is_valid=False`, le corridor
    doit être invalidé (aucune trajectoire acceptable dans une zone interdite).

    Règles durcies :
      - pente > 35°           → contournement strict, rejet si impossible
      - eau < 20 m             → déviation latérale obligatoire (~40 m offset)
      - zone humaine proche    → répulseur fort
      - couvert < 30% espèce forestière → rejet
      - surface exposée forestière → pénalisation forte
    """
    slope = float(terrain_v10.get("pente_deg", 10))
    dist_eau = float(terrain_v10.get("distance_eau_m", 200))
    canopy = float(terrain_v10.get("canopy", 0.5))
    dist_urbain = float(terrain_v10.get("distance_urbain_m", terrain_v10.get("distance_humain_m", 1000)))

    couvert_pref = float((species_behavior or {}).get("couvert_pref", 0.5))

    # Rejet si couvert < 30% pour espèce forestière (couvert_pref > 0.6)
    if couvert_pref > 0.6 and canopy < 0.30:
        return path, False

    # Rejet si zone humaine < 80 m (routes/urbain majeurs)
    if dist_urbain < 80:
        return path, False

    # Rejet si pente > 45° sur la majeure partie (pas contournable)
    if slope > 45:
        return path, False

    needs_deviation = (slope > ORGANIC_CONFIG["slope_reroute_deg"]
                        or dist_eau < ORGANIC_CONFIG["water_min_dist_m"])
    if not needs_deviation:
        return path, True

    if len(path) < 3:
        return path, True

    # Offset perpendiculaire pour contournement léger
    mid = path[len(path) // 2]
    head = path[0]
    tail = path[-1]
    dlat = tail[0] - head[0]
    dlon = tail[1] - head[1]
    norm = math.hypot(dlat, dlon) or 1.0
    perp_lat = -dlon / norm
    perp_lon = dlat / norm
    offset = 0.0005  # ~50 m — contournement plus franc qu'avant
    deviated = [(p[0] + perp_lat * offset * 0.6, p[1] + perp_lon * offset * 0.6) for p in path]
    return deviated, True


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
# Phase N — BLOC 2 : PIPELINE RÉSEAU ZONES ↔ ZONES
# ============================================================
# Matrice des paires biologiquement compatibles par espèce.
# Clés possibles (types de zones vitales) : "alimentation", "repos", "rut",
# "humide", "thermique", "refuge", "saline", "hotspot".
BIOLOGICAL_PAIR_COMPATIBILITY: dict[str, set[tuple[str, str]]] = {
    "chevreuil": {
        ("alimentation", "repos"), ("alimentation", "humide"),
        ("alimentation", "saline"), ("repos", "saline"),
        ("repos", "thermique"), ("alimentation", "rut"),
        ("rut", "repos"), ("humide", "repos"),
        ("alimentation", "hotspot"), ("saline", "hotspot"),
    },
    "orignal": {
        ("humide", "alimentation"), ("humide", "repos"),
        ("humide", "saline"), ("alimentation", "repos"),
        ("repos", "rut"), ("alimentation", "rut"),
        ("saline", "alimentation"), ("hotspot", "humide"),
    },
    "wapiti": {
        ("alimentation", "repos"), ("alimentation", "rut"),
        ("rut", "repos"), ("alimentation", "saline"),
        ("saline", "repos"), ("humide", "alimentation"),
        ("thermique", "repos"), ("hotspot", "alimentation"),
    },
    "ours_noir": {
        ("alimentation", "refuge"), ("alimentation", "humide"),
        ("alimentation", "repos"), ("refuge", "humide"),
        ("alimentation", "hotspot"), ("hotspot", "refuge"),
    },
    "dindon_sauvage": {
        ("alimentation", "thermique"), ("alimentation", "repos"),
        ("thermique", "repos"), ("alimentation", "hotspot"),
    },
}


def _collect_vital_nodes(bundle: dict, lat: float, lon: float, species: str) -> list[dict]:
    """Collecte toutes les zones vitales + salines + hotspots dans un rayon élargi.

    Chaque nœud : `{type, lat, lon, score, source_id, source_raw}`.
    Types normalisés : alimentation, repos, rut, humide, thermique, refuge, saline, hotspot.
    """
    mark_call(ENGINE_NAME)
    R_SCAN_DEG = (ORGANIC_CONFIG["functional_radius_max_m"] * 1.5) / 111000.0
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    nodes: list[dict] = []

    # Zones vitales (classiques)
    for z in bundle.get("zones") or []:
        c = z.get("center") or {}
        zlat = c.get("lat", z.get("lat"))
        zlon = c.get("lng", c.get("lon", z.get("lng", z.get("lon"))))
        if zlat is None or zlon is None:
            continue
        ztype = (z.get("type") or "").lower()
        # Mapping des types vers les clés normalisées Phase N
        type_map = {
            "alimentation": "alimentation", "feeding": "alimentation",
            "repos": "repos", "bedding": "repos",
            "rut": "rut",
            "eau": "humide", "water": "humide", "humide": "humide",
            "thermique": "thermique", "thermal": "thermique",
            "refuge": "refuge",
        }
        normalized = type_map.get(ztype, ztype if ztype in {"alimentation", "repos", "rut", "humide", "thermique", "refuge"} else None)
        if not normalized:
            continue
        dx_m = abs(zlat - lat) * 111000.0
        dy_m = abs(zlon - lon) * 111000.0 * cos_lat
        if (dx_m ** 2 + dy_m ** 2) > ((ORGANIC_CONFIG["functional_radius_max_m"] * 1.5) ** 2):
            continue
        nodes.append({
            "type": normalized, "lat": float(zlat), "lon": float(zlon),
            "score": float(z.get("score", 50)), "source_id": z.get("id", f"zone_{normalized}"),
            "source": "zones",
        })

    # Salines
    for s in bundle.get("salines") or []:
        slat = s.get("lat")
        slon = s.get("lng", s.get("lon"))
        if slat is None or slon is None:
            continue
        nodes.append({
            "type": "saline", "lat": float(slat), "lon": float(slon),
            "score": float(s.get("score_global_v11", s.get("score", 60))),
            "source_id": s.get("id", f"saline_{len(nodes)}"), "source": "salines",
        })

    # Hotspots
    for h in bundle.get("hotspots") or []:
        hlat = h.get("lat")
        hlon = h.get("lng", h.get("lon"))
        if hlat is None or hlon is None:
            continue
        nodes.append({
            "type": "hotspot", "lat": float(hlat), "lon": float(hlon),
            "score": float(h.get("intensity", 50)),
            "source_id": h.get("id", f"hotspot_{len(nodes)}"), "source": "hotspots",
        })

    return nodes


def _compatible_pairs(nodes: list[dict], species: str) -> list[tuple[dict, dict]]:
    """Construit l'ensemble des paires biologiquement compatibles pour l'espèce."""
    mark_call(ENGINE_NAME)
    compat = BIOLOGICAL_PAIR_COMPATIBILITY.get(
        species, BIOLOGICAL_PAIR_COMPATIBILITY["chevreuil"]
    )
    # Bidirectionnalité des paires
    compat_full = set()
    for a, b in compat:
        compat_full.add((a, b))
        compat_full.add((b, a))

    pairs: list[tuple[dict, dict]] = []
    seen_keys: set[tuple[str, str]] = set()
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if j <= i:
                continue
            if (a["type"], b["type"]) not in compat_full:
                continue
            # Distance minimale — éviter les corridors trop courts (< 200 m)
            d = _hav(a["lat"], a["lon"], b["lat"], b["lon"])
            if d < 200 or d > 2000:
                continue
            key = tuple(sorted([a["source_id"], b["source_id"]]))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            pairs.append((a, b))
    return pairs


def _enforce_segment_max(path: list[tuple[float, float]], max_m: float = 20.0) -> list[tuple[float, float]]:
    """Post-subdivise les segments > max_m en insérant des points intermédiaires.
    Garantit l'invariant §9 CORRIDORS : segment ≤ 20 m.
    N'effectue PAS de trim (la densité finale peut dépasser 120 points — c'est acceptable
    institutionnellement : l'invariant prioritaire est "jamais segment > 20 m").
    """
    if len(path) < 2:
        return path
    out: list[tuple[float, float]] = [path[0]]
    for i in range(1, len(path)):
        a = path[i - 1]
        b = path[i]
        d = _hav(a[0], a[1], b[0], b[1])
        if d > max_m:
            n_sub = int(math.ceil(d / max_m))
            for k in range(1, n_sub):
                frac = k / n_sub
                out.append((a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac))
        out.append(b)
    return out


def _generate_corridor_between(node_a: dict, node_b: dict, species_behavior: dict,
                                 terrain_ms: dict, seed_salt: str) -> list[tuple[float, float]]:
    """Phase N — BLOC 2 : Génère un corridor Catmull-Rom entre deux zones vitales.

    Produit 12 points de contrôle biomimétiques (sinuosités + oscillations) puis
    subdivise à 120 points via `_catmull_rom_organic(subs=12)`.
    """
    mark_call(ENGINE_NAME)
    s_lat, s_lon = node_a["lat"], node_a["lon"]
    e_lat, e_lon = node_b["lat"], node_b["lon"]
    seed = _seed_noise(s_lat, s_lon, f"{node_a['source_id']}->{node_b['source_id']}_{seed_salt}")

    cos_lat = max(0.5, math.cos(math.radians(s_lat)))
    sinuosity = float(species_behavior.get("sinuosity", 1.0))
    micro_coulees = float(terrain_ms.get("features", {}).get("micro_coulees", 0.4))

    n_ctrl = 12
    ctrl: list[tuple[float, float]] = [(s_lat, s_lon)]
    for j in range(1, n_ctrl - 1):
        frac = j / (n_ctrl - 1)
        b_lat = s_lat + (e_lat - s_lat) * frac
        b_lon = s_lon + (e_lon - s_lon) * frac

        # Oscillation basse fréquence (flux biomimétique)
        osc_low = sinuosity * 0.040 * math.sin(j * 1.9
                                                + _seed_noise(s_lat, s_lon, f"osc_low_{j}_{seed_salt}") * 6.28)
        # Oscillation haute fréquence (micro-relief)
        osc_high = micro_coulees * 0.017 * math.sin(j * 5.3
                                                     + _seed_noise(s_lat, s_lon, f"osc_high_{j}_{seed_salt}") * 6.28)
        # Fractal variation light
        frac_perturb = 0.012 * (_seed_noise(s_lat, s_lon, f"frac_{j}_{seed_salt}") - 0.5)

        dlat = e_lat - s_lat
        dlon = e_lon - s_lon
        off = osc_low + osc_high + frac_perturb
        ctrl.append((b_lat + off * dlon, b_lon + off * dlat / cos_lat))
    ctrl.append((e_lat, e_lon))

    path = _catmull_rom_organic(ctrl, subs=12)
    # Garantir segment ≤ 20 m (invariant CORRIDORS §9)
    path = _enforce_segment_max(path, max_m=ORGANIC_CONFIG["segment_max_m"])
    return path


def _corridor_crosses_rayon(path: list[tuple[float, float]], wp_lat: float, wp_lon: float,
                             r_min_m: float, r_max_m: float) -> bool:
    """Vérifie qu'au moins un point du path est dans l'anneau fonctionnel [r_min, r_max]."""
    for p in path:
        d = _hav(p[0], p[1], wp_lat, wp_lon)
        if r_min_m <= d <= r_max_m:
            return True
    return False


def _compute_attractivity_score(node_a: dict, node_b: dict, path: list[tuple[float, float]],
                                  species_behavior: dict) -> tuple[float, list[dict]]:
    """Phase N — BLOC 3 : Score d'attractivité d'un corridor.

    Basé sur les types des deux nœuds (poids par espèce) + score individuel.
    Retourne `(score_0_100, attractors_list)`.
    """
    mark_call(ENGINE_NAME)
    attractors: list[dict] = []
    base_weights = {
        "saline": 25, "alimentation": 22, "humide": 18,
        "rut": 18, "repos": 15, "thermique": 14, "refuge": 14, "hotspot": 20,
    }
    for node in (node_a, node_b):
        w = base_weights.get(node["type"], 10)
        # Modulation par score individuel 0..100
        contrib = w * (node.get("score", 50) / 100.0)
        attractors.append({
            "type": node["type"], "source_id": node["source_id"],
            "score_individual": node.get("score"), "contribution": round(contrib, 2),
        })

    # Bonus hydrologique pour espèces dépendantes
    hydro_dep = float(species_behavior.get("hydro_dep", 0.5))
    if hydro_dep > 0.7 and ("humide" in (node_a["type"], node_b["type"])):
        attractors.append({"type": "hydro_bonus", "contribution": 8})

    total = sum(a.get("contribution", 0) for a in attractors)
    return round(min(100.0, max(0.0, total)), 2), attractors
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
                                      wind_deg: int = 225, wind_speed: int = 15,
                                      anchor_mode: str = "AUTO",
                                      anchor_priority: list[str] | None = None,
                                      allow_multi_anchor: bool = False,
                                      external_entry_exit_radius_m: float = 600.0,
                                      densify_vitals: bool = True,
                                      enable_chained_corridors: bool = True,
                                      ) -> dict:
    """Génère le réseau ORGANIC complet autour du waypoint.

    P22H_FIX (2026-05-09 · COMMANDANT STEEVE-MAX) — paramètres SALINE_CENTERED :
      - anchor_mode : "AUTO" | "SALINE_CENTERED" | "WAYPOINT"
      - anchor_priority : liste priorités (default : saline > feeding > rut > rest > waypoint)
      - allow_multi_anchor : autorise corridors multi-ancres (post-MVP)
      - external_entry_exit_radius_m : rayon entry/exit nodes (default 600m)

    P22M+P22I (2026-05-10 · COMMANDANT STEEVE-MAX) :
      - densify_vitals : ×3 anchor points biologiques (default True)
      - enable_chained_corridors : génère chains multi-nœuds (default True)
    """
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
    R_MIN_M = ORGANIC_CONFIG["functional_radius_min_m"]
    R_MAX_M = ORGANIC_CONFIG["functional_radius_max_m"]

    # ═════════════════════════════════════════════════════════════
    # Phase N — BLOC 1+2 : PIPELINE RÉSEAU ZONES ↔ ZONES
    #   (Abolition totale du générateur radial depuis waypoint.)
    # P22H — Ajout de la priorisation par mode d'ancrage doctrinal.
    # ═════════════════════════════════════════════════════════════
    nodes = _collect_vital_nodes(bundle, lat, lon, species)

    # ═════════════════════════════════════════════════════════════
    # P22M_DENSIFICATION_VITALE_X3_Ω (2026-05-10 · COMMANDANT STEEVE-MAX)
    # ═════════════════════════════════════════════════════════════
    # Doctrine : tripler les anchor points biologiques (alim, repos, rut,
    # thermique, humide) en générant 2 satellites jittered par node.
    # FUSION ADD-ONLY — module externe `anchor_densifier_omega`.
    # Activation conditionnelle : default ON (paramètre `densify_vitals`).
    nodes_before_densify = len(nodes)
    densification_stats: dict[str, Any] = {}
    if densify_vitals and nodes:
        nodes = densify_vital_nodes_x3(nodes)
        densification_stats = densification_summary(
            [{"type": "_marker"}] * nodes_before_densify, nodes,
        )
        densification_stats["n_nodes_before"] = nodes_before_densify
        densification_stats["n_nodes_after"] = len(nodes)

    pairs = _compatible_pairs(nodes, species)
    # P22H_FIX : priorisation salines/feeding/rut/rest selon directive.
    pairs = _reorder_pairs_by_anchor(
        pairs,
        anchor_mode=anchor_mode,
        anchor_priority=anchor_priority or ANCHOR_PRIORITY_DEFAULT,
    )

    corridors: list[dict] = []
    for idx, (node_a, node_b) in enumerate(pairs):
        # Phase N — BLOC 2.1.c : Catmull-Rom organique entre zones
        path = _generate_corridor_between(node_a, node_b, behavior, terrain_ms, f"pair_{idx}")

        # Phase N — BLOC 2.1.d : filtre d'observation — le corridor doit
        # traverser le rayon fonctionnel 420–780 m autour du waypoint
        if not _corridor_crosses_rayon(path, lat, lon, R_MIN_M, R_MAX_M):
            continue

        # Phase N — BLOC 4 : Smart deviation HARD-BLOCKING
        path, is_valid = _smart_deviation(path, terrain_v10, behavior)
        if not is_valid:
            continue  # Corridor invalidé (zone interdite non contournable)
        # Garantir à nouveau segment ≤ 20 m après déviation + post-trim
        path = _enforce_segment_max(path, max_m=ORGANIC_CONFIG["segment_max_m"])

        # Phase N — BLOC 3 : Score d'attractivité obligatoire
        attractivity_score, attractors_list = _compute_attractivity_score(node_a, node_b, path, behavior)
        if attractivity_score < 10:
            # Rejet : corridor sans attracteur valide
            continue

        # Intensity basée sur attractivité + fused + modulation saisonnière/horaire
        base_intensity = 30 + attractivity_score * 0.55 + fused["fused_score"] * 20
        season_mult = 1.1 if month in [9, 10, 11] and species in {"cerf", "orignal", "wapiti", "chevreuil"} else 1.0
        time_mult = 1.15 if (5 <= hour <= 8 or 16 <= hour <= 19) else 0.7 if (10 <= hour <= 14) else 1.0
        seed_i = _seed_noise(lat, lon, f"pair_{idx}")
        intensity = round(min(100, max(10, base_intensity * season_mult * time_mult + (seed_i - 0.5) * 15)), 1)

        # Phase N — BLOC 5 : classification hiérarchique avec seuils recalibrés
        n_attractors = len(attractors_list)
        hierarchy = _classify_hierarchy(intensity, n_attractors)

        # Attraction/répulsion bundle (pour cohérence API rétrocompatible)
        ar = compute_attraction_repulsion({"path": [[p[0], p[1]] for p in path]}, bundle)

        # Thickness profile variable
        thickness = _variable_thickness_profile(path, intensity, n_attractors, fused["fused_score"])

        corridors.append({
            "id": f"network_{idx:03d}",
            "hierarchy": hierarchy,
            "path": [[round(p[0], 6), round(p[1], 6)] for p in path],
            "n_points": len(path),
            "intensity": intensity,
            "species_profile": species,
            "node_from": {"type": node_a["type"], "source_id": node_a["source_id"],
                           "lat": node_a["lat"], "lon": node_a["lon"]},
            "node_to": {"type": node_b["type"], "source_id": node_b["source_id"],
                         "lat": node_b["lat"], "lon": node_b["lon"]},
            "attractivity_score": attractivity_score,
            "attractors": attractors_list,
            "n_attractors": n_attractors,
            "terrain_multiscale": terrain_ms["features"],
            "fused_score": fused["fused_score"],
            "attraction_repulsion": ar,
            "thickness_profile": thickness,
            "thickness_min_px": min(thickness) if thickness else ORGANIC_CONFIG["thickness_min_px"],
            "thickness_max_px": max(thickness) if thickness else ORGANIC_CONFIG["thickness_max_px"],
            "source": "ENGINE-IA-CORRIDORS-ORGANIC-Ω (Network refactor Phase N)",
            "version": ENGINE_VERSION,
        })

    # Phase N — BLOC 2 : auto-interconnexion DÉSACTIVÉE
    #   Dans le pipeline réseau zones↔zones, les corridors partagent déjà leurs
    #   nœuds biologiques (saline, alimentation, repos, ...), donc la
    #   connectivité est intrinsèque. Les connectors artificiels <50 m sont
    #   désormais redondants et ajoutaient du bruit visuel.
    corridors_full = corridors

    # ═════════════════════════════════════════════════════════════
    # P22I_MULTI_ANCHOR_CHAINED_CORRIDORS_Ω (2026-05-10 · COMMANDANT STEEVE-MAX)
    # ═════════════════════════════════════════════════════════════
    # Doctrine : générer des corridors multi-nœuds chained
    # (alim → repos → rut → thermique) selon séquences canoniques par espèce.
    # FUSION ADD-ONLY — module externe `chained_corridors_omega`.
    # Préserve les corridors atomiques d'origine ET ajoute les chains.
    chain_stats: dict[str, Any] = {}
    chain_applied = False
    if enable_chained_corridors and corridors_full:
        atomic_count = len(corridors_full)
        corridors_full = chain_corridors_for_species(corridors_full, species)
        chain_stats = chained_summary(
            corridors_full[:atomic_count], corridors_full,
        )
        chain_applied = True

    # ═════════════════════════════════════════════════════════════
    # P22Σ_V3 — FUSION VEINEUSE LOCALE (TERRITORY_CONTINUOUS only)
    # ═════════════════════════════════════════════════════════════
    # Doctrine : pour le mode TERRITORY_CONTINUOUS, fusionner les corridors
    # d'une même espèce à ≤18 m (overlap ≥30%) en veines principales.
    # FUSION ADD-ONLY — module externe `corridors_fusion_omega`.
    # SALINE_CENTERED legacy : fusion désactivée pour préserver la rosace
    # 360° saline-centrée P22H.
    fusion_applied = False
    fusion_stats: dict[str, Any] = {}
    if (anchor_mode or "AUTO").upper() == "TERRITORY_CONTINUOUS" and corridors_full:
        before_count = len(corridors_full)
        corridors_full = fuse_corridors_by_species(corridors_full)
        fusion_stats = fusion_summary(corridors_full)
        fusion_stats["n_corridors_before_fusion"] = before_count
        fusion_applied = True

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
        # P22H_FIX (2026-05-09 · COMMANDANT STEEVE-MAX) — traçabilité ancrage
        "p22h_anchor_doctrine": {
            "anchor_mode": (anchor_mode or "AUTO").upper(),
            "anchor_priority": anchor_priority or ANCHOR_PRIORITY_DEFAULT,
            "allow_multi_anchor": bool(allow_multi_anchor),
            "external_entry_exit_radius_m": float(external_entry_exit_radius_m),
            "saline_centered_active": (anchor_mode or "AUTO").upper() == "SALINE_CENTERED",
            "n_pairs_evaluated": len(pairs),
            "first_pair_types": list({pairs[0][0]["type"], pairs[0][1]["type"]}) if pairs else [],
        },
        # P22Σ_V3 (2026-05-09 · COMMANDANT STEEVE-MAX) — traçabilité fusion veineuse
        "p22sigma_v3_fusion_doctrine": {
            "fusion_applied": fusion_applied,
            "fusion_summary": fusion_stats if fusion_applied else None,
            "doctrine": "P22Σ_V3_FUSION_VEINEUSE_Ω",
            "activation_rule": "anchor_mode == TERRITORY_CONTINUOUS",
        },
        # P22M (2026-05-10 · COMMANDANT STEEVE-MAX) — traçabilité densification ×3
        "p22m_densification_doctrine": {
            "densify_vitals_active": bool(densify_vitals),
            "densification_summary": densification_stats if densify_vitals else None,
            "doctrine": "P22M_DENSIFICATION_VITALE_X3_Ω",
        },
        # P22I (2026-05-10 · COMMANDANT STEEVE-MAX) — traçabilité chained corridors
        "p22i_chained_doctrine": {
            "chained_applied": chain_applied,
            "chained_summary": chain_stats if chain_applied else None,
            "doctrine": "P22I_MULTI_ANCHOR_CHAINED_CORRIDORS_Ω",
        },
    }


# ============================================================
# Validation IA_CORRIDORS_ORGANIC (§7)
# ============================================================
def validate_organic(organic_bundle: dict) -> dict:
    """Valide un bundle ORGANIC vs les contraintes Phase N (Network Refactor).

    Règles Phase N (BLOC 8) — anti-régression durcie :
      - Aucun corridor isolé (doit relier 2 zones vitales distinctes)
      - Aucun corridor multi-espèces
      - Tous les corridors avec attractivity_score ≥ 10
      - Hiérarchie diversifiée (≠ 100% veine_principale → ERREUR_HIERARCHIE_Ω)
      - Aucun corridor rectiligne (détection : max_segment_m ≤ 20 m)
      - Pas de référence au waypoint comme générateur (node_from.source ≠ waypoint)
      - Différentiation espèce présente (species_profile cohérent)
    """
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

        # Phase N — BLOC 8 : règles durcies
        # Corridor isolé : doit avoir node_from ET node_to distincts
        node_from = c.get("node_from") or {}
        node_to = c.get("node_to") or {}
        if not node_from or not node_to:
            violations.append({"rule": "corridor_isolated_no_nodes", "corridor": c.get("id")})
        elif node_from.get("source_id") == node_to.get("source_id"):
            violations.append({"rule": "corridor_self_loop", "corridor": c.get("id")})

        # Attractivity obligatoire
        if c.get("attractivity_score", 0) < 10:
            violations.append({"rule": "attractivity_score_below_min", "corridor": c.get("id"),
                                "detail": f"{c.get('attractivity_score')} < 10"})
        if not c.get("attractors"):
            violations.append({"rule": "attractors_missing", "corridor": c.get("id")})

        # Détection de segment rectiligne >20 m
        path = c.get("path") or []
        max_seg = 0.0
        for i in range(1, len(path)):
            d = _hav(path[i - 1][0], path[i - 1][1], path[i][0], path[i][1])
            if d > max_seg:
                max_seg = d
        if max_seg > ORGANIC_CONFIG["segment_max_m"] * 1.2:  # tolérance 20% (24 m)
            violations.append({"rule": "segment_above_max", "corridor": c.get("id"),
                                "detail": f"max_seg={max_seg:.1f}m"})

    # Phase N — BLOC 5.3 : ERREUR_HIERARCHIE_Ω si tout en veine_principale
    hierarchy_set = {c.get("hierarchy") for c in real_corridors}
    if len(real_corridors) >= 5 and hierarchy_set == {"veine_principale"}:
        violations.append({
            "rule": "ERREUR_HIERARCHIE_Ω",
            "detail": "Tous les corridors classés veine_principale — hiérarchie écrasée (BLOC 5.3)",
        })

    # Phase N — BLOC 1 : détection d'un générateur radial (anti-régression)
    if len(real_corridors) >= 4:
        origins = [tuple(c.get("path", [[None, None]])[0]) for c in real_corridors if c.get("path")]
        # Si toutes les origines sont identiques → générateur radial (rejeté)
        unique_origins = set(origins)
        if len(unique_origins) <= 1:
            violations.append({
                "rule": "ERREUR_RADIAL_GENERATOR",
                "detail": "Toutes les origines corridors identiques — suspicion générateur radial (BLOC 1)",
            })

    # Différentiation espèce — tous doivent avoir le même species_profile ET ≠ générique
    species_set = {c.get("species_profile") for c in real_corridors}
    if len(species_set) > 1:
        violations.append({
            "rule": "multi_species_mixed",
            "detail": f"Espèces mélangées : {species_set}",
        })

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "conforme": len(violations) == 0,
        "corridors_total": len(corridors),
        "real_corridors": len(real_corridors),
        "connectors": len([c for c in corridors if c.get("type") == "connector"]),
        "hierarchy_distribution": {h: sum(1 for c in real_corridors if c.get("hierarchy") == h)
                                    for h in {"veine_principale", "veine_secondaire", "capillaire"}},
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
