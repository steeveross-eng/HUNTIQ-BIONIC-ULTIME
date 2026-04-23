"""
ENGINE_RESEAU_VEINEUX_Ω — Implémentation X200 P0 (support)
============================================================
Phase    : X200-P0-ACTIVATION — support orchestration corridors
Activé comme SUPPORT des 3 engines P0 pour :
  - hiérarchie 5 niveaux CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE (restauration V7)
  - convergence 600 m ± 30 % (420-780 m)
  - règle « ≥ 2 zones vitales » enforçable

SOURCE V7 : core/scoring_pipeline/corridors_v10/classifier.py
"""
from __future__ import annotations

from typing import Dict, Any, List
from fastapi import APIRouter
from fastapi.responses import JSONResponse

FEATURE_FLAG_ACTIVE: bool = True
ENGINE_ID = "ENGINE_RESEAU_VEINEUX_Ω"
PHASE = "X200-P0-ACTIVATION"

# Hiérarchie 5 niveaux V7 canonique (restauration corridors_v10.classifier)
CORRIDOR_LEVELS_V7 = [
    {"level": "CRITIQUE", "score_min": 85, "score_max": 100, "color": "#CC0000",
     "weight_px": 3.0, "largeur_m": 4, "dash_array": "10,4"},
    {"level": "MAJEUR",   "score_min": 70, "score_max": 84,  "color": "#FF0000",
     "weight_px": 2.5, "largeur_m": 6, "dash_array": None},
    {"level": "FORT",     "score_min": 50, "score_max": 69,  "color": "#FF8C00",
     "weight_px": 2.0, "largeur_m": 11, "dash_array": None},
    {"level": "MODERE",   "score_min": 30, "score_max": 49,  "color": "#FFD700",
     "weight_px": 1.5, "largeur_m": 17, "dash_array": None},
    {"level": "FAIBLE",   "score_min": 0,  "score_max": 29,  "color": "#BFBFBF",
     "weight_px": 1.2, "largeur_m": 26, "dash_array": None},
]

# Rayon fonctionnel 600 m ± 30 %
FUNCTIONAL_RADIUS_NOMINAL_M = 600
FUNCTIONAL_RADIUS_MIN_M = 420
FUNCTIONAL_RADIUS_MAX_M = 780
MAIN_VEIN_CONVERGENCE_M = 15


def classify_corridor(score: float) -> Dict[str, Any]:
    """Classification 5 niveaux V7 par score 0-100."""
    for lvl in CORRIDOR_LEVELS_V7:
        if lvl["score_min"] <= score <= lvl["score_max"]:
            return {**lvl, "score": score}
    return {**CORRIDOR_LEVELS_V7[-1], "score": score}


def validate_functional_radius(radius_m: float) -> Dict[str, Any]:
    """Valide que le rayon fonctionnel respecte 600m ± 30%."""
    ok = FUNCTIONAL_RADIUS_MIN_M <= radius_m <= FUNCTIONAL_RADIUS_MAX_M
    return {
        "radius_m": radius_m,
        "conforme_600m_30pct": ok,
        "min": FUNCTIONAL_RADIUS_MIN_M,
        "max": FUNCTIONAL_RADIUS_MAX_M,
        "nominal": FUNCTIONAL_RADIUS_NOMINAL_M,
    }


def enforce_vital_zone_rule(connections: List[Dict]) -> Dict[str, Any]:
    """Règle V7 : corridor ≥ 2 zones vitales. Enforce mode."""
    count = len(connections or [])
    return {
        "connections_count": count,
        "min_required": 2,
        "corridor_valid": count >= 2,
        "rejection_reason": None if count >= 2 else "vital_zone_connections_insufficient",
    }


router = APIRouter(prefix="/api/v7-ultime/reseau-veineux", tags=["ENGINE_RESEAU_VEINEUX_Ω_X200_P0"])


# ═══════════════════════════════════════════════════════════════════════
# X200-P1-EXTERNAL-INFLOW_Ω — endpoints lecture seule
# ═══════════════════════════════════════════════════════════════════════
from engines.reseau_veineux_omega.external_inflow import (
    external_inflow_status,
    generate_entry_nodes,
    trace_organic_path,
    find_nearest_vital_zone,
    fuse_external_internal,
    classify_corridor_commandant,
    HIERARCHY_5_LEVELS_COMMANDANT,
)


