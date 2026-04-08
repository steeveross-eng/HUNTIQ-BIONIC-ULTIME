"""
Critical Sites — K3 v3.0.0
============================

BCE-4X ULTIME ABSOLU x3 | STEEVE-MAX
Expose les sites critiques par espece.
LECTURE SEULE sur knowledge.json v3.0.0.
"""
from typing import Optional
from modules.bionic_knowledge_engine.knowledge_provider import _load_knowledge
from modules.species_engine.resolver import resolve


def get_critical_sites(species_input: str) -> Optional[dict]:
    """Retourne les sites critiques pour une espece."""
    _, k2_id = resolve(species_input)
    if k2_id is None:
        return None

    k = _load_knowledge()
    cs = k.get("critical_sites", {})
    data = cs.get(k2_id)
    if data is None:
        return None

    return {
        "species_id": k2_id,
        "sites": data,
        "_source": "K3_critical_sites",
    }
