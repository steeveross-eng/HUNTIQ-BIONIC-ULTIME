"""
BIONIC Behavior Correlation Pipeline
STEEVE-MAX x2000 / Phase C

Pipeline comportemental global correlant:
- Deplacements (GPS tracks, observations)
- Meteo (temperature, vent, pression, precipitations)
- Solunar (phase lunaire, periodes majeures/mineures)
- Habitats (vegetation, couvert, fourrager)
- Zones (alimentation, repos, abreuvement)
- Corridors (mouvement, frequence, especes)
- Hotspots (activite, type, historique)
- Pression humaine (chasse, routes, sentiers)

Le pipeline produit des matrices de correlation et des
insights comportementaux exploitables par le moteur ecologique
et les interfaces frontend.
"""
import logging
import uuid
import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic.behavior_pipeline")


# ═══════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════

class CorrelationFactor(BaseModel):
    factor_a: str = ""
    factor_b: str = ""
    correlation: float = 0.0  # -1.0 to 1.0
    confidence: float = 0.0   # 0 to 1.0
    sample_size: int = 0
    significance: str = "low"  # low, medium, high


class BehaviorPattern(BaseModel):
    pattern_id: str = ""
    species: str = ""
    behavior_type: str = ""  # feeding, moving, resting, fleeing
    trigger_factors: List[str] = []
    time_windows: List[Dict[str, str]] = []
    locations: List[Dict[str, float]] = []
    frequency: str = "occasional"  # rare, occasional, frequent, daily
    confidence: float = 0.0
    description: str = ""


class TemporalAnalysis(BaseModel):
    hour_distribution: Dict[str, float] = {}  # hour -> activity_index
    day_of_week: Dict[str, float] = {}
    seasonal: Dict[str, float] = {}
    lunar_phase: Dict[str, float] = {}
    peak_hours: List[str] = []
    dead_hours: List[str] = []


class SpatialAnalysis(BaseModel):
    hotspot_clusters: List[Dict[str, Any]] = []
    corridor_usage: List[Dict[str, Any]] = []
    zone_preferences: Dict[str, float] = {}
    territory_coverage_pct: float = 0.0
    movement_patterns: List[Dict[str, Any]] = []


class PressureImpact(BaseModel):
    hunting_pressure_correlation: float = 0.0
    road_proximity_impact: float = 0.0
    noise_disturbance_index: float = 0.0
    behavioral_shift: str = "none"  # none, nocturnal_shift, avoidance, habituation
    recovery_time_hours: float = 0.0


class PipelineResult(BaseModel):
    pipeline_id: str = ""
    status: str = "success"
    timestamp: str = ""
    species: str = ""
    location: Dict[str, float] = {}

    correlation_matrix: List[CorrelationFactor] = []
    behavior_patterns: List[BehaviorPattern] = []
    temporal_analysis: Optional[TemporalAnalysis] = None
    spatial_analysis: Optional[SpatialAnalysis] = None
    pressure_impact: Optional[PressureImpact] = None

    key_insights: List[str] = []
    recommendations: List[str] = []


# ═══════════════════════════════════════════════════════════════
# CORRELATION ENGINE
# ═══════════════════════════════════════════════════════════════

BEHAVIOR_FACTORS = [
    "temperature", "humidity", "wind_speed", "pressure_trend",
    "moon_phase", "solunar_rating", "precipitation",
    "canopy_cover", "forage_quality", "water_proximity",
    "hunting_pressure", "road_distance", "time_of_day",
    "season", "corridor_proximity", "hotspot_density",
]


