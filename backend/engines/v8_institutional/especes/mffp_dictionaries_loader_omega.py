"""
mffp_dictionaries_loader_omega.py — ORDRE N°52-R12
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Loader des dictionnaires PROPOSÉS pour PHASE_3 R8 (R12 livraison).

Tous les dictionnaires sont chargés depuis :
  /app/backend/data/territoire/dictionaries_proposed/*.json

Doctrine R12 :
  · Les dictionnaires sont en status='PROPOSÉ' (à valider par Commandant).
  · Aucune valeur inventée : toutes basées sur la documentation MFFP
    publique (Manuel d'aménagement 2016, Normes inventaire 2018).
  · La référence scientifique est attachée à chaque dictionnaire pour
    audit forensique.
  · Les fonctions PHASE_3 R8 utilisent ces dicts UNIQUEMENT après
    validation explicite du Commandant (status='VALIDÉ' ou 'OFFICIAL').
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mffp_dictionaries_loader_omega")

DICTIONARIES_ROOT = Path(
    "/app/backend/data/territoire/dictionaries_proposed")

DICTIONARY_FILES = {
    "structure_classification_rules": (
        DICTIONARIES_ROOT / "structure_classification_rules.json"),
    "cl_dens_to_pct": (
        DICTIONARIES_ROOT / "cl_dens_to_pct.json"),
    "classes_age": (
        DICTIONARIES_ROOT / "classes_age.json"),
    "ty_couv_to_forest_binary": (
        DICTIONARIES_ROOT / "ty_couv_to_forest_binary.json"),
    "tables_rendement_mffp": (
        DICTIONARIES_ROOT / "tables_rendement_mffp.json"),
    "habitat_preferences_par_espece": (
        DICTIONARIES_ROOT / "habitat_preferences_par_espece.json"),
    "perturbation_severity": (
        DICTIONARIES_ROOT / "perturbation_severity.json"),
}


def load_dictionary(name: str) -> Dict[str, Any]:
    """Charge un dictionnaire par son nom canonique."""
    if name not in DICTIONARY_FILES:
        raise KeyError(
            f"DICTIONARY_INCONNU::{name} :: connus={list(DICTIONARY_FILES)}")
    p = DICTIONARY_FILES[name]
    if not p.exists():
        raise FileNotFoundError(
            f"DICTIONARY_FILE_MISSING::{p}")
    return json.loads(p.read_text(encoding="utf-8"))


def load_all_dictionaries() -> Dict[str, Dict[str, Any]]:
    """Charge tous les dictionnaires PROPOSÉS."""
    return {name: load_dictionary(name) for name in DICTIONARY_FILES}


def get_dictionary_status(name: str) -> str:
    """Retourne le status du dictionnaire : PROPOSÉ / VALIDÉ / OFFICIAL."""
    try:
        d = load_dictionary(name)
        return d.get("status", "UNKNOWN")
    except Exception as e:
        return f"ERROR::{e}"


def all_proposed_dictionaries_status() -> Dict[str, str]:
    """Retourne le status de tous les dictionnaires."""
    return {name: get_dictionary_status(name) for name in DICTIONARY_FILES}


def all_validated_for_p0() -> bool:
    """Indique si TOUS les dicts requis pour P0 sont VALIDÉS (pas PROPOSÉS).

    P0 critiques : structure_classification_rules, cl_dens_to_pct,
                   classes_age, ty_couv_to_forest_binary.
    """
    p0_required = [
        "structure_classification_rules", "cl_dens_to_pct",
        "classes_age", "ty_couv_to_forest_binary",
    ]
    for name in p0_required:
        status = get_dictionary_status(name)
        if status not in ("VALIDÉ", "OFFICIAL"):
            return False
    return True


def all_validated_for_p1() -> bool:
    """Indique si TOUS les dicts requis pour P1 (R15) sont VALIDÉS.

    P1 = P0 critiques + tables_rendement_mffp +
         habitat_preferences_par_espece + perturbation_severity.
    """
    p1_required = [
        "structure_classification_rules", "cl_dens_to_pct",
        "classes_age", "ty_couv_to_forest_binary",
        "tables_rendement_mffp", "habitat_preferences_par_espece",
        "perturbation_severity",
    ]
    for name in p1_required:
        status = get_dictionary_status(name)
        if status not in ("VALIDÉ", "OFFICIAL"):
            return False
    return True


def list_validation_blockers() -> List[Dict[str, Any]]:
    """Liste les dictionnaires non validés et les raisons."""
    blockers = []
    for name in DICTIONARY_FILES:
        try:
            d = load_dictionary(name)
            status = d.get("status", "UNKNOWN")
            if status not in ("VALIDÉ", "OFFICIAL"):
                blockers.append({
                    "dictionary": name,
                    "status": status,
                    "validation_required_by_commandant": d.get(
                        "validation_required_by_commandant", []),
                })
        except Exception as e:
            blockers.append({
                "dictionary": name,
                "status": "FILE_ERROR",
                "error": str(e),
            })
    return blockers


__all__ = [
    "load_dictionary",
    "load_all_dictionaries",
    "get_dictionary_status",
    "all_proposed_dictionaries_status",
    "all_validated_for_p0",
    "all_validated_for_p1",
    "list_validation_blockers",
    "DICTIONARIES_ROOT",
    "DICTIONARY_FILES",
]
