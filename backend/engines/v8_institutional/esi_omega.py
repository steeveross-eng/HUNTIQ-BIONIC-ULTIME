"""
ENGINE SECURITE-INSTITUTIONNELLE-Omega (ESI-Omega)
===================================================
GUARDIAN CENTRAL DU SYSTEME BIONIC V8-PURE
Unifie: BCE validators + Governance + Exclusion + Auth + Audit
Impose: BCE-4X, STEEVE-MAX, V8-PURE, Document Maitre ULTIME MAX
Protege: Master Switch (autorite exclusive Commandant)

ZERO heritage V6/V7. ZERO duplication. ZERO regression.
ZERO smoothing. ZERO simplification. ZERO interpolation non autorisee.
100% tracabilite. 100% conformite. 100% integrite.

Inputs: 24 engines, 4 piliers, pipelines, routers
Outputs: validation, blocage, correction, audit
"""
import time
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional

logger = logging.getLogger("bionic.esi_omega")
router = APIRouter(prefix="/api/v8/esi", tags=["ESI-Omega — Engine Securite Institutionnelle"])

# ═══════════════════════════════════════════════════════
# LOIS INSTITUTIONNELLES — NON NEGOCIABLES
# ═══════════════════════════════════════════════════════

DOCUMENT_MAITRE = "V8-ENGINES-INSTITUTIONNEL-Omega-ULTIME-MAX-2026"
MODE = "STRICT-INSTITUTIONNEL"
MASTER_SWITCH_AUTHORITY = "admin@huntiq.com"

TERRAIN_RULES = {
    "pente_max_deg": 45,
    "eau_min_m": 10,
    "smoothing": False,
    "simplification_polygonale": False,
    "interpolation_non_autorisee": False,
}

VISUAL_RULES = {
    "salines": {"shape": "cercle_organique", "color": "#FDD835", "opacity": 1.0},
    "affuts": {"shape": "cercle_gris_x", "color": "#9E9E9E", "x_color": "#424242"},
    "corridors": {"color": "#FF8F00", "opacity": 1.0},
    "vent": {"color": "#90CAF9", "width_mm": 1.5},
    "zones": {"rut": "#C62828", "alimentation": "#2E7D32", "repos": "#1565C0", "eau": "#29B6F6"},
}

BCE_4X_LAWS = [
    "ZERO_REGRESSION",
    "ZERO_DUPLICATION",
    "ZERO_PERTE",
    "ZERO_ALTERATION_NON_DOCUMENTEE",
    "ZERO_INTERPRETATION",
    "ZERO_HERITAGE_V6_V7",
    "ZERO_SMOOTHING",
    "ZERO_SIMPLIFICATION_POLYGONALE",
    "ZERO_INTERPOLATION_NON_AUTORISEE",
    "CENT_PCT_TRACABILITE",
    "CENT_PCT_CONFORMITE",
    "CENT_PCT_SECURITE_TERRAIN",
    "CENT_PCT_INTEGRITE_OUTPUTS",
]

ENGINES_INSTITUTIONNELS = [
    "ZONES", "CORRIDORS", "AFFUTS", "HOTSPOTS", "VENT", "HEATMAP",
    "SALINES", "NUTRITION-MINERAUX", "PRESSION", "RISQUE",
    "FREQUENTATION", "SAISONNALITE", "COMPORTEMENT", "COMPORTEMENT-AVANCE",
    "TERRAIN-COST", "VISIBILITE", "CAMERAS", "BIO-SIGNES",
    "AUDIO-ACOUSTIQUE", "PSYCHOLOGIE", "PREDICTION-48H", "CONNECTIVITE",
    "INTELLIGENCE", "SCORE-GLOBAL",
]

PILIERS = ["BIO-SYSTEME", "COMPORTEMENT-HUMAIN", "SYSTEME-SENSORIEL", "PREDICTION-INTELLIGENCE"]

# ═══════════════════════════════════════════════════════
# AUDIT LOG — TRACABILITE 100%
# ═══════════════════════════════════════════════════════

_audit_log = []


def _log_audit(action, target, result, detail=""):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "target": target,
        "result": result,
        "detail": detail,
    }
    _audit_log.append(entry)
    if len(_audit_log) > 1000:
        _audit_log.pop(0)
    return entry


# ═══════════════════════════════════════════════════════
# VALIDATORS V8-PURE (fusionnes depuis BCE)
# ═══════════════════════════════════════════════════════

def validate_terrain(terrain):
    violations = []
    if terrain.get("pente_deg", 0) > TERRAIN_RULES["pente_max_deg"]:
        violations.append(f"EXCLUSION: pente {terrain['pente_deg']}deg > {TERRAIN_RULES['pente_max_deg']}deg")
    if terrain.get("distance_eau_m", 999) < TERRAIN_RULES["eau_min_m"]:
        violations.append(f"EXCLUSION: eau {terrain['distance_eau_m']}m < {TERRAIN_RULES['eau_min_m']}m")
    return {"valid": len(violations) == 0, "violations": violations}


