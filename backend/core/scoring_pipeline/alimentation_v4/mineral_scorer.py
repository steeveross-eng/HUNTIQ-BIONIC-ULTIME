"""
BCE-4X P0-X-3 — SCORING MINERAUX + SAISONNIER
================================================
ORDONNANCE STEEVE-MAX 2026-04-06 | SUPRA VALIDE
Branche: BIONIC_REWRITE_P0

Scoring des mineraux du sol (logique inversee: carence = score eleve)
et multiplicateur saisonnier par espece.

Sources scientifiques SUPRA validees:
- Atwood & Weeks (2002) — Mineral requirements of white-tailed deer
- Tankersley & Gasaway (1983) — Mineral lick use by moose
- Parker et al. (2009) — Nutrition integrates environmental responses
- MFFP Quebec (2019) — Carte pedologique

Critere 7 (Sentier): SUPRA valide conditionnellement (dependance OSM).
Critere 9 (Securite): SUPRA valide conditionnellement (proxy, 5%).
"""
import logging

logger = logging.getLogger("bionic.salines_v4.mineral_scorer")

# ═══════════════════════════════════════════════════════════
# SEUILS DE CARENCE — BASES PEDOLOGIQUES QUEBEC
# ═══════════════════════════════════════════════════════════

CARENCE_THRESHOLDS = {
    "selenium_ppm": {"seuil": 0.2, "points": 30, "label": "Selenium"},
    "calcium_ppm": {"seuil": 500, "points": 25, "label": "Calcium"},
    "phosphore_ppm": {"seuil": 10, "points": 20, "label": "Phosphore"},
    "zinc_ppm": {"seuil": 5, "points": 15, "label": "Zinc"},
    "cuivre_ppm": {"seuil": 3, "points": 10, "label": "Cuivre"},
}

# ═══════════════════════════════════════════════════════════
# MULTIPLICATEURS SAISONNIERS — PAR ESPECE
# Sources: Hewitt 2011, Robbins 1993, Tankersley 1983, Parker 2009
# ═══════════════════════════════════════════════════════════

SEASONAL_MULTIPLIERS = {
    "CERF": {
        4: 1.2, 5: 1.2,    # Printemps: croissance bois, Ca/P++
        6: 1.3, 7: 1.3,    # Ete: lactation, Na++
        8: 1.0, 9: 1.0, 10: 1.0,  # Automne: base
        11: 0.8, 12: 0.8, 1: 0.8, 2: 0.8, 3: 0.8,  # Hiver: reduit
    },
    "ORIGNAL": {
        4: 1.3, 5: 1.3,    # Printemps: Na critique apres hiver
        6: 1.2, 7: 1.2,    # Ete: Na stable
        8: 0.9, 9: 0.9, 10: 0.9,  # Automne: rut, moins stationnaire
        11: 0.7, 12: 0.7, 1: 0.7, 2: 0.7, 3: 0.7,  # Hiver: sedentaire
    },
    "WAPITI": {
        4: 1.2, 5: 1.2,    # Printemps: Ca/P++
        6: 1.1, 7: 1.1,    # Ete: modere
        8: 1.0, 9: 1.0, 10: 1.0,  # Automne: base
        11: 0.8, 12: 0.8, 1: 0.8, 2: 0.8, 3: 0.8,  # Hiver: reduit
    },
}


def score_mineral_carences(nutriments_sol: dict) -> tuple:
    """
    Score les carences du sol (logique INVERSEE: sol carencé → score ELEVE).
    Un sol carencé justifie DAVANTAGE la presence d'une saline.

    Retourne: (score 0-100, liste des carences detectees)
    """
    score = 0
    carences = []

    for key, config in CARENCE_THRESHOLDS.items():
        valeur = nutriments_sol.get(key, config["seuil"] + 1)
        if valeur < config["seuil"]:
            score += config["points"]
            carences.append({
                "mineral": config["label"],
                "valeur": valeur,
                "seuil": config["seuil"],
                "points": config["points"],
            })

    return min(100, score), carences


def get_seasonal_multiplier(species: str, month: int) -> tuple:
    """
    Retourne le multiplicateur saisonnier pour l'espece et le mois donnes.
    Retourne: (multiplicateur float, justification string)
    """
    species_upper = species.upper()
    multipliers = SEASONAL_MULTIPLIERS.get(species_upper, SEASONAL_MULTIPLIERS["CERF"])
    mult = multipliers.get(month, 1.0)

    # Justification saisonniere
    if month in [4, 5]:
        saison = "printemps"
        justif = "Croissance bois (Ca/P)" if species_upper != "ORIGNAL" else "Besoin Na critique post-hiver"
    elif month in [6, 7]:
        saison = "ete"
        justif = "Lactation/sudation (Na)" if species_upper == "CERF" else "Alimentation aquatique (Na)"
    elif month in [8, 9, 10]:
        saison = "automne"
        justif = "Rut/engraissement" if species_upper == "ORIGNAL" else "Besoins moderes"
    else:
        saison = "hiver"
        justif = "Conservation energie, activite reduite"

    return mult, f"{saison}: {justif} (x{mult})"


def compute_seasonal_mineral_score(nutriments_sol: dict, species: str, month: int) -> dict:
    """
    Score mineral + saisonnier combine.
    Retourne un dict complet avec score, carences, multiplicateur et tracabilite.
    """
    mineral_score, carences = score_mineral_carences(nutriments_sol)
    multiplier, justif = get_seasonal_multiplier(species, month)

    # Score combine = mineral * multiplicateur saisonnier
    combined_score = min(100, round(mineral_score * multiplier))

    return {
        "mineral_score_brut": mineral_score,
        "seasonal_multiplier": multiplier,
        "combined_score": combined_score,
        "carences": carences,
        "n_carences": len(carences),
        "justification_saisonniere": justif,
        "species": species.upper(),
        "month": month,
    }
