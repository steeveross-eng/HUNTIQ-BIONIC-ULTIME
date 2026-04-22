"""
ENGINE_WILDLIFE_BEHAVIOR_Ω — Implémentation X200 P0
=====================================================
Phase     : X200-P0-ACTIVATION — VERSION_V31_CORE_PREPARATOIRE_Ω
Priorité  : P0 #1 (CERF — critique locomotion_cerf_profil)

RESTAURATION V7 ULTIME : importe `CORRIDOR_PROFILES` depuis corridors_v10.species_profiles
Réintègre le profil CERF (absent en X180) + 4 autres espèces V7.
"""
from __future__ import annotations

from typing import Dict, Any, List
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# ═══════════════════════════════════════════════════════════════════════
# FEATURE FLAG — ACTIVÉ X200-P0 SOUS ORDRE COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
FEATURE_FLAG_ACTIVE: bool = True

ENGINE_ID = "ENGINE_WILDLIFE_BEHAVIOR_Ω"
PHASE = "X200-P0-ACTIVATION"


def _load_v7_profiles() -> Dict[str, Dict[str, Any]]:
    """Import lazy des profils V7 ULTIME canoniques (corridors_v10)."""
    try:
        from core.scoring_pipeline.corridors_v10.species_profiles import CORRIDOR_PROFILES
        return CORRIDOR_PROFILES
    except Exception as e:
        return {"_error": str(e)}


def get_species_profile(species: str) -> Dict[str, Any]:
    """Retourne le profil comportemental V7 pour une espèce.

    Espèces supportées : CERF (restauré), ORIGNAL, OURS, DINDON, CHEVREUIL.
    """
    profiles = _load_v7_profiles()
    key = (species or "").upper().strip()
    # Alias : chevreuil → cerf (V7 utilise CERF canonique)
    if key == "CHEVREUIL":
        key = "CERF"
    profile = profiles.get(key)
    if not profile:
        return {"available": False, "species": species, "reason": "profile_not_found_in_v7"}
    return {"available": True, "species": key.lower(), "profile": profile,
            "source": "corridors_v10.species_profiles (V7 ULTIME)"}


def locomotion_constraints(species: str, season: str = "automne") -> Dict[str, Any]:
    """Contraintes de locomotion pour un corridor, avec modulation saisonnière V7."""
    res = get_species_profile(species)
    if not res.get("available"):
        return res
    p = res["profile"]
    saison = p.get("saisonnalite", {}).get(season, {})
    return {
        "species": res["species"],
        "season": season,
        "angle_max_deg": 50 if p.get("style_deplacement") == "opportuniste" else (
            35 if p.get("style_deplacement") == "lineaire" else 45
        ),
        "segment_max_m": p.get("largeur_corridor_m", 150) / 7.5,  # largeur→segment
        "water_affinity": p.get("affinite_hydro"),
        "forest_preference": p.get("preference_forestiere"),
        "pressure_sensitivity": p.get("sensibilite_pression"),
        "road_avoidance_m": p.get("distance_route_evitement_m"),
        "building_avoidance_m": p.get("distance_batiment_evitement_m"),
        "style": p.get("style_deplacement"),
        "speed": p.get("vitesse_deplacement"),
        "slope_optimal_deg": p.get("pente_optimale_deg"),
        "slope_max_deg": p.get("pente_max_deg"),
        "season_mobility": saison.get("mobilite"),
        "season_cover": saison.get("couvert"),
        "season_hydro": saison.get("hydro"),
        "v7_restored": True,
    }


# ═══════════════════════════════════════════════════════════════════════
# ROUTER FASTAPI
# ═══════════════════════════════════════════════════════════════════════
router = APIRouter(
    prefix="/api/v7-ultime/wildlife-behavior",
    tags=["ENGINE_WILDLIFE_BEHAVIOR_Ω_X200_P0"],
)


@router.get("/status")
async def status():
    profiles = _load_v7_profiles()
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "phase": PHASE,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "species_restored": sorted(profiles.keys()) if "_error" not in profiles else [],
        "cerf_restored": "CERF" in profiles,
        "v7_source": "core/scoring_pipeline/corridors_v10/species_profiles.py",
    })


@router.post("/compute")
async def compute(payload: dict = None):
    payload = payload or {}
    species = payload.get("species", "CERF")
    season = payload.get("season", "automne")
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "phase": PHASE,
        "profile": get_species_profile(species),
        "constraints": locomotion_constraints(species, season),
    })
