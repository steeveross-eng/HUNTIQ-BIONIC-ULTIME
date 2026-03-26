"""
SUPRA Advanced Engines — BCE-4X / STEEVE-MAX
==============================================
Moteurs d'analyse avancee pour le module SUPRA/INTELLIGENCE.

Moteurs:
  1. Pertinence Terrain — Score de pertinence du terrain pour la chasse
  2. Risque — Evaluation des risques (meteo, terrain, reglementation)
  3. Recommandation Intelligente — Suggestions basees sur les donnees (hybride LLM)
  4. Correlation Meteo/Terrain — Analyse croisee des donnees

Architecture: Algorithmes deterministes + couche LLM optionnelle
"""

from fastapi import APIRouter, Query
from datetime import datetime, timezone
import httpx
import logging
import math

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v6/supra/advanced", tags=["supra-advanced"])


# ============================================================
# 1. MOTEUR DE PERTINENCE TERRAIN
# ============================================================
def _compute_terrain_relevance(lat, lng, species, month, weather_data=None):
    """Calcul deterministe de la pertinence du terrain."""
    base_score = 60

    # Facteur saison
    season_bonus = {
        "cerf": {9: 25, 10: 30, 11: 25, 12: 15, 1: 10},
        "orignal": {9: 30, 10: 25, 11: 20, 12: 10},
        "dindon": {4: 25, 5: 30, 9: 20, 10: 15},
    }
    sp = species.lower() if species else "cerf"
    bonus = season_bonus.get(sp, season_bonus["cerf"]).get(month, 0)
    base_score += bonus

    # Facteur latitude (nord = meilleur pour grands gibiers)
    if lat and lat > 47:
        base_score += 10
    elif lat and lat > 46:
        base_score += 5

    # Facteur meteo (si disponible)
    if weather_data:
        wind = weather_data.get("wind_speed_kmh", 0)
        if 5 <= wind <= 15:
            base_score += 8
        pressure = weather_data.get("pressure_hpa", 1013)
        if pressure >= 1015:
            base_score += 5

    return min(100, max(0, round(base_score, 1)))


@router.get("/terrain-relevance")
async def terrain_relevance(
    lat: float = Query(...),
    lng: float = Query(...),
    species: str = Query("cerf"),
):
    """Score de pertinence du terrain pour la chasse."""
    month = datetime.now(timezone.utc).month

    # Fetch weather v3 data
    weather_data = None
    try:
        from engines.weather_v3.router import get_current_weather
        weather_data = await get_current_weather(lat, lng)
    except Exception:
        pass

    score = _compute_terrain_relevance(lat, lng, species, month, weather_data)

    factors = []
    if month in [9, 10, 11]:
        factors.append({"factor": "Saison d'automne", "impact": "positif", "detail": "Periode optimale pour le rut"})
    if lat and lat > 46.5:
        factors.append({"factor": "Latitude nord", "impact": "positif", "detail": "Zone propice au grand gibier"})
    if weather_data and weather_data.get("wind_speed_kmh", 0) < 20:
        factors.append({"factor": "Vent modere", "impact": "positif", "detail": "Dispersion d'odeur favorable"})

    return {
        "score": score,
        "species": species,
        "factors": factors,
        "engine": "terrain_relevance_v1",
    }


# ============================================================
# 2. MOTEUR DE RISQUE
# ============================================================
@router.get("/risk-assessment")
async def risk_assessment(
    lat: float = Query(...),
    lng: float = Query(...),
):
    """Evaluation des risques (meteo, terrain, reglementation)."""
    risks = []
    overall_risk = 0

    # Fetch weather
    weather_data = None
    try:
        from engines.weather_v3.router import get_current_weather
        weather_data = await get_current_weather(lat, lng)
    except Exception:
        pass

    if weather_data and not weather_data.get("error"):
        wind = weather_data.get("wind_speed_kmh", 0)
        if wind > 40:
            risks.append({"type": "meteo", "level": "critique", "detail": f"Vents violents ({wind} km/h)", "score": 90})
            overall_risk += 30
        elif wind > 25:
            risks.append({"type": "meteo", "level": "modere", "detail": f"Vents forts ({wind} km/h)", "score": 50})
            overall_risk += 15

        precip = weather_data.get("precipitation_mm", 0)
        if precip > 10:
            risks.append({"type": "meteo", "level": "modere", "detail": f"Fortes precipitations ({precip}mm)", "score": 60})
            overall_risk += 20

        visibility = weather_data.get("visibility_m")
        if visibility and visibility < 1000:
            risks.append({"type": "visibilite", "level": "critique", "detail": f"Visibilite reduite ({visibility}m)", "score": 80})
            overall_risk += 25

        temp = weather_data.get("temperature_c", 0)
        if temp < -20:
            risks.append({"type": "hypothermie", "level": "critique", "detail": f"Temperature extreme ({temp}C)", "score": 85})
            overall_risk += 25
        elif temp < -10:
            risks.append({"type": "hypothermie", "level": "modere", "detail": f"Froid intense ({temp}C)", "score": 50})
            overall_risk += 10

    # Risque reglementaire (heure legale)
    now_hour = datetime.now(timezone.utc).hour - 5  # EST approx
    if now_hour < 6 or now_hour > 18:
        risks.append({"type": "reglementaire", "level": "info", "detail": "Hors heures de chasse legales", "score": 30})

    if not risks:
        risks.append({"type": "global", "level": "faible", "detail": "Aucun risque majeur detecte", "score": 0})

    return {
        "overall_risk": min(100, overall_risk),
        "risk_level": "critique" if overall_risk > 60 else "modere" if overall_risk > 30 else "faible",
        "risks": risks,
        "engine": "risk_assessment_v1",
    }


