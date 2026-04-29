"""
engine_ia_omega.py — ENGINE IA Ω · ANALYSE INSTITUTIONNELLE
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · PHASE XV · BLOC 2

ENGINE_IA_Ω :
  - Analyse corrélative inter-engines (VISION, ODEUR, PATTERNS, COMPORTEMENT, SENSORIEL)
  - Analyse inter-espèces (5 espèces)
  - Analyse inter-saisonnière
  - Analyse inter-habitat
  - Détection d'anomalies
  - Détection de patterns multi-facteurs
  - Consolidation scientifique institutionnelle
  - AUCUN POUVOIR DÉCISIONNEL — Analyse uniquement.

Source EXCLUSIVE : 5 BIO_REACTEURS_Ω + 5 ENGINES SCIENTIFIQUES_Ω.
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime, timezone
from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
    load_bio_reacteur, ESPECES_SUPPORTEES,
)
from engines.v8_institutional.scientifique_omega.engine_vision_omega import compute as compute_vision
from engines.v8_institutional.scientifique_omega.engine_odeur_omega import compute as compute_odeur
from engines.v8_institutional.scientifique_omega.engine_patterns_omega import compute as compute_patterns
from engines.v8_institutional.scientifique_omega.engine_comportement_omega import compute as compute_comportement
from engines.v8_institutional.scientifique_omega.engine_sensoriel_omega import compute as compute_sensoriel


ENGINE_IA_SPEC: Dict[str, Any] = {
    "engine_id": "ENGINE_IA_Ω",
    "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
    "phase": "PHASE_XV_ENGINE_IA_Ω",
    "objectif_institutionnel": (
        "Analyse corrélative institutionnelle inter-engines, inter-espèces, "
        "inter-saisonnière, inter-habitat. Détection d'anomalies et patterns "
        "multi-facteurs. Consolidation scientifique. AUCUN POUVOIR DÉCISIONNEL."
    ),
    "engines_consumed": [
        "ENGINE_VISION_Ω", "ENGINE_ODEUR_Ω", "ENGINE_PATTERNS_Ω",
        "ENGINE_COMPORTEMENT_Ω", "ENGINE_SENSORIEL_Ω",
    ],
    "especes_consumed": list(ESPECES_SUPPORTEES),
    "exclusivement_bio_reacteur": True,
    "fallback_active": False,
    "interpolation_active": False,
    "anti_generique_strict": True,
    "decision_authority": False,
    "analyse_only": True,
    "version": "v1.0-PHASE_XV_Ω",
}


def _detect_corridor_overlaps(corridors_by_espece: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Détecte les corridors potentiellement partagés entre espèces."""
    out = []
    keys = list(corridors_by_espece.keys())
    for i, e1 in enumerate(keys):
        for e2 in keys[i+1:]:
            c1 = set(s.lower() for s in (corridors_by_espece[e1] or []))
            c2 = set(s.lower() for s in (corridors_by_espece[e2] or []))
            common = c1 & c2
            if common:
                out.append({
                    "espece_pair": [e1, e2],
                    "shared_corridor_terms_count": len(common),
                    "examples": list(common)[:3],
                })
    return out


