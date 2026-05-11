"""V20_3D_OVERLAYS_Ω — CARTE_3D_INTEGRATION_SOUS_HEADER_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · FUSION ADD-ONLY · V30_LOCK
ANTI-GÉNÉRIQUE_Ω STRICT : aucune donnée mockée.

4 endpoints pour alimenter le viewer Cesium 3D :
  GET /api/v20/corridors/active        → corridors actifs (du bundle V20)
  GET /api/v20/zones/active            → zones vitales actives (du bundle V20)
  GET /api/v20/territoire/buffer-600m  → buffer géodésique 600 m (centré waypoint)
  GET /api/v20/points-interet/active   → affûts + salines (du bundle V20)

Tous ces endpoints réutilisent `v20_territoire_bundle` (cache LRU + disque) :
zéro recalcul lourd, zéro mock.
"""

from __future__ import annotations

import math
import time
from typing import Any, List

from fastapi import APIRouter, HTTPException, Query, Response

router = APIRouter(prefix="/api/v20", tags=["V20_3D_OVERLAYS_Ω"])


# ───────────────────────── HELPERS GÉODÉSIQUES ──────────────────────────

_EARTH_RADIUS_M = 6371000.0


def _geodesic_buffer_circle(
    lat: float, lon: float, radius_m: float, n_points: int = 64
) -> list[list[float]]:
    """Génère un polygone GeoJSON (fermé) circulaire géodésique autour de (lat,lon).

    Retourne une liste de [lon, lat] (convention GeoJSON, fermée).
    """
    coords: list[list[float]] = []
    lat_rad = math.radians(lat)
    ang_dist = radius_m / _EARTH_RADIUS_M  # rad
    for i in range(n_points):
        bearing = 2.0 * math.pi * i / n_points
        sin_lat2 = (
            math.sin(lat_rad) * math.cos(ang_dist)
            + math.cos(lat_rad) * math.sin(ang_dist) * math.cos(bearing)
        )
        lat2 = math.asin(sin_lat2)
        lon2 = math.radians(lon) + math.atan2(
            math.sin(bearing) * math.sin(ang_dist) * math.cos(lat_rad),
            math.cos(ang_dist) - math.sin(lat_rad) * sin_lat2,
        )
        coords.append([math.degrees(lon2), math.degrees(lat2)])
    coords.append(coords[0])  # GeoJSON polygon: fermé
    return coords


async def _fetch_bundle(
    lat: float,
    lon: float,
    species: str,
    month: int,
    hour: int,
    wind_deg: float,
    wind_speed: float,
) -> dict[str, Any]:
    """Récupère le bundle V20 (cache LRU + recalcul si miss). Anti-générique."""
    try:
        from engines.v8_institutional.v20_performance_bundle import (
            v20_territoire_bundle,
        )
        # Un Response factice pour satisfaire la signature
        resp = Response()
        bundle = await v20_territoire_bundle(
            response=resp,
            lat=lat,
            lon=lon,
            species=species,
            month=month,
            hour=hour,
            wind_deg=wind_deg,
            wind_speed=wind_speed,
        )
        return bundle
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"V20_BUNDLE_FETCH_FAILED · ANTI-GÉNÉRIQUE strict : {e}",
        )


# ─────────────────────────── ENDPOINTS ──────────────────────────────────


@router.get("/corridors/active")
async def corridors_active(
    lat: float = Query(...),
    lon: float = Query(...),
    species: str = Query("orignal"),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(7, ge=0, le=23),
    wind_deg: float = Query(225.0),
    wind_speed: float = Query(15.0),
) -> dict[str, Any]:
    """Corridors écologiques ACTIFS du bundle V20 (réels, validés RenduΩ)."""
    t0 = time.time()
    bundle = await _fetch_bundle(lat, lon, species, month, hour, wind_deg, wind_speed)
    corridors: List[dict[str, Any]] = bundle.get("corridors") or []
    return {
        "ok": True,
        "engine": "V20_3D_OVERLAYS_Ω",
        "source": "v20_territoire_bundle",
        "anti_generique_strict": True,
        "n_corridors": len(corridors),
        "corridors": corridors,
        "waypoint": {"lat": lat, "lng": lon},
        "species": species,
        "served_ms": round((time.time() - t0) * 1000, 2),
        "bundle_cache": bundle.get("cache"),
    }


