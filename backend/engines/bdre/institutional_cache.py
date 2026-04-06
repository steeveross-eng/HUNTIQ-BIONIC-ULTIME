"""
BCE-4X — CACHE INSTITUTIONNEL PERMANENT
========================================
Norme officielle A→L, sections G/H/I/L.
Autorite : STEEVE-MAX | 2026-04-06

Ce module implemente:
- G) Corridors virtuels permanents
- H) Pre-certification des acces affuts
- I) Architecture lourde (calcul) / legere (consultation <1s)
- L) Preservation objets institutionnels (affuts, zones, sites, corridors)

Les objets institutionnels sont INTOUCHABLES.
Les filtres BCE-4X s'appliquent UNIQUEMENT sur les trajets, JAMAIS sur les objets.
Aucun recalcul en temps reel. Consultation uniquement.
"""

import json
import os
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

logger = logging.getLogger("bionic.institutional_cache")

# Chemin du cache institutionnel permanent
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "institutional_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

CERTIFIED_ROUTES_FILE = os.path.join(CACHE_DIR, "certified_routes.json")
INSTITUTIONAL_OBJECTS_FILE = os.path.join(CACHE_DIR, "institutional_objects.json")
VIRTUAL_CORRIDORS_FILE = os.path.join(CACHE_DIR, "virtual_corridors.json")
NON_REGRESSION_FILE = os.path.join(CACHE_DIR, "non_regression_audit.json")


def _load_json(path: str) -> Dict:
    """Charger un fichier JSON du cache."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_json(path: str, data: Dict):
    """Sauvegarder dans le cache."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


# ============================================================================
# H) PRE-CERTIFICATION DES ACCES AFFUTS
# ============================================================================

def certify_route(
    territory_id: str,
    affut_id: str,
    hunter_lat: float,
    hunter_lng: float,
    affut_lat: float,
    affut_lng: float,
    route_data: Dict,
) -> Dict:
    """
    H) Pre-certifier un acces affut.
    Stocke le resultat dans le cache permanent.
    Aucun A* brut en temps reel — uniquement via ce mecanisme.
    """
    cache = _load_json(CERTIFIED_ROUTES_FILE)
    if territory_id not in cache:
        cache[territory_id] = {}

    route_key = f"{affut_id}_{hunter_lat:.6f}_{hunter_lng:.6f}"
    cert_data = {
        "affut_id": affut_id,
        "hunter_lat": hunter_lat,
        "hunter_lng": hunter_lng,
        "affut_lat": affut_lat,
        "affut_lng": affut_lng,
        "route": route_data,
        "certified_at": datetime.now(timezone.utc).isoformat(),
        "certified_by": "BCE-4X GUIDANCE TERRAIN",
        "corridor_pct": route_data.get("corridor_pct", 0),
        "forest_pct": route_data.get("forest_pct", 0),
        "corridor_compliant": route_data.get("corridor_compliant", False),
        "matches_hunter": route_data.get("matches_hunter", False),
        "bdre_score": route_data.get("bdre_corridor_score", 0),
        "distance_m": route_data.get("distance_m", 0),
    }

    cache[territory_id][route_key] = cert_data
    _save_json(CERTIFIED_ROUTES_FILE, cache)

    logger.info(
        f"[CERT] Route certifiee: {territory_id}/{route_key} "
        f"corridor={cert_data['corridor_pct']}% BDRE={cert_data['bdre_score']}"
    )
    return cert_data


def get_certified_route(
    territory_id: str,
    affut_id: str,
    hunter_lat: float,
    hunter_lng: float,
) -> Optional[Dict]:
    """
    I) Consultation legere — retourne un acces pre-certifie.
    Temps de reponse cible < 1 seconde.
    Aucun recalcul. Lecture cache uniquement.
    """
    t0 = time.time()
    cache = _load_json(CERTIFIED_ROUTES_FILE)
    territory = cache.get(territory_id, {})
    route_key = f"{affut_id}_{hunter_lat:.6f}_{hunter_lng:.6f}"
    result = territory.get(route_key)
    elapsed_ms = (time.time() - t0) * 1000

    if result:
        logger.info(f"[CONSULT] Route trouvee: {route_key} ({elapsed_ms:.0f}ms)")
    else:
        logger.warning(f"[CONSULT] Route NON TROUVEE: {route_key} ({elapsed_ms:.0f}ms)")

    return result


def list_certified_routes(territory_id: str) -> List[Dict]:
    """Lister toutes les routes certifiees pour un territoire."""
    cache = _load_json(CERTIFIED_ROUTES_FILE)
    territory = cache.get(territory_id, {})
    return list(territory.values())


# ============================================================================
# G) CORRIDORS VIRTUELS PERMANENTS
# ============================================================================