def _detect_thermal_anomalies(thermal_by_espece: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Détecte les espèces ayant un seuil thermique critique."""
    anomalies = []
    for esp, val in thermal_by_espece.items():
        if val is None:
            anomalies.append({"espece": esp, "type": "seuil_thermique_NON_DOCUMENTE"})
        elif isinstance(val, (int, float)) and val < 20.0:
            anomalies.append({
                "espece": esp, "type": "seuil_thermique_critique",
                "valeur_C": val,
                "note": "Seuil < 20°C — espèce thermosensible (stress hivernal/estival critique)",
            })
    return anomalies


def _detect_snow_anomalies(snow_by_espece: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Détecte les seuils neige critiques."""
    anomalies = []
    for esp, val in snow_by_espece.items():
        if val is None:
            anomalies.append({"espece": esp, "type": "seuil_neige_NON_DOCUMENTE"})
        elif isinstance(val, (int, float)) and val < 30.0:
            anomalies.append({
                "espece": esp, "type": "seuil_neige_mobilite_critique",
                "valeur_cm": val,
                "note": "Seuil mobilité < 30 cm — vulnérabilité hivernale forte",
            })
    return anomalies


def _detect_seasonal_patterns(species_results: Dict[str, Dict]) -> Dict[str, Any]:
    """Détecte les patterns saisonniers actifs simultanés."""
    patterns = {
        "rut_actif_concurrents": [],
        "hyperphagie_active_concurrents": [],
        "ravages_hivernaux_concurrents": [],
        "nidification_active_concurrents": [],
    }
    for esp, ia_pkg in species_results.items():
        rep = (ia_pkg.get("patterns") or {}).get("reproduction") or {}
        if rep.get("rut_actif"):
            patterns["rut_actif_concurrents"].append(esp)
        comp = (ia_pkg.get("comportement") or {}).get("comportements_par_saison") or {}
        automne = comp.get("automne") or {}
        if isinstance(automne, dict) and automne.get("hyperphagie"):
            patterns["hyperphagie_active_concurrents"].append(esp)
        hiver = comp.get("hiver") or {}
        if isinstance(hiver, dict) and hiver.get("ravages"):
            patterns["ravages_hivernaux_concurrents"].append(esp)
        if rep.get("nidification_sites"):
            patterns["nidification_active_concurrents"].append(esp)
    return patterns


def _detect_human_pressure_concentration(odeur_by_espece: Dict[str, Dict]) -> Dict[str, Any]:
    """Synthèse cumulée des pressions humaines déclarées par espèce."""
    aggregate = {
        "routes_total_lines": 0,
        "agriculture_total_lines": 0,
        "urbanisation_total_lines": 0,
        "attractifs_anthropiques_total_lines": 0,
        "conflits_humains_total_lines": 0,
        "by_espece": {},
    }
    for esp, odeur in odeur_by_espece.items():
        sh = odeur.get("sources_humaines") or {}
        ek = {
            "routes": len(sh.get("routes") or []),
            "agriculture": len(sh.get("agriculture") or []),
            "urbanisation": len(sh.get("urbanisation") or []),
            "attractifs": len(sh.get("attractifs_anthropiques") or []),
            "conflits": len(sh.get("conflits_humains") or []),
        }
        aggregate["by_espece"][esp] = ek
        aggregate["routes_total_lines"] += ek["routes"]
        aggregate["agriculture_total_lines"] += ek["agriculture"]
        aggregate["urbanisation_total_lines"] += ek["urbanisation"]
        aggregate["attractifs_anthropiques_total_lines"] += ek["attractifs"]
        aggregate["conflits_humains_total_lines"] += ek["conflits"]
    return aggregate


def compute_ia(env: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Exécute les 5 ENGINES SCIENTIFIQUES_Ω sur les 5 espèces puis applique
    l'analyse corrélative institutionnelle. Aucun pouvoir décisionnel."""
    env = env or {}
    species_results = {}
    corridors_by_espece = {}
    thermal_by_espece = {}
    snow_by_espece = {}
    odeur_by_espece = {}

    for esp in ESPECES_SUPPORTEES:
        v = compute_vision(esp, env)
        o = compute_odeur(esp, env)
        p = compute_patterns(esp, env)
        c = compute_comportement(esp, env)
        s = compute_sensoriel(esp, env)
        species_results[esp] = {
            "vision": v, "odeur": o, "patterns": p,
            "comportement": c, "sensoriel": s,
        }
        # Aggrégats
        cz = (v.get("zones_critiques") or {}).get("rut") or []
        # corridors_reels_gps via patterns
        corridors_by_espece[esp] = (p.get("deplacements") or {}).get("zones_passage_essentielles") or []
        thermal_by_espece[esp] = (s.get("thermosensibilite") or {}).get("seuil_stress_C")
        snow_by_espece[esp] = (s.get("neige") or {}).get("seuil_mobilite_cm")
        odeur_by_espece[esp] = o

    correlations = {
        "corridors_overlaps_inter_especes": _detect_corridor_overlaps(corridors_by_espece),
        "anomalies_thermiques": _detect_thermal_anomalies(thermal_by_espece),
        "anomalies_neige": _detect_snow_anomalies(snow_by_espece),
        "patterns_saisonniers_simultanes": _detect_seasonal_patterns(species_results),
        "pression_humaine_concentration": _detect_human_pressure_concentration(odeur_by_espece),
    }

    bio_reacteurs_sha = {
        esp: load_bio_reacteur(esp).get("_runtime_sha256")
        for esp in ESPECES_SUPPORTEES
    }

    return {
        "engine_id": "ENGINE_IA_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XV_ENGINE_IA_Ω",
        "computed_at_utc": datetime.now(timezone.utc).isoformat(),
        "engines_consumed": ENGINE_IA_SPEC["engines_consumed"],
        "especes_consumed": ENGINE_IA_SPEC["especes_consumed"],
        "decision_authority": False,
        "analyse_only": True,
        "bio_reacteurs_runtime_sha256": bio_reacteurs_sha,
        "correlations": correlations,
        "consolidation_scientifique_institutionnelle": {
            "engines_executed": 25,  # 5 espèces × 5 engines scientifiques
            "anomalies_count": (
                len(correlations["anomalies_thermiques"]) + len(correlations["anomalies_neige"])
            ),
            "corridors_overlaps_count": len(correlations["corridors_overlaps_inter_especes"]),
        },
        "exclusivement_bio_reacteur": True,
        "fallback_active": False,
        "interpolation_active": False,
        "by_espece_summary": {
            esp: {
                "vision_keys": list(species_results[esp]["vision"].keys()),
                "odeur_keys": list(species_results[esp]["odeur"].keys()),
                "patterns_keys": list(species_results[esp]["patterns"].keys()),
                "comportement_keys": list(species_results[esp]["comportement"].keys()),
                "sensoriel_keys": list(species_results[esp]["sensoriel"].keys()),
            }
            for esp in ESPECES_SUPPORTEES
        },
    }
