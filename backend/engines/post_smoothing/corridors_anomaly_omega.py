"""
CORRIDORS_ANOMALY_OMEGA · P22G_CORRIDORS_REFINEMENT_X100_Ω
═══════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Module de détection d'anomalies dans les corridors organic post-RENDU-Ω.

DOCTRINE :
  - detect_rectilinear_corridors : path trop droit (signature radiale interdite)
  - detect_fractal_corridors : variations brusques d'angle (artefact algorithmique)
  - detect_obstacle_proximity : passage trop près d'obstacles terrain

MÉTRIQUES INSTITUTIONNELLES :
  - density : nombre de corridors / km²
  - continuity : ratio de corridors connectés à au moins 2 nœuds vitaux
  - connectivity : nombre de paires uniques (saline-feeding, etc.)
  - acceptance_rate : ratio acceptés/total post-RENDU-Ω
  - rendu_omega_conformity : conformité doctrinale stricte

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · FICHIER NEUF
═══════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import math
from typing import Any
from datetime import datetime, timezone


# ═══ SEUILS DE DÉTECTION ANOMALIES ═══
RECTILINEAR_RATIO_THRESHOLD = 1.02   # path_length / direct_distance < 1.02 → suspect
RECTILINEAR_ANGLE_MAX_DEG = 1.5       # courbure quasi-nulle
FRACTAL_ANGLE_THRESHOLD_DEG = 90.0    # angle abrupt > 90° = fractal
FRACTAL_MIN_OCCURRENCES = 3           # ≥ 3 angles abrupts = fractal
OBSTACLE_PROXIMITY_MIN_M = 10.0       # < 10m d'un obstacle = anomalie


def _haversine_m(p1: list, p2: list) -> float:
    """Distance Haversine en mètres entre 2 points [lat, lon]."""
    if not p1 or not p2:
        return 0.0
    lat1, lon1 = float(p1[0]), float(p1[1])
    lat2, lon2 = float(p2[0]), float(p2[1])
    R = 6371000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def _path_length_m(path: list) -> float:
    return sum(_haversine_m(path[i], path[i + 1])
               for i in range(len(path) - 1)) if len(path) > 1 else 0.0


def _bearing_deg(p1: list, p2: list) -> float:
    """Cap géographique entre 2 points en degrés."""
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2)
         - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0


def _angle_change_deg(p1: list, p2: list, p3: list) -> float:
    """Changement d'angle absolu en chaque vertex (0-180°)."""
    b1 = _bearing_deg(p1, p2)
    b2 = _bearing_deg(p2, p3)
    diff = abs(b2 - b1) % 360.0
    return min(diff, 360.0 - diff)


# ═══ DÉTECTEURS D'ANOMALIES ═══

def detect_rectilinear(path: list) -> dict:
    """Détecte un corridor quasi-rectiligne (signature artefact radial)."""
    if not path or len(path) < 4:
        return {"is_rectilinear": False, "reason": "insufficient_points"}
    plen = _path_length_m(path)
    direct = _haversine_m(path[0], path[-1])
    if direct == 0:
        return {"is_rectilinear": True, "reason": "degenerate_path", "ratio": 0.0}
    ratio = plen / direct
    max_angle = max(
        (_angle_change_deg(path[i], path[i + 1], path[i + 2])
         for i in range(len(path) - 2)),
        default=0.0,
    )
    is_rect = (ratio < RECTILINEAR_RATIO_THRESHOLD
               and max_angle < RECTILINEAR_ANGLE_MAX_DEG)
    return {
        "is_rectilinear": is_rect,
        "ratio": round(ratio, 4),
        "max_angle_deg": round(max_angle, 2),
        "threshold_ratio": RECTILINEAR_RATIO_THRESHOLD,
        "threshold_angle_deg": RECTILINEAR_ANGLE_MAX_DEG,
    }


def detect_fractal(path: list) -> dict:
    """Détecte un corridor avec variations brusques d'angle (≥ 3 angles > 90°)."""
    if not path or len(path) < 3:
        return {"is_fractal": False, "n_abrupt_angles": 0}
    abrupt_indices: list[int] = []
    abrupt_angles: list[float] = []
    for i in range(len(path) - 2):
        ang = _angle_change_deg(path[i], path[i + 1], path[i + 2])
        if ang > FRACTAL_ANGLE_THRESHOLD_DEG:
            abrupt_indices.append(i + 1)
            abrupt_angles.append(round(ang, 1))
    n_abrupt = len(abrupt_indices)
    return {
        "is_fractal": n_abrupt >= FRACTAL_MIN_OCCURRENCES,
        "n_abrupt_angles": n_abrupt,
        "abrupt_angles_sample": abrupt_angles[:5],
        "threshold_min_occurrences": FRACTAL_MIN_OCCURRENCES,
        "threshold_angle_deg": FRACTAL_ANGLE_THRESHOLD_DEG,
    }


