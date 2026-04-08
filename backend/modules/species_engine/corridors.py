"""
Dynamic Corridors — S5
========================

K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
Expose les corridors dynamiques K2.2 par espece et saison.
LECTURE SEULE sur knowledge.json.
"""
from typing import Optional
from modules.bionic_knowledge_engine.knowledge_provider import _load_knowledge
from modules.species_engine.resolver import resolve


def get_corridors(species_input: str, season: str = None) -> Optional[dict]:
    """Retourne les corridors dynamiques K2.2 pour une espece.

    Args:
        species_input: Tout identifiant d'espece
        season: Filtre optionnel par saison

    Returns:
        Liste de corridors ou None si pas de K2
    """
    _, k2_id = resolve(species_input)
    if k2_id is None:
        return None

    k = _load_knowledge()
    dc = k.get("dynamic_corridors", {})
    models = dc.get("models", [])

    # Filtrer par espece
    species_corridors = [m for m in models if k2_id in m.get("species", [])]

    # Filtre optionnel par saison
    if season:
        season_map = {
            "printemps": "spring", "spring": "spring",
            "ete": "summer", "summer": "summer",
            "automne": "fall", "fall": "fall",
            "hiver": "winter", "winter": "winter",
        }
        season_en = season_map.get(season.lower(), season.lower())
        species_corridors = [c for c in species_corridors if c.get("season") == season_en]

    return {
        "species_id": k2_id,
        "total": len(species_corridors),
        "corridors": species_corridors,
        "_source": "K2.2_dynamic_corridors",
    }
