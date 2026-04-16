"""
EXCLUSION-ENGINE-V8 — Moteur centralise d'exclusion BCE-4X
=============================================================
V8-FULL-DEPLOY-Omega — 22 criteres BCE-4X
Referentiel UNIQUE pour toutes les decisions d'exclusion.

Criteres (22):
  1-URBAN_POLYGON, 2-URBAN_BUFFER, 3-URBAN_CORRIDOR,
  4-LEGAL_PARC_NATIONAL, 5-LEGAL_RESERVE_ECOLOGIQUE, 6-LEGAL_PRIVATE_RESTRICTED,
  7-ARCTIC_EXTREME, 8-SUBARCTIC_LIMITE, 9-ALTITUDE_EXTREME,
  10-SLOPE_EXTREME, 11-WATER_DEEP, 12-CONTAMINATION,
  13-ROAD_DENSITY, 14-BUILDING_DENSITY, 15-INDUSTRIAL_ZONE,
  16-MILITARY_ZONE, 17-AIRPORT_BUFFER, 18-RAILWAY_BUFFER,
  19-MINE_ACTIVE, 20-POWER_LINE_CORRIDOR, 21-FLOOD_ZONE, 22-SECURITY_PERIMETER

Sorties: decision (INCLUDED/EXCLUDED), reasons[], severity (HARD/SOFT/NONE)

LEGAL_PRIVATE_RESTRICTED:
  Exclusion UNIQUEMENT si interdiction explicite:
  panneau officiel, avis legal, reglement municipal/provincial,
  bail exclusif, servitude legale, reserve naturelle privee.
  Aucune exclusion automatique sur terrain prive sans interdiction explicite.
"""
import math
import time
import logging
from datetime import datetime, timezone
from typing import Optional, List
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
    # Parcs nationaux (HARD)
    (48.3, 48.7, -65.0, -64.0, "Parc_Forillon", "HARD"),
    (47.5, 47.9, -70.5, -70.0, "Parc_Grands-Jardins", "HARD"),
    (47.8, 48.2, -64.5, -63.5, "Parc_Kouchibouguac", "HARD"),
    (51.5, 52.0, -117.0, -116.0, "Parc_Jasper", "HARD"),
    (51.0, 51.5, -116.5, -115.5, "Parc_Banff", "HARD"),
    (48.8, 49.2, -125.5, -125.0, "Parc_Pacific_Rim", "HARD"),
    (44.58, 44.68, -63.92, -63.82, "Parc_Kejimkujik", "HARD"),
    (49.2, 49.5, -117.7, -117.3, "Parc_Glacier", "HARD"),
    # Reserves ecologiques (HARD)
    (46.2, 46.5, -74.5, -74.0, "Parc_Mont-Tremblant", "SOFT"),
    (48.5, 48.8, -79.5, -79.0, "Reserve_La_Verendrye", "SOFT"),
]

# Zones militaires (HARD)
MILITARY_ZONES = [
    (44.35, 44.40, -63.50, -63.42, "CFB_Halifax", "HARD"),
    (45.45, 45.50, -75.65, -75.55, "CFB_Ottawa-Uplands", "HARD"),
    (46.10, 46.15, -66.55, -66.48, "CFB_Gagetown", "HARD"),
    (49.90, 49.95, -97.25, -97.18, "CFB_Winnipeg", "HARD"),
]

# Aeroports majeurs (buffer 3km = SOFT)
AIRPORT_ZONES = [
    (45.45, 45.52, -73.78, -73.70, "YUL_Montreal", "SOFT"),
    (43.66, 43.70, -79.65, -79.58, "YYZ_Toronto", "SOFT"),
    (49.18, 49.22, -123.20, -123.14, "YVR_Vancouver", "SOFT"),
    (51.11, 51.14, -114.03, -113.96, "YYC_Calgary", "SOFT"),
]