@router.get("/zones/active")
async def zones_active(
    lat: float = Query(...),
    lon: float = Query(...),
    species: str = Query("orignal"),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(7, ge=0, le=23),
    wind_deg: float = Query(225.0),
    wind_speed: float = Query(15.0),
) -> dict[str, Any]:
    """Zones vitales ACTIVES du bundle V20 (alimentation/rut/repos/eau/...)."""
    t0 = time.time()
    bundle = await _fetch_bundle(lat, lon, species, month, hour, wind_deg, wind_speed)
    zones: List[dict[str, Any]] = bundle.get("zones") or []
    return {
        "ok": True,
        "engine": "V20_3D_OVERLAYS_Ω",
        "source": "v20_territoire_bundle",
        "anti_generique_strict": True,
        "n_zones": len(zones),
        "zones": zones,
        "waypoint": {"lat": lat, "lng": lon},
        "species": species,
        "served_ms": round((time.time() - t0) * 1000, 2),
        "bundle_cache": bundle.get("cache"),
    }


@router.get("/territoire/buffer-600m")
async def territoire_buffer_600m(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_m: float = Query(600.0, ge=50.0, le=5000.0),
    n_points: int = Query(64, ge=12, le=256),
) -> dict[str, Any]:
    """Buffer géodésique centré sur le waypoint actif.

    Default : 600 m (rayon de visibilité Cesium imposé par CARTE_3D_INTEGRATION).
    Sortie : GeoJSON Polygon (coordonnées [lon, lat] fermées).
    """
    t0 = time.time()
    ring = _geodesic_buffer_circle(lat, lon, radius_m, n_points)
    feature = {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [ring]},
        "properties": {
            "center": {"lat": lat, "lng": lon},
            "radius_m": radius_m,
            "n_points": n_points,
            "engine": "V20_3D_OVERLAYS_Ω",
        },
    }
    return {
        "ok": True,
        "engine": "V20_3D_OVERLAYS_Ω",
        "anti_generique_strict": True,
        "feature": feature,
        "served_ms": round((time.time() - t0) * 1000, 2),
    }


@router.get("/points-interet/active")
async def points_interet_active(
    lat: float = Query(...),
    lon: float = Query(...),
    species: str = Query("orignal"),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(7, ge=0, le=23),
    wind_deg: float = Query(225.0),
    wind_speed: float = Query(15.0),
) -> dict[str, Any]:
    """Points d'intérêt ACTIFS : affûts + salines (réels) du bundle V20."""
    t0 = time.time()
    bundle = await _fetch_bundle(lat, lon, species, month, hour, wind_deg, wind_speed)
    affuts: List[dict[str, Any]] = bundle.get("affuts") or []
    salines: List[dict[str, Any]] = bundle.get("salines") or []

    # Normalisation : un seul tableau "points_interet" avec catégorie
    poi: list[dict[str, Any]] = []
    for a in affuts:
        if not isinstance(a, dict):
            continue
        _lat = a.get("lat")
        _lng = a.get("lng") or a.get("lon")
        if _lat is None or _lng is None:
            continue
        poi.append({
            "lat": float(_lat),
            "lng": float(_lng),
            "category": "affut",
            "score": a.get("score"),
            "type_key": a.get("type_key"),
            "id": a.get("id"),
            "source": a.get("source") or "V20_BUNDLE_AFFUT",
        })
    for s in salines:
        if not isinstance(s, dict):
            continue
        _lat = s.get("lat")
        _lng = s.get("lng") or s.get("lon")
        if _lat is None or _lng is None:
            continue
        poi.append({
            "lat": float(_lat),
            "lng": float(_lng),
            "category": "saline",
            "score": s.get("score"),
            "type_key": s.get("type") or "saline",
            "id": s.get("id"),
            "source": s.get("source") or "V20_BUNDLE_SALINE",
        })

    return {
        "ok": True,
        "engine": "V20_3D_OVERLAYS_Ω",
        "source": "v20_territoire_bundle",
        "anti_generique_strict": True,
        "n_points_interet": len(poi),
        "n_affuts": sum(1 for p in poi if p["category"] == "affut"),
        "n_salines": sum(1 for p in poi if p["category"] == "saline"),
        "points_interet": poi,
        "waypoint": {"lat": lat, "lng": lon},
        "species": species,
        "served_ms": round((time.time() - t0) * 1000, 2),
        "bundle_cache": bundle.get("cache"),
    }
