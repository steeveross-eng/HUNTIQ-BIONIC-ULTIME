"""
ENGINE_TROPHIC_BEHAVIOR_Ω — Comportement trophique par espèce et contexte.
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : BIOLOGIE (E44)
RÔLE : SECONDAIRE · PRIORITÉ : MAJEUR
"""
from typing import Dict, Any

ENGINE_NAME = "ENGINE_TROPHIC_BEHAVIOR_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

_TROPHIC_TYPE = {
    "orignal":         "Herbivore ruminant brouteur aquatique/forestier",
    "chevreuil":       "Herbivore ruminant sélectif",
    "cerf":            "Herbivore ruminant sélectif",
    "ours_noir":       "Omnivore opportuniste",
    "ours":            "Omnivore opportuniste",
    "dindon_sauvage":  "Granivore + insectivore saisonnier",
    "dindon":          "Granivore + insectivore saisonnier",
    "wapiti":          "Herbivore ruminant grand brouteur",
}

_ACTIVITY_WINDOWS = {
    "orignal":   {"dawn": 0.9, "day": 0.2, "dusk": 1.0, "night": 0.7},
    "chevreuil": {"dawn": 1.0, "day": 0.3, "dusk": 0.95, "night": 0.5},
    "cerf":      {"dawn": 1.0, "day": 0.3, "dusk": 0.95, "night": 0.5},
    "ours_noir": {"dawn": 0.6, "day": 0.8, "dusk": 0.9, "night": 0.5},
    "ours":      {"dawn": 0.6, "day": 0.8, "dusk": 0.9, "night": 0.5},
    "dindon_sauvage": {"dawn": 0.9, "day": 1.0, "dusk": 0.7, "night": 0.0},
    "dindon":    {"dawn": 0.9, "day": 1.0, "dusk": 0.7, "night": 0.0},
    "wapiti":    {"dawn": 0.9, "day": 0.4, "dusk": 1.0, "night": 0.5},
}


def _window_of(hour: int) -> str:
    if 4 <= hour < 8: return "dawn"
    if 8 <= hour < 17: return "day"
    if 17 <= hour < 21: return "dusk"
    return "night"


def compute_trophic(species: str, hour: int = 7,
                    forage_quality: Dict[str, Any] | None = None,
                    champs_nourriciers: Dict[str, Any] | None = None) -> Dict[str, Any]:
    key = str(species or "orignal").lower()
    window = _window_of(int(hour))
    activity = (_ACTIVITY_WINDOWS.get(key, _ACTIVITY_WINDOWS["orignal"]))[window]
    foraging_pressure = round(
        activity * (0.5 + 0.5 * float((forage_quality or {}).get("forage_quality_index", 0.6)))
        + 0.2 * float((champs_nourriciers or {}).get("mean_attractiveness", 0.0)), 3
    )
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "BIOLOGIE", "role": "SECONDAIRE",
        "species": key,
        "trophic_type": _TROPHIC_TYPE.get(key, "inconnu"),
        "activity_window": window,
        "activity_score": activity,
        "foraging_pressure_index": foraging_pressure,
        "data_sources": ["ENGINE_SPECIES_PROFILES_Ω", "ENGINE_FORAGE_QUALITÉ_Ω"],
    }