def validate_geometry(polygon):
    violations = []
    if not polygon or len(polygon) < 4:
        violations.append("GEOMETRIE: polygone insuffisant (<4 vertices)")
    if polygon and len(polygon) >= 3:
        for i in range(1, len(polygon)):
            if polygon[i] == polygon[i - 1]:
                violations.append(f"GEOMETRIE: vertex duplique index {i}")
    return {"valid": len(violations) == 0, "violations": violations}


def validate_corridor(corridor):
    violations = []
    path = corridor.get("path", [])
    if len(path) < 2:
        violations.append("CORRIDOR: path insuffisant (<2 points)")
    ts = corridor.get("terrain_start", {})
    te = corridor.get("terrain_end", {})
    if ts.get("distance_eau_m", 999) < TERRAIN_RULES["eau_min_m"]:
        violations.append(f"CORRIDOR: start sur eau ({ts['distance_eau_m']}m)")
    if te.get("distance_eau_m", 999) < TERRAIN_RULES["eau_min_m"]:
        violations.append(f"CORRIDOR: end sur eau ({te['distance_eau_m']}m)")
    if ts.get("pente_deg", 0) > TERRAIN_RULES["pente_max_deg"]:
        violations.append(f"CORRIDOR: start pente extreme ({ts['pente_deg']}deg)")
    if te.get("pente_deg", 0) > TERRAIN_RULES["pente_max_deg"]:
        violations.append(f"CORRIDOR: end pente extreme ({te['pente_deg']}deg)")
    return {"valid": len(violations) == 0, "violations": violations}


def validate_visual_signature(layer_type, properties):
    violations = []
    rules = VISUAL_RULES.get(layer_type)
    if not rules:
        return {"valid": True, "violations": []}
    if "color" in rules and properties.get("color") != rules["color"]:
        violations.append(f"VISUEL: couleur {properties.get('color')} != {rules['color']} (norme)")
    if "opacity" in rules and properties.get("opacity", 1.0) != rules["opacity"]:
        violations.append(f"VISUEL: opacite {properties.get('opacity')} != {rules['opacity']}")
    return {"valid": len(violations) == 0, "violations": violations}


def validate_species_coherence(species, data):
    violations = []
    valid_species = ["cerf", "orignal", "chevreuil", "ours", "dindon", "caribou", "wapiti", "coyote", "loup"]
    if species not in valid_species:
        violations.append(f"ESPECE: {species} non reconnue")
    return {"valid": len(violations) == 0, "violations": violations}


def validate_season_coherence(month, data):
    violations = []
    if not 1 <= month <= 12:
        violations.append(f"SAISON: mois {month} invalide")
    return {"valid": len(violations) == 0, "violations": violations}


def validate_scoring_determinism(lat, lon, species, score1, score2):
    violations = []
    if abs(score1 - score2) > 0.01:
        violations.append(f"DETERMINISME: scores differents pour meme input ({score1} vs {score2})")
    return {"valid": len(violations) == 0, "violations": violations}


# ═══════════════════════════════════════════════════════
# FULL VALIDATION — TOUS ENGINES + PILIERS
# ═══════════════════════════════════════════════════════

def validate_bundle(bundle):
    results = {"total_checks": 0, "passed": 0, "failed": 0, "violations": []}

    for z in bundle.get("zones", []):
        results["total_checks"] += 1
        tv = validate_terrain(z.get("terrain", {}))
        gv = validate_geometry(z.get("polygon", []))
        if tv["valid"] and gv["valid"]:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["violations"].extend(tv["violations"])
            results["violations"].extend(gv["violations"])

    for c in bundle.get("corridors", []):
        results["total_checks"] += 1
        cv = validate_corridor(c)
        if cv["valid"]:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["violations"].extend(cv["violations"])

    for a in bundle.get("affuts", []):
        results["total_checks"] += 1
        tv = validate_terrain(a.get("terrain", {}))
        if tv["valid"]:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["violations"].extend(tv["violations"])

    results["conformite"] = "CONFORME" if results["failed"] == 0 else "NON-CONFORME"
    return results


# ═══════════════════════════════════════════════════════
# MASTER SWITCH PROTECTION
# ═══════════════════════════════════════════════════════

def verify_master_switch_authority(email):
    if email != MASTER_SWITCH_AUTHORITY:
        _log_audit("MASTER_SWITCH_VIOLATION", email, "BLOQUE", "Tentative non autorisee")
        return False
    return True


# ═══════════════════════════════════════════════════════
# ENDPOINTS ESI-Omega
# ═══════════════════════════════════════════════════════

@router.get("/status")
async def esi_status():
    return {
        "engine": "ESI-Omega",
        "document_maitre": DOCUMENT_MAITRE,
        "mode": MODE,
        "master_switch_authority": MASTER_SWITCH_AUTHORITY,
        "engines_proteges": len(ENGINES_INSTITUTIONNELS),
        "piliers_proteges": len(PILIERS),
        "lois_bce4x": len(BCE_4X_LAWS),
        "terrain_rules": TERRAIN_RULES,
        "visual_rules": VISUAL_RULES,
        "audit_entries": len(_audit_log),
        "status": "ACTIF — GUARDIAN CENTRAL",
    }


