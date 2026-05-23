"""
ENGINE-IA-VISION-REGISTRY-Ω — Registre préparatoire IA Vision
==============================================================
Phase XI-SUPRA-K — expose `/app/registry/ia_vision/ia_vision_registry_v1.json`
pour préparer l'intégration IA Vision (NASA EarthData + LIDAR WCS 1 m).

Endpoints :
  GET /api/v20/territoire/ia-vision/status
  GET /api/v20/territoire/ia-vision/validate
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from engines.v8_institutional.engine_science_omega import register_engine, mark_call

# P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω (2026-05-23) — Registry HR-ready (additif read-only).
try:
    from engines.v8_institutional import ndvi_lidar_p0_registry_omega as NDVI_LIDAR_P0  # noqa: F401
except ImportError:
    NDVI_LIDAR_P0 = None  # type: ignore

ENGINE_NAME = "ENGINE-IA-VISION-REGISTRY-Ω"
ENGINE_VERSION = "V1.0-PHASE-XI-SUPRA-K-2026-04"

register_engine(
    ENGINE_NAME,
    ENGINE_VERSION,
    "Registre préparatoire IA Vision (NASA + LIDAR) — schéma + endpoints",
    "BIO-SYSTEME",
    ["ENGINE-IA-VISION-ECOLOGIQUE-Ω"],
)

router = APIRouter(prefix="/api/v20/territoire/ia-vision", tags=["V20 IA-Vision"])

REGISTRY_DIR = Path("/app/registry/ia_vision")
REGISTRY_FILE = REGISTRY_DIR / "ia_vision_registry_v1.json"

REQUIRED_KEYS = ["data_sources", "outputs", "validation_rules", "integration_points"]
REQUIRED_DATA_SOURCES = {"NASA_EARTHDATA", "LIDAR_WCS_1M"}


def _load_registry() -> dict[str, Any]:
    if not REGISTRY_FILE.exists():
        raise FileNotFoundError(f"Registre IA Vision manquant: {REGISTRY_FILE}")
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def validate_registry() -> dict:
    mark_call(ENGINE_NAME)
    try:
        reg = _load_registry()
    except FileNotFoundError as e:
        return {"ok": False, "error": str(e), "engine": ENGINE_NAME}

    violations: list[dict] = []
    for k in REQUIRED_KEYS:
        if k not in reg:
            violations.append({"rule": f"missing_{k}"})

    sources_present = {s.get("id") for s in reg.get("data_sources", [])}
    missing_sources = REQUIRED_DATA_SOURCES - sources_present
    if missing_sources:
        violations.append({
            "rule": "missing_data_sources",
            "detail": sorted(missing_sources),
        })

    outputs = reg.get("outputs", {})
    if "zones_probables" not in outputs:
        violations.append({"rule": "missing_outputs.zones_probables"})

    return {
        "ok": len(violations) == 0,
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "registry_version": reg.get("version"),
        "registry_status": reg.get("status"),
        "data_sources_present": sorted(sources_present),
        "violations": violations,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/status")
async def ia_vision_status():
    mark_call(ENGINE_NAME)
    exists = REGISTRY_FILE.exists()
    info: dict[str, Any] = {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "registry_path": str(REGISTRY_FILE),
        "registry_exists": exists,
    }
    if exists:
        reg = _load_registry()
        info.update({
            "registry_version": reg.get("version"),
            "status": reg.get("status"),
            "engine_backing": reg.get("engine_backing"),
            "data_sources": [s.get("id") for s in reg.get("data_sources", [])],
            "sealed_at": reg.get("sealed_at"),
            "preparation_status": reg.get("preparation_status"),
        })
    return info


@router.get("/validate")
async def ia_vision_validate():
    return validate_registry()
