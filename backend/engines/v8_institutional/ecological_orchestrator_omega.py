"""
ecological_orchestrator_omega.py — PHASE_XVII_SUPRA_ENGINE_CORRIDORS_ECOLOGIQUE_Ω
================================================================================
Phase     : PHASE_XVII_SUPRA_ENGINE_CORRIDORS_ECOLOGIQUE_Ω — ACTIVATED
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

ORCHESTRATEUR UNIFIÉ DES 5 ENGINES ÉCOLOGIQUES + IA PREDICTIVE_OMEGA.

Garantit que CHAQUE corridor est le résultat d'un consensus écologique entre :
  1. engine_eco_zones_omega       — habitat / vital zones hierarchy
  2. engine_bio_scoring_omega     — attractivité biologique 8-factors
  3. engine_hydro_topo_omega      — topographie + hydrologie
  4. engine_reseau_veineux_omega  — réseau veineux naturel + external_inflow
  5. engine_predictive_omega      — IA-CORRIDORS predictive comportementale

Heatmaps réelles (couches d'enrichissement, V1 déterministe) :
  - MFFP    zones_humides       → modulation eco_zones + hydro_topo
  - MFFP    ravages_orignal     → modulation predictive (espèce orignal)
  - SEPAQ   pression_humaine    → pénalité bio_scoring + predictive
  - USGS    gps_traces          → bonus predictive (spécifique espèce)
  - NOAA    snow_depth          → modulation hydro_topo (mobilité hivernale)
  - NASA    ndvi                → bonus bio_scoring (productivité végétale)

Règles d'enforcement institutionnelles :
  §3 Origine du corridor DOIT être dans la couronne externe 30 % (≥ 70 % R_max).
  §4 Le corridor DOIT relier ≥ 2 zones vitales (ou 1 zone + 1 saline).

Application :
  - mode "annotate"  : pose les metadata (par défaut)
  - mode "enforce"   : filtre les corridors non conformes (active via env)
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# P22ΩΩ_IA_CORRIDORS_P0_Ω (2026-05-23) — Registry IA P0 (additif read-only).
try:
    from engines.v8_institutional import ia_corridors_registry_omega as IA_CORRIDORS_P0  # noqa: F401
except ImportError:
    IA_CORRIDORS_P0 = None  # type: ignore

# ═══════════════════════════════════════════════════════════════════════
# 1. Heatmaps registry — chemins canoniques
# ═══════════════════════════════════════════════════════════════════════
HEATMAPS_BASE = Path(os.environ.get("HEATMAPS_BASE", "/app/registry/heatmaps"))
HEATMAP_SOURCES: Dict[str, str] = {
    "mffp_zones_humides":     "mffp/zones_humides_v1.json",
    "mffp_ravages_orignal":   "mffp/ravages_orignal_v1.json",
    "sepaq_pression_humaine": "sepaq/pression_humaine_v1.json",
    "usgs_gps_traces":        "usgs/gps_traces_v1.json",
    "noaa_neige":             "noaa/snow_depth_v1.json",
    "nasa_ndvi":              "nasa/ndvi_v1.json",
}

# Pondérations institutionnelles du consensus écologique
ECOLOGICAL_CONSENSUS_WEIGHTS: Dict[str, float] = {
    "eco_zones":      0.22,
    "bio_scoring":    0.22,
    "hydro_topo":     0.18,
    "reseau_veineux": 0.18,
    "predictive":     0.20,
}

# Règle institutionnelle §3 — origine externe 30 % de la couronne 600 m
EXTERNAL_RING_FRACTION = 0.30

# Mode d'enforcement — par défaut "enforce" (activation P0 PHASE XVII)
ENFORCE_MODE = os.environ.get("PHASE_XVII_ENFORCE", "1") == "1"

# Cache lazy des heatmaps
_HEATMAP_CACHE: Dict[str, Optional[Dict[str, Any]]] = {}


def _load_heatmap(key: str) -> Optional[Dict[str, Any]]:
    """Charge une heatmap (lazy-cache)."""
    if key in _HEATMAP_CACHE:
        return _HEATMAP_CACHE[key]
    rel = HEATMAP_SOURCES.get(key)
    if not rel:
        _HEATMAP_CACHE[key] = None
        return None
    full = HEATMAPS_BASE / rel
    if not full.exists():
        _HEATMAP_CACHE[key] = None
        return None
    try:
        _HEATMAP_CACHE[key] = json.loads(full.read_text(encoding="utf-8"))
    except Exception:
        _HEATMAP_CACHE[key] = None
    return _HEATMAP_CACHE[key]


def reset_heatmap_cache() -> None:
    """Vide le cache (tests, hot-reload)."""
    _HEATMAP_CACHE.clear()


def get_heatmaps_status() -> Dict[str, Any]:
    """Audit des heatmaps disponibles."""
    status: Dict[str, Any] = {
        "phase": "PHASE_XVII_SUPRA_ENGINE_CORRIDORS_ECOLOGIQUE_Ω",
        "base_path": str(HEATMAPS_BASE),
        "sources": {},
        "all_available": True,
        "fallback_mode": False,
        "enforce_mode": ENFORCE_MODE,
    }
    for key, rel in HEATMAP_SOURCES.items():
        full = HEATMAPS_BASE / rel
        present = full.exists()
        status["sources"][key] = {
            "path": str(full),
            "present": present,
            "size_bytes": full.stat().st_size if present else 0,
        }
        if not present:
            status["all_available"] = False
            status["fallback_mode"] = True
    return status


def compute_external_ring_radius(r_max_m: float) -> Tuple[float, float]:
    """Retourne (r_inner, r_outer) de la couronne externe 30 %."""
    r_inner = r_max_m * (1.0 - EXTERNAL_RING_FRACTION)
    r_outer = r_max_m
    return r_inner, r_outer


# ═══════════════════════════════════════════════════════════════════════
# 2. Sampling des heatmaps grilles (lat/lng → valeur)
# ═══════════════════════════════════════════════════════════════════════
def _sample_heatmap_at(hm: Dict[str, Any], lat: float, lng: float) -> Optional[float]:
    """Échantillonne une heatmap au point (lat, lng) avec nearest-neighbor."""
    if not hm:
        return None
    grid = hm.get("grid") or {}
    rows = grid.get("rows", 0)
    cols = grid.get("cols", 0)
    cell = grid.get("cell_size_m", 50.0)
    anchor = hm.get("anchor") or {}
    a_lat = anchor.get("lat")
    a_lng = anchor.get("lng")
    values = hm.get("values") or []
    if not values or rows <= 0 or cols <= 0 or a_lat is None or a_lng is None:
        return None
    # Distance en mètres locaux (small-angle approx)
    dy_m = (lat - a_lat) * 111000.0
    dx_m = (lng - a_lng) * 111000.0 * math.cos(math.radians(a_lat))
    half_rows = rows / 2
    half_cols = cols / 2
    i = int(round(half_rows - 0.5 + dy_m / cell))
    j = int(round(half_cols - 0.5 + dx_m / cell))
    if i < 0 or i >= rows or j < 0 or j >= cols:
        return None
    try:
        return float(values[i][j])
    except (IndexError, TypeError, ValueError):
        return None


def _sample_along_path(hm: Dict[str, Any], path: List[List[float]]) -> Optional[float]:
    """Moyenne échantillonnée le long d'un path (max 10 échantillons)."""
    if not hm or not path:
        return None
    n = min(10, max(2, len(path)))
    samples: List[float] = []
    for k in range(n):
        idx = int(round(k * (len(path) - 1) / max(1, n - 1)))
        pt = path[idx]
        v = _sample_heatmap_at(hm, pt[0], pt[1])
        if v is not None:
            samples.append(v)
    if not samples:
        return None
    return sum(samples) / len(samples)


