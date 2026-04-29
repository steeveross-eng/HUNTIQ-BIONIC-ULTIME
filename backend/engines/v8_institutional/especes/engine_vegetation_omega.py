"""
engine_vegetation_omega.py — PHASE XVII · ENGINE_VÉGÉTATION_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°37

ENGINE scientifique autonome consommant :
  • Les 20 études NUTRITION du dataset SCI_Ω unifié
  • Les BIO_REACTEURS_Ω pour ENGINE_NUTRITION
  • Aucun legacy, aucun fallback, aucune interpolation.

Sortie principale :
  compute_vegetation_availability(espece) → Vegetation_Availability_Ω ∈ [0, 100]
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from .bio_reacteur_loader_omega import ESPECES_SUPPORTEES, load_all_bio_reacteurs
from .datasets_science_omega import (
    harmonize_nutrition_studies, ESPECES_CANONICAL, SAISONS_CANONICAL,
)


__all__ = [
    "compute_vegetation_availability",
    "compute_vegetation_all_especes",
    "ENGINE_VEGETATION_Ω_LOCK_SHA256",
    "ENGINE_VEGETATION_SPEC",
]


WEIGHTS_VEGETATION = {
    "coverage_studies_count": 0.20,       # nombre d'études nutrition disponibles
    "saisonnalite_complete": 0.25,        # couverture 4 saisons
    "fiabilite_etudes": 0.20,
    "qualite_preuve_pr": 0.15,
    "variabilite_taxonomique": 0.10,     # études multi-espèces
    "consumables_diversite": 0.10,        # types de nourritures distincts couverts
}

# Score de confiance par label (identique engine_habitat)
CONFIDENCE_SCORE = {"ÉLEVÉ": 100.0, "MOYEN": 60.0, "FAIBLE": 25.0, "INCONNU": 0.0}

# Types d'aliments canoniques attendus par espèce (biologiquement contraints)
CONSUMABLES_EXPECTED = {
    "CHEVREUIL": ["brout_feuillus", "brout_resineux", "glands_mast", "bourgeons",
                   "herbacees", "ronces"],
    "ORIGNAL": ["brout_saule", "brout_bouleau", "brout_sapin", "aquatiques_macrophytes",
                 "ramilles_hivernales"],
    "OURS_NOIR": ["petits_fruits", "glands_mast", "insectes", "charognes",
                   "herbacees_printanieres", "noix"],
    "WAPITI": ["graminees", "herbacees", "arbustes", "branchages_hivernaux",
                "graminees_montagnardes"],
    "DINDON_SAUVAGE": ["glands_mast", "graines", "insectes_invertebres", "bourgeons",
                        "residus_culture_mais"],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


ENGINE_VEGETATION_SPEC = {
    "id": "ENGINE_VÉGÉTATION_Ω",
    "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
    "input_sources": ["SCI_Ω.nutrition_studies", "BIO_REACTEURS_Ω.ENGINE_NUTRITION",
                      "BIO_REACTEURS_Ω.ENGINE_MINERAUX"],
    "weights": WEIGHTS_VEGETATION,
    "output_signature": [
        "vegetation_availability_omega",
        "seasonal_coverage",
        "studies_count",
        "avg_confidence",
        "consumables_detected",
        "consumables_expected_match_ratio",
        "anti_generique_violations",
    ],
}
ENGINE_VEGETATION_Ω_LOCK_SHA256 = _sha_str(json.dumps(ENGINE_VEGETATION_SPEC, sort_keys=True,
                                                        ensure_ascii=False))


def _detect_consumables(study_focus: str, study_bloc: str) -> List[str]:
    """Détecte les catégories consommables textuellement."""
    txt = f"{study_focus} {study_bloc}".lower()
    hits = []
    # Cartographie mots-clés → consumables canoniques
    keyword_map = {
        "sapin": "brout_sapin", "saule": "brout_saule", "bouleau": "brout_bouleau",
        "tremble": "brout_feuillus", "glands": "glands_mast", "mast": "glands_mast",
        "fruits": "petits_fruits", "baies": "petits_fruits",
        "bleuet": "petits_fruits", "framboise": "petits_fruits",
        "cèdre": "brout_resineux", "cedre": "brout_resineux",
        "pruch": "brout_resineux", "ronces": "ronces",
        "insect": "insectes", "invertébr": "insectes_invertebres",
        "invertebr": "insectes_invertebres", "charogn": "charognes",
        "graminée": "graminees", "graminee": "graminees",
        "arbuste": "arbustes", "herbac": "herbacees", "herbacée": "herbacees",
        "aquatique": "aquatiques_macrophytes", "macrophyte": "aquatiques_macrophytes",
        "bourgeon": "bourgeons", "ramille": "ramilles_hivernales",
        "grain": "graines", "résidus": "residus_culture", "resid": "residus_culture",
        "noix": "noix", "feuillu": "brout_feuillus", "résineu": "brout_resineux",
        "resineu": "brout_resineux",
    }
    for kw, canon in keyword_map.items():
        if kw in txt and canon not in hits:
            hits.append(canon)
    return hits


def compute_vegetation_availability(espece: str,
                                      nutrition_studies: List[Dict[str, Any]] | None = None,
                                      bio_reacteurs: Dict[str, Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """Calcule Vegetation_Availability_Ω pour une espèce canonique."""
    if espece not in ESPECES_CANONICAL:
        raise ValueError(f"ESPECE_NON_CANONIQUE::{espece}")

    if nutrition_studies is None:
        nutrition_studies = harmonize_nutrition_studies()
    if bio_reacteurs is None:
        bio_reacteurs = load_all_bio_reacteurs()

    violations: List[str] = []
    # Études pertinentes pour l'espèce (multi-especes OK si espece présente)
    studies_esp = [s for s in nutrition_studies
                   if espece in s["especes_canoniques"]]
    if not studies_esp:
        violations.append(f"{espece}::ENGINE_VEGETATION::NO_STUDIES_AVAILABLE")

    # AXE 1 — Nombre d'études
    # Saturation à 10 études disponibles = 100
    coverage_count_score = min(100.0, (len(studies_esp) / 10.0) * 100.0)

    # AXE 2 — Saisonnalité (couverture des 4 saisons)
    saisons_couvertes = set()
    for s in studies_esp:
        for sa in s["saisons_canoniques"]:
            saisons_couvertes.add(sa)
    saisonnalite_score = (len(saisons_couvertes & set(SAISONS_CANONICAL)) / 4.0) * 100.0

    # AXE 3 — Fiabilité
    conf_scores = [CONFIDENCE_SCORE.get(s["niveau_confiance"], 0.0) for s in studies_esp]
    fiabilite_score = sum(conf_scores) / len(conf_scores) if conf_scores else 0.0

    # AXE 4 — Qualité preuve (% PR)
    pr_count = sum(1 for s in studies_esp if s["type_preuve"] == "PR")
    qualite_score = (pr_count / len(studies_esp)) * 100.0 if studies_esp else 0.0

    # AXE 5 — Variabilité taxonomique
    multi_esp_count = sum(1 for s in studies_esp if len(s["especes_canoniques"]) > 1)
    variabilite_score = (multi_esp_count / len(studies_esp)) * 100.0 if studies_esp else 0.0

    # AXE 6 — Consumables détectés vs attendus
    consumables_found = set()
    for s in studies_esp:
        for c in _detect_consumables(s["focus"], s["bloc_id"]):
            consumables_found.add(c)
    expected = set(CONSUMABLES_EXPECTED.get(espece, []))
    if not expected:
        consumables_ratio = 0.0
        violations.append(f"{espece}::ENGINE_VEGETATION::NO_CONSUMABLES_EXPECTED")
    else:
        matches = len(consumables_found & expected)
        consumables_ratio = (matches / len(expected)) * 100.0

    # Composite pondéré
    composite = (
        coverage_count_score * WEIGHTS_VEGETATION["coverage_studies_count"]
        + saisonnalite_score * WEIGHTS_VEGETATION["saisonnalite_complete"]
        + fiabilite_score * WEIGHTS_VEGETATION["fiabilite_etudes"]
        + qualite_score * WEIGHTS_VEGETATION["qualite_preuve_pr"]
        + variabilite_score * WEIGHTS_VEGETATION["variabilite_taxonomique"]
        + consumables_ratio * WEIGHTS_VEGETATION["consumables_diversite"]
    )
    composite = round(composite, 2)

    br_nut = bio_reacteurs.get(espece, {}).get("bio_reacteur_outputs", {}).get("ENGINE_NUTRITION", {})
    br_params_count = len(br_nut.get("parametres_alimentes", {}))

    return {
        "super_engine_id": "ENGINE_VÉGÉTATION_Ω",
        "espece": espece,
        "computed_at_utc": _now(),
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "vegetation_availability_omega": composite,
        "seasonal_coverage": sorted(saisons_couvertes),
        "seasonal_coverage_ratio": round(saisonnalite_score, 2),
        "studies_count": len(studies_esp),
        "avg_confidence": round(fiabilite_score, 2),
        "peer_reviewed_ratio": round(qualite_score, 2),
        "consumables_expected": sorted(expected),
        "consumables_detected": sorted(consumables_found),
        "consumables_expected_match_ratio": round(consumables_ratio, 2),
        "scores_axes": {
            "coverage_studies_count": round(coverage_count_score, 2),
            "saisonnalite_complete": round(saisonnalite_score, 2),
            "fiabilite_etudes": round(fiabilite_score, 2),
            "qualite_preuve_pr": round(qualite_score, 2),
            "variabilite_taxonomique": round(variabilite_score, 2),
            "consumables_diversite": round(consumables_ratio, 2),
        },
        "bio_reacteur_params_count": br_params_count,
        "anti_generique_violations": violations,
        "anti_generique_pass": len(violations) == 0,
        "fallback_active": False,
        "interpolation_active": False,
    }


def compute_vegetation_all_especes() -> Dict[str, Any]:
    """Bundle Vegetation_Availability_Ω pour les 5 espèces."""
    studies = harmonize_nutrition_studies()
    bio = load_all_bio_reacteurs()
    results = {}
    for esp in ESPECES_CANONICAL:
        results[esp] = compute_vegetation_availability(esp, studies, bio)

    master = round(
        sum(r["vegetation_availability_omega"] for r in results.values()) / len(results), 2)
    total_violations = sum(len(r["anti_generique_violations"]) for r in results.values())
    return {
        "manifest_id": "ENGINE_VÉGÉTATION_Ω_BUNDLE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "computed_at_utc": _now(),
        "engine_lock_sha256": ENGINE_VEGETATION_Ω_LOCK_SHA256,
        "vegetation_master_score_omega": master,
        "results_par_espece": results,
        "anti_generique_violations_total": total_violations,
        "anti_generique_pass_global": total_violations == 0,
    }
