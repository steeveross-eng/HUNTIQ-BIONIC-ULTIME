"""
v12_plus_router.py — Router REST autonome V12-SUPRA+ Ω
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_Ω · STEEVE-MAX · 2026-02-19
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU

Router REST autonome qui ne dépend PAS de engines/nutrition_intelligence/__init__.py
(actuellement cassé : module `x5100_mineral_score` manquant).

Endpoints :
  GET  /api/v6/nutrition-intelligence/v12-plus/health
  POST /api/v6/nutrition-intelligence/v12-plus/fiche-saline-ultime

Verrou Phase III maintenu (aucune dépendance circulaire).
"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/v6/nutrition-intelligence/v12-plus",
    tags=["V12-SUPRA+ Fiche Saline Ultime"],
)


# ═════════════════════════════════════════════════════════════════════
# Models
# ═════════════════════════════════════════════════════════════════════
class FicheSalineUltimeRequest(BaseModel):
    lat: float
    lon: float
    species: str = Field(..., description="orignal|chevreuil|cerf|ours_noir|dindon_sauvage|wapiti|coyote")
    month: int = Field(..., ge=1, le=12)
    profil: str = Field("moyenne", description="moyenne|male_rut|femelle_gest|femelle_lact|juvenile")
    hour: int = Field(14, ge=0, le=23)
    wind_deg: float = Field(225.0)
    wind_speed: float = Field(15.0)
    saline_id: Optional[str] = None
    saline_score: Optional[float] = None
    saline_type: Optional[str] = "naturelle"


# ═════════════════════════════════════════════════════════════════════
# Endpoints
# ═════════════════════════════════════════════════════════════════════
@router.get("/health")
async def v12_plus_health():
    """Health check V12-SUPRA+ · vérifie disponibilité tables doctrinales."""
    try:
        from engines.v8_institutional._v12_plus_tables import (
            RATIO_CAP_CIBLE_OMEGA, CONSO_KG_MS_JOUR, FOOD_PLOT_SURFACE_M2,
            TRACE_PPM_CIBLE, APPROCHE_VENT_DOCTRINALE, STRATEGIE_CORRIDORS,
            TABLES_DOCTRINE, TABLES_VERSION,
        )
        from engines.v8_institutional.engine_nutrition_v12_supra_plus import (
            ENGINE_NAME, ENGINE_VERSION, DOCTRINE, PHASE_III_LOCK,
        )
        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "doctrine": DOCTRINE,
            "phase_iii_lock": PHASE_III_LOCK,
            "tables": {
                "doctrine": TABLES_DOCTRINE,
                "version": TABLES_VERSION,
                "especes_ratio_cap": list(RATIO_CAP_CIBLE_OMEGA.keys()),
                "especes_conso_kg": list(CONSO_KG_MS_JOUR.keys()),
                "cultures_food_plot": list(FOOD_PLOT_SURFACE_M2.keys()),
                "especes_trace_ppm": list(TRACE_PPM_CIBLE.keys()),
                "especes_approche_vent": list(APPROCHE_VENT_DOCTRINALE.keys()),
                "especes_corridors": list(STRATEGIE_CORRIDORS.keys()),
            },
            "endpoint": "POST /api/v6/nutrition-intelligence/v12-plus/fiche-saline-ultime",
            "status": "OPERATIONAL",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"V12+ health failed: {e}")


@router.post("/fiche-saline-ultime")
async def v12_plus_fiche_saline_ultime(req: FicheSalineUltimeRequest):
    """V12-SUPRA+ · FICHE SALINE ULTIME PRD-READY · 10 blocs structurés.

    Trigger : clic sur saline suggérée pour espèce active dans BionicLayersV8.
    Adapté à : orignal / chevreuil / cerf / ours_noir / dindon_sauvage / wapiti / coyote.

    Verrou Phase III maintenu (V12 hub intact, V20 inchangé).
    """
    try:
        from engines.v8_institutional.engine_nutrition_v12_supra_plus import (
            compute_fiche_saline_ultime,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"V12+ engine import failed: {e}")

    saline = None
    if req.saline_id:
        saline = {
            "id": req.saline_id,
            "lat": req.lat,
            "lng": req.lon,
            "type": req.saline_type or "naturelle",
            "status": "ACTIVE",
            "attractiveness_score": req.saline_score or 70,
        }

    try:
        fiche = await compute_fiche_saline_ultime(
            lat=req.lat, lon=req.lon,
            species=req.species, month=req.month,
            saline=saline, profil=req.profil, hour=req.hour,
            wind_deg=req.wind_deg, wind_speed=req.wind_speed,
        )
        return fiche
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"V12+ compute failed: {type(e).__name__}: {e}")
