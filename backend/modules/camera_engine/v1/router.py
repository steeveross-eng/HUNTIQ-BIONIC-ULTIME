"""
Camera Engine - API Router
Phase 1: Camera management and email ingestion endpoints
Phase 3 (CAM-Omega): Photo upload, stats, thumbnails
"""
import logging
import os
import io
import base64
import uuid as uuid_lib
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..dependencies import get_camera_db
from .models import (
    CameraCreate, CameraUpdate, CameraResponse, CameraListResponse,
    CameraEventResponse, CameraEventListResponse,
    EmailIngestionRequest, EmailIngestionResponse,
    PhotoUploadResponse, CameraStatsResponse
)
from .services import CameraRegistryService, EmailIngestionService, ExifReaderService, ImageEncryptionService
from ...roles_engine.v1.dependencies import get_current_user_with_role
from ...roles_engine.v1.models import UserWithRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/camera", tags=["Camera Engine"])


# ============================================
# CAMERA MANAGEMENT ENDPOINTS
# ============================================

@router.post("/cameras", response_model=CameraResponse, status_code=201)
async def create_camera(
    data: CameraCreate,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """
    Create a new camera.
    
    RÈGLE ABSOLUE: waypoint_id est OBLIGATOIRE.
    Une caméra sans waypoint sera rejetée.
    """
    service = CameraRegistryService(db)
    camera, error = await service.create_camera(user.user_id, data)
    
    if error:
        logger.warning(f"Camera creation rejected for user {user.user_id}: {error}")
        raise HTTPException(status_code=400, detail=error)
    
    return CameraResponse(**camera.model_dump())


@router.get("/cameras", response_model=CameraListResponse)
async def list_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """List all cameras for the current user."""
    service = CameraRegistryService(db)
    cameras, total = await service.list_cameras(user.user_id, skip, limit)
    
    return CameraListResponse(
        cameras=[CameraResponse(**c.model_dump()) for c in cameras],
        total=total
    )


@router.get("/cameras/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: str,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get camera details by ID."""
    service = CameraRegistryService(db)
    camera = await service.get_camera(camera_id, user.user_id)
    
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    return CameraResponse(**camera.model_dump())


@router.patch("/cameras/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: str,
    data: CameraUpdate,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """
    Update camera details.
    
    Note: Le waypoint_id ne peut pas être modifié ou supprimé.
    """
    service = CameraRegistryService(db)
    camera, error = await service.update_camera(camera_id, user.user_id, data)
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return CameraResponse(**camera.model_dump())


@router.delete("/cameras/{camera_id}", status_code=204)
async def delete_camera(
    camera_id: str,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Delete (deactivate) a camera."""
    service = CameraRegistryService(db)
    success = await service.delete_camera(camera_id, user.user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    return None


# ============================================
# EMAIL INGESTION ENDPOINT
# ============================================

@router.post("/email-ingest", response_model=EmailIngestionResponse)
async def ingest_email(
    request: EmailIngestionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """
    Process incoming email with photo attachments.
    
    This endpoint is called by the email forwarding service.
    
    RÈGLES:
    - L'email doit être envoyé à l'alias email de la caméra
    - La caméra DOIT avoir un waypoint associé
    - Seules les images sont traitées
    
    Statuts possibles:
    - SUCCESS: Photo ingérée et événement créé
    - FAILED: Rejet (caméra non trouvée, pas de waypoint, pas d'image)
    - QUARANTINED: Erreur lors du traitement
    """
    service = EmailIngestionService(db)
    response = await service.process_email(request)
    
    return response


# ============================================
# CAMERA EVENTS ENDPOINTS
# ============================================

@router.get("/events", response_model=CameraEventListResponse)
async def list_events(
    camera_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """List camera events for user."""
    service = EmailIngestionService(db)
    events, total = await service.get_events(user.user_id, camera_id, skip, limit)
    
    return CameraEventListResponse(
        events=[CameraEventResponse(
            id=e.id,
            user_id=e.user_id,
            camera_id=e.camera_id,
            waypoint_id=e.waypoint_id,
            timestamp=e.timestamp,
            species=e.species,
            direction=e.direction,
            activity=e.activity,
            individual_id=e.individual_id,
            thumbnail_url=e.thumbnail_url,
            is_quarantined=e.is_quarantined,
            created_at=e.created_at
        ) for e in events],
        total=total
    )


@router.get("/events/{event_id}", response_model=CameraEventResponse)
async def get_event(
    event_id: str,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get camera event details."""
    service = EmailIngestionService(db)
    event = await service.get_event(event_id, user.user_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    return CameraEventResponse(
        id=event.id,
        user_id=event.user_id,
        camera_id=event.camera_id,
        waypoint_id=event.waypoint_id,
        timestamp=event.timestamp,
        species=event.species,
        direction=event.direction,
        activity=event.activity,
        individual_id=event.individual_id,
        thumbnail_url=event.thumbnail_url,
        is_quarantined=event.is_quarantined,
        created_at=event.created_at
    )


# ============================================
# INGESTION LOGS ENDPOINT
# ============================================

@router.get("/ingestion-logs")
async def get_ingestion_logs(
    camera_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get ingestion logs for debugging and monitoring."""
    service = EmailIngestionService(db)
    logs = await service.get_ingestion_logs(user.user_id, camera_id, limit)
    
    return {
        "logs": [log.model_dump() for log in logs],
        "total": len(logs)
    }


# ============================================
# PHOTO UPLOAD ENDPOINTS (CAM-D)
# ============================================

@router.post("/photos/upload", response_model=PhotoUploadResponse)
async def upload_photos(
    camera_id: str = Form(...),
    files: List[UploadFile] = File(...),
    timestamp_override: Optional[str] = Form(None),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """
    Upload photos manually for a camera.
    Accepts 1-20 images. Each image is validated, EXIF extracted,
    encrypted, and stored as a camera event.
    """
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 photos par upload")
    
    # Verify camera ownership
    cam_service = CameraRegistryService(db)
    camera = await cam_service.get_camera(camera_id, user.user_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera non trouvee")
    
    exif_service = ExifReaderService()
    encryption_service = ImageEncryptionService()
    events_created = 0
    events = []
    validation_results = []
    
    for uploaded_file in files:
        filename = uploaded_file.filename or "unknown.jpg"
        content_type = uploaded_file.content_type or "image/jpeg"
        
        # Read file content
        image_data = await uploaded_file.read()
        file_size = len(image_data)
        
        # Basic validation
        if file_size == 0:
            validation_results.append({
                "filename": filename,
                "status": "invalid",
                "reason": "empty_file"
            })
            continue
        
        if file_size > 50 * 1024 * 1024:
            validation_results.append({
                "filename": filename,
                "status": "invalid",
                "reason": "too_large"
            })
            continue
        
        if not content_type.startswith("image/"):
            validation_results.append({
                "filename": filename,
                "status": "invalid",
                "reason": "not_an_image"
            })
            continue
        
        # Extract EXIF
        exif_data = exif_service.extract_exif(image_data)
        
        # Determine timestamp
        ts = None
        if timestamp_override:
            try:
                ts = datetime.fromisoformat(timestamp_override)
            except Exception:
                pass
        if not ts and exif_data.get("timestamp"):
            try:
                ts = datetime.fromisoformat(exif_data["timestamp"])
            except Exception:
                pass
        if not ts:
            ts = datetime.now(timezone.utc)
        
        # Encrypt and store
        event_id = str(uuid_lib.uuid4())
        photo_id = str(uuid_lib.uuid4())
        storage_dir = f"/app/backend/uploads/photos/{user.user_id}/{camera_id}"
        os.makedirs(storage_dir, exist_ok=True)
        storage_path = f"{storage_dir}/{event_id}.enc"
        
        encrypted_data = encryption_service.encrypt_image(image_data)
        with open(storage_path, "wb") as f:
            f.write(encrypted_data)
        
        # Generate thumbnail
        thumb_path = None
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(image_data))
            img.thumbnail((320, 320))
            thumb_dir = f"/app/backend/uploads/thumbs/{user.user_id}/{camera_id}"
            os.makedirs(thumb_dir, exist_ok=True)
            thumb_path = f"{thumb_dir}/{event_id}_thumb.jpg"
            img.save(thumb_path, "JPEG", quality=70)
        except Exception as e:
            logger.debug(f"Thumbnail generation skipped: {e}")
        
        # Create event
        event_doc = {
            "id": event_id,
            "user_id": user.user_id,
            "camera_id": camera_id,
            "waypoint_id": camera.waypoint_id,
            "timestamp": ts.isoformat() if ts else datetime.now(timezone.utc).isoformat(),
            "raw_image_url": storage_path,
            "thumbnail_url": thumb_path,
            "exif_data": exif_data,
            "source": "manual",
            "species": None,
            "direction": "unknown",
            "activity": "unknown",
            "individual_id": None,
            "is_quarantined": False,
            "quarantine_reason": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db['camera_events'].insert_one(event_doc)
        
        # Create photo record
        photo_doc = {
            "id": photo_id,
            "event_id": event_id,
            "camera_id": camera_id,
            "user_id": user.user_id,
            "filename_original": filename,
            "storage_path": storage_path,
            "thumbnail_path": thumb_path,
            "file_size": file_size,
            "mime_type": content_type,
            "validation_status": "valid",
            "exif_quality_score": exif_data.get("quality_score", 0) if isinstance(exif_data, dict) else 0,
            "encrypted": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db['camera_photos'].insert_one(photo_doc)
        
        # Increment camera photo count
        await cam_service.increment_photo_count(camera_id)
        
        events_created += 1
        events.append({"id": event_id, "camera_id": camera_id, "timestamp": ts.isoformat() if ts else ""})
        validation_results.append({
            "filename": filename,
            "status": "valid",
            "exif_quality": exif_data.get("quality_score", 0) if isinstance(exif_data, dict) else 0
        })
    
    return PhotoUploadResponse(
        success=events_created > 0,
        events_created=events_created,
        events=events,
        validation_results=validation_results
    )


@router.get("/photos/{photo_id}/thumbnail")
async def get_photo_thumbnail(
    photo_id: str,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get photo thumbnail (JPEG)."""
    photo = await db['camera_photos'].find_one(
        {"id": photo_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not photo or not photo.get("thumbnail_path"):
        raise HTTPException(status_code=404, detail="Thumbnail non trouve")
    
    thumb_path = photo["thumbnail_path"]
    if not os.path.exists(thumb_path):
        raise HTTPException(status_code=404, detail="Fichier thumbnail manquant")
    
    from fastapi.responses import FileResponse
    return FileResponse(thumb_path, media_type="image/jpeg")


@router.get("/photos/{photo_id}/view")
async def view_photo(
    photo_id: str,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Decrypt and serve photo (full resolution)."""
    photo = await db['camera_photos'].find_one(
        {"id": photo_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not photo:
        raise HTTPException(status_code=404, detail="Photo non trouvee")
    
    storage_path = photo.get("storage_path", "")
    if not os.path.exists(storage_path):
        raise HTTPException(status_code=404, detail="Fichier photo manquant")
    
    encryption_service = ImageEncryptionService()
    with open(storage_path, "rb") as f:
        encrypted = f.read()
    
    decrypted = encryption_service.decrypt_image(encrypted)
    
    from fastapi.responses import Response
    return Response(content=decrypted, media_type=photo.get("mime_type", "image/jpeg"))


# ============================================
# CAMERA STATS ENDPOINT
# ============================================

@router.get("/stats", response_model=CameraStatsResponse)
async def get_camera_stats(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get camera stats for the current user."""
    total_cameras = await db['cameras'].count_documents({"user_id": user.user_id})
    active_cameras = await db['cameras'].count_documents({"user_id": user.user_id, "status": "active"})
    total_photos = await db['camera_photos'].count_documents({"user_id": user.user_id})
    total_events = await db['camera_events'].count_documents({"user_id": user.user_id})
    
    # Recent events (last 10)
    cursor = db['camera_events'].find(
        {"user_id": user.user_id, "is_quarantined": False},
        {"_id": 0, "raw_image_url": 0}
    ).sort("timestamp", -1).limit(10)
    recent = await cursor.to_list(length=10)
    
    return CameraStatsResponse(
        total_cameras=total_cameras,
        active_cameras=active_cameras,
        total_photos=total_photos,
        total_events=total_events,
        recent_events=recent
    )


# ============================================
# DB INDEXES (CAM-A)
# ============================================

async def ensure_camera_indexes(db: AsyncIOMotorDatabase):
    """Create MongoDB indexes for camera collections."""
    await db['cameras'].create_index([("user_id", 1), ("status", 1)])
    await db['cameras'].create_index("email_alias", unique=True, sparse=True)
    await db['camera_events'].create_index([("user_id", 1), ("timestamp", -1)])
    await db['camera_events'].create_index([("camera_id", 1), ("timestamp", -1)])
    await db['camera_events'].create_index([("waypoint_id", 1), ("timestamp", -1)])
    await db['camera_events'].create_index("species")
    await db['camera_photos'].create_index("event_id")
    await db['camera_photos'].create_index([("camera_id", 1), ("created_at", -1)])
    await db['camera_ingestion_logs'].create_index([("camera_id", 1), ("created_at", -1)])
