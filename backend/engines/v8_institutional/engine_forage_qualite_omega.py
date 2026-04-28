"""
ENGINE_FORAGE_QUALITÉ_Ω — Qualité nutritionnelle des végétaux disponibles.
═══════════════════════════════════════════════════════════════════════════
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω
NIVEAU : BIOLOGIE (E38) · RÔLE : PRINCIPAL · PRIORITÉ : MAJEUR
"""
from typing import Dict, Any, List

ENGINE_NAME = "ENGINE_FORAGE_QUALITÉ_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

# Qualités de fourrage par habitat × saison
_FORAGE_INDEX = {
    "foret_feuillus":     {"spring": 0.75, "summer": 0.85, "fall": 0.90, "winter": 0.35},
    "foret_resineux":     {"spring": 0.55, "summer": 0.50, "fall": 0.45, "winter": 0.40},
    "foret_melangee":     {"spring": 0.75, "summer": 0.80, "fall": 0.85, "winter": 0.40},
    "milieu_humide":      {"spring": 0.95, "summer": 0.90, "fall": 0.70, "winter": 0.45},
    "transition":         {"spring": 0.80, "summer": 0.75, "fall": 0.70, "winter": 0.40},
    "agricole":           {"spring": 0.85, "summer": 0.95, "fall": 1.00, "winter": 0.35},
    "ravage":             {"spring": 0.40, "summer": 0.45, "fall": 0.55, "winter": 0.75},
}


def _season_of(month: int) -> str:
    if month in (3, 4, 5): return "spring"
    if month in (6, 7, 8): return "summer"
    if month in (9, 10, 11): return "fall"
    return "winter"


def compute_forage_quality(habitats_critiques: List[Dict[str, Any]] | None,
                           month: int = 10) -> Dict[str, Any]:
    habitats_critiques = habitats_critiques or []
    season = _season_of(int(month))
    scores = []
    by_habitat = {}
    for h in habitats_critiques:
        htype = str(h.get("type") or h.get("category") or "foret_melangee").lower()
        idx = _FORAGE_INDEX.get(htype, _FORAGE_INDEX["foret_melangee"])
        s = idx[season]
        by_habitat[htype] = round(s, 3)
        scores.append(s)
    mean = round(sum(scores) / len(scores), 3) if scores else 0.6
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "BIOLOGIE", "role": "PRINCIPAL",
        "season": season,
        "forage_quality_index": mean,
        "per_habitat": by_habitat,
        "data_sources": ["ENGINE_HABITAT_SUPRA", "MFFP_guides_forestiers"],
    }
