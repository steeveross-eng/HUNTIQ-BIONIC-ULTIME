"""
engine_comportement_omega.py — ENGINE SCIENTIFIQUE Ω · COMPORTEMENT
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · PHASE XV · BLOC 1

Représente les comportements documentés :
  - alimentaires
  - de déplacement
  - de reproduction
  - de repos
  - d'évitement humain
  - face aux prédateurs
  - thermiques

Source EXCLUSIVE : BIO_REACTEUR_Ω_<ESPECE>.json.
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, timezone
from engines.v8_institutional.especes.bio_reacteur_loader_omega import load_bio_reacteur


ENGINE_COMPORTEMENT_SPEC: Dict[str, Any] = {
    "engine_id": "ENGINE_COMPORTEMENT_Ω",
    "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
    "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
    "objectif_institutionnel": (
        "Comportements documentés (alimentation, déplacement, reproduction, repos, "
        "évitement humain, prédateurs, thermique). Issus exclusivement des BIO_REACTEURS_Ω."
    ),
    "bio_reacteur_inputs_required": [
        "comportements_saisonniers.printemps",
        "comportements_saisonniers.ete",
        "comportements_saisonniers.automne",
        "comportements_saisonniers.hiver",
        "sites_critiques.repos",
        "sites_critiques.alimentation",
        "interactions.predation",
        "thermoregulation.comportements_adaptation",
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

    cs = {
        "printemps": _values_from(bp_outputs, "ENGINE_COMPORTEMENT", "comportements_saisonniers.printemps"),
        "ete": _values_from(bp_outputs, "ENGINE_COMPORTEMENT", "comportements_saisonniers.ete"),
        "automne": _values_from(bp_outputs, "ENGINE_COMPORTEMENT", "comportements_saisonniers.automne"),
        "hiver": _values_from(bp_outputs, "ENGINE_COMPORTEMENT", "comportements_saisonniers.hiver"),
    }

    def collect_bullets(saison_dict, sub):
        if not isinstance(saison_dict, dict):
            return []
        return saison_dict.get(sub, []) or []

    alimentaires = []
    deplacement = []
    reproduction = []
    repos = collect_bullets(cs.get("printemps") or {}, "habitat") if cs.get("printemps") else []
    repos.extend([] if not (cs.get("ete") and isinstance(cs["ete"], dict)) else cs["ete"].get("habitat", []) or [])
    repos_sites = _values_from(bp_outputs, "ENGINE_SITES_CRITIQUES", "sites_critiques.repos")
    if repos_sites:
        repos.extend(repos_sites)

    for season_data in cs.values():
        if isinstance(season_data, dict):
            alimentaires.extend(season_data.get("alimentation", []) or [])
            deplacement.extend(season_data.get("deplacements", []) or [])
            reproduction.extend(season_data.get("reproduction", []) or [])
            reproduction.extend(season_data.get("rut", []) or [])
            reproduction.extend(season_data.get("hyperphagie", []) or [])

    evitement_humain = _values_from(bp_outputs, "ENGINE_INTERACTIONS", "interactions.competition") or []
    face_predateurs = _values_from(bp_outputs, "ENGINE_INTERACTIONS", "interactions.predation") or []
    thermiques = _values_from(bp_outputs, "ENGINE_SENSORIEL", "thermoregulation.comportements_adaptation") or []

    return {
        "engine_id": "ENGINE_COMPORTEMENT_Ω",
        "espece_id": espece_id,
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_bio_reacteur_sha256": reacteur.get("_runtime_sha256"),
        "comportements_alimentaires": alimentaires,
        "comportements_deplacement": deplacement,
        "comportements_reproduction": reproduction,
        "comportements_repos": repos,
        "comportements_evitement_humain": evitement_humain,
        "comportements_face_predateurs": face_predateurs,
        "comportements_thermiques": thermiques,
        "comportements_par_saison": cs,
        "exclusivement_bio_reacteur": True,
        "fallback_active": False,
        "interpolation_active": False,
    }
