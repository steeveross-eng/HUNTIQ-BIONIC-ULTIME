"""
ENGINE_SOL_NUTRIMENTS_Ω — Nutriments minéraux et organiques du sol.
═══════════════════════════════════════════════════════════════════════════
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω (BCE-4X · STEEVE-MAX · 2026-04-27)
NIVEAU : BIOLOGIE (E37)
RÔLE : SECONDAIRE · PRIORITÉ : MAJEUR
DOCTRINE : V30 LOCKED · aucune dépendance cryptographique · AVAL seulement.

Module institutionnel read-only : évalue la charge en nutriments (N, P, K,
Ca, Mg, oligo-éléments) et matière organique du sol à partir de la typologie
renvoyée par ENGINE_SOL_SUPRA (E16).
"""
from typing import Dict, Any

ENGINE_NAME = "ENGINE_SOL_NUTRIMENTS_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"
ENGINE_LEVEL = "BIOLOGIE"
ENGINE_ROLE = "SECONDAIRE"
ENGINE_PRIORITY = "MAJEUR"

# Profils nutriments types par texture de sol
_SOIL_PROFILES = {
    "argileux":    {"N": 0.75, "P": 0.55, "K": 0.80, "Ca": 0.70, "Mg": 0.65, "OM": 0.70},
    "sablonneux":  {"N": 0.35, "P": 0.40, "K": 0.30, "Ca": 0.25, "Mg": 0.30, "OM": 0.25},
    "limoneux":    {"N": 0.65, "P": 0.60, "K": 0.60, "Ca": 0.55, "Mg": 0.50, "OM": 0.60},
    "humifere":    {"N": 0.90, "P": 0.70, "K": 0.75, "Ca": 0.85, "Mg": 0.80, "OM": 0.95},
    "tourbeux":    {"N": 0.80, "P": 0.45, "K": 0.40, "Ca": 0.30, "Mg": 0.55, "OM": 0.90},
    "rocheux":     {"N": 0.15, "P": 0.20, "K": 0.25, "Ca": 0.35, "Mg": 0.20, "OM": 0.10},
}


def compute_sol_nutriments(sol_meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    sol_meta = sol_meta or {}
    texture = str(sol_meta.get("texture", "limoneux")).lower()
    profile = _SOIL_PROFILES.get(texture, _SOIL_PROFILES["limoneux"])
    drainage = float(sol_meta.get("drainage", 0.5))
    fertility_score = round(
        profile["N"] * 0.25 + profile["P"] * 0.15 + profile["K"] * 0.15
        + profile["Ca"] * 0.10 + profile["Mg"] * 0.10 + profile["OM"] * 0.25, 3
    ) * min(1.2, 0.7 + drainage * 0.5)
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": ENGINE_LEVEL, "role": ENGINE_ROLE,
        "texture": texture,
        "nutrients_ratio": profile,  # 0..1 par nutriment
        "organic_matter_ratio": profile["OM"],
        "drainage_factor": drainage,
        "fertility_index": round(min(1.0, fertility_score), 3),
        "data_sources": ["ENGINE_SOL_SUPRA", "pedology_reference_QC"],
    }
