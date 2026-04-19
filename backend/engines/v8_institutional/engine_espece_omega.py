"""ENGINE-ESPECE-Ω — Profils espèces depuis catalog SCIENCE-Ω."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call, get_species_profile

ENGINE_NAME = "ENGINE-ESPECE-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Profils espèces (5 espèces BCE-4X)", "BIO-SYSTEME", ["MFFP_INVENTAIRES"])


def compute_especes(species: str) -> dict:
    mark_call(ENGINE_NAME)
    profile = get_species_profile(species)
    if not profile:
        return {"engine": ENGINE_NAME, "version": ENGINE_VERSION, "species": species, "found": False, "score": 0}
    # Score confiance profil = richesse des champs renseignés
    populated = sum(1 for v in profile.values() if v)
    score = min(100, populated * 20)
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION, "species": species, "found": True, "score": score,
        "profile": profile,
        "data_sources": ["MFFP_INVENTAIRES"],
    }
