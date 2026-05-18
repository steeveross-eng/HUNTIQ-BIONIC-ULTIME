"""
RECLASSED → modules/utility_modules/liste_epicerie.py
Consolidation V6 (Directive STEEVE-MAX)
Ce fichier est conserve pour compatibilite d'import.

P22ΩΩ_QUALITY_GROUPE_A · 2026-05-18 · STEEVE-MAX
Wildcard import remplacé par imports explicites (singleton + classes publiques).
"""
from modules.utility_modules.liste_epicerie import (
    ItemCategory,
    ListeEpicerieItem,
    ListeEpicerieResponse,
    ListeEpicerieService,
    liste_epicerie_service,
)

__all__ = [
    "ItemCategory",
    "ListeEpicerieItem",
    "ListeEpicerieResponse",
    "ListeEpicerieService",
    "liste_epicerie_service",
]
