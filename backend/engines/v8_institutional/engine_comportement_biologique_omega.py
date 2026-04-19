"""ENGINE-COMPORTEMENT-BIOLOGIQUE-Ω — Patterns comportementaux saisonniers."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call, get_species_profile

ENGINE_NAME = "ENGINE-COMPORTEMENT-BIOLOGIQUE-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Patterns comportementaux biologiques saisonniers (home range, activite, corridors)", "COMPORTEMENT-HUMAIN", ["USGS_MOVEMENT"])

_SAISON_MOIS = {1:"hiver",2:"hiver",3:"printemps",4:"printemps",5:"printemps",6:"ete",7:"ete",8:"ete",9:"automne",10:"automne",11:"automne",12:"hiver"}


def compute_comportement_biologique(species: str, month: int, hour: int = 7) -> dict:
    mark_call(ENGINE_NAME)
    profile = get_species_profile(species)
    saison = _SAISON_MOIS.get(int(month), "automne")
    behavior = profile.get("behavior", {}) if profile else {}
    comp_sais = (behavior.get("comportements_saisonniers") or {}).get(saison, "")

    # Score activite probable a cette heure
    is_crep = 5 <= hour <= 8 or 17 <= hour <= 20
    is_noct = hour < 5 or hour > 20
    activite_score = 80 if is_crep else (60 if is_noct else 40)

    # Score composite mobilite (corridor presence + dispersion connue)
    has_corridors = "corridors" in behavior
    home_range = behavior.get("home_range_km2") or [0, 0]
    mobility = (sum(home_range) / 2) if isinstance(home_range, list) else 0
    score = min(100, activite_score * 0.5 + (mobility * 2) * 0.3 + (30 if has_corridors else 0) * 0.2)

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION, "species": species, "saison": saison, "hour": hour,
        "score": round(score, 1),
        "activite_score": activite_score,
        "comportement_saison": comp_sais,
        "home_range_km2": home_range,
        "is_crepusculaire": is_crep,
        "is_nocturne": is_noct,
        "data_sources": ["USGS_MOVEMENT", "MFFP_INVENTAIRES"],
    }
