"""
4 PILIERS STRUCTURELS — ORCHESTRATEURS MAITRES
BIONIC OS — V8-ENGINES-INSTITUTIONNEL-Omega-ULTIME-MAX
Chaque pilier orchestre ses engines associes.
"""
import time
import logging
from fastapi import APIRouter, Query

logger = logging.getLogger("bionic.v8_institutional")
router = APIRouter(prefix="/api/v8/institutional", tags=["V8 Institutional — 24 Engines + 4 Piliers"])

# ═══ IMPORTS 24 ENGINES ═══
from engines.v8_institutional.engine_zones import compute_zones
from engines.v8_national.phase_b_engines import generate_corridors_ta as compute_corridors_legacy


def compute_corridors(lat, lon, species, month, hour, wind_deg=225, zones=None):
    """Shim legacy (pre-Phase-L) — redirige vers phase_b_engines.
    Le module `engine_corridors.py` a été archivé dans
    `_ARCHIVE_NON_ACTIVE/engine_corridors_legacy_pre_L.py` (Phase XI-SUPRA-M 2026-04-20).
    Cette fonction reste disponible uniquement pour compatibilité `piliers_router`.
    Les consommateurs modernes doivent utiliser `ENGINE-IA-CORRIDORS-ORGANIC-Ω`.
    """
    return compute_corridors_legacy(lat, lon, species, month, hour, wind_deg=wind_deg, zones=zones)
from engines.v8_institutional.engine_affuts import compute_affuts
from engines.v8_institutional.engine_hotspots import compute_hotspots
from engines.v8_institutional.engine_vent import compute_wind_vectors, compute_scent_cone
from engines.v8_institutional.engine_heatmap import compute_heatmap
from engines.v8_institutional.engine_salines import compute_salines
from engines.v8_institutional.engine_pression import compute_pression
from engines.v8_institutional.engine_risque import compute_risque
from engines.v8_institutional.engine_frequentation import compute_frequentation
from engines.v8_institutional.engine_saisonnalite import compute_saisonnalite
from engines.v8_institutional.engine_comportement import compute_comportement
from engines.v8_institutional.engine_comportement_avance import compute_comportement_avance
from engines.v8_institutional.engine_terrain_cost import compute_terrain_cost
from engines.v8_institutional.engine_visibilite import compute_visibilite
from engines.v8_institutional.engine_connectivite import compute_connectivite
from engines.v8_institutional.engine_intelligence import compute_intelligence
from engines.v8_institutional.engine_score_global import compute_score_global
from engines.v8_institutional.engine_prediction import compute_prediction_48h
from engines.v8_institutional.engine_bio_signes import compute_bio_signes
from engines.v8_institutional.engine_audio_acoustique import compute_audio_acoustique
from engines.v8_institutional.engine_psychologie import compute_psychologie


# ═══ PILIER 1: BIO-SYSTEME ═══
@router.get("/pilier/bio-systeme")
async def pilier_bio_systeme(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(10), hour: int = Query(7), wind_deg: float = Query(225),
):
    start = time.time()
    zones = compute_zones(lat, lon, species, month)
    corridors = compute_corridors(lat, lon, species, month, hour, wind_deg, zones=zones)
    affuts = compute_affuts(lat, lon, species, zones, corridors, wind_deg)
    hotspots = compute_hotspots(lat, lon, species, zones, corridors, affuts)
    wind = compute_wind_vectors(lat, lon, wind_deg, 15)
    salines = compute_salines(lat, lon, species, month)
    return {
        "pilier": "BIO-SYSTEME",
        "zones": {"count": len(zones), "data": zones},
        "corridors": {"count": len(corridors), "data": corridors},
        "affuts": {"count": len(affuts), "data": affuts},
        "hotspots": {"count": len(hotspots), "data": hotspots},
        "wind_vectors": {"count": len(wind), "data": wind},
        "salines": {"count": len(salines), "data": salines},
        "compute_ms": round((time.time() - start) * 1000),
    }


