"""
engine_habitat_omega.py — PHASE XVII · ENGINE_HABITAT_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°37

ENGINE scientifique autonome consommant :
  • Les 50 études HABITAT du dataset SCI_Ω unifié
  • Les BIO_REACTEURS_Ω pour la couche ENGINE_HABITAT
  • Aucun legacy, aucun fallback, aucune interpolation.

Sortie principale :
  compute_habitat_score(espece) → Habitat_Score_Ω ∈ [0, 100]
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from .bio_reacteur_loader_omega import ESPECES_SUPPORTEES, load_all_bio_reacteurs
from .datasets_science_omega import (
    harmonize_habitat_studies, ESPECES_CANONICAL,
)


__all__ = [
    "compute_habitat_score", "compute_habitat_all_especes",
    "ENGINE_HABITAT_Ω_LOCK_SHA256", "ENGINE_HABITAT_SPEC",
]


# Pondération institutionnelle des axes habitat (total = 1.0)
WEIGHTS_HABITAT = {
    "diversite_biomes": 0.25,       # nombre de biomes distincts documentés
    "fiabilite_etudes": 0.20,       # moyenne des niveaux de confiance
    "couverture_temporelle": 0.15,  # étalement temporel des études
    "qualite_preuve": 0.15,         # % d'études PR (peer-reviewed)
    "anthropisation_tolerance": 0.10,  # présence urbaine/agricole
    "profondeur_biome_pivot": 0.15,  # dominance du biome-pivot de l'espèce
}

BIOME_PIVOT_PAR_ESPECE = {
    "CHEVREUIL": "FORET_MIXTE",
    "ORIGNAL": "FORET_BOREAL",
    "OURS_NOIR": "FORET_BOREAL",
    "WAPITI": "MONTAGNE",
    "DINDON_SAUVAGE": "FORET_DE_CHENES",
}

# Score de confiance par label
CONFIDENCE_SCORE = {"ÉLEVÉ": 100.0, "MOYEN": 60.0, "FAIBLE": 25.0, "INCONNU": 0.0}
PREUVE_SCORE = {"PR": 100.0, "UNI": 80.0, "GOV": 70.0, "UNKNOWN": 40.0}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


ENGINE_HABITAT_SPEC = {
    "id": "ENGINE_HABITAT_Ω",
    "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
    "input_sources": ["SCI_Ω.habitat_studies", "BIO_REACTEURS_Ω.ENGINE_HABITAT"],
    "weights": WEIGHTS_HABITAT,
    "output_signature": [
        "habitat_score_omega",
        "biome_pivot",
        "biomes_covered",
        "studies_count",
        "avg_confidence",
        "peer_reviewed_ratio",
        "temporal_coverage_years",
        "anti_generique_violations",
    ],
}
ENGINE_HABITAT_Ω_LOCK_SHA256 = _sha_str(json.dumps(ENGINE_HABITAT_SPEC, sort_keys=True,
                                                     ensure_ascii=False))


def compute_habitat_score(espece: str,
                           habitat_studies: List[Dict[str, Any]] | None = None,
                           bio_reacteurs: Dict[str, Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """Calcule Habitat_Score_Ω pour une espèce canonique.

    Formule institutionnelle stricte, 6 axes pondérés. Aucun fallback.
    """
    if espece not in ESPECES_CANONICAL:
        raise ValueError(f"ESPECE_NON_CANONIQUE::{espece}")

    if habitat_studies is None:
        habitat_studies = harmonize_habitat_studies()
    if bio_reacteurs is None:
        bio_reacteurs = load_all_bio_reacteurs()

    violations: List[str] = []
    studies_esp = [s for s in habitat_studies if s["espece_canonique"] == espece]
    if not studies_esp:
        violations.append(f"{espece}::ENGINE_HABITAT::NO_STUDIES_AVAILABLE")

    # AXE 1 — Diversité des biomes
    biomes = set()
    for s in studies_esp:
        for b in s["biome_types"]:
            biomes.add(b)
    # Saturation à 8 biomes distincts = 100
    diversite_biomes_score = min(100.0, (len(biomes) / 8.0) * 100.0)

    # AXE 2 — Fiabilité des études
    conf_scores = [CONFIDENCE_SCORE.get(s["niveau_confiance"], 0.0) for s in studies_esp]
    fiabilite_score = sum(conf_scores) / len(conf_scores) if conf_scores else 0.0

    # AXE 3 — Couverture temporelle (étalement d'années)
    annees = [s["annee"] for s in studies_esp if s["annee"]]
    if len(annees) >= 2:
        amplitude = max(annees) - min(annees)
        # 50 ans d'étalement = 100, 10 ans = 20
        temporelle_score = min(100.0, amplitude / 0.5)
    elif len(annees) == 1:
        temporelle_score = 30.0
    else:
        temporelle_score = 0.0
        violations.append(f"{espece}::ENGINE_HABITAT::NO_TEMPORAL_DATA")

    # AXE 4 — Qualité de preuve (% PR)
    pr_count = sum(1 for s in studies_esp if s["type_preuve"] == "PR")
    qualite_score = (pr_count / len(studies_esp)) * 100.0 if studies_esp else 0.0

    # AXE 5 — Tolérance anthropisation (présence urbain/agricole dans les études)
    anthro_biomes = {"URBAIN", "PERIURBAIN", "MILIEUX_AGRICOLES", "CHAMPS_AGRICOLES",
                     "MOSAIQUE_AGRICOLE_FORESTIERE", "MOSAIQUE_FORESTIERE_AGRICOLE",
                     "MOSAIQUE_BOREAL_AGRICOLE", "MOSAIQUE_BOREAL_PRAIRIES",
                     "MOSAIQUE_FORESTIERE_AGRICOLE_URBAINE", "MOSAIQUE_AGROFORESTIERE",
                     "LIERES_BOREALES_AGRICOLES", "MOSAIQUE_AGRICOLE"}
    anthro_detect = biomes & anthro_biomes
    anthro_score = min(100.0, len(anthro_detect) * 20.0)  # 5 biomes anthro = 100

    # AXE 6 — Profondeur biome-pivot
    pivot = BIOME_PIVOT_PAR_ESPECE.get(espece)
    if not pivot:
        violations.append(f"{espece}::ENGINE_HABITAT::NO_PIVOT_DEFINED")
        pivot_score = 0.0
    else:
        pivot_count = sum(1 for s in studies_esp if pivot in s["biome_types"])
        pivot_score = (pivot_count / len(studies_esp)) * 100.0 if studies_esp else 0.0

    # Score composite pondéré
    composite = (
        diversite_biomes_score * WEIGHTS_HABITAT["diversite_biomes"]
        + fiabilite_score * WEIGHTS_HABITAT["fiabilite_etudes"]
        + temporelle_score * WEIGHTS_HABITAT["couverture_temporelle"]
        + qualite_score * WEIGHTS_HABITAT["qualite_preuve"]
        + anthro_score * WEIGHTS_HABITAT["anthropisation_tolerance"]
        + pivot_score * WEIGHTS_HABITAT["profondeur_biome_pivot"]
    )
    composite = round(composite, 2)

    # Enrichissement avec l'engine bio_reacteur
    br_habitat = bio_reacteurs.get(espece, {}).get("bio_reacteur_outputs", {}).get("ENGINE_HABITAT", {})
    br_params_count = len(br_habitat.get("parametres_alimentes", {}))

    return {
        "super_engine_id": "ENGINE_HABITAT_Ω",
        "espece": espece,
        "computed_at_utc": _now(),
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "habitat_score_omega": composite,
        "biome_pivot": pivot,
        "biomes_covered": sorted(biomes),
        "biomes_count": len(biomes),
        "studies_count": len(studies_esp),
        "avg_confidence": round(fiabilite_score, 2),
        "peer_reviewed_ratio": round(qualite_score, 2),
        "temporal_coverage_years": (max(annees) - min(annees)) if len(annees) >= 2 else 0,
        "annees_min": min(annees) if annees else None,
        "annees_max": max(annees) if annees else None,
        "scores_axes": {
            "diversite_biomes": round(diversite_biomes_score, 2),
            "fiabilite_etudes": round(fiabilite_score, 2),
            "couverture_temporelle": round(temporelle_score, 2),
            "qualite_preuve": round(qualite_score, 2),
            "anthropisation_tolerance": round(anthro_score, 2),
            "profondeur_biome_pivot": round(pivot_score, 2),
        },
        "bio_reacteur_params_count": br_params_count,
        "anti_generique_violations": violations,
        "anti_generique_pass": len(violations) == 0,
        "fallback_active": False,
        "interpolation_active": False,
    }


def compute_habitat_all_especes() -> Dict[str, Any]:
    """Retourne le bundle Habitat_Score_Ω pour les 5 espèces."""
    studies = harmonize_habitat_studies()
    bio = load_all_bio_reacteurs()
    results = {}
    for esp in ESPECES_CANONICAL:
        results[esp] = compute_habitat_score(esp, studies, bio)

    master_score = round(
        sum(r["habitat_score_omega"] for r in results.values()) / len(results), 2)
    total_violations = sum(len(r["anti_generique_violations"]) for r in results.values())
    return {
        "manifest_id": "ENGINE_HABITAT_Ω_BUNDLE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "computed_at_utc": _now(),
        "engine_lock_sha256": ENGINE_HABITAT_Ω_LOCK_SHA256,
        "habitat_master_score_omega": master_score,
        "results_par_espece": results,
        "anti_generique_violations_total": total_violations,
        "anti_generique_pass_global": total_violations == 0,
    }
