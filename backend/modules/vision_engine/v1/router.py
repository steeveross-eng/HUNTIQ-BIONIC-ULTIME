"""
Vision Engine — API Router
Endpoints for IA Vision analysis, hotspots, trajectories
"""
import os
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...camera_engine.dependencies import get_camera_db
from .services import VisionAnalysisService
from ...roles_engine.v1.dependencies import get_current_user_with_role
from ...roles_engine.v1.models import UserWithRole

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/vision", tags=["Vision IA"])


@router.post("/analyze")
async def analyze_photo(
    photo_id: str = Form(None),
    camera_id: str = Form(None),
    image: UploadFile = File(None),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Analyze a photo using IA Vision. Accepts photo_id OR direct image upload."""
    service = VisionAnalysisService(db)

    if photo_id:
        # Load from stored photo
        photo = await db["camera_photos"].find_one({"id": photo_id, "user_id": user.user_id}, {"_id": 0})
        if not photo:
            raise HTTPException(status_code=404, detail="Photo non trouvee")

        storage_path = photo.get("storage_path", "")
        if not os.path.exists(storage_path):
            raise HTTPException(status_code=404, detail="Fichier photo manquant")

        # Decrypt
        from ...camera_engine.v1.services import ImageEncryptionService
        enc_service = ImageEncryptionService()
        with open(storage_path, "rb") as f:
            encrypted = f.read()
        image_data = enc_service.decrypt_image(encrypted)

        # Get camera info for GPS fallback
        cam = await db["cameras"].find_one({"id": photo.get("camera_id")}, {"_id": 0})
        gps_lat = cam.get("gps_lat") if cam else None
        gps_lon = cam.get("gps_lon") if cam else None
        cam_id = photo.get("camera_id", camera_id or "")

        result = await service.analyze_photo(
            user_id=user.user_id, photo_id=photo_id, camera_id=cam_id,
            image_data=image_data, mime_type=photo.get("mime_type", "image/jpeg"),
            gps_lat=gps_lat, gps_lon=gps_lon, event_id=photo.get("event_id")
        )

    elif image:
        image_data = await image.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="Image vide")

        # Get camera GPS if camera_id provided
        gps_lat, gps_lon = None, None
        if camera_id:
            cam = await db["cameras"].find_one({"id": camera_id, "user_id": user.user_id}, {"_id": 0})
            if cam:
                gps_lat = cam.get("gps_lat")
                gps_lon = cam.get("gps_lon")

        result = await service.analyze_photo(
            user_id=user.user_id, photo_id=str(hash(image_data))[:12],
            camera_id=camera_id or "direct_upload",
            image_data=image_data, mime_type=image.content_type or "image/jpeg",
            gps_lat=gps_lat, gps_lon=gps_lon
        )
    else:
        raise HTTPException(status_code=400, detail="Fournir photo_id ou image")

    return {"success": True, "analysis": result}


@router.post("/batch-analyze")
async def batch_analyze(
    photo_ids: list = [],
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Batch analyze multiple photos."""
    if not photo_ids:
        raise HTTPException(status_code=400, detail="Fournir photo_ids")
    if len(photo_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 photos par batch")

    service = VisionAnalysisService(db)
    results = []
    failed = 0

    for pid in photo_ids:
        try:
            photo = await db["camera_photos"].find_one({"id": pid, "user_id": user.user_id}, {"_id": 0})
            if not photo:
                failed += 1
                continue

            storage_path = photo.get("storage_path", "")
            if not os.path.exists(storage_path):
                failed += 1
                continue

            from ...camera_engine.v1.services import ImageEncryptionService
            enc_service = ImageEncryptionService()
            with open(storage_path, "rb") as f:
                encrypted = f.read()
            image_data = enc_service.decrypt_image(encrypted)

            cam = await db["cameras"].find_one({"id": photo.get("camera_id")}, {"_id": 0})
            result = await service.analyze_photo(
                user_id=user.user_id, photo_id=pid,
                camera_id=photo.get("camera_id", ""),
                image_data=image_data,
                gps_lat=cam.get("gps_lat") if cam else None,
                gps_lon=cam.get("gps_lon") if cam else None,
                event_id=photo.get("event_id")
            )
            results.append(result)
        except Exception as e:
            logger.error(f"Batch analyze error for {pid}: {e}")
            failed += 1

    return {"success": True, "results": results, "processed": len(results), "failed": failed}


@router.get("/analyses")
async def get_analyses(
    camera_id: Optional[str] = Query(None),
    species: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get vision analyses for the current user."""
    service = VisionAnalysisService(db)
    analyses = await service.get_analyses(user.user_id, camera_id, species, limit)
    return {"analyses": analyses, "total": len(analyses)}


@router.post("/hotspots/generate")
async def generate_hotspots(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Generate ALPHA hotspots from vision analyses."""
    service = VisionAnalysisService(db)
    hotspots = await service.generate_hotspots(user.user_id)
    return {"success": True, "hotspots": hotspots, "total": len(hotspots)}


@router.get("/hotspots/alpha")
async def get_alpha_hotspots(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get stored ALPHA hotspots."""
    service = VisionAnalysisService(db)
    hotspots = await service.get_hotspots(user.user_id)
    return {"hotspots": hotspots, "total": len(hotspots)}


@router.post("/trajectories/generate")
async def generate_trajectories(
    days: int = Query(30, ge=1, le=365),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Generate trajectories from multi-camera analyses."""
    service = VisionAnalysisService(db)
    trajectories = await service.generate_trajectories(user.user_id, days)
    return {"success": True, "trajectories": trajectories, "total": len(trajectories)}


@router.get("/trajectories")
async def get_trajectories(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get stored trajectories."""
    service = VisionAnalysisService(db)
    trajectories = await service.get_trajectories(user.user_id)
    return {"trajectories": trajectories, "total": len(trajectories)}


@router.get("/stats")
async def get_vision_stats(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Get IA Vision stats."""
    total_analyses = await db["vision_analyses"].count_documents({"user_id": user.user_id})
    total_hotspots = await db["vision_hotspots"].count_documents({"user_id": user.user_id})
    total_trajectories = await db["vision_trajectories"].count_documents({"user_id": user.user_id})
    alpha_count = await db["vision_analyses"].count_documents({"user_id": user.user_id, "alpha_score": {"$gte": 85}})
    species_cursor = db["vision_analyses"].distinct("species", {"user_id": user.user_id})
    species_list = await species_cursor if hasattr(species_cursor, '__await__') else species_cursor

    return {
        "total_analyses": total_analyses,
        "total_hotspots": total_hotspots,
        "total_trajectories": total_trajectories,
        "alpha_count": alpha_count,
        "species_detected": [s for s in species_list if s != "aucun_animal"] if isinstance(species_list, list) else []
    }


# ============================================
# H: COMMERCIAL VALUE ENDPOINTS
# ============================================

@router.get("/territories/scores")
async def get_territory_scores(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """H2: Get territory scores based on ALPHA analysis."""
    service = VisionAnalysisService(db)
    scores = await service.compute_territory_scores(user.user_id)
    return {"territories": scores, "total": len(scores)}


@router.get("/territories/anomalies")
async def get_anomalies(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """H6: Detect anomalies in territory activity."""
    service = VisionAnalysisService(db)
    anomalies = await service.detect_anomalies(user.user_id)
    return {"anomalies": anomalies, "total": len(anomalies)}


@router.get("/territories/report")
async def get_commercial_report(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """H4: Generate commercial report for territories."""
    service = VisionAnalysisService(db)
    report = await service.generate_commercial_report(user.user_id)
    return report


async def ensure_vision_indexes(db: AsyncIOMotorDatabase):
    """Create MongoDB indexes for vision collections."""
    await db["vision_analyses"].create_index([("user_id", 1), ("analyzed_at", -1)])
    await db["vision_analyses"].create_index([("camera_id", 1), ("analyzed_at", -1)])
    await db["vision_analyses"].create_index([("species", 1), ("alpha_score", -1)])
    await db["vision_analyses"].create_index([("location", "2dsphere")], sparse=True)
    await db["vision_individuals"].create_index([("user_id", 1), ("species", 1)])
    await db["vision_individuals"].create_index([("territory_center", "2dsphere")], sparse=True)
    await db["vision_trajectories"].create_index([("user_id", 1), ("created_at", -1)])
    await db["vision_hotspots"].create_index([("user_id", 1), ("score", -1)])
    await db["vision_hotspots"].create_index([("location", "2dsphere")], sparse=True)
