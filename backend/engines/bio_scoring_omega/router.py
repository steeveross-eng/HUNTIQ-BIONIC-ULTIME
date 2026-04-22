"""
ENGINE_BIO_SCORING_Ω — Implémentation X200 P0 (support)
=========================================================
Phase    : X200-P0-ACTIVATION — support scoring biologique
Active le scoring 8-facteurs V7 + façade-miroir V30 lecture seule.

SOURCE V7 : core/scoring_pipeline/corridors_v10/scoring.py
"""
from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

FEATURE_FLAG_ACTIVE: bool = True
ENGINE_ID = "ENGINE_BIO_SCORING_Ω"
PHASE = "X200-P0-ACTIVATION"

# Poids V7 des 8 facteurs (0-100 pts total)
FACTOR_WEIGHTS_V7 = {
    "ecl":              25,  # espace classe
    "canopy":           20,
    "pressure_human":   15,
    "food_refuge":      15,
    "topo_hydro":       10,
    "regeneration":     5,
    "cost":             10,
    # bonus multiplicateurs
    "bonus_diversity":  1.05,
    "mod_short":        1.10,  # corridor < 8 cellules
    "mod_long":         0.85,  # corridor > 40 cellules
}


def score_8_factors(subscores: Dict[str, float]) -> Dict[str, Any]:
    """Calcule le score biologique 0-100 selon les 8 facteurs V7.

    Args:
        subscores: dict avec clés optionnelles :
          ecl [0-1], canopy [0-1], pressure_human [0-1] (1=loin),
          food_refuge [0-1], topo_hydro [0-1], regeneration [0-1], cost [0-1],
          from_type, to_type (str), n_cells (int)
    """
    s = 0.0
    # Facteur 1 - ECL
    ecl = float(subscores.get("ecl", 0))
    if ecl >= 0.7: s += 25
    elif ecl >= 0.5: s += 15 + (ecl - 0.5) * 50
    elif ecl >= 0.3: s += 5 + (ecl - 0.3) * 50
    # Facteur 2 - Canopy
    can = float(subscores.get("canopy", 0))
    if can >= 0.7: s += 20
    elif can >= 0.4: s += 8 + (can - 0.4) * 40
    # Facteur 3 - Pression humaine (inversé : 1 = éloigné)
    ph = float(subscores.get("pressure_human", 0))
    s += ph * 15
    # Facteur 4 - Nourriture + Refuge
    fr = float(subscores.get("food_refuge", 0))
    s += min(15, fr * 15)
    # Facteur 5 - Topo + Hydro
    th = float(subscores.get("topo_hydro", 0))
    s += th * 10
    # Facteur 6 - Régénération
    rg = float(subscores.get("regeneration", 0))
    s += min(5, rg * 7)
    # Facteur 7 - Cost (inversé : 1 = bas coût)
    c = float(subscores.get("cost", 0))
    s += c * 10
    # Facteur 8 - Bonus diversité
    from_t = subscores.get("from_type")
    to_t = subscores.get("to_type")
    if from_t and to_t and from_t != to_t:
        s *= FACTOR_WEIGHTS_V7["bonus_diversity"]
    # Modifs longueur
    n = int(subscores.get("n_cells", 20))
    if n < 8:
        s *= FACTOR_WEIGHTS_V7["mod_short"]
    elif n > 40:
        s *= FACTOR_WEIGHTS_V7["mod_long"]
    final = max(0.0, min(100.0, s))
    return {
        "score_0_100": round(final, 2),
        "subscores_applied": subscores,
        "weights_used": FACTOR_WEIGHTS_V7,
    }


router = APIRouter(prefix="/api/v7-ultime/bio-scoring", tags=["ENGINE_BIO_SCORING_Ω_X200_P0"])


@router.get("/status")
async def status():
    # Vérification V30 miroir
    from engines.bio_scoring_omega.v30_mirror_read_only import assert_v30_integrity
    v30_check = assert_v30_integrity()
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "phase": PHASE,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "factor_weights": FACTOR_WEIGHTS_V7,
        "v30_mirror": {
            "integrity_ok": v30_check["invariant"],
            "v30_sha256": v30_check["v30_sha256"],
        },
        "v7_source": "core/scoring_pipeline/corridors_v10/scoring.py",
    })


@router.post("/compute")
async def compute(payload: dict = None):
    payload = payload or {}
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "result": score_8_factors(payload),
    })
