"""
Seasonal Intelligence — S4
============================

K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
Expose les comportements saisonniers K2.1 par espece.
LECTURE SEULE sur knowledge.json.
"""
from typing import Optional
from modules.bionic_knowledge_engine.knowledge_provider import _load_knowledge
from modules.species_engine.resolver import resolve


_SEASON_MAP = {
    "printemps": "spring", "spring": "spring",
    "ete": "summer", "summer": "summer",
    "automne": "fall", "fall": "fall",
    "hiver": "winter", "winter": "winter",
}


def get_seasonal_behavior(species_input: str, season: str) -> Optional[dict]:
    """Retourne le comportement saisonnier K2.1 pour une espece et saison.

    Args:
        species_input: Tout identifiant d'espece
        season: Saison (FR ou EN)

    Returns:
        Donnees comportementales saisonnieres ou None
    """
    _, k2_id = resolve(species_input)
    if k2_id is None:
        return None

    k = _load_knowledge()
    sb = k.get("seasonal_behaviors", {})
    species_data = sb.get(k2_id)
    if species_data is None:
        return None

    season_en = _SEASON_MAP.get(season.lower())
    if season_en is None:
        return None

    behavior = species_data.get(season_en)
    if behavior is None:
        return None

    return {
        "species_id": k2_id,
        "season": season_en,
        "season_fr": season.lower() if season.lower() in ["printemps", "ete", "automne", "hiver"] else season_en,
        "behavior": behavior,
        "_source": "K2.1_seasonal_behaviors",
    }


def get_all_seasonal(species_input: str) -> Optional[dict]:
    """Retourne les comportements des 4 saisons pour une espece."""
    _, k2_id = resolve(species_input)
    if k2_id is None:
        return None

    k = _load_knowledge()
    sb = k.get("seasonal_behaviors", {})
    species_data = sb.get(k2_id)
    if species_data is None:
        return None

    return {
        "species_id": k2_id,
        "seasons": {s: species_data.get(s) for s in ["spring", "summer", "fall", "winter"]},
        "_source": "K2.1_seasonal_behaviors",
    }