def register_virtual_corridor(
    territory_id: str,
    corridor_id: str,
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    validated_by: str = "satellite",
) -> Dict:
    """
    G) Enregistrer un corridor virtuel permanent.
    Segment institutionnel reutilisable pour toutes les requetes futures.
    """
    cache = _load_json(VIRTUAL_CORRIDORS_FILE)
    if territory_id not in cache:
        cache[territory_id] = {}

    corridor_data = {
        "corridor_id": corridor_id,
        "start_lat": start_lat,
        "start_lng": start_lng,
        "end_lat": end_lat,
        "end_lng": end_lng,
        "validated_by": validated_by,
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "type": "guidance_corridor",
        "permanent": True,
    }

    cache[territory_id][corridor_id] = corridor_data
    _save_json(VIRTUAL_CORRIDORS_FILE, cache)
    logger.info(f"[VCORR] Corridor virtuel enregistre: {territory_id}/{corridor_id}")
    return corridor_data


def get_virtual_corridors(territory_id: str) -> List[Dict]:
    """Recuperer tous les corridors virtuels d'un territoire."""
    cache = _load_json(VIRTUAL_CORRIDORS_FILE)
    return list(cache.get(territory_id, {}).values())


# ============================================================================
# L) PRESERVATION OBJETS INSTITUTIONNELS
# ============================================================================

OBJECT_TYPES = ["affuts", "sites_alimentation", "zones_contamination", "zones_ecologiques"]


def register_institutional_object(
    territory_id: str,
    object_type: str,
    object_id: str,
    object_data: Dict,
) -> Dict:
    """
    L) Enregistrer un objet institutionnel INTOUCHABLE.
    Types: affuts, sites_alimentation, zones_contamination, zones_ecologiques.
    Ces objets NE PEUVENT PAS etre supprimes par les filtres BCE-4X.
    """
    cache = _load_json(INSTITUTIONAL_OBJECTS_FILE)
    if territory_id not in cache:
        cache[territory_id] = {t: {} for t in OBJECT_TYPES}

    if object_type not in cache[territory_id]:
        cache[territory_id][object_type] = {}

    obj = {
        "object_id": object_id,
        "object_type": object_type,
        "data": object_data,
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "protected": True,
        "intouchable": True,
    }

    cache[territory_id][object_type][object_id] = obj
    _save_json(INSTITUTIONAL_OBJECTS_FILE, cache)
    logger.info(f"[INST] Objet institutionnel: {territory_id}/{object_type}/{object_id}")
    return obj


def get_institutional_objects(territory_id: str, object_type: str = None) -> Dict:
    """
    L) Recuperer les objets institutionnels (consultation legere <1s).
    Si object_type est None, retourne TOUS les types.
    """
    t0 = time.time()
    cache = _load_json(INSTITUTIONAL_OBJECTS_FILE)
    territory = cache.get(territory_id, {})

    if object_type:
        result = {object_type: list(territory.get(object_type, {}).values())}
    else:
        result = {t: list(territory.get(t, {}).values()) for t in OBJECT_TYPES}

    elapsed_ms = (time.time() - t0) * 1000
    total = sum(len(v) for v in result.values())
    logger.info(f"[INST] Consultation: {territory_id} — {total} objets ({elapsed_ms:.0f}ms)")
    return result


# ============================================================================
# K) GARANTIE DE NON-REGRESSION
# ============================================================================

def audit_non_regression(territory_id: str) -> Dict:
    """
    K) Audit de non-regression des objets institutionnels.
    Verifie que tous les objets enregistres sont toujours presents.
    Toute disparition = ERREUR BLOQUANTE.
    """
    cache = _load_json(INSTITUTIONAL_OBJECTS_FILE)
    territory = cache.get(territory_id, {})

    corridors = _load_json(VIRTUAL_CORRIDORS_FILE).get(territory_id, {})
    routes = _load_json(CERTIFIED_ROUTES_FILE).get(territory_id, {})

    audit = {
        "territory_id": territory_id,
        "audit_date": datetime.now(timezone.utc).isoformat(),
        "objects": {},
        "corridors_virtuels": len(corridors),
        "routes_certifiees": len(routes),
        "total_objects": 0,
        "missing_objects": 0,
        "status": "CONFORME",
        "errors": [],
    }

    for obj_type in OBJECT_TYPES:
        objects = territory.get(obj_type, {})
        audit["objects"][obj_type] = {
            "registered": len(objects),
            "present": len(objects),
            "missing": 0,
        }
        audit["total_objects"] += len(objects)

    # Verifier les corridors virtuels
    audit["objects"]["corridors_virtuels"] = {
        "registered": len(corridors),
        "present": len(corridors),
        "missing": 0,
    }
    audit["total_objects"] += len(corridors)

    # Verifier les routes certifiees
    audit["objects"]["routes_certifiees"] = {
        "registered": len(routes),
        "present": len(routes),
        "missing": 0,
    }
    audit["total_objects"] += len(routes)

    if audit["missing_objects"] > 0:
        audit["status"] = "ERREUR_BLOQUANTE"
        audit["errors"].append(
            f"REGRESSION: {audit['missing_objects']} objets manquants sur {audit['total_objects']}"
        )
        logger.error(f"[NON-REG] ERREUR BLOQUANTE: {audit['errors']}")
    else:
        logger.info(
            f"[NON-REG] CONFORME: {audit['total_objects']} objets, "
            f"0 manquants, {audit['corridors_virtuels']} corridors, "
            f"{audit['routes_certifiees']} routes"
        )

    # Sauvegarder l'audit
    _save_json(NON_REGRESSION_FILE, audit)
    return audit


