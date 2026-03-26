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

ECOLOGICAL_ZONES = {
    "chevreuil": {
        "nom_commun": "Cerf de Virginie (Odocoileus virginianus)",
        "habitat_principal": "Forets mixtes et decidues du sud du Quebec et de l'Ontario. Bordures de foret, friches agricoles, zones de regeneration.",
        "zones_ecologiques": [
            {"zone": "Erabliere a bouleau jaune", "description": "Zone optimale. Couvert dense en ete, nourriture abondante (glands, ramilles). Sol loam riche en Ca et P."},
            {"zone": "Foret mixte (coniferes-feuillus)", "description": "Habitat hivernal prefere. Les coniferes offrent un couvert thermique. Sol plus acide, deficits frequents en P et Se."},
            {"zone": "Friches et regeneration", "description": "Alimentation estivale riche (herbacees, arbustes). Sol variable. Points nutritionnels efficaces en bordure."},
        ],
        "comportement_saisonnier": {
            "printemps": "Recuperation post-hivernale. Males: debut croissance bois. Femelles: fin gestation. Besoins Ca/P/Na maximaux.",
            "ete": "Croissance bois active. Lactation biches. Alimentation diversifiee. Frequentation points nutritionnels moderee.",
            "pre_rut": "Stockage energetique intense. Males: marquage territorial, frottis. Besoins energetiques en hausse.",
            "rut": "Depense energetique extreme pour males. Alimentation reduite. Supplementation energetique critique.",
            "post_rut": "Recuperation males. Debut gestation femelles. Besoins proteiques et energetiques eleves.",
            "hiver": "Survie. Metabolisme reduit. Conservation energetique. Yards de cerfs en coniferes denses.",
        },
    },
    "orignal": {
        "nom_commun": "Orignal (Alces americanus)",
        "habitat_principal": "Forets boreales et mixtes du Quebec, Ontario, et provinces maritimes. Zones humides, lacs, cours d'eau.",
        "zones_ecologiques": [
            {"zone": "Foret boreale (pessiere-sapiniere)", "description": "Habitat principal. Alimentation hivernale sur sapins et bouleaux. Sol tres acide, deficits severes en Na, Ca, P, Se."},
            {"zone": "Zones humides et riveraines", "description": "Alimentation estivale sur plantes aquatiques (nenuphars, potamots). Source naturelle de Na. Points nutritionnels efficaces en peripherie."},
            {"zone": "Brulis et coupes forestieres", "description": "Regeneration riche en feuillus. Habitat de transition. Sol perturbe, disponibilite minerale variable."},
        ],
        "comportement_saisonnier": {
            "printemps": "Sortie des ravages. Recherche active de sodium (salines naturelles, bords de route). Debut croissance bois massifs.",
            "ete": "Alimentation aquatique. Frequentation maximale des zones humides. Croissance bois rapide (2cm/jour).",
            "pre_rut": "Marquage territorial. Depouillement du velours. Besoins energetiques en forte hausse.",
            "rut": "Vocalisation, combat entre males. Perte de poids significative (jusqu'a 20%). Supplementation critique.",
            "post_rut": "Recuperation. Migration vers ravages hivernaux. Besoin de reconstituer les reserves.",
            "hiver": "Ravages en sapiniere dense. Metabolisme reduit de 30%. Alimentation sur ramilles de sapin et bouleau.",
        },
    },
    "ours_noir": {
        "nom_commun": "Ours noir (Ursus americanus)",
        "habitat_principal": "Forets mixtes et boreales. Zones riches en petits fruits, noix et insectes. Evite les zones ouvertes.",
        "zones_ecologiques": [
            {"zone": "Foret decidue riche (erabliere, chenaie)", "description": "Habitat automnal optimal. Glands, faines, noix. Sol riche. Points nutritionnels attractifs en lisiere."},
            {"zone": "Foret boreale (pessiere-bleuetiere)", "description": "Habitat estival. Bleuets, framboises, insectes. Sol acide, deficits en Ca et P compensables par supplementation."},
            {"zone": "Zones humides et vallees", "description": "Source de proteines (poissons, amphibiens). Habitat printanier post-hibernation. Besoins mineraux maximaux a la sortie."},
        ],
        "comportement_saisonnier": {
            "printemps": "Sortie d'hibernation. Perte de 15-30% de masse corporelle. Recherche intensive de nourriture. Besoins Ca/Na/K maximaux.",
            "ete": "Alimentation sur petits fruits et insectes. Constitution progressive des reserves. Frequentation reguliere des points attractifs.",
            "pre_rut": "Hyperphagie debutante. Consommation alimentaire multipliee par 3. Recherche de sources energetiques denses.",
            "rut": "Accouplement. Males parcourent de grandes distances. Alimentation reduite mais besoins energetiques eleves.",
            "post_rut": "Hyperphagie maximale. Jusqu'a 20,000 calories/jour. Accumulation de graisse pour hibernation. Phase critique.",
            "hiver": "Hibernation (novembre-avril). Metabolisme reduit de 75%. Aucune alimentation. Femelles: mise bas en janvier.",
        },
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
        "ecozone": ECOLOGICAL_ZONES.get(species, {}),
    }


def get_ecological_zones(species: str = None) -> dict:
    """Retourne les descriptions ecologiques pour une ou toutes les especes."""
    if species and species in ECOLOGICAL_ZONES:
        return {"species": species, "data": ECOLOGICAL_ZONES[species]}
    return {"all_species": ECOLOGICAL_ZONES}