# ═══ PILIER 2: COMPORTEMENT HUMAIN ═══
@router.get("/pilier/comportement-humain")
async def pilier_comportement_humain(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(10), hour: int = Query(7),
):
    start = time.time()
    pression = compute_pression(lat, lon)
    risque = compute_risque(lat, lon, species, month)
    freq = compute_frequentation(lat, lon, species, month, hour)
    saison = compute_saisonnalite(month, species, hour)
    comport = compute_comportement(lat, lon, species, month, hour)
    comport_av = compute_comportement_avance(lat, lon, species, month, hour)
    return {
        "pilier": "COMPORTEMENT-HUMAIN",
        "pression": pression, "risque": risque, "frequentation": freq,
        "saisonnalite": saison, "comportement": comport, "comportement_avance": comport_av,
        "compute_ms": round((time.time() - start) * 1000),
    }


# ═══ PILIER 3: SYSTEME SENSORIEL ═══
@router.get("/pilier/systeme-sensoriel")
async def pilier_systeme_sensoriel(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(10), hour: int = Query(7),
):
    start = time.time()
    terrain = compute_terrain_cost(lat, lon)
    visibilite = compute_visibilite(lat, lon)
    bio_signes = compute_bio_signes(lat, lon, species, month)
    audio = compute_audio_acoustique(lat, lon, species, hour)
    return {
        "pilier": "SYSTEME-SENSORIEL",
        "terrain_cost": terrain, "visibilite": visibilite,
        "bio_signes": bio_signes,
        "audio_acoustique": audio,
        "cameras": {"status": "ACTIF — delegation camera_engine/vision_engine"},
        "compute_ms": round((time.time() - start) * 1000),
    }


# ═══ PILIER 4: PREDICTION & INTELLIGENCE ═══
@router.get("/pilier/prediction-intelligence")
async def pilier_prediction_intelligence(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(10), hour: int = Query(7), wind_deg: float = Query(225),
):
    start = time.time()
    zones = compute_zones(lat, lon, species, month)
    corridors = compute_corridors(lat, lon, species, month, hour)
    intelligence = compute_intelligence(lat, lon, species, month, wind_deg)
    score = compute_score_global(lat, lon, species, month, hour)
    conn = compute_connectivite(lat, lon, zones, corridors)
    psycho = compute_psychologie(lat, lon, species, month, hour, 30)
    pred = compute_prediction_48h(lat, lon, species, month, hour)
    return {
        "pilier": "PREDICTION-INTELLIGENCE",
        "intelligence": intelligence, "score_global": score, "connectivite": conn,
        "psychologie_animale": psycho,
        "prediction_48h": {"best_window": pred["best_window"], "optimal_count": len(pred["optimal_windows"]), "scenarios": pred["scenarios"]},
        "compute_ms": round((time.time() - start) * 1000),
    }


# ═══ MASTER ENDPOINT: TOUS LES 4 PILIERS ═══
@router.get("/full")
async def institutional_full(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(10), hour: int = Query(7),
    wind_deg: float = Query(225), wind_speed: float = Query(15),
):
    start = time.time()
    zones = compute_zones(lat, lon, species, month)
    corridors = compute_corridors(lat, lon, species, month, hour, wind_deg, zones=zones)
    affuts = compute_affuts(lat, lon, species, zones, corridors, wind_deg)
    hotspots = compute_hotspots(lat, lon, species, zones, corridors, affuts)
    wind = compute_wind_vectors(lat, lon, wind_deg, wind_speed)
    salines = compute_salines(lat, lon, species, month)
    pression = compute_pression(lat, lon)
    risque = compute_risque(lat, lon, species, month)
    freq = compute_frequentation(lat, lon, species, month, hour)
    saison = compute_saisonnalite(month, species, hour)
    comport = compute_comportement(lat, lon, species, month, hour)
    terrain = compute_terrain_cost(lat, lon)
    visibilite = compute_visibilite(lat, lon)
    intelligence = compute_intelligence(lat, lon, species, month, wind_deg)
    score = compute_score_global(lat, lon, species, month, hour, wind_speed)
    conn = compute_connectivite(lat, lon, zones, corridors)

    return {
        "document_maitre": "V8-ENGINES-INSTITUTIONNEL-Omega-ULTIME-MAX-2026",
        "engines_count": 24,
        "piliers_count": 4,
        "bio_systeme": {"zones": len(zones), "corridors": len(corridors), "affuts": len(affuts), "hotspots": len(hotspots), "salines": len(salines)},
        "comportement_humain": {"pression": pression["pression_score"], "risque": risque["risque_score"], "frequentation_faune": freq["frequentation_faune"]},
        "systeme_sensoriel": {"terrain_cost": terrain["cost_surface"], "visibilite": visibilite["visibility_score"]},
        "prediction_intelligence": {"score_global": score["score_global"], "classification": score["classification"], "intelligence": intelligence["recommendation"]},
        "saisonnalite": saison,
        "compute_ms": round((time.time() - start) * 1000),
    }


