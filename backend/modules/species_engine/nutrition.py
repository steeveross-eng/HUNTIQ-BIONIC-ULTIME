"""
Advanced Nutrition — S8
========================

K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
Expose la nutrition avancee K2.3 (oligo-elements) et besoins
sodium saisonniers par espece.
LECTURE SEULE sur knowledge.json.
"""
from typing import Optional
from modules.bionic_knowledge_engine.knowledge_provider import (
    _load_knowledge,
    get_species_nutrition_needs,
)
from modules.species_engine.resolver import resolve


_SEASON_MAP = {
    "printemps": "spring", "spring": "spring",
    "ete": "summer", "summer": "summer",
    "automne": "fall", "fall": "fall",
    "hiver": "winter", "winter": "winter",
}


def get_nutrition(species_input: str, season: str) -> Optional[dict]:
    """Retourne la nutrition avancee K2.3 pour une espece et saison.

    Inclut : besoins sodium, ratio Ca:P, oligo-elements (Se, Zn, Cu, Mn)

    Args:
        species_input: Tout identifiant d'espece
        season: Saison (FR ou EN)

    Returns:
        Donnees nutritionnelles completes ou None
    """
    _, k2_id = resolve(species_input)
    if k2_id is None:
        return None

    season_en = _SEASON_MAP.get(season.lower())
    if season_en is None:
        return None

    # Utilise le provider existant pour sodium + Ca:P + trace
    nutrition = get_species_nutrition_needs(k2_id, season_en)
    if not nutrition:
        return None

    # Ajouter le contexte sodium saisonnier complet
    k = _load_knowledge()
    sodium_data = k.get("nutrition", {}).get("sodium", {}).get("data", {})
    species_sodium = sodium_data.get(k2_id, {})

    return {
        "species_id": k2_id,
        "season": season_en,
        "sodium_current": nutrition.get("sodium"),
        "sodium_all_seasons": species_sodium,
        "calcium_phosphorus": nutrition.get("calcium_phosphorus"),
        "trace_elements": nutrition.get("trace_elements"),
        "_source": "K2.3_advanced_nutrition",
    }