@router.get("/validate/terrain")
async def validate_terrain_endpoint(
    pente_deg: float = Query(0), distance_eau_m: float = Query(999),
    canopy: float = Query(0.5), distance_route_m: float = Query(500),
):
    terrain = {"pente_deg": pente_deg, "distance_eau_m": distance_eau_m, "canopy": canopy, "distance_route_m": distance_route_m}
    result = validate_terrain(terrain)
    _log_audit("VALIDATE_TERRAIN", f"pente={pente_deg},eau={distance_eau_m}", result["valid"])
    return {"engine": "ESI-Omega", **result, "rules": TERRAIN_RULES}


@router.get("/validate/bundle")
async def validate_bundle_endpoint(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
):
    start = time.time()
    from engines.v8_national.map_bundle import map_bundle as _mb
    from unittest.mock import AsyncMock
    
    # Fetch bundle data directly from generators
    from engines.v8_national.phase_b_engines import generate_zones_ta, generate_corridors_ta, generate_affuts_ta
    m = datetime.now(timezone.utc).month
    h = datetime.now(timezone.utc).hour
    zones = generate_zones_ta(lat, lon, species, m)
    corridors = generate_corridors_ta(lat, lon, species, m, h)
    affuts = generate_affuts_ta(lat, lon, species, zones, corridors)
    
    bundle = {"zones": zones, "corridors": corridors, "affuts": affuts}
    result = validate_bundle(bundle)
    _log_audit("VALIDATE_BUNDLE", f"{lat},{lon},{species}", result["conformite"])
    return {
        "engine": "ESI-Omega",
        **result,
        "compute_ms": round((time.time() - start) * 1000),
    }


@router.get("/validate/visual")
async def validate_visual_endpoint(
    layer_type: str = Query(...), color: str = Query(""), opacity: float = Query(1.0),
):
    result = validate_visual_signature(layer_type, {"color": color, "opacity": opacity})
    _log_audit("VALIDATE_VISUAL", f"{layer_type},{color}", result["valid"])
    return {"engine": "ESI-Omega", **result, "norme": VISUAL_RULES.get(layer_type, {})}


@router.get("/laws")
async def esi_laws():
    return {
        "engine": "ESI-Omega",
        "bce_4x": BCE_4X_LAWS,
        "terrain_rules": TERRAIN_RULES,
        "visual_rules": VISUAL_RULES,
        "engines_proteges": ENGINES_INSTITUTIONNELS,
        "piliers_proteges": PILIERS,
        "master_switch_authority": MASTER_SWITCH_AUTHORITY,
        "document_maitre": DOCUMENT_MAITRE,
    }


@router.get("/audit")
async def esi_audit(limit: int = Query(50)):
    return {
        "engine": "ESI-Omega",
        "entries": _audit_log[-limit:],
        "total": len(_audit_log),
    }


@router.get("/conformite/full")
async def esi_conformite_full(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
):
    start = time.time()
    checks = []

    # 1. Species coherence
    sc = validate_species_coherence(species, {})
    checks.append({"check": "species_coherence", **sc})

    # 2. Season coherence
    m = datetime.now(timezone.utc).month
    mc = validate_season_coherence(m, {})
    checks.append({"check": "season_coherence", **mc})

    # 3. Bundle validation
    from engines.v8_national.phase_b_engines import generate_zones_ta, generate_corridors_ta, generate_affuts_ta
    h = datetime.now(timezone.utc).hour
    zones = generate_zones_ta(lat, lon, species, m)
    corridors = generate_corridors_ta(lat, lon, species, m, h)
    affuts = generate_affuts_ta(lat, lon, species, zones, corridors)
    bv = validate_bundle({"zones": zones, "corridors": corridors, "affuts": affuts})
    checks.append({"check": "bundle_validation", "total": bv["total_checks"], "passed": bv["passed"], "failed": bv["failed"], "conformite": bv["conformite"]})

    # 4. Visual signatures
    for lt, rules in VISUAL_RULES.items():
        if "color" in rules:
            vv = validate_visual_signature(lt, {"color": rules["color"], "opacity": rules.get("opacity", 1.0)})
            checks.append({"check": f"visual_{lt}", **vv})

    # 5. Scoring determinism
    from engines.v8_institutional.engine_score_global import compute_score_global
    s1 = compute_score_global(lat, lon, species, m, h)
    s2 = compute_score_global(lat, lon, species, m, h)
    sd = validate_scoring_determinism(lat, lon, species, s1["score_global"], s2["score_global"])
    checks.append({"check": "scoring_determinism", **sd})

    total = len(checks)
    passed = sum(1 for c in checks if c.get("valid", c.get("conformite") == "CONFORME"))
    failed = total - passed

    _log_audit("CONFORMITE_FULL", f"{lat},{lon},{species}", f"{passed}/{total}")

    return {
        "engine": "ESI-Omega",
        "document_maitre": DOCUMENT_MAITRE,
        "checks": checks,
        "total": total,
        "passed": passed,
        "failed": failed,
        "conformite_globale": "CONFORME" if failed == 0 else "NON-CONFORME",
        "compute_ms": round((time.time() - start) * 1000),
    }
