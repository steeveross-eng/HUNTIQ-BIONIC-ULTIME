"""
SPECIES WEIGHTING PROFILES — variantes pondérations par espèce (Phase X).
Applique sur SCORE-GLOBAL-REALITY selon species.
"""

# Base 21 axes. Profils par espèce ajustent ± relatifs.
# Orignal: + habitat/hydrologie/thermique (zones humides, sensible chaleur)
# Chevreuil: + nutrition/stress (résilient mais sensible pression)
# Wapiti: + connectivite/habitat (migration)
# Ours: + population/habitat (home range large)
# Dindon: + ia_vision/comportement (sol foraging)

SPECIES_WEIGHTS = {
    "orignal": {
        "habitat": 0.11, "hydrologie": 0.08, "thermique": 0.10, "connectivite": 0.08,
        "nutrition": 0.09, "stress_anthropique": 0.08, "population": 0.05, "hotspots": 0.05,
        "comportement_bio": 0.05, "quality": 0.04, "calibration": 0.04, "climat_futur": 0.05,
        "sensoriel": 0.03, "sol": 0.03, "pression_atmo": 0.03, "incertitude_inv": 0.04,
        "zones": 0.02, "lunaire": 0.01, "ia_vision": 0.01, "contamination_malus": 0.01, "vent": 0.00,
    },
    "chevreuil": {
        "nutrition": 0.12, "stress_anthropique": 0.10, "habitat": 0.08, "population": 0.07,
        "hotspots": 0.07, "connectivite": 0.06, "comportement_bio": 0.06, "thermique": 0.05,
        "quality": 0.05, "calibration": 0.04, "sensoriel": 0.04, "hydrologie": 0.03,
        "sol": 0.03, "climat_futur": 0.03, "pression_atmo": 0.04, "incertitude_inv": 0.04,
        "zones": 0.03, "lunaire": 0.02, "ia_vision": 0.02, "contamination_malus": 0.02, "vent": 0.00,
    },
    "wapiti": {
        "connectivite": 0.10, "habitat": 0.10, "nutrition": 0.09, "population": 0.08,
        "hotspots": 0.06, "stress_anthropique": 0.07, "comportement_bio": 0.06, "thermique": 0.05,
        "quality": 0.04, "calibration": 0.04, "climat_futur": 0.05, "sensoriel": 0.04,
        "hydrologie": 0.04, "sol": 0.03, "pression_atmo": 0.03, "incertitude_inv": 0.04,
        "zones": 0.03, "lunaire": 0.02, "ia_vision": 0.02, "contamination_malus": 0.01, "vent": 0.00,
    },
    "ours_noir": {
        "population": 0.10, "habitat": 0.10, "nutrition": 0.10, "hotspots": 0.07,
        "stress_anthropique": 0.08, "connectivite": 0.06, "thermique": 0.05, "comportement_bio": 0.05,
        "quality": 0.04, "calibration": 0.04, "hydrologie": 0.04, "sol": 0.04,
        "climat_futur": 0.03, "pression_atmo": 0.03, "incertitude_inv": 0.04, "sensoriel": 0.03,
        "zones": 0.03, "lunaire": 0.02, "ia_vision": 0.02, "contamination_malus": 0.03, "vent": 0.00,
    },
    "dindon_sauvage": {
        "ia_vision": 0.08, "comportement_bio": 0.08, "habitat": 0.08, "sol": 0.08,
        "nutrition": 0.09, "population": 0.07, "hotspots": 0.07, "thermique": 0.05,
        "connectivite": 0.05, "stress_anthropique": 0.06, "quality": 0.04, "calibration": 0.04,
        "climat_futur": 0.04, "pression_atmo": 0.03, "incertitude_inv": 0.04, "sensoriel": 0.03,
        "hydrologie": 0.03, "zones": 0.02, "lunaire": 0.02, "contamination_malus": 0.02, "vent": 0.00,
    },
}

_ALIAS = {
    "cerf": "chevreuil", "deer": "chevreuil",
    "moose": "orignal",
    "elk": "wapiti",
    "bear": "ours_noir", "ours": "ours_noir",
    "turkey": "dindon_sauvage", "dindon": "dindon_sauvage",
}


def get_species_weights(species: str) -> dict | None:
    key = _ALIAS.get(species.lower(), species.lower())
    w = SPECIES_WEIGHTS.get(key)
    if not w:
        return None
    # Renormalise (paranoia)
    total = sum(w.values()) or 1.0
    return {k: round(v / total, 5) for k, v in w.items()}
