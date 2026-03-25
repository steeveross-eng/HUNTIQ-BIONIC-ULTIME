"""
CORE Scoring Pipeline — Registre des especes
================================================
Directive x3205. Source unique de verite pour les especes supportees.
BCE-4X: Aucune modification des identifiants ou des ordres existants.

NOTE SUR L'ORDRE:
  Les moteurs individuels preservent leur propre SPECIES_LIST derivee
  de leurs profils (l'ordre peut varier). Ce registre definit la
  reference canonique.
"""

# ══════════════════════════════════════════════════════════════════
# REGISTRE CANONIQUE DES ESPECES
# ══════════════════════════════════════════════════════════════════

SPECIES_REGISTRY = {
    "CERF": {
        "id": "cerf",
        "nom_fr": "Cerf de Virginie",
        "nom_scientifique": "Odocoileus virginianus",
        "frontend_ids": ["chevreuil", "cerf", "tous"],
        "salines_enabled": True,
    },
    "ORIGNAL": {
        "id": "orignal",
        "nom_fr": "Orignal",
        "nom_scientifique": "Alces americanus",
        "frontend_ids": ["orignal"],
        "salines_enabled": True,
    },
    "OURS": {
        "id": "ours",
        "nom_fr": "Ours noir",
        "nom_scientifique": "Ursus americanus",
        "frontend_ids": ["ours_noir", "ours"],
        "salines_enabled": False,
    },
    "DINDON": {
        "id": "dindon",
        "nom_fr": "Dindon sauvage",
        "nom_scientifique": "Meleagris gallopavo",
        "frontend_ids": ["dindon_sauvage", "dindon"],
        "salines_enabled": False,
    },
    "WAPITI": {
        "id": "wapiti",
        "nom_fr": "Wapiti",
        "nom_scientifique": "Cervus canadensis",
        "frontend_ids": ["wapiti"],
        "salines_enabled": True,
    },
}

# Liste canonique (ordre: CERF, ORIGNAL, OURS, DINDON, WAPITI)
SPECIES_LIST = list(SPECIES_REGISTRY.keys())

# Mapping frontend → backend (tous les alias connus)
FRONTEND_SPECIES_MAP = {}
for sp_id, sp_info in SPECIES_REGISTRY.items():
    for fid in sp_info["frontend_ids"]:
        FRONTEND_SPECIES_MAP[fid] = sp_id


def resolve_species(species: str, default: str = "CERF") -> str:
    """Resout un identifiant espece (frontend ou backend) vers l'ID canonique.
    Accepte majuscules, minuscules, IDs frontend.
    Retourne le default si non reconnu."""
    upper = species.upper()
    if upper in SPECIES_REGISTRY:
        return upper
    lower = species.lower()
    if lower in FRONTEND_SPECIES_MAP:
        return FRONTEND_SPECIES_MAP[lower]
    return default


def get_species_info(species: str) -> dict:
    """Retourne les informations du registre pour une espece."""
    resolved = resolve_species(species)
    return SPECIES_REGISTRY.get(resolved, SPECIES_REGISTRY["CERF"])
