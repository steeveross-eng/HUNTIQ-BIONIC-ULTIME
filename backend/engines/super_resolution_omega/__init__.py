"""
ENGINE_SUPER_RESOLUTION_OMEGA · NEW_ENGINE_4 · IA SUPER RESOLUTION
══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Objectif : upscaling haute fidélité de DEM_HR, LIDAR_HR, SPECTRAL.

Stratégie HIGH_FIDELITY :
  - V1 LIVE  : Lanczos resampling x4 (PIL) — anti-générique, pas de mock
  - V2 PREP  : architecture compatible Real-ESRGAN (torch+realesrgan
              à installer en option, scaffolding prêt)

Différence Lanczos vs Real-ESRGAN :
  - Lanczos : interpolation polynomiale de degré 3, qualité photographique
              acceptable, déterministe, sans GPU.
  - Real-ESRGAN : réseau de neurones x4 entraîné, qualité supérieure,
              nécessite torch + GPU pour des temps acceptables.

DOCTRINE ANTI-GÉNÉRIQUE :
  - Aucune valeur synthétique.
  - Lanczos est une vraie super-résolution mathématique standard.
  - Documentation explicite : V1 fournit Lanczos, V2 fournira Real-ESRGAN
    quand torch/realesrgan seront disponibles.

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW ENGINE EXTERNE
"""

from __future__ import annotations

import base64
import io
import logging
from typing import Any

import numpy as np
from PIL import Image

from engines.v8_institutional.engine_science_omega import mark_call, register_engine

logger = logging.getLogger("engine_super_resolution_omega")

ENGINE_NAME = "ENGINE-SUPER-RESOLUTION-Ω"
ENGINE_VERSION = "V1_LOCK-NEW_ENGINE_4_LANCZOS_X4-2026-05"
ENGINE_DOCTRINE = "NEW_ENGINE_4 · IA_SUPER_RESOLUTION · HIGH_FIDELITY"

# Modes supportés
MODE_LANCZOS_X4 = "LANCZOS_X4"
MODE_LANCZOS_X2 = "LANCZOS_X2"
MODE_BICUBIC_X4 = "BICUBIC_X4"
MODE_REAL_ESRGAN_X4 = "REAL_ESRGAN_X4"  # V2 — nécessite torch + realesrgan

DEFAULT_MODE = MODE_LANCZOS_X4
MAX_INPUT_SIZE = 512  # px max input pour usage runtime preview

register_engine(
    ENGINE_NAME, ENGINE_VERSION,
    "PHASE 4 IA SUPER RESOLUTION : Lanczos x4 + scaffold Real-ESRGAN",
    "BIO-SYSTEME",
    ["PIL_LANCZOS", "REAL_ESRGAN_PREP"],
)


# ═════════════════════ DETECTORS ═════════════════════
def _has_real_esrgan() -> bool:
    """Détecte si torch + realesrgan sont disponibles."""
    try:
        import torch  # noqa: F401
        from realesrgan import RealESRGANer  # noqa: F401
        return True
    except Exception:
        return False


# ═════════════════════ CORE UPSCALERS ═════════════════════
def upscale_array_lanczos(arr: np.ndarray, factor: int = 4) -> np.ndarray:
    """Upscale matrice 2D ou 3D via Lanczos (PIL).

    INPUT  : np.ndarray (H, W) float ou (H, W, C) uint8
    OUTPUT : np.ndarray upscalé par `factor`
    """
    if arr.ndim == 2:
        # Matrice scalaire (DEM, NDVI, etc.) : normalize → uint8 → resize → denormalize
        a_min = float(np.nanmin(arr))
        a_max = float(np.nanmax(arr))
        span = max(1e-9, a_max - a_min)
        norm = ((arr - a_min) / span * 255.0).astype(np.uint8)
        img = Image.fromarray(norm, mode="L")
        target_size = (int(arr.shape[1] * factor), int(arr.shape[0] * factor))
        upscaled = img.resize(target_size, Image.LANCZOS)
        upscaled_arr = np.array(upscaled, dtype=np.float32) / 255.0
        return upscaled_arr * span + a_min
    elif arr.ndim == 3 and arr.shape[2] in (3, 4):
        # Image RGB(A)
        if arr.dtype != np.uint8:
            arr_u8 = ((arr - arr.min()) / max(1e-9, arr.max() - arr.min())
                      * 255.0).astype(np.uint8)
        else:
            arr_u8 = arr
        mode = "RGBA" if arr.shape[2] == 4 else "RGB"
        img = Image.fromarray(arr_u8, mode=mode)
        target_size = (int(arr.shape[1] * factor), int(arr.shape[0] * factor))
        upscaled = img.resize(target_size, Image.LANCZOS)
        return np.array(upscaled)
    else:
        raise ValueError(f"Unsupported array shape: {arr.shape}")


