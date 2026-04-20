"""
ENGINE-SPECIES-PROFILES-Ω — Registre dynamique des profils d'espèces
=====================================================================
Phase XI-SUPRA-K — extraction dynamique des profils biologiques depuis
`/app/registry/species_profiles_v1.json` (élimination du codage en dur).

Endpoints :
  GET /api/v20/territoire/species-profiles/status
  GET /api/v20/territoire/species-profiles/validate
  GET /api/v20/territoire/species-profiles/{species_key}
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-SPECIES-PROFILES-Ω"
ENGINE_VERSION = "V1.0-PHASE-XI-SUPRA-K-2026-04"

register_engine(
    ENGINE_NAME,
    ENGINE_VERSION,
    "Registre dynamique des profils d'espèces (JSON sourcé, non codé en dur)",
    "BIO-SYSTEME",
    ["ENGINE-ESPECE-Ω", "ENGINE-IA-CORRIDORS-Ω"],
)

router = APIRouter(prefix="/api/v20/territoire/species-profiles", tags=["V20 Species-Profiles"])

REGISTRY_PATH = Path("/app/registry/species_profiles_v1.json")

# Clés obligatoires pour validation stricte
REQUIRED_TOP_KEYS = ["habitat", "movement", "hydrology", "nutrition"]
REQUIRED_HABITAT_KEYS = ["preferred", "canopy_preference"]
REQUIRED_MOVEMENT_KEYS = ["corridor_style", "typical_length_m"]
REQUIRED_HYDRO_KEYS = ["water_dist_min_m", "water_dist_max_m"]


def _load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Registry species_profiles manquant: {REGISTRY_PATH}")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def get_species_profile(species_key: str) -> dict | None:
    mark_call(ENGINE_NAME)
    reg = _load_registry()
    return reg.get("species", {}).get(species_key)


def list_species() -> list[str]:
    mark_call(ENGINE_NAME)
    reg = _load_registry()
    return sorted(list(reg.get("species", {}).keys()))


def validate_registry() -> dict:
    """Valide la structure complète du registre."""
    mark_call(ENGINE_NAME)
    try:
        reg = _load_registry()
    except FileNotFoundError as e:
        return {"ok": False, "error": str(e), "engine": ENGINE_NAME}

    violations: list[dict] = []
    species = reg.get("species") or {}

    if not species:
        violations.append({"rule": "species_not_empty", "detail": "aucune espèce"})

    for key, profile in species.items():
        for rk in REQUIRED_TOP_KEYS:
            if rk not in profile:
                violations.append({"species": key, "rule": f"missing_{rk}"})
        habitat = profile.get("habitat", {})
        for rk in REQUIRED_HABITAT_KEYS:
            if rk not in habitat:
                violations.append({"species": key, "rule": f"missing_habitat_{rk}"})
        movement = profile.get("movement", {})
        for rk in REQUIRED_MOVEMENT_KEYS:
            if rk not in movement:
                violations.append({"species": key, "rule": f"missing_movement_{rk}"})
        hydro = profile.get("hydrology", {})
        for rk in REQUIRED_HYDRO_KEYS:
            if rk not in hydro:
                violations.append({"species": key, "rule": f"missing_hydrology_{rk}"})

    return {
        "ok": len(violations) == 0,
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "registry_version": reg.get("version"),
        "species_count": len(species),
        "species_keys": sorted(species.keys()),
        "violations": violations,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/status")
async def species_profiles_status():
    mark_call(ENGINE_NAME)
    exists = REGISTRY_PATH.exists()
    info: dict[str, Any] = {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "registry_path": str(REGISTRY_PATH),
        "registry_exists": exists,
    }
    if exists:
        reg = _load_registry()
        info.update({
            "registry_version": reg.get("version"),
            "species_count": len(reg.get("species", {})),
            "species_keys": sorted(list(reg.get("species", {}).keys())),
            "sealed_at": reg.get("sealed_at"),
            "source_of_truth": reg.get("source_of_truth"),
        })
    return info


@router.get("/validate")
async def species_profiles_validate():
    return validate_registry()


@router.get("/{species_key}")
async def species_profiles_get(species_key: str):
    profile = get_species_profile(species_key)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Espèce inconnue: {species_key}")
    return {"species_key": species_key, "profile": profile, "engine": ENGINE_NAME}
