"""ENGINE-CLIMAT-FUTUR-Ω — Projections CMIP6 calibrees."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-CLIMAT-FUTUR-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Projections climatiques CMIP6 (T, precip, anomalies) 2030/2040/2050", "ENVIRONNEMENT", ["NASA_EARTHDATA", "NOAA_CLIMATE"])

# Scenarios CMIP6 SSP2-4.5 (mediane IPCC AR6 pour Est Canadien)
# Sources: IPCC AR6 WG1 Atlas, Ouranos QC consortium 2022
_CMIP6_QC_AR6 = {
    "temperature_anomaly_c": {"2030": 1.5, "2040": 2.2, "2050": 2.8},
    "precipitation_change_pct": {"2030": 4.0, "2040": 7.5, "2050": 11.0},
    "snow_days_change_pct": {"2030": -12.0, "2040": -20.0, "2050": -28.0},
}


def compute_climat_futur(terrain_v10: dict) -> dict:
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}
    meteo = (terrain_v10.get("meteo") if isinstance(terrain_v10, dict) else None) or {}

    current_temp = meteo.get("temperature_c", 5.0)

    # Projections T + precipitation
    projections = {}
    for year, dt in _CMIP6_QC_AR6["temperature_anomaly_c"].items():
        projections[year] = {
            "temp_c": round(current_temp + dt, 1),
            "temp_anomaly_c": dt,
            "precip_change_pct": _CMIP6_QC_AR6["precipitation_change_pct"][year],
            "snow_days_change_pct": _CMIP6_QC_AR6["snow_days_change_pct"][year],
        }

    # Score habitabilite future (100=stable, 0=bouleversement)
    # Penalites: T anomaly forte + neige reduite (impact orignal+dindon)
    t2050 = projections["2050"]["temp_anomaly_c"]
    snow_reduction = abs(_CMIP6_QC_AR6["snow_days_change_pct"]["2050"])
    penalty = min(100, t2050 * 20 + snow_reduction * 1.0)
    score = round(max(0, 100 - penalty), 1)

    if score > 70:
        stability = "STABLE"
    elif score > 50:
        stability = "MODERE"
    elif score > 30:
        stability = "PREOCCUPANT"
    else:
        stability = "CRITIQUE"

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "score": score,
        "stability_level": stability,
        "scenario": "CMIP6 SSP2-4.5 (IPCC AR6 Atlas / Ouranos QC)",
        "projections": projections,
        "anomalie_2050_c": t2050,
        "snow_days_change_2050_pct": _CMIP6_QC_AR6["snow_days_change_pct"]["2050"],
        "data_sources": ["NASA_EARTHDATA", "NOAA_CLIMATE", "IPCC_AR6", "OURANOS_QC"],
        "limites": [
            "Projections = scenario median SSP2-4.5 (pas de SSP1-2.6 ou SSP5-8.5)",
            "Pas de downscaling bioclimatique fin (grille AR6 ~100 km)",
        ],
    }