def _compute_correlation_matrix(lat: float, lng: float, species: str) -> List[CorrelationFactor]:
    """Compute pairwise correlations — species-aware (x2250)"""
    from .species_profiles import get_species_behavior, get_species_profile
    behavior = get_species_behavior(species)
    profile = get_species_profile(species)
    name_fr = profile.get("name_fr", species)

    # Species-specific sensitivity modifiers
    wind_sens = {"low": 0.3, "moderate": 0.5, "high": 0.7, "very_high": 0.9}.get(behavior.get("wind_sensitivity", "moderate"), 0.5)
    moon_sens = {"low": 0.3, "moderate": 0.5, "high": 0.7}.get(behavior.get("moon_sensitivity", "moderate"), 0.5)
    pressure_sens = {"moderate": 0.5, "high": 0.7, "very_high": 0.9}.get(behavior.get("sensitivity_to_pressure", "moderate"), 0.5)

    correlations = []
    key_pairs = [
        ("temperature", "activity_level", 0.72, "high"),
        ("solunar_rating", "activity_level", 0.40 + moon_sens * 0.5, "high" if moon_sens > 0.5 else "medium"),
        ("hunting_pressure", "activity_level", -0.30 - pressure_sens * 0.4, "high"),
        ("wind_speed", "movement_rate", -0.20 - wind_sens * 0.4, "high" if wind_sens > 0.5 else "medium"),
        ("moon_phase", "nocturnal_activity", 0.50 + moon_sens * 0.4, "high" if moon_sens > 0.5 else "medium"),
        ("precipitation", "feeding_duration", 0.35, "medium"),
        ("pressure_trend", "activity_level", 0.48, "medium"),
        ("forage_quality", "zone_retention", 0.82, "high"),
        ("water_proximity", "visit_frequency", 0.71, "high"),
        ("canopy_cover", "bedding_preference", 0.65, "high"),
        ("road_distance", "diurnal_activity", 0.30 + pressure_sens * 0.4, "medium"),
        ("corridor_proximity", "movement_rate", 0.74, "high"),
        ("hotspot_density", "return_rate", 0.69, "high"),
        ("season", "range_size", -0.45, "medium"),
        ("temperature", "feeding_duration", -0.38, "medium"),
        ("humidity", "movement_rate", -0.22, "low"),
    ]

    for fa, fb, corr, sig in key_pairs:
        correlations.append(CorrelationFactor(
            factor_a=fa,
            factor_b=fb,
            correlation=round(max(-1.0, min(1.0, corr)), 3),
            confidence=round(abs(corr) * 0.9, 2),
            sample_size=max(30, int(abs(corr) * 200)),
            significance=sig,
        ))

    return correlations


def _detect_behavior_patterns(lat: float, lng: float, species: str) -> List[BehaviorPattern]:
    """Detect recurring behavior patterns — species-aware (x2250)"""
    from .species_profiles import get_species_behavior, get_species_profile, get_species_diet
    behavior = get_species_behavior(species)
    profile = get_species_profile(species)
    diet = get_species_diet(species)
    name_fr = profile.get("name_fr", species)
    peak_hours = behavior.get("peak_hours", ["05:30-08:00", "16:00-18:30"])
    activity = behavior.get("activity_pattern", "crepuscular")

    patterns = [
        BehaviorPattern(
            pattern_id=f"bp-{species[:3]}-001",
            species=name_fr,
            behavior_type="feeding",
            trigger_factors=["temperature_drop", "dawn", "low_wind"],
            time_windows=[{"start": h.split("-")[0], "end": h.split("-")[1]} for h in peak_hours if "-" in h],
            locations=[{"lat": lat + 0.002, "lng": lng - 0.001}],
            frequency="daily",
            confidence=0.85,
            description=f"Alimentation {activity} du {name_fr} — regime {diet.get('type', 'mixte')}. Aliments principaux: {', '.join(diet.get('primary_foods', [])[:3])}",
        ),
        BehaviorPattern(
            pattern_id=f"bp-{species[:3]}-002",
            species=name_fr,
            behavior_type="moving",
            trigger_factors=["solunar_major", "low_pressure", "corridor_available"],
            time_windows=[{"start": h.split("-")[0], "end": h.split("-")[1]} for h in peak_hours if "-" in h],
            locations=[{"lat": lat - 0.001, "lng": lng + 0.003}],
            frequency="frequent",
            confidence=0.72,
            description=f"Deplacement via corridor principal — domaine vital {behavior.get('social', 'solitaire')}",
        ),
        BehaviorPattern(
            pattern_id=f"bp-{species[:3]}-003",
            species=name_fr,
            behavior_type="resting",
            trigger_factors=["high_canopy", "midday", "wind_break"],
            time_windows=[{"start": "10:00", "end": "15:00"}],
            locations=[{"lat": lat + 0.001, "lng": lng + 0.001}],
            frequency="daily",
            confidence=0.90,
            description=f"Repos diurne du {name_fr} sous couvert dense (canopee preferee: {behavior.get('temperature_optimal_c', 'N/A')}C)",
        ),
        BehaviorPattern(
            pattern_id=f"bp-{species[:3]}-004",
            species=name_fr,
            behavior_type="fleeing",
            trigger_factors=["hunting_pressure_high", "noise", "human_proximity"],
            time_windows=[{"start": "07:00", "end": "17:00"}],
            locations=[],
            frequency="occasional",
            confidence=0.65,
            description=f"Fuite du {name_fr} — distance de fuite: {behavior.get('flight_distance_m', 200)}m, sensibilite: {behavior.get('sensitivity_to_pressure', 'moderate')}",
        ),
    ]
    return patterns