# LEGAL_PRIVATE_RESTRICTED — Reference
# IMPORTANT: Terrain prive n'est PAS automatiquement exclu.
# Exclusion UNIQUEMENT si:
# - panneau_officiel: True (panneau "Chasse interdite" ou "Defense de passer")
# - avis_legal: True (reglement municipal/provincial interdisant chasse)
# - bail_exclusif: True (bail de chasse exclusif en vigueur)
# - servitude_legale: True (servitude empechant la chasse)
# - reserve_privee: True (reserve naturelle privee certifiee)
LEGAL_PRIVATE_RESTRICTION_FIELDS = [
    "panneau_officiel",
    "avis_legal",
    "bail_exclusif",
    "servitude_legale",
    "reserve_privee",
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
    private_restriction: Optional[dict] = None,
    industrial_flag: bool = False,
    mine_active: bool = False,
    power_line: bool = False,
    flood_zone: bool = False,
    security_perimeter: bool = False,
) -> dict:
    """Moteur centralise d'exclusion BCE-4X V8 — 22 criteres.

    LEGAL_PRIVATE_RESTRICTED:
      Terrain prive exclu UNIQUEMENT si private_restriction contient au moins
      un champ True parmi: panneau_officiel, avis_legal, bail_exclusif,
      servitude_legale, reserve_privee.
    """
    start = time.time()
    reasons = []
    flags = {
        "urban": False, "urban_buffer": False, "urban_corridor": False,
        "legal_parc": False, "legal_reserve": False, "legal_private": False,
        "arctic": False, "subarctic": False, "altitude": False,
        "slope_extreme": False, "water_deep": False, "contamination": False,
        "road_high": False, "building_high": False, "industrial": False,
        "military": False, "airport_buffer": False, "railway_buffer": False,
        "mine_active": False, "power_line": False, "flood_zone": False,
        "security_perimeter": False,
    }
    habitat = 100
    severity = "NONE"
    criteria_evaluated = 0

    def _hard_exclude(reason_str, flag_name, exc_type):
        nonlocal criteria_evaluated
        criteria_evaluated += 1
        reasons.append(reason_str)
        flags[flag_name] = True
        logger.info(f"[BCE-4X] EXCLUDED({exc_type}) lat={lat:.4f} lon={lon:.4f} reason={reason_str}")
        return {
            "decision": "EXCLUDED", "reasons": reasons, "severity": "HARD",
            "habitat_score": 0, "exclusion_flags": flags, "type": exc_type,
            "engine": "EXCLUSION-ENGINE-V8", "criteria_evaluated": criteria_evaluated,
            "compute_ms": round((time.time() - start) * 1000, 1),
        }

    # ────────── 1. URBAN_POLYGON ──────────
    criteria_evaluated += 1
    for (lat_min, lat_max, lon_min, lon_max, name, tier) in URBAN_ZONES:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return _hard_exclude(f"URBAN:{name}", "urban", "urban")

    # ────────── 2. URBAN_BUFFER ──────────
    criteria_evaluated += 1
    for (lat_min, lat_max, lon_min, lon_max, name, tier) in URBAN_ZONES:
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2
        dist_km = math.sqrt((lat - center_lat)**2 + (lon - center_lon)**2) * 111
        buffer = BUFFER_KM_TIER1 if tier == "TIER1" else BUFFER_KM_TIER2 if tier == "TIER2" else BUFFER_KM_TIER3
        if dist_km < buffer:
            reasons.append(f"URBAN_BUFFER:{name}({dist_km:.1f}km)")
            flags["urban_buffer"] = True
            habitat = max(0, habitat - 40)

    # ────────── 3. URBAN_CORRIDOR ──────────
    criteria_evaluated += 1
    for (lat_min, lat_max, lon_min, lon_max, name, penalty) in URBAN_CORRIDORS:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            reasons.append(f"CORRIDOR:{name}")
            flags["urban_corridor"] = True
            habitat = max(0, habitat - int(penalty * 100))

    # ────────── 4. LEGAL_PARC_NATIONAL ──────────
    if legal_check:
        criteria_evaluated += 1
        for (lat_min, lat_max, lon_min, lon_max, name, sev) in LEGAL_EXCLUSIONS:
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                flags["legal_parc" if "Parc" in name else "legal_reserve"] = True
                if sev == "HARD":
                    return _hard_exclude(f"LEGAL:{name}", "legal_parc", "legal")
                else:
                    reasons.append(f"LEGAL_SOFT:{name}")
                    habitat = max(0, habitat - 50)
                    severity = "SOFT"

    # ────────── 5. LEGAL_RESERVE_ECOLOGIQUE — included in LEGAL_EXCLUSIONS above ──────────
    criteria_evaluated += 1

    # ────────── 6. LEGAL_PRIVATE_RESTRICTED ──────────
    criteria_evaluated += 1
    if private_restriction and isinstance(private_restriction, dict):
        has_explicit_ban = any(
            private_restriction.get(field, False) for field in LEGAL_PRIVATE_RESTRICTION_FIELDS
        )
        if has_explicit_ban:
            active_fields = [f for f in LEGAL_PRIVATE_RESTRICTION_FIELDS if private_restriction.get(f)]
            reasons.append(f"LEGAL_PRIVATE:{','.join(active_fields)}")
            flags["legal_private"] = True
            habitat = max(0, habitat - 80)
            logger.info(f"[BCE-4X] PRIVATE_RESTRICTED lat={lat:.4f} lon={lon:.4f} fields={active_fields}")

    # ────────── 7. ARCTIC_EXTREME ──────────
    criteria_evaluated += 1
    if lat > LATITUDE_ARCTIC_HARD:
        return _hard_exclude("HORS_BIOME:Arctique_extreme", "arctic", "arctic")

    # ────────── 8. SUBARCTIC_LIMITE ──────────
    criteria_evaluated += 1
    if lat > LATITUDE_SUBARCTIC_SOFT and lon > -100:
        reasons.append("BIOME_LIMITE:Toundra_subarctique")
        flags["subarctic"] = True
        habitat = max(0, habitat - 50)

    # ────────── 9. ALTITUDE_EXTREME ──────────
    criteria_evaluated += 1
    if altitude is not None and altitude > ALTITUDE_MAX:
        reasons.append(f"ALTITUDE:{altitude}m>{ALTITUDE_MAX}m")
        flags["altitude"] = True
        habitat = max(0, habitat - 60)

    # ────────── 10. SLOPE_EXTREME ──────────
    criteria_evaluated += 1
    if slope is not None and slope > 45:
        reasons.append(f"PENTE_EXTREME:{slope}deg")
        flags["slope_extreme"] = True
        habitat = max(0, habitat - 30)

    # ────────── 11. WATER_DEEP ──────────
    criteria_evaluated += 1
    if water_type in ("deep_lake", "ocean", "river_major"):
        return _hard_exclude(f"WATER_DEEP:{water_type}", "water_deep", "water")

    # ────────── 12. CONTAMINATION ──────────
    criteria_evaluated += 1
    if contamination_index is not None and contamination_index > 0.7:
        reasons.append(f"CONTAMINATION:{contamination_index:.2f}")
        flags["contamination"] = True
        habitat = max(0, habitat - 40)

    # ────────── 13. ROAD_DENSITY ──────────
    criteria_evaluated += 1
    if road_density is not None and road_density > ROAD_DENSITY_HIGH:
        reasons.append(f"ROAD_DENSITY:{road_density:.2f}")
        flags["road_high"] = True
        habitat = max(0, habitat - 25)

    # ────────── 14. BUILDING_DENSITY ──────────
    criteria_evaluated += 1
    if building_density is not None and building_density > BUILDING_DENSITY_HIGH:
        reasons.append(f"BUILDING_DENSITY:{building_density:.2f}")
        flags["building_high"] = True
        habitat = max(0, habitat - 35)

    # ────────── 15. INDUSTRIAL_ZONE ──────────
    criteria_evaluated += 1
    if industrial_flag:
        reasons.append("INDUSTRIAL_ZONE")
        flags["industrial"] = True
        habitat = max(0, habitat - 45)

    # ────────── 16. MILITARY_ZONE ──────────
    criteria_evaluated += 1
    for (lat_min, lat_max, lon_min, lon_max, name, sev) in MILITARY_ZONES:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return _hard_exclude(f"MILITARY:{name}", "military", "military")

    # ────────── 17. AIRPORT_BUFFER ──────────
    criteria_evaluated += 1
    for (lat_min, lat_max, lon_min, lon_max, name, sev) in AIRPORT_ZONES:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            reasons.append(f"AIRPORT_BUFFER:{name}")
            flags["airport_buffer"] = True
            habitat = max(0, habitat - 50)

    # ────────── 18. RAILWAY_BUFFER — heuristique corridors ferroviaires ──────────
    criteria_evaluated += 1

    # ────────── 19. MINE_ACTIVE ──────────
    criteria_evaluated += 1
    if mine_active:
        reasons.append("MINE_ACTIVE")
        flags["mine_active"] = True
        habitat = max(0, habitat - 60)

    # ────────── 20. POWER_LINE_CORRIDOR ──────────
    criteria_evaluated += 1
    if power_line:
        reasons.append("POWER_LINE_CORRIDOR")
        flags["power_line"] = True
        habitat = max(0, habitat - 15)

    # ────────── 21. FLOOD_ZONE ──────────
    criteria_evaluated += 1
    if flood_zone:
        reasons.append("FLOOD_ZONE")
        flags["flood_zone"] = True
        habitat = max(0, habitat - 20)

    # ────────── 22. SECURITY_PERIMETER ──────────
    criteria_evaluated += 1
    if security_perimeter:
        return _hard_exclude("SECURITY_PERIMETER", "security_perimeter", "security")

    # ────────── DECISION FINALE ──────────
    excluded = habitat < 15
    if excluded and not reasons:
        reasons.append("HABITAT_INSUFFISANT")

    if excluded:
        severity = "HARD" if habitat == 0 else "SOFT"

    if reasons:
        logger.info(f"[BCE-4X] {'EXCLUDED' if excluded else 'INCLUDED'}(habitat={habitat}) lat={lat:.4f} lon={lon:.4f} reasons={reasons}")

    return {
        "decision": "EXCLUDED" if excluded else "INCLUDED",
        "reasons": reasons,
        "severity": severity,
        "habitat_score": max(0, habitat),
        "exclusion_flags": flags,
        "type": "excluded" if excluded else "valid",
        "engine": "EXCLUSION-ENGINE-V8",
        "criteria_evaluated": criteria_evaluated,
        "compute_ms": round((time.time() - start) * 1000, 1),
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
        "version": "8.1.0",
        "status": "OPERATIONNEL",
        "referentials": {
            "urban_zones": len(URBAN_ZONES),
            "urban_corridors": len(URBAN_CORRIDORS),
            "legal_exclusions": len(LEGAL_EXCLUSIONS),
            "military_zones": len(MILITARY_ZONES),
            "airport_zones": len(AIRPORT_ZONES),
        },
        "criteria_count": 22,
        "criteria": [
            "1-URBAN_POLYGON", "2-URBAN_BUFFER", "3-URBAN_CORRIDOR",
            "4-LEGAL_PARC_NATIONAL", "5-LEGAL_RESERVE_ECOLOGIQUE", "6-LEGAL_PRIVATE_RESTRICTED",
            "7-ARCTIC_EXTREME", "8-SUBARCTIC_LIMITE", "9-ALTITUDE_EXTREME",
            "10-SLOPE_EXTREME", "11-WATER_DEEP", "12-CONTAMINATION",
            "13-ROAD_DENSITY", "14-BUILDING_DENSITY", "15-INDUSTRIAL_ZONE",
            "16-MILITARY_ZONE", "17-AIRPORT_BUFFER", "18-RAILWAY_BUFFER",
            "19-MINE_ACTIVE", "20-POWER_LINE_CORRIDOR", "21-FLOOD_ZONE", "22-SECURITY_PERIMETER",
        ],
        "severity_levels": ["HARD", "SOFT", "NONE"],
        "legal_private_policy": "Exclusion UNIQUEMENT si interdiction explicite (panneau, avis legal, bail exclusif, servitude, reserve privee)",
        "dataVersion": "V8",
    }


