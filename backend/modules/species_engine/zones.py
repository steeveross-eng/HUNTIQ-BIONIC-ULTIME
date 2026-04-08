"""
Ecological Zones — S6
======================

K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
Expose les zones ecologiques K2.4 par espece.
LECTURE SEULE sur knowledge.json.
"""
from typing import Optional
from modules.bionic_knowledge_engine.knowledge_provider import _load_knowledge
from modules.species_engine.resolver import resolve


def get_zones(species_input: str) -> Optional[dict]:
    """Retourne les zones ecologiques K2.4 ou l'espece est dominante.

    Args:
        species_input: Tout identifiant d'espece

    Returns:
        Liste de zones ecologiques ou None si pas de K2
    """
    _, k2_id = resolve(species_input)
    if k2_id is None:
        return None

    k = _load_knowledge()
    ez = k.get("ecological_zones", {})
    all_zones = ez.get("zones", [])

    # Filtrer les zones ou cette espece est dominante
    species_zones = [z for z in all_zones if k2_id in z.get("dominant_species", [])]

    return {
        "species_id": k2_id,
        "total": len(species_zones),
        "zones": species_zones,
        "_source": "K2.4_ecological_zones",
    }


def get_all_zones() -> dict:
    """Retourne toutes les zones ecologiques."""
    k = _load_knowledge()
    ez = k.get("ecological_zones", {})
    zones = ez.get("zones", [])
    return {
        "total": len(zones),
        "zones": zones,
        "_source": "K2.4_ecological_zones",
    }
