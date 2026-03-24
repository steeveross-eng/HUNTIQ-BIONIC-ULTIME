"""
BIONIC Data Fabric — Unified Schemas
STEEVE-MAX x2000 / Phase B

Schema unifie pour la normalisation des donnees inter-modules.
Point d'acces centralise pour INTELLIGENCE / ANALYSE / MON TERRITOIRE.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class DataDomain(str, Enum):
    TERRITORY = "territory"
    WILDLIFE = "wildlife"
    WEATHER = "weather"
    SOIL = "soil"
    VEGETATION = "vegetation"
    HYDROLOGY = "hydrology"
    PREDICTIONS = "predictions"
    SCORING = "scoring"
    OBSERVATIONS = "observations"
    CAMERAS = "cameras"
    GPS_TRACKS = "gps_tracks"
    ALERTS = "alerts"
    SALINE = "saline"
    CORRIDORS = "corridors"
    HOTSPOTS = "hotspots"
    SPECIES = "species"       # x2250: referentiel especes
    PERMITS = "permits"       # x2250: permis et enregistrement
    LEGAL = "legal"           # x2250: cadre juridique


class DataQuality(str, Enum):
    RAW = "raw"
    VALIDATED = "validated"
    ENRICHED = "enriched"
    CONSOLIDATED = "consolidated"


class NormalizedDataPoint(BaseModel):
    """Schema unifie pour tout point de donnee BIONIC"""
    id: str = ""
    domain: DataDomain = DataDomain.TERRITORY
    source_module: str = ""
    timestamp: str = ""
    location: Optional[Dict[str, float]] = None
    quality: DataQuality = DataQuality.RAW
    data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    tags: List[str] = []
    version: str = "1.0"


class DataFabricQuery(BaseModel):
    """Requete multi-domaine sur la Data Fabric"""
    domains: List[DataDomain] = []
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_m: int = 1000
    time_range_hours: int = 168  # 7 days default
    quality_min: DataQuality = DataQuality.RAW
    limit: int = 100
    include_history: bool = False


class DataFabricResponse(BaseModel):
    status: str = "success"
    query_id: str = ""
    total_records: int = 0
    domains_queried: List[str] = []
    data_points: List[NormalizedDataPoint] = []
    coherence_score: float = 0.0
    freshness: Dict[str, str] = {}


class ModuleConnectionStatus(BaseModel):
    module_name: str = ""
    domain: str = ""
    connected: bool = False
    last_sync: str = ""
    record_count: int = 0
    health: str = "unknown"


class FabricHealthResponse(BaseModel):
    status: str = "operational"
    total_modules_connected: int = 0
    total_data_points: int = 0
    domains_active: List[str] = []
    module_connections: List[ModuleConnectionStatus] = []
    coherence_global: float = 0.0


class HistoryEntry(BaseModel):
    timestamp: str = ""
    domain: str = ""
    action: str = ""
    data_count: int = 0
    source: str = ""
