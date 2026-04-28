"""
ENGINE_CARENCE_NUTRITIONNELLE_Ω — Détection de carences par espèce.
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : BIOLOGIE (E39)
RÔLE : SECONDAIRE · PRIORITÉ : MAJEUR
"""
from typing import Dict, Any

ENGINE_NAME = "ENGINE_CARENCE_NUTRITIONNELLE_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

# Besoins minéraux relatifs par espèce (1.0 = référence nominale)
_NEEDS = {
    "orignal":         {"Na": 1.30, "Ca": 1.15, "P": 1.05, "Mg": 1.00, "K": 1.05},
    "chevreuil":       {"Na": 1.20, "Ca": 1.10, "P": 1.00, "Mg": 0.95, "K": 1.05},
    "cerf":            {"Na": 1.20, "Ca": 1.10, "P": 1.00, "Mg": 0.95, "K": 1.05},
    "ours_noir":       {"Na": 0.90, "Ca": 1.20, "P": 1.15, "Mg": 0.90, "K": 1.00},
    "ours":            {"Na": 0.90, "Ca": 1.20, "P": 1.15, "Mg": 0.90, "K": 1.00},
    "dindon_sauvage":  {"Na": 0.60, "Ca": 1.35, "P": 1.15, "Mg": 0.80, "K": 0.95},
    "dindon":          {"Na": 0.60, "Ca": 1.35, "P": 1.15, "Mg": 0.80, "K": 0.95},
    "wapiti":          {"Na": 1.25, "Ca": 1.15, "P": 1.10, "Mg": 1.00, "K": 1.05},
}


def compute_carence(species: str, sol_nutriments: Dict[str, Any] | None,
                    forage_quality: Dict[str, Any] | None) -> Dict[str, Any]:
    key = str(species or "orignal").lower()
    needs = _NEEDS.get(key, _NEEDS["orignal"])
    avail = (sol_nutriments or {}).get("nutrients_ratio") or {}
    forage = (forage_quality or {}).get("forage_quality_index", 0.6)
    deficits = {}
    for nut, need in needs.items():
        got = avail.get(nut) or avail.get(nut.capitalize()) or 0.5
        # Ajustement forage × disponibilité
        effective = got * (0.7 + 0.3 * forage)
        diff = need - effective
        if diff > 0:
            deficits[nut] = round(diff, 3)
    total_def = round(sum(deficits.values()), 3)
    risk = "FAIBLE" if total_def < 0.3 else ("MODÉRÉ" if total_def < 0.7 else "ÉLEVÉ")
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "BIOLOGIE", "role": "SECONDAIRE",
        "species": key,
        "deficits_vs_needs": deficits,
        "total_deficit_score": total_def,
        "carence_risk": risk,
        "data_sources": ["ENGINE_SOL_NUTRIMENTS_Ω", "ENGINE_FORAGE_QUALITÉ_Ω"],
    }
