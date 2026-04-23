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
# CATALOGUE SAISONS MFFP 2026 — Zone 2 (Bas-Saint-Laurent) — sous-zones 2A/2B
# ═══════════════════════════════════════════════════════════════════════
# Signature institutionnelle : synchronisation annuelle sous ORDRE du
# COMMANDANT (phase X200-P2). Source : calendrier officiel MFFP Québec
# 2026, zone 2 Bas-Saint-Laurent. Les plages listées (mois, jour) sont
# INCLUSIVES. Chaque entrée précise l'arme autorisée (carabine, arc,
# arbalète) et la sous-zone (2A / 2B / all).
#
# Note Ω : ce catalogue est versionné. Toute mise à jour annuelle doit
# repasser par un ORDRE DIRECT du COMMANDANT (synchronisation X200-P2).
# ═══════════════════════════════════════════════════════════════════════
MFFP_CATALOGUE_VERSION = "MFFP_2026_ZONE_2_BSL_X200_P2_SYNC_Ω"

SEASONS_MFFP_2026 = {
    "orignal": [
        {"start": (9, 19), "end": (10, 18), "weapon": "carabine", "subzone": "all"},
        {"start": (9, 12), "end": (10, 18), "weapon": "arc",      "subzone": "all"},
        {"start": (9, 12), "end": (10, 18), "weapon": "arbalete", "subzone": "all"},
    ],
    "chevreuil": [
        {"start": (11, 1),  "end": (11, 30), "weapon": "carabine", "subzone": "2A"},
        {"start": (10, 25), "end": (11, 30), "weapon": "arc",      "subzone": "all"},
        {"start": (10, 25), "end": (11, 30), "weapon": "arbalete", "subzone": "all"},
    ],
    "cerf": [   # cerf = chevreuil — alias institutionnel V7
        {"start": (11, 1),  "end": (11, 30), "weapon": "carabine", "subzone": "2A"},
        {"start": (10, 25), "end": (11, 30), "weapon": "arc",      "subzone": "all"},
        {"start": (10, 25), "end": (11, 30), "weapon": "arbalete", "subzone": "all"},
    ],
    "ours": [
        {"start": (5, 15), "end": (6, 30),  "weapon": "carabine", "subzone": "all"},
        {"start": (9, 1),  "end": (10, 31), "weapon": "carabine", "subzone": "all"},
        {"start": (5, 15), "end": (6, 30),  "weapon": "arc",      "subzone": "all"},
        {"start": (9, 1),  "end": (10, 31), "weapon": "arc",      "subzone": "all"},
    ],
    "dindon": [
        {"start": (4, 25), "end": (5, 31), "weapon": "carabine", "subzone": "all"},
        {"start": (4, 25), "end": (5, 31), "weapon": "arc",      "subzone": "all"},
        {"start": (4, 25), "end": (5, 31), "weapon": "arbalete", "subzone": "all"},
    ],
    "wapiti": [],  # NON ADMISSIBLE en zone 2 (confirmé MFFP 2026)
}

# Vue agrégée héritée (union de toutes les fenêtres, toutes armes/sous-zones)
SEASONS_ZONE_BSL = {
    sp: list({(w["start"], w["end"]) for w in windows})
    for sp, windows in SEASONS_MFFP_2026.items()
}

LEGAL_HOURS_OFFSET_MIN = {"sunrise": -30, "sunset": +30}


def _in_range(d: date, start: tuple, end: tuple) -> bool:
    s = date(d.year, start[0], start[1])
    e = date(d.year, end[0], end[1])
    return s <= d <= e


def is_legal(species: str, d: date,
             weapon: Optional[str] = None,
             subzone: str = "all") -> Dict[str, Any]:
    """Vérifie la légalité d'une chasse (species, date) en zone 2 BSL.

    Si `weapon` est précisé, contrainte restreinte à cette arme.
    `subzone` : "all" par défaut, ou "2A" / "2B".
    """
    species = species.lower().strip()
    weapon = (weapon or "").lower().strip() or None
    windows = SEASONS_MFFP_2026.get(species, [])
    if not windows:
        return {"legal": False, "reason": "species_not_allowed_in_zone",
                "species": species, "date": d.isoformat(),
                "catalogue_version": MFFP_CATALOGUE_VERSION}
    matched = []
    for w in windows:
        if weapon and w["weapon"] != weapon:
            continue
        if w["subzone"] not in ("all", subzone):
            continue
        if _in_range(d, w["start"], w["end"]):
            matched.append({
                "window": {"start": f"{w['start'][0]:02d}-{w['start'][1]:02d}",
                           "end":   f"{w['end'][0]:02d}-{w['end'][1]:02d}"},
                "weapon": w["weapon"], "subzone": w["subzone"],
            })
    if matched:
        return {"legal": True, "species": species, "date": d.isoformat(),
                "weapons_allowed": sorted({m["weapon"] for m in matched}),
                "matches": matched, "catalogue_version": MFFP_CATALOGUE_VERSION}
    # Pas de match : retourner toutes les fenêtres applicables
    return {"legal": False, "reason": "out_of_season",
            "species": species, "date": d.isoformat(),
            "weapon_filter": weapon, "subzone_filter": subzone,
            "next_windows": [
                {"start": f"{w['start'][0]:02d}-{w['start'][1]:02d}",
                 "end":   f"{w['end'][0]:02d}-{w['end'][1]:02d}",
                 "weapon": w["weapon"], "subzone": w["subzone"]}
                for w in windows
            ],
            "catalogue_version": MFFP_CATALOGUE_VERSION}


def compute_legal_time(species: str, iso_date: Optional[str] = None,
                       weapon: Optional[str] = None,
                       subzone: str = "all") -> Dict[str, Any]:
    d = datetime.fromisoformat(iso_date).date() if iso_date else date.today()
    result = is_legal(species, d, weapon=weapon, subzone=subzone)
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
        "phase": "X200-P2-LEGAL-TIME-SYNC",
        "catalogue_version": MFFP_CATALOGUE_VERSION,
        "ready": auth["authorized"],
        "authorization": auth,
        "v30_modified": False,
        "diagnostic_panel_active": False,
        "species_catalogue": list(SEASONS_MFFP_2026.keys()),
        "zone": "zone_2_bas_saint_laurent",
        "weapons_supported": ["carabine", "arc", "arbalete"],
        "subzones_supported": ["all", "2A", "2B"],
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
        weapon=p.get("weapon"),
        subzone=str(p.get("subzone", "all")),
    ))