def upscale_array_bicubic(arr: np.ndarray, factor: int = 4) -> np.ndarray:
    """Upscale via bicubic (compat fallback)."""
    if arr.ndim == 2:
        a_min, a_max = float(np.nanmin(arr)), float(np.nanmax(arr))
        span = max(1e-9, a_max - a_min)
        norm = ((arr - a_min) / span * 255.0).astype(np.uint8)
        img = Image.fromarray(norm, mode="L")
        target_size = (int(arr.shape[1] * factor), int(arr.shape[0] * factor))
        upscaled = img.resize(target_size, Image.BICUBIC)
        return np.array(upscaled, dtype=np.float32) / 255.0 * span + a_min
    raise ValueError("Bicubic upscaler implémenté pour ndim=2 uniquement")


def upscale_real_esrgan_x4(arr: np.ndarray) -> np.ndarray:
    """Upscale via Real-ESRGAN x4 — V2 si torch + realesrgan installés.

    Si non disponibles → fallback Lanczos x4 + warning institutionnel.
    """
    if not _has_real_esrgan():
        logger.warning("[%s] Real-ESRGAN non installé. Fallback Lanczos x4.", ENGINE_NAME)
        return upscale_array_lanczos(arr, factor=4)
    # Implementation V2 (à activer quand torch + realesrgan disponibles)
    raise NotImplementedError(
        "Real-ESRGAN V2 — installer torch>=2.4 + realesrgan-ncnn-vulkan-py")


# ═════════════════════ HIGH-LEVEL PIPELINE ═════════════════════
def upscale_dem_hr(elev_grid: list[list[float]],
                    factor: int = 4,
                    mode: str = DEFAULT_MODE) -> dict[str, Any]:
    """Upscale DEM HR (élévation 2D) par `factor`."""
    mark_call(ENGINE_NAME)
    arr = np.array(elev_grid, dtype=np.float32)
    if arr.ndim != 2 or arr.size == 0:
        return {"valid": False, "error": "elev_grid invalide"}

    if mode == MODE_REAL_ESRGAN_X4:
        if _has_real_esrgan():
            try:
                up = upscale_real_esrgan_x4(arr)
            except NotImplementedError:
                up = upscale_array_lanczos(arr, factor=4)
                mode = MODE_LANCZOS_X4 + " (fallback Real-ESRGAN absent)"
        else:
            up = upscale_array_lanczos(arr, factor=4)
            mode = MODE_LANCZOS_X4 + " (fallback Real-ESRGAN non installé)"
    elif mode == MODE_LANCZOS_X2:
        up = upscale_array_lanczos(arr, factor=2)
    elif mode == MODE_BICUBIC_X4:
        up = upscale_array_bicubic(arr, factor=4)
    else:
        up = upscale_array_lanczos(arr, factor=factor)

    return {
        "valid": True,
        "mode": mode,
        "factor": factor,
        "shape_in": list(arr.shape),
        "shape_out": list(up.shape),
        "stats_in": {
            "min": float(np.nanmin(arr)), "max": float(np.nanmax(arr)),
            "mean": float(np.nanmean(arr)),
        },
        "stats_out": {
            "min": float(np.nanmin(up)), "max": float(np.nanmax(up)),
            "mean": float(np.nanmean(up)),
        },
        "doctrine": ENGINE_DOCTRINE,
        "real_esrgan_available": _has_real_esrgan(),
    }


def upscale_spectral_layer(spectral_grid: list[list[float]],
                            layer_name: str = "ndvi",
                            factor: int = 4,
                            mode: str = DEFAULT_MODE) -> dict[str, Any]:
    """Upscale couche spectrale (NDVI/NDWI/EVI/LST) par `factor`."""
    mark_call(ENGINE_NAME)
    out = upscale_dem_hr(spectral_grid, factor=factor, mode=mode)
    out["layer_name"] = layer_name
    out["doctrine_applied"] = f"SPECTRAL_UPSCALE · {layer_name.upper()}"
    return out


def upscale_lidar_hr(lidar_grid: list[list[float]],
                      factor: int = 2,
                      mode: str = MODE_LANCZOS_X2) -> dict[str, Any]:
    """Upscale LIDAR HR (déjà fin) par x2 max pour préserver fidélité."""
    mark_call(ENGINE_NAME)
    out = upscale_dem_hr(lidar_grid, factor=factor, mode=mode)
    out["doctrine_applied"] = "LIDAR_UPSCALE_X2"
    return out


def export_array_as_png_base64(arr: np.ndarray) -> str:
    """Exporte une matrice 2D normalisée en PNG base64 pour visualisation."""
    a_min, a_max = float(np.nanmin(arr)), float(np.nanmax(arr))
    span = max(1e-9, a_max - a_min)
    norm = ((arr - a_min) / span * 255.0).astype(np.uint8)
    img = Image.fromarray(norm, mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")
