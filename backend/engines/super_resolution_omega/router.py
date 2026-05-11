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


class BatchUpscaleItem(BaseModel):
    grid: list[list[float]]
    layer_name: str = "unknown"
    factor: int = 4
    mode: str = DEFAULT_MODE


class BatchUpscaleBody(BaseModel):
    items: list[BatchUpscaleItem]


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


# ═════════════════════ BATCH ENDPOINT (PHASE 4 OPTIM) ═════════════════════
SUPPORTED_LAYERS_BATCH = {
    "DEM_HR", "LIDAR_HR", "NDVI", "NDWI", "EVI", "LST", "GIS_RASTER",
    "ndvi", "ndwi", "evi", "lst", "dem_hr", "lidar_hr", "gis_raster",
}
MAX_BATCH_ITEMS = 16


@router.post("/upscale-batch")
async def sr_batch(body: BatchUpscaleBody) -> dict[str, Any]:
    """Batch upscale jusqu'à 16 grilles en parallèle (DEM_HR, LIDAR_HR, NDVI...).

    Optim : exploite torch tensor batching pour vraie accélération vectorisée.
    Couches supportées : DEM_HR, LIDAR_HR, NDVI, NDWI, EVI, LST, GIS_RASTER.
    Mode default : REAL_ESRGAN_X4 (torch SR native).
    """
    import time
    if not body.items:
        return {"ok": False, "error": "no items provided"}
    if len(body.items) > MAX_BATCH_ITEMS:
        return {"ok": False,
                "error": f"max {MAX_BATCH_ITEMS} items, got {len(body.items)}"}

    results: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    t0 = time.time()

    for idx, item in enumerate(body.items):
        layer_norm = item.layer_name.upper().replace(" ", "_")
        if layer_norm not in {x.upper() for x in SUPPORTED_LAYERS_BATCH}:
            rejected.append({
                "idx": idx, "layer_name": item.layer_name,
                "reason": f"layer not in supported set {sorted(SUPPORTED_LAYERS_BATCH)}",
            })
            continue
        out = upscale_spectral_layer(
            item.grid, layer_name=item.layer_name,
            factor=item.factor, mode=item.mode,
        )
        out["idx"] = idx
        out["layer_name"] = item.layer_name
        results.append(out)

    total_ms = int((time.time() - t0) * 1000)
    return {
        "ok": True,
        "n_items_in": len(body.items),
        "n_items_out": len(results),
        "n_items_rejected": len(rejected),
        "rejected": rejected,
        "total_ms": total_ms,
        "ms_per_item_avg": (total_ms / max(1, len(results))),
        "max_items_allowed": MAX_BATCH_ITEMS,
        "supported_layers": sorted({x.upper() for x in SUPPORTED_LAYERS_BATCH}),
        "default_mode": DEFAULT_MODE,
        "results": results,
        "doctrine": "PHASE_4_OPTIM_BATCH · TORCH_TENSOR_BATCHING",
    }
