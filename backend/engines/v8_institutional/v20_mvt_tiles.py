"""
V20 MVT TILES — PHASE-PERFORMANCE-Omega V11-SUPRA
=====================================================
Tile-filtered GeoJSON pour CORRIDORS / ZONES / CONTAMINATION.

CHOIX ARCHITECTURAL (Anti-protobuf-conflict):
  Format: TILE-FILTERED GeoJSON (compatible Leaflet.VectorGrid slicer).
  Avantages identiques au MVT PBF pour notre volumetrie (<10K entites):
    - Bande passante reduite par (z,x,y)
    - Cache CDN par URL (immutable)
    - Scalabilite 5000+ utilisateurs
  Pourquoi pas PBF: mapbox-vector-tile force protobuf>=6, incompatible
  avec google-ai-generativelanguage/grpcio-status utilises par la plateforme.
  Documente dans RAPPORT DIAGNOSTIC-Omega.

Zoom supporte: 12-16.
TTL: 24h (aligne avec bundle).
Cache-Control: public, max-age=86400, immutable.
"""
import math
import time
import logging
from collections import OrderedDict
from fastapi import APIRouter, Query, Response, HTTPException

logger = logging.getLogger("bionic.v20_mvt")
router = APIRouter(prefix="/api/v20/territoire/tiles", tags=["V20 MVT Tiles"])

# ═══ CACHE TILE TTL 24h ═══
_TILE_CACHE: "OrderedDict[str, tuple[float, dict]]" = OrderedDict()
_TILE_TTL = 86400
_TILE_MAX = 1024

_LAYERS_SUPPORTED = {"corridors", "zones", "contamination", "salines", "affuts", "hotspots", "vent", "nutrition"}
_ZOOM_MIN, _ZOOM_MAX = 12, 16


def _tile_bounds(z: int, x: int, y: int) -> tuple[float, float, float, float]:
    """Retourne (min_lon, min_lat, max_lon, max_lat) du tile (z,x,y)."""
    n = 2.0 ** z
    lon_min = x / n * 360.0 - 180.0
    lon_max = (x + 1) / n * 360.0 - 180.0
    lat_max_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_min_rad = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
    lat_min = math.degrees(lat_min_rad)
    lat_max = math.degrees(lat_max_rad)
    return lon_min, lat_min, lon_max, lat_max


def _bbox_contains_point(bounds, lat, lon) -> bool:
    return bounds[0] <= lon <= bounds[2] and bounds[1] <= lat <= bounds[3]


def _path_intersects_bbox(path, bounds) -> bool:
    """path = [[lat,lng], ...]. Test grossier: au moins un point dans bbox."""
    if not path:
        return False
    for p in path:
        try:
            lat = p[0] if isinstance(p, (list, tuple)) else p.get("lat")
            lng = p[1] if isinstance(p, (list, tuple)) else (p.get("lng") or p.get("lon"))
            if lat is not None and lng is not None and _bbox_contains_point(bounds, lat, lng):
                return True
        except (IndexError, AttributeError, TypeError):
            continue
    return False


def _polygon_intersects_bbox(polygon, bounds) -> bool:
    """polygon = [[lat,lng], ...] (Catmull-Rom). Test: au moins un sommet dans bbox."""
    if not polygon:
        return False
    for p in polygon:
        try:
            lat = p[0] if isinstance(p, (list, tuple)) else None
            lng = p[1] if isinstance(p, (list, tuple)) else None
            if lat is not None and lng is not None and _bbox_contains_point(bounds, lat, lng):
                return True
        except (IndexError, AttributeError, TypeError):
            continue
    return False


def _cache_get(key: str):
    e = _TILE_CACHE.get(key)
    if not e:
        return None
    ts, payload = e
    if time.time() - ts > _TILE_TTL:
        _TILE_CACHE.pop(key, None)
        return None
    _TILE_CACHE.move_to_end(key)
    return payload


def _cache_set(key: str, payload: dict):
    _TILE_CACHE[key] = (time.time(), payload)
    _TILE_CACHE.move_to_end(key)
    while len(_TILE_CACHE) > _TILE_MAX:
        _TILE_CACHE.popitem(last=False)