@router.get("/external-inflow/status")
async def external_inflow_endpoint_status():
    return JSONResponse(external_inflow_status())


@router.post("/external-inflow/preview")
async def external_inflow_preview(payload: dict = None):
    """Génère un preview complet : entry_nodes + tracés + fusion (READ_ONLY)."""
    p = payload or {}
    lat = float(p.get("lat", 48.206657))
    lon = float(p.get("lon", -68.382422))
    count = int(p.get("entry_nodes_count", 16))
    vital_zones = p.get("vital_zones") or []
    internal_paths = p.get("internal_paths") or []
    signals = {
        "water_points": p.get("water_points", []),
        "steep_slope_points": p.get("steep_slope_points", []),
        "forest_cover": p.get("forest_cover", 0.6),
        "vital_zones": vital_zones,
    }

    entry_nodes = generate_entry_nodes(lat, lon, count=count, terrain_signals=signals)

    external_paths = []
    for node in entry_nodes:
        target = find_nearest_vital_zone(node, vital_zones)
        if target is None:
            continue
        path = trace_organic_path(node, target)
        # Score heuristique = weight_node * 100 pour classification
        score = node["weight"] * 100
        cls = classify_corridor_commandant(score)
        external_paths.append({
            "id": f"ext_{node['index']:02d}",
            "entry_node_id": node["id"],
            "target_type": target.get("type"),
            "path": path,
            "level": cls["level"],
            "color": cls["color"],
            "largeur_m": cls["largeur_m"],
            "weight_render": cls["weight"],
            "score": round(score, 2),
        })

    fusion_diag = fuse_external_internal(external_paths, internal_paths)

    return JSONResponse({
        "phase": "PHASE_X200_P1_EXTERNAL_INFLOW_Ω",
        "mode": "READ_ONLY",
        "waypoint": {"lat": lat, "lon": lon},
        "entry_nodes": entry_nodes,
        "entry_nodes_count": len(entry_nodes),
        "external_paths": external_paths,
        "external_paths_count": len(external_paths),
        "fusion": fusion_diag,
        "hierarchy_commandant": HIERARCHY_5_LEVELS_COMMANDANT,
        "contract": {
            "smoother_touched": False,
            "rendu_modified": False,
            "v30_read_write": False,
        },
    })


# ═══════════════════════════════════════════════════════════════════════
# GEOJSON ENDPOINT (X200-P1-ACTIVATION — READ_ONLY)
# ═══════════════════════════════════════════════════════════════════════
def _build_geojson(lat: float, lon: float, entry_nodes, external_paths,
                   internal_paths, fusion_diag) -> dict:
    features = []
    # Centre
    features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {"role": "center", "symbol": "+"},
    })
    # Entry nodes (Points)
    for n in entry_nodes:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [n["lng"], n["lat"]]},
            "properties": {
                "role": "entry_node", "id": n["id"],
                "bearing_deg": n["bearing_deg"], "radius_m": n["radius_m"],
                "weight": n["weight"], "components": n.get("components", {}),
            },
        })
    # External paths (LineStrings)
    for ep in external_paths:
        coords = [[p[1], p[0]] for p in ep["path"]]  # lng,lat pour GeoJSON
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "role": "external_path", "id": ep["id"],
                "entry_node_id": ep["entry_node_id"], "target_type": ep["target_type"],
                "level": ep["level"], "color": ep["color"],
                "largeur_m": ep["largeur_m"], "weight_render": ep["weight_render"],
                "score": ep["score"],
            },
        })
    # Internal paths (LineStrings — si fournis)
    for ip in (internal_paths or []):
        coords = [[p[1], p[0]] for p in ip.get("path", [])]
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "role": "internal_path", "id": ip.get("id"),
                "largeur_m": ip.get("largeur_m"),
            },
        })
    # Fusion points (Points)
    for f in fusion_diag.get("fusion_points", []):
        # Récupérer le point de contact à partir des indices
        ext_id = f["external_id"]; int_id = f["internal_id"]
        ext = next((e for e in external_paths if e["id"] == ext_id), None)
        inte = next((i for i in (internal_paths or []) if i.get("id") == int_id), None)
        if ext and inte and f["contact_point_external_idx"] < len(ext["path"]):
            pt = ext["path"][f["contact_point_external_idx"]]
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [pt[1], pt[0]]},
                "properties": {
                    "role": "fusion_point",
                    "external_id": ext_id, "internal_id": int_id,
                    "distance_m": f["distance_m"],
                    "width_multiplier": f["width_multiplier"],
                    "new_width_m": f["new_width_m"],
                },
            })
    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "phase": "PHASE_X200_P1_EXTERNAL_INFLOW_ACTIVATION_Ω",
            "waypoint": {"lat": lat, "lon": lon},
            "entry_nodes_count": len(entry_nodes),
            "external_paths_count": len(external_paths),
            "internal_paths_count": len(internal_paths or []),
            "fusions_detected": fusion_diag.get("fusions_detected", 0),
            "hierarchy_commandant": HIERARCHY_5_LEVELS_COMMANDANT,
            "contract": {
                "smoother_touched": False,
                "rendu_modified": False,
                "v30_read_write": False,
            },
        },
    }


