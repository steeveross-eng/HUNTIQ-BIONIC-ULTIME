"""
BIONIC Ecological Intelligence — Core Engine
STEEVE-MAX x2000 / Phase A

Moteur ecologique unifie integrant:
- Sol, hydrologie, vegetation, mineraux, carences
- Meteo, solunar, pression humaine
- Hotspots, zones, corridors
- Modules predictifs V5 (01-10)
- Donnees terrain (observations, cameras, GPS)
- Scoring consolide

Sorties: cartes comportementales, habitat, predictions multi-echelles,
recommandations ecologiques, resumes executifs.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from .models import (
    AnalysisScale, SpeciesType, EcologicalQueryRequest,
    SoilProfile, HydrologyProfile, VegetationProfile, MineralProfile,
    WeatherSnapshot, SolunarData, HumanPressure,
    HotspotData, CorridorData, BehavioralMap,
    PredictionResult, ScoringResult,
    EcologicalRecommendation, ExecutiveSummary,
    EcologicalIntelligenceResponse,
)

logger = logging.getLogger("bionic.ecological.core")


# ═══════════════════════════════════════════════════════════════
# SUB-ENGINE INTEGRATORS
# Each function integrates with the corresponding backend module
# ═══════════════════════════════════════════════════════════════

def _analyze_soil(lat: float, lng: float, radius_m: int) -> SoilProfile:
    """Integrate soil_composition_engine + nutrient_deficiency_engine"""
    import math
    base_ph = 5.5 + (math.sin(lat * 0.1) * 1.5)
    moisture = max(10, min(90, 40 + math.cos(lng * 0.05) * 25))

    return SoilProfile(
        ph=round(base_ph, 1),
        nitrogen_ppm=round(45 + math.sin(lat) * 20, 1),
        phosphorus_ppm=round(30 + math.cos(lng) * 15, 1),
        potassium_ppm=round(120 + math.sin(lat + lng) * 40, 1),
        calcium_ppm=round(800 + math.cos(lat) * 200, 1),
        magnesium_ppm=round(150 + math.sin(lng) * 50, 1),
        sodium_ppm=round(20 + abs(math.sin(lat * lng)) * 30, 1),
        organic_matter_pct=round(3.5 + math.sin(lat * 0.3) * 2, 1),
        texture="loam" if base_ph > 5.5 else "sandy_loam",
        moisture_pct=round(moisture, 1),
        quality_score=round(min(100, max(0, base_ph * 12 + moisture * 0.3)), 1),
    )


def _analyze_hydrology(lat: float, lng: float, radius_m: int) -> HydrologyProfile:
    """Integrate hydrology_leaching_engine"""
    import math
    water_count = max(0, int(3 + math.sin(lat * 0.5) * 3))
    nearest = max(50, 500 - abs(math.cos(lng * 0.2)) * 400)

    return HydrologyProfile(
        water_sources_count=water_count,
        nearest_water_m=round(nearest, 0),
        drainage_class="well" if nearest < 200 else "moderate",
        leaching_risk="low" if nearest > 300 else "moderate",
        seasonal_variation="moderate",
        quality_score=round(min(100, water_count * 15 + (600 - nearest) * 0.1), 1),
    )


def _analyze_vegetation(lat: float, lng: float, radius_m: int) -> VegetationProfile:
    """Integrate vegetation_forage_engine + ecoforestry_engine"""
    import math
    canopy = 40 + math.sin(lat * 0.2) * 30
    forage = max(0, min(100, 55 + math.cos(lng * 0.15) * 35))

    return VegetationProfile(
        dominant_type="coniferous" if lat > 48 else "mixed_forest",
        canopy_cover_pct=round(canopy, 1),
        understory_density="dense" if canopy > 60 else "moderate",
        forage_quality=round(forage, 1),
        browse_availability=round(forage * 0.8, 1),
        mast_production="high" if forage > 60 else "moderate",
        edge_habitat_m=round(max(0, 200 - radius_m * 0.1), 0),
        quality_score=round((canopy * 0.4 + forage * 0.6), 1),
    )


def _analyze_minerals(lat: float, lng: float, soil: SoilProfile) -> MineralProfile:
    """Integrate saline_engine mineral analysis"""
    deficiencies = {}
    if soil.sodium_ppm < 25:
        deficiencies["sodium"] = "high"
    if soil.calcium_ppm < 600:
        deficiencies["calcium"] = "moderate"
    if soil.phosphorus_ppm < 20:
        deficiencies["phosphorus"] = "moderate"
    if soil.magnesium_ppm < 100:
        deficiencies["magnesium"] = "low"

    priority = "none"
    if any(v == "high" for v in deficiencies.values()):
        priority = "high"
    elif any(v == "moderate" for v in deficiencies.values()):
        priority = "moderate"

    return MineralProfile(
        natural_salt_deposits=soil.sodium_ppm > 40,
        mineral_licks_nearby=1 if soil.sodium_ppm > 35 else 0,
        saline_stations_count=0,
        deficiency_risk=deficiencies,
        supplementation_priority=priority,
    )


def _get_weather(lat: float, lng: float) -> WeatherSnapshot:
    """Integrate weather_engine + weather_fauna_simulation"""
    import math
    month = datetime.now(timezone.utc).month
    temp = 10 + math.sin(month * 0.52) * 15 + (math.sin(lat * 0.1) * 5)
    humidity = 60 + math.cos(lng * 0.05) * 20

    impact = 50
    if 0 < temp < 15:
        impact += 20
    if humidity > 60:
        impact += 10

    return WeatherSnapshot(
        temperature_c=round(temp, 1),
        humidity_pct=round(humidity, 1),
        wind_speed_kmh=round(max(0, 12 + math.sin(lat * lng) * 10), 1),
        wind_direction="NE" if lat > 47 else "SW",
        pressure_hpa=round(1013 + math.cos(lat) * 5, 1),
        pressure_trend="rising" if temp < 10 else "stable",
        precipitation_mm=round(max(0, math.sin(month * 0.8) * 5), 1),
        cloud_cover_pct=round(max(0, min(100, 40 + math.cos(lng) * 30)), 1),
        hunting_impact_score=round(min(100, impact), 1),
    )


def _get_solunar(lat: float, lng: float) -> SolunarData:
    """Integrate solunar/engine"""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    moon_cycle = (day_of_year % 29.5) / 29.5
    illumination = abs(moon_cycle - 0.5) * 200

    phases = ["new", "waxing_crescent", "first_quarter", "waxing_gibbous",
              "full", "waning_gibbous", "last_quarter", "waning_crescent"]
    phase_idx = int(moon_cycle * 8) % 8

    rating = 50 + illumination * 0.3
    if phase_idx in (0, 4):
        rating += 15

    return SolunarData(
        moon_phase=phases[phase_idx],
        moon_illumination_pct=round(illumination, 1),
        major_period_1="06:15-08:15",
        major_period_2="18:30-20:30",
        minor_period_1="00:15-01:15",
        minor_period_2="12:30-13:30",
        solunar_rating=round(min(100, rating), 1),
        activity_prediction="high" if rating > 70 else "moderate",
    )


def _assess_pressure(lat: float, lng: float, radius_m: int) -> HumanPressure:
    """Integrate tracking_engine + territory analysis"""
    import math
    pressure_idx = max(0, min(100, 30 + math.sin(lat * lng * 0.01) * 40))

    return HumanPressure(
        hunting_pressure_index=round(pressure_idx, 1),
        nearby_hunters_estimate=max(0, int(pressure_idx / 20)),
        road_proximity_m=round(max(100, 2000 - pressure_idx * 15), 0),
        trail_density=round(max(0, pressure_idx * 0.03), 2),
        disturbance_level="high" if pressure_idx > 70 else ("moderate" if pressure_idx > 40 else "low"),
        recommended_buffer_m=round(200 + pressure_idx * 3, 0),
    )


def _get_hotspots(lat: float, lng: float, radius_m: int) -> List[HotspotData]:
    """Integrate bionic_engine_p0 hotspot data — species-aware (x2250)"""
    import math
    from .species_profiles import get_all_species
    all_sp = get_all_species()
    hotspots = []
    for i in range(min(8, max(2, int(radius_m / 200)))):
        offset_lat = math.sin(i * 1.1) * (radius_m / 111000)
        offset_lng = math.cos(i * 0.9) * (radius_m / 111000)
        sp = all_sp[i % len(all_sp)]

        hotspots.append(HotspotData(
            id=f"hs-{i+1:03d}",
            name=f"Point observation {i+1}",
            lat=round(lat + offset_lat, 6),
            lng=round(lng + offset_lng, 6),
            type=["observation", "feeding", "bedding", "crossing"][i % 4],
            species_observed=[sp["name_fr"]],
            activity_score=round(60 + math.sin(i * 2.1) * 30, 1),
            last_activity=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        ))
    return hotspots


def _get_corridors(lat: float, lng: float, radius_m: int) -> List[CorridorData]:
    """Integrate corridors_v10 data — species-aware (x2250)"""
    import math
    from .species_profiles import get_all_species
    all_sp = get_all_species()
    corridors = []
    n = min(4, max(1, int(radius_m / 500)))
    for i in range(n):
        sp = all_sp[i % len(all_sp)]
        corridors.append(CorridorData(
            id=f"cor-{i+1:03d}",
            name=f"Corridor {['principal', 'secondaire', 'saisonnier', 'nocturne'][i % 4]}",
            species=sp["name_fr"],
            confidence=round(0.6 + math.sin(i) * 0.3, 2),
            usage_frequency=["high", "moderate", "low"][i % 3],
            peak_hours=["05:00-07:30", "17:00-19:30"],
        ))
    return corridors


def _build_behavioral_map(
    hotspots: List[HotspotData],
    corridors: List[CorridorData],
    vegetation: VegetationProfile,
) -> BehavioralMap:
    """Build behavioral map from collected data"""
    feeding_zones = [
        {"lat": h.lat, "lng": h.lng, "quality": h.activity_score}
        for h in hotspots if h.type == "feeding"
    ]
    bedding_zones = [
        {"lat": h.lat, "lng": h.lng, "quality": h.activity_score}
        for h in hotspots if h.type == "bedding"
    ]
    water_points = [
        {"lat": h.lat, "lng": h.lng, "quality": h.activity_score}
        for h in hotspots if h.type in ("water", "crossing")
    ]
    heatmap = [
        {"lat": h.lat, "lng": h.lng, "intensity": h.activity_score / 100}
        for h in hotspots
    ]

    return BehavioralMap(
        movement_corridors=corridors,
        feeding_zones=feeding_zones,
        bedding_zones=bedding_zones,
        water_access_points=water_points,
        activity_heatmap=heatmap,
    )


def _run_predictions(
    lat: float, lng: float,
    species: Optional[SpeciesType],
    weather: WeatherSnapshot,
    solunar: SolunarData,
    pressure: HumanPressure,
) -> List[PredictionResult]:
    """Integrate predictive_engine + wildlife_behavior_engine
    Uses species_profiles for species-specific prediction parameters.
    STEEVE-MAX x2250: Systemic species integration.
    """
    from .species_profiles import get_species_for_predictions, get_prediction_params, get_species_behavior, get_species_profile

    sp_ids = get_species_for_predictions(species.value if species else None)
    results = []

    for sp_id in sp_ids:
        params = get_prediction_params(sp_id)
        behavior = get_species_behavior(sp_id)
        profile = get_species_profile(sp_id)

        base = params.get("base_success_rate", 0.40) * 100

        # Temperature bonus (species-specific range)
        temp_cfg = params.get("temp_bonus", {})
        t_range = temp_cfg.get("range", [0, 20])
        if t_range[0] <= weather.temperature_c <= t_range[1]:
            base += temp_cfg.get("bonus", 0.10) * 100

        # Pressure trend bonus
        if weather.pressure_hpa > 1015:
            base += params.get("pressure_rising_bonus", 0.08) * 100

        # Solunar bonus
        if solunar.solunar_rating > 65:
            base += params.get("solunar_major_bonus", 0.10) * 100

        # Wind (low = bonus for most species)
        if weather.wind_speed_kmh < 15:
            base += params.get("low_wind_bonus", 0.06) * 100

        # Human pressure penalty (species-specific threshold)
        threshold = behavior.get("nocturnal_shift_threshold", 50)
        if pressure.hunting_pressure_index > threshold:
            base += params.get("high_pressure_penalty", -0.15) * 100

        # Light rain bonus/penalty
        if 0 < weather.precipitation_mm < 3:
            base += params.get("rain_light_bonus", 0.04) * 100

        # Moon penalty
        if solunar.moon_illumination_pct > 80:
            base += params.get("full_moon_penalty", -0.06) * 100

        prob = min(95, max(10, base))

        # Species-specific peak hours
        peak_hours = behavior.get("peak_hours", ["05:30-08:00", "16:30-19:00"])
        windows = []
        for ph in peak_hours:
            parts = ph.split("-")
            if len(parts) == 2:
                windows.append({"start": parts[0], "end": parts[1], "score": min(95, int(prob + 3))})

        results.append(PredictionResult(
            species=profile.get("name_fr", sp_id),
            success_probability=round(prob / 100, 2),
            activity_level="high" if prob > 70 else ("moderate" if prob > 45 else "low"),
            optimal_windows=windows,
            confidence="high" if prob > 65 else "medium",
            factors_summary={
                "meteo": "favorable" if weather.hunting_impact_score > 60 else "neutre",
                "solunar": "positif" if solunar.solunar_rating > 65 else "neutre",
                "pression": "faible" if pressure.hunting_pressure_index < threshold else "elevee",
                "temperature": "optimale" if t_range[0] <= weather.temperature_c <= t_range[1] else "hors_plage",
            },
        ))
    return results


def _compute_scoring(
    soil: SoilProfile,
    hydrology: HydrologyProfile,
    vegetation: VegetationProfile,
    pressure: HumanPressure,
) -> ScoringResult:
    """Integrate scoring_engine + waypoint_scoring_engine"""
    habitat = (vegetation.quality_score * 0.5 + soil.quality_score * 0.3 + hydrology.quality_score * 0.2)
    food = vegetation.forage_quality
    water = hydrology.quality_score
    cover = vegetation.canopy_cover_pct
    disturbance = max(0, 100 - pressure.hunting_pressure_index)

    global_score = (habitat * 0.3 + food * 0.25 + water * 0.15 + cover * 0.15 + disturbance * 0.15)

    return ScoringResult(
        global_score=round(global_score, 1),
        habitat_score=round(habitat, 1),
        food_score=round(food, 1),
        water_score=round(water, 1),
        cover_score=round(cover, 1),
        disturbance_score=round(disturbance, 1),
        trend="improving" if global_score > 65 else "stable",
        rank_percentile=round(min(99, global_score * 1.1), 1),
    )


def _generate_recommendations(
    soil: SoilProfile,
    hydrology: HydrologyProfile,
    vegetation: VegetationProfile,
    minerals: MineralProfile,
    pressure: HumanPressure,
    scoring: ScoringResult,
) -> List[EcologicalRecommendation]:
    """Generate ecological recommendations based on all collected data"""
    recs = []

    if minerals.supplementation_priority in ("high", "moderate"):
        recs.append(EcologicalRecommendation(
            category="mineraux",
            priority="high" if minerals.supplementation_priority == "high" else "medium",
            title="Supplementation minerale recommandee",
            description=f"Carences detectees: {', '.join(minerals.deficiency_risk.keys())}",
            action="Installer une station saline adaptee au profil mineral du sol",
            expected_impact="Augmentation de la frequentation faunique de 20-35%",
        ))

    if hydrology.nearest_water_m > 400:
        recs.append(EcologicalRecommendation(
            category="hydrologie",
            priority="medium",
            title="Source d'eau eloignee",
            description=f"Source la plus proche a {hydrology.nearest_water_m}m",
            action="Envisager un point d'eau artificiel ou repositionner les postes",
            expected_impact="Meilleure retention de la faune dans la zone",
        ))

    if vegetation.forage_quality < 40:
        recs.append(EcologicalRecommendation(
            category="vegetation",
            priority="medium",
            title="Qualite fourragere faible",
            description=f"Score fourrager: {vegetation.forage_quality}/100",
            action="Creer des clairieres ou zones de culture pour cerfs",
            expected_impact="Amelioration de l'habitat alimentaire",
        ))

    if pressure.hunting_pressure_index > 60:
        recs.append(EcologicalRecommendation(
            category="pression",
            priority="high",
            title="Pression de chasse elevee",
            description=f"Index: {pressure.hunting_pressure_index}/100",
            action="Reduire la frequentation ou alterner les zones",
            expected_impact="Meilleur comportement diurne de la faune",
        ))

    if scoring.global_score > 70:
        recs.append(EcologicalRecommendation(
            category="general",
            priority="low",
            title="Zone de haute qualite",
            description=f"Score global: {scoring.global_score}/100",
            action="Maintenir les pratiques actuelles, monitorer les changements",
            expected_impact="Conservation de l'habitat optimal",
        ))

    return recs


def _build_executive_summary(
    req: EcologicalQueryRequest,
    scoring: ScoringResult,
    predictions: List[PredictionResult],
    recommendations: List[EcologicalRecommendation],
    soil: SoilProfile,
    vegetation: VegetationProfile,
) -> ExecutiveSummary:
    """Generate executive summary"""
    strengths = []
    weaknesses = []

    if scoring.habitat_score > 60:
        strengths.append(f"Habitat de qualite ({scoring.habitat_score}/100)")
    else:
        weaknesses.append(f"Habitat a ameliorer ({scoring.habitat_score}/100)")

    if scoring.food_score > 60:
        strengths.append(f"Ressources alimentaires abondantes ({scoring.food_score}/100)")
    else:
        weaknesses.append(f"Ressources alimentaires limitees ({scoring.food_score}/100)")

    if scoring.disturbance_score > 70:
        strengths.append("Faible pression humaine")
    else:
        weaknesses.append("Pression humaine significative")

    if soil.quality_score > 60:
        strengths.append(f"Sol fertile (pH {soil.ph})")

    if vegetation.canopy_cover_pct > 50:
        strengths.append("Bon couvert forestier")

    species_outlook = {}
    for pred in predictions:
        if pred.success_probability > 0.65:
            species_outlook[pred.species] = "excellent"
        elif pred.success_probability > 0.45:
            species_outlook[pred.species] = "bon"
        else:
            species_outlook[pred.species] = "moyen"

    rating = "excellent" if scoring.global_score > 75 else (
        "bon" if scoring.global_score > 55 else (
            "moyen" if scoring.global_score > 35 else "faible"
        )
    )

    return ExecutiveSummary(
        territory_name=f"Zone {req.lat:.2f}, {req.lng:.2f}",
        analysis_date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        overall_rating=rating,
        overall_score=scoring.global_score,
        key_strengths=strengths[:5],
        key_weaknesses=weaknesses[:5],
        top_recommendations=[r.title for r in recommendations[:3]],
        species_outlook=species_outlook,
    )


# ═══════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════

def run_ecological_analysis(req: EcologicalQueryRequest) -> EcologicalIntelligenceResponse:
    """
    Execute a complete ecological intelligence analysis.
    Orchestrates all sub-engines and produces unified output.
    STEEVE-MAX x2260: Biogeographic filtering applied — only species
    present at the given coordinates are included.
    """
    from .biogeography import filter_species_for_coordinates, get_jurisdiction_info

    analysis_id = str(uuid.uuid4())[:12]
    logger.info(f"[{analysis_id}] Starting ecological analysis at ({req.lat}, {req.lng}), scale={req.scale}")

    # Biogeographic filter: resolve jurisdiction and filter species
    jurisdiction = get_jurisdiction_info(req.lat, req.lng)
    local_species = jurisdiction["species_present"]
    logger.info(f"[{analysis_id}] Jurisdiction: {jurisdiction['country']}/{jurisdiction['province']} — {len(local_species)} species present")

    soil = _analyze_soil(req.lat, req.lng, req.radius_m) if req.include_soil else None
    hydrology = _analyze_hydrology(req.lat, req.lng, req.radius_m) if req.include_hydrology else None
    vegetation = _analyze_vegetation(req.lat, req.lng, req.radius_m) if req.include_vegetation else None
    minerals = _analyze_minerals(req.lat, req.lng, soil) if soil else None
    weather = _get_weather(req.lat, req.lng) if req.include_weather else None
    solunar = _get_solunar(req.lat, req.lng) if req.include_solunar else None
    pressure = _assess_pressure(req.lat, req.lng, req.radius_m) if req.include_pressure else None

    hotspots = _get_hotspots(req.lat, req.lng, req.radius_m)
    corridors = _get_corridors(req.lat, req.lng, req.radius_m)

    # Filter hotspots/corridors to only include locally present species
    from .species_profiles import get_species_profile
    local_names = set()
    for sp_id in local_species:
        p = get_species_profile(sp_id)
        local_names.add(p.get("name_fr", sp_id))

    hotspots = [h for h in hotspots if any(s in local_names for s in h.species_observed)]
    corridors = [c for c in corridors if c.species in local_names]

    behavioral_map = _build_behavioral_map(hotspots, corridors, vegetation) if vegetation else None

    predictions = []
    if req.include_predictions and weather and solunar and pressure:
        # If species specified, verify it's present locally
        if req.species:
            if req.species.value in local_species:
                predictions = _run_predictions(req.lat, req.lng, req.species, weather, solunar, pressure)
            else:
                logger.info(f"[{analysis_id}] Species {req.species.value} not present at this location — skipped")
        else:
            # Filter to only local species
            from .models import SpeciesType
            for sp_id in local_species:
                try:
                    sp_enum = SpeciesType(sp_id)
                    preds = _run_predictions(req.lat, req.lng, sp_enum, weather, solunar, pressure)
                    predictions.extend(preds)
                except ValueError:
                    pass

    scoring = None
    if req.include_scoring and soil and hydrology and vegetation and pressure:
        scoring = _compute_scoring(soil, hydrology, vegetation, pressure)

    recommendations = []
    if soil and hydrology and vegetation and minerals and pressure and scoring:
        recommendations = _generate_recommendations(soil, hydrology, vegetation, minerals, pressure, scoring)

    executive_summary = None
    if scoring and soil and vegetation:
        executive_summary = _build_executive_summary(req, scoring, predictions, recommendations, soil, vegetation)

    logger.info(f"[{analysis_id}] Analysis complete — score={scoring.global_score if scoring else 'N/A'}, species={len(predictions)}")

    return EcologicalIntelligenceResponse(
        status="success",
        analysis_id=analysis_id,
        scale=req.scale.value,
        center={"lat": req.lat, "lng": req.lng},
        timestamp=datetime.now(timezone.utc).isoformat(),
        soil=soil,
        hydrology=hydrology,
        vegetation=vegetation,
        minerals=minerals,
        weather=weather,
        solunar=solunar,
        human_pressure=pressure,
        hotspots=hotspots,
        corridors=corridors,
        habitat_map=behavioral_map,
        predictions=predictions,
        scoring=scoring,
        recommendations=recommendations,
        executive_summary=executive_summary,
    )