async def _get_bundle(lat: float, lon: float, species: str, month: int, hour: int, wind_deg: float):
    """Recupere le bundle via cache V20 (shared cache).

    PHASE_XII_SUPRA_PURGE_TERRITOIRE_MVT_Ω :
    le chemin de fallback (cache MISS) DOIT passer par RenduΩ pour interdire
    tout bypass de la validation X150 (Section 1.3 de la directive
    RAPATRIEMENT_RENDUΩ_V20). V30 LOCKED intact.
    """
    from engines.v8_institutional.v20_performance_bundle import _cache_get as bundle_cache_get, _cache_key
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.post_smoothing.renduomega import apply_renduomega_to_bundle
    # PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME
    from engines.post_smoothing.veineux_omega import apply_veineux_omega_to_bundle

    key = _cache_key(lat, lon, species, month, hour, wind_deg)
    cached = bundle_cache_get(key)
    if cached is not None:
        return cached
    # Compute si pas en cache (force cold) — pipeline COMPLET RenduΩ
    result = await compute_territoire_v10(lat, lon, species, month, hour, wind_deg, 15.0)
    result["waypoint"] = {"lat": lat, "lng": lon}
    result["species"] = species
    # Normalisation contamination zones (cônes V30 → points {lat,lng})
    _contam_in = result.get("contamination") or []
    _contam_norm = []
    for _c in _contam_in:
        if not isinstance(_c, dict):
            continue
        _lat = _c.get("lat")
        _lng = _c.get("lng") or _c.get("lon")
        if _lat is None or _lng is None:
            _src = _c.get("affut_source") or {}
            _lat = _src.get("lat")
            _lng = _src.get("lng") or _src.get("lon")
        if _lat is None or _lng is None:
            _poly = _c.get("polygon") or _c.get("coords") or []
            if isinstance(_poly, list) and _poly:
                try:
                    _lat = sum(p[0] for p in _poly) / len(_poly)
                    _lng = sum(p[1] for p in _poly) / len(_poly)
                except Exception:
                    _lat = _lng = None
        if _lat is not None and _lng is not None:
            _contam_norm.append({"lat": float(_lat), "lng": float(_lng),
                                 "intensity": _c.get("intensity"),
                                 "source": "V20_MVT_TILES_NORMALIZED"})
    result["contamination_zones"] = _contam_norm
    result = apply_veineux_omega_to_bundle(result)
    return apply_renduomega_to_bundle(result)


