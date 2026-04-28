"""
protections_omega.py — PHASE 2 STABILISATION TERRITOIRE Ω
═══════════════════════════════════════════════════════════════════════════
Commandant : STEEVE-MAX
Protocole  : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Module DÉCLARATIF des 10 protections institutionnelles. Lecture seule.
Aucune logique métier n'y vit ; cet objet sert exclusivement aux endpoints
de santé (/health) et au HUD frontend pour afficher l'état des protections.

Toute modification doit recevoir l'aval explicite du Commandant.
═══════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from typing import Dict, List, Tuple


# Liste figée — modification interdite hors directive Commandant.
PROTECTIONS_OMEGA: Tuple[Dict[str, str], ...] = (
    {
        "code": "BCE_4X_ULTIME_ABSOLU",
        "label": "BCE-4X — ULTIME ABSOLU",
        "version": "TOP-ABSOLU",
        "rule": "ZÉRO divergence · ZÉRO duplication · ZÉRO fallback",
        "status": "ACTIF",
    },
    {
        "code": "STEEVE_MAX_AUTHORITY",
        "label": "STEEVE-MAX — AUTHORITY_Ω",
        "version": "PRIORITÉ_COMMANDANT",
        "rule": "Priorité absolue Commandant — toute directive prime sur tout",
        "status": "ACTIF",
    },
    {
        "code": "ANTI_REGRESSION_OMEGA",
        "label": "ANTI-RÉGRESSION_Ω",
        "version": "X200",
        "rule": "Tests OMÉGA bloquants à chaque release · SHA-256 V30 invariants",
        "status": "ACTIF",
    },
    {
        "code": "ANTI_DUPLICATION_OMEGA",
        "label": "ANTI-DUPLICATION_Ω",
        "version": "X40",
        "rule": "Aucune duplication de panneau · cert · score · couche Ω",
        "status": "ACTIF",
    },
    {
        "code": "ANTI_LEGACY_OMEGA",
        "label": "ANTI-LEGACY_Ω",
        "version": "PURGE_TOTALE",
        "rule": "Purge V5/V6/V7 — modules legacy neutralisés (9 modules)",
        "status": "ACTIF",
    },
    {
        "code": "ZERO_FALLBACK_OMEGA",
        "label": "ZERO-FALLBACK_Ω",
        "version": "STRICT",
        "rule": "Interdiction des routes non-Ω · stratégie SW supprimée",
        "status": "ACTIF",
    },
    {
        "code": "MODULARITE_100",
        "label": "MODULARITÉ-100%",
        "version": "PHASE-E",
        "rule": "Tous les modules TERRITOIRE activés et applied=true",
        "status": "ACTIF",
    },
    {
        "code": "TRACE_LOG_OMEGA",
        "label": "TRACE-LOG_Ω",
        "version": "MAX",
        "rule": "Logs supervisor/ + payload echo registry_lock_v30 sur chaque appel",
        "status": "ACTIF",
    },
    {
        "code": "SHIELD_OMEGA_MAX",
        "label": "SHIELD-Ω-MAX",
        "version": "INTEGRAL",
        "rule": "Protection frontend (SW disabled) + backend (V30 LOCKED inviolé)",
        "status": "ACTIF",
    },
    {
        "code": "WATCHDOG_OMEGA",
        "label": "WATCHDOG-Ω",
        "version": "PHASE_2",
        "rule": "/api/v30/territoire/health pinguable toutes 5 min · anti-hibernation",
        "status": "ACTIF",
    },
)


def list_protections() -> List[Dict[str, str]]:
    """Retourne la liste figée des protections (lecture seule, copie défensive)."""
    return [dict(p) for p in PROTECTIONS_OMEGA]


def all_active() -> bool:
    """Renvoie True si TOUTES les protections sont marquées ACTIF."""
    return all(p["status"] == "ACTIF" for p in PROTECTIONS_OMEGA)


def get_count() -> int:
    return len(PROTECTIONS_OMEGA)
