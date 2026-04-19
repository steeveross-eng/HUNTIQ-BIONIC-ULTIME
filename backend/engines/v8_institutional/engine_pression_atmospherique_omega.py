"""ENGINE-PRESSION-ATMOSPHERIQUE-Ω — Pression + tendance + impact faunique."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-PRESSION-ATMOSPHERIQUE-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Pression atmospherique + tendance + impact comportemental faunique", "ENVIRONNEMENT", ["OPEN_METEO"])


def compute_pression_atmospherique(terrain_v10: dict) -> dict:
    mark_call(ENGINE_NAME)
    meteo = (terrain_v10.get("meteo") if isinstance(terrain_v10, dict) else None) or {}
    # fallback sur terrain_v10 directement si c'est deja un dict meteo
    if "pressure_hpa" not in meteo and "pressure_msl_hpa" not in meteo:
        src = terrain_v10 if isinstance(terrain_v10, dict) else {}
        if "pressure_hpa" in src or "pressure_msl_hpa" in src:
            meteo = src

    pressure_hpa = meteo.get("pressure_hpa") or meteo.get("pressure_msl_hpa") or 1013.25
    trend_hpa_24h = meteo.get("pressure_trend_24h") or 0.0

    # Activite faunique: optimum pression 1010-1020, baisse (fronts) = alimentation avant front
    if 1010 <= pressure_hpa <= 1020:
        stability = "STABLE"
        base_score = 80
    elif 1005 <= pressure_hpa < 1010 or 1020 < pressure_hpa <= 1025:
        stability = "TRANSITION"
        base_score = 70
    elif pressure_hpa < 1005:
        stability = "BASSE"
        base_score = 55
    else:
        stability = "HAUTE"
        base_score = 65

    # Bonus si baisse (front approchant = activite pre-front accrue)
    if trend_hpa_24h < -2:
        base_score = min(100, base_score + 15)
        trend_effect = "PRE-FRONT (activite accrue)"
    elif trend_hpa_24h > 2:
        base_score = max(0, base_score - 5)
        trend_effect = "POST-FRONT (activite reduite)"
    else:
        trend_effect = "STABLE"

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "score": base_score,
        "pressure_hpa": round(pressure_hpa, 1),
        "trend_24h_hpa": round(trend_hpa_24h, 2),
        "stability_level": stability,
        "trend_effect": trend_effect,
        "activity_forecast": "ELEVEE" if base_score > 75 else ("NORMALE" if base_score > 55 else "FAIBLE"),
        "data_sources": ["OPEN_METEO"],
        "references": [
            "Vercauteren et al. 2006 — deer activity & barometric pressure",
            "Solunar fluctuations — atmospheric",
        ],
    }
