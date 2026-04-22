"""
ENGINE_ECO_ZONES_Ω — Implémentation X200 P0
=============================================
Phase     : X200-P0-ACTIVATION
Priorité  : P0 #2 (20 salines hiérarchisées + zones vitales 6 types)

RESTAURATION V7 ULTIME :
- Source salines : `modules/salines_ultime_engine/router.py` (5 scores × 20 sources)
- Source nutrition : `modules/nutrition_engine_v7/pipeline.py` (Sol→Nutriments→Fourrage→Gibier)
- Classification habitat 4 niveaux (OPTIMAL/FONCTIONNEL/DÉGRADÉ/INUTILISABLE)
- Types zones vitales : salines, alimentation, repos, rut, thermique, humide
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse

FEATURE_FLAG_ACTIVE: bool = True
ENGINE_ID = "ENGINE_ECO_ZONES_Ω"
PHASE = "X200-P0-ACTIVATION"

# Seuils de classification habitat V7
HABITAT_THRESHOLDS = {
    "OPTIMAL":      {"min": 75, "color": "#2E7D32"},
    "FONCTIONNEL":  {"min": 50, "color": "#689F38"},
    "DEGRADE":      {"min": 25, "color": "#F57C00"},
    "INUTILISABLE": {"min": 0,  "color": "#D32F2F"},
}

# 6 types de zones vitales V7
VITAL_ZONE_TYPES = ("salines", "alimentation", "repos", "rut", "thermique", "humide")

# Catalogue des 20 sources salines V7 (hiérarchisées par score moyen)
SALINE_SOURCES_V7 = [
    # Score 5 (critique)
    {"id": "mfffp_salines_officielles",    "score": 5, "desc": "Inventaire officiel MFFP Québec"},
    {"id": "bdre_salines_validated",        "score": 5, "desc": "Base de données régionale - validé terrain"},
    {"id": "lidar_saline_signatures",       "score": 5, "desc": "Signatures LiDAR minéralisées"},
    # Score 4 (fort)
    {"id": "hydro_concentration_mineraux",  "score": 4, "desc": "Concentration minérale hydro-détectée"},
    {"id": "vegetation_halophyte_ndvi",     "score": 4, "desc": "Signature végétation halophyte NDVI"},
    {"id": "soil_salinity_mapping",          "score": 4, "desc": "Cartographie salinité sol"},
    {"id": "wildlife_traces_clustering",    "score": 4, "desc": "Clusters de traces faune (pins EXPERT)"},
    # Score 3 (majeur)
    {"id": "mineral_outcrops",              "score": 3, "desc": "Affleurements minéraux détectés"},
    {"id": "wet_depression_mineral",        "score": 3, "desc": "Dépressions humides minéralisées"},
    {"id": "riparian_mineral_zones",        "score": 3, "desc": "Zones riveraines minéralisées"},
    {"id": "ecoforest_successional",        "score": 3, "desc": "Stades successionnels favorables" },
    # Score 2 (modéré)
    {"id": "topographic_convergence",       "score": 2, "desc": "Convergence topographique"},
    {"id": "canopy_gap_density",            "score": 2, "desc": "Densité trouées canopée"},
    {"id": "snowmelt_mineral_accumulation", "score": 2, "desc": "Accumulation minérale fonte"},
    {"id": "ia_vision_predicted",           "score": 2, "desc": "Prédiction IA Vision"},
    # Score 1 (faible/indicatif)
    {"id": "historical_patterns",           "score": 1, "desc": "Patterns historiques"},
    {"id": "user_reports_unverified",       "score": 1, "desc": "Signalements utilisateurs non vérifiés"},
    {"id": "climate_projected",             "score": 1, "desc": "Projections climatiques"},
    {"id": "harvester_federal",             "score": 1, "desc": "Harvester fédéral national"},
    {"id": "crowd_sourced_annotations",     "score": 1, "desc": "Annotations crowd-sourcées"},
]


def classify_habitat(score: float) -> Dict[str, Any]:
    """Classification 4 niveaux V7 par score 0-100."""
    for level, cfg in HABITAT_THRESHOLDS.items():
        if score >= cfg["min"]:
            return {"level": level, "color": cfg["color"], "score": score}
    return {"level": "INUTILISABLE", "color": "#D32F2F", "score": score}


def get_20_saline_sources() -> List[Dict[str, Any]]:
    """Retourne les 20 sources salines hiérarchisées V7 ULTIME."""
    return sorted(SALINE_SOURCES_V7, key=lambda s: -s["score"])


def build_vital_zones_hierarchy(raw_zones: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Construit la liste hiérarchisée des zones vitales par type.

    Si raw_zones est fourni, trie par type + score ; sinon renvoie modèle canonique vide.
    """
    if not raw_zones:
        return [{"type": t, "zones": [], "required": t in ("salines", "alimentation")}
                for t in VITAL_ZONE_TYPES]
    hierarchy = {t: [] for t in VITAL_ZONE_TYPES}
    for z in raw_zones:
        t = str(z.get("type", "")).lower()
        if t in hierarchy:
            hierarchy[t].append(z)
    return [{"type": t, "zones": sorted(hierarchy[t], key=lambda x: -float(x.get("score", 0))),
             "count": len(hierarchy[t]),
             "required": t in ("salines", "alimentation")}
            for t in VITAL_ZONE_TYPES]


router = APIRouter(prefix="/api/v7-ultime/eco-zones", tags=["ENGINE_ECO_ZONES_Ω_X200_P0"])


@router.get("/status")
async def status():
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "phase": PHASE,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "habitat_levels": list(HABITAT_THRESHOLDS.keys()),
        "vital_zone_types": list(VITAL_ZONE_TYPES),
        "saline_sources_count": len(SALINE_SOURCES_V7),
        "v7_sources_restored": [
            "modules/salines_ultime_engine (5 scores × 20 sources)",
            "modules/nutrition_engine_v7 (Sol→Nutriments→Fourrage→Gibier)",
            "core/scoring_pipeline/repos_v1",
            "core/scoring_pipeline/alimentation_v1+v2",
        ],
    })


@router.get("/saline-sources")
async def saline_sources():
    sources = get_20_saline_sources()
    by_score = {}
    for s in sources:
        by_score.setdefault(s["score"], []).append(s["id"])
    return JSONResponse({
        "total": len(sources),
        "sources": sources,
        "by_score": by_score,
        "v7_source": "modules/salines_ultime_engine",
    })


@router.post("/compute")
async def compute(payload: dict = None):
    payload = payload or {}
    raw_zones = payload.get("vital_zones", [])
    score = float(payload.get("habitat_score", 0))
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "phase": PHASE,
        "habitat_classification": classify_habitat(score),
        "vital_zones_hierarchy": build_vital_zones_hierarchy(raw_zones),
        "saline_sources": get_20_saline_sources(),
    })
