"""
ENGINE-HABITAT-SUPRA — Moteur habitat institutionnel
=====================================================
Extrait + etend la fonction `score_habitat` de NUTRITION-V12-SUPRA en
moteur dedie reutilisable par tous les engines en aval.

Inputs:  terrain_v10 (LiDAR 1m + IRDA + Open-Meteo)
Outputs: score 0-100, breakdown 7 facteurs, mosaicite, habitat_type
"""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-HABITAT-SUPRA"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(
    name=ENGINE_NAME,
    version=ENGINE_VERSION,
    description="Habitat score 0-100 depuis LiDAR+IRDA+IA-Vision (couvert, strate, feuillus, hydrologie, drainage, pente, exposition) + mosaicite + habitat_type",
    pillar="BIO-SYSTEME",
    dependencies=["LIDAR_WCS_1M", "IRDA_PEDOLOGIE", "OPEN_METEO"],
)


def _habitat_type(terrain: dict) -> str:
    """Classification ecologique simplifiee de l'habitat."""
    canopy = terrain.get("canopy", 0.5)
    feuillus = terrain.get("feuillus_ratio", 0.4)
    if canopy < 0.3:
        return "ouvert"
    if canopy > 0.8:
        return "ferme"
    if feuillus > 0.6:
        return "mixte-feuillus"
    if feuillus < 0.25:
        return "resineux"
    return "mixte"


def _mosaicite(terrain: dict) -> float:
    """Indice 0-1 de mosaicite (diversite verticale + strates)."""
    canopy = terrain.get("canopy", 0.5)
    strate = terrain.get("strate_1_3m", 0.3)
    rugosite = terrain.get("rugosite", 0.5)
    # Mosaicite optimum = canopy middle + strate haute + rugosite haute
    val = (1 - abs(canopy - 0.65)) * 0.4 + strate * 0.3 + rugosite * 0.3
    return round(max(0.0, min(1.0, val)), 3)


def compute_habitat_supra(terrain_v10: dict, contamination_v2: dict | None = None) -> dict:
    """Retourne habitat score + breakdown + type + mosaicite.

    Phase X-C: intégration profonde contamination_v2 (CWD/MDC) comme paramètre
    direct. Pénalise composite selon cwd_risk et distance zone MDC.
    """
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}

    canopy = terrain.get("canopy", 0.5)
    strate = terrain.get("strate_1_3m", 0.3)
    feuillus = terrain.get("feuillus_ratio", 0.4)
    couvert_pct = terrain.get("couvert_pct", 50.0)
    pente = terrain.get("pente_deg", 10.0)
    exposition = terrain.get("exposition_deg", 180.0)
    distance_eau = terrain.get("distance_eau_m", 200)
    drainage = terrain.get("drainage_class", 3)

    s_couvert = max(0, 100 - abs(couvert_pct - 70) * 2)
    s_strate = min(100, strate * 100 * 1.2)
    s_feuillus = min(100, feuillus * 100 + 10)
    if distance_eau < 30:
        s_hydro = 55
    elif distance_eau < 250:
        s_hydro = 95
    elif distance_eau < 600:
        s_hydro = 75
    else:
        s_hydro = 45
    s_drainage = max(20, 100 - abs(drainage - 4) * 18)
    if 5 <= pente <= 20:
        s_pente = 95
    elif pente < 5:
        s_pente = 65
    elif pente <= 35:
        s_pente = max(30, 95 - (pente - 20) * 3)
    else:
        s_pente = 20
    expo_norm = abs(((exposition - 180) + 180) % 360 - 180)
    s_expo = max(40, 100 - expo_norm * 0.3)

    composite = round(
        s_couvert * 0.18 + s_strate * 0.20 + s_feuillus * 0.18
        + s_hydro * 0.12 + s_drainage * 0.10 + s_pente * 0.12 + s_expo * 0.10,
        1,
    )

    # Phase X-C : malus contamination_v2 (CWD/MDC)
    cwd_malus = 0.0
    cwd_info = {}
    if contamination_v2:
        risk = (contamination_v2.get("cwd_risk") or "").upper()
        dist = contamination_v2.get("distance_nearest_cwd_km")
        if risk == "ELEVE":
            cwd_malus = 12.0
        elif risk == "MODERE":
            cwd_malus = 6.0
        elif risk == "FAIBLE":
            cwd_malus = 2.0
        composite = round(max(0.0, composite - cwd_malus), 1)
        cwd_info = {"cwd_risk": risk or None, "distance_km": dist, "malus_applied": cwd_malus}

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "score": composite,
        "habitat_type": _habitat_type(terrain),
        "mosaicite": _mosaicite(terrain),
        "canopy": canopy,
        "breakdown": {
            "couvert": round(s_couvert, 1),
            "strate": round(s_strate, 1),
            "feuillus": round(s_feuillus, 1),
            "hydro": round(s_hydro, 1),
            "drainage": round(s_drainage, 1),
            "pente": round(s_pente, 1),
            "exposition": round(s_expo, 1),
        },
        "contamination_v2_impact": cwd_info or None,
        "data_sources": ["LIDAR_WCS_1M", "IRDA_PEDOLOGIE", "OPEN_METEO"],
    }
