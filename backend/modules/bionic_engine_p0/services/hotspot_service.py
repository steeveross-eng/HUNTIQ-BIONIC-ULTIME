"""
BIONIC ENGINE - Hotspot Service V6
PHASE P1-HOTSPOTS — MISE A NIVEAU V6 (Cercles 600m + Exclusion V7)

Service de generation des hotspots cartographiques.
Geometrie: Cercles parfaits 600m (directive STEEVE-MAX).
Exclusion V7: Cache local 41,944 polygones eau (ZERO API temps reel).
Triple verification: point-check V5 + cache local V7 + Overpass fallback.

SPECIFICATIONS OBLIGATOIRES:
- Geometrie: CERCLES 600m (ZERO carre, ZERO polygone irregulier)
- Exclusion V7 via cache local (ZERO requete viewport-complet)
- Triple verification eau: point V5 + polygon V7 local + Overpass fallback
- Alignement comportemental par espece

Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x100
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
import logging

from modules.bionic_engine_p0.modules.predictive_territorial import PredictiveTerritorialService
from modules.bionic_engine_p0.modules.behavioral_models import BehavioralModelsService
from modules.bionic_engine_p0.contracts.data_contracts import Species

# Import du nouveau générateur ORGANIQUE
from modules.bionic_engine_p0.services.organic_contour_generator import (
    OrganicContourGenerator,
    create_hotspot_style,
    generate_id,
    calculate_polygon_area_m2,
    MIN_AREA_M2,
    MAX_AREA_M2
)

# Import du cache OSM
try:
    from modules.bionic_engine_p0.services.osm_cache_service import get_osm_cache
except ImportError:
    get_osm_cache = None

# Import Exclusion Engine V7 pour filtrage geometrique
try:
    from shapely.geometry import Polygon as ShapelyPolygon, MultiPolygon
    from shapely.ops import unary_union
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

logger = logging.getLogger("bionic_engine.hotspot_service")


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class BoundsInput(BaseModel):
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)


class UserWaypoint(BaseModel):
    id: str
    latitude: float
    longitude: float


class HotspotRequest(BaseModel):
    bounds: BoundsInput
    species: List[str] = ["moose"]
    time_range: str = "24h"
    hotspot_types: List[str] = ["activity_peak", "feeding_zone", "rut_zone"]
    datetime_start: Optional[str] = None
    min_score_threshold: int = 70
    include_waypoints: bool = False
    user_waypoints: List[UserWaypoint] = []


class HotspotStyle(BaseModel):
    stroke_color: str
    stroke_width: float = 1.5
    fill_opacity: float = 0  # TOUJOURS 0


class TimeValidity(BaseModel):
    start: str
    end: str
    optimal_hours: List[int] = []


class HotspotMetadata(BaseModel):
    source_factor: str
    factor_score: float
    dominant_behavior: str
    generated_at: str


class Hotspot(BaseModel):
    id: str
    type: str
    geometry: Dict[str, Any]
    score: float
    confidence: float
    time_validity: TimeValidity
    species: List[str]
    style: HotspotStyle
    metadata: HotspotMetadata


class HotspotStatistics(BaseModel):
    total_hotspots: int
    by_type: Dict[str, int]
    avg_score: float
    coverage_km2: float


class HotspotResponse(BaseModel):
    success: bool
    hotspots: List[Hotspot]
    statistics: HotspotStatistics
    metadata: Dict[str, Any]


# =============================================================================
# HOTSPOT SERVICE
# =============================================================================

class HotspotService:
    """
    Service de generation de hotspots ORGANIQUES V6.
    
    MISE A NIVEAU V6 — Exclusion Geometrique V7 (Shapely).
    
    SPECIFICATIONS GOLDEN V6.x:
    - Formes 100% ORGANIQUES (ZERO cercle)
    - Superficie: 5000-10000 m2
    - Exclusion GEOMETRIQUE V7: polygones vs eau/routes/urbain
    - Alignement comportemental par espece
    - Contours 1-2px, centre transparent
    - ZERO fill, ZERO effets
    - BCE-4X / STEEVE-MAX conforme
    """
    
    # Taille de tuile pour le cache eau V7 (0.05° ~ 5.5km)
    TILE_SIZE_DEG = 0.05
    # Seuil d'overlap eau pour exclusion (15%)
    WATER_OVERLAP_THRESHOLD = 0.15
    # Rayon de generation V6.x: 600m cercle parfait (directive STEEVE-MAX)
    GENERATION_RADIUS_M = 600
    CIRCLE_NUM_POINTS = 48

    def __init__(self):
        self._pt_service = PredictiveTerritorialService()
        self._bm_service = BehavioralModelsService()
        self._organic_gen = OrganicContourGenerator()
        self._osm_cache = get_osm_cache() if get_osm_cache else None
        self._water_tile_cache: Dict[str, list] = {}
        self._local_water_union = None
        self._local_water_loaded = False
        self._v7_exclusion_stats = {"tiles_fetched": 0, "hotspots_excluded": 0, "local_cache_used": False}
        # Charger les polygones eau depuis le cache local OSM
        self._load_local_water_cache()

    def _load_local_water_cache(self):
        """
        V7 — Charge les polygones eau depuis les fichiers cache OSM locaux.
        ZERO dependance API externe. Donnees pre-calculees ~400Mo.
        """
        import os
        import json
        from pathlib import Path

        cache_dir = Path("/app/backend/data/osm_cache")
        if not cache_dir.exists():
            logger.warning("[V7-LOCAL] Repertoire cache OSM non trouve")
            return

        if not SHAPELY_AVAILABLE:
            return

        water_polys = []
        files_scanned = 0

        for fname in os.listdir(cache_dir):
            if not fname.endswith(".json") or fname.startswith("CA-") or fname == "hydro_debug.json":
                continue
            fpath = cache_dir / fname
            if fpath.stat().st_size < 10000:  # Skip small files
                continue
            try:
                with open(fpath) as f:
                    data = json.load(f)
                zones = data.get("exclusion_zones", [])
                for zone in zones:
                    if zone.get("type") != "water":
                        continue
                    coords = zone.get("coordinates", [])
                    if len(coords) >= 4:
                        try:
                            poly = ShapelyPolygon([(c[0], c[1]) for c in coords])
                            if poly.is_valid and poly.area > 0:
                                water_polys.append(poly)
                        except Exception:
                            pass
                files_scanned += 1
            except Exception:
                continue

        if water_polys:
            try:
                self._local_water_union = unary_union(water_polys)
                self._local_water_loaded = True
                logger.info(
                    f"[V7-LOCAL] Cache eau local charge: {len(water_polys)} polygones "
                    f"depuis {files_scanned} fichiers"
                )
            except Exception as e:
                logger.warning(f"[V7-LOCAL] Erreur union eau: {e}")
        else:
            logger.warning("[V7-LOCAL] Aucun polygone eau dans le cache local")

    def _tile_key(self, lat: float, lng: float) -> str:
        """Calcule la cle de tuile 0.05° pour un point."""
        tile_lat = round(lat / self.TILE_SIZE_DEG) * self.TILE_SIZE_DEG
        tile_lng = round(lng / self.TILE_SIZE_DEG) * self.TILE_SIZE_DEG
        return f"{tile_lat:.3f},{tile_lng:.3f}"

    def _tile_bounds(self, tile_key: str) -> tuple:
        """Retourne (south, west, north, east) pour une tuile."""
        parts = tile_key.split(",")
        center_lat = float(parts[0])
        center_lng = float(parts[1])
        half = self.TILE_SIZE_DEG / 2
        return (
            center_lat - half,
            center_lng - half,
            center_lat + half,
            center_lng + half,
        )

    def _fetch_water_for_tile(self, tile_key: str) -> list:
        """
        V7 — Requete Overpass LOCALISEE par tuile (FALLBACK uniquement).
        Utilise en dernier recours si le cache local est vide.
        """
        if tile_key in self._water_tile_cache:
            return self._water_tile_cache[tile_key]

        if not SHAPELY_AVAILABLE:
            self._water_tile_cache[tile_key] = []
            return []

        south, west, north, east = self._tile_bounds(tile_key)

        query = f"""[out:json][timeout:15];
