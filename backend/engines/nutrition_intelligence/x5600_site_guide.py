"""
×5600 — SITE_GUIDE_ENGINE
Recommandations contextuelles: ou implanter, comment construire.
Souche bois mou vs bois dur. Surfaces, couvert, exposition.
"""

SUBSTRATE_OPTIONS = {
    "bois_mou": {
        "name": "Souche bois mou (sapin, epinette, pin)",
        "absorption": "ELEVEE",
        "liberation": "Progressive (6-10 semaines)",
        "duree": "Longue (1-2 saisons avant remplacement)",
        "reactivation_weeks": 8,
        "cost_cad": 0,
        "avantages": [
            "Absorption minerale superieure (fibre spongieuse)",
            "Liberation lente et constante des mineraux",
            "Duree de vie plus longue",
            "Ideal pour sols acides et coniferes",
        ],
        "inconvenients": [
            "Plus difficile a trouver en zone feuillu",
            "Risque de pourriture si drainage insuffisant",
        ],
    },
    "bois_dur": {
        "name": "Souche bois dur (erable, bouleau, chene)",
        "absorption": "MODEREE",
        "liberation": "Rapide (3-5 semaines)",
        "duree": "Moyenne (recharges frequentes)",
        "reactivation_weeks": 5,
        "cost_cad": 0,
        "avantages": [
            "Facilement disponible en zone mixte/feuillu",
            "Surface dure = moins de perte par pluie",
            "Ideal pour sites a fort trafic animal",
        ],
        "inconvenients": [
            "Recharges plus frequentes",
            "Absorption minerale inferieure",
            "Moins efficace en liberation lente",
        ],
    },
}

SITE_CRITERIA = {
    "surface_min_m2": 2,
    "surface_max_m2": 6,
    "surface_optimale_m2": 4,
    "couvert_ideal": "Semi-ouvert (30-60% canopee)",
    "exposition_ideale": "Sud-Est (soleil matinal, ombre apres-midi)",
    "drainage": "Bien draine, eviter cuvettes",
    "distance_corridor_m": 50,
    "distance_eau_m": 200,
    "distance_route_m": 300,
}


def generate_site_guide(species: str, season: str, soil_type: str) -> dict:
    """Guide complet pour implantation site d'alimentation."""
    surface = SITE_CRITERIA["surface_optimale_m2"]
    if species == "orignal":
        surface = 6
    elif species == "wapiti":
        surface = 5

    return {
        "species": species,
        "season": season,
        "soil_type": soil_type,
        "implantation": {
            "surface_recommandee_m2": surface,
            "couvert": SITE_CRITERIA["couvert_ideal"],
            "exposition": SITE_CRITERIA["exposition_ideale"],
            "drainage": SITE_CRITERIA["drainage"],
            "distance_corridor_m": SITE_CRITERIA["distance_corridor_m"],
            "distance_eau_m": SITE_CRITERIA["distance_eau_m"],
            "distance_route_m": SITE_CRITERIA["distance_route_m"],
        },
        "substrats": {
            "bois_mou": {
                **SUBSTRATE_OPTIONS["bois_mou"],
                "recommande": soil_type in ("acide", "coniferes", "sableux"),
            },
            "bois_dur": {
                **SUBSTRATE_OPTIONS["bois_dur"],
                "recommande": soil_type in ("loam", "mixte"),
            },
        },
        "construction": [
            f"1. Selectionner une souche {'bois mou' if soil_type in ('acide', 'coniferes') else 'bois dur'} de {surface}m2 minimum",
            "2. Creuser une depression de 10-15cm autour de la souche",
            "3. Assurer un drainage correct (pente legere)",
            "4. Appliquer le melange mineral initial sur et autour de la souche",
            "5. Couvrir de branches mortes pour protection initiale",
            f"6. Reactiver toutes les {SUBSTRATE_OPTIONS['bois_mou' if soil_type in ('acide', 'coniferes') else 'bois_dur']['reactivation_weeks']} semaines",
        ],
    }
