"""
P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER — Router admin pour cron prewarm
==================================================================
COMMANDANT STEEVE-MAX · 2026-05-18 · BCE-4X ULTIME ABSOLU

Endpoints :
  GET  /api/admin/essentiel-prewarm/status  → état du cron
  POST /api/admin/essentiel-prewarm/trigger → déclenche un cycle manuel
"""
import logging
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse

logger = logging.getLogger("bionic.essentiel_prewarm_router")

router = APIRouter(prefix="/api/admin/essentiel-prewarm", tags=["admin", "p22omegaomega"])


@router.get("/status")
async def essentiel_prewarm_status():
    """Retourne l'état du cron pré-calcul 2000 membres."""
    try:
        from engines.v8_institutional.essentiel_prewarm_cron import get_cron_state
        return get_cron_state()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/trigger")
async def essentiel_prewarm_trigger(background_tasks: BackgroundTasks):
    """Déclenche manuellement un cycle (en arrière-plan, non bloquant)."""
    try:
        from engines.v8_institutional.essentiel_prewarm_cron import _run_one_cycle
        from database import db as mongo_db
        background_tasks.add_task(_run_one_cycle, mongo_db)
        return {
            "status": "triggered",
            "note": "Cycle lancé en arrière-plan. Consulter /status pour suivi.",
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
