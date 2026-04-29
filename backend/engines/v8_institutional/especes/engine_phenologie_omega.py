"""
engine_phenologie_omega.py — PHASE XVII · ENGINE_PHÉNOLOGIE_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°37

ENGINE scientifique autonome consommant :
  • Études nutrition + habitat fusionnées (saisonnalité inter-espèces)
  • Les BIO_REACTEURS_Ω.ENGINE_COMPORTEMENT
  • Aucun legacy, aucun fallback, aucune interpolation.

Sortie principale :
  compute_phenology_seasonal_index(espece) → Phenology_Seasonal_Index_Ω ∈ [0, 100]
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from .bio_reacteur_loader_omega import load_all_bio_reacteurs
from .datasets_science_omega import (
    harmonize_nutrition_studies, harmonize_habitat_studies,
    ESPECES_CANONICAL, SAISONS_CANONICAL,
)


__all__ = [
    "compute_phenology_seasonal_index",
    "compute_phenology_all_especes",
    "ENGINE_PHENOLOGIE_Ω_LOCK_SHA256",
    "ENGINE_PHENOLOGIE_SPEC",
]


WEIGHTS_PHENO = {
    "saisonnalite_full": 0.30,           # couverture des 4 saisons (nut+hab)
    "documented_events_count": 0.20,      # événements phénologiques documentés
    "fiabilite_etudes": 0.15,
    "behavior_signals": 0.15,             # rut, hyperphagie, migration, nidification
    "saisons_critiques_couvertes": 0.10,  # saisons critiques dietz/habitat
    "convergence_datasets": 0.10,         # concordance nut + hab
}

# Événements phénologiques canoniques à détecter dans le focus des études
PHENO_EVENTS = {
    "rut": ["rut", "brame", "breeding season"],
    "hyperphagie": ["hyperphagie", "engraissement", "pré-hivern", "fattening"],
    "mise_bas": ["mise bas", "parturition", "faonnage", "fawning"],
    "migration": ["migrat", "dispersion", "saisonnière"],
    "hibernation": ["hibernation", "tanière", "denning"],
    "nidification": ["nidif", "nesting", "dortoir", "roosting"],
    "mue": ["mue", "molting"],
    "parade": ["parade", "display", "lekking"],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


ENGINE_PHENOLOGIE_SPEC = {
    "id": "ENGINE_PHÉNOLOGIE_Ω",
    "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
    "input_sources": ["SCI_Ω.nutrition_studies", "SCI_Ω.habitat_studies",
                      "BIO_REACTEURS_Ω.ENGINE_COMPORTEMENT"],
    "weights": WEIGHTS_PHENO,
    "output_signature": [
        "phenology_seasonal_index_omega",
        "seasonal_coverage_full",
        "phenological_events_detected",
        "critical_seasons_covered",
        "nut_hab_convergence_ratio",
        "anti_generique_violations",
    ],
}
ENGINE_PHENOLOGIE_Ω_LOCK_SHA256 = _sha_str(json.dumps(ENGINE_PHENOLOGIE_SPEC, sort_keys=True,
                                                        ensure_ascii=False))

CONFIDENCE_SCORE = {"ÉLEVÉ": 100.0, "MOYEN": 60.0, "FAIBLE": 25.0, "INCONNU": 0.0}

# Saisons critiques par espèce (scientifiquement sourcées)
SAISONS_CRITIQUES_PAR_ESPECE = {
    "CHEVREUIL": ["HIVER"],                        # mortalité hivernale ravages
    "ORIGNAL": ["HIVER", "AUTOMNE"],               # rut + mortalité hiver
    "OURS_NOIR": ["AUTOMNE", "HIVER"],             # hyperphagie + hibernation
    "WAPITI": ["AUTOMNE", "HIVER"],                # rut + mortalité
    "DINDON_SAUVAGE": ["PRINTEMPS", "HIVER"],      # nidif + mortalité nivale
}


def _detect_pheno_events(studies: List[Dict[str, Any]]) -> Dict[str, int]:
    """Compte les événements phénologiques détectés textuellement."""
    counts = {k: 0 for k in PHENO_EVENTS}
    for s in studies:
        # focus + bloc (nutrition) OU titre (habitat)
        if "focus" in s:
            txt = f"{s['focus']} {s.get('bloc_id', '')}".lower()
        else:
            txt = s.get("titre", "").lower()
        for event, keywords in PHENO_EVENTS.items():
            if any(kw in txt for kw in keywords):
                counts[event] += 1
    return counts


def compute_phenology_seasonal_index(espece: str,
                                       nutrition_studies: List[Dict[str, Any]] | None = None,
                                       habitat_studies: List[Dict[str, Any]] | None = None,
                                       bio_reacteurs: Dict[str, Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """Calcule Phenology_Seasonal_Index_Ω pour une espèce."""
    if espece not in ESPECES_CANONICAL:
        raise ValueError(f"ESPECE_NON_CANONIQUE::{espece}")

    if nutrition_studies is None:
        nutrition_studies = harmonize_nutrition_studies()
    if habitat_studies is None:
        habitat_studies = harmonize_habitat_studies()
    if bio_reacteurs is None:
        bio_reacteurs = load_all_bio_reacteurs()

    violations: List[str] = []

    # Études pertinentes
    nut_esp = [s for s in nutrition_studies if espece in s["especes_canoniques"]]
    hab_esp = [s for s in habitat_studies if s["espece_canonique"] == espece]
    all_esp = nut_esp + hab_esp
    if not all_esp:
        violations.append(f"{espece}::ENGINE_PHENOLOGIE::NO_STUDIES")

    # AXE 1 — Couverture saisons (nutrition fournit seule les saisons)
    saisons_nut = set()
    for s in nut_esp:
        for sa in s["saisons_canoniques"]:
            saisons_nut.add(sa)
    saisonnalite_score = (len(saisons_nut & set(SAISONS_CANONICAL)) / 4.0) * 100.0

    # AXE 2 — Événements phénologiques détectés
    pheno_counts = _detect_pheno_events(all_esp)
    events_found = sum(1 for v in pheno_counts.values() if v > 0)
    # Saturation à 6 événements distincts = 100
    events_score = min(100.0, (events_found / 6.0) * 100.0)

    # AXE 3 — Fiabilité études (combinée nut + hab)
    conf_vals = []
    for s in all_esp:
        key = "niveau_confiance" if "niveau_confiance" in s else "niveau_confiance"
        conf_vals.append(CONFIDENCE_SCORE.get(s.get(key, "INCONNU"), 0.0))
    fiabilite_score = sum(conf_vals) / len(conf_vals) if conf_vals else 0.0

    # AXE 4 — Signaux comportementaux forts (rut, hyperphagie, hibernation…)
    strong_signals = ["rut", "hyperphagie", "hibernation", "nidification"]
    signals_found = sum(1 for sig in strong_signals if pheno_counts[sig] > 0)
    signals_score = (signals_found / len(strong_signals)) * 100.0

    # AXE 5 — Saisons critiques couvertes
    critiques = set(SAISONS_CRITIQUES_PAR_ESPECE.get(espece, []))
    if not critiques:
        critiques_score = 0.0
        violations.append(f"{espece}::ENGINE_PHENOLOGIE::NO_CRITICAL_SEASONS_DEFINED")
    else:
        critiques_found = critiques & saisons_nut
        critiques_score = (len(critiques_found) / len(critiques)) * 100.0

    # AXE 6 — Convergence datasets (au moins 1 nut + 1 hab pour l'espèce)
    has_nut = len(nut_esp) > 0
    has_hab = len(hab_esp) > 0
    if has_nut and has_hab:
        convergence_score = 100.0
    elif has_nut or has_hab:
        convergence_score = 50.0
    else:
        convergence_score = 0.0
        violations.append(f"{espece}::ENGINE_PHENOLOGIE::NO_DATASET_CONVERGENCE")

    # Composite
    composite = (
        saisonnalite_score * WEIGHTS_PHENO["saisonnalite_full"]
        + events_score * WEIGHTS_PHENO["documented_events_count"]
        + fiabilite_score * WEIGHTS_PHENO["fiabilite_etudes"]
        + signals_score * WEIGHTS_PHENO["behavior_signals"]
        + critiques_score * WEIGHTS_PHENO["saisons_critiques_couvertes"]
        + convergence_score * WEIGHTS_PHENO["convergence_datasets"]
    )
    composite = round(composite, 2)

    # BR comportement (params)
    br_comp = bio_reacteurs.get(espece, {}).get("bio_reacteur_outputs", {}).get("ENGINE_COMPORTEMENT", {})
    br_params_count = len(br_comp.get("parametres_alimentes", {}))

    return {
        "super_engine_id": "ENGINE_PHÉNOLOGIE_Ω",
        "espece": espece,
        "computed_at_utc": _now(),
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phenology_seasonal_index_omega": composite,
        "seasonal_coverage_full": sorted(saisons_nut),
        "seasonal_coverage_ratio": round(saisonnalite_score, 2),
        "phenological_events_detected": {k: v for k, v in pheno_counts.items() if v > 0},
        "critical_seasons_expected": sorted(critiques),
        "critical_seasons_covered": sorted(critiques & saisons_nut) if critiques else [],
        "nut_hab_convergence_ratio": round(convergence_score, 2),
        "studies_nut_count": len(nut_esp),
        "studies_hab_count": len(hab_esp),
        "scores_axes": {
            "saisonnalite_full": round(saisonnalite_score, 2),
            "documented_events_count": round(events_score, 2),
            "fiabilite_etudes": round(fiabilite_score, 2),
            "behavior_signals": round(signals_score, 2),
            "saisons_critiques_couvertes": round(critiques_score, 2),
            "convergence_datasets": round(convergence_score, 2),
        },
        "bio_reacteur_params_count": br_params_count,
        "anti_generique_violations": violations,
        "anti_generique_pass": len(violations) == 0,
        "fallback_active": False,
        "interpolation_active": False,
    }


def compute_phenology_all_especes() -> Dict[str, Any]:
    """Bundle Phenology_Seasonal_Index_Ω pour les 5 espèces."""
    nut = harmonize_nutrition_studies()
    hab = harmonize_habitat_studies()
    bio = load_all_bio_reacteurs()
    results = {}
    for esp in ESPECES_CANONICAL:
        results[esp] = compute_phenology_seasonal_index(esp, nut, hab, bio)

    master = round(
        sum(r["phenology_seasonal_index_omega"] for r in results.values()) / len(results), 2)
    total_violations = sum(len(r["anti_generique_violations"]) for r in results.values())
    return {
        "manifest_id": "ENGINE_PHÉNOLOGIE_Ω_BUNDLE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "computed_at_utc": _now(),
        "engine_lock_sha256": ENGINE_PHENOLOGIE_Ω_LOCK_SHA256,
        "phenology_master_score_omega": master,
        "results_par_espece": results,
        "anti_generique_violations_total": total_violations,
        "anti_generique_pass_global": total_violations == 0,
    }
