"""ENGINE-INCERTITUDE-Ω — Quantification incertitude par couche/engine/espece."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call, get_studies, get_species_profile

ENGINE_NAME = "ENGINE-INCERTITUDE-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Incertitude par couche/engine/espece (variance, densite etudes, confiance GOV/UNI/PR)", "GOUVERNANCE", [])


def _confidence_source(org: str) -> float:
    """Score confiance selon type source: GOV=1.0, UNI=0.85, PR (peer-reviewed journals)=0.75."""
    org_lower = (org or "").lower()
    if any(k in org_lower for k in ["gov", "mffp", "usgs", "usfws", "noaa", "nasa", "iucn", "parcs"]):
        return 1.0
    if any(k in org_lower for k in ["univ", "university", "canadian science", "wiley", "frontiers", "alces"]):
        return 0.85
    return 0.75


def compute_incertitude(terrain_v10: dict, species: str = "cerf") -> dict:
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}

    # Terrain fiabilite (deja expose)
    fiabilite_terrain = terrain.get("fiabilite", 0.5)

    # Studies density pour l'espece
    studies = get_studies()
    species_studies = [s for s in studies if species.lower() in (s.get("topic") or "").lower() or species.lower() == "cerf"]
    density = min(1.0, len(species_studies) / 5)

    # Confiance pondérée des sources
    confidences = [_confidence_source(s.get("org", "")) for s in studies]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

    # Completude profil espece
    profile = get_species_profile(species) or {}
    profile_completeness = min(1.0, sum(1 for v in profile.values() if v) / 5)

    # Uncertainty score (0=certain, 100=incertain)
    certainty = fiabilite_terrain * 0.35 + density * 0.25 + avg_confidence * 0.25 + profile_completeness * 0.15
    uncertainty_score = round((1 - certainty) * 100, 1)

    if uncertainty_score < 20:
        level = "TRES-FAIBLE"
    elif uncertainty_score < 40:
        level = "FAIBLE"
    elif uncertainty_score < 60:
        level = "MODEREE"
    else:
        level = "FORTE"

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "uncertainty_score": uncertainty_score,
        "certainty_score": round(certainty * 100, 1),
        "score": round((1 - (uncertainty_score / 100)) * 100, 1),  # inverse pour dashboard
        "level": level,
        "factors": {
            "terrain_fiabilite": fiabilite_terrain,
            "studies_density_species": round(density, 3),
            "avg_source_confidence": round(avg_confidence, 3),
            "profile_completeness": round(profile_completeness, 3),
        },
        "studies_count": len(studies),
        "studies_species_specific": len(species_studies),
    }