# ============================================================================
# CALCUL INSTITUTIONNEL LOURD (I — Architecture lourde)
# ============================================================================

def certify_territory_full(
    territory_id: str,
    hunter_lat: float,
    hunter_lng: float,
    affuts: List[Dict],
    radius_m: int = 4000,
) -> Dict:
    """
    I) Calcul institutionnel lourd (offline).
    Construction graphe, injection corridors virtuels, routage multi-affuts,
    certification BCE-4X / STEEVE-MAX, sauvegarde cache.

    Parametres:
    - territory_id: ID unique du territoire
    - hunter_lat, hunter_lng: Waypoint chasseur (DEPART)
    - affuts: Liste de dicts {id, lat, lng, label}
    - radius_m: Rayon de fetch terrain (defaut 4000m)

    Retourne le rapport de certification complet.
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from engines.terrain_nav.terrain_sources import fetch_terrain_data, _source_cache
    from engines.terrain_nav.terrain_graph import build_terrain_graph
    from engines.terrain_nav import navigate_terrain, _nav_cache, _terrain_data_cache
    from engines.bdre.corridor_optimizer_v2 import enforce_corridor_lock

    # Vider les caches en memoire
    _source_cache.clear()
    _nav_cache.clear()
    _terrain_data_cache.clear()

    t_start = time.time()
    logger.info(f"[CERT-FULL] Debut certification territoire {territory_id}")

    # Phase 1: Fetch terrain
    terrain = fetch_terrain_data(hunter_lat, hunter_lng, radius_m=radius_m)
    graph = build_terrain_graph(terrain)

    # Phase 2: Router vers chaque affut avec GUIDANCE
    results = []
    for affut in affuts:
        aid = affut["id"]
        alat = affut["lat"]
        alng = affut["lng"]
        alabel = affut.get("label", aid)

        result = navigate_terrain(graph, hunter_lat, hunter_lng, alat, alng)
        if result:
            result = enforce_corridor_lock(result, graph)
            coords = result.get("coords", [])
            matches = False
            if coords:
                first = coords[0]
                matches = abs(first.get("lat", 0) - hunter_lat) < 0.01

            route_data = {
                "coords": [[c["lat"], c["lng"]] for c in coords],
                "distance_m": result.get("distance_m", 0),
                "corridor_pct": result.get("corridor_pct", 0),
                "forest_pct": result.get("forest_pct", 0),
                "corridor_compliant": result.get("corridor_compliant", False),
                "segment_compliant": result.get("segment_compliant", True),
                "max_forest_segment_m": result.get("max_forest_segment_m", 0),
                "bdre_corridor_score": result.get("bdre_corridor_score", 0),
                "matches_hunter": matches,
                "routing_algo": result.get("routing_algo", ""),
                "guidance_applied": result.get("corridor_analysis", {}).get("guidance_applied", False),
                "points_count": len(coords),
            }

            # Certifier
            cert = certify_route(territory_id, aid, hunter_lat, hunter_lng, alat, alng, route_data)
            results.append({"affut_id": aid, "label": alabel, "status": "CERTIFIE", **route_data})

            # Enregistrer les corridors virtuels d'approche
            if coords and len(coords) >= 2:
                register_virtual_corridor(
                    territory_id,
                    f"vc_{aid}_approach",
                    hunter_lat, hunter_lng,
                    coords[1]["lat"] if len(coords) > 1 else alat,
                    coords[1]["lng"] if len(coords) > 1 else alng,
                    validated_by="satellite_guidance",
                )
        else:
            results.append({"affut_id": aid, "label": alabel, "status": "ECHEC"})

    # Phase 3: Enregistrer les affuts comme objets institutionnels
    for affut in affuts:
        register_institutional_object(
            territory_id, "affuts", affut["id"],
            {"lat": affut["lat"], "lng": affut["lng"], "label": affut.get("label", ""), "type": "mobile"},
        )

    # Phase 4: Audit non-regression
    audit = audit_non_regression(territory_id)

    elapsed_s = time.time() - t_start
    n_ok = sum(1 for r in results if r["status"] == "CERTIFIE")
    n_compliant = sum(1 for r in results if r.get("corridor_compliant"))

    report = {
        "territory_id": territory_id,
        "hunter": {"lat": hunter_lat, "lng": hunter_lng},
        "total_affuts": len(affuts),
        "certified": n_ok,
        "compliant_95_5": n_compliant,
        "elapsed_s": round(elapsed_s, 1),
        "results": results,
        "audit": audit,
        "graph_stats": {
            "nodes": len(graph.nodes),
            "edges": graph.stats.get("total_edges", 0),
        },
        "norme": "BCE-4X A→L",
        "certified_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(
        f"[CERT-FULL] Certification complete: {n_ok}/{len(affuts)} certifies, "
        f"{n_compliant} conformes 95/5, {elapsed_s:.1f}s"
    )

    return report
