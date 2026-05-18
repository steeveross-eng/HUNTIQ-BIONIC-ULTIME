"""
RECLASSED → modules/experiments/chasseur_jumeau.py
Consolidation V6 (Directive STEEVE-MAX)
Ce fichier est conserve pour compatibilite d'import.

P22ΩΩ_QUALITY_GROUPE_A · 2026-05-18 · STEEVE-MAX
Wildcard import remplacé par imports explicites (singleton + classes publiques).
"""
from modules.experiments.chasseur_jumeau import (
    ChasseurProfile,
    ChasseurJumeauResponse,
    ChasseurJumeauService,
    chasseur_jumeau_service,
)

__all__ = [
    "ChasseurProfile",
    "ChasseurJumeauResponse",
    "ChasseurJumeauService",
    "chasseur_jumeau_service",
]
