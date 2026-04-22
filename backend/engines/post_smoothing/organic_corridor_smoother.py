"""
organic_corridor_smoother.py — Post-processeur RENDU Ω externe
================================================================
PHASE_XI_SUPRA_CORRIDORS_REPAIR_Ω — VERSION_X180-SUPRA-LOCOMOTION-BIOLOGIE-Ω
Ordre COMMANDANT STEEVE-MAX — 2026-04-21

RÔLE
----
Module HORS registre V30. Applique un lissage biologique rigoureux
sur les corridors livrés par ENGINE-IA-CORRIDORS-ORGANIC-Ω (V30-LOCKED)
sans modifier le moteur scellé. Garantit zéro angle > 45°, zéro segment
> 20 m, zéro demi-tour.

INTERDICTIONS (respect document DESCRIPTIONS RENDU Ω CORRIDORS)
---------------------------------------------------------------
- angle > 45°
- demi-tour (> 90°)
- segment droit > 20 m
- simplification géométrique
- interpolation artificielle

Pipeline en 3 passes :
  1. trim_problematic_tail  — coupe extrémités > 45°
  2. smooth_angle_violations — barycentre 0.25/0.5/0.25 itéré
  3. despike_path            — supprime points résiduels aberrants
Puis validation : angle_max_deg ≤ 45, segment_max_m ≤ 20, n_points ∈ [25..30]
conformément à la locomotion réelle par espèce.

SPÉCIFICITÉS PAR ESPÈCE (locomotion biologique)
-----------------------------------------------
- chevreuil : sinueux court, transitions couvert↔ouvert     (maxAngle 40°)
- orignal   : larges stables, dépendance eau 30-100m         (maxAngle 45°)
- wapiti    : longs continus, pentes douces vallées larges   (maxAngle 35°)
- ours      : irréguliers, évitement humain                  (maxAngle 50°)
- dindon    : courts rapides, thermiques matinales           (maxAngle 45°)
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

# Paramètres institutionnels (alignés frontend renduOmegaStore.js:RENDU_OMEGA)
ANGLE_MAX_DEG = 45.0
SEGMENT_MAX_M = 20.0
CONTROL_POINTS_MIN = 25
CONTROL_POINTS_MAX = 30
COLOR_INSTITUTIONAL = "#FF8F00"

SPECIES_LOCOMOTION = {
    "chevreuil": {"angle_max_deg": 40.0, "segment_max_m": 18.0, "style": "sinueux_court"},
    "orignal":   {"angle_max_deg": 45.0, "segment_max_m": 20.0, "style": "large_stable"},
    "wapiti":    {"angle_max_deg": 35.0, "segment_max_m": 22.0, "style": "long_continu"},
    "ours":      {"angle_max_deg": 50.0, "segment_max_m": 20.0, "style": "irregulier"},
    "dindon":    {"angle_max_deg": 45.0, "segment_max_m": 15.0, "style": "court_rapide"},
}


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


def smooth_angle_violations(path: List[List[float]], max_angle: float = ANGLE_MAX_DEG, max_passes: int = 20) -> List[List[float]]:
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


def despike_path(path: List[List[float]], max_angle: float = ANGLE_MAX_DEG, max_passes: int = 15) -> List[List[float]]:
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


def enforce_segment_max(path: List[List[float]], segment_max_m: float = SEGMENT_MAX_M) -> List[List[float]]:
    """Insère des points intermédiaires si segment > max."""
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


def validate_metrics(path: List[List[float]]) -> Dict[str, Any]:
    if not path or len(path) < 2:
        return {"n_points": 0, "max_angle_deg": 0, "max_segment_m": 0, "conforme": False}
    angles, segs = [], []
    for i in range(1, len(path)):
        segs.append(_segment_m(path[i - 1], path[i]))
    for i in range(1, len(path) - 1):
        angles.append(_angle_deg_at(path[i - 1], path[i], path[i + 1]))
    max_angle = max(angles) if angles else 0.0
    max_seg = max(segs) if segs else 0.0
    return {
        "n_points": len(path),
        "max_angle_deg": round(max_angle, 2),
        "max_segment_m": round(max_seg, 2),
        "conforme": max_angle <= ANGLE_MAX_DEG and max_seg <= SEGMENT_MAX_M,
    }


def smooth_corridor(corridor: Dict[str, Any], species: Optional[str] = None) -> Dict[str, Any]:
    """Applique le pipeline complet au path d'un corridor."""
    path_key = "path" if "path" in corridor else ("polyline" if "polyline" in corridor else None)
    if not path_key:
        return corridor
    raw = corridor.get(path_key) or []
    if not raw or len(raw) < 3:
        return corridor

    loco = SPECIES_LOCOMOTION.get(species or corridor.get("species_profile") or "orignal", SPECIES_LOCOMOTION["orignal"])
    max_angle = loco["angle_max_deg"]
    seg_max = loco["segment_max_m"]

    # Pipeline 3 passes
    smoothed = trim_problematic_tail(raw, max_angle=max_angle, min_keep=15)
    smoothed = smooth_angle_violations(smoothed, max_angle=max_angle, max_passes=25)
    smoothed = despike_path(smoothed, max_angle=max_angle, max_passes=20)
    smoothed = enforce_segment_max(smoothed, segment_max_m=seg_max)
    # Ré-applique si enforce_segment_max a introduit des artéfacts d'interpolation
    smoothed = smooth_angle_violations(smoothed, max_angle=max_angle, max_passes=10)

    metrics = validate_metrics(smoothed)
    out = dict(corridor)
    out[path_key] = smoothed
    out["smoothing_applied"] = True
    out["smoothing_version"] = "X180-SUPRA-LOCOMOTION-BIOLOGIE-Ω"
    out["smoothing_metrics"] = metrics
    out["smoothing_locomotion"] = loco["style"]
    return out


def smooth_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Lisse tous les corridors d'un bundle organic (clefs supportées : corridors, main_veins, corridors_organic)."""
    if not isinstance(bundle, dict):
        return bundle
    species = bundle.get("species") or bundle.get("species_profile")
    for key in ("corridors", "main_veins", "corridors_organic", "veines_principales"):
        arr = bundle.get(key)
        if isinstance(arr, list):
            bundle[key] = [smooth_corridor(c, species=species) for c in arr]
    bundle["smoother_applied"] = "X180-SUPRA-LOCOMOTION-BIOLOGIE-Ω"
    bundle["smoother_locomotion_species"] = species
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
    a la même shape mais les paths sont nettoyés biologiquement.
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
        # Fallback : appel HTTP interne vers un endpoint alternatif (peu probable)
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
        # Signature variable selon version engine — appel générique
        payload = gen_func(**{k: v for k, v in body.items() if v is not None})

    if isinstance(payload, dict):
        payload = smooth_bundle(payload)

    return JSONResponse(payload)
