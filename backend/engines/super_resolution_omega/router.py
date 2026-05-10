"""ENGINE_SUPER_RESOLUTION_Ω · Router FastAPI · NEW_ENGINE_4."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from . import (
    DEFAULT_MODE,
    ENGINE_DOCTRINE,
    ENGINE_NAME,
    ENGINE_VERSION,
    MAX_INPUT_SIZE,
    MODE_BICUBIC_X4,
    MODE_LANCZOS_X2,
    MODE_LANCZOS_X4,
    MODE_REAL_ESRGAN_X4,
    MODE_TORCH_BICUBIC_X4,
    _has_real_esrgan,
    _has_torch,
    upscale_dem_hr,
    upscale_lidar_hr,
    upscale_spectral_layer,
)

router = APIRouter(prefix="/api/v20/super-resolution",
                    tags=["ENGINE_SUPER_RESOLUTION_Ω_NEW_ENGINE_4"])


class GridUpscaleBody(BaseModel):
    grid: list[list[float]]
    factor: int = 4
    mode: str = DEFAULT_MODE
    layer_name: str = "ndvi"


@router.get("/status")
async def sr_status() -> dict[str, Any]:
    return {
        "engine_name": ENGINE_NAME, "version": ENGINE_VERSION,
        "doctrine": ENGINE_DOCTRINE,
        "modes_supported": [
            MODE_REAL_ESRGAN_X4, MODE_TORCH_BICUBIC_X4,
            MODE_LANCZOS_X4, MODE_LANCZOS_X2, MODE_BICUBIC_X4,
        ],
        "default_mode": DEFAULT_MODE,
        "max_input_size_px": MAX_INPUT_SIZE,
        "torch_available": _has_torch(),
        "real_esrgan_native_available": _has_real_esrgan(),
        "implementation_note": (
            "REAL_ESRGAN_X4 utilise SR torch native (bicubic anti-aliased + "
            "Laplacian sharpening 3×3) si realesrgan package absent. "
            "Conserve la qualité supérieure au Lanczos via pipeline torch."
        ),
        "active": True, "priority": 0,
    }


@router.post("/upscale-dem")
async def sr_dem(body: GridUpscaleBody) -> dict[str, Any]:
    """Upscale DEM HR par factor (default x4 Lanczos)."""
    return upscale_dem_hr(body.grid, factor=body.factor, mode=body.mode)


@router.post("/upscale-lidar")
async def sr_lidar(body: GridUpscaleBody) -> dict[str, Any]:
    """Upscale LIDAR HR (limité x2 pour préservation fidélité)."""
    return upscale_lidar_hr(body.grid, factor=min(body.factor, 2), mode=body.mode)


@router.post("/upscale-spectral")
async def sr_spectral(body: GridUpscaleBody) -> dict[str, Any]:
    """Upscale couche spectrale (NDVI/NDWI/EVI/LST)."""
    return upscale_spectral_layer(
        body.grid, layer_name=body.layer_name,
        factor=body.factor, mode=body.mode)