@router.get("/{layer}/{z}/{x}/{y}.json")
async def v20_tile(
    layer: str,
    z: int,
    x: int,
    y: int,
    response: Response,
    lat: float = Query(...),
    lon: float = Query(...),
    species: str = Query("cerf"),
    month: int = Query(10),
    hour: int = Query(7),
    wind_deg: float = Query(225),
):
    """
    Tile MVT-compatible (GeoJSON filtre) pour layer in {corridors, zones, contamination}.
    Zoom 12-16. Cache 24h. CDN-ready.
    """
    if layer not in _LAYERS_SUPPORTED:
        raise HTTPException(status_code=400, detail=f"Layer '{layer}' non supportee. Autorisees: {_LAYERS_SUPPORTED}")
    if z < _ZOOM_MIN or z > _ZOOM_MAX:
        raise HTTPException(status_code=400, detail=f"Zoom hors plage [{_ZOOM_MIN}-{_ZOOM_MAX}]")

    t0 = time.time()
    tile_key = f"{layer}_{z}_{x}_{y}_{lat:.3f}_{lon:.3f}_{species}_{month}_{hour}_{int(wind_deg/15)*15%360}"
    cached = _cache_get(tile_key)

    if cached is not None:
        response.headers["Cache-Control"] = "public, max-age=86400, immutable"
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Compute-Ms"] = str(round((time.time() - t0) * 1000, 2))
        return cached

    bounds = _tile_bounds(z, x, y)
    bundle = await _get_bundle(lat, lon, species, month, hour, wind_deg)

    features = []
    if layer == "corridors":
        for c in bundle.get("corridors", []):
            path = c.get("path") or [[c.get("start", {}).get("lat"), c.get("start", {}).get("lng")],
                                     [c.get("end", {}).get("lat"), c.get("end", {}).get("lng")]]
            if _path_intersects_bbox(path, bounds):
                # PHASE_XII_SUPRA — SECTION 3.3 : style strict RenduΩ
                # Priorité absolue aux attributs attribués par
                # apply_renduomega_to_bundle (color=#FF8F00, width_px in
                # {1.2, 2.0, 3.0}, opacity ≥ 0.75). Fallback V30 sinon.
                _rom_width = c.get("width_px_renduomega")
                _weight = _rom_width if _rom_width is not None else c.get("weight")
                _color = c.get("color") or "#FF8F00"
                _opacity = c.get("opacity")
                if _opacity is None or _opacity < 0.75:
                    _opacity = 0.75
                _rom_block = c.get("renduomega") or {}
                _rom_accepted = _rom_block.get("accepted") if isinstance(_rom_block, dict) else None
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[p[1], p[0]] for p in path if isinstance(p, (list, tuple)) and len(p) >= 2],
                    },
                    "properties": {
                        "layer": "corridors",
                        "corridor_type": c.get("type", "normal"),
                        "intensity": c.get("intensity"),
                        "color": _color,
                        "weight": _weight,
                        "width_px": _weight,
                        "opacity": _opacity,
                        "species_profile": c.get("species_profile"),
                        "is_network_link": c.get("is_network_link", False),
                        "renduomega_accepted": _rom_accepted,
                        "min_zoom": c.get("min_zoom", 13),
                        "zindex": c.get("zindex", 4),
                    },
                })
    elif layer == "zones":
        for zn in bundle.get("zones", []):
            poly = zn.get("polygon", [])
            if _polygon_intersects_bbox(poly, bounds):
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[p[1], p[0]] for p in poly if isinstance(p, (list, tuple)) and len(p) >= 2]],
                    },
                    "properties": {
                        "layer": "zones",
                        "zone_type": zn.get("type"),
                        "score": zn.get("score"),
                        "terrain": zn.get("terrain", {}),
                        "excluded": zn.get("excluded", False),
                        "exclusion_reason": zn.get("exclusion_reason"),
                    },
                })
    elif layer == "contamination":
        cont = bundle.get("contamination", [])
        cones = cont if isinstance(cont, list) else ([cont] if cont else [])
        for cone in cones:
            poly = cone.get("polygon", [])
            if _polygon_intersects_bbox(poly, bounds):
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[p[1], p[0]] for p in poly if isinstance(p, (list, tuple)) and len(p) >= 2]],
                    },
                    "properties": {
                        "layer": "contamination",
                        "intensity": cone.get("intensity"),
                        "color": cone.get("color"),
                        "opacity": cone.get("opacity"),
                        "fill_opacity": cone.get("fill_opacity"),
                        "reach_m": cone.get("reach_m"),
                        "cone_angle_deg": cone.get("cone_angle_deg"),
                        "affut_source": cone.get("affut_source", {}),
                    },
                })
    elif layer == "salines":
        for s in bundle.get("salines", []):
            lat_s = s.get("lat") or (s.get("center") or {}).get("lat")
            lon_s = s.get("lng") or s.get("lon") or (s.get("center") or {}).get("lng")
            if lat_s is None or lon_s is None:
                continue
            if not _bbox_contains_point(bounds, lat_s, lon_s):
                continue
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon_s, lat_s]},
                "properties": {
                    "layer": "salines",
                    "status": s.get("status"),
                    "score": s.get("score"),
                    "eau_distance_m": s.get("eau_distance_m"),
                    "eau_conforme": s.get("eau_conforme"),
                    "corridor_distance_m": s.get("corridor_distance_m"),
                    "corridor_conforme": s.get("corridor_conforme"),
                    "suggestion": s.get("suggestion"),
                    # V11-SUPRA multi-axe scoring
                    "score_bio_global": s.get("score_bio_global"),
                    "score_bio_species": s.get("score_bio_species"),
                    "score_terrain": s.get("score_terrain"),
                    "score_reseau": s.get("score_reseau"),
                    "score_nutrition": s.get("score_nutrition"),
                    "score_accoutumance": s.get("score_accoutumance"),
                    "score_global_v11": s.get("score_global_v11"),
                    "interdit": s.get("interdit"),
                    "motif_interdiction": s.get("motif_interdiction"),
                    "nutrient_target_profile": s.get("nutrient_target_profile"),
                    "nutrition_analysis_600m": s.get("nutrition_analysis_600m"),
                    "alertes_reseau": s.get("alertes_reseau"),
                    "statut_institutionnel": s.get("statut_institutionnel"),
                    "recommandations": s.get("recommandations"),
                    "source_v11": s.get("source_v11"),
                },
            })
    elif layer == "affuts":
        for a in bundle.get("affuts", []):
            lat_a = a.get("lat")
            lon_a = a.get("lng") or a.get("lon")
            if lat_a is None or lon_a is None:
                continue
            if not _bbox_contains_point(bounds, lat_a, lon_a):
                continue
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon_a, lat_a]},
                "properties": {
                    "layer": "affuts",
                    "type": a.get("type"),
                    "score": a.get("score"),
                    "score_affut_v12": a.get("score_affut_v12"),
                    "score_distance_corridor": a.get("score_distance_corridor"),
                    "distance_corridor_m": a.get("distance_corridor_m"),
                    "classe_corridor_cible": a.get("classe_corridor_cible"),
                    "corridor_type": a.get("corridor_type"),
                    "orientation_deg": a.get("orientation_deg"),
                    "pente_deg": a.get("pente_deg"),
                    "affut_repositionne": a.get("affut_repositionne"),
                    "ancienne_position": a.get("ancienne_position"),
                    "nouvelle_position": a.get("nouvelle_position"),
                    "justification": a.get("justification"),
                    "recommandation": a.get("recommandation"),
                    "quality": a.get("quality"),
                    "source": a.get("source"),
                },
            })
    elif layer == "hotspots":
        for h in bundle.get("hotspots", []):
            lat_h = h.get("lat")
            lon_h = h.get("lng") or h.get("lon")
            if lat_h is None or lon_h is None:
                continue
            if not _bbox_contains_point(bounds, lat_h, lon_h):
                continue
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon_h, lat_h]},
                "properties": {
                    "layer": "hotspots",
                    "intensity": h.get("intensity"),
                    "source_engine": h.get("source_engine"),
                    "source": h.get("source"),
                },
            })
    elif layer == "vent":
        # Vent = segments directionnels (start/end) depuis engine_vent
        for v in bundle.get("wind_vectors", []):
            start = v.get("start") or {}
            end = v.get("end") or {}
            lat_v = start.get("lat")
            lon_v = start.get("lng") or start.get("lon")
            if lat_v is None or lon_v is None:
                continue
            if not _bbox_contains_point(bounds, lat_v, lon_v):
                continue
            lat_e = end.get("lat")
            lon_e = end.get("lng") or end.get("lon")
            if lat_e is not None and lon_e is not None:
                geom = {
                    "type": "LineString",
                    "coordinates": [[lon_v, lat_v], [lon_e, lat_e]],
                }
            else:
                geom = {"type": "Point", "coordinates": [lon_v, lat_v]}
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {
                    "layer": "vent",
                    "id": v.get("id"),
                    "speed_kmh": v.get("speed_kmh"),
                    "direction_deg": v.get("direction_deg"),
                    "decay": v.get("decay"),
                },
            })
    elif layer == "nutrition":
        # Nutrition-V12-SUPRA: grille carences + besoins comme points GeoJSON
        nutri = bundle.get("nutrition") or {}
        carences = nutri.get("carte_carences") or []
        besoins_map = {}
        for b in (nutri.get("carte_besoins") or []):
            besoins_map[(round(b.get("lat", 0), 5), round(b.get("lng", 0), 5))] = b
        for p in carences:
            la, lo = p.get("lat"), p.get("lng")
            if la is None or lo is None:
                continue
            if not _bbox_contains_point(bounds, la, lo):
                continue
            besoin = besoins_map.get((round(la, 5), round(lo, 5))) or {}
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lo, la]},
                "properties": {
                    "layer": "nutrition",
                    "carence_dominante": p.get("carence_dominante"),
                    "severite": p.get("severite"),
                    "severite_tag": p.get("severite_tag"),
                    "deficits": p.get("deficits"),
                    "besoin_dominant": besoin.get("besoin_dominant"),
                    "besoin_intensite": besoin.get("intensite"),
                    "score_nutritionnel_global": nutri.get("score_nutritionnel"),
                    "saison": nutri.get("saison"),
                    "engine": nutri.get("engine"),
                },
            })

    payload = {
        "type": "FeatureCollection",
        "layer": layer,
        "tile": {"z": z, "x": x, "y": y},
        "bounds": {"min_lon": bounds[0], "min_lat": bounds[1], "max_lon": bounds[2], "max_lat": bounds[3]},
        "count": len(features),
        "features": features,
    }

    _cache_set(tile_key, payload)
    response.headers["Cache-Control"] = "public, max-age=86400, immutable"
    response.headers["X-Cache"] = "MISS"
    response.headers["X-Compute-Ms"] = str(round((time.time() - t0) * 1000, 2))
    return payload


@router.get("/stats")
async def v20_tiles_stats():
    return {
        "tile_cache_size": len(_TILE_CACHE),
        "tile_cache_max": _TILE_MAX,
        "tile_cache_ttl_sec": _TILE_TTL,
        "layers_supported": sorted(_LAYERS_SUPPORTED),
        "zoom_range": [_ZOOM_MIN, _ZOOM_MAX],
    }


@router.post("/purge")
async def v20_tiles_purge():
    """PHASE_XII_SUPRA_PURGE_TERRITOIRE_MVT_Ω — Section 1.2.

    Purge TOTALE du cache MVT tiles LRU. Les tuiles seront re-générées
    au prochain fetch via le pipeline RenduΩ obligatoire (_get_bundle
    patché pour appliquer apply_renduomega_to_bundle).
    """
    cleared = len(_TILE_CACHE)
    _TILE_CACHE.clear()
    return {
        "phase": "XII_SUPRA_PURGE_TERRITOIRE_MVT_Ω",
        "section": "1.2",
        "tiles_cache_cleared": cleared,
        "layers_supported": sorted(_LAYERS_SUPPORTED),
        "rebuild_mode": "renduomega_only",
        "ok": True,
    }