# ═══════════════════════════════════════════════════════════════════════
# 3. Score de consensus écologique
# ═══════════════════════════════════════════════════════════════════════
def compute_consensus_score(
    eco_score: float, bio_score: float, hydro_score: float,
    veineux_score: float, predictive_score: float,
) -> Dict[str, Any]:
    """Calcule le score de consensus écologique pondéré [0..100]."""
    w = ECOLOGICAL_CONSENSUS_WEIGHTS
    consensus = (
        eco_score * w["eco_zones"] + bio_score * w["bio_scoring"]
        + hydro_score * w["hydro_topo"] + veineux_score * w["reseau_veineux"]
        + predictive_score * w["predictive"]
    )
    consensus = max(0.0, min(100.0, consensus))
    label = ("EXCELLENT" if consensus >= 80 else
             "BON" if consensus >= 60 else
             "PARTIEL" if consensus >= 40 else "FAIBLE")
    return {
        "consensus_score": round(consensus, 2),
        "label": label,
        "components": {
            "eco_zones": round(eco_score, 2),
            "bio_scoring": round(bio_score, 2),
            "hydro_topo": round(hydro_score, 2),
            "reseau_veineux": round(veineux_score, 2),
            "predictive": round(predictive_score, 2),
        },
        "weights": dict(w),
    }


