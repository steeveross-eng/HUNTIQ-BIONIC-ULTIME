"""
SALINE INTELLIGENCE ULTRA — Seasonal Metabolism Engine V1
Cycles metaboliques saisonniers: rut, gestation, croissance bois, hibernation.
Interconnecte: solunar/engine (intensite lunaire), weather_engine (meteo),
               wildlife_nutritional_engine (besoins), bionic_engine_p0/services/species_behavior_v7.

Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x1000
"""
import math
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger("saline.seasonal_metabolism")

# Metabolic phases calendar (Quebec — cervids primarily)
METABOLIC_CALENDAR = {
    1: {"phase": "survie_hivernale", "energy_demand": 0.60, "mineral_priority": ["Ca", "P", "Mg"], "activity": "low"},
    2: {"phase": "survie_hivernale", "energy_demand": 0.55, "mineral_priority": ["Ca", "P", "Mg"], "activity": "low"},
    3: {"phase": "transition_printaniere", "energy_demand": 0.70, "mineral_priority": ["Na", "K", "Ca"], "activity": "increasing"},
    4: {"phase": "croissance_bois_debut", "energy_demand": 0.85, "mineral_priority": ["Ca", "P", "Na", "Zn"], "activity": "high"},
    5: {"phase": "croissance_bois_intense", "energy_demand": 1.00, "mineral_priority": ["Ca", "P", "Na", "Zn", "Cu"], "activity": "high"},
    6: {"phase": "croissance_bois_intense", "energy_demand": 1.00, "mineral_priority": ["Ca", "P", "Na", "Mg"], "activity": "high"},
    7: {"phase": "mineralisation_velours", "energy_demand": 0.90, "mineral_priority": ["Ca", "P", "Mn"], "activity": "moderate"},
    8: {"phase": "velours_durcissement", "energy_demand": 0.80, "mineral_priority": ["Ca", "P"], "activity": "moderate"},
    9: {"phase": "pre_rut", "energy_demand": 0.95, "mineral_priority": ["Na", "K", "Se", "Zn"], "activity": "high"},
    10: {"phase": "rut_actif", "energy_demand": 1.00, "mineral_priority": ["Na", "K", "Mg", "Se"], "activity": "very_high"},
    11: {"phase": "rut_tardif", "energy_demand": 0.90, "mineral_priority": ["Na", "Ca", "Mg"], "activity": "high"},
    12: {"phase": "recuperation_post_rut", "energy_demand": 0.65, "mineral_priority": ["Ca", "P", "Mg", "Cu"], "activity": "low"},
}

# Female-specific overrides
FEMALE_CALENDAR_OVERRIDE = {
    5: {"phase": "gestation_tardive", "energy_demand": 1.10, "mineral_priority": ["Ca", "P", "Se", "Cu", "Zn"]},
    6: {"phase": "lactation_debut", "energy_demand": 1.20, "mineral_priority": ["Ca", "P", "Na", "K", "Se"]},
    7: {"phase": "lactation_intense", "energy_demand": 1.15, "mineral_priority": ["Ca", "P", "Na", "K"]},
    8: {"phase": "lactation_sevrage", "energy_demand": 0.95, "mineral_priority": ["Ca", "P", "Na"]},
}

# Mineral demand multipliers per metabolic phase
PHASE_MINERAL_MULTIPLIERS = {
    "survie_hivernale": 0.60,
    "transition_printaniere": 0.80,
    "croissance_bois_debut": 1.30,
    "croissance_bois_intense": 1.50,
    "mineralisation_velours": 1.20,
    "velours_durcissement": 1.00,
    "pre_rut": 1.25,
    "rut_actif": 1.40,
    "rut_tardif": 1.15,
    "recuperation_post_rut": 0.70,
    "gestation_tardive": 1.35,
    "lactation_debut": 1.50,
    "lactation_intense": 1.40,
    "lactation_sevrage": 1.10,
}

# Solunar influence on mineral intake behavior
SOLUNAR_ACTIVITY_BOOST = {
    "extreme": 1.25,
    "fort": 1.15,
    "modere": 1.05,
    "faible": 1.00,
}


