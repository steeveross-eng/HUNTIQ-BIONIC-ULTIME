"""
Scientific Overlay — K5
========================

BCE-4X ULTIME ABSOLU x3 | COMMANDANT STEEVE-MAX
Surcouche scientifique ADDITIVE pour chaque moteur.
ZERO modification des scores. LECTURE SEULE.

Genere des annotations scientifiques par moteur en consommant
knowledge.json v3.1.0 et Species Engine v3.
"""
import logging
from typing import Optional
from modules.bionic_knowledge_engine.knowledge_provider import _load_knowledge
from modules.species_engine.resolver import resolve, has_k2_data

logger = logging.getLogger("species_engine.k5_overlay")


def _get_season_en(season: str) -> str:
    m = {"printemps": "spring", "ete": "summer", "automne": "fall", "hiver": "winter"}
    return m.get(season.lower(), season.lower())


def overlay_supra(species: str, season: str, lat: float, lng: float) -> dict:
    """Surcouche scientifique pour SUPRA.
    Ajoute : profil espece, comportement saisonnier, sites critiques.
    ZERO modification du score SUPRA.
    """
    _, k2_id = resolve(species)
    if not k2_id:
        return {"_k5_activated": False, "reason": "no_k2_data"}

    k = _load_knowledge()
    season_en = _get_season_en(season)
    sp = k["species"].get(k2_id, {})
    sb = k.get("seasonal_behaviors", {}).get(k2_id, {}).get(season_en, {})
    cs = k.get("critical_sites", {}).get(k2_id, {})
    lt = k.get("long_term_trends", {}).get(k2_id, {})

    logger.info(f"K5-SUPRA activated: {k2_id}/{season_en} lat={lat}")
    return {
        "_k5_activated": True,
        "_engine": "SUPRA",
        "species_profile": {
            "id": k2_id,
            "scientific_name": sp.get("scientific_name"),
            "weight_kg": sp.get("weight_kg"),
            "home_range_km2": sp.get("home_range_km2"),
        },
        "seasonal_behavior": {
            "feeding_intensity": sb.get("feeding_intensity"),
            "movement_km_day": sb.get("movement_km_day"),
            "activity_peak_hours": sb.get("activity_peak_hours"),
            "aggregation": sb.get("aggregation"),
            "behavior_notes": sb.get("behavior_notes"),
        },
        "critical_sites_summary": list(cs.keys()) if cs else [],
        "population_trend": lt.get("population_trend"),
    }


def overlay_ultra(species: str, season: str, lat: float, lng: float) -> dict:
    """Surcouche scientifique pour ULTRA (saline).
    Ajoute : besoins sodium scientifiques, sensibilite climatique.
    ZERO modification du score ULTRA.
    """
    _, k2_id = resolve(species)
    if not k2_id:
        return {"_k5_activated": False, "reason": "no_k2_data"}

    k = _load_knowledge()
    season_en = _get_season_en(season)
    sodium = k.get("nutrition", {}).get("sodium", {}).get("data", {}).get(k2_id, {})
    cs = k.get("climate_sensitivity", {}).get(k2_id, {})
    sb = k.get("seasonal_behaviors", {}).get(k2_id, {}).get(season_en, {})

    logger.info(f"K5-ULTRA activated: {k2_id}/{season_en}")
    return {
        "_k5_activated": True,
        "_engine": "ULTRA",
        "sodium_scientific": {
            "need_mg_kg_day": sodium.get(season_en),
            "sodium_seeking": sb.get("sodium_seeking", False),
            "all_seasons": sodium,
        },
        "climate_impact": {
            "thermal_stress_c": cs.get("thermal_stress_threshold_c"),
            "vulnerability": cs.get("vulnerability"),
            "notes": cs.get("behavioral_response"),
        },
    }


def overlay_fiche(species: str, season: str, lat: float, lng: float) -> dict:
    """Surcouche scientifique pour FICHE.
    Ajoute : zones ecologiques pertinentes, habitats preferences.
    ZERO modification du score FICHE.
    """
    _, k2_id = resolve(species)
    if not k2_id:
        return {"_k5_activated": False, "reason": "no_k2_data"}

    k = _load_knowledge()
    sp = k["species"].get(k2_id, {})
    zones = k.get("ecological_zones", {}).get("zones", [])
    species_zones = [z for z in zones if k2_id in z.get("dominant_species", [])]

    logger.info(f"K5-FICHE activated: {k2_id}")
    return {
        "_k5_activated": True,
        "_engine": "FICHE",
        "habitat_preferences": sp.get("habitat_preferences", []),
        "ecological_zones": [
            {"id": z["id"], "name_fr": z["name_fr"], "biome": z["biome"]}
            for z in species_zones
        ],
        "human_tolerance": sp.get("human_tolerance"),
    }