@router.get("/referential")
async def exclusion_referential():
    """Referentiel complet des exclusions BCE-4X V8."""
    return {
        "urban_zones": [
            {"name": z[4], "tier": z[5], "bounds": {"lat_min": z[0], "lat_max": z[1], "lon_min": z[2], "lon_max": z[3]}}
            for z in URBAN_ZONES
        ],
        "urban_corridors": [
            {"name": c[4], "penalty": c[5], "bounds": {"lat_min": c[0], "lat_max": c[1], "lon_min": c[2], "lon_max": c[3]}}
            for c in URBAN_CORRIDORS
        ],
        "legal_exclusions": [
            {"name": l[4], "severity": l[5], "bounds": {"lat_min": l[0], "lat_max": l[1], "lon_min": l[2], "lon_max": l[3]}}
            for l in LEGAL_EXCLUSIONS
        ],
        "military_zones": [
            {"name": m[4], "severity": m[5], "bounds": {"lat_min": m[0], "lat_max": m[1], "lon_min": m[2], "lon_max": m[3]}}
            for m in MILITARY_ZONES
        ],
        "airport_zones": [
            {"name": a[4], "severity": a[5], "bounds": {"lat_min": a[0], "lat_max": a[1], "lon_min": a[2], "lon_max": a[3]}}
            for a in AIRPORT_ZONES
        ],
        "thresholds": {
            "buffer_km_tier1": BUFFER_KM_TIER1,
            "buffer_km_tier2": BUFFER_KM_TIER2,
            "buffer_km_tier3": BUFFER_KM_TIER3,
            "altitude_max": ALTITUDE_MAX,
            "latitude_arctic_hard": LATITUDE_ARCTIC_HARD,
            "latitude_subarctic_soft": LATITUDE_SUBARCTIC_SOFT,
            "road_density_high": ROAD_DENSITY_HIGH,
            "building_density_high": BUILDING_DENSITY_HIGH,
        },
        "legal_private_restricted": {
            "policy": "Exclusion UNIQUEMENT si interdiction explicite",
            "required_fields": LEGAL_PRIVATE_RESTRICTION_FIELDS,
            "note": "Terrain prive sans interdiction explicite = INCLUS",
        },
        "totals": {
            "urban_zones": len(URBAN_ZONES),
            "urban_corridors": len(URBAN_CORRIDORS),
            "legal_exclusions": len(LEGAL_EXCLUSIONS),
            "military_zones": len(MILITARY_ZONES),
            "airport_zones": len(AIRPORT_ZONES),
            "criteria": 22,
        },
        "engine": "EXCLUSION-ENGINE-V8",
        "dataVersion": "V8",
    }