@router.post("/external-inflow/geojson")
async def external_inflow_geojson(payload: dict = None):
    """Sérialisation GeoJSON FeatureCollection (READ_ONLY)."""
    p = payload or {}
    lat = float(p.get("lat", 48.206657))
    lon = float(p.get("lon", -68.382422))
    count = int(p.get("entry_nodes_count", 16))
    vital_zones = p.get("vital_zones") or []
    internal_paths = p.get("internal_paths") or []
    signals = {
        "water_points": p.get("water_points", []),
        "steep_slope_points": p.get("steep_slope_points", []),
        "forest_cover": p.get("forest_cover", 0.6),
        "vital_zones": vital_zones,
    }
    entry_nodes = generate_entry_nodes(lat, lon, count=count, terrain_signals=signals)
    external_paths = []
    for node in entry_nodes:
        target = find_nearest_vital_zone(node, vital_zones)
        if target is None:
            continue
        path = trace_organic_path(node, target)
        score = node["weight"] * 100
        cls = classify_corridor_commandant(score)
        external_paths.append({
            "id": f"ext_{node['index']:02d}",
            "entry_node_id": node["id"],
            "target_type": target.get("type"),
            "path": path,
            "level": cls["level"], "color": cls["color"],
            "largeur_m": cls["largeur_m"], "weight_render": cls["weight"],
            "score": round(score, 2),
        })
    fusion_diag = fuse_external_internal(external_paths, internal_paths)
    return JSONResponse(_build_geojson(lat, lon, entry_nodes, external_paths,
                                       internal_paths, fusion_diag))


@router.get("/external-inflow/geojson")
async def external_inflow_geojson_get(
    lat: float = 48.206657, lon: float = -68.382422, entry_nodes_count: int = 16,
):
    """Variante GET avec waypoint par défaut et aucune zone vitale/internal (démo)."""
    # Zones vitales démo par défaut pour que le GeoJSON soit non vide
    demo_vital = [
        {"type": "salines", "lat": lat + 0.0005, "lng": lon + 0.0005, "score": 90},
        {"type": "repos",   "lat": lat + 0.0003, "lng": lon - 0.0004, "score": 70},
    ]
    return await external_inflow_geojson({
        "lat": lat, "lon": lon, "entry_nodes_count": entry_nodes_count,
        "vital_zones": demo_vital,
    })


@router.get("/status")
async def status():
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "phase": PHASE,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "levels_5_restored": [l["level"] for l in CORRIDOR_LEVELS_V7],
        "functional_radius_600_30pct": [FUNCTIONAL_RADIUS_MIN_M, FUNCTIONAL_RADIUS_MAX_M],
        "main_vein_convergence_m": MAIN_VEIN_CONVERGENCE_M,
        "v7_source": "core/scoring_pipeline/corridors_v10/classifier.py",
    })


@router.get("/levels")
async def levels():
    return JSONResponse({"levels": CORRIDOR_LEVELS_V7})


@router.post("/compute")
async def compute(payload: dict = None):
    payload = payload or {}
    score = float(payload.get("score", 0))
    radius = float(payload.get("radius_m", 600))
    connections = payload.get("vital_connections", [])
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "classification": classify_corridor(score),
        "functional_radius": validate_functional_radius(radius),
        "vital_zone_rule": enforce_vital_zone_rule(connections),
    })
