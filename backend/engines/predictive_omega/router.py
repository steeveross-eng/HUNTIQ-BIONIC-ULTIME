"""
ENGINE_PREDICTIVE_Ω — Router FastAPI — X199 ACTIVÉ
====================================================
Phase : PHASE_X199_ACTIVATION_Ω — moteur #5 (dépend 1,2,3,4)
Commandant STEEVE-MAX

Rôle : Prédiction de probabilité de présence animale agrégeant les sorties
des moteurs ecoforestry (canopée, mosaïque), terrain_3d (pente, exposition),
legal_time (saison) et heure (fenêtre d'activité).

Activation : triple verrou X199. V30 INTANGIBLE.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from engines.x199_commons import is_x199_authorized, unauthorized_response
from engines.ecoforestry_omega.router import compute_ecoforestry
# P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · COMMANDANT STEEVE-MAX
# engines.terrain_3d_omega SUPPRIMÉ — stub no-op pour conserver predictive_omega.
def compute_terrain_3d(_triangle):
    """Stub no-op post-cleanup 3D — retourne valeurs neutres pour pente/exposition."""
    return {"slope_deg": 0.0, "aspect_cardinal": "N", "elevation_m": 0.0}
from engines.legal_time_omega.router import is_legal

FEATURE_FLAG_ACTIVE: bool = True

ENGINE_ID = "ENGINE_PREDICTIVE_Ω"
CATEGORY = "etendu"
ROLE = "Prédictions comportementales, flux animaliers, probabilité présence, tendance saisonnière"
MAX_KB_TARGET = 110

# Fenêtres d'activité (heures locales) par espèce
ACTIVITY_WINDOWS = {
    "orignal":   [(5, 8), (17, 20)],
    "chevreuil": [(5, 9), (16, 20)],
    "cerf":      [(5, 9), (16, 20)],
    "ours":      [(4, 10), (16, 21)],
    "dindon":    [(6, 11), (15, 18)],
    "wapiti":    [(5, 9), (17, 20)],
}

# Poids institutionnels Ω (somme = 1.0)
WEIGHTS = {
    "canopy":     0.25,
    "mosaic":     0.15,
    "slope":      0.15,   # malus si pente trop forte
    "aspect":     0.10,
    "legal":      0.20,   # binaire saison → multiplicateur fort
    "activity":   0.15,
}


def _canopy_score_species(canopy: float, species: str) -> float:
    """Préférence de couverture par espèce (0-1)."""
    prefs = {
        "orignal": 0.6, "chevreuil": 0.7, "cerf": 0.7,
        "ours": 0.75, "dindon": 0.5, "wapiti": 0.55,
    }
    target = prefs.get(species.lower(), 0.6)
    return max(0.0, 1.0 - abs(canopy - target))


def _slope_score(slope_deg: float) -> float:
    # Favorable 0-20°, pénalité linéaire après
    if slope_deg <= 20.0:
        return 1.0 - (slope_deg / 40.0)  # 1.0→0.5 en 20°
    return max(0.0, 0.5 - (slope_deg - 20) / 50.0)


def _aspect_score(aspect_cardinal: str, species: str) -> float:
    favored = {
        "orignal":   ("N", "NE", "NW", "E"),      # ombrage, humidité
        "chevreuil": ("S", "SE", "SW", "E"),      # thermie, lisières
        "cerf":      ("S", "SE", "SW", "E"),
        "ours":      ("N", "NE", "NW", "E"),
        "dindon":    ("S", "SE", "E"),
        "wapiti":    ("S", "E", "SE", "W"),
    }.get(species.lower(), ("N", "E", "S", "W"))
    return 1.0 if aspect_cardinal in favored else 0.55


def _activity_score(hour: int, species: str) -> float:
    windows = ACTIVITY_WINDOWS.get(species.lower(), [(5, 9), (17, 20)])
    for start, end in windows:
        if start <= hour < end:
            return 1.0
    return 0.25


def compute_predictive(lat: float, lng: float, species: str = "orignal",
                       iso_date: Optional[str] = None, hour: int = 7,
                       month: Optional[int] = None) -> Dict[str, Any]:
    d = datetime.fromisoformat(iso_date).date() if iso_date else date.today()
    m = month if month is not None else d.month
    species_l = species.lower()

    eco = compute_ecoforestry(lat, lng, m)
    t3d = compute_terrain_3d([])
    leg = is_legal(species_l, d)

    canopy_s = _canopy_score_species(float(eco["canopy_fraction"]), species_l)
    mosaic_s = float(eco["mosaic_diversity_index"])
    slope_s  = _slope_score(float(t3d["slope_deg"]))
    aspect_s = _aspect_score(t3d["aspect_cardinal"], species_l)
    legal_s  = 1.0 if leg.get("legal") else 0.0
    act_s    = _activity_score(int(hour), species_l)

    raw = (
        canopy_s  * WEIGHTS["canopy"]
        + mosaic_s  * WEIGHTS["mosaic"]
        + slope_s   * WEIGHTS["slope"]
        + aspect_s  * WEIGHTS["aspect"]
        + legal_s   * WEIGHTS["legal"]
        + act_s     * WEIGHTS["activity"]
    )
    # Saison non légale → malus multiplicateur 0.3 (présence possible, exploitation illégale)
    multiplier = 1.0 if legal_s >= 1.0 else 0.3
    prob = max(0.0, min(1.0, raw * multiplier))

    return {
        "engine_id": ENGINE_ID,
        "lat": lat, "lng": lng, "species": species_l,
        "date": d.isoformat(), "hour": int(hour),
        "probability_0_1": round(prob, 4),
        "components": {
            "canopy":   round(canopy_s, 4),
            "mosaic":   round(mosaic_s, 4),
            "slope":    round(slope_s, 4),
            "aspect":   round(aspect_s, 4),
            "legal":    round(legal_s, 4),
            "activity": round(act_s, 4),
        },
        "weights": WEIGHTS,
        "legal_multiplier": multiplier,
        "upstream_engines": ["ECOFORESTRY_Ω", "3D_TERRAIN_Ω", "LEGAL_TIME_Ω"],
        "v30_engine_touched": False,
    }


router = APIRouter(
    prefix="/api/v7-ultime/predictive/compute",
    tags=["ENGINE_PREDICTIVE_Ω_X199_ACTIVE"],
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
        "activity_windows": ACTIVITY_WINDOWS,
        "weights": WEIGHTS,
        "upstream": ["ECOFORESTRY_Ω", "3D_TERRAIN_Ω", "LEGAL_TIME_Ω"],
    })


@router.post("")
@router.post("/")
async def engine_compute(payload: dict = None):
    if not is_x199_authorized(FEATURE_FLAG_ACTIVE)["authorized"]:
        raise unauthorized_response(ENGINE_ID, FEATURE_FLAG_ACTIVE)
    p = payload or {}
    return JSONResponse(compute_predictive(
        lat=float(p.get("lat", 48.206657)),
        lng=float(p.get("lng", p.get("lon", -68.382422))),
        species=str(p.get("species", "orignal")),
        iso_date=p.get("date"),
        hour=int(p.get("hour", 7)),
        month=p.get("month"),
    ))
