"""
Climate Sensitivity — K3 v3.0.0
=================================

BCE-4X ULTIME ABSOLU x3 | STEEVE-MAX
Expose les donnees de sensibilite climatique par espece.
LECTURE SEULE sur knowledge.json v3.0.0.
"""
from typing import Optional
from modules.bionic_knowledge_engine.knowledge_provider import _load_knowledge
from modules.species_engine.resolver import resolve


def get_climate(species_input: str) -> Optional[dict]:
    """Retourne la sensibilite climatique pour une espece."""
    _, k2_id = resolve(species_input)
    if k2_id is None:
        return None

    k = _load_knowledge()
    cs = k.get("climate_sensitivity", {})
    data = cs.get(k2_id)
    if data is None:
        return None

    return {
        "species_id": k2_id,
        "climate_sensitivity": data,
        "_source": "K3_climate_sensitivity",
    }


def get_snow_tolerance(species_input: str) -> Optional[dict]:
    """Retourne la tolerance a la neige pour une espece."""
    _, k2_id = resolve(species_input)
    if k2_id is None:
        return None

    k = _load_knowledge()
    st = k.get("snow_tolerance", {})
    data = st.get(k2_id)
    if data is None:
        return None

    return {
        "species_id": k2_id,
        "snow_tolerance": data,
        "_source": "K3_snow_tolerance",
    }