def get_metabolic_state(month: int, species: str = "orignal",
                        sex: str = "male", solunar_data: Dict = None,
                        weather_data: Dict = None) -> Dict[str, Any]:
    """
    Determine l'etat metabolique courant et les besoins mineraux prioritaires.
    Integre donnees solunaires et meteorologiques BIONIC.
    """
    calendar = METABOLIC_CALENDAR.get(month, METABOLIC_CALENDAR[10])

    # Female overrides
    if sex == "female" and month in FEMALE_CALENDAR_OVERRIDE:
        calendar = {**calendar, **FEMALE_CALENDAR_OVERRIDE[month]}

    phase = calendar["phase"]
    base_energy = calendar["energy_demand"]
    priority_minerals = calendar["mineral_priority"]
    activity = calendar.get("activity", "moderate")

    # Solunar intensity bonus (from BIONIC solunar/engine)
    solunar_boost = 1.0
    solunar_score = 0
    if solunar_data:
        solunar_score = solunar_data.get("solunar_score", 50)
        intensity = solunar_data.get("lunar_intensity", 0.5)
        if intensity > 0.8:
            solunar_boost = SOLUNAR_ACTIVITY_BOOST["extreme"]
        elif intensity > 0.6:
            solunar_boost = SOLUNAR_ACTIVITY_BOOST["fort"]
        elif intensity > 0.3:
            solunar_boost = SOLUNAR_ACTIVITY_BOOST["modere"]
        else:
            solunar_boost = SOLUNAR_ACTIVITY_BOOST["faible"]

    # Weather stress factor (from BIONIC weather_engine)
    weather_stress = 1.0
    temp_c = None
    if weather_data:
        temp_c = weather_data.get("temperature", weather_data.get("temp", None))
        if temp_c is not None:
            if temp_c < -20:
                weather_stress = 1.30  # extreme cold = higher energy demand
            elif temp_c < -10:
                weather_stress = 1.15
            elif temp_c > 30:
                weather_stress = 1.20  # heat stress
            elif temp_c > 25:
                weather_stress = 1.10

    # Final energy demand
    effective_energy = round(base_energy * solunar_boost * weather_stress, 3)
    mineral_multiplier = PHASE_MINERAL_MULTIPLIERS.get(phase, 1.0) * solunar_boost * weather_stress

    # Saline visit probability (higher during high-demand phases)
    visit_probability = _compute_visit_probability(phase, activity, solunar_boost)

    # Optimal saline check times (based on activity + solunar)
    peak_hours = _get_peak_hours(activity, solunar_data)

    return {
        "month": month,
        "species": species,
        "sex": sex,
        "metabolic_phase": phase,
        "energy_demand_factor": effective_energy,
        "mineral_multiplier": round(mineral_multiplier, 3),
        "priority_minerals": priority_minerals,
        "activity_level": activity,
        "solunar_boost": round(solunar_boost, 3),
        "solunar_score": solunar_score,
        "weather_stress_factor": round(weather_stress, 3),
        "temperature_c": temp_c,
        "saline_visit_probability": visit_probability,
        "peak_visit_hours": peak_hours,
        "recommendations": _generate_recommendations(phase, priority_minerals, month),
        "source": "BIONIC solunar/engine + weather_engine + species_behavior_v7",
    }


def _compute_visit_probability(phase: str, activity: str, solunar_boost: float) -> Dict[str, Any]:
    """Probabilite de visite saline basee sur la phase metabolique."""
    base_proba = {
        "very_high": 0.85,
        "high": 0.70,
        "moderate": 0.50,
        "increasing": 0.55,
        "low": 0.25,
    }.get(activity, 0.50)

    adjusted = min(0.98, base_proba * solunar_boost)

    return {
        "daily_probability": round(adjusted, 3),
        "weekly_expected_visits": round(adjusted * 7, 1),
        "confidence": "high" if adjusted > 0.7 else "moderate" if adjusted > 0.4 else "low",
    }


def _get_peak_hours(activity: str, solunar_data: Dict = None) -> List[Dict[str, str]]:
    """Heures de visite optimales combinant activite + solunaire."""
    base_peaks = []
    if activity in ("very_high", "high"):
        base_peaks = [
            {"start": "05:30", "end": "08:00", "type": "aube"},
            {"start": "16:00", "end": "19:30", "type": "crepuscule"},
        ]
    else:
        base_peaks = [
            {"start": "06:00", "end": "07:30", "type": "aube"},
            {"start": "17:00", "end": "18:30", "type": "crepuscule"},
        ]

    # Add solunar windows if available
    if solunar_data and "hunting_windows" in solunar_data:
        for window in solunar_data["hunting_windows"][:2]:
            base_peaks.append({
                "start": window.get("start", ""),
                "end": window.get("end", ""),
                "type": f"solunaire_{window.get('intensity', 'modere')}",
            })

    return base_peaks


def _generate_recommendations(phase: str, priority_minerals: List[str], month: int) -> List[str]:
    """Recommandations contextuelles pour la phase metabolique."""
    recs = []

    if "Na" in priority_minerals[:2]:
        recs.append("Sodium prioritaire — privilegier blocs/granules haute teneur Na")
    if "Ca" in priority_minerals[:2] and "P" in priority_minerals[:3]:
        recs.append("Phase osseuse — ratio Ca:P 2:1 optimal")
    if "Se" in priority_minerals:
        recs.append("Selenium critique — verifier supplementation Se")
    if "Zn" in priority_minerals and "Cu" in priority_minerals:
        recs.append("Oligo-elements essentiels — Zn et Cu pour immunite et reproduction")

    phase_recs = {
        "croissance_bois_intense": "Periode critique bois: maximiser Ca+P+Na, renouveler salines frequemment",
        "rut_actif": "Rut actif: forte consommation Na+K, visites frequentes, salines strategiques",
        "survie_hivernale": "Survie hivernale: acces reduit, privilegier emplacements proteges du vent",
        "lactation_debut": "Lactation: besoins Ca+P doubles, salines pres zones repos femelles",
        "gestation_tardive": "Gestation tardive: Se+Cu critiques pour sante du faon",
    }
    if phase in phase_recs:
        recs.append(phase_recs[phase])

    return recs
