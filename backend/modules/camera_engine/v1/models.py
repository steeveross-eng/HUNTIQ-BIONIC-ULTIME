"""
Camera Engine - Pydantic Models
CAMERA-BRANDS-Omega-FINAL: Standardisation complete marques/modeles/type
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class CameraManufacturer(str, Enum):
    """Marques officielles Canada/USA — CAMERA-BRANDS-Omega-FINAL"""
    SPYPOINT = "spypoint"
    BROWNING = "browning"
    BUSHNELL = "bushnell"
    MOULTRIE = "moultrie"
    TACTACAM = "tactacam"
    STEALTH_CAM = "stealth_cam"
    WILDGAME = "wildgame"
    CUDDEBACK = "cuddeback"
    COVERT = "covert"
    RECONYX = "reconyx"
    EXODUS = "exodus"
    SPARTAN = "spartan"
    PRIMOS = "primos"
    GARDEPRO = "gardepro"
    CAMPARK = "campark"
    MEIDASE = "meidase"
    CREATIVEXP = "creativexp"
    WOSPORTS = "wosports"
    GSM_OUTDOORS = "gsm_outdoors"
    BOLY = "boly"
    OTHER = "other"


class CameraType(str, Enum):
    """Type de camera — obligatoire"""
    CELLULAIRE = "cellulaire"
    REGULIERE = "reguliere"


class CameraStatus(str, Enum):
    """Camera operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class EventActivity(str, Enum):
    """Types of activity captured"""
    PASSAGE = "passage"
    FEEDING = "feeding"
    RESTING = "resting"
    ALERT = "alert"
    UNKNOWN = "unknown"


class EventDirection(str, Enum):
    """Direction of movement"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    STATIONARY = "stationary"
    UNKNOWN = "unknown"


# ============================================
# CAMERA MODELS
# ============================================

class CameraBase(BaseModel):
    """Base camera model with shared fields"""
    manufacturer: CameraManufacturer = CameraManufacturer.OTHER
    model: Optional[str] = None
    serial: Optional[str] = None
    name: Optional[str] = None
    camera_type: Optional[CameraType] = None
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    integration_type: str = "manual"


class CameraCreate(CameraBase):
    """Model for creating a new camera - waypoint_id is OPTIONAL"""
    waypoint_id: Optional[str] = Field(None, description="ID du waypoint associe - optionnel")
    camera_type: CameraType = Field(..., description="Type de camera obligatoire: cellulaire ou reguliere")


class CameraUpdate(BaseModel):
    """Model for updating camera"""
    manufacturer: Optional[CameraManufacturer] = None
    model: Optional[str] = None
    serial: Optional[str] = None
    name: Optional[str] = None
    camera_type: Optional[CameraType] = None
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    status: Optional[CameraStatus] = None
    integration_type: Optional[str] = None


class CameraLocationUpdate(BaseModel):
    """Model for updating camera location"""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class Camera(CameraBase):
    """Complete camera model for database storage and responses"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    email_alias: str
    api_secret: str = ""
    waypoint_id: Optional[str] = None
    location: Optional[dict] = None
    status: CameraStatus = CameraStatus.ACTIVE
    photo_count: int = 0
    last_photo_at: Optional[datetime] = None
    external_account: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class CameraResponse(BaseModel):
    """API response model for camera"""
    id: str
    user_id: str
    email_alias: str
    api_secret: str = ""
    waypoint_id: Optional[str] = None
    manufacturer: CameraManufacturer
    model: Optional[str] = None
    serial: Optional[str] = None
    name: Optional[str] = None
    camera_type: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    location: Optional[dict] = None
    status: CameraStatus
    photo_count: int = 0
    last_photo_at: Optional[datetime] = None
    integration_type: str = "manual"
    external_account: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class CameraListResponse(BaseModel):
    """Response for listing cameras"""
    cameras: List[CameraResponse]
    total: int


# ============================================
# CAMERA EVENT MODELS
# ============================================

class CameraEventBase(BaseModel):
    """Base camera event model"""
    species: Optional[str] = None
    direction: EventDirection = EventDirection.UNKNOWN
    activity: EventActivity = EventActivity.UNKNOWN
    individual_id: Optional[str] = None
    notes: Optional[str] = None


class CameraEventCreate(CameraEventBase):
    """Model for creating camera event (internal use)"""
    camera_id: str
    timestamp: datetime
    raw_image_url: str


class CameraEvent(CameraEventBase):
    """Complete camera event model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    camera_id: str
    waypoint_id: Optional[str] = None
    timestamp: datetime
    raw_image_url: str
    thumbnail_url: Optional[str] = None
    exif_data: Optional[dict] = None
    source: str = "manual"
    is_quarantined: bool = False
    quarantine_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class CameraEventResponse(BaseModel):
    """API response model for camera event"""
    id: str
    user_id: str
    camera_id: str
    waypoint_id: Optional[str] = None
    timestamp: datetime
    species: Optional[str] = None
    direction: EventDirection
    activity: EventActivity
    individual_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_quarantined: bool
    created_at: datetime


class CameraEventListResponse(BaseModel):
    """Response for listing camera events"""
    events: List[CameraEventResponse]
    total: int


# ============================================
# EMAIL INGESTION MODELS
# ============================================

class EmailIngestionStatus(str, Enum):
    """Status of email ingestion"""
    SUCCESS = "success"
    FAILED = "failed"
    QUARANTINED = "quarantined"


class EmailIngestionRequest(BaseModel):
    """Request model for email ingestion webhook"""
    from_email: str
    to_email: str
    subject: Optional[str] = None
    body: Optional[str] = None
    attachments: List[dict] = []


class EmailIngestionResponse(BaseModel):
    """Response for email ingestion"""
    status: EmailIngestionStatus
    message: str
    event_id: Optional[str] = None
    camera_id: Optional[str] = None
    quarantine_reason: Optional[str] = None


class IngestionLog(BaseModel):
    """Log entry for ingestion attempts"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    camera_id: Optional[str] = None
    email_alias: str
    from_email: str
    status: EmailIngestionStatus
    message: str
    event_id: Optional[str] = None
    error_details: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# PHOTO MODELS (CAM-A)
# ============================================

class CameraPhoto(BaseModel):
    """Individual photo stored for a camera event"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    camera_id: str
    user_id: str
    filename_original: str
    storage_path: str
    thumbnail_path: Optional[str] = None
    file_size: int = 0
    mime_type: str = "image/jpeg"
    width: Optional[int] = None
    height: Optional[int] = None
    validation_status: str = "valid"
    validation_reason: Optional[str] = None
    exif_quality_score: int = 0
    encrypted: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PhotoUploadResponse(BaseModel):
    """Response from photo upload endpoint"""
    success: bool
    events_created: int
    events: List[dict] = []
    validation_results: List[dict] = []


class CameraStatsResponse(BaseModel):
    """Stats for camera dashboard"""
    total_cameras: int = 0
    active_cameras: int = 0
    total_photos: int = 0
    total_events: int = 0
    recent_events: List[dict] = []