# ============================================================
# 3. MOTEUR DE RECOMMANDATION INTELLIGENTE (Hybride)
# ============================================================
@router.get("/recommendations")
async def smart_recommendations(
    lat: float = Query(...),
    lng: float = Query(...),
    species: str = Query("cerf"),
    use_llm: bool = Query(False),
):
    """Recommandations intelligentes basees sur les conditions actuelles."""
    month = datetime.now(timezone.utc).month

    # Fetch weather
    weather_data = None
    try:
        from engines.weather_v3.router import get_current_weather
        weather_data = await get_current_weather(lat, lng)
    except Exception:
        pass

    # Algorithme deterministe
    recommendations = []

    if weather_data and not weather_data.get("error"):
        wind = weather_data.get("wind_speed_kmh", 0)
        temp = weather_data.get("temperature_c", 0)
        pressure = weather_data.get("pressure_hpa", 1013)
        hunting = weather_data.get("hunting_score", {})

        # Vent
        if wind < 5:
            recommendations.append({
                "category": "vent",
                "priority": "haute",
                "text": "Vent tres faible. Privilegiez les affuts en hauteur pour eviter la detection par l'odeur.",
                "action": "Utilisez un affut sureleve ou un treestand.",
            })
        elif 5 <= wind <= 15:
            recommendations.append({
                "category": "vent",
                "priority": "info",
                "text": "Conditions de vent optimales. Le vent leger disperse bien votre odeur.",
                "action": "Positionnez-vous face au vent pour maximiser la couverture.",
            })
        elif wind > 25:
            recommendations.append({
                "category": "vent",
                "priority": "critique",
                "text": "Vents forts. Animaux au repos dans les zones protegees.",
                "action": "Cherchez les corridors abrites et les fonds de vallee.",
            })

        # Pression
        if pressure >= 1020:
            recommendations.append({
                "category": "pression",
                "priority": "haute",
                "text": "Haute pression — activite animale accrue. Moment optimal pour la chasse.",
                "action": "Sortez aux heures matinales et en fin de journee.",
            })
        elif pressure < 1000:
            recommendations.append({
                "category": "pression",
                "priority": "info",
                "text": "Basse pression. Les animaux se nourrissent avant la tempete.",
                "action": "Concentrez-vous sur les zones d'alimentation.",
            })

        # Temperature
        if temp < -10:
            recommendations.append({
                "category": "temperature",
                "priority": "critique",
                "text": f"Temperature tres basse ({temp}C). Risque d'hypothermie.",
                "action": "Equipement thermique obligatoire. Limitez les sorties a 2-3h.",
            })

        # Saison
        if species.lower() == "cerf" and month in [10, 11]:
            recommendations.append({
                "category": "saison",
                "priority": "haute",
                "text": "Periode de rut active. Les males sont en deplacement.",
                "action": "Utilisez les appels et les leurres de rut dans les corridors.",
            })

    # LLM optionnel (si active et configure)
    llm_recommendation = None
    if use_llm:
        llm_recommendation = "[LLM] Module IA non active. Activez l'integration LLM dans la configuration pour obtenir des recommandations personnalisees."

    return {
        "recommendations": recommendations,
        "count": len(recommendations),
        "llm_enabled": use_llm,
        "llm_recommendation": llm_recommendation,
        "engine": "smart_recommendations_v1",
    }


# ============================================================
# 4. MOTEUR DE CORRELATION METEO/TERRAIN
# ============================================================
@router.get("/weather-terrain-correlation")
async def weather_terrain_correlation(
    lat: float = Query(...),
    lng: float = Query(...),
    species: str = Query("cerf"),
):
    """Analyse croisee meteo/terrain pour predictions d'activite."""
    month = datetime.now(timezone.utc).month

    # Fetch weather
    weather_data = None
    try:
        from engines.weather_v3.router import get_current_weather
        weather_data = await get_current_weather(lat, lng)
    except Exception:
        pass

    terrain_score = _compute_terrain_relevance(lat, lng, species, month, weather_data)

    hunting_score = 50
    if weather_data and weather_data.get("hunting_score"):
        hunting_score = weather_data["hunting_score"].get("overall", 50)

    # Correlation composite
    composite = round(terrain_score * 0.5 + hunting_score * 0.5, 1)

    # Prediction d'activite
    if composite >= 75:
        activity = "tres_elevee"
        prediction = "Conditions exceptionnelles. Forte probabilite d'activite animale."
    elif composite >= 60:
        activity = "elevee"
        prediction = "Bonnes conditions. Activite animale probable aux heures crepusculaires."
    elif composite >= 45:
        activity = "moderee"
        prediction = "Conditions moyennes. Activite concentree sur les zones d'alimentation."
    else:
        activity = "faible"
        prediction = "Conditions defavorables. Animaux au repos dans les zones de couvert."

    return {
        "composite_score": composite,
        "terrain_score": terrain_score,
        "weather_score": hunting_score,
        "predicted_activity": activity,
        "prediction": prediction,
        "species": species,
        "engine": "weather_terrain_correlation_v1",
    }