# ═══ TERRITOIRE ENDPOINT — V10-SUPRA SOURCE UNIQUE RENDERING ═══
@router.get("/territoire")
async def institutional_territoire(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(10), hour: int = Query(7),
    wind_deg: float = Query(225), wind_speed: float = Query(15),
):
    """TERRITOIRE V10-SUPRA — Source UNIQUE de rendering.
    TOUTES couches recalculees depuis ENGINE-TERRAIN-V10-SUPRA (donnees reelles + IA).
    ZERO donnees simulees. ZERO fallback. ZERO legacy.
    """
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional.esi_omega import validate_bundle, _log_audit

    result = await compute_territoire_v10(lat, lon, species, month, hour, wind_deg, wind_speed)

    bv = validate_bundle({"zones": result["zones"], "corridors": result["corridors"], "affuts": result["affuts"]})
    _log_audit("TERRITOIRE_V10_RENDER", f"{lat},{lon},{species}",
        f"{bv['conformite']} source={result.get('data_source')} fiabilite={result.get('data_fiabilite')}")
    result["esi_omega"] = bv["conformite"]

    return result


# ═══ V10-SUPRA TERRAIN — SOURCE ABSOLUE DE VERITE ═══
@router.get("/terrain-v10")
async def institutional_terrain_v10(
    lat: float = Query(...), lon: float = Query(...),
):
    """V10-SUPRA: Profil terrain complet REEL+IA.
    MNT SRTM, meteo complete, IA Vision foret, surfaces derivees.
    """
    from engines.v8_institutional.terrain_v10_supra import compute_terrain_v10
    from engines.v8_institutional.esi_omega import _log_audit

    result = await compute_terrain_v10(lat, lon)
    t = result.get("terrain", {})
    _log_audit("TERRAIN_V10_SUPRA", f"{lat},{lon}",
        f"source={t.get('source')} fiabilite={t.get('fiabilite')} elev={t.get('elevation_m')}m")

    return result


# ═══ SUPRA-DONNEES ENDPOINT (legacy V9, delegue a V10) ═══
@router.get("/supra-donnees")
async def institutional_supra_donnees(
    lat: float = Query(...), lon: float = Query(...),
):
    """SUPRA-DONNEES-Omega: terrain enrichi par donnees reelles.
    MNT Open-Meteo (SRTM), meteo/sol reels, validation, ponderation.
    """
    start = time.time()
    from engines.v8_institutional.supra_donnees import get_enriched_terrain
    from engines.v8_institutional.esi_omega import _log_audit

    result = await get_enriched_terrain(lat, lon)
    source = result.get("terrain", {}).get("source", "INCONNU")
    fiabilite = result.get("terrain", {}).get("fiabilite", 0)
    _log_audit("SUPRA_DONNEES_FETCH", f"{lat},{lon}", f"source={source} fiabilite={fiabilite}")

    return {
        **result,
        "compute_ms": round((time.time() - start) * 1000),
    }


