"""
Species ID Resolver — S2
=========================

K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
ZERO_INTERPRETATION | ZERO_REGRESSION | ZERO_LOSS | TRACEABILITY

Resolveur unifie d'identifiants especes.
Mappe entre les referentiels operationnel (species_profiles.py)
et scientifique (knowledge.json K2).

Accepte : ID operationnel, ID scientifique, nom FR, nom EN, nom latin.
Retourne : (operational_id, knowledge_id | None)
"""
from typing import Optional, Tuple

# Mapping bidirectionnel operationnel <-> knowledge
_OP_TO_K2 = {
    "orignal": "moose",
    "cerf_virginie": "deer",
    "ours_noir": "bear",
    "wapiti": "elk",
}

_K2_TO_OP = {v: k for k, v in _OP_TO_K2.items()}

# Alias complet : tout identifiant possible -> operational_id
_ALIAS_MAP = {
    # Orignal / Moose
    "orignal": "orignal",
    "moose": "orignal",
    "alces alces": "orignal",
    "alces": "orignal",

    # Cerf de Virginie / Deer
    "cerf_virginie": "cerf_virginie",
    "cerf": "cerf_virginie",
    "chevreuil": "cerf_virginie",
    "deer": "cerf_virginie",
    "white-tailed deer": "cerf_virginie",
    "odocoileus virginianus": "cerf_virginie",

    # Ours noir / Bear
    "ours_noir": "ours_noir",
    "ours": "ours_noir",
    "bear": "ours_noir",
    "black bear": "ours_noir",
    "ursus americanus": "ours_noir",

    # Wapiti / Elk
    "wapiti": "wapiti",
    "elk": "wapiti",
    "cervus canadensis": "wapiti",

    # Dindon sauvage (pas de K2)
    "dindon_sauvage": "dindon_sauvage",
    "dindon": "dindon_sauvage",
    "wild turkey": "dindon_sauvage",
    "turkey": "dindon_sauvage",
    "meleagris gallopavo": "dindon_sauvage",

    # Caribou (pas de K2)
    "caribou": "caribou",
    "rangifer tarandus caribou": "caribou",
    "rangifer tarandus": "caribou",

    # Cerf mulet (pas de K2)
    "cerf_mulet": "cerf_mulet",
    "mule deer": "cerf_mulet",
    "odocoileus hemionus": "cerf_mulet",

    # Pronghorn (pas de K2)
    "pronghorn": "pronghorn",
    "antilocapre": "pronghorn",
    "antilocapra americana": "pronghorn",
}


def resolve(species_input: str) -> Tuple[Optional[str], Optional[str]]:
    """Resout un identifiant d'espece vers (operational_id, knowledge_id).

    Args:
        species_input: Tout identifiant (FR, EN, latin, alias)

    Returns:
        (operational_id, knowledge_id) ou (None, None) si inconnu.
        knowledge_id est None si l'espece n'a pas de donnees K2.
    """
    key = species_input.strip().lower()
    op_id = _ALIAS_MAP.get(key)
    if op_id is None:
        return (None, None)
    k2_id = _OP_TO_K2.get(op_id)
    return (op_id, k2_id)


def get_operational_id(species_input: str) -> Optional[str]:
    """Retourne l'ID operationnel ou None."""
    op_id, _ = resolve(species_input)
    return op_id


def get_knowledge_id(species_input: str) -> Optional[str]:
    """Retourne l'ID knowledge (K2) ou None."""
    _, k2_id = resolve(species_input)
    return k2_id


def has_k2_data(species_input: str) -> bool:
    """Verifie si l'espece possede des donnees K2."""
    _, k2_id = resolve(species_input)
    return k2_id is not None


def get_all_species_ids() -> list:
    """Retourne tous les IDs operationnels."""
    return list(_OP_TO_K2.keys()) + ["dindon_sauvage", "caribou", "cerf_mulet", "pronghorn"]


def get_k2_species_ids() -> list:
    """Retourne les IDs operationnels ayant des donnees K2."""
    return list(_OP_TO_K2.keys())
