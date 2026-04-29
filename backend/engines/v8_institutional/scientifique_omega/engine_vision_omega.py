"""
engine_vision_omega.py — ENGINE SCIENTIFIQUE Ω · VISION
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · PHASE XV · BLOC 1

Représente les zones visibles utilisées par l'espèce :
  - habitats préférentiels (mosaïques forestières, zones humides, prairies)
  - zones critiques (mise bas, rut, repos, alimentation, eau)
  - zones thermiques (ombrage, fraîcheur, stress thermique)
  - zones de fragmentation (routes, agriculture, coupes)
  - connectivité écologique (corridors continus)

Source EXCLUSIVE : BIO_REACTEUR_Ω_<ESPECE>.json (chaîne RAPPORT → BIO_PROFILE → BIO_REACTEUR).
Aucune logique générique. Aucun fallback. Aucune interpolation.
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, timezone

from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
    load_bio_reacteur, BioReacteurError,
)


ENGINE_VISION_SPEC: Dict[str, Any] = {
    "engine_id": "ENGINE_VISION_Ω",
    "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
    "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
    "objectif_institutionnel": (
        "Représentation institutionnelle des zones visibles utilisées par l'espèce. "
        "Habitats préférentiels, zones critiques, zones thermiques, fragmentation, "
        "connectivité écologique."
    ),
    "bio_reacteur_inputs_required": [
        "habitat.types_couverts",
        "habitat.zones_humides",
        "habitat.zones_thermiques",
        "habitat.zones_ouvertes",
        "habitat.zones_matures",
        "habitat.mosaiques_foret_agriculture",
        "habitat.zones_transition",
        "sites_critiques.mise_bas",
        "sites_critiques.rut",
        "sites_critiques.repos",
        "sites_critiques.alimentation",
        "sites_critiques.eau",
        "sites_critiques.nidification",
        "sites_critiques.tanieres",
        "pression_humaine.fragmentation",
        "pression_humaine.routes",
        "pression_humaine.agriculture",
        "corridors.connectivite_optimum",
    ],
    "exclusivement_bio_reacteur": True,
    "fallback_active": False,
    "interpolation_active": False,
    "anti_generique_strict": True,
    "version": "v1.0-PHASE_XV_Ω",
}


def _safe_get(d: Dict, dotted: str) -> Any:
    cur: Any = d
    for k in dotted.split("."):
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return None
    return cur


def compute(espece_id: str, env: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Compute des couches VISION_Ω strictement à partir du BIO_REACTEUR_Ω.

    NE FABRIQUE AUCUNE DONNÉE. Lecture/projection seulement.
    Lève BioReacteurError si l'espèce n'a pas de BIO_REACTEUR validé.
    """
    env = env or {}
    reacteur = load_bio_reacteur(espece_id)
    bp_outputs = reacteur["bio_reacteur_outputs"]
    bp_engine_territoire = bp_outputs.get("ENGINE_TERRITOIRE", {}).get("parametres_alimentes", {})
    bp_engine_habitat = bp_outputs.get("ENGINE_HABITAT", {}).get("parametres_alimentes", {})
    bp_engine_sites = bp_outputs.get("ENGINE_SITES_CRITIQUES", {}).get("parametres_alimentes", {})

    def _values_from(slot, path):
        node = slot.get(path, {})
        return node.get("value") if isinstance(node, dict) else None

    habitats_preferentiels = {
        "types_couverts": _values_from(bp_engine_habitat, "habitat.types_couverts"),
        "mosaiques_foret_agriculture": _values_from(bp_engine_habitat, "habitat.mosaiques_foret_agriculture"),
        "zones_ouvertes": _values_from(bp_engine_habitat, "habitat.zones_ouvertes"),
        "zones_matures": _values_from(bp_engine_habitat, "habitat.zones_matures"),
        "zones_humides": _values_from(bp_engine_territoire, "habitat.zones_humides"),
    }
    zones_critiques = {
        "mise_bas": _values_from(bp_engine_sites, "sites_critiques.mise_bas"),
        "rut": _values_from(bp_engine_sites, "sites_critiques.rut"),
        "repos": _values_from(bp_engine_sites, "sites_critiques.repos"),
        "alimentation": _values_from(bp_engine_sites, "sites_critiques.alimentation"),
        "eau": _values_from(bp_engine_sites, "sites_critiques.eau"),
        "nidification": _values_from(bp_engine_sites, "sites_critiques.nidification"),
        "tanieres": _values_from(bp_engine_sites, "sites_critiques.tanieres"),
    }
    zones_thermiques = {
        "zones_thermiques_habitat": _values_from(bp_engine_territoire, "habitat.zones_thermiques"),
    }
    bp_engine_climat = bp_outputs.get("ENGINE_CLIMAT", {}).get("parametres_alimentes", {})
    seuil_thermique = _values_from(bp_engine_climat, "thermoregulation.seuil_stress")
    zones_thermiques["seuil_stress_C"] = seuil_thermique

    bp_engine_corridors = bp_outputs.get("ENGINE_CORRIDORS", {}).get("parametres_alimentes", {})
    fragmentation = {
        "fragmentation_penalty": _values_from(bp_engine_corridors, "corridors.fragmentation_penalty"),
        "connectivite_optimum": _values_from(bp_engine_corridors, "corridors.connectivite_optimum"),
    }

    return {
        "engine_id": "ENGINE_VISION_Ω",
        "espece_id": espece_id,
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_bio_reacteur_sha256": reacteur.get("_runtime_sha256"),
        "habitats_preferentiels": habitats_preferentiels,
        "zones_critiques": zones_critiques,
        "zones_thermiques": zones_thermiques,
        "fragmentation": fragmentation,
        "exclusivement_bio_reacteur": True,
        "fallback_active": False,
        "interpolation_active": False,
    }
