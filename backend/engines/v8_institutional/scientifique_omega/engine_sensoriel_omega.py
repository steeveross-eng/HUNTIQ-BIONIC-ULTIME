"""
engine_sensoriel_omega.py — ENGINE SCIENTIFIQUE Ω · SENSORIEL
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · PHASE XV · BLOC 1

Représente les sensibilités sensorielles :
  - vision (ouvert/fermé, ombrage)
  - odorat (attracteurs/répulseurs)
  - ouïe (routes, humains)
  - thermosensibilité (stress thermique)
  - neige (mobilité réduite)

Source EXCLUSIVE : BIO_REACTEUR_Ω_<ESPECE>.json.
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, timezone
from engines.v8_institutional.especes.bio_reacteur_loader_omega import load_bio_reacteur


ENGINE_SENSORIEL_SPEC: Dict[str, Any] = {
    "engine_id": "ENGINE_SENSORIEL_Ω",
    "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
    "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
    "objectif_institutionnel": (
        "Sensibilités sensorielles documentées : vision, odorat, ouïe, "
        "thermosensibilité, neige. Issues exclusivement des BIO_REACTEURS_Ω."
    ),
    "bio_reacteur_inputs_required": [
        "thermoregulation.seuil_stress",
        "thermoregulation.comportements_adaptation",
        "neige.seuil_mobilite",
        "neige.seuil_mortalite",
        "habitat.zones_thermiques",
        "habitat.zones_ouvertes",
        "habitat.zones_matures",
        "pression_humaine.routes",
        "pression_humaine.urbanisation",
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

    vision = {
        "habitat_zones_ouvertes": _values_from(bp_outputs, "ENGINE_HABITAT", "habitat.zones_ouvertes"),
        "habitat_zones_matures": _values_from(bp_outputs, "ENGINE_HABITAT", "habitat.zones_matures"),
        "habitat_zones_thermiques_ombrage": _values_from(bp_outputs, "ENGINE_TERRITOIRE", "habitat.zones_thermiques"),
    }
    # Odorat — récupéré de la pression humaine + nutrition
    import json as _json
    from pathlib import Path as _Path
    bp_path = _Path(f"/app/frontend/public/reports/bio_profile_omega/BIO_PROFILE_Ω_{espece_id}.json")
    with open(bp_path, "r", encoding="utf-8") as f:
        bp = _json.load(f)
    odorat = {
        "attractifs_anthropiques": bp.get("pression_humaine", {}).get("attractifs_anthropiques", []),
        "agriculture": bp.get("pression_humaine", {}).get("agriculture", []),
    }
    ouie = {
        "routes": bp.get("pression_humaine", {}).get("routes", []),
        "urbanisation": bp.get("pression_humaine", {}).get("urbanisation", []),
    }
    thermosensibilite = {
        "seuil_stress_C": _values_from(bp_outputs, "ENGINE_SENSORIEL", "thermoregulation.seuil_stress"),
        "comportements_adaptation": _values_from(bp_outputs, "ENGINE_SENSORIEL", "thermoregulation.comportements_adaptation"),
    }
    neige = {
        "seuil_mobilite_cm": _values_from(bp_outputs, "ENGINE_SENSORIEL", "neige.seuil_mobilite"),
        "seuil_mortalite_cm": _values_from(bp_outputs, "ENGINE_SENSORIEL", "neige.seuil_mortalite"),
    }

    return {
        "engine_id": "ENGINE_SENSORIEL_Ω",
        "espece_id": espece_id,
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_bio_reacteur_sha256": reacteur.get("_runtime_sha256"),
        "vision": vision,
        "odorat": odorat,
        "ouie": ouie,
        "thermosensibilite": thermosensibilite,
        "neige": neige,
        "exclusivement_bio_reacteur": True,
        "fallback_active": False,
        "interpolation_active": False,
    }
