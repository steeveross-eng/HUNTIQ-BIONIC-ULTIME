"""
ENGINE-HYDROLOGIE-SUPRA — Moteur hydrologie institutionnel
===========================================================
Inputs: terrain_v10 (IRDA drainage, soil_moisture, nappe + LiDAR elevation)
Outputs: score 0-100, indices (retention, surface_water_proximity, drainage_quality, flood_risk)
"""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-HYDROLOGIE-SUPRA"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(
    name=ENGINE_NAME,
    version=ENGINE_VERSION,
    description="Hydrologie institutionnelle (surface water, drainage, retention, flood risk, nappe)",
    pillar="BIO-SYSTEME",
    dependencies=["IRDA_PEDOLOGIE", "LIDAR_WCS_1M", "OPEN_METEO"],
)


def compute_hydrologie_supra(terrain_v10: dict) -> dict:
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}

    distance_eau = terrain.get("distance_eau_m", 300)
    drainage = terrain.get("drainage_class", 3)
    soil_moisture = terrain.get("soil_moisture", 0.3)
    nappe = terrain.get("nappe_profondeur_m", 1.0)
    hydro_index = terrain.get("hydro_index", 0.3)
    zone_humide = terrain.get("zone_humide", False)
    pente = terrain.get("pente_deg", 10.0)

    # Proximite eau de surface (100=tres proche, 0=loin)
    if distance_eau < 50:
        s_prox = 100
    elif distance_eau < 300:
        s_prox = 85
    elif distance_eau < 800:
        s_prox = 55
    else:
        s_prox = 25

    # Drainage: optimum 3-5
    s_drainage = max(15, 100 - abs(drainage - 4) * 18)

    # Capacite retention (nappe haute + soil_moisture = retention forte)
    retention = min(1.0, soil_moisture * 0.6 + max(0, 1 - nappe / 3) * 0.4)
    s_retention = round(retention * 100, 1)

    # Risque inondation (plat + zone humide + nappe haute + sol sature)
    flood_score = 0.0
    if pente < 3:
        flood_score += 30
    if zone_humide:
        flood_score += 30
    if nappe < 0.5:
        flood_score += 20
    if soil_moisture > 0.5:
        flood_score += 20
    s_flood = min(100, flood_score)

    # Score composite: proximite 25%, drainage 25%, retention 25%, flood INVERSE 25%
    composite = round(s_prox * 0.25 + s_drainage * 0.25 + s_retention * 0.25 + (100 - s_flood) * 0.25, 1)

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "score": composite,
        "proximity_water_score": round(s_prox, 1),
        "drainage_score": round(s_drainage, 1),
        "retention_score": s_retention,
        "flood_risk_score": round(s_flood, 1),
        "hydro_index": hydro_index,
        "zone_humide": zone_humide,
        "nappe_profondeur_m": nappe,
        "data_sources": ["IRDA_PEDOLOGIE", "LIDAR_WCS_1M", "OPEN_METEO"],
    }
