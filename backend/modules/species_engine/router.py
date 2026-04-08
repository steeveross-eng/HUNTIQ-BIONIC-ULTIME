"""
Species Engine Router — S1
============================

K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
ZERO_INTERPRETATION | ZERO_REGRESSION | ZERO_LOSS | TRACEABILITY

Router FastAPI pour le Species Engine.
Tous les endpoints sont en LECTURE SEULE.
Aucune modification des moteurs existants.

Prefix: /api/v6/species-engine
"""
import logging
from fastapi import APIRouter, Query
from typing import Optional

from modules.species_engine.resolver import (
    resolve,
    has_k2_data,
    get_all_species_ids,
    get_k2_species_ids,
)
from modules.species_engine.bridge import get_full_profile, get_registry
from modules.species_engine.seasonal import get_seasonal_behavior, get_all_seasonal
from modules.species_engine.corridors import get_corridors
from modules.species_engine.zones import get_zones, get_all_zones
from modules.species_engine.cross_species import get_cross_inference_all, get_cross_inference_pair
from modules.species_engine.nutrition import get_nutrition
from modules.species_engine.climate import get_climate, get_snow_tolerance
from modules.species_engine.critical_sites import get_critical_sites

logger = logging.getLogger("species_engine.router")

router = APIRouter(
    prefix="/api/v6/species-engine",
    tags=["Species Engine K3"],
)


# ============================================================
# S1: HEALTH + REGISTRY
# ============================================================

@router.get("/health")
async def health():
    """Sante du Species Engine."""
    return {
        "status": "operational",
        "engine": "species_engine_k3",
        "version": "1.0.0",
        "protocol": "BCE-4X ULTIME ABSOLU",
        "authority": "COMMANDANT STEEVE-MAX",
        "total_species": len(get_all_species_ids()),
        "k2_species": len(get_k2_species_ids()),
        "modules": ["resolver", "bridge", "seasonal", "corridors", "zones", "cross_species", "nutrition"],
        "phases": "S0-S9",
    }


@router.get("/registry")
async def registry():
    """Registre complet des 8 especes avec statut K2."""
    reg = get_registry()
    return {
        "status": "success",
        "total": len(reg),
        "k2_available": sum(1 for r in reg if r["has_k2_data"]),
        "species": reg,
        "protocol": "BCE-4X ULTIME ABSOLU",
    }


# ============================================================
# S3: FULL PROFILE (Knowledge Bridge)
# ============================================================

@router.get("/{species_id}/full-profile")
async def full_profile(species_id: str, season: str = "automne"):
    """Profil unifie complet (operationnel + K2 scientifique)."""
    profile = get_full_profile(species_id, season)
    if profile is None:
        return {
            "status": "error",
            "message": f"Espece '{species_id}' non trouvee",
            "available": get_all_species_ids(),
        }
    return {
        "status": "success",
        "profile": profile,
        "protocol": "BCE-4X ULTIME ABSOLU",
    }


# ============================================================
# S4: SEASONAL INTELLIGENCE
# ============================================================

@router.get("/{species_id}/seasonal/{season}")
async def seasonal_behavior(species_id: str, season: str):
    """Comportement saisonnier K2.1 pour une espece et saison."""
    data = get_seasonal_behavior(species_id, season)
    if data is None:
        k2 = has_k2_data(species_id)
        if not k2:
            return {
                "status": "error",
                "message": f"Pas de donnees K2 pour '{species_id}'",
                "k2_species": get_k2_species_ids(),
            }
        return {
            "status": "error",
            "message": f"Saison '{season}' invalide",
            "valid_seasons": ["printemps", "ete", "automne", "hiver"],
        }
    return {"status": "success", **data}


@router.get("/{species_id}/seasonal")
async def seasonal_all(species_id: str):
    """Comportements des 4 saisons pour une espece."""
    data = get_all_seasonal(species_id)
    if data is None:
        return {
            "status": "error",
            "message": f"Pas de donnees K2 pour '{species_id}'",
            "k2_species": get_k2_species_ids(),
        }
    return {"status": "success", **data}