(way["natural"="water"]({south},{west},{north},{east});
 relation["natural"="water"]({south},{west},{north},{east});
 way["waterway"="riverbank"]({south},{west},{north},{east});
 way["water"="lake"]({south},{west},{north},{east});
 way["water"="river"]({south},{west},{north},{east});
 way["water"="reservoir"]({south},{west},{north},{east}););
out body;>;out skel qt;"""

        overpass_servers = [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
        ]

        water_polys = []
        import httpx
        import time as _time

        for server_url in overpass_servers:
            for attempt in range(2):
                try:
                    if attempt > 0:
                        _time.sleep(1.5)
                    with httpx.Client(timeout=20) as client:
                        resp = client.post(server_url, data={"data": query})
                        if resp.status_code == 200:
                            data = resp.json()
                            nodes = {}
                            for el in data.get("elements", []):
                                if el["type"] == "node":
                                    nodes[el["id"]] = (el["lon"], el["lat"])
                            for el in data.get("elements", []):
                                if el["type"] == "way" and "nodes" in el:
                                    coords = [nodes[n] for n in el["nodes"] if n in nodes]
                                    if len(coords) >= 4:
                                        try:
                                            poly = ShapelyPolygon(coords)
                                            if poly.is_valid and poly.area > 0:
                                                water_polys.append(poly)
                                        except Exception:
                                            pass
                            self._water_tile_cache[tile_key] = water_polys
                            self._v7_exclusion_stats["tiles_fetched"] += 1
                            return water_polys
                        elif resp.status_code == 429:
                            _time.sleep(2)
                            continue
                        elif resp.status_code == 504:
                            break
                except Exception:
                    break

        self._water_tile_cache[tile_key] = water_polys
        self._v7_exclusion_stats["tiles_fetched"] += 1
        return water_polys

    def _check_hotspot_water_v7(self, coords: list, center_lat: float, center_lng: float) -> bool:
        """
        V7 — Triple verification eau pour un hotspot:
          1. Point-check V5 via OSM cache (instantane)
          2. Polygon-check V7 via cache local 400Mo (geometrique, ZERO API)
          3. Fallback: Overpass localisee par tuile (si cache local absent)

        Retourne True si le hotspot doit etre EXCLU (sur eau).
        """
        # === CHECK 1: Point V5 (OSM cache, instantane) ===
        if self._osm_cache:
            is_excluded, exclusion_type = self._osm_cache.is_point_excluded(
                center_lat, center_lng
            )
            if is_excluded and exclusion_type == "water":
                logger.debug(f"[V7-EXCL] Point {center_lat:.4f},{center_lng:.4f} exclu V5 (eau)")
                self._v7_exclusion_stats["hotspots_excluded"] += 1
                return True

        if not SHAPELY_AVAILABLE:
            return False

        try:
            # coords est en format GeoJSON [lng, lat]
            hotspot_poly = ShapelyPolygon(coords)
            if not hotspot_poly.is_valid:
                hotspot_poly = hotspot_poly.buffer(0)
            if hotspot_poly.is_empty or hotspot_poly.area <= 0:
                return False
        except Exception:
            return False

        # === CHECK 2: Cache local eau (PRIMAIRE, ZERO API) ===
        if self._local_water_loaded and self._local_water_union is not None:
            try:
                overlap = hotspot_poly.intersection(self._local_water_union).area
                overlap_ratio = overlap / hotspot_poly.area if hotspot_poly.area > 0 else 0

                if overlap_ratio > self.WATER_OVERLAP_THRESHOLD:
                    logger.info(
                        f"[V7-LOCAL] Hotspot {center_lat:.4f},{center_lng:.4f} exclu: "
                        f"{overlap_ratio:.1%} chevauchement eau"
                    )
                    self._v7_exclusion_stats["hotspots_excluded"] += 1
                    self._v7_exclusion_stats["local_cache_used"] = True
                    return True
                # Cache local dit pas d'eau => VALIDE
                self._v7_exclusion_stats["local_cache_used"] = True
                return False
            except Exception as e:
                logger.warning(f"[V7-LOCAL] Erreur check local: {e}")

        # === CHECK 3: Fallback Overpass (si cache local absent) ===
        tile_key = self._tile_key(center_lat, center_lng)
        water_polys = self._fetch_water_for_tile(tile_key)

        if not water_polys:
            return False

        try:
            water_union = unary_union(water_polys)
            overlap = hotspot_poly.intersection(water_union).area
            overlap_ratio = overlap / hotspot_poly.area

            if overlap_ratio > self.WATER_OVERLAP_THRESHOLD:
                logger.info(
                    f"[V7-EXCL] Hotspot {center_lat:.4f},{center_lng:.4f} exclu: "
                    f"{overlap_ratio:.1%} chevauchement eau (Overpass fallback)"
                )
                self._v7_exclusion_stats["hotspots_excluded"] += 1
                return True
        except Exception as e:
            logger.warning(f"[V7-EXCL] Erreur check geometrique: {e}")

        return False

    def _generate_circle_coords(self, center_lat: float, center_lng: float, radius_m: float) -> list:
        """Genere les coordonnees d'un cercle parfait en [lng, lat] format GeoJSON."""
        import math
        coords = []
        for i in range(self.CIRCLE_NUM_POINTS):
            angle = 2 * math.pi * i / self.CIRCLE_NUM_POINTS
            dlat = (radius_m * math.cos(angle)) / 111320.0
            dlng = (radius_m * math.sin(angle)) / (111320.0 * math.cos(math.radians(center_lat)))
            coords.append([center_lng + dlng, center_lat + dlat])
        coords.append(coords[0])  # Fermer le cercle
        return coords

    def generate_hotspots(self, request: HotspotRequest) -> HotspotResponse:
        """
        Genere les hotspots pour une zone et periode.
        GOLDEN V6.x: Exclusion geometrique V7 appliquee.
        """
        start_time = datetime.now(timezone.utc)
        
        # V7: Reset des stats d'exclusion par requete
        self._v7_exclusion_stats = {"tiles_fetched": 0, "hotspots_excluded": 0, "local_cache_used": self._local_water_loaded}
        
        # Parser datetime
        if request.datetime_start:
            base_datetime = datetime.fromisoformat(request.datetime_start.replace('Z', '+00:00'))
        else:
            base_datetime = datetime.now(timezone.utc)
        
        # Calculer la fin selon time_range
        time_range_hours = {"24h": 24, "72h": 72, "7d": 168}
        hours = time_range_hours.get(request.time_range, 24)
        end_datetime = base_datetime + timedelta(hours=hours)
        
        hotspots = []
        
        # Calculer la taille de la zone en km
        lat_range_km = (request.bounds.north - request.bounds.south) * 111
        lng_range_km = (request.bounds.east - request.bounds.west) * 111 * abs(math.cos(math.radians((request.bounds.north + request.bounds.south) / 2)))
        area_km2 = lat_range_km * lng_range_km
        
        # Adapter la résolution à la taille de la zone (max 16 points pour performance)
        if area_km2 > 100:
            resolution = 3  # 9 points pour grandes zones
        elif area_km2 > 25:
            resolution = 4  # 16 points
        else:
            resolution = 5  # 25 points pour petites zones
        
        grid_points = self._generate_grid(request.bounds, resolution=resolution)
        
        # Pour chaque espece demandee
        for species_str in request.species:
            try:
                species = Species(species_str)
            except ValueError:
                continue
            
            # Pour chaque point de la grille
            for lat, lng in grid_points:
                # Calculer le score P0
                score_result = self._pt_service.calculate_score(
                    latitude=lat,
                    longitude=lng,
                    species=species,
                    datetime_target=base_datetime,
                    include_advanced_factors=True
                )
                
                if not score_result.success:
                    continue
                
                # Extraire les facteurs avances
                advanced_factors = score_result.metadata.get("advanced_factors", {})
                factor_scores = score_result.metadata.get("advanced_factor_scores", {})
                
                # Generer hotspots selon les types demandes
                for hotspot_type in request.hotspot_types:
                    hotspot = self._create_hotspot_from_factors(
                        hotspot_type=hotspot_type,
                        lat=lat,
                        lng=lng,
                        species=species_str,
                        score_result=score_result,
                        advanced_factors=advanced_factors,
                        factor_scores=factor_scores,
                        base_datetime=base_datetime,
                        end_datetime=end_datetime,
                        min_threshold=request.min_score_threshold
                    )
                    
                    if hotspot:
                        hotspots.append(hotspot)
        
        # Ajouter hotspots personnalises par waypoints utilisateur
        if request.include_waypoints and request.user_waypoints:
            for wp in request.user_waypoints:
                for species_str in request.species:
                    try:
                        species = Species(species_str)
                        wp_hotspot = self._create_waypoint_hotspot(
                            waypoint=wp,
                            species=species,
                            base_datetime=base_datetime,
                            end_datetime=end_datetime
                        )
                        if wp_hotspot:
                            hotspots.append(wp_hotspot)
                    except ValueError:
                        continue
        
        # Calculer statistiques
        by_type = {}
        total_score = 0
        for hs in hotspots:
            by_type[hs.type] = by_type.get(hs.type, 0) + 1
            total_score += hs.score
        
        avg_score = total_score / len(hotspots) if hotspots else 0
        
        # Estimation couverture
        coverage_km2 = self._estimate_coverage(request.bounds)
        
        calc_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return HotspotResponse(
            success=True,
            hotspots=hotspots,
            statistics=HotspotStatistics(
                total_hotspots=len(hotspots),
                by_type=by_type,
                avg_score=round(avg_score, 1),
                coverage_km2=round(coverage_km2, 2)
            ),
            metadata={
                "calculation_time_ms": round(calc_time, 1),
                "grid_resolution": resolution,
                "geometry": "circle_600m",
                "version": "GOLDEN-V6-HOTSPOTS-3.0",
                "exclusion_engine": "V7-local-cache" if self._local_water_loaded else ("V7-tile-localized" if SHAPELY_AVAILABLE else "V5-point"),
                "v7_hotspots_excluded": self._v7_exclusion_stats["hotspots_excluded"],
                "v7_local_cache_active": self._local_water_loaded,
                "generation_radius_m": self.GENERATION_RADIUS_M,
                "circle_num_points": self.CIRCLE_NUM_POINTS
            }
        )
    
    def _generate_grid(
        self,
        bounds: BoundsInput,
        resolution: int = 8
    ) -> List[tuple]:
        """Genere une grille de points dans les bounds."""
        points = []
        lat_step = (bounds.north - bounds.south) / resolution
        lng_step = (bounds.east - bounds.west) / resolution
        
        for i in range(resolution):
            for j in range(resolution):
                lat = bounds.south + (i + 0.5) * lat_step
                lng = bounds.west + (j + 0.5) * lng_step
                points.append((lat, lng))
        
        return points
    
    def _create_hotspot_from_factors(
        self,
        hotspot_type: str,
        lat: float,
        lng: float,
        species: str,
        score_result: Any,
        advanced_factors: Dict,
        factor_scores: Dict,
        base_datetime: datetime,
        end_datetime: datetime,
        min_threshold: int
    ) -> Optional[Hotspot]:
        """
        Cree un hotspot ORGANIQUE si le facteur depasse le seuil.
        
        REFONTE V3: Utilise OrganicContourGenerator pour formes naturelles.
        """
        
        # Mapper type de hotspot vers facteur P0
        type_to_factor = {
            "activity_peak": ("overall", score_result.overall_score),
            "feeding_zone": ("digestive", factor_scores.get("digestive", 0)),
            "rut_zone": ("hormonal", factor_scores.get("hormonal", 0)),
            "thermal_refuge": ("thermal_stress", 100 - factor_scores.get("thermal_stress", 0)),
            "water_source": ("hydric_stress", 100 - factor_scores.get("hydric_stress", 0)),
            "predation_risk": ("predation", factor_scores.get("predation", 0)),
            "snow_impact": ("snow", factor_scores.get("snow", 0)),
            "human_avoidance": ("human_disturbance", 100 - factor_scores.get("human_disturbance", 0)),
            "mineral_site": ("mineral", factor_scores.get("mineral", 0)),
            "composite_optimal": ("overall", score_result.overall_score)
        }
        
        factor_name, score = type_to_factor.get(hotspot_type, ("overall", 0))
        
        if score < min_threshold:
            return None
        
        # Vérifier évitement OSM AVANT génération (point check V5 - maintenu)
        if self._osm_cache:
            is_excluded, exclusion_type = self._osm_cache.is_point_excluded(lat, lng)
            if is_excluded:
                logger.debug(f"[V5] Point {lat},{lng} exclu: {exclusion_type}")
                return None
        
        # Determiner heures optimales
        optimal_hours = []
        if hotspot_type in ["activity_peak", "feeding_zone"]:
            optimal_hours = [6, 7, 8, 17, 18, 19]
        elif hotspot_type == "rut_zone":
            optimal_hours = [5, 6, 7, 8, 16, 17, 18, 19]
        
        # Comportement dominant
        dominant_behavior = "normal"
        hormonal = advanced_factors.get("hormonal", {})
        if hormonal.get("phase") == "rut_peak":
            dominant_behavior = "rut_seeking"
        elif advanced_factors.get("digestive", {}).get("phase") == "active_feeding":
            dominant_behavior = "feeding"
        
        # V6: Generer CERCLE PARFAIT 600m (directive STEEVE-MAX)
        coords = self._generate_circle_coords(lat, lng, self.GENERATION_RADIUS_M)
        
        if coords is None or len(coords) < 4:
            return None
        
        # === EXCLUSION V7: Triple verification eau ===
        if self._check_hotspot_water_v7(coords, lat, lng):
            logger.info(f"[V7-EXCL] Hotspot {hotspot_type} at {lat:.4f},{lng:.4f} exclu (eau V7)")
            return None
        
        geometry = {
            "type": "Polygon",
            "coordinates": [coords]
        }
        
        return Hotspot(
            id=generate_id("HS"),
            type=hotspot_type,
            geometry=geometry,
            score=round(score, 1),
            confidence=round(score_result.confidence, 2),
            time_validity=TimeValidity(
                start=base_datetime.isoformat(),
                end=end_datetime.isoformat(),
                optimal_hours=optimal_hours
            ),
            species=[species],
            style=HotspotStyle(**create_hotspot_style(hotspot_type, species)),
            metadata=HotspotMetadata(
                source_factor=factor_name,
                factor_score=round(score, 1),
                dominant_behavior=dominant_behavior,
                generated_at=datetime.now(timezone.utc).isoformat()
            )
        )
    
    def _create_waypoint_hotspot(
        self,
        waypoint: UserWaypoint,
        species: Species,
        base_datetime: datetime,
        end_datetime: datetime
    ) -> Optional[Hotspot]:
        """Cree un hotspot personnalise autour d'un waypoint utilisateur."""
        
        score_result = self._pt_service.calculate_score(
            latitude=waypoint.latitude,
            longitude=waypoint.longitude,
            species=species,
            datetime_target=base_datetime,
            include_advanced_factors=True
        )
        
        if not score_result.success or score_result.overall_score < 50:
            return None
        
        # Vérifier évitement OSM AVANT génération
        if self._osm_cache:
            is_excluded, exclusion_type = self._osm_cache.is_point_excluded(
                waypoint.latitude, waypoint.longitude
            )
            if is_excluded:
                logger.debug(f"Waypoint {waypoint.id} exclu: {exclusion_type}")
                return None
        
        # V6: Generer CERCLE PARFAIT 600m autour du waypoint
        coords = self._generate_circle_coords(
            waypoint.latitude, waypoint.longitude, self.GENERATION_RADIUS_M
        )
        
        if coords is None or len(coords) < 4:
            return None
        
        # === EXCLUSION V7: Triple verification eau pour waypoint ===
        if self._check_hotspot_water_v7(coords, waypoint.latitude, waypoint.longitude):
            logger.info(f"[V7-EXCL] Waypoint {waypoint.id} exclu (eau V7)")
            return None
        
        geometry = {
            "type": "Polygon",
            "coordinates": [coords]
        }
        
        return Hotspot(
            id=generate_id("HS"),
            type="composite_optimal",
            geometry=geometry,
            score=round(score_result.overall_score, 1),
            confidence=round(score_result.confidence, 2),
            time_validity=TimeValidity(
                start=base_datetime.isoformat(),
                end=end_datetime.isoformat(),
                optimal_hours=[6, 7, 8, 17, 18, 19]
            ),
            species=[species.value],
            style=HotspotStyle(**create_hotspot_style("composite_optimal", species.value)),
            metadata=HotspotMetadata(
                source_factor="user_waypoint",
                factor_score=round(score_result.overall_score, 1),
                dominant_behavior="custom",
                generated_at=datetime.now(timezone.utc).isoformat()
            )
        )
    
    def _estimate_coverage(self, bounds: BoundsInput) -> float:
        """Estime la couverture en km2."""
        lat_diff = bounds.north - bounds.south
        lng_diff = bounds.east - bounds.west
        
        # Approximation: 1 degre lat ~ 111km, 1 degre lng ~ 111km * cos(lat)
        avg_lat = (bounds.north + bounds.south) / 2
        lat_km = lat_diff * 111
        lng_km = lng_diff * 111 * abs(math.cos(math.radians(avg_lat)))
        
        return lat_km * lng_km


import math