def detect_obstacle_proximity(path: list, obstacles: list) -> dict:
    """Détecte un corridor passant à moins de 10m d'un obstacle.

    obstacles : liste de dicts {lat, lon, type, name?}
    """
    if not path or not obstacles:
        return {"is_too_close": False, "n_violations": 0}
    violations = []
    for ob in obstacles:
        ob_lat = ob.get("lat")
        ob_lon = ob.get("lon", ob.get("lng"))
        if ob_lat is None or ob_lon is None:
            continue
        for i, p in enumerate(path):
            d = _haversine_m([p[0], p[1]], [ob_lat, ob_lon])
            if d < OBSTACLE_PROXIMITY_MIN_M:
                violations.append({
                    "obstacle_type": ob.get("type", "unknown"),
                    "obstacle_name": ob.get("name", "?"),
                    "vertex_index": i,
                    "distance_m": round(d, 2),
                })
                break  # un seul vertex suffit pour signaler
    return {
        "is_too_close": len(violations) > 0,
        "n_violations": len(violations),
        "violations_sample": violations[:5],
        "threshold_min_m": OBSTACLE_PROXIMITY_MIN_M,
    }


# ═══ MÉTRIQUES INSTITUTIONNELLES ═══

def compute_density(corridors: list, lat_center: float, lon_center: float,
                    radius_m: float = 780.0) -> dict:
    """Densité de corridors par km² dans le rayon fonctionnel."""
    n = len(corridors)
    area_km2 = math.pi * (radius_m / 1000.0) ** 2
    density = n / area_km2 if area_km2 > 0 else 0.0
    return {
        "n_corridors": n,
        "radius_m": radius_m,
        "area_km2": round(area_km2, 4),
        "density_per_km2": round(density, 2),
    }


def compute_continuity(corridors: list) -> dict:
    """Ratio de corridors connectés à AU MOINS 2 nœuds vitaux distincts."""
    if not corridors:
        return {"continuity_ratio": 0.0, "n_connected": 0, "n_total": 0}
    n_connected = 0
    for c in corridors:
        nf = c.get("node_from") or {}
        nt = c.get("node_to") or {}
        if (nf.get("source_id") and nt.get("source_id")
                and nf["source_id"] != nt["source_id"]):
            n_connected += 1
    return {
        "continuity_ratio": round(n_connected / len(corridors), 3),
        "n_connected": n_connected,
        "n_total": len(corridors),
    }


def compute_connectivity(corridors: list) -> dict:
    """Nombre de paires uniques de types reliés (saline↔feeding, etc.)."""
    if not corridors:
        return {"connectivity_pairs": 0, "pairs_unique": []}
    pairs: set[tuple[str, str]] = set()
    for c in corridors:
        nf_t = (c.get("node_from") or {}).get("type")
        nt_t = (c.get("node_to") or {}).get("type")
        if nf_t and nt_t:
            pair = tuple(sorted([nf_t, nt_t]))
            pairs.add(pair)
    return {
        "connectivity_pairs": len(pairs),
        "pairs_unique": [list(p) for p in sorted(pairs)],
    }


def compute_acceptance_rate(payload: dict) -> dict:
    """Taux d'acceptation post-RENDU-Ω."""
    accepted = len(payload.get("corridors") or [])
    rejected = len(payload.get("corridors_rejected_by_renduomega") or [])
    total = accepted + rejected
    rate = accepted / total if total > 0 else 1.0
    return {
        "accepted": accepted,
        "rejected_by_renduomega": rejected,
        "total_candidates": total,
        "acceptance_rate": round(rate, 4),
    }


