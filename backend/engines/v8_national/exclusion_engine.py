"""
EXCLUSION-ENGINE-V8 — Moteur centralise d'exclusion BCE-4X
=============================================================
Referentiel UNIQUE pour toutes les decisions d'exclusion.
Remplace tous les filtres locaux (UrbanMask legacy, BCE-4X parcellaire).

Entrees: lat, lon, biome, habitat_score, urban_flag, road_density,
         building_density, legal_zone_flag, altitude, slope,
         water_type, contamination_index, species
Sorties: decision (INCLUDED/EXCLUDED), reason, severity (HARD/SOFT)

Integrations: SPATIAL-V8, ZONES-V8, SCORE-V8, VISION-IA-V8
"""
import math
import logging
from typing import Optional
from fastapi import APIRouter, Query

from .referentials import detect_biome, BIOMES

logger = logging.getLogger("bionic.exclusion_engine_v8")
router = APIRouter(prefix="/api/v8/exclusion", tags=["V8 Exclusion Engine"])


# ═══════════════════════════════════════════════════════
# REFERENTIELS D'EXCLUSION — CANADA-WIDE
# ═══════════════════════════════════════════════════════

# 20 villes majeures + agglomerations (polygones simplifies)
URBAN_ZONES = [
    # (lat_min, lat_max, lon_min, lon_max, name, population_tier)
    (45.40, 45.62, -73.98, -73.47, "Montreal", "TIER1"),
    (43.58, 43.80, -79.65, -79.20, "Toronto", "TIER1"),
    (49.20, 49.35, -123.25, -123.00, "Vancouver", "TIER1"),
    (45.30, 45.50, -75.85, -75.58, "Ottawa-Gatineau", "TIER1"),
    (51.00, 51.12, -114.22, -113.92, "Calgary", "TIER1"),
    (53.45, 53.62, -113.62, -113.32, "Edmonton", "TIER1"),
    (49.82, 49.95, -97.25, -97.00, "Winnipeg", "TIER1"),
    (46.76, 46.88, -71.35, -71.12, "Quebec-City", "TIER2"),
    (44.60, 44.72, -63.66, -63.48, "Halifax", "TIER2"),
    (43.80, 43.92, -79.60, -79.40, "Mississauga", "TIER2"),
    (48.40, 48.50, -89.32, -89.14, "Thunder-Bay", "TIER3"),
    (46.46, 46.56, -81.02, -80.88, "Sudbury", "TIER3"),
    (46.06, 46.14, -64.85, -64.68, "Moncton", "TIER3"),
    (46.07, 46.13, -66.70, -66.60, "Fredericton", "TIER3"),
    (46.22, 46.28, -63.16, -63.08, "Charlottetown", "TIER3"),
    (47.50, 47.60, -52.80, -52.65, "St-Johns", "TIER3"),
    (52.10, 52.20, -106.75, -106.55, "Saskatoon", "TIER3"),
    (50.42, 50.48, -104.65, -104.55, "Regina", "TIER3"),
    (45.50, 45.60, -73.62, -73.48, "Laval", "TIER2"),
    (45.52, 45.58, -73.48, -73.36, "Longueuil", "TIER2"),
    (46.78, 46.88, -71.28, -71.16, "Levis", "TIER3"),
    (48.42, 48.46, -71.08, -71.02, "Saguenay", "TIER3"),
    (45.38, 45.42, -71.92, -71.86, "Sherbrooke", "TIER3"),
    (46.33, 46.37, -72.58, -72.52, "Trois-Rivieres", "TIER3"),
]

# Corridors urbains denses (axes inter-villes)
URBAN_CORRIDORS = [
    (45.0, 46.0, -74.5, -71.0, "Corridor_QC-MTL-QC", 0.25),
    (43.5, 44.5, -80.0, -79.0, "Corridor_GTA", 0.30),
    (49.0, 49.3, -123.5, -122.5, "Corridor_Metro_Vancouver", 0.30),
    (43.0, 43.4, -80.5, -79.8, "Corridor_Hamilton-KW", 0.20),
    (45.3, 45.5, -76.0, -75.5, "Corridor_Ottawa-Ouest", 0.15),
]

# Zones legales interdites (reserves, parcs nationaux stricts)
LEGAL_EXCLUSIONS = [
    (48.3, 48.7, -65.0, -64.0, "Parc_Forillon", "HARD"),
    (47.5, 47.9, -70.5, -70.0, "Parc_Grands-Jardins", "HARD"),
    (46.2, 46.5, -74.5, -74.0, "Parc_Mont-Tremblant", "SOFT"),
    (47.8, 48.2, -64.5, -63.5, "Parc_Kouchibouguac", "HARD"),
    (51.5, 52.0, -117.0, -116.0, "Parc_Jasper", "HARD"),
    (51.0, 51.5, -116.5, -115.5, "Parc_Banff", "HARD"),
    (48.8, 49.2, -125.5, -125.0, "Parc_Pacific_Rim", "HARD"),
]

