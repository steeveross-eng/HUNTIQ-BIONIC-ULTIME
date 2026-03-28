"""
Weather Engine V3 — Moteur meteo BIONIC (remplace WeatherEngineV9)
===================================================================
BCE-4X PURGE: WeatherEngineV9 supprime. Ce moteur utilise les donnees
du contexte meteo V3 (Open-Meteo) pour evaluer l'impact meteorologique
sur les corridors fauniques.
"""

from .base import BionicEngine, EngineResult
from typing import Dict, Any


class WeatherEngineV3(BionicEngine):
    ENGINE_ID = "weather"
    ENGINE_NAME = "Weather Engine V3"
    DEFAULT_WEIGHT = 0.12

    def evaluate(self, context: Dict[str, Any]) -> EngineResult:
        weather = context.get("weather", {})
        season = context.get("season", "automne")
        species = context.get("species", "moose")

        if not weather:
            return EngineResult(
                engine_id=self.ENGINE_ID,
                score=50.0,
                weight=self.DEFAULT_WEIGHT,
                certainty=0.3,
                justification="Aucune donnee meteo disponible — score neutre",
                classification_impact=0,
                details={"source": "none"},
            )

        temp = weather.get("temperature", weather.get("temperature_c", 10))
        wind = weather.get("wind_speed_kmh", weather.get("wind_speed", 0))
        precip = weather.get("precipitation_1h_mm", weather.get("precipitation_mm", 0))
        humidity = weather.get("humidity", weather.get("humidity_pct", 50))

        # Score temperature
        temp_score = 70
        if species == "moose":
            if -10 <= temp <= 5:
                temp_score = 90
            elif temp < -25 or temp > 20:
                temp_score = 35
        elif species == "deer":
            if -5 <= temp <= 10:
                temp_score = 85
            elif temp < -20 or temp > 25:
                temp_score = 40
        elif species == "bear":
            if 5 <= temp <= 20:
                temp_score = 85
            elif temp < -5:
                temp_score = 20

        # Score vent
        wind_score = 80
        if 5 <= wind <= 20:
            wind_score = 90
        elif wind > 40:
            wind_score = 30
        elif wind > 25:
            wind_score = 55

        # Score precipitation
        precip_score = 75
        if 0.5 <= precip <= 3:
            precip_score = 85
        elif precip > 10:
            precip_score = 35
        elif precip > 5:
            precip_score = 50

        # Score composite
        score = temp_score * 0.4 + wind_score * 0.35 + precip_score * 0.25
        certainty = 0.85

        # Classification impact
        impact = 0
        if score >= 80:
            impact = 1
        elif score <= 40:
            impact = -1

        justification = (
            f"Meteo V3: {temp:.0f}C, vent {wind:.0f}km/h, precip {precip:.1f}mm "
            f"(temp={temp_score:.0f}, vent={wind_score:.0f}, precip={precip_score:.0f})"
        )

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=certainty,
            justification=justification,
            classification_impact=impact,
            details={
                "temperature_c": temp,
                "wind_kmh": wind,
                "precipitation_mm": precip,
                "humidity_pct": humidity,
                "sub_scores": {
                    "temperature": temp_score,
                    "wind": wind_score,
                    "precipitation": precip_score,
                },
                "source": "open-meteo-v3",
            },
        )
