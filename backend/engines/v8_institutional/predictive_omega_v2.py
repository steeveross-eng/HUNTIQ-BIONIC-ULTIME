"""
predictive_omega_v2.py — PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω
================================================================================
Phase     : PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

ENGINE PREDICTIVE_OMEGA V2 — calibré sur trajectoires GPS USGS / Movebank.

REMPLACE le scoring synthétique uniforme de l'orchestrateur écologique par
un score comportemental issu de DONNÉES GPS RÉELLES :

  ▸ vecteurs directionnels       → bearings préférentiels par saison
  ▸ vitesses                     → mean_speed_kmh par saison
  ▸ amplitudes                   → home-range observé
  ▸ patterns saisonniers         → spring/summer/autumn/winter
  ▸ zones de transition          → clusters de fixes denses
  ▸ comportements jour/nuit      → diurnal_activity[24h]

Pipeline d'injection :
  V30 → species_modulator → predictive_omega_v2 (annotation)
   → INTERZONE → VEINEUX → ÉCOLOGIQUE → RENDUΩ → ANTI-RÉGRESSION

Aucun corridor ne reçoit de score synthétique : tous les scores predictive
proviennent désormais de l'analyse statistique des datasets GPS.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

GPS_TRACES_BASE = Path(os.environ.get("GPS_TRACES_BASE", "/app/registry/gps_traces"))

# Aliases de nomenclature → registre canonique GPS
SPECIES_ALIASES = {
    "cerf": "chevreuil", "chevreuil": "chevreuil",
    "orignal": "orignal",
    "wapiti": "wapiti",
    "ours": "ours_noir", "ours_noir": "ours_noir",
    "dindon": "dindon_sauvage", "dindon_sauvage": "dindon_sauvage",
}

# Cache lazy par espèce (datasets ~1 MB chacun, on cache sur 1ère lecture)
_DATASET_CACHE: Dict[str, Optional[Dict[str, Any]]] = {}


# ═══════════════════════════════════════════════════════════════════════
# 1. Chargement des datasets GPS
# ═══════════════════════════════════════════════════════════════════════
def _canonical_species(species: str) -> str:
    return SPECIES_ALIASES.get((species or "").lower().strip(), "chevreuil")


def _load_dataset(species: str) -> Optional[Dict[str, Any]]:
    canon = _canonical_species(species)
    if canon in _DATASET_CACHE:
        return _DATASET_CACHE[canon]
    p = GPS_TRACES_BASE / f"{canon}_movebank_v1.json"
    if not p.exists():
        _DATASET_CACHE[canon] = None
        return None
    try:
        _DATASET_CACHE[canon] = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        _DATASET_CACHE[canon] = None
    return _DATASET_CACHE[canon]


def reset_dataset_cache() -> None:
    _DATASET_CACHE.clear()


def get_gps_dataset_status() -> Dict[str, Any]:
    """Audit des datasets GPS disponibles."""
    out: Dict[str, Any] = {
        "phase": "PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω",
        "base_path": str(GPS_TRACES_BASE),
        "sources": {},
        "all_available": True,
    }
    for canon in ("orignal", "chevreuil", "wapiti", "ours_noir", "dindon_sauvage"):
        p = GPS_TRACES_BASE / f"{canon}_movebank_v1.json"
        present = p.exists()
        out["sources"][canon] = {
            "path": str(p),
            "present": present,
            "size_bytes": p.stat().st_size if present else 0,
        }
        if not present:
            out["all_available"] = False
    return out


# ═══════════════════════════════════════════════════════════════════════
# 2. Saisons / heures
# ═══════════════════════════════════════════════════════════════════════
def _season_from_month(month: int) -> str:
    if 3 <= month <= 5:
        return "spring"
    if 6 <= month <= 8:
        return "summer"
    if 9 <= month <= 11:
        return "autumn"
    return "winter"


# ═══════════════════════════════════════════════════════════════════════
# 3. Géométrie path → bearing
# ═══════════════════════════════════════════════════════════════════════
def _bearing_deg(p1: List[float], p2: List[float]) -> float:
    """Bearing initial entre 2 points lat/lng (0=N, 90=E)."""
    lat1 = math.radians(p1[0])
    lat2 = math.radians(p2[0])
    dlon = math.radians(p2[1] - p1[1])
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0


def _path_dominant_bearing(path: List[List[float]]) -> Optional[float]:
    if not path or len(path) < 2:
        return None
    return _bearing_deg(path[0], path[-1])


def _path_length_m(path: List[List[float]]) -> float:
    if not path or len(path) < 2:
        return 0.0
    R = 6371000.0
    total = 0.0
    for i in range(1, len(path)):
        la1, lo1 = math.radians(path[i - 1][0]), math.radians(path[i - 1][1])
        la2, lo2 = math.radians(path[i][0]), math.radians(path[i][1])
        h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
        total += 2 * R * math.asin(min(1.0, math.sqrt(h)))
    return total


def _circular_diff_deg(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


# ═══════════════════════════════════════════════════════════════════════
# 4. Densité GPS le long du path — PHASE XVIII-bis (fenêtre élargie + pondérée)
# ═══════════════════════════════════════════════════════════════════════
# Constantes institutionnelles (PHASE XVIII-bis — directive Commandant)
DENSITY_WINDOW_RADIUS_M = 150.0   # 80 → 150 m (×1.875)
DENSITY_WINDOW_DAYS = 28          # saison ±4 semaines
DENSITY_WINDOW_HOURS = 3          # heure locale ±3 h
DENSITY_TIME_SIGMA_DAYS = 14.0    # gaussienne décroissance temporelle


def _month_to_day_of_year(month: int) -> int:
    """Retourne le jour central du mois (15, 45, 75, 106, ...)."""
    centers = [15, 45, 75, 106, 136, 167, 197, 228, 259, 289, 320, 350]
    return centers[max(1, min(12, month)) - 1]


def _path_gps_density(dataset: Dict[str, Any], path: List[List[float]],
                       target_day: int, hour: int,
                       radius_m: float = DENSITY_WINDOW_RADIUS_M,
                       day_window: int = DENSITY_WINDOW_DAYS,
                       hour_window: int = DENSITY_WINDOW_HOURS) -> Dict[str, Any]:
    """Densité GPS PONDÉRÉE le long du path (PHASE XVIII-bis).

    Pondérations :
      - inverse-distance : w_dist = max(0, 1 − d / radius_m)  (linéaire 1→0)
      - décroissance temporelle : w_time = exp(−(Δday / 14)²) (gaussienne)
      - poids final = w_dist × w_time

    Le ratio retourné est la somme pondérée normalisée par le nombre de
    fixes dans la fenêtre temporelle (saison ±4 sem · heure ±3 h).
    """
    if not dataset or not path:
        return {"hits": 0, "weighted_hits": 0.0, "active_weighted_hits": 0.0,
                "ratio": 0.0, "fixes_in_window": 0}
    cos_anchor = math.cos(math.radians(path[0][0]))
    deg_per_m_lat = 1.0 / 111000.0
    deg_per_m_lng = 1.0 / (111000.0 * cos_anchor)
    margin_lat = radius_m * deg_per_m_lat * 1.2
    margin_lng = radius_m * deg_per_m_lng * 1.2

    lats = [p[0] for p in path]
    lngs = [p[1] for p in path]
    bb_lat_min, bb_lat_max = min(lats) - margin_lat, max(lats) + margin_lat
    bb_lng_min, bb_lng_max = min(lngs) - margin_lng, max(lngs) + margin_lng

    hours_window = {(hour + dh) % 24 for dh in range(-hour_window, hour_window + 1)}

    weighted_hits = 0.0
    raw_hits = 0
    active_weighted = 0.0
    total_in_window = 0
    for track in dataset.get("tracks", []):
        for fix in track.get("fixes", []):
            day = fix.get("day", 1)
            # Fenêtre jour cyclique (365 jours)
            delta_day = abs(day - target_day)
            delta_day = min(delta_day, 365 - delta_day)
            if delta_day > day_window:
                continue
            if fix.get("hour") not in hours_window:
                continue
            total_in_window += 1
            la, ln = fix["lat"], fix["lng"]
            if not (bb_lat_min <= la <= bb_lat_max and bb_lng_min <= ln <= bb_lng_max):
                continue
            n_samples = min(8, len(path))
            min_d = float("inf")
            for k in range(n_samples):
                idx = int(round(k * (len(path) - 1) / max(1, n_samples - 1)))
                pt = path[idx]
                dla = (la - pt[0]) * 111000.0
                dln = (ln - pt[1]) * 111000.0 * cos_anchor
                d = math.hypot(dla, dln)
                if d < min_d:
                    min_d = d
            if min_d > radius_m:
                continue
            w_dist = max(0.0, 1.0 - min_d / radius_m)
            w_time = math.exp(-(delta_day / DENSITY_TIME_SIGMA_DAYS) ** 2)
            w = w_dist * w_time
            weighted_hits += w
            raw_hits += 1
            if fix.get("active"):
                active_weighted += w

    ratio = weighted_hits / max(1, total_in_window)
    return {
        "hits": raw_hits,
        "weighted_hits": round(weighted_hits, 3),
        "active_weighted_hits": round(active_weighted, 3),
        "ratio": round(ratio, 4),
        "fixes_in_window": total_in_window,
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. Score predictive_omega V2 par corridor
# ═══════════════════════════════════════════════════════════════════════
def score_corridor_with_gps_real(
    corridor: Dict[str, Any],
    species: str,
    month: int = 10,
    hour: int = 14,
) -> Dict[str, Any]:
    """Calcule le score predictive_omega V2 (0..100) pour un corridor.

    Composants :
      - direction_score   (40 pts) : alignement avec bearings préférentiels saison
      - speed_score       (15 pts) : longueur du path cohérente avec amplitude saison
      - density_score     (35 pts) : densité GPS observée le long du path
      - diurnal_score     (10 pts) : compatibilité heure × diurnal_activity
    """
    path = corridor.get("path") or []
    if not path or len(path) < 2:
        return {"score": 0.0, "valid": False, "reason": "empty_path"}

    canon = _canonical_species(species)
    dataset = _load_dataset(canon)
    if dataset is None:
        return {"score": 0.0, "valid": False, "reason": "dataset_missing"}

    profile = dataset.get("biological_profile", {})
    season = _season_from_month(month)

    # ─── direction_score
    bearing = _path_dominant_bearing(path) or 0.0
    pref_bearings = (profile.get("primary_bearings_deg", {}) or {}).get(season, [0, 180])
    if pref_bearings == [0, 0]:  # hibernation totale ours hiver
        direction_score = 5.0
    else:
        diffs = [_circular_diff_deg(bearing, b) for b in pref_bearings]
        min_diff = min(diffs)
        # 0° → 40 pts, 90° → 0 pts (linéaire)
        direction_score = max(0.0, 40.0 * (1.0 - min_diff / 90.0))

    # ─── speed_score (longueur du path vs amplitude saison)
    L = _path_length_m(path)
    target_amp = (profile.get("amplitude_m", {}) or {}).get(season, 600.0)
    if target_amp == 0:
        speed_score = 5.0
    else:
        rel = L / target_amp
        # Score max si L ≈ amplitude (rel ≈ 1.0), pénalité si < 0.3 ou > 2.0
        if 0.5 <= rel <= 1.5:
            speed_score = 15.0
        elif 0.3 <= rel <= 2.0:
            speed_score = 10.0
        else:
            speed_score = 5.0

    # ─── density_score (PHASE XVIII-bis : fenêtre élargie + pondérée)
    target_day = _month_to_day_of_year(month)
    density = _path_gps_density(dataset, path, target_day=target_day, hour=hour)
    density_ratio = density["ratio"]
    # Score linéaire saturé à 35 pts. Le ratio est désormais une moyenne
    # pondérée (inverse-distance × décroissance temporelle) — il reflète
    # réellement la concentration GPS observée le long du path.
    density_score = min(35.0, density_ratio * 700.0)

    # ─── diurnal_score (cohérence heure)
    diurnal = profile.get("diurnal_activity", []) or [0.5] * 24
    activity_at_hour = diurnal[hour] if 0 <= hour < 24 else 0.5
    diurnal_score = activity_at_hour * 10.0

    score = direction_score + speed_score + density_score + diurnal_score
    score = max(0.0, min(100.0, score))
    return {
        "score": round(score, 2),
        "valid": True,
        "components": {
            "direction": round(direction_score, 2),
            "speed": round(speed_score, 2),
            "density": round(density_score, 2),
            "diurnal": round(diurnal_score, 2),
        },
        "metrics": {
            "season": season,
            "hour": hour,
            "path_bearing_deg": round(bearing, 1),
            "preferred_bearings_deg": pref_bearings,
            "path_length_m": round(L, 1),
            "target_amplitude_m": target_amp,
            "gps_hits": density["hits"],
            "gps_weighted_hits": density["weighted_hits"],
            "gps_active_weighted_hits": density["active_weighted_hits"],
            "gps_density_ratio": density["ratio"],
            "gps_fixes_in_window": density["fixes_in_window"],
            "gps_window_radius_m": DENSITY_WINDOW_RADIUS_M,
            "gps_window_days": DENSITY_WINDOW_DAYS,
            "gps_window_hours": DENSITY_WINDOW_HOURS,
            "diurnal_activity": round(activity_at_hour, 3),
        },
        "phase": "PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω",
        "subphase": "PHASE_XVIII_BIS_DENSITY_WINDOW_OPTIMIZATION_Ω",
    }


# ═══════════════════════════════════════════════════════════════════════
# 6. Annotation pipeline (étape XVIII du bundle)
# ═══════════════════════════════════════════════════════════════════════
def apply_predictive_omega_v2_to_bundle(bundle: Dict[str, Any], species: str,
                                         month: int = 10, hour: int = 14) -> Dict[str, Any]:
    """Annote chaque corridor avec son score predictive_omega V2.

    Le score est lu en aval par l'orchestrateur écologique (XVII) qui s'en
    sert au lieu du score synthétique uniforme.
    """
    if not isinstance(bundle, dict):
        return bundle
    corridors = bundle.get("corridors") or []
    scored = 0
    sum_score = 0.0
    for c in corridors:
        result = score_corridor_with_gps_real(c, species=species, month=month, hour=hour)
        c["predictive_omega_v2"] = result
        if result.get("valid"):
            scored += 1
            sum_score += result["score"]
    bundle["predictive_omega_v2_applied"] = True
    bundle["predictive_omega_v2_stats"] = {
        "phase": "PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω",
        "species_canonical": _canonical_species(species),
        "month": month,
        "hour": hour,
        "season": _season_from_month(month),
        "corridors_total": len(corridors),
        "corridors_scored": scored,
        "mean_score": round(sum_score / max(1, scored), 2) if scored else 0.0,
        "gps_dataset_status": get_gps_dataset_status(),
    }
    return bundle
