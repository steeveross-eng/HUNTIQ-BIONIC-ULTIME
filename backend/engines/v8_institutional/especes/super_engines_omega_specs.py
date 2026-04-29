"""
super_engines_omega_specs.py — BLOC 4 PHASE XIV
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3

PRÉ-ACTIVATION DES SUPER ENGINES_Ω — INTERFACES UNIQUEMENT.
AUCUNE LOGIQUE NOUVELLE — implémentation prévue en PHASE XV.

Liste verrouillée et immuable :
  - ENGINE_CORRIDORS_MASTER_Ω
  - ENGINE_NUTRITION_MASTER_Ω
  - ENGINE_SENSORIEL_MASTER_Ω
  - ENGINE_COMPORTEMENT_MASTER_Ω
  - ENGINE_GOUVERNANCE_MASTER_Ω
  - ENGINE_TERRITOIRE_MASTER_Ω

Dépendance OBLIGATOIRE : BIO_REACTEURS_Ω_<ESPECE>.json (READ-ONLY).
Aucune génération générique hors cadre BIO_PROFILE_Ω → BIO_REACTEURS_Ω.
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from datetime import datetime, timezone


@dataclass(frozen=True)
class SuperEngineSpec:
    """Spécification déclarative d'un SUPER ENGINE_Ω. IMMUABLE.

    Phase XV pourra implémenter `compute()` mais ne PEUT pas modifier
    cette spécification (verrouillée par le Commandant en Phase XIV).
    """
    super_engine_id: str
    nom_doctrinal: str
    objectif_institutionnel: str
    bio_reacteur_inputs_required: List[str]
    engines_consumed: List[str]
    outputs_signature: Dict[str, str]
    anti_generique_strict: bool = True
    fallback_authorized: bool = False
    interpolation_authorized: bool = False
    bio_reacteur_dependency: str = "BIO_REACTEURS_Ω_<ESPECE>.json (READ-ONLY)"
    activation_status: str = "PRE_ACTIVATED_AWAITING_PHASE_XV_LOGIC"
    phase_creation: str = "PHASE_XIV"
    phase_activation_logique: str = "PHASE_XV (à venir)"


# ─────────────────────────────────────────────────────────────────────
# 6 SUPER ENGINES_Ω — VERROUILLAGE ABSOLU
# ─────────────────────────────────────────────────────────────────────

SUPER_ENGINES_Ω: Dict[str, SuperEngineSpec] = {
    "ENGINE_CORRIDORS_MASTER_Ω": SuperEngineSpec(
        super_engine_id="ENGINE_CORRIDORS_MASTER_Ω",
        nom_doctrinal="Maître des corridors écologiques inter-espèces",
        objectif_institutionnel=(
            "Fusion institutionnelle des 5 ENGINE_CORRIDORS d'espèce en un score "
            "corridor maître par tuile territoriale, prenant en compte le partage "
            "inter-espèces, la fragmentation et la connectivité optimale issus "
            "exclusivement des BIO_REACTEURS_Ω."
        ),
        bio_reacteur_inputs_required=[
            "corridors.corridors_reels_gps",
            "corridors.connectivite_optimum",
            "corridors.fragmentation_penalty",
            "corridors.zones_passage_essentielles",
            "corridors.distances_typiques",
            "interactions.partage_corridors",
        ],
        engines_consumed=["ENGINE_CORRIDORS", "ENGINE_INTERACTIONS"],
        outputs_signature={
            "score_corridor_master_omega": "float (0..100) — fusion 5 espèces",
            "layer_corridors_master_omega": "geo-feature collection",
            "bottleneck_segments": "list[dict]",
            "shared_corridor_segments": "list[dict] — partage inter-espèces",
            "fragmentation_penalty_master": "float (0..1)",
        },
    ),
    "ENGINE_NUTRITION_MASTER_Ω": SuperEngineSpec(
        super_engine_id="ENGINE_NUTRITION_MASTER_Ω",
        nom_doctrinal="Maître de la disponibilité nutritionnelle territoriale",
        objectif_institutionnel=(
            "Synthèse territoriale des besoins nutritionnels, énergétiques et "
            "minéraux des 5 espèces avec saisonnalité stricte issue exclusivement "
            "des BIO_REACTEURS_Ω. Pondération sodium/calcium/magnésium par espèce."
        ),
        bio_reacteur_inputs_required=[
            "nutrition.besoins_proteines",
            "nutrition.besoins_energetiques",
            "nutrition.besoins_mineraux.sodium",
            "nutrition.besoins_mineraux.calcium",
            "nutrition.besoins_mineraux.magnesium",
            "nutrition.alimentation_saisonniere.printemps",
            "nutrition.alimentation_saisonniere.ete",
            "nutrition.alimentation_saisonniere.automne",
            "nutrition.alimentation_saisonniere.hiver",
        ],
        engines_consumed=["ENGINE_NUTRITION", "ENGINE_MINERAUX"],
        outputs_signature={
            "score_nutrition_master_omega": "float (0..100)",
            "layer_nutrition_disponibilite": "geo-feature collection",
            "saisons_critiques": "list[str]",
            "deficit_mineraux_par_espece": "dict[espece -> dict]",
        },
    ),
    "ENGINE_SENSORIEL_MASTER_Ω": SuperEngineSpec(
        super_engine_id="ENGINE_SENSORIEL_MASTER_Ω",
        nom_doctrinal="Maître des contraintes sensorielles & climatiques",
        objectif_institutionnel=(
            "Synthèse des seuils thermiques, pluviométriques et nivologiques par "
            "espèce ; dérive un indicateur sensoriel territorial composite "
            "exclusivement à partir des seuils BIO_PROFILE_Ω validés."
        ),
        bio_reacteur_inputs_required=[
            "thermoregulation.seuil_stress",
            "thermoregulation.comportements_adaptation",
            "neige.seuil_mobilite",
            "neige.seuil_mortalite",
        ],
        engines_consumed=["ENGINE_SENSORIEL", "ENGINE_CLIMAT"],
        outputs_signature={
            "score_sensoriel_master_omega": "float (0..100)",
            "thermique_stress_aggregate_C": "float",
            "neige_critique_aggregate_cm": "float",
            "espece_zones_refuge": "dict[espece -> list]",
        },
    ),
    "ENGINE_COMPORTEMENT_MASTER_Ω": SuperEngineSpec(
        super_engine_id="ENGINE_COMPORTEMENT_MASTER_Ω",
        nom_doctrinal="Maître des comportements saisonniers fusionnés",
        objectif_institutionnel=(
            "Fusion saisonnière des comportements des 5 espèces (printemps, été, "
            "automne, hiver) avec sous-blocs déplacements/alimentation/rut/"
            "hyperphagie/ravages/mise-bas/nidification — alimenté EXCLUSIVEMENT "
            "par BIO_REACTEURS_Ω."
        ),
        bio_reacteur_inputs_required=[
            "comportements_saisonniers.printemps",
            "comportements_saisonniers.ete",
            "comportements_saisonniers.automne",
            "comportements_saisonniers.hiver",
        ],
        engines_consumed=[
            "ENGINE_COMPORTEMENT", "ENGINE_RUT", "ENGINE_NIDIFICATION",
            "ENGINE_HABITAT",
        ],
        outputs_signature={
            "score_comportement_master_omega": "float (0..100)",
            "calendrier_phenologique_unifie": "dict[saison -> dict[espece -> bullets]]",
            "rut_actif_concurrents": "list[espece]",
            "hyperphagie_active_concurrents": "list[espece]",
        },
    ),
    "ENGINE_GOUVERNANCE_MASTER_Ω": SuperEngineSpec(
        super_engine_id="ENGINE_GOUVERNANCE_MASTER_Ω",
        nom_doctrinal="Maître de la gouvernance institutionnelle BCE-4X",
        objectif_institutionnel=(
            "Auditeur institutionnel multi-espèces — agrège pression humaine, "
            "maladies, dynamique populationnelle 20 ans, conflits, attractifs "
            "anthropiques. Émet des recommandations d'aménagement et de "
            "régulation cynégétique à partir des BIO_REACTEURS_Ω strictement."
        ),
        bio_reacteur_inputs_required=[
            "pression_humaine.routes",
            "pression_humaine.agriculture",
            "pression_humaine.urbanisation",
            "pression_humaine.fragmentation",
            "pression_humaine.attractifs_anthropiques",
            "pression_humaine.conflits_humains",
            "maladies.cwd",
            "maladies.lpdv",
            "maladies.tique_hiver",
            "maladies.autres",
            "dynamique.tendances_20_ans",
            "dynamique.expansion",
            "dynamique.declin",
            "dynamique.facteurs",
        ],
        engines_consumed=["ENGINE_INTERACTIONS"],
        outputs_signature={
            "score_gouvernance_master_omega": "float (0..100)",
            "recommandations_amenagement": "list[dict]",
            "alertes_maladies_actives": "list[espece -> maladie]",
            "tendances_population_20_ans": "dict[espece -> trend]",
        },
    ),
    "ENGINE_TERRITOIRE_MASTER_Ω": SuperEngineSpec(
        super_engine_id="ENGINE_TERRITOIRE_MASTER_Ω",
        nom_doctrinal="Maître territorial — fusion finale Ω",
        objectif_institutionnel=(
            "Engine final qui consomme les 5 SUPER ENGINES précédents pour "
            "produire le score territorial composite BCE-4X et la couche "
            "TERRITOIRE_Ω_MASTER. Aucune logique générique. Strictement piloté "
            "par les sorties des autres SUPER ENGINES_Ω."
        ),
        bio_reacteur_inputs_required=[
            "habitat.types_couverts",
            "habitat.mosaiques_foret_agriculture",
            "habitat.zones_humides",
            "habitat.zones_thermiques",
            "habitat.zones_ouvertes",
            "habitat.zones_matures",
            "habitat.zones_transition",
            "sites_critiques.mise_bas",
            "sites_critiques.nidification",
            "sites_critiques.rut",
            "sites_critiques.tanieres",
            "sites_critiques.repos",
            "sites_critiques.alimentation",
            "sites_critiques.eau",
        ],
        engines_consumed=[
            "ENGINE_CORRIDORS_MASTER_Ω", "ENGINE_NUTRITION_MASTER_Ω",
            "ENGINE_SENSORIEL_MASTER_Ω", "ENGINE_COMPORTEMENT_MASTER_Ω",
            "ENGINE_GOUVERNANCE_MASTER_Ω",
        ],
        outputs_signature={
            "score_territoire_master_omega": "float (0..100) — score Ω final",
            "layer_territoire_master_omega": "geo-feature collection unifié",
            "decision_aptitude_territoriale": "str (APTE/MARGINAL/INAPTE)",
            "rang_territorial_par_espece": "dict[espece -> rang]",
        },
    ),
}


SUPER_ENGINE_LOCK_SHA256 = (
    # Verrouillage immuable de la liste (sha256 sur le nom + objectifs)
    __import__("hashlib").sha256(
        "|".join(
            f"{k}::{v.nom_doctrinal}::{','.join(v.bio_reacteur_inputs_required)}"
            for k, v in sorted(SUPER_ENGINES_Ω.items())
        ).encode("utf-8")
    ).hexdigest()
)


def list_super_engines() -> Dict[str, Any]:
    """Liste publique des 6 SUPER ENGINES (interfaces uniquement)."""
    return {
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_PRE_ACTIVATION_SUPER_ENGINES_Ω",
        "issued_by": "COMMANDANT STEEVE-MAX",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "super_engines_count": len(SUPER_ENGINES_Ω),
        "super_engines": {k: asdict(v) for k, v in SUPER_ENGINES_Ω.items()},
        "super_engine_lock_sha256": SUPER_ENGINE_LOCK_SHA256,
        "bio_reacteur_dependency_obligatoire": True,
        "anti_generique_strict": True,
        "fallback_authorized": False,
        "interpolation_authorized": False,
        "phase_logique_implementation": "PHASE_XV (à venir)",
        "note_institutionnelle": (
            "Spécifications verrouillées en PHASE XIV. "
            "Aucune génération générique de SUPER ENGINE en dehors du cadre "
            "BIO_PROFILE_Ω → BIO_REACTEURS_Ω. Implémentation logique attendue "
            "exclusivement en PHASE XV sur ordre formel du Commandant."
        ),
    }


__all__ = [
    "SuperEngineSpec",
    "SUPER_ENGINES_Ω",
    "SUPER_ENGINE_LOCK_SHA256",
    "list_super_engines",
]
