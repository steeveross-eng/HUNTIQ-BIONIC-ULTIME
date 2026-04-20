"""ENGINE-POPULATION-DYNAMICS-Ω — Demographie multi-especes."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call, get_species_profile

ENGINE_NAME = "ENGINE-POPULATION-DYNAMICS-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Dynamique de population (croissance, mortalite, tendances 5/10/20 ans)", "BIO-SYSTEME", ["MFFP_INVENTAIRES"])

# Parametres demographiques par espece (ordre de grandeur litterature biologique)
_PARAMS = {
    "orignal":        {"natalite": 0.35, "mortalite": 0.18, "capacite_port_km2": 0.4, "tendance_10ans": -0.15, "sensible_climat": True},
    "chevreuil":      {"natalite": 0.75, "mortalite": 0.25, "capacite_port_km2": 8.0, "tendance_10ans": 0.20, "sensible_climat": False},
    "wapiti":         {"natalite": 0.50, "mortalite": 0.20, "capacite_port_km2": 1.5, "tendance_10ans": 0.10, "sensible_climat": False},
    "ours_noir":      {"natalite": 0.30, "mortalite": 0.12, "capacite_port_km2": 0.1, "tendance_10ans": 0.05, "sensible_climat": False},
    "dindon_sauvage": {"natalite": 3.50, "mortalite": 0.60, "capacite_port_km2": 5.0, "tendance_10ans": 0.30, "sensible_climat": True},
}

_ALIAS = {"cerf": "chevreuil", "deer": "chevreuil", "moose": "orignal", "elk": "wapiti",
          "bear": "ours_noir", "turkey": "dindon_sauvage"}


def compute_population_dynamics(species: str, contamination_v2: dict | None = None) -> dict:
    mark_call(ENGINE_NAME)
    key = _ALIAS.get(species.lower(), species.lower())
    params = dict(_PARAMS.get(key) or _PARAMS["chevreuil"])
    profile = get_species_profile(species)

    # Phase X-C : intégration contamination_v2 — augmente mortalité selon CWD
    cwd_impact = {}
    if contamination_v2:
        risk = (contamination_v2.get("cwd_risk") or "").upper()
        dist = contamination_v2.get("distance_nearest_cwd_km")
        mortality_bonus = 0.0
        tendance_penalty = 0.0
        if risk == "ELEVE":
            mortality_bonus = 0.08
            tendance_penalty = 0.10
        elif risk == "MODERE":
            mortality_bonus = 0.04
            tendance_penalty = 0.05
        elif risk == "FAIBLE":
            mortality_bonus = 0.01
            tendance_penalty = 0.01
        if mortality_bonus > 0:
            params["mortalite"] = round(params["mortalite"] + mortality_bonus, 3)
            params["tendance_10ans"] = round(params["tendance_10ans"] - tendance_penalty, 3)
        cwd_impact = {
            "cwd_risk": risk or None,
            "distance_km": dist,
            "mortality_bonus": mortality_bonus,
            "tendance_penalty": tendance_penalty,
        }

    # Taux de croissance r = natalite - mortalite
    r = params["natalite"] - params["mortalite"]

    # Score demographique (0-100) combinant:
    # - croissance favorable (r>0 = sante)
    # - capacite portante (densite soutenable)
    # - tendance 10 ans
    growth_score = min(100, max(0, (r + 0.5) * 100))  # r=-0.5→0, r=0→50, r=+0.5→100
    trend_score = min(100, max(0, (params["tendance_10ans"] + 0.3) * 166))  # -0.3→0, 0→50, +0.3→100
    score = round(growth_score * 0.5 + trend_score * 0.3 + (50 if params["capacite_port_km2"] > 0.5 else 30) * 0.2, 1)

    # Projections demographiques simples (exponentielle)
    # N(t) = N0 * (1+r)^t, t = 5,10,20 ans
    n0 = 1.0  # indice relatif
    projections = {
        "5_ans": round(n0 * (1 + r) ** 5, 3),
        "10_ans": round(n0 * (1 + r) ** 10, 3),
        "20_ans": round(n0 * (1 + r) ** 20, 3),
    }
    # Application tendance observee
    for k, years in [("5_ans", 5), ("10_ans", 10), ("20_ans", 20)]:
        projections[k + "_observed"] = round(n0 * (1 + params["tendance_10ans"] / 10) ** years, 3)

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "species": key,
        "species_profile_found": bool(profile),
        "score": score,
        "parametres_demographiques": params,
        "taux_croissance_r": round(r, 3),
        "projections_index_N0": projections,
        "sensibilite_climat": params["sensible_climat"],
        "contamination_v2_impact": cwd_impact or None,
        "data_sources": ["MFFP_INVENTAIRES"],
        "limites": [
            "Parametres = ordres de grandeur litterature (pas de calibration terrain)",
            "Modele exponentiel sans capacite portante dynamique (logistique = backlog)",
            "Prédation et stochasticite non modelisees",
        ],
    }