def compute_rendu_omega_conformity(corridors: list) -> dict:
    """Score de conformité RENDU-Ω : 100% si tous les corridors ont
    `renduomega.accepted: true` ET aucune anomalie détectée.
    """
    if not corridors:
        return {"conformity_pct": 0.0, "n_conform": 0, "n_total": 0}
    n_conform = sum(1 for c in corridors
                    if (c.get("renduomega") or {}).get("accepted") is True)
    return {
        "conformity_pct": round(100.0 * n_conform / len(corridors), 2),
        "n_conform": n_conform,
        "n_total": len(corridors),
        "doctrine": "P22G_SEMI_STRICT",
    }


# ═══ ANOMALY MAP COMPLÈTE ═══

def build_anomaly_map(payload: dict, obstacles: list | None = None) -> dict:
    """Génère la carte d'anomalies complète pour un bundle organic.

    Retourne :
      {
        anomalies_per_corridor: [...],
        summary: {n_rectilinear, n_fractal, n_obstacle_close, n_total},
        metrics: {density, continuity, connectivity, acceptance, conformity},
      }
    """
    corridors = payload.get("corridors") or []
    waypoint = payload.get("waypoint") or {}
    lat = float(waypoint.get("lat") or 0.0)
    lon = float(waypoint.get("lon") or waypoint.get("lng") or 0.0)
    obs = obstacles or []

    anomalies_list: list[dict[str, Any]] = []
    n_rect = 0
    n_fract = 0
    n_obst = 0
    for c in corridors:
        path = c.get("path") or []
        if not isinstance(path, list) or len(path) < 3:
            continue
        rect = detect_rectilinear(path)
        fract = detect_fractal(path)
        obst = detect_obstacle_proximity(path, obs)
        if rect["is_rectilinear"]:
            n_rect += 1
        if fract["is_fractal"]:
            n_fract += 1
        if obst["is_too_close"]:
            n_obst += 1
        anomalies_list.append({
            "id": c.get("id"),
            "hierarchy": c.get("hierarchy"),
            "rectilinear": rect,
            "fractal": fract,
            "obstacle_proximity": obst,
            "any_anomaly": (rect["is_rectilinear"]
                            or fract["is_fractal"]
                            or obst["is_too_close"]),
        })

    summary = {
        "n_corridors_analyzed": len(anomalies_list),
        "n_rectilinear": n_rect,
        "n_fractal": n_fract,
        "n_obstacle_close": n_obst,
        "n_clean": sum(1 for a in anomalies_list if not a["any_anomaly"]),
    }

    metrics = {
        "density": compute_density(corridors, lat, lon),
        "continuity": compute_continuity(corridors),
        "connectivity": compute_connectivity(corridors),
        "acceptance_rate": compute_acceptance_rate(payload),
        "rendu_omega_conformity": compute_rendu_omega_conformity(corridors),
    }

    return {
        "engine": "CORRIDORS_ANOMALY_OMEGA_X100",
        "doctrine": "P22G_REFINEMENT_X100_Ω",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "waypoint": {"lat": lat, "lon": lon, "species": waypoint.get("species")},
        "anomalies_per_corridor": anomalies_list,
        "summary": summary,
        "metrics": metrics,
    }


# ═══ ENDPOINT FASTAPI ═══
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v20/territoire/corridors-organic",
    tags=["CORRIDORS_ANOMALY_X100"],
)


class AnomalyMapBody(BaseModel):
    lat: float = 48.206657
    lon: float = -68.382422
    species: str = "orignal"
    month: int = 10
    hour: int = 7
    wind_deg: int = 225
    wind_speed: int = 15
    anchor_mode: str = "SALINE_CENTERED"
    obstacles: list[dict] | None = None


@router.post("/anomaly-map")
async def anomaly_map_endpoint(body: AnomalyMapBody):
    """P22G_REFINEMENT_X100_Ω — Génère la carte d'anomalies + métriques pour
    un bundle de corridors organic au point (lat, lon) pour une espèce donnée.

    Pipeline :
      1. Génère le bundle organic via l'engine V30 (avec anchor_mode appliqué)
      2. Détecte les 3 types d'anomalies (rectilinear, fractal, obstacle_close)
      3. Calcule les 5 métriques institutionnelles
      4. Retourne la carte complète
    """
    from engines.v8_institutional import (
        engine_ia_corridors_organic_omega as organic_mod,
    )
    payload = await organic_mod.generate_organic_corridors(
        body.lat, body.lon, body.species, body.month, body.hour,
        body.wind_deg, body.wind_speed,
        anchor_mode=body.anchor_mode,
    )
    return build_anomaly_map(payload, obstacles=body.obstacles or [])
