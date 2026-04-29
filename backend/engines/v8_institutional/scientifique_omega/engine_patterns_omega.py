"""
engine_patterns_omega.py — ENGINE SCIENTIFIQUE Ω · PATTERNS
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · PHASE XV · BLOC 1

Représente les patterns saisonniers et comportementaux :
  - déplacements (corridors, distances, rythmes)
  - pression humaine (nocturnité, évitement)
  - climat (neige, chaleur, humidité)
  - reproduction (rut, nidification)
  - nutrition (protéines printemps, énergie automne)

Source EXCLUSIVE : BIO_REACTEUR_Ω_<ESPECE>.json.
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, timezone
from engines.v8_institutional.especes.bio_reacteur_loader_omega import load_bio_reacteur


ENGINE_PATTERNS_SPEC: Dict[str, Any] = {
    "engine_id": "ENGINE_PATTERNS_Ω",
    "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
    "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
    "objectif_institutionnel": (
        "Patterns saisonniers et comportementaux : déplacements, pression humaine, "
        "climat, reproduction, nutrition. Issus exclusivement des BIO_REACTEURS_Ω."
    ),
    "bio_reacteur_inputs_required": [
        "comportements_saisonniers.printemps",
        "comportements_saisonniers.ete",
        "comportements_saisonniers.automne",
        "comportements_saisonniers.hiver",
        "corridors.distances_typiques",
        "corridors.connectivite_optimum",
        "thermoregulation.seuil_stress",
        "neige.seuil_mobilite",
        "neige.seuil_mortalite",
        "nutrition.besoins_proteines",
        "nutrition.besoins_energetiques",
    ],
    "exclusivement_bio_reacteur": True,
    "fallback_active": False,
    "interpolation_active": False,
    "anti_generique_strict": True,
    "version": "v1.0-PHASE_XV_Ω",
}


def _values_from(outputs, engine_name, path):
    eng = outputs.get(engine_name, {}).get("parametres_alimentes", {})
    node = eng.get(path, {})
    return node.get("value") if isinstance(node, dict) else None


def compute(espece_id: str, env: Dict[str, Any] | None = None) -> Dict[str, Any]:
    env = env or {}
    reacteur = load_bio_reacteur(espece_id)
    bp_outputs = reacteur["bio_reacteur_outputs"]

    deplacements = {
        "distances_typiques": _values_from(bp_outputs, "ENGINE_CORRIDORS", "corridors.distances_typiques"),
        "connectivite_optimum": _values_from(bp_outputs, "ENGINE_CORRIDORS", "corridors.connectivite_optimum"),
        "fragmentation_penalty": _values_from(bp_outputs, "ENGINE_CORRIDORS", "corridors.fragmentation_penalty"),
        "zones_passage_essentielles": _values_from(bp_outputs, "ENGINE_CORRIDORS", "corridors.zones_passage_essentielles"),
        "comportement_automne": _values_from(bp_outputs, "ENGINE_COMPORTEMENT", "comportements_saisonniers.automne"),
        "comportement_hiver": _values_from(bp_outputs, "ENGINE_COMPORTEMENT", "comportements_saisonniers.hiver"),
    }
    climat = {
        "thermique_seuil_C": _values_from(bp_outputs, "ENGINE_SENSORIEL", "thermoregulation.seuil_stress"),
        "neige_seuil_mobilite_cm": _values_from(bp_outputs, "ENGINE_SENSORIEL", "neige.seuil_mobilite"),
        "neige_seuil_mortalite_cm": _values_from(bp_outputs, "ENGINE_SENSORIEL", "neige.seuil_mortalite"),
        "thermique_comportements_adaptation": _values_from(bp_outputs, "ENGINE_SENSORIEL", "thermoregulation.comportements_adaptation"),
    }
    reproduction = {
        "rut_actif": _values_from(bp_outputs, "ENGINE_RUT", "comportements_saisonniers.automne.rut"),
        "rut_sites": _values_from(bp_outputs, "ENGINE_RUT", "sites_critiques.rut"),
        "nidification_sites": _values_from(bp_outputs, "ENGINE_NIDIFICATION", "sites_critiques.nidification"),
        "reproduction_printemps": _values_from(bp_outputs, "ENGINE_NIDIFICATION", "comportements_saisonniers.printemps.reproduction"),
    }
    nutrition_patterns = {
        "besoins_proteines": _values_from(bp_outputs, "ENGINE_NUTRITION", "nutrition.besoins_proteines"),
        "besoins_energetiques": _values_from(bp_outputs, "ENGINE_NUTRITION", "nutrition.besoins_energetiques"),
        "alimentation_printemps": _values_from(bp_outputs, "ENGINE_NUTRITION", "nutrition.alimentation_saisonniere.printemps"),
        "alimentation_automne": _values_from(bp_outputs, "ENGINE_NUTRITION", "nutrition.alimentation_saisonniere.automne"),
    }

    return {
        "engine_id": "ENGINE_PATTERNS_Ω",
        "espece_id": espece_id,
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_bio_reacteur_sha256": reacteur.get("_runtime_sha256"),
        "deplacements": deplacements,
        "climat": climat,
        "reproduction": reproduction,
        "nutrition_patterns": nutrition_patterns,
        "exclusivement_bio_reacteur": True,
        "fallback_active": False,
        "interpolation_active": False,
    }