# Seuils
BUFFER_KM_TIER1 = 3.0
BUFFER_KM_TIER2 = 2.0
BUFFER_KM_TIER3 = 1.5
ALTITUDE_MAX = 2500
LATITUDE_ARCTIC_HARD = 72
LATITUDE_SUBARCTIC_SOFT = 62
ROAD_DENSITY_HIGH = 0.7
BUILDING_DENSITY_HIGH = 0.5


def evaluate_exclusion(
    lat: float, lon: float,
    species: str = "cerf",
    altitude: Optional[float] = None,
    slope: Optional[float] = None,
    road_density: Optional[float] = None,
    building_density: Optional[float] = None,
    water_type: Optional[str] = None,
    contamination_index: Optional[float] = None,
    legal_check: bool = True,
) -> dict:
    """Moteur centralise d'exclusion BCE-4X V8.
    
    Returns:
        {
            "decision": "INCLUDED" | "EXCLUDED",
            "reasons": [...],
            "severity": "HARD" | "SOFT" | "NONE",
            "habitat_score": 0-100,
            "exclusion_flags": {...},
            "engine": "EXCLUSION-ENGINE-V8"
        }
    """
    reasons = []
    flags = {
        "urban": False, "urban_buffer": False, "urban_corridor": False,
        "legal": False, "arctic": False, "altitude": False,
        "water_deep": False, "contamination": False, "road_high": False,
        "building_high": False, "slope_extreme": False,
    }
    habitat = 100
    severity = "NONE"

    # ────────── 1. EXCLUSION URBAINE (polygones) ──────────
    for (lat_min, lat_max, lon_min, lon_max, name, tier) in URBAN_ZONES:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            reasons.append(f"URBAN:{name}")
            flags["urban"] = True
            return {
                "decision": "EXCLUDED",
                "reasons": reasons,
                "severity": "HARD",
                "habitat_score": 0,
                "exclusion_flags": flags,
                "type": "urban",
                "engine": "EXCLUSION-ENGINE-V8",
            }

    # ────────── 2. BUFFER URBAIN (rayon) ──────────
    for (lat_min, lat_max, lon_min, lon_max, name, tier) in URBAN_ZONES:
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2
        dist_km = math.sqrt((lat - center_lat)**2 + (lon - center_lon)**2) * 111
        buffer = BUFFER_KM_TIER1 if tier == "TIER1" else BUFFER_KM_TIER2 if tier == "TIER2" else BUFFER_KM_TIER3
        if dist_km < buffer:
            reasons.append(f"URBAN_BUFFER:{name}({dist_km:.1f}km)")
            flags["urban_buffer"] = True
            habitat = max(0, habitat - 40)

    # ────────── 3. CORRIDORS URBAINS ──────────
    for (lat_min, lat_max, lon_min, lon_max, name, penalty) in URBAN_CORRIDORS:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            reasons.append(f"CORRIDOR:{name}")
            flags["urban_corridor"] = True
            habitat = max(0, habitat - int(penalty * 100))

    # ────────── 4. ZONES LEGALES INTERDITES ──────────
    if legal_check:
        for (lat_min, lat_max, lon_min, lon_max, name, sev) in LEGAL_EXCLUSIONS:
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                reasons.append(f"LEGAL:{name}")
                flags["legal"] = True
                if sev == "HARD":
                    return {
                        "decision": "EXCLUDED",
                        "reasons": reasons,
                        "severity": "HARD",
                        "habitat_score": 0,
                        "exclusion_flags": flags,
                        "type": "legal",
                        "engine": "EXCLUSION-ENGINE-V8",
                    }
                else:
                    habitat = max(0, habitat - 50)
                    severity = "SOFT"

    # ────────── 5. ARCTIQUE / HORS BIOME ──────────
    if lat > LATITUDE_ARCTIC_HARD:
        reasons.append("HORS_BIOME:Arctique_extreme")
        flags["arctic"] = True
        return {
            "decision": "EXCLUDED",
            "reasons": reasons,
            "severity": "HARD",
            "habitat_score": 0,
            "exclusion_flags": flags,
            "type": "arctic",
            "engine": "EXCLUSION-ENGINE-V8",
        }
    if lat > LATITUDE_SUBARCTIC_SOFT and lon > -100:
        reasons.append("BIOME_LIMITE:Toundra_subarctique")
        habitat = max(0, habitat - 50)

    # ────────── 6. ALTITUDE EXTREME ──────────
    if altitude is not None and altitude > ALTITUDE_MAX:
        reasons.append(f"ALTITUDE:{altitude}m>{ALTITUDE_MAX}m")
        flags["altitude"] = True
        habitat = max(0, habitat - 60)

    # ────────── 7. PENTE EXTREME ──────────
    if slope is not None and slope > 45:
        reasons.append(f"PENTE_EXTREME:{slope}deg")
        flags["slope_extreme"] = True
        habitat = max(0, habitat - 30)

    # ────────── 8. EAU PROFONDE ──────────
    if water_type in ("deep_lake", "ocean", "river_major"):
        reasons.append(f"WATER_DEEP:{water_type}")
        flags["water_deep"] = True
        return {
            "decision": "EXCLUDED",
            "reasons": reasons,
            "severity": "HARD",
            "habitat_score": 0,
            "exclusion_flags": flags,
            "type": "water",
            "engine": "EXCLUSION-ENGINE-V8",
        }

    # ────────── 9. CONTAMINATION ──────────
    if contamination_index is not None and contamination_index > 0.7:
        reasons.append(f"CONTAMINATION:{contamination_index:.2f}")
        flags["contamination"] = True
        habitat = max(0, habitat - 40)

    # ────────── 10. DENSITE ROUTIERE ──────────
    if road_density is not None and road_density > ROAD_DENSITY_HIGH:
        reasons.append(f"ROAD_DENSITY:{road_density:.2f}")
        flags["road_high"] = True
        habitat = max(0, habitat - 25)

    # ────────── 11. DENSITE BATIMENTS ──────────
    if building_density is not None and building_density > BUILDING_DENSITY_HIGH:
        reasons.append(f"BUILDING_DENSITY:{building_density:.2f}")
        flags["building_high"] = True
        habitat = max(0, habitat - 35)

    # ────────── DECISION FINALE ──────────
    excluded = habitat < 15
    if excluded and not reasons:
        reasons.append("HABITAT_INSUFFISANT")

    if excluded:
        severity = "HARD" if habitat == 0 else "SOFT"

    return {
        "decision": "EXCLUDED" if excluded else "INCLUDED",
        "reasons": reasons,
        "severity": severity,
        "habitat_score": max(0, habitat),
        "exclusion_flags": flags,
        "type": "excluded" if excluded else "valid",
        "engine": "EXCLUSION-ENGINE-V8",
    }


