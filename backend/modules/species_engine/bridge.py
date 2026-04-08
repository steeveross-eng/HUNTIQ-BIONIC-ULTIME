"""
Knowledge Bridge — S3
======================

K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
ZERO_INTERPRETATION | ZERO_REGRESSION | ZERO_LOSS | TRACEABILITY

Fusionne les profils operationnels (species_profiles.py) avec les
donnees scientifiques K2 (knowledge.json) en un profil unifie.
LECTURE SEULE sur les deux referentiels.
"""
from typing import Optional

from modules.bionic_ecological_engine.species_profiles import get_species_profile
from modules.bionic_knowledge_engine.knowledge_provider import (
    get_species_data,
    get_species_nutrition_needs,
    get_corridors_for_species,
    get_knowledge_meta,
)
from modules.species_engine.resolver import resolve, has_k2_data


def get_full_profile(species_input: str, season: str = "automne") -> Optional[dict]:
    """Construit le profil unifie complet d'une espece.

    Fusionne :
    - Profil operationnel (ecology, diet, behavior, predictions, hunting)
    - Donnees K2 scientifiques (weight, home_range, temperature, habitat,
      breeding, nutrition, corridors) si disponibles

    ZERO modification des donnees source. Assemblage ADDITIF uniquement.

    Args:
        species_input: Tout identifiant d'espece
        season: Saison pour les donnees nutritionnelles

    Returns:
        Profil unifie ou None si espece inconnue
    """
    op_id, k2_id = resolve(species_input)
    if op_id is None:
        return None

    # 1. Profil operationnel (toujours present)
    op_profile = get_species_profile(op_id)

    # 2. Base du profil unifie
    unified = {
        "species_id": op_id,
        "name_fr": op_profile.get("name_fr", ""),
        "name_en": op_profile.get("name_en", ""),
        "name_latin": op_profile.get("name_latin", ""),
        "category": op_profile.get("category", ""),
        "icon": op_profile.get("icon", ""),
        "color": op_profile.get("color", ""),
        "map_color": op_profile.get("map_color", ""),

        # Profil operationnel complet
        "operational": {
            "ecology": op_profile.get("ecology", {}),
            "diet": op_profile.get("diet", {}),
            "behavior": op_profile.get("behavior", {}),
            "predictions": op_profile.get("predictions", {}),
            "hunting": op_profile.get("hunting", {}),
        },

        # Statut K2
        "has_k2_data": k2_id is not None,
        "knowledge_id": k2_id,
    }

    # 3. Donnees K2 scientifiques (si disponibles)
    if k2_id is not None:
        k2_species = get_species_data(k2_id)
        k2_nutrition = get_species_nutrition_needs(k2_id, season)
        k2_corridors = get_corridors_for_species(k2_id)
        k2_meta = get_knowledge_meta()

        unified["scientific"] = {
            "weight_kg": k2_species.get("weight_kg") if k2_species else None,
            "home_range_km2": k2_species.get("home_range_km2") if k2_species else None,
            "temperature_range": k2_species.get("temperature_range") if k2_species else None,
            "habitat_preferences": k2_species.get("habitat_preferences", []) if k2_species else [],
            "human_tolerance": k2_species.get("human_tolerance") if k2_species else None,
            "breeding": k2_species.get("breeding") if k2_species else None,
        }

        unified["scientific_nutrition"] = k2_nutrition
        unified["scientific_corridors"] = k2_corridors

        unified["knowledge_meta"] = {
            "version": k2_meta.get("version"),
            "total_sources": k2_meta.get("total_sources"),
            "evidence_coverage": k2_meta.get("evidence_coverage"),
        }
    else:
        unified["scientific"] = None
        unified["scientific_nutrition"] = None
        unified["scientific_corridors"] = None
        unified["knowledge_meta"] = None

    return unified


def get_registry() -> list:
    """Retourne le registre complet des especes avec statut K2."""
    from modules.species_engine.resolver import get_all_species_ids
    from modules.bionic_ecological_engine.species_profiles import SPECIES_PROFILES

    registry = []
    for op_id in get_all_species_ids():
        profile = SPECIES_PROFILES.get(op_id, {})
        k2_available = has_k2_data(op_id)
        _, k2_id = resolve(op_id)
        registry.append({
            "species_id": op_id,
            "name_fr": profile.get("name_fr", op_id),
            "name_en": profile.get("name_en", ""),
            "name_latin": profile.get("name_latin", ""),
            "category": profile.get("category", ""),
            "has_k2_data": k2_available,
            "knowledge_id": k2_id,
        })
    return registry
