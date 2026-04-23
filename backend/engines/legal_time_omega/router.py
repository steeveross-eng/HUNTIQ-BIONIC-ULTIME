"""
ENGINE_LEGAL_TIME_Ω — Router FastAPI — X199 ACTIVÉ
====================================================
Phase : PHASE_X199_ACTIVATION_Ω — moteur #4 (racine)
Commandant STEEVE-MAX

Rôle : Fenêtres légales de chasse Québec (zones Bas-Saint-Laurent),
validation `(species, date)` dans saison autorisée, exclusions temporelles.

Référence institutionnelle : MFFP Québec — calendrier général zone 2
(Bas-Saint-Laurent). Implémentation déterministe pour validation API.

Activation : triple verrou X199. V30 INTANGIBLE.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from engines.x199_commons import is_x199_authorized, unauthorized_response

FEATURE_FLAG_ACTIVE: bool = True

ENGINE_ID = "ENGINE_LEGAL_TIME_Ω"
CATEGORY = "etendu"
ROLE = "Fenêtres légales de chasse, saisons, zones réglementées, exclusions temporelles"
MAX_KB_TARGET = 60

# ═══════════════════════════════════════════════════════════════════════
# CATALOGUE SAISONS — Zone 2 (Bas-Saint-Laurent) — Référence 2024-2025
# (mois, jour) inclusifs. Les dates réelles doivent être synchronisées
# annuellement au registre MFFP. Implémentation institutionnelle Ω.
# ═══════════════════════════════════════════════════════════════════════
SEASONS_ZONE_BSL = {
    "orignal":    [((9, 19), (10, 18))],         # mi-septembre → mi-octobre
    "chevreuil":  [((11, 1), (11, 30))],         # novembre
    "cerf":       [((11, 1), (11, 30))],
    "ours":       [((5, 15), (6, 30)), ((9, 1), (10, 31))],
    "dindon":     [((4, 25), (5, 31))],
    "wapiti":     [],                             # non admissible zone 2
}

LEGAL_HOURS_OFFSET_MIN = {"sunrise": -30, "sunset": +30}


def _in_range(d: date, start: tuple, end: tuple) -> bool:
    s = date(d.year, start[0], start[1])
    e = date(d.year, end[0], end[1])
    return s <= d <= e


def is_legal(species: str, d: date) -> Dict[str, Any]:
    species = species.lower().strip()
    windows = SEASONS_ZONE_BSL.get(species, [])
    if not windows:
        return {"legal": False, "reason": "species_not_allowed_in_zone",
                "species": species, "date": d.isoformat()}
    for w in windows:
        if _in_range(d, w[0], w[1]):
            return {"legal": True, "species": species, "date": d.isoformat(),
                    "window": {"start": f"{w[0][0]:02d}-{w[0][1]:02d}",
                               "end":   f"{w[1][0]:02d}-{w[1][1]:02d}"}}
    return {"legal": False, "reason": "out_of_season",
            "species": species, "date": d.isoformat(),
            "next_windows": [{"start": f"{w[0][0]:02d}-{w[0][1]:02d}",
                              "end":   f"{w[1][0]:02d}-{w[1][1]:02d}"} for w in windows]}


def compute_legal_time(species: str, iso_date: Optional[str] = None) -> Dict[str, Any]:
    d = datetime.fromisoformat(iso_date).date() if iso_date else date.today()
    result = is_legal(species, d)
    result["engine_id"] = ENGINE_ID
    result["zone"] = "zone_2_bas_saint_laurent"
    result["legal_hours_offset_min"] = LEGAL_HOURS_OFFSET_MIN
    result["v30_engine_touched"] = False
    return result


router = APIRouter(
    prefix="/api/v7-ultime/legal-time/compute",
    tags=["ENGINE_LEGAL_TIME_Ω_X199_ACTIVE"],
)


@router.get("/status")
async def engine_status():
    auth = is_x199_authorized(FEATURE_FLAG_ACTIVE)
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "category": CATEGORY,
        "role": ROLE,
        "max_kb_target": MAX_KB_TARGET,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "phase": "X199-ACTIVATION",
        "ready": auth["authorized"],
        "authorization": auth,
        "v30_modified": False,
        "diagnostic_panel_active": False,
        "species_catalogue": list(SEASONS_ZONE_BSL.keys()),
        "zone": "zone_2_bas_saint_laurent",
    })


@router.post("")
@router.post("/")
async def engine_compute(payload: dict = None):
    if not is_x199_authorized(FEATURE_FLAG_ACTIVE)["authorized"]:
        raise unauthorized_response(ENGINE_ID, FEATURE_FLAG_ACTIVE)
    p = payload or {}
    return JSONResponse(compute_legal_time(
        species=str(p.get("species", "orignal")),
        iso_date=p.get("date"),
    ))
