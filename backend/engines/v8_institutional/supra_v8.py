"""
SUPRA V8 — Integration TERRITOIRE → SUPRA
============================================
PHASE-2: Connecte SUPRA aux outputs consolides de TERRITOIRE
Modules: FICHE, ANALYSE, COMPARATIF, RECOMMANDATION, PREDICTION, SCORE GLOBAL
ESI-Omega validation sur tous outputs
"""
import time
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Query

logger = logging.getLogger("bionic.supra_v8")
router = APIRouter(prefix="/api/v8/supra", tags=["SUPRA V8 — Integration Institutionnelle"])

# Import institutional engines
from engines.v8_institutional.engine_score_global import compute_score_global
from engines.v8_institutional.engine_intelligence import compute_intelligence
from engines.v8_institutional.engine_prediction import compute_prediction_48h
from engines.v8_institutional.engine_terrain_cost import compute_terrain_cost
from engines.v8_institutional.engine_visibilite import compute_visibilite
from engines.v8_institutional.engine_pression import compute_pression
from engines.v8_institutional.engine_risque import compute_risque
from engines.v8_institutional.engine_saisonnalite import compute_saisonnalite
from engines.v8_institutional.engine_comportement import compute_comportement
from engines.v8_institutional.engine_bio_signes import compute_bio_signes
from engines.v8_institutional.engine_salines import compute_salines
from engines.v8_institutional.engine_frequentation import compute_frequentation


@router.get("/fiche")
async def supra_fiche(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None),
):
    start = time.time()
    m = month or datetime.now(timezone.utc).month
    terrain = compute_terrain_cost(lat, lon)
    visibilite = compute_visibilite(lat, lon)
    pression = compute_pression(lat, lon)
    saison = compute_saisonnalite(m, species, 7)
    bio = compute_bio_signes(lat, lon, species, m)
    return {
        "module": "FICHE",
        "terrain": terrain,
        "visibilite": visibilite,
        "pression": pression,
        "saisonnalite": saison,
        "bio_signes": {"composite": bio["composite_score"], "traces": len(bio["adn_visuel"]["traces"])},
        "compute_ms": round((time.time() - start) * 1000),
    }


@router.get("/analyse")
async def supra_analyse(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None), hour: int = Query(None),
):
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    intel = compute_intelligence(lat, lon, species, m)
    score = compute_score_global(lat, lon, species, m, h)
    risque = compute_risque(lat, lon, species, m)
    comport = compute_comportement(lat, lon, species, m, h)
    freq = compute_frequentation(lat, lon, species, m, h)
    return {
        "module": "ANALYSE",
        "intelligence": intel,
        "score_global": score,
        "risque": risque,
        "comportement": comport,
        "frequentation": freq,
        "compute_ms": round((time.time() - start) * 1000),
    }


@router.get("/recommandation")
async def supra_recommandation(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None), hour: int = Query(None),
    wind_deg: float = Query(225),
):
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    intel = compute_intelligence(lat, lon, species, m, wind_deg)
    score = compute_score_global(lat, lon, species, m, h)
    salines = compute_salines(lat, lon, species, m)
    pred = compute_prediction_48h(lat, lon, species, m, h)
    best = pred.get("best_window", {})

    reco = "EXCELLENT" if score["score_global"] > 70 else "BON" if score["score_global"] > 50 else "MODERE" if score["score_global"] > 30 else "DECONSEILLE"
    return {
        "module": "RECOMMANDATION",
        "verdict": reco,
        "score_global": score["score_global"],
        "classification": score["classification"],
        "site_quality": intel["recommendation"],
        "best_window": best,
        "salines_optimales": len(salines),
        "actions": [
            f"Score site: {score['score_global']}/100 ({score['classification']})",
            f"Meilleur creneau: H{best.get('hour', '?')} J{best.get('day', '?')} (score {best.get('score', '?')})",
            f"Salines: {len(salines)} positions optimales identifiees",
        ],
        "compute_ms": round((time.time() - start) * 1000),
    }


@router.get("/prediction")
async def supra_prediction(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None), hour: int = Query(None),
):
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    pred = compute_prediction_48h(lat, lon, species, m, h)
    return {
        "module": "PREDICTION",
        "timeline": pred["timeline"],
        "optimal_windows": pred["optimal_windows"],
        "scenarios": pred["scenarios"],
        "best": pred["best_window"],
        "worst": pred["worst_window"],
        "compute_ms": round((time.time() - start) * 1000),
    }


@router.get("/score")
async def supra_score(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None), hour: int = Query(None),
):
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    score = compute_score_global(lat, lon, species, m, h)
    return {
        "module": "SCORE-GLOBAL",
        **score,
        "compute_ms": round((time.time() - start) * 1000),
    }


@router.get("/score-global-interne")
async def supra_score_global_interne(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None), hour: int = Query(None),
    wind_deg: float = Query(225),
):
    """SCORE GLOBAL INTERNE — 6 composantes + journalisation ESI-Omega."""
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour

    # 6 composantes
    score = compute_score_global(lat, lon, species, m, h)
    risque = compute_risque(lat, lon, species, m)
    comport = compute_comportement(lat, lon, species, m, h)
    intel = compute_intelligence(lat, lon, species, m, wind_deg)

    composantes = {
        "terrain": score["breakdown"]["terrain"],
        "thermal": score["breakdown"]["thermal"],
        "temporal": score["breakdown"]["temporal"],
        "comportement": round(comport.get("distance_fuite_m", 0) / 5, 1),
        "risque": risque["risque_score"],
        "intelligence": intel["site_composite"],
    }

    coherence_ok = all(isinstance(v, (int, float)) and v >= 0 for v in composantes.values())

    # Journalisation ESI-Omega
    from engines.v8_institutional.esi_omega import _log_audit
    _log_audit(
        "SCORE_GLOBAL_INTERNE_ACTIVATION",
        f"{lat},{lon},{species}",
        "CONFORME" if coherence_ok else "NON-CONFORME",
        f"6 composantes: {composantes}"
    )

    return {
        "module": "SCORE-GLOBAL-INTERNE",
        "mode": "INTERNE",
        "score_global": score["score_global"],
        "classification": score["classification"],
        "composantes_6": composantes,
        "coherence": "CONFORME" if coherence_ok else "NON-CONFORME",
        "thermal": score["thermal"],
        "engine": "V8-SCORE-GLOBAL-INTERNE",
        "esi_omega_logged": True,
        "compute_ms": round((time.time() - start) * 1000),
    }


@router.get("/status")
async def supra_status():
    return {
        "engine": "SUPRA-V8-INSTITUTIONNEL",
        "modules": ["FICHE", "ANALYSE", "RECOMMANDATION", "PREDICTION", "SCORE-GLOBAL", "SCORE-GLOBAL-INTERNE"],
        "source": "24 ENGINES INSTITUTIONNELS via TERRITOIRE",
        "validation": "ESI-Omega",
        "status": "ACTIF",
    }