# ============================================================
# S5: DYNAMIC CORRIDORS
# ============================================================

@router.get("/{species_id}/corridors")
async def species_corridors(species_id: str, season: Optional[str] = None):
    """Corridors dynamiques K2.2 pour une espece."""
    data = get_corridors(species_id, season)
    if data is None:
        return {
            "status": "error",
            "message": f"Pas de donnees K2 pour '{species_id}'",
            "k2_species": get_k2_species_ids(),
        }
    return {"status": "success", **data}


# ============================================================
# S6: ECOLOGICAL ZONES
# ============================================================

@router.get("/{species_id}/zones")
async def species_zones(species_id: str):
    """Zones ecologiques K2.4 ou l'espece est dominante."""
    data = get_zones(species_id)
    if data is None:
        return {
            "status": "error",
            "message": f"Pas de donnees K2 pour '{species_id}'",
            "k2_species": get_k2_species_ids(),
        }
    return {"status": "success", **data}


@router.get("/zones/all")
async def all_zones():
    """Toutes les zones ecologiques K2.4."""
    data = get_all_zones()
    return {"status": "success", **data}


# ============================================================
# S7: CROSS-SPECIES INTELLIGENCE
# ============================================================

@router.get("/cross-inference")
async def cross_inference():
    """Matrice complete d'inferences inter-especes K2.5."""
    data = get_cross_inference_all()
    return {"status": "success", **data}


@router.get("/cross-inference/{species_a}/{species_b}")
async def cross_inference_pair(species_a: str, species_b: str):
    """Inference entre deux especes specifiques."""
    data = get_cross_inference_pair(species_a, species_b)
    if data is None:
        return {
            "status": "error",
            "message": f"Paire invalide : '{species_a}' / '{species_b}'",
            "k2_species": get_k2_species_ids(),
        }
    return {"status": "success", **data}


# ============================================================
# S8: ADVANCED NUTRITION
# ============================================================

@router.get("/{species_id}/nutrition/{season}")
async def species_nutrition(species_id: str, season: str):
    """Nutrition avancee K2.3 pour une espece et saison."""
    data = get_nutrition(species_id, season)
    if data is None:
        k2 = has_k2_data(species_id)
        if not k2:
            return {
                "status": "error",
                "message": f"Pas de donnees K2 pour '{species_id}'",
                "k2_species": get_k2_species_ids(),
            }
        return {
            "status": "error",
            "message": f"Saison '{season}' invalide",
            "valid_seasons": ["printemps", "ete", "automne", "hiver"],
        }
    return {"status": "success", **data}


# ============================================================
# K3 v3.0.0: CLIMATE SENSITIVITY
# ============================================================

@router.get("/{species_id}/climate")
async def species_climate(species_id: str):
    """Sensibilite climatique et tolerance a la neige pour une espece."""
    climate = get_climate(species_id)
    snow = get_snow_tolerance(species_id)
    if climate is None and snow is None:
        return {
            "status": "error",
            "message": f"Pas de donnees climatiques pour '{species_id}'",
            "k2_species": get_k2_species_ids(),
        }
    result = {"status": "success", "species_id": climate["species_id"] if climate else snow["species_id"]}
    if climate:
        result["climate_sensitivity"] = climate["climate_sensitivity"]
    if snow:
        result["snow_tolerance"] = snow["snow_tolerance"]
    result["_source"] = "K3_climate_snow"
    return result


# ============================================================
# K3 v3.0.0: CRITICAL SITES
# ============================================================

@router.get("/{species_id}/critical-sites")
async def species_critical_sites(species_id: str):
    """Sites critiques pour une espece."""
    data = get_critical_sites(species_id)
    if data is None:
        return {
            "status": "error",
            "message": f"Pas de donnees de sites critiques pour '{species_id}'",
            "k2_species": get_k2_species_ids(),
        }
    return {"status": "success", **data}


logger.info("Species Engine K3 v3.0.0 loaded — 14 endpoints, 8 species, K2+ bridge active")
