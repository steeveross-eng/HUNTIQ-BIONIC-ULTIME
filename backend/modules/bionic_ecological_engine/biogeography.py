"""
BIONIC Biogeography Filter — Filtrage Ecologique Global
STEEVE-MAX x2260-V2

Couche SYSTEMIQUE appliquee dans TOUT BIONIC pour empecher
toute incoherence ecologique, legale ou geographique.

Aucune espece ne doit apparaitre dans une region ou elle n'existe pas.

Usage:
    from .biogeography import filter_species_for_location, get_species_status

    # Filtre les especes pour Quebec
    available = filter_species_for_location(country="CA", province="QC")
    # -> ["orignal", "cerf_virginie", "ours_noir", "dindon_sauvage", "caribou"]

    # Verifie le statut d'une espece
    status = get_species_status("wapiti", "CA", "QC")
    # -> {"status": "absent", "huntable": false, ...}
"""
import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("bionic.biogeography")

_BIOGEO_DATA: Dict[str, Any] = {}

# Reverse geocoding approximatif (lat/lng -> province/state)
# Bornes simplifiees pour les principales provinces/etats
_GEO_BOUNDS = {
    # Canada
    ("CA", "QC"): {"lat_min": 45.0, "lat_max": 62.5, "lng_min": -80.0, "lng_max": -57.0},
    ("CA", "ON"): {"lat_min": 42.0, "lat_max": 56.9, "lng_min": -95.2, "lng_max": -74.3},
    ("CA", "NB"): {"lat_min": 44.6, "lat_max": 48.1, "lng_min": -69.1, "lng_max": -63.8},
    ("CA", "NS"): {"lat_min": 43.4, "lat_max": 47.1, "lng_min": -66.5, "lng_max": -59.7},
    ("CA", "MB"): {"lat_min": 49.0, "lat_max": 60.0, "lng_min": -102.0, "lng_max": -88.9},
    ("CA", "SK"): {"lat_min": 49.0, "lat_max": 60.0, "lng_min": -110.0, "lng_max": -101.4},
    ("CA", "AB"): {"lat_min": 49.0, "lat_max": 60.0, "lng_min": -120.0, "lng_max": -110.0},
    ("CA", "BC"): {"lat_min": 48.3, "lat_max": 60.0, "lng_min": -139.1, "lng_max": -114.0},
    ("CA", "YT"): {"lat_min": 60.0, "lat_max": 69.7, "lng_min": -141.0, "lng_max": -123.8},
    ("CA", "NT"): {"lat_min": 60.0, "lat_max": 78.8, "lng_min": -136.5, "lng_max": -102.0},
    ("CA", "NU"): {"lat_min": 51.7, "lat_max": 83.1, "lng_min": -120.7, "lng_max": -61.2},
    ("CA", "NL"): {"lat_min": 46.6, "lat_max": 60.4, "lng_min": -67.8, "lng_max": -52.6},
    ("CA", "PE"): {"lat_min": 45.9, "lat_max": 47.1, "lng_min": -64.5, "lng_max": -62.0},
    # US (principales regions de chasse)
    ("US", "ME"): {"lat_min": 43.1, "lat_max": 47.5, "lng_min": -71.1, "lng_max": -67.0},
    ("US", "NH"): {"lat_min": 42.7, "lat_max": 45.3, "lng_min": -72.6, "lng_max": -70.7},
    ("US", "VT"): {"lat_min": 42.7, "lat_max": 45.0, "lng_min": -73.4, "lng_max": -71.5},
    ("US", "NY"): {"lat_min": 40.5, "lat_max": 45.0, "lng_min": -79.8, "lng_max": -71.9},
    ("US", "PA"): {"lat_min": 39.7, "lat_max": 42.3, "lng_min": -80.5, "lng_max": -74.7},
    ("US", "MN"): {"lat_min": 43.5, "lat_max": 49.4, "lng_min": -97.2, "lng_max": -89.5},
    ("US", "WI"): {"lat_min": 42.5, "lat_max": 47.1, "lng_min": -92.9, "lng_max": -86.8},
    ("US", "MI"): {"lat_min": 41.7, "lat_max": 48.3, "lng_min": -90.4, "lng_max": -82.1},
    ("US", "MT"): {"lat_min": 44.4, "lat_max": 49.0, "lng_min": -116.1, "lng_max": -104.0},
    ("US", "WY"): {"lat_min": 41.0, "lat_max": 45.0, "lng_min": -111.1, "lng_max": -104.1},
    ("US", "CO"): {"lat_min": 37.0, "lat_max": 41.0, "lng_min": -109.1, "lng_max": -102.0},
    ("US", "ID"): {"lat_min": 42.0, "lat_max": 49.0, "lng_min": -117.2, "lng_max": -111.0},
    ("US", "UT"): {"lat_min": 37.0, "lat_max": 42.0, "lng_min": -114.1, "lng_max": -109.0},
    ("US", "WA"): {"lat_min": 45.5, "lat_max": 49.0, "lng_min": -124.8, "lng_max": -116.9},
    ("US", "OR"): {"lat_min": 42.0, "lat_max": 46.3, "lng_min": -124.6, "lng_max": -116.5},
    ("US", "AK"): {"lat_min": 51.2, "lat_max": 71.4, "lng_min": -179.2, "lng_max": -130.0},
    ("US", "SD"): {"lat_min": 42.5, "lat_max": 46.0, "lng_min": -104.1, "lng_max": -96.4},
    ("US", "ND"): {"lat_min": 45.9, "lat_max": 49.0, "lng_min": -104.1, "lng_max": -96.6},
    ("US", "NE"): {"lat_min": 40.0, "lat_max": 43.0, "lng_min": -104.1, "lng_max": -95.3},
    ("US", "NM"): {"lat_min": 31.3, "lat_max": 37.0, "lng_min": -109.1, "lng_max": -103.0},
    ("US", "AZ"): {"lat_min": 31.3, "lat_max": 37.0, "lng_min": -114.8, "lng_max": -109.0},
}