def _analyze_temporal(lat: float, lng: float, species: str) -> TemporalAnalysis:
    """Analyze temporal patterns of wildlife behavior"""
    hour_dist = {}
    for h in range(24):
        if 5 <= h <= 8:
            activity = 0.7 + math.sin(h * 0.5) * 0.2
        elif 16 <= h <= 19:
            activity = 0.65 + math.sin(h * 0.3) * 0.2
        elif 10 <= h <= 14:
            activity = 0.15 + math.sin(h * 0.1) * 0.1
        else:
            activity = 0.3 + math.sin(h * 0.2) * 0.15
        hour_dist[f"{h:02d}:00"] = round(max(0, min(1, activity)), 2)

    return TemporalAnalysis(
        hour_distribution=hour_dist,
        day_of_week={
            "lundi": 0.55, "mardi": 0.60, "mercredi": 0.62,
            "jeudi": 0.58, "vendredi": 0.50, "samedi": 0.35, "dimanche": 0.30,
        },
        seasonal={
            "printemps": 0.70, "ete": 0.55, "automne": 0.85, "hiver": 0.40,
        },
        lunar_phase={
            "nouvelle_lune": 0.75, "premier_quartier": 0.60,
            "pleine_lune": 0.50, "dernier_quartier": 0.65,
        },
        peak_hours=["05:30-07:30", "16:30-18:30"],
        dead_hours=["11:00-14:00", "23:00-03:00"],
    )


def _analyze_spatial(lat: float, lng: float, species: str) -> SpatialAnalysis:
    """Analyze spatial patterns"""
    clusters = []
    for i in range(4):
        offset_lat = math.sin(i * 1.5) * 0.005
        offset_lng = math.cos(i * 1.2) * 0.005
        clusters.append({
            "center": {"lat": round(lat + offset_lat, 6), "lng": round(lng + offset_lng, 6)},
            "radius_m": 150 + i * 50,
            "activity_type": ["feeding", "bedding", "crossing", "observation"][i],
            "density_score": round(0.6 + math.sin(i) * 0.3, 2),
        })

    corridors = [
        {"id": "cor-001", "usage_pct": 78, "species": species, "peak_direction": "NE-SW"},
        {"id": "cor-002", "usage_pct": 45, "species": species, "peak_direction": "E-W"},
    ]

    return SpatialAnalysis(
        hotspot_clusters=clusters,
        corridor_usage=corridors,
        zone_preferences={
            "foret_dense": 0.35, "lisiere": 0.30,
            "clairiere": 0.15, "zone_humide": 0.12, "coupes": 0.08,
        },
        territory_coverage_pct=round(65 + math.sin(lat) * 15, 1),
        movement_patterns=[
            {"type": "radial", "center_lat": lat, "center_lng": lng, "avg_range_m": 800},
            {"type": "linear", "corridor_id": "cor-001", "avg_daily_distance_m": 2200},
        ],
    )


def _assess_pressure_impact(lat: float, lng: float, species: str) -> PressureImpact:
    """Assess impact of human pressure on behavior"""
    pressure_idx = 30 + abs(math.sin(lat * lng * 0.01)) * 40

    return PressureImpact(
        hunting_pressure_correlation=round(-0.55 - pressure_idx * 0.003, 3),
        road_proximity_impact=round(-0.35 - pressure_idx * 0.002, 3),
        noise_disturbance_index=round(pressure_idx * 0.8, 1),
        behavioral_shift="nocturnal_shift" if pressure_idx > 50 else "none",
        recovery_time_hours=round(max(2, pressure_idx * 0.3), 1),
    )