# ═══════════════════════════════════════════════════════════════════════
# 4. Synthèse écologique POUR UN CORRIDOR (heatmaps appliquées)
# ═══════════════════════════════════════════════════════════════════════
def synthesize_ecological_layers_for_corridor(
    corridor: Dict[str, Any],
    species: str,
    waypoint: Dict[str, float],
    bundle_zones: Optional[List[Dict[str, Any]]] = None,
    bundle_salines: Optional[List[Dict[str, Any]]] = None,
    r_max_m: float = 780.0,
) -> Dict[str, Any]:
    """Synthèse biologique pour un corridor — lecture effective des heatmaps."""
    path = corridor.get("path") or []
    if not path:
        return {"valid": False, "reason": "empty_path"}

    bundle_zones = bundle_zones or []
    bundle_salines = bundle_salines or []
    species_canon = (species or "").lower().strip()

    # Seuil de proximité d'inclusion zone vitale (centroid → tout point du path)
    ZONE_PROXIMITY_M = 120.0

    # ─── Comptage zones vitales touchées (eco_zones)
    zones_touched_count, zones_touched_names = 0, []
    for z in bundle_zones:
        poly = z.get("polygon") or []
        if not poly:
            continue
        cz_lat = sum(p[0] for p in poly) / len(poly)
        cz_lon = sum(p[1] for p in poly) / len(poly)
        for pt in path:
            if _dist_m([pt[0], pt[1]], [cz_lat, cz_lon]) < ZONE_PROXIMITY_M:
                zones_touched_count += 1
                zones_touched_names.append(z.get("type") or z.get("nom") or "zone")
                break
    salines_touched = sum(
        1 for s in bundle_salines
        if any(_dist_m([pt[0], pt[1]],
                       [s.get("lat", 0), s.get("lng") or s.get("lon") or 0]) < ZONE_PROXIMITY_M
               for pt in path)
    )

    # ─── eco_zones score (bonus heatmap MFFP zones humides si orignal)
    eco_base = min(100.0, 25.0 * zones_touched_count + 12.0 * salines_touched)
    hm_humides = _load_heatmap("mffp_zones_humides")
    avg_humid = _sample_along_path(hm_humides, path) or 0.5
    if species_canon == "orignal":
        eco_score = min(100.0, eco_base + 20.0 * avg_humid)
    else:
        eco_score = min(100.0, eco_base + 5.0 * avg_humid)

    # ─── bio_scoring — longueur idéale + bonus NDVI – pénalité pression humaine
    L = sum(_dist_m(path[i - 1], path[i]) for i in range(1, len(path))) if len(path) >= 2 else 0
    bio_base = 100.0 if 420 <= L <= 780 else (60.0 if 350 <= L < 1100 else 30.0)
    hm_ndvi = _load_heatmap("nasa_ndvi")
    avg_ndvi = _sample_along_path(hm_ndvi, path) or 0.55
    hm_pression = _load_heatmap("sepaq_pression_humaine")
    avg_press = _sample_along_path(hm_pression, path) or 0.0
    bio_score = max(0.0, min(100.0, bio_base + 15.0 * (avg_ndvi - 0.4) - 25.0 * avg_press))

    # ─── hydro_topo — pénalité neige hivernale, bonus humidité ravages
    hm_snow = _load_heatmap("noaa_neige")
    avg_snow = _sample_along_path(hm_snow, path) or 18.0
    snow_penalty = max(0.0, (avg_snow - 30.0) * 0.6)  # pénalité au-delà 30 cm
    hydro_score = max(0.0, min(100.0, 75.0 - snow_penalty + 10.0 * avg_humid))

    # ─── reseau_veineux — bonus si interzone/entrant
    veineux_score = (
        90.0 if (corridor.get("interzone_generated") or corridor.get("entering_corridor"))
        else 65.0
    )

    # ─── predictive — UTILISE predictive_omega_v2 (Phase XVIII) si présent
    pv2 = corridor.get("predictive_omega_v2") or {}
    if pv2.get("valid"):
        # Le score V2 (0..100) issu des trajectoires GPS USGS RÉELLES
        # remplace intégralement le score synthétique uniforme.
        predictive_score = float(pv2.get("score") or 0.0)
        predictive_source = "PHASE_XVIII_GPS_USGS"
        avg_gps = (pv2.get("metrics") or {}).get("gps_density_ratio") or 0.0
        avg_ravages = avg_ravages = _sample_along_path(_load_heatmap("mffp_ravages_orignal"), path) or 0.0
    else:
        # Fallback : score synthétique d'origine si dataset GPS absent
        hm_gps = _load_heatmap("usgs_gps_traces")
        avg_gps = _sample_along_path(hm_gps, path) or 0.1
        hm_ravages = _load_heatmap("mffp_ravages_orignal")
        avg_ravages = _sample_along_path(hm_ravages, path) or 0.0
        pred_base = 70.0 + min(20.0, 5.0 * zones_touched_count)
        pred_bonus = 25.0 * avg_gps
        if species_canon == "orignal":
            pred_bonus += min(15.0, 0.25 * avg_ravages)
        pred_bonus -= 15.0 * avg_press
        predictive_score = max(0.0, min(100.0, pred_base + pred_bonus))
        predictive_source = "PHASE_XVII_FALLBACK_SYNTHETIC"

    consensus = compute_consensus_score(
        eco_score, bio_score, hydro_score, veineux_score, predictive_score,
    )

    # ─── Règle §4 : ≥ 2 zones vitales (compte les salines)
    relies_2_vital = (zones_touched_count + salines_touched) >= 2

    # ─── Règle §3 : AU MOINS UNE EXTRÉMITÉ du corridor (origin OU end) DOIT
    # se situer dans la couronne externe 30 % du rayon fonctionnel R_max.
    # Interprétation institutionnelle : un corridor significatif relie le
    # cœur du territoire à sa périphérie biologique (couronne externe).
    r_inner, r_outer = compute_external_ring_radius(r_max_m)
    origin = path[0]
    endpoint = path[-1]
    wp = [waypoint.get("lat", 0), waypoint.get("lng", 0)]
    origin_dist_m = _dist_m(wp, [origin[0], origin[1]])
    end_dist_m = _dist_m(wp, [endpoint[0], endpoint[1]])
    r_outer_tol = r_outer * 1.10  # tolérance ±10 % au-delà R_max
    origin_in_ring = (r_inner <= origin_dist_m <= r_outer_tol)
    end_in_ring = (r_inner <= end_dist_m <= r_outer_tol)
    extremity_in_ring = origin_in_ring or end_in_ring

    valid = relies_2_vital and extremity_in_ring and consensus["consensus_score"] >= 50
    reason = "ok"
    if not relies_2_vital:
        reason = "fail_lt_2_vital_zones"
    elif not extremity_in_ring:
        reason = (f"fail_no_extremity_in_30pct_ring("
                  f"d_o={int(origin_dist_m)}m,d_e={int(end_dist_m)}m,"
                  f"ring=[{int(r_inner)},{int(r_outer)}])")
    elif consensus["consensus_score"] < 50:
        reason = f"fail_consensus_lt_50({consensus['consensus_score']})"

    return {
        "valid": valid,
        "reason": reason,
        "consensus": consensus,
        "metrics": {
            "length_m": round(L, 2),
            "zones_touched": zones_touched_count,
            "zones_touched_names": zones_touched_names[:5],
            "salines_touched": salines_touched,
            "relies_to_2_vital_zones": relies_2_vital,
            "origin_dist_from_waypoint_m": round(origin_dist_m, 1),
            "endpoint_dist_from_waypoint_m": round(end_dist_m, 1),
            "origin_in_external_ring_30pct": origin_in_ring,
            "endpoint_in_external_ring_30pct": end_in_ring,
            "extremity_in_external_ring_30pct": extremity_in_ring,
            "external_ring_m": [round(r_inner, 1), round(r_outer, 1)],
            "heatmap_samples": {
                "mffp_humides_avg": round(avg_humid, 3),
                "nasa_ndvi_avg": round(avg_ndvi, 3),
                "sepaq_pression_avg": round(avg_press, 3),
                "noaa_snow_cm_avg": round(avg_snow, 1),
                "usgs_gps_avg": round(avg_gps, 3),
                "mffp_ravages_orignal_avg": round(avg_ravages, 1),
            },
            "predictive_source": predictive_source,
        },
        "phase": "PHASE_XVII_SUPRA_ENGINE_CORRIDORS_ECOLOGIQUE_Ω",
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. Orchestration du bundle complet
# ═══════════════════════════════════════════════════════════════════════
def orchestrate_bundle(bundle: Dict[str, Any], species: str) -> Dict[str, Any]:
    """Annote tous les corridors + applique l'enforcement institutionnel.

    Si ENFORCE_MODE = True (P0 PHASE XVII), les corridors dont valid=False
    sont retirés de la liste mais conservés sous `corridors_rejected_phase_xvii`
    pour traçabilité institutionnelle.
    """
    if not isinstance(bundle, dict):
        return bundle
    waypoint = bundle.get("waypoint") or {}
    zones = bundle.get("zones") or []
    salines = bundle.get("salines") or []
    corridors = bundle.get("corridors") or []

    # Détermine r_max effectif (si modulator espèce dispo, sinon 780)
    r_max_m = 780.0
    try:
        from engines.v8_institutional.species_modulator_omega import compute_radius_action_m
        r_max_m = float(compute_radius_action_m(species).get("r_max_m") or 780.0)
    except Exception:
        pass

    annotated: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    pass_count = 0
    rejected_reasons: Dict[str, int] = {}
    for c in corridors:
        anno = synthesize_ecological_layers_for_corridor(
            c, species=species, waypoint=waypoint,
            bundle_zones=zones, bundle_salines=salines, r_max_m=r_max_m,
        )
        c["ecological_consensus"] = anno
        if anno.get("valid"):
            pass_count += 1
            annotated.append(c)
        else:
            r = anno.get("reason") or "unknown"
            r_short = r.split("(")[0]
            rejected_reasons[r_short] = rejected_reasons.get(r_short, 0) + 1
            if ENFORCE_MODE:
                rejected.append(c)
            else:
                annotated.append(c)

    if ENFORCE_MODE:
        bundle["corridors"] = annotated
        bundle["corridors_rejected_phase_xvii"] = [
            {
                "id": c.get("id"),
                "reason": (c.get("ecological_consensus") or {}).get("reason"),
                "consensus_score": ((c.get("ecological_consensus") or {}).get("consensus") or {}).get("consensus_score"),
            }
            for c in rejected
        ]
    else:
        bundle["corridors"] = annotated

    bundle["ecological_orchestrator_applied"] = True
    bundle["ecological_orchestrator_stats"] = {
        "total_input": len(corridors),
        "total_output": len(bundle["corridors"]),
        "passing_consensus": pass_count,
        "rejected_count": len(rejected),
        "rejected_reasons": rejected_reasons,
        "rate_pct": round(100.0 * pass_count / max(1, len(corridors)), 1),
        "heatmaps_status": get_heatmaps_status(),
        "consensus_weights": dict(ECOLOGICAL_CONSENSUS_WEIGHTS),
        "enforce_mode": ENFORCE_MODE,
        "external_ring_fraction": EXTERNAL_RING_FRACTION,
        "r_max_m_used": r_max_m,
        "phase": "PHASE_XVII_SUPRA_ENGINE_CORRIDORS_ECOLOGIQUE_Ω",
    }
    return bundle


# ═══════════════════════════════════════════════════════════════════════
# 6. Helpers internes
# ═══════════════════════════════════════════════════════════════════════
def _dist_m(a, b) -> float:
    R = 6371000.0
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(min(1.0, math.sqrt(h)))
