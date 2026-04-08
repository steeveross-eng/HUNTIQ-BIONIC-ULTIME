"""
Knowledge Provider — Singleton d'acces au knowledge.json
=========================================================

K1 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
ZERO_INTERPRETATION | ZERO_REGRESSION | ZERO_LOSS | TRACEABILITY

Ce module charge knowledge.json une seule fois au demarrage et expose
des fonctions de lookup par species, habitat, soil, nutrition.
Les moteurs SUPRA/ULTRA/FICHE/SOL importent ce module pour enrichir
leurs reponses avec les annotations scientifiques (sources, evidence_level).

Usage:
    from modules.bionic_knowledge_engine.knowledge_provider import (
        get_species_data,
        get_habitat_data,
        get_soil_data,
        get_nutrition_data,
        get_sources_for_ids,
        get_evidence_level,
        get_knowledge_meta,
    )
"""
import json
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Singleton — charge une seule fois
_KNOWLEDGE: Optional[dict] = None
_KNOWLEDGE_PATH = os.path.join(
    os.path.dirname(__file__), "data", "knowledge.json"
)


def _load_knowledge() -> dict:
    global _KNOWLEDGE
    if _KNOWLEDGE is None:
        with open(_KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
            _KNOWLEDGE = json.load(f)
        logger.info(
            f"Knowledge Engine loaded: {len(_KNOWLEDGE['sources'])} sources, "
            f"{len(_KNOWLEDGE['species'])} species, "
            f"{len(_KNOWLEDGE['habitats'])} habitats, "
            f"{len(_KNOWLEDGE['soils'])} soils"
        )
    return _KNOWLEDGE


# ==============================================
# SPECIES LOOKUP
# ==============================================

def get_species_data(species_id: str) -> Optional[dict]:
    """Get species data by id (moose, deer, bear, elk, turkey).
    Maps common names: orignal->moose, cerf->deer, ours->bear, wapiti->elk, dindon->turkey.
    Compatible v3.0.0 (dict) and v2.0.0 (list).
    """
    k = _load_knowledge()
    name_map = {
        "orignal": "moose", "moose": "moose",
        "cerf": "deer", "deer": "deer", "chevreuil": "deer", "cerf_virginie": "deer",
        "ours": "bear", "bear": "bear", "ours_noir": "bear",
        "wapiti": "elk", "elk": "elk",
        "dindon": "turkey", "turkey": "turkey", "dindon_sauvage": "turkey",
    }
    mapped_id = name_map.get(species_id.lower(), species_id.lower())
    species_data = k["species"]
    if isinstance(species_data, dict):
        return species_data.get(mapped_id)
    for sp in species_data:
        if sp["id"] == mapped_id:
            return sp
    return None


def get_species_habitat_preferences(species_id: str) -> list:
    """Get habitat preferences with source annotations for a species."""
    sp = get_species_data(species_id)
    if not sp:
        return []
    return sp.get("habitat_preferences", [])


def get_species_nutrition_needs(species_id: str, season: str) -> dict:
    """Get nutritional needs (sodium, Ca:P, trace) for species+season.
    Compatible v3.0.0 structure.
    """
    k = _load_knowledge()
    sp = get_species_data(species_id)
    if not sp:
        return {}
    mapped_id = sp["id"]
    season_map = {
        "printemps": "spring", "spring": "spring",
        "ete": "summer", "summer": "summer",
        "automne": "fall", "fall": "fall",
        "hiver": "winter", "winter": "winter",
    }
    season_en = season_map.get(season.lower(), "fall")
    sodium = k["nutrition"]["sodium"]
    sodium_need = sodium["data"].get(mapped_id, {}).get(season_en, 0)
    ca_p = k["nutrition"]["calcium_phosphorus"]
    trace = k["nutrition"]["trace_elements"]

    # v3.0.0: calcium_phosphorus is per-species dict
    if "data" in ca_p:
        ca_p_data = ca_p["data"].get(mapped_id, {})
    else:
        ca_p_data = ca_p

    # Build trace elements response
    trace_result = {}
    for el, data in trace.items():
        trace_result[el] = {
            "optimal_range": data.get("optimal", data.get("optimal_range")),
            "unit": data.get("unit", "ppm"),
        }

    return {
        "sodium": {
            "value": sodium_need,
            "unit": sodium["unit"],
            "source_ids": sodium.get("source_ids", []),
        },
        "calcium_phosphorus": {
            "optimal_ratio": ca_p_data.get("optimal_ratio", ca_p.get("optimal_ratio", "N/A")),
            "source_ids": ca_p_data.get("source_ids", ca_p.get("source_ids", [])),
        },
        "trace_elements": trace_result,
    }


# ==============================================
# HABITAT LOOKUP
# ==============================================

def get_habitat_data(habitat_id: str) -> Optional[dict]:
    """Get habitat data by id. Compatible v3.0.0 (dict) and v2.0.0 (list)."""
    k = _load_knowledge()
    habitats = k["habitats"]
    if isinstance(habitats, dict):
        return habitats.get(habitat_id)
    for h in habitats:
        if h["id"] == habitat_id:
            return h
    return None


def get_all_habitats() -> list:
    """Get all habitats."""
    habitats = _load_knowledge()["habitats"]
    if isinstance(habitats, dict):
        return list(habitats.values())
    return habitats


# ==============================================
# SOIL LOOKUP
# ==============================================

def get_soil_data(soil_id: str) -> Optional[dict]:
    """Get soil data by id. Compatible v3.0.0 (dict) and v2.0.0 (list)."""
    k = _load_knowledge()
    soils = k["soils"]
    if isinstance(soils, dict):
        return soils.get(soil_id)
    for s in soils:
        if s["id"] == soil_id:
            return s
    return None


def get_all_soils() -> list:
    """Get all soils."""
    soils = _load_knowledge()["soils"]
    if isinstance(soils, dict):
        return list(soils.values())
    return soils


# ==============================================
# NUTRITION LOOKUP
# ==============================================

def get_nutrition_data() -> dict:
    """Get full nutrition data block."""
    return _load_knowledge()["nutrition"]


# ==============================================
# CORRIDORS LOOKUP
# ==============================================

def get_corridors_for_species(species_id: str) -> list:
    """Get corridor models applicable to a species."""
    k = _load_knowledge()
    sp = get_species_data(species_id)
    if not sp:
        return []
    mapped_id = sp["id"]
    return [
        m for m in k["corridors"]["models"]
        if mapped_id in m.get("species", [])
    ]


# ==============================================
# SOURCES & EVIDENCE
# ==============================================

def get_sources_for_ids(source_ids: list) -> list:
    """Get full source objects for a list of source_ids."""
    k = _load_knowledge()
    source_map = {s["id"]: s for s in k["sources"]}
    return [source_map[sid] for sid in source_ids if sid in source_map]


def get_evidence_level(level_code: str) -> Optional[dict]:
    """Get evidence level definition by code (E1-E5)."""
    k = _load_knowledge()
    return k["evidence_levels"].get(level_code)


def get_all_sources() -> list:
    """Get all registered sources."""
    return _load_knowledge()["sources"]


# ==============================================
# META
# ==============================================

def get_knowledge_meta() -> dict:
    """Get knowledge.json metadata for API responses."""
    k = _load_knowledge()
    cert = k.get("_certification", {})
    species_data = k.get("species", {})
    species_count = len(species_data) if isinstance(species_data, dict) else len(species_data)
    habitats_data = k.get("habitats", {})
    habitats_count = len(habitats_data) if isinstance(habitats_data, dict) else len(habitats_data)
    soils_data = k.get("soils", {})
    soils_count = len(soils_data) if isinstance(soils_data, dict) else len(soils_data)
    return {
        "version": k.get("version"),
        "protocol": k.get("protocol"),
        "total_sources": len(k.get("sources", [])),
        "total_species": species_count,
        "total_habitats": habitats_count,
        "total_soils": soils_count,
        "evidence_coverage": cert.get("evidence_coverage", "N/A"),
    }
