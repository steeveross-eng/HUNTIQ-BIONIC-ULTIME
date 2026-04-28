"""
fusion_territoire_omega_router.py — PHASE-E PRÉ-FUSION (AVAL V30)
═══════════════════════════════════════════════════════════════════════════
Commandant : STEEVE-MAX
Protocole  : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Router FastAPI EXPOSANT EN LECTURE SEULE le score ULTIME institutionnel
de fusion territoire. Ne modifie rien en amont.

GET /api/v30/territoire/ultime-score
    ?lat=48.206657&lon=-68.382422&species=orignal&month=10&hour=14
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/api/v30/territoire",
    tags=["PHASE-E_FUSION_TERRITOIRE_Ω"],
)

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422

_ALLOWED_SPECIES = ("orignal", "cerf", "ours", "dindon", "wapiti")


@router.get("/ultime-score")
async def territoire_ultime_score(
    lat: float = Query(OFFICIAL_LAT, description="Latitude (défaut waypoint officiel BSL)"),
    lon: float = Query(OFFICIAL_LNG, description="Longitude (défaut waypoint officiel BSL)"),
    species: str = Query("orignal", description="Espèce officielle"),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(14, ge=0, le=23),
):
    """Retourne le score ULTIME PHASE-E (fusion territoire) — LECTURE SEULE.

    - V30 verrouillé cryptographiquement (SHA-256 echo dans la réponse).
    - Agrège 6 chaînes institutionnelles (48 engines).
    - Bande : TRÈS_FAVORABLE · FAVORABLE · NEUTRE · DÉFAVORABLE · PROSCRIT.
    - Inhibiteurs absolus : BIO_PRESENCE_MASK_HALT, V30_NON_CONFORME_DOWNGRADE.
    """
    sp = (species or "orignal").lower()
    if sp not in _ALLOWED_SPECIES:
        return JSONResponse(
            status_code=400,
            content={
                "error": "species invalide",
                "allowed": list(_ALLOWED_SPECIES),
            },
        )
    try:
        from engines.v8_institutional.fusion_territoire_omega import compute_ultime_score
        payload = await compute_ultime_score(
            lat=lat, lon=lon, species=sp, month=month, hour=hour,
        )
        return JSONResponse(content=payload)
    except RuntimeError as e:
        # V30 mutation → 409 FUSION PROSCRITE
        return JSONResponse(
            status_code=409,
            content={
                "phase": "PHASE-E_FUSION_TERRITOIRE_Ω",
                "error": str(e),
                "action": "FUSION_PROSCRITE",
                "v30_locked": False,
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "phase": "PHASE-E_FUSION_TERRITOIRE_Ω",
                "error": f"UNEXPECTED_FAILURE: {type(e).__name__}: {e}",
            },
        )


@router.get("/ultime-score/spec")
async def territoire_ultime_score_spec():
    """Retourne la spécification formelle (JSON) lue depuis le livrable L1."""
    import json, os
    spec_path = "/app/frontend/public/reports/audit_territoire_omega_ultime/FUSION_TERRITOIRE_OMEGA.json"
    if not os.path.exists(spec_path):
        return JSONResponse(status_code=404, content={"error": "spec non publiée"})
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    return JSONResponse(content=spec)