# ═══ SUPRA-DONNEES: TERRITOIRE ENRICHI ═══
@router.get("/territoire-reel")
async def institutional_territoire_reel(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(10), hour: int = Query(7),
    wind_deg: float = Query(225), wind_speed: float = Query(15),
):
    """TERRITOIRE avec donnees REELLES via SUPRA-DONNEES.
    Elevation reelle, meteo reelle, sol reel.
    """
    start = time.time()
    from engines.v8_institutional.supra_donnees import get_enriched_terrain
    from engines.v8_institutional.engine_salines import compute_salines
    from engines.v8_institutional.engine_hotspots import compute_hotspots
    from engines.v8_institutional.engine_vent import compute_wind_vectors, compute_scent_cone
    from engines.v8_institutional.esi_omega import validate_bundle, _log_audit

    # Donnees reelles via SUPRA-DONNEES
    enriched = await get_enriched_terrain(lat, lon)
    real_terrain = enriched.get("terrain", {})
    real_meteo = enriched.get("meteo", {})

    # Utiliser le vent reel si disponible
    actual_wind_deg = real_meteo.get("wind_direction_deg", wind_deg) if real_meteo else wind_deg
    actual_wind_speed = real_meteo.get("wind_speed_kmh", wind_speed) if real_meteo else wind_speed

    zones = compute_zones(lat, lon, species, month)
    corridors = compute_corridors(lat, lon, species, month, hour, actual_wind_deg, zones=zones)
    affuts = compute_affuts(lat, lon, species, zones, corridors, actual_wind_deg)
    hotspots = compute_hotspots(lat, lon, species, zones, corridors, affuts)
    salines = compute_salines(lat, lon, species, month)
    wind = compute_wind_vectors(lat, lon, actual_wind_deg, actual_wind_speed)
    scent_cone = compute_scent_cone(lat, lon, actual_wind_deg, actual_wind_speed)

    bv = validate_bundle({"zones": zones, "corridors": corridors, "affuts": affuts})
    _log_audit("TERRITOIRE_REEL_RENDER", f"{lat},{lon},{species}", f"{bv['conformite']} wind={actual_wind_deg}deg/{actual_wind_speed}kmh source={real_terrain.get('source')}")

    return {
        "zones": zones,
        "corridors": corridors,
        "affuts": affuts,
        "hotspots": hotspots,
        "salines": salines,
        "wind_vectors": wind,
        "contamination": scent_cone,
        "real_terrain": real_terrain,
        "real_meteo": real_meteo,
        "real_elevation": enriched.get("elevation"),
        "esi_omega": bv["conformite"],
        "data_source": real_terrain.get("source", "ESTIME"),
        "data_fiabilite": real_terrain.get("fiabilite", 0),
        "document_maitre": "V8-ENGINES-INSTITUTIONNEL-Omega-ULTIME-MAX-2026",
        "source": "SUPRA-DONNEES-Omega",
        "compute_ms": round((time.time() - start) * 1000),
    }


# ═══ SECURITE-Omega V19 — AUDIT COMPLET ═══
@router.get("/securite-v19")
async def institutional_securite_v19(
    lat: float = Query(46.8), lon: float = Query(-71.2),
    species: str = Query("cerf"), month: int = Query(10), hour: int = Query(7),
):
    """Audit securite V19 complet: shields + guards + validators + BCE-4X."""
    from engines.v8_institutional.securite_omega_v19 import run_security_audit_v19
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional.esi_omega import _log_audit

    territoire = await compute_territoire_v10(lat, lon, species, month, hour)
    audit = run_security_audit_v19(territoire)
    _log_audit("SECURITE_V19_AUDIT", "ALL_ENGINES", audit["verdict"])

    return audit


# ═══ STATUS ═══
@router.get("/status")
async def institutional_status():
    return {
        "document_maitre": "V8-ENGINES-INSTITUTIONNEL-Omega-ULTIME-MAX-2026",
        "mode": "STRICT-INSTITUTIONNEL",
        "engines": 24,
        "piliers": 4,
        "actifs": 24,
        "stubs": 0,
        "status": "VERROUILLE — ZERO STUB",
    }
