"""
ENGINE-RENDER-Ω — Moteur central de rendu TERRITOIRE (Phase XI-SUPRA)
=======================================================================
Source de vérité institutionnelle pour :
  - 14 couches obligatoires
  - Règles de zoom (macro / zones / détails)
  - Symbologie harmonisée
  - Validation payload de rendu

Endpoints :
  GET /api/v20/territoire/render-config
  POST /api/v20/territoire/render-validate  (payload bundle)
"""
from fastapi import APIRouter
from pydantic import BaseModel
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

register_engine(
    "ENGINE-RENDER-Ω",
    "V1-PHASE-XI-SUPRA-2026-04",
    "Moteur central rendu TERRITOIRE (14 couches + zoom + symbologie)",
    "GOUVERNANCE",
    [],
)

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Render"])

# ============================================================
# 14 COUCHES OBLIGATOIRES — ordre z-index montant
# ============================================================
LAYERS_REQUIRED = [
    {"id": "corridors", "order": 10, "bundle_key": "corridors", "zoom_min": 0, "symbology": "line-hierarchy"},
    {"id": "zones_ecologiques", "order": 20, "bundle_key": "zones", "zoom_min": 14, "symbology": "polygon-semi"},
    {"id": "zones_fauniques_canada", "order": 25, "bundle_key": "canada_zones_summary", "zoom_min": 0, "symbology": "polygon-semi"},
    {"id": "contamination_v2", "order": 30, "bundle_key": "contamination_v2_heatmap", "zoom_min": 0, "symbology": "heatmap-institutional"},
    {"id": "habitats_lep", "order": 35, "bundle_key": "lep_nearby", "zoom_min": 0, "symbology": "polygon-violet"},
    {"id": "zones_risque", "order": 40, "bundle_key": "zones_risque", "zoom_min": 0, "symbology": "polygon-alert"},
    {"id": "salines", "order": 50, "bundle_key": "salines", "zoom_min": 14, "symbology": "square-blue"},
    {"id": "hotspots", "order": 60, "bundle_key": "hotspots", "zoom_min": 14, "symbology": "circle-red"},
    {"id": "stations_hydat", "order": 65, "bundle_key": "hydat_nearby", "zoom_min": 14, "symbology": "point-lightblue"},
    {"id": "habitats_critiques", "order": 70, "bundle_key": "habitats_critiques", "zoom_min": 14, "symbology": "polygon-orange"},
    {"id": "deplacements_ia", "order": 75, "bundle_key": "deplacements_ia", "zoom_min": 16, "symbology": "line-dashed"},
    {"id": "affuts", "order": 80, "bundle_key": "affuts", "zoom_min": 16, "symbology": "triangle"},
    {"id": "points_observation", "order": 85, "bundle_key": "observations", "zoom_min": 16, "symbology": "pin-gold"},
    {"id": "score_local", "order": 90, "bundle_key": "score_local", "zoom_min": 0, "symbology": "overlay-label"},
]

# Règles de zoom institutionnelles
ZOOM_RULES = {
    "macro": {"range": "z<14", "layers": ["corridors", "contamination_v2", "habitats_lep", "zones_fauniques_canada", "zones_risque", "score_local"]},
    "mid": {"range": "14<=z<16", "layers": ["zones_ecologiques", "hotspots", "salines", "stations_hydat", "habitats_critiques"]},
    "detail": {"range": "z>=16", "layers": ["affuts", "points_observation", "deplacements_ia"]},
}

# Symbologie harmonisée (design system)
SYMBOLOGY = {
    "line-hierarchy": {
        "affut": {"type": "triangle", "color": "#C62828", "weight": 2.0},
        "corridor_extreme": {"type": "line", "color": "#D32F2F", "weight": 5},
        "corridor_intense": {"type": "line", "color": "#1976D2", "weight": 4},
        "corridor_modere": {"type": "line", "color": "#388E3C", "weight": 3},
    },
    "polygon-semi": {"fillOpacity": 0.25, "weight": 1.5, "color": "#2E7D32"},
    "heatmap-institutional": {"blur": 18, "radius": 22, "minOpacity": 0.4, "gradient": {"0.2": "#fff9c4", "0.5": "#f4511e", "0.9": "#880e4f"}},
    "polygon-violet": {"color": "#8E24AA", "fillColor": "#CE93D8", "fillOpacity": 0.35, "weight": 1.5},
    "polygon-alert": {"color": "#F57C00", "fillColor": "#FFE082", "fillOpacity": 0.30, "weight": 1.5, "dashArray": "4 4"},
    "square-blue": {"icon": "square", "color": "#1565C0", "size": 14},
    "circle-red": {"icon": "circle", "color": "#E53935", "size": 12},
    "point-lightblue": {"icon": "circle", "color": "#4FC3F7", "size": 7},
    "polygon-orange": {"color": "#E65100", "fillColor": "#FFCC80", "fillOpacity": 0.30, "weight": 1.5},
    "line-dashed": {"color": "#00796B", "weight": 2, "dashArray": "6 4"},
    "triangle": {"icon": "triangle", "color": "#C62828", "size": 16},
    "pin-gold": {"icon": "pin", "color": "#FFB300", "size": 14},
    "overlay-label": {"bg": "rgba(14,17,23,0.88)", "color": "#F3F4F6", "fontSize": 13, "pill": True},
}


def get_render_config() -> dict:
    mark_call("ENGINE-RENDER-Ω")
    return {
        "engine": "ENGINE-RENDER-Ω",
        "version": "V1-PHASE-XI-SUPRA-2026-04",
        "layers_required_count": len(LAYERS_REQUIRED),
        "layers": LAYERS_REQUIRED,
        "zoom_rules": ZOOM_RULES,
        "symbology": SYMBOLOGY,
    }


def validate_render_payload(bundle: dict) -> dict:
    """Vérifie que le bundle expose les 14 couches obligatoires.

    Accepte listes vides (couche vide ≠ couche manquante), refuse clés absentes.
    """
    mark_call("ENGINE-RENDER-Ω")
    missing = []
    present = []
    for layer in LAYERS_REQUIRED:
        key = layer["bundle_key"]
        if key in bundle:
            present.append(layer["id"])
        else:
            missing.append({"layer": layer["id"], "bundle_key": key})
    return {
        "engine": "ENGINE-RENDER-Ω",
        "required_total": len(LAYERS_REQUIRED),
        "present_count": len(present),
        "missing_count": len(missing),
        "missing": missing,
        "present": present,
        "conforme": len(missing) == 0,
    }


class BundleForValidation(BaseModel):
    bundle: dict


@router.get("/render-config")
async def v20_render_config():
    """ENGINE-RENDER-Ω : configuration rendu (14 couches + zoom + symbologie)."""
    return get_render_config()


@router.post("/render-validate")
async def v20_render_validate(payload: BundleForValidation):
    """Valide un payload bundle contre le registre des 14 couches obligatoires."""
    return validate_render_payload(payload.bundle)
