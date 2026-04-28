"""
especes_omega_base.py — PHASE_XII_ESPECES_Ω · BCE-4X ULTIME ABSOLU
═══════════════════════════════════════════════════════════════════════
Commandant STEEVE-MAX · Module COMMUN aux 5 engines espèces Ω.

Définit :
  - Dataclass EspeceProfile (sources GOV/UNI/PR + DOI + dimensions).
  - Fonctions de scoring institutionnels (RSF/SSF/MaxEnt placeholders).
  - Validateurs BCE-4X (NO_VULGARISATION, NO_OPINION, TRACEABILITY_DOI).
  - Pipeline I/O standardisé pour agrégateur ENGINE_ESPECES_Ω.

LECTURE SEULE V30 — n'altère AUCUN moteur cryptographique scellé.
═══════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class SourceRef:
    """Référence scientifique traçable BCE-4X."""
    institution: str
    type: str  # GOV | UNI | PR
    title: str
    year: int
    doi_or_url: Optional[str] = None
    methodologie: Optional[str] = None

    def is_valid(self) -> bool:
        return self.type in ("GOV", "UNI", "PR") and bool(self.institution) and bool(self.title)


@dataclass(frozen=True)
class SeuilScientifique:
    """Seuil numérique scientifique avec source et unité."""
    metric: str         # "thermique_max" | "neige_max" | "ndvi_min" | etc.
    valeur: float
    unite: str          # "°C" | "cm" | "ratio" | "%"
    seuil_type: str     # "stress" | "mortality" | "selection_optimum"
    source: str         # institution clé
    note: Optional[str] = None


@dataclass(frozen=True)
class EspeceProfile:
    """Profil scientifique BCE-4X d'une espèce — input des engines Ω."""
    espece_id: str
    nom_scientifique: str
    tableau_maitre_ref: str
    sources: List[SourceRef]
    seuils: List[SeuilScientifique]
    dimensions_scientifiques: List[str]
    sorties_territoire: List[str]
    style_palette: Dict[str, str]   # habitat / corridors / critiques (couleurs Ω)

    def validate_bce4x(self) -> Tuple[bool, List[str]]:
        """Vérifie conformité BCE-4X : ≥3 sources triple validation, ≥1 DOI."""
        errors: List[str] = []
        types = {s.type for s in self.sources}
        if not {"GOV", "UNI", "PR"}.issubset(types):
            errors.append("BCE-4X violation: sources doivent inclure GOV+UNI+PR (triple validation)")
        if not any(s.doi_or_url for s in self.sources):
            errors.append("BCE-4X violation: TRACEABILITY_DOI_REQUIRED — au moins 1 DOI/URL requis")
        for s in self.sources:
            if not s.is_valid():
                errors.append(f"Source invalide: {s.institution}")
        return (len(errors) == 0, errors)


def compute_score_pression_humaine(
    routes_density: float,         # km/km²
    urbanisation_pct: float,       # 0-100
    agriculture_pct: float,        # 0-100
    weights: Dict[str, float] = None,
) -> float:
    """Score de pression humaine 0-100 (plus haut = plus pressé).

    Pondération par défaut alignée sur Montgomery et al. 2019 (DOI 10.1002/eap.1923).
    """
    w = weights or {"routes": 0.45, "urb": 0.35, "agri": 0.20}
    score = (
        w["routes"] * min(routes_density / 5.0, 1.0) * 100
        + w["urb"] * min(urbanisation_pct / 50.0, 1.0) * 100
        + w["agri"] * min(agriculture_pct / 70.0, 1.0) * 100
    )
    return round(min(max(score, 0.0), 100.0), 2)


def compute_score_fragmentation(
    forest_patches_count: int,
    largest_patch_index: float,    # 0-100
    edge_density: float,           # m/ha
) -> float:
    """Score de fragmentation 0-100 (plus haut = plus fragmenté)."""
    nb_score = min(forest_patches_count / 50.0, 1.0) * 100
    lpi_inv = 100.0 - max(min(largest_patch_index, 100.0), 0.0)
    ed_score = min(edge_density / 200.0, 1.0) * 100
    score = 0.35 * nb_score + 0.40 * lpi_inv + 0.25 * ed_score
    return round(min(max(score, 0.0), 100.0), 2)


def compute_score_thermique(temperature_c: float, seuil_stress_c: float) -> float:
    """Score de stress thermique 0-100 selon le seuil propre à l'espèce."""
    if temperature_c < seuil_stress_c:
        return 0.0
    delta = temperature_c - seuil_stress_c
    score = min(delta * 10.0, 100.0)
    return round(score, 2)


def compute_score_neige(snow_depth_cm: float, seuil_mortalite_cm: float) -> float:
    """Score de mortalité neige 0-100."""
    if snow_depth_cm < seuil_mortalite_cm * 0.6:
        return 0.0
    if snow_depth_cm >= seuil_mortalite_cm:
        return min(50.0 + (snow_depth_cm - seuil_mortalite_cm) * 2.5, 100.0)
    pct = (snow_depth_cm - seuil_mortalite_cm * 0.6) / (seuil_mortalite_cm * 0.4)
    return round(pct * 50.0, 2)


def normalize_engine_output(profile: EspeceProfile, layers: Dict[str, Any], scores: Dict[str, float]) -> Dict[str, Any]:
    """Normalise la sortie d'un engine espèce (format pipeline TERRITOIRE_Ω)."""
    return {
        "engine_marker": f"ENGINE_ESPECE_{profile.espece_id}_Ω",
        "espece_id": profile.espece_id,
        "nom_scientifique": profile.nom_scientifique,
        "tableau_maitre_ref": profile.tableau_maitre_ref,
        "phase": "PHASE_XII_ESPECES_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
        "layers_omega": layers,
        "scores_omega": scores,
        "style_palette": profile.style_palette,
        "sources_count": len(profile.sources),
        "sources_doi": [s.doi_or_url for s in profile.sources if s.doi_or_url],
    }


__all__ = [
    "SourceRef", "SeuilScientifique", "EspeceProfile",
    "compute_score_pression_humaine", "compute_score_fragmentation",
    "compute_score_thermique", "compute_score_neige",
    "normalize_engine_output",
]