# Statuts consideres comme "present" (espece visible dans BIONIC)
PRESENT_STATUSES = {"present", "introduced"}
# Statuts consideres comme "absent" (espece invisible dans BIONIC)
ABSENT_STATUSES = {"absent", "disappeared"}


def _load_biogeography():
    """Load biogeography data from JSON file."""
    global _BIOGEO_DATA
    if _BIOGEO_DATA:
        return

    json_path = os.path.join(os.path.dirname(__file__), "bionic_species_biogeography.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            _BIOGEO_DATA = json.load(f)
        logger.info(f"Biogeography matrix loaded: {len(_BIOGEO_DATA) - 1} species")
    except FileNotFoundError:
        logger.error(f"Biogeography file not found: {json_path}")
        _BIOGEO_DATA = {"_metadata": {}}
    except json.JSONDecodeError as e:
        logger.error(f"Biogeography JSON parse error: {e}")
        _BIOGEO_DATA = {"_metadata": {}}


def resolve_location(lat: float, lng: float) -> Tuple[str, str]:
    """
    Resolve lat/lng to (country, province/state) using approximate bounds.
    Returns ("CA", "QC") or ("US", "MT") etc.
    Falls back to ("CA", "QC") if no match found.
    """
    best_match = None
    best_distance = float("inf")

    for (country, prov), bounds in _GEO_BOUNDS.items():
        if (bounds["lat_min"] <= lat <= bounds["lat_max"] and
                bounds["lng_min"] <= lng <= bounds["lng_max"]):
            center_lat = (bounds["lat_min"] + bounds["lat_max"]) / 2
            center_lng = (bounds["lng_min"] + bounds["lng_max"]) / 2
            dist = (lat - center_lat) ** 2 + (lng - center_lng) ** 2
            if dist < best_distance:
                best_distance = dist
                best_match = (country, prov)

    return best_match or ("CA", "QC")


def get_species_status(species_id: str, country: str, province: str) -> Dict[str, Any]:
    """
    Get the biogeographic status of a species in a specific jurisdiction.

    Returns:
        {"status": "present/absent/...", "abundance": "...", "huntable": bool, ...}
    """
    _load_biogeography()

    species_data = _BIOGEO_DATA.get(species_id, {})
    distribution = species_data.get("distribution", {})
    country_data = distribution.get(country, {})

    # Check specific province first
    prov_data = country_data.get(province, None)
    if prov_data:
        return prov_data

    # Check wildcard (e.g., "ALL_LOWER_48")
    if country == "US" and province != "AK":
        all_lower = country_data.get("ALL_LOWER_48", None)
        if all_lower:
            return all_lower

    # Default: absent
    return {
        "status": "absent",
        "abundance": "none",
        "huntable": False,
        "zones": "",
        "notes": "Aucune donnee biogeographique pour cette juridiction",
    }


def is_species_present(species_id: str, country: str, province: str) -> bool:
    """Check if a species is present (or introduced) in a jurisdiction."""
    status = get_species_status(species_id, country, province)
    return status.get("status", "absent") in PRESENT_STATUSES


def is_species_huntable(species_id: str, country: str, province: str) -> bool:
    """Check if a species is huntable in a jurisdiction."""
    status = get_species_status(species_id, country, province)
    return status.get("huntable", False)


def filter_species_for_location(
    country: str = "CA",
    province: str = "QC",
    only_huntable: bool = False,
) -> List[str]:
    """
    Filter species that are present in a specific jurisdiction.

    Args:
        country: "CA" or "US"
        province: Province/State code (e.g., "QC", "ON", "MT")
        only_huntable: If True, only return huntable species

    Returns:
        List of species IDs present in the jurisdiction
    """
    _load_biogeography()

    present_species = []
    for species_id in _BIOGEO_DATA:
        if species_id.startswith("_"):
            continue

        if is_species_present(species_id, country, province):
            if only_huntable and not is_species_huntable(species_id, country, province):
                continue
            present_species.append(species_id)

    return present_species


def filter_species_for_coordinates(
    lat: float,
    lng: float,
    only_huntable: bool = False,
) -> List[str]:
    """
    Filter species based on lat/lng coordinates.
    Resolves location first, then filters.
    """
    country, province = resolve_location(lat, lng)
    return filter_species_for_location(country, province, only_huntable)


def get_jurisdiction_info(lat: float, lng: float) -> Dict[str, Any]:
    """
    Get full jurisdiction info for a location.
    Returns country, province, available species, and huntable species.
    """
    country, province = resolve_location(lat, lng)
    all_present = filter_species_for_location(country, province, only_huntable=False)
    huntable = filter_species_for_location(country, province, only_huntable=True)

    species_details = []
    for sp_id in all_present:
        status = get_species_status(sp_id, country, province)
        species_data = _BIOGEO_DATA.get(sp_id, {})
        species_details.append({
            "id": sp_id,
            "name_fr": species_data.get("name_fr", sp_id),
            "status": status.get("status", "unknown"),
            "abundance": status.get("abundance", "unknown"),
            "huntable": status.get("huntable", False),
            "zones": status.get("zones", ""),
            "notes": status.get("notes", ""),
        })

    return {
        "country": country,
        "province": province,
        "total_species_present": len(all_present),
        "total_huntable": len(huntable),
        "species_present": all_present,
        "species_huntable": huntable,
        "species_details": species_details,
    }


logger.info("BIONIC Biogeography Filter loaded")
