"""
ENGINE-CONTAMINATION-Ω V2 + MODULE ANTI-CONTAMINATION-INSTITUTIONNEL-Ω
======================================================================
V2 : CWD/maladies + cartographie heatmap + impact propagation
ANTI-CONTAMINATION : filtre et valide observations avant ingestion.
"""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

register_engine("ENGINE-CONTAMINATION-Ω-V2", "V2-PHASE-X-2026-04", "Contamination CWD/maladies + heatmap + propagation", "BIO-SYSTEME", ["CWD_ALLIANCE", "MFFP_INVENTAIRES"])
register_engine("ANTI-CONTAMINATION-INSTITUTIONNEL-Ω", "V1-PHASE-X-2026-04", "Filtrage systematique + validation croisee observations", "GOUVERNANCE", [])

# Zones MDC connues QC (2024) — source MFFP
_CWD_ZONES_QC = [
    {"zone": "Estrie-Sud", "lat": 45.4, "lon": -72.0, "cases_2024": 8, "surveillance": "INTENSIVE"},
    {"zone": "Monteregie-Frelighsburg", "lat": 45.0, "lon": -72.8, "cases_2024": 3, "surveillance": "ACTIVE"},
]


def compute_contamination_v2(contamination_v1: list, lat: float, lon: float, species: str) -> dict:
    """V2: enrichit contamination-V1 avec CWD/maladies proximales."""
    mark_call("ENGINE-CONTAMINATION-Ω-V2")

    # Distance a zones CWD connues
    nearest_cwd = None
    min_dist = float("inf")
    for z in _CWD_ZONES_QC:
        d = ((lat - z["lat"]) ** 2 + (lon - z["lon"]) ** 2) ** 0.5 * 111  # ~km
        if d < min_dist:
            min_dist = d
            nearest_cwd = z

    cwd_risk = "FAIBLE"
    if nearest_cwd:
        if min_dist < 20:
            cwd_risk = "ELEVE"
        elif min_dist < 60:
            cwd_risk = "MODERE"
        elif min_dist < 150:
            cwd_risk = "FAIBLE"
        else:
            cwd_risk = "TRES-FAIBLE"

    # Score propreté (100 = clean, 0 = fortement contamine)
    score = 100
    if contamination_v1:
        score -= min(50, len(contamination_v1) * 5)
    if cwd_risk == "ELEVE":
        score -= 30
    elif cwd_risk == "MODERE":
        score -= 15
    score = max(0, score)

    return {
        "engine": "ENGINE-CONTAMINATION-Ω-V2",
        "score": score,
        "contamination_v1_cones": len(contamination_v1) if contamination_v1 else 0,
        "cwd_risk": cwd_risk,
        "nearest_cwd_zone": nearest_cwd,
        "distance_nearest_cwd_km": round(min_dist, 1) if nearest_cwd else None,
        "species": species,
        "references": [
            "CWD Alliance Data Dashboard (cwd-info.org)",
            "MFFP Surveillance MDC Estrie 2024",
        ],
        "recommendations": [
            "Declarer toute observation suspecte a MFFP 1-877-346-6763",
            "Ne pas transporter cervide intact hors zone MDC",
        ] if cwd_risk in ("ELEVE", "MODERE") else [],
    }


def anti_contamination_filter(observation: dict) -> dict:
    """Filtre observation avant ingestion ML. Detecte anomalies, rejette si non-coherent."""
    mark_call("ANTI-CONTAMINATION-INSTITUTIONNEL-Ω")
    issues = []
    confidence = float(observation.get("confidence", 0.75))

    # Validation geo
    lat = observation.get("lat")
    lon = observation.get("lon")
    if not (lat and lon):
        issues.append("coords_invalid")
    elif not (40 <= lat <= 60 and -85 <= lon <= -55):
        issues.append("coords_out_of_qc_extent")

    # Validation source
    valid_sources = {"camera-reconyx", "camera-cellulaire", "camera-sd", "gps-cellulaire",
                      "pin", "note", "photo-exif", "video", "recolte", "trace", "collier-gps"}
    if observation.get("source_type") not in valid_sources:
        issues.append("unknown_source_type")

    # Validation confidence
    if confidence < 0.2:
        issues.append("confidence_too_low")

    # Validation espece
    valid_species = {"cerf", "chevreuil", "orignal", "wapiti", "ours_noir", "dindon_sauvage", "moose", "deer", "elk", "bear", "turkey"}
    if observation.get("species", "").lower() not in valid_species:
        issues.append("unknown_species")

    accepted = len(issues) == 0 or (issues == ["unknown_species"] and confidence > 0.5)
    severity = "REJECT" if len(issues) >= 2 else ("WARN" if issues else "OK")

    return {
        "accepted": accepted,
        "severity": severity,
        "issues": issues,
        "confidence_adjusted": round(confidence * (1 - 0.2 * len(issues)), 3),
    }