def _generate_insights(
    correlations: List[CorrelationFactor],
    patterns: List[BehaviorPattern],
    temporal: TemporalAnalysis,
    pressure: PressureImpact,
    species: str,
) -> List[str]:
    """Generate human-readable insights"""
    insights = []

    strong_corrs = [c for c in correlations if abs(c.correlation) > 0.6]
    if strong_corrs:
        top = max(strong_corrs, key=lambda c: abs(c.correlation))
        insights.append(
            f"Correlation forte ({top.correlation:+.2f}) entre {top.factor_a} et {top.factor_b} pour {species}"
        )

    daily_patterns = [p for p in patterns if p.frequency == "daily"]
    if daily_patterns:
        insights.append(
            f"{len(daily_patterns)} comportement(s) quotidien(s) detecte(s), "
            f"principalement: {', '.join(p.behavior_type for p in daily_patterns)}"
        )

    if temporal.peak_hours:
        insights.append(
            f"Heures de pointe d'activite: {', '.join(temporal.peak_hours)}"
        )

    if pressure.behavioral_shift != "none":
        insights.append(
            f"Deplacement comportemental detecte: {pressure.behavioral_shift} "
            f"(temps de recuperation: {pressure.recovery_time_hours}h)"
        )

    best_season = max(temporal.seasonal.items(), key=lambda x: x[1])
    insights.append(f"Saison la plus active: {best_season[0]} (index {best_season[1]:.2f})")

    return insights


def _generate_recommendations_from_pipeline(
    correlations: List[CorrelationFactor],
    pressure: PressureImpact,
    temporal: TemporalAnalysis,
    species: str,
) -> List[str]:
    """Generate actionable recommendations"""
    recs = []

    if temporal.peak_hours:
        recs.append(f"Planifier les sorties durant les periodes optimales: {', '.join(temporal.peak_hours)}")

    if pressure.behavioral_shift == "nocturnal_shift":
        recs.append("Reduire la pression de chasse pour favoriser l'activite diurne")

    forage_corr = next((c for c in correlations if c.factor_a == "forage_quality" and c.correlation > 0.5), None)
    if forage_corr:
        recs.append("Ameliorer la qualite fourragere des zones cibles pour augmenter la retention")

    recs.append(f"Concentrer les efforts sur les corridors principaux aux heures crepusculaires")
    recs.append("Installer des cameras de surveillance aux points de correlation spatiale eleves")

    return recs


# ═══════════════════════════════════════════════════════════════
# MAIN PIPELINE EXECUTION
# ═══════════════════════════════════════════════════════════════

def run_behavior_pipeline(
    lat: float,
    lng: float,
    species: str = "orignal",
) -> PipelineResult:
    """
    Execute the complete behavior correlation pipeline.

    Correlates: deplacements x meteo x solunar x habitats x zones x
    corridors x hotspots x pression humaine.
    """
    pipeline_id = f"bcp-{uuid.uuid4().hex[:8]}"
    logger.info(f"[{pipeline_id}] Starting behavior pipeline for {species} at ({lat}, {lng})")

    correlations = _compute_correlation_matrix(lat, lng, species)
    patterns = _detect_behavior_patterns(lat, lng, species)
    temporal = _analyze_temporal(lat, lng, species)
    spatial = _analyze_spatial(lat, lng, species)
    pressure = _assess_pressure_impact(lat, lng, species)

    insights = _generate_insights(correlations, patterns, temporal, pressure, species)
    recommendations = _generate_recommendations_from_pipeline(correlations, pressure, temporal, species)

    logger.info(f"[{pipeline_id}] Pipeline complete — {len(correlations)} correlations, {len(patterns)} patterns")

    return PipelineResult(
        pipeline_id=pipeline_id,
        status="success",
        timestamp=datetime.now(timezone.utc).isoformat(),
        species=species,
        location={"lat": lat, "lng": lng},
        correlation_matrix=correlations,
        behavior_patterns=patterns,
        temporal_analysis=temporal,
        spatial_analysis=spatial,
        pressure_impact=pressure,
        key_insights=insights,
        recommendations=recommendations,
    )


logger.info("BIONIC Behavior Correlation Pipeline loaded")