def overlay_sol(species: str, season: str, lat: float, lng: float) -> dict:
    """Surcouche scientifique pour SOL.
    Ajoute : tolerance neige, impact sol sur espece.
    ZERO modification du score SOL.
    """
    _, k2_id = resolve(species)
    if not k2_id:
        return {"_k5_activated": False, "reason": "no_k2_data"}

    k = _load_knowledge()
    season_en = _get_season_en(season)
    st = k.get("snow_tolerance", {}).get(k2_id, {})
    tr = k.get("nutrition", {}).get("trace_elements", {})

    logger.info(f"K5-SOL activated: {k2_id}/{season_en}")
    return {
        "_k5_activated": True,
        "_engine": "SOL",
        "snow_tolerance": {
            "mobility_threshold_cm": st.get("mobility_threshold_cm"),
            "behavioral_response": st.get("behavioral_response"),
            "mortality_risk": st.get("mortality_risk"),
        },
        "trace_elements_needs": {
            el: {"optimal": data.get("optimal"), "unit": data.get("unit")}
            for el, data in tr.items()
            if k2_id in data.get("species_affected", [])
        },
    }


def overlay_territoire(species: str, season: str, lat: float, lng: float) -> dict:
    """Surcouche scientifique pour MON_TERRITOIRE.
    Validation scientifique des zones, corridors, habitats.
    ZERO modification des zones existantes.
    """
    _, k2_id = resolve(species)
    if not k2_id:
        return {"_k5_activated": False, "reason": "no_k2_data"}

    k = _load_knowledge()
    season_en = _get_season_en(season)
    sp = k["species"].get(k2_id, {})

    # Corridors pertinents
    dc = k.get("dynamic_corridors", {}).get("models", [])
    species_corridors = [
        {"id": c["id"], "type": c["type"], "driver": c["driver"], "max_km": c["max_distance_km"], "season": c["season"]}
        for c in dc if k2_id in c.get("species", [])
    ]
    season_corridors = [c for c in species_corridors if c["season"] == season_en or c["season"] == "all"]

    # Zones ecologiques
    zones = k.get("ecological_zones", {}).get("zones", [])
    species_zones = [
        {"id": z["id"], "biome": z["biome"], "lat_range": z["latitude_range"]}
        for z in zones if k2_id in z.get("dominant_species", [])
    ]

    # Critical sites pertinents pour la saison
    cs = k.get("critical_sites", {}).get(k2_id, {})
    seasonal_sites = {}
    for site_type, site_data in cs.items():
        site_season = site_data.get("season", "")
        month_map = {"spring": ["march", "april", "may"], "summer": ["june", "july", "august"],
                     "fall": ["september", "october", "november"], "winter": ["december", "january", "february"]}
        if site_season == "all" or season_en in site_season.lower():
            seasonal_sites[site_type] = site_data.get("habitat", "")

    # Cross-species presence
    csi = k.get("cross_species_inference", {})
    competitions = {}
    for pair_key, comp in csi.get("competition_matrix", {}).items():
        if k2_id in pair_key:
            competitions[pair_key] = {"type": comp["type"], "intensity": comp["intensity"]}

    logger.info(f"K5-MON_TERRITOIRE activated: {k2_id}/{season_en} ({lat},{lng})")
    return {
        "_k5_activated": True,
        "_engine": "MON_TERRITOIRE",
        "species_validation": {
            "id": k2_id,
            "scientific_name": sp.get("scientific_name"),
            "home_range_km2": sp.get("home_range_km2"),
        },
        "corridors_scientifiques": {
            "total": len(species_corridors),
            "seasonal": season_corridors,
            "all": species_corridors,
        },
        "zones_ecologiques": species_zones,
        "sites_critiques_saison": seasonal_sites,
        "interactions_especes": competitions,
        "data_quality": k.get("data_quality", {}).get("per_species", {}).get(k2_id, {}),
    }
