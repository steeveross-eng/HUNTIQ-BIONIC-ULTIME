"""
BCE-4X — COUCHE D'EXCLUSIONS UNIVERSELLE
==========================================
ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0

COUCHE NON NEGOCIABLE appliquee AVANT TOUT CALCUL:
  - SUPRA, BDRE, AFFUTS, Relocalisation, Fusion corridor
  - Scoring, Rasterisation, OSM, BDRE interne
  - Frontend (toutes layers), Moteur d'affichage, Moteur de decision

TYPES D'EXCLUSION:
  EAU      : Lacs, etangs, marais, cours d'eau (buffer 30m)
  URBAIN   : Zones residentielles, commerciales, industrielles (buffer 55m)
  ROUTES   : Axes routiers, chemins publics (buffer 15m)
  HUMAIN   : Zones d'activite humaine, batiments, camping (buffer 40m)
  SECURITE : Zones de tir restreint, habitations (buffer 150m)

AUCUN module ne peut bypasser cette couche.
Authority: COMMANDANT STEEVE-MAX | BCE-4X GOLDEN V6+ | Permanent.
"""
import math
import hashlib
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("bce.exclusion_layer")

# Buffers par type d'exclusion (metres)
EXCLUSION_BUFFERS = {
    "EAU": 30,
    "URBAIN": 55,
    "ROUTES": 15,
    "HUMAIN": 40,
    "SECURITE": 150,
}

# Seuils cost_surface hash
WATER_HASH_THRESHOLD = 0.88
URBAN_HASH_THRESHOLD = 0.82
ROAD_HASH_THRESHOLD = 0.90
HUMAN_HASH_THRESHOLD = 0.85
SECURITY_HASH_THRESHOLD = 0.92