# ═══════════════════════════════════════════════════════
# ENDPOINT API
# ═══════════════════════════════════════════════════════

@router.get("/decision")
async def exclusion_decision(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    altitude: Optional[float] = Query(None),
    slope: Optional[float] = Query(None),
    road_density: Optional[float] = Query(None),
    building_density: Optional[float] = Query(None),
    water_type: Optional[str] = Query(None),
    contamination_index: Optional[float] = Query(None),
):
    """Decision d'exclusion centralisee BCE-4X V8."""
    from modules.canada_v72.data import detect_province
    province = detect_province(lat, lon)
    biome = detect_biome(lat, lon, province)

    result = evaluate_exclusion(
        lat, lon, species,
        altitude=altitude, slope=slope,
        road_density=road_density, building_density=building_density,
        water_type=water_type, contamination_index=contamination_index,
    )

    result["context"] = {
        "province": province,
        "biome": biome,
        "biome_name": BIOMES.get(biome, {}).get("name", biome),
        "location": {"lat": lat, "lon": lon},
    }
    result["dataVersion"] = "V8"

    return result


@router.get("/status")
async def exclusion_status():
    """Statut EXCLUSION-ENGINE-V8."""
    return {
        "engine": "EXCLUSION-ENGINE-V8",
        "version": "8.0.0",
        "status": "OPERATIONNEL",
        "referentials": {
            "urban_zones": len(URBAN_ZONES),
            "urban_corridors": len(URBAN_CORRIDORS),
            "legal_exclusions": len(LEGAL_EXCLUSIONS),
        },
        "criteria_count": 11,
        "criteria": [
            "urban_polygon", "urban_buffer", "urban_corridor",
            "legal_zone", "arctic", "altitude", "slope_extreme",
            "water_deep", "contamination", "road_density", "building_density",
        ],
        "severity_levels": ["HARD", "SOFT", "NONE"],
        "dataVersion": "V8",
    }
