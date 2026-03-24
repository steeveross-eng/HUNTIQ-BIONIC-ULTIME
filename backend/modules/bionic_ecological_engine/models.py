"""
BIONIC Ecological Intelligence Engine — Models
STEEVE-MAX x2000 / Phase A

Modeles Pydantic pour le moteur ecologique unifie.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class AnalysisScale(str, Enum):
    MICRO = "micro"       # 100m radius
    ZONE = "zone"         # 600m radius
    SECTOR = "sector"     # 2km radius
    TERRITORY = "territory"  # full territory
    REGIONAL = "regional"    # multi-territory


class SpeciesType(str, Enum):
    """Toutes les especes integrees dans BIONIC — STEEVE-MAX x2250"""
    ORIGNAL = "orignal"
    CERF_VIRGINIE = "cerf_virginie"
    OURS_NOIR = "ours_noir"
    DINDON_SAUVAGE = "dindon_sauvage"
    CARIBOU = "caribou"
    WAPITI = "wapiti"
    CERF_MULET = "cerf_mulet"
    PRONGHORN = "pronghorn"


class EcologicalQueryRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    radius_m: int = Field(600, ge=100, le=50000)
    species: Optional[SpeciesType] = None
    scale: AnalysisScale = AnalysisScale.ZONE
    include_soil: bool = True
    include_hydrology: bool = True
    include_vegetation: bool = True
    include_weather: bool = True
    include_solunar: bool = True
    include_pressure: bool = True
    include_predictions: bool = True
    include_scoring: bool = True


class SoilProfile(BaseModel):
    ph: float = 0.0
    nitrogen_ppm: float = 0.0
    phosphorus_ppm: float = 0.0
    potassium_ppm: float = 0.0
    calcium_ppm: float = 0.0
    magnesium_ppm: float = 0.0
    sodium_ppm: float = 0.0
    organic_matter_pct: float = 0.0
    texture: str = "loam"
    moisture_pct: float = 0.0
    quality_score: float = 0.0


class HydrologyProfile(BaseModel):
    water_sources_count: int = 0
    nearest_water_m: float = 0.0
    drainage_class: str = "moderate"
    leaching_risk: str = "low"
    seasonal_variation: str = "stable"
    quality_score: float = 0.0


class VegetationProfile(BaseModel):
    dominant_type: str = "mixed_forest"
    canopy_cover_pct: float = 0.0
    understory_density: str = "moderate"
    forage_quality: float = 0.0
    browse_availability: float = 0.0
    mast_production: str = "moderate"
    edge_habitat_m: float = 0.0
    quality_score: float = 0.0


class MineralProfile(BaseModel):
    natural_salt_deposits: bool = False
    mineral_licks_nearby: int = 0
    saline_stations_count: int = 0
    deficiency_risk: Dict[str, str] = {}
    supplementation_priority: str = "none"


class WeatherSnapshot(BaseModel):
    temperature_c: float = 0.0
    humidity_pct: float = 0.0
    wind_speed_kmh: float = 0.0
    wind_direction: str = "N"
    pressure_hpa: float = 1013.0
    pressure_trend: str = "stable"
    precipitation_mm: float = 0.0
    cloud_cover_pct: float = 0.0
    hunting_impact_score: float = 0.0


class SolunarData(BaseModel):
    moon_phase: str = "new"
    moon_illumination_pct: float = 0.0
    major_period_1: str = ""
    major_period_2: str = ""
    minor_period_1: str = ""
    minor_period_2: str = ""
    solunar_rating: float = 0.0
    activity_prediction: str = "moderate"


class HumanPressure(BaseModel):
    hunting_pressure_index: float = 0.0
    nearby_hunters_estimate: int = 0
    road_proximity_m: float = 0.0
    trail_density: float = 0.0
    disturbance_level: str = "low"
    recommended_buffer_m: float = 0.0


class HotspotData(BaseModel):
    id: str = ""
    name: str = ""
    lat: float = 0.0
    lng: float = 0.0
    type: str = "observation"
    species_observed: List[str] = []
    activity_score: float = 0.0
    last_activity: str = ""


class CorridorData(BaseModel):
    id: str = ""
    name: str = ""
    species: str = ""
    confidence: float = 0.0
    usage_frequency: str = "moderate"
    peak_hours: List[str] = []


class PredictionResult(BaseModel):
    species: str = ""
    success_probability: float = 0.0
    activity_level: str = "moderate"
    optimal_windows: List[Dict[str, Any]] = []
    confidence: str = "medium"
    factors_summary: Dict[str, str] = {}


class ScoringResult(BaseModel):
    global_score: float = 0.0
    habitat_score: float = 0.0
    food_score: float = 0.0
    water_score: float = 0.0
    cover_score: float = 0.0
    disturbance_score: float = 0.0
    trend: str = "stable"
    rank_percentile: float = 0.0


class EcologicalRecommendation(BaseModel):
    category: str = ""
    priority: str = "medium"
    title: str = ""
    description: str = ""
    action: str = ""
    expected_impact: str = ""


class HabitatMap(BaseModel):
    zone_type: str = ""
    polygon_coords: List[List[float]] = []
    habitat_quality: float = 0.0
    dominant_species: List[str] = []
    seasonal_use: Dict[str, str] = {}


class BehavioralMap(BaseModel):
    movement_corridors: List[CorridorData] = []
    feeding_zones: List[Dict[str, Any]] = []
    bedding_zones: List[Dict[str, Any]] = []
    water_access_points: List[Dict[str, Any]] = []
    activity_heatmap: List[Dict[str, Any]] = []


class ExecutiveSummary(BaseModel):
    territory_name: str = ""
    analysis_date: str = ""
    overall_rating: str = ""
    overall_score: float = 0.0
    key_strengths: List[str] = []
    key_weaknesses: List[str] = []
    top_recommendations: List[str] = []
    species_outlook: Dict[str, str] = {}


class EcologicalIntelligenceResponse(BaseModel):
    status: str = "success"
    analysis_id: str = ""
    scale: str = ""
    center: Dict[str, float] = {}
    timestamp: str = ""

    soil: Optional[SoilProfile] = None
    hydrology: Optional[HydrologyProfile] = None
    vegetation: Optional[VegetationProfile] = None
    minerals: Optional[MineralProfile] = None
    weather: Optional[WeatherSnapshot] = None
    solunar: Optional[SolunarData] = None
    human_pressure: Optional[HumanPressure] = None

    hotspots: List[HotspotData] = []
    corridors: List[CorridorData] = []
    habitat_map: Optional[BehavioralMap] = None

    predictions: List[PredictionResult] = []
    scoring: Optional[ScoringResult] = None
    recommendations: List[EcologicalRecommendation] = []
    executive_summary: Optional[ExecutiveSummary] = None
