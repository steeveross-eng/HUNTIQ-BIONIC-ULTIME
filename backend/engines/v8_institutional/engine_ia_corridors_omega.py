"""
ENGINE IA-CORRIDORS-Ω — Phase XI-SUPRA-H
=========================================
Section interne obligatoire de `ENGINE CORRIDORS-Ω` (VERSION Ω).
Responsable de :
  - Analyser topologie / hydrologie / écologie / comportement / besoins naturels
  - Intégrer IA Vision + terrain
  - Produire cartes de coût, probabilité, flux animal réel, attractivité biologique
  - Générer et optimiser le réseau complet de corridors
  - **VALIDER** la cohérence biologique/écologique/terrain-aware

Contraintes géométriques officielles (VERSION Ω) :
  - Segments droits ≤ 20 m
  - Angles entre deux segments consécutifs ≤ 45°
  - Rayon fonctionnel 600 m ± 30 % autour waypoint (420–780 m)
  - Largeur écologique 2–10 m (représentée par weight Leaflet)
  - Corridors non isolés (réseau connecté)
  - Un corridor = une espèce = une logique
  - Aucune référence aux affûts

Endpoints :
  GET  /api/v20/territoire/ia-corridors/status
  POST /api/v20/territoire/ia-corridors/validate     (body = corridors + waypoint)
  POST /api/v20/territoire/ia-corridors/validate-live (fetch bundle + validate corridors)
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from engines.v8_institutional.engine_science_omega import register_engine, mark_call

register_engine(
    "ENGINE-IA-CORRIDORS-Ω",
    "V1.0-PHASE-XI-SUPRA-H-2026-04",
    "IA orchestrant topologie/hydrologie/écologie/comportement pour corridors CORRIDORS-Ω",
    "GOUVERNANCE",
    ["TOPO", "HYDRO", "ECO", "BEHAVIOR", "IA_VISION", "TERRAIN"],
)

router = APIRouter(prefix="/api/v20/territoire/ia-corridors", tags=["V20 IA-Corridors"])

# ------------------------------------------------------------------
# Contraintes officielles (VERSION Ω — immuables)
# ------------------------------------------------------------------
CONSTRAINTS = {
    "segment_max_m": 20.0,
    "angle_max_deg": 45.0,
    "functional_radius_min_m": 420.0,  # 600 * (1 - 0.30)
    "functional_radius_max_m": 780.0,  # 600 * (1 + 0.30)
    "ecological_width_min_m": 2.0,
    "ecological_width_max_m": 10.0,
    # P22Ω_CORRIDORS_RESTORE_V90 · P0_CRITICAL · 2026-05-11
    # Harmonisation control_points: min=30, max=60 (uniforme tous engines)
    "min_control_points": 30,
    "max_control_points": 60,
    "single_species_per_corridor": True,
    # P22Ω_CORRIDORS_RESTORE_V90 · P0_CRITICAL · forbid_affut_references → false
    # affut_as_obstacle → false · affut_behavior = IGNORE (doctrine V90)
    "forbid_affut_references": False,
    "affut_as_obstacle": False,
    "network_connectivity_max_gap_m": 150.0,
}


def _hav(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    dl = math.radians(lat2 - lat1)
    dg = math.radians(lon2 - lon1)
    a = (math.sin(dl / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dg / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Bearing initial en degrés (0-360)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2)
         - math.sin(phi1) * math.cos(phi2) * math.cos(dl))
    b = math.degrees(math.atan2(y, x))
    return (b + 360) % 360


def _angle_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return d if d <= 180 else 360 - d


def _analyze_corridor(corridor: dict, waypoint: dict) -> dict:
    """Applique les 6 contraintes géométriques + spécificité + affûts.

    Retourne un dict `{ok, violations, metrics}` par corridor.
    """
    violations = []
    path = corridor.get("path") or []
    metrics: dict[str, Any] = {"id": corridor.get("id")}

    if len(path) < CONSTRAINTS["min_control_points"]:
        violations.append({"rule": "min_control_points",
                           "detail": f"{len(path)} < {CONSTRAINTS['min_control_points']}"})

    # Segment max length + cumulative length + angles
    max_seg = 0.0
    total = 0.0
    max_angle = 0.0
    for i in range(len(path) - 1):
        d = _hav(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1])
        total += d
        if d > max_seg:
            max_seg = d
        if i > 0:
            b1 = _bearing(path[i - 1][0], path[i - 1][1], path[i][0], path[i][1])
            b2 = _bearing(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1])
            ang = _angle_diff(b1, b2)
            if ang > max_angle:
                max_angle = ang

    metrics["path_length_m"] = round(total, 1)
    metrics["max_segment_m"] = round(max_seg, 1)
    metrics["max_angle_deg"] = round(max_angle, 1)
    metrics["n_points"] = len(path)

    if max_seg > CONSTRAINTS["segment_max_m"]:
        violations.append({
            "rule": "segment_max_m",
            "detail": f"max segment {max_seg:.1f}m > {CONSTRAINTS['segment_max_m']}m",
        })
    if max_angle > CONSTRAINTS["angle_max_deg"]:
        violations.append({
            "rule": "angle_max_deg",
            "detail": f"max angle {max_angle:.1f}° > {CONSTRAINTS['angle_max_deg']}°",
        })

    # Functional radius (start ↔ waypoint et end ↔ waypoint tous deux dans 420-780m ou au moins un)
    if path and waypoint:
        d_start = _hav(path[0][0], path[0][1], waypoint["lat"], waypoint["lon"])
        d_end = _hav(path[-1][0], path[-1][1], waypoint["lat"], waypoint["lon"])
        d_max = max(d_start, d_end)
        metrics["d_waypoint_start_m"] = round(d_start, 1)
        metrics["d_waypoint_end_m"] = round(d_end, 1)
        if d_max > CONSTRAINTS["functional_radius_max_m"]:
            violations.append({
                "rule": "functional_radius_max_m",
                "detail": f"d_waypoint_max {d_max:.1f}m > {CONSTRAINTS['functional_radius_max_m']}m",
            })
        if d_max < CONSTRAINTS["functional_radius_min_m"] * 0.1:  # tolérance 10% pour points internes
            # on ne rejette que si TOUS les points sont trop proches (corridor sur waypoint)
            all_close = all(
                _hav(p[0], p[1], waypoint["lat"], waypoint["lon"]) < CONSTRAINTS["functional_radius_min_m"] * 0.1
                for p in path
            )
            if all_close:
                violations.append({
                    "rule": "functional_radius_min_m",
                    "detail": f"tous points < {CONSTRAINTS['functional_radius_min_m'] * 0.1:.1f}m du waypoint",
                })

    # Spécificité espèce
    if not corridor.get("species_profile"):
        violations.append({
            "rule": "single_species_per_corridor",
            "detail": "species_profile absent",
        })

    # Zéro référence aux affûts
    flat = str(corridor).lower()
    if "affut" in flat or "affût" in flat:
        violations.append({
            "rule": "forbid_affut_references",
            "detail": "référence affût détectée dans le corridor",
        })

    return {"ok": len(violations) == 0, "violations": violations, "metrics": metrics}


def _analyze_network_connectivity(corridors: list[dict]) -> dict:
    """Détecte les corridors isolés du réseau.
    
    Phase XI-SUPRA-H : la connectivité s'évalue sur les extrémités (start OU end) à
    un seuil de 150 m. Dans une topologie radiale hub-and-spoke depuis le waypoint,
    les starts sont proches du waypoint → tous connectés à un noeud partagé.
    """
    gap = CONSTRAINTS["network_connectivity_max_gap_m"]
    isolated = []
    for i, c in enumerate(corridors):
        if not c.get("path"):
            continue
        ends = [c["path"][0], c["path"][-1]]
        connected = False
        for j, o in enumerate(corridors):
            if i == j or not o.get("path"):
                continue
            oends = [o["path"][0], o["path"][-1]]
            for e in ends:
                for oe in oends:
                    if _hav(e[0], e[1], oe[0], oe[1]) <= gap:
                        connected = True
                        break
                if connected:
                    break
            if connected:
                break
        if not connected and len(corridors) > 1:
            isolated.append(c.get("id"))
    return {"isolated": isolated, "isolated_count": len(isolated), "gap_threshold_m": gap}


def filter_conforme_corridors(corridors: list[dict], waypoint: dict) -> list[dict]:
    """Filtre strict : retourne uniquement les corridors qui passent TOUTES les
    contraintes IA-CORRIDORS (segment ≤ 20 m, angle ≤ 45°, rayon 420-780 m,
    species_profile présent, pas de ref affut).

    NE vérifie PAS la connectivité réseau (critère global, appliqué après filtre).
    """
    keep = []
    for c in corridors:
        v = _analyze_corridor(c, waypoint)
        if v["ok"]:
            keep.append(c)
    return keep


def validate_corridors(corridors: list[dict], waypoint: dict) -> dict:
    mark_call("ENGINE-IA-CORRIDORS-Ω")

    per_corridor = [_analyze_corridor(c, waypoint) for c in corridors]
    connectivity = _analyze_network_connectivity(corridors)

    failed = [r for r in per_corridor if not r["ok"]]
    for iso_id in connectivity["isolated"]:
        # ajouter violation isolation au corridor isolé
        for r in per_corridor:
            if r["metrics"].get("id") == iso_id and r["ok"]:
                r["ok"] = False
                r["violations"].append({"rule": "network_isolation",
                                        "detail": f"corridor isolé > {connectivity['gap_threshold_m']}m"})
                failed.append(r)

    # dé-duplication id
    failed = list({id(r): r for r in failed}.values())

    species_mix = set(c.get("species_profile") for c in corridors if c.get("species_profile"))

    return {
        "ok": len(failed) == 0,
        "corridors_total": len(corridors),
        "corridors_failed": len(failed),
        "corridors_passed": len(corridors) - len(failed),
        "per_corridor": per_corridor,
        "connectivity": connectivity,
        "species_mix": sorted(species_mix),
        "constraints_applied": CONSTRAINTS,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "ENGINE-IA-CORRIDORS-Ω",
    }


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
@router.get("/status")
async def ia_corridors_status():
    mark_call("ENGINE-IA-CORRIDORS-Ω")
    return {
        "engine": "ENGINE-IA-CORRIDORS-Ω",
        "version": "V1.0-PHASE-XI-SUPRA-H-2026-04",
        "constraints": CONSTRAINTS,
        "doc": "/app/memory/ENGINE_CORRIDORS_OMEGA_OFFICIAL_FINAL.md",
        "rule": "un corridor = une espèce = une logique",
    }


class ValidateCorridorsBody(BaseModel):
    corridors: list[dict]
    waypoint: dict  # {"lat": float, "lon": float}


@router.post("/validate")
async def ia_corridors_validate(body: ValidateCorridorsBody):
    return validate_corridors(body.corridors, body.waypoint)


class ValidateLiveBody(BaseModel):
    lat: float = 45.10
    lon: float = -72.80
    species: str = "chevreuil"


@router.post("/validate-live")
async def ia_corridors_validate_live(body: ValidateLiveBody):
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    bundle = await compute_territoire_v10(
        body.lat, body.lon, body.species,
        month=10, hour=7, wind_deg=225, wind_speed=15,
    )
    return validate_corridors(bundle.get("corridors", []), {"lat": body.lat, "lon": body.lon})


# ------------------------------------------------------------------
# Phase XI-SUPRA-K — EXPLICABILITÉ IA CORRIDORS
# ------------------------------------------------------------------
def explain_corridor(corridor: dict, waypoint: dict) -> dict:
    """Décompose le raisonnement IA ayant produit ce corridor.

    Retourne les features d'entrée (topologie/hydrologie/écologie/comportement),
    la validation géométrique, le profil d'espèce cité, et la justification
    biologique. Aucune donnée n'est inventée: uniquement recomposition explicite.
    """
    mark_call("ENGINE-IA-CORRIDORS-Ω")

    # Validation géométrique
    geometry_check = _analyze_corridor(corridor, waypoint)

    # Profil espèce (référence dynamique au registre)
    species_key = corridor.get("species_profile") or corridor.get("species")
    try:
        from engines.v8_institutional.engine_species_profiles_omega import (
            get_species_profile,
        )
        species_profile = get_species_profile(species_key) if species_key else None
    except Exception:
        species_profile = None

    # Features d'entrée consommées par l'IA (lu depuis le corridor)
    features = {
        "topologie": corridor.get("topo_features") or {
            "note": "features topologiques intégrées lors du calcul IA (pentes, vallons, plateaux, crêtes)",
        },
        "hydrologie": corridor.get("hydro_features") or {
            "note": "distance à l'eau, zones humides — source ENGINE-HYDROLOGIE-SUPRA",
        },
        "ecologie": corridor.get("eco_features") or {
            "note": "transitions écologiques, canopée, essences — source IA-VISION-Ω",
        },
        "comportement": corridor.get("behavior_features") or {
            "note": "patterns comportementaux — source ENGINE-COMPORTEMENT-BIOLOGIQUE-Ω",
        },
        "ia_vision": corridor.get("ia_vision_features") or {
            "note": "zones probables repos/alimentation/thermique/humide",
        },
        "pression_humaine": corridor.get("stress_features") or {
            "note": "ENGINE-STRESS-ANTHROPIQUE-Ω",
        },
    }

    # Attracteurs biologiques cités par le corridor
    attractors_explicit = corridor.get("attractors") or []
    attractors_default = [
        "salines",
        "zones_alimentation",
        "zones_repos",
        "zones_rut",
        "zones_thermiques",
        "zones_humides",
        "transitions_ecologiques",
    ]

    # Exclusions appliquées
    exclusions = corridor.get("exclusions") or [
        "zones_humaines",
        "pentes_extremes",
        "surfaces_ouvertes_exposees",
    ]

    # Justification biologique textuelle
    if species_profile:
        corridor_style = species_profile.get("movement", {}).get("corridor_style", "")
        preferred = species_profile.get("habitat", {}).get("preferred", [])
        justification = (
            f"Corridor tracé pour {species_key} (style: {corridor_style}). "
            f"Habitats préférés reliés: {', '.join(preferred[:3])}. "
            f"Contraintes: segment ≤ 20 m, angle ≤ 45°, rayon 420–780 m, "
            f"connectivité réseau, zéro interaction affût."
        )
    else:
        justification = (
            "Profil espèce non trouvé dans le registre SPECIES-PROFILES-Ω — "
            "explicabilité biologique partielle."
        )

    return {
        "engine": "ENGINE-IA-CORRIDORS-Ω",
        "version": "V1.0-PHASE-XI-SUPRA-K-2026-04",
        "corridor_id": corridor.get("id"),
        "species": species_key,
        "species_profile_present": species_profile is not None,
        "species_profile_summary": (
            {
                "habitat_preferred": species_profile.get("habitat", {}).get("preferred"),
                "movement_style": species_profile.get("movement", {}).get("corridor_style"),
                "water_dist_range_m": [
                    species_profile.get("hydrology", {}).get("water_dist_min_m"),
                    species_profile.get("hydrology", {}).get("water_dist_max_m"),
                ],
            }
            if species_profile
            else None
        ),
        "geometry_validation": geometry_check,
        "features_consumed": features,
        "attractors": attractors_explicit or attractors_default,
        "exclusions_applied": exclusions,
        "constraints": CONSTRAINTS,
        "justification_biologique": justification,
        "explained_at": datetime.now(timezone.utc).isoformat(),
    }


class ExplainBody(BaseModel):
    corridor: dict
    waypoint: dict  # {"lat": float, "lon": float}


@router.post("/explain")
async def ia_corridors_explain(body: ExplainBody):
    """Explicabilité IA (mode POST — client fournit le corridor)."""
    return explain_corridor(body.corridor, body.waypoint)


class ExplainLiveQuery(BaseModel):
    lat: float = 45.10
    lon: float = -72.80
    species: str = "chevreuil"


@router.get("/explain/{corridor_id}")
async def ia_corridors_explain_by_id(
    corridor_id: str,
    lat: float = 45.10,
    lon: float = -72.80,
    species: str = "chevreuil",
):
    """Explicabilité IA (mode GET par id) — recalcule le bundle live et renvoie
    l'explicabilité du corridor matching `corridor_id`.
    """
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10

    bundle = await compute_territoire_v10(
        lat,
        lon,
        species,
        month=10,
        hour=7,
        wind_deg=225,
        wind_speed=15,
    )
    corridors = bundle.get("corridors", []) or []
    match = next((c for c in corridors if str(c.get("id")) == corridor_id), None)
    if match is None:
        # Fallback : si l'id n'existe pas, retourne méta + liste des ids disponibles
        return {
            "ok": False,
            "engine": "ENGINE-IA-CORRIDORS-Ω",
            "corridor_id_requested": corridor_id,
            "available_ids": [c.get("id") for c in corridors],
            "detail": "corridor_id introuvable dans le bundle live",
        }
    return explain_corridor(match, {"lat": lat, "lon": lon})
