"""
ENGINE_CHAMPS_NOURRICIERS_Ω — Détection et scoring des champs nourriciers.
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : BIOLOGIE (E41)
RÔLE : SECONDAIRE · PRIORITÉ : MAJEUR
"""
from typing import Dict, Any, List

ENGINE_NAME = "ENGINE_CHAMPS_NOURRICIERS_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

_CROP_ATTRACT = {
    "mais":     {"orignal": 0.70, "chevreuil": 0.95, "ours": 0.85, "dindon": 1.00, "wapiti": 0.85},
    "soya":     {"orignal": 0.40, "chevreuil": 0.80, "ours": 0.55, "dindon": 0.70, "wapiti": 0.55},
    "luzerne":  {"orignal": 0.85, "chevreuil": 0.90, "ours": 0.30, "dindon": 0.35, "wapiti": 0.90},
    "avoine":   {"orignal": 0.70, "chevreuil": 0.75, "ours": 0.40, "dindon": 0.85, "wapiti": 0.75},
    "pomme":    {"orignal": 0.75, "chevreuil": 0.80, "ours": 0.95, "dindon": 0.50, "wapiti": 0.70},
}


def compute_champs_nourriciers(zones: List[Dict[str, Any]] | None,
                               species: str = "orignal",
                               month: int = 10) -> Dict[str, Any]:
    zones = zones or []
    key = str(species or "orignal").lower().replace("_sauvage", "").replace("_noir", "")
    fields = []
    total_score = 0.0
    for z in zones:
        ztype = str(z.get("type") or z.get("category") or "").lower()
        if ztype in ("agricole", "champs", "culture"):
            crop = str(z.get("crop") or z.get("subtype") or "mais").lower()
            attract = _CROP_ATTRACT.get(crop, _CROP_ATTRACT["mais"]).get(key, 0.5)
            season_factor = 1.2 if month in (8, 9, 10) else (0.9 if month in (6, 7) else 0.5)
            score = round(attract * season_factor, 3)
            fields.append({"lat": z.get("lat"), "lng": z.get("lng"),
                           "crop": crop, "attractiveness": score})
            total_score += score
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "BIOLOGIE", "role": "SECONDAIRE",
        "species": species,
        "month": month,
        "fields_count": len(fields),
        "mean_attractiveness": round(total_score / len(fields), 3) if fields else 0.0,
        "fields": fields,
        "data_sources": ["ENGINE_ZONES", "MAPAQ_rotations"],
    }