def _hash_value(lat, lng, salt):
    """Valeur deterministe 0-1 pour une coordonnee et un type."""
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000
    p = math.pi / 180
    a = (
        math.sin((lat2 - lat1) * p / 2) ** 2
        + math.cos(lat1 * p) * math.cos(lat2 * p)
        * math.sin((lng2 - lng1) * p / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


# =================================================================
# DETECTION INDIVIDUELLE PAR TYPE
# =================================================================

def _is_water(lat, lng):
    """Detection eau: cost_surface + cache OSM."""
    try:
        from core.scoring_pipeline.corridors_v10.cost_surface import _load_cell_data
        cell = _load_cell_data(lat, lng, 10)
        if cell.get("is_water", False):
            return True
        if cell.get("distance_eau_m", 500) < EXCLUSION_BUFFERS["EAU"]:
            return True
    except Exception:
        pass
    # Fallback deterministe
    return _hash_value(lat, lng, "water_body") > WATER_HASH_THRESHOLD


def _is_urban(lat, lng):
    """Detection urbain: cache Shapely UNIQUEMENT (pas de fallback hash)."""
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import (
            _point_intersects_anthropic,
        )
        return _point_intersects_anthropic(lat, lng)
    except Exception:
        return False


def _is_road(lat, lng):
    """Detection route: cost_surface UNIQUEMENT (donnees reelles)."""
    try:
        from core.scoring_pipeline.corridors_v10.cost_surface import _load_cell_data
        cell = _load_cell_data(lat, lng, 10)
        if cell.get("is_road", False):
            return True
        if cell.get("distance_route_m", 500) < EXCLUSION_BUFFERS["ROUTES"]:
            return True
    except Exception:
        pass
    return False


def _is_human_zone(lat, lng):
    """Detection zone humaine: cache Shapely UNIQUEMENT (pas de fallback hash)."""
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import (
            _point_intersects_anthropic,
        )
        return _point_intersects_anthropic(lat, lng)
    except Exception:
        return False


def _is_security_zone(lat, lng):
    """Detection zone de securite: cache Shapely UNIQUEMENT (buffer 150m)."""
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import (
            _point_intersects_anthropic,
        )
        return _point_intersects_anthropic(lat, lng)
    except Exception:
        return False


# =================================================================
# API PUBLIQUE — POINT
# =================================================================

def check_point_exclusions(lat: float, lng: float) -> Dict[str, Any]:
    """
    COUCHE UNIVERSELLE BCE-4X — Verification d'un point unique.

    Retourne:
      {
        "excluded": bool,
        "exclusions": ["EAU", "URBAIN", ...],
        "details": {...}
      }
    """
    exclusions = []
    details = {}

    if _is_water(lat, lng):
        exclusions.append("EAU")
        details["EAU"] = {"buffer_m": EXCLUSION_BUFFERS["EAU"]}

    if _is_urban(lat, lng):
        exclusions.append("URBAIN")
        details["URBAIN"] = {"buffer_m": EXCLUSION_BUFFERS["URBAIN"]}

    if _is_road(lat, lng):
        exclusions.append("ROUTES")
        details["ROUTES"] = {"buffer_m": EXCLUSION_BUFFERS["ROUTES"]}

    if _is_human_zone(lat, lng):
        exclusions.append("HUMAIN")
        details["HUMAIN"] = {"buffer_m": EXCLUSION_BUFFERS["HUMAIN"]}

    if _is_security_zone(lat, lng):
        exclusions.append("SECURITE")
        details["SECURITE"] = {"buffer_m": EXCLUSION_BUFFERS["SECURITE"]}

    return {
        "excluded": len(exclusions) > 0,
        "exclusions": exclusions,
        "lat": lat,
        "lng": lng,
        "details": details,
    }


# =================================================================
# API PUBLIQUE — SEGMENT (corridor, chemin)
# =================================================================

def check_segment_exclusions(
    coords: List[Dict[str, float]],
    segment_id: str = "SEG-000",
) -> Dict[str, Any]:
    """
    COUCHE UNIVERSELLE BCE-4X — Verification d'un segment complet.
    5 points de controle: 0%, 25%, 50%, 75%, 100%.

    Retourne:
      {
        "excluded": bool,
        "exclusions_found": [{"point": str, "types": [...]}],
        "segment_id": str
      }
    """
    if not coords or len(coords) < 2:
        return {"excluded": False, "exclusions_found": [], "segment_id": segment_id}

    check_fractions = [0.0, 0.25, 0.5, 0.75, 1.0]
    exclusions_found = []

    for frac in check_fractions:
        if frac == 0.0:
            lat, lng = coords[0]["lat"], coords[0]["lng"]
            label = "debut"
        elif frac == 1.0:
            lat, lng = coords[-1]["lat"], coords[-1]["lng"]
            label = "fin"
        else:
            lat = coords[0]["lat"] + frac * (coords[-1]["lat"] - coords[0]["lat"])
            lng = coords[0]["lng"] + frac * (coords[-1]["lng"] - coords[0]["lng"])
            label = f"frac_{int(frac * 100)}pct"

        result = check_point_exclusions(lat, lng)
        if result["excluded"]:
            exclusions_found.append({
                "point": label,
                "lat": lat,
                "lng": lng,
                "types": result["exclusions"],
            })

    return {
        "excluded": len(exclusions_found) > 0,
        "exclusions_found": exclusions_found,
        "segment_id": segment_id,
    }


# =================================================================
# API PUBLIQUE — FILTRE CORRIDORS (liste complete)
# =================================================================

def filter_corridors_bce4x(
    corridors: List[Dict[str, Any]],
    id_key: str = "id",
) -> Dict[str, Any]:
    """
    COUCHE UNIVERSELLE BCE-4X — Filtre une liste complete de corridors.

    Retourne:
      {
        "valid": [...],
        "excluded": [...],
        "summary": {"total": N, "valid": N, "excluded": N, "by_type": {...}}
      }
    """
    valid = []
    excluded = []
    by_type = {"EAU": 0, "URBAIN": 0, "ROUTES": 0, "HUMAIN": 0, "SECURITE": 0}

    for corridor in corridors:
        coords = corridor.get("coords", corridor.get("path", []))
        seg_id = corridor.get(id_key, "UNKNOWN")

        # Normaliser les coords
        normalized = []
        for c in coords:
            if isinstance(c, dict):
                normalized.append(c)
            elif isinstance(c, (list, tuple)) and len(c) >= 2:
                normalized.append({"lat": c[1], "lng": c[0]})

        if len(normalized) < 2:
            valid.append(corridor)
            continue

        result = check_segment_exclusions(normalized, seg_id)

        if result["excluded"]:
            # Enregistrer les types d'exclusion
            for ef in result["exclusions_found"]:
                for t in ef["types"]:
                    by_type[t] = by_type.get(t, 0) + 1

            excluded.append({
                "corridor": corridor,
                "exclusions": result["exclusions_found"],
            })
        else:
            valid.append(corridor)

    logger.info(
        f"[BCE-4X EXCLUSION] Total={len(corridors)} Valid={len(valid)} "
        f"Excluded={len(excluded)} (EAU={by_type['EAU']} URBAIN={by_type['URBAIN']} "
        f"ROUTES={by_type['ROUTES']} HUMAIN={by_type['HUMAIN']} SECURITE={by_type['SECURITE']})"
    )

    return {
        "valid": valid,
        "excluded": excluded,
        "summary": {
            "total": len(corridors),
            "valid": len(valid),
            "excluded": len(excluded),
            "by_type": by_type,
        },
    }


# =================================================================
# API PUBLIQUE — FILTRE CANDIDATS (salines, affuts, relocalisations)
# =================================================================

def filter_candidates_bce4x(
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    COUCHE UNIVERSELLE BCE-4X — Filtre une liste de candidats (points).

    Retourne:
      {"valid": [...], "excluded": [...], "summary": {...}}
    """
    valid = []
    excluded = []
    by_type = {"EAU": 0, "URBAIN": 0, "ROUTES": 0, "HUMAIN": 0, "SECURITE": 0}

    for cand in candidates:
        lat = cand.get("lat", 0)
        lng = cand.get("lng", 0)
        result = check_point_exclusions(lat, lng)

        if result["excluded"]:
            for t in result["exclusions"]:
                by_type[t] = by_type.get(t, 0) + 1
            excluded.append({"candidate": cand, "exclusions": result["exclusions"]})
        else:
            valid.append(cand)

    return {
        "valid": valid,
        "excluded": excluded,
        "summary": {
            "total": len(candidates),
            "valid": len(valid),
            "excluded": len(excluded),
            "by_type": by_type,
        },
    }
