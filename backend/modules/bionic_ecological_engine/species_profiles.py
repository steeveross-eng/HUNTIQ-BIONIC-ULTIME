"""
BIONIC Species Profiles — Referentiel Central des Especes
STEEVE-MAX x2250

Base de donnees systematique de TOUTES les especes chassables
integrees dans l'ecosysteme BIONIC. Chaque profil contient:
- Identification (nom FR/EN/latin, categorie, statut legal)
- Ecologie (habitat, alimentation, comportement, besoins)
- Chasse (saisons, armes, techniques, reglementations)
- Predictions (facteurs d'influence, patterns, seuils)
- Cartographie (couches, couleurs, icones)

Ce fichier est le SEUL point de reference pour les especes.
Tous les modules (backend + frontend) doivent l'utiliser.
"""
from typing import Dict, List, Any


# ═══════════════════════════════════════════════════════════════
# SPECIES PROFILES DATABASE
# ═══════════════════════════════════════════════════════════════

SPECIES_PROFILES: Dict[str, Dict[str, Any]] = {

    # ──────────────────────────────────────────────────────
    # ORIGNAL (Moose)
    # ──────────────────────────────────────────────────────
    "orignal": {
        "id": "orignal",
        "name_fr": "Orignal",
        "name_en": "Moose",
        "name_latin": "Alces alces",
        "category": "gros_gibier",
        "icon": "antlers",
        "color": "#8B4513",
        "map_color": "#A0522D",

        "ecology": {
            "habitat_primary": ["foret_boreale", "foret_mixte", "zone_humide"],
            "habitat_secondary": ["coupe_forestiere", "brulis", "lisiere"],
            "altitude_range_m": [0, 1200],
            "home_range_km2": {"male": 25, "female": 15},
            "preferred_canopy_pct": [30, 70],
            "water_dependency": "high",
            "edge_habitat_preference": "high",
        },

        "diet": {
            "type": "herbivore_browser",
            "primary_foods": ["saule", "bouleau", "tremble", "erable_a_epis", "plantes_aquatiques"],
            "secondary_foods": ["herbes", "fougeres", "ecorces", "lichens"],
            "mineral_needs": {
                "sodium": "very_high",
                "calcium": "high",
                "phosphorus": "high",
                "magnesium": "moderate",
            },
            "daily_intake_kg": 20,
            "saline_attraction": "very_high",
            "seasonal_diet": {
                "printemps": "bourgeons, plantes_aquatiques, herbes",
                "ete": "plantes_aquatiques, feuilles, herbes",
                "automne": "brout_ligneux, ecorces, champignons",
                "hiver": "brout_ligneux, ecorces, coniferes",
            },
        },

        "behavior": {
            "activity_pattern": "crepuscular",
            "peak_hours": ["05:00-08:00", "16:00-19:00"],
            "social": "solitary",
            "rut_period": "septembre-octobre",
            "sensitivity_to_pressure": "moderate",
            "flight_distance_m": 200,
            "nocturnal_shift_threshold": 60,
            "temperature_optimal_c": [-5, 15],
            "wind_sensitivity": "moderate",
            "moon_sensitivity": "moderate",
        },

        "predictions": {
            "base_success_rate": 0.45,
            "temp_bonus": {"range": [-5, 10], "bonus": 0.15},
            "pressure_rising_bonus": 0.10,
            "solunar_major_bonus": 0.12,
            "low_wind_bonus": 0.08,
            "rut_bonus": 0.25,
            "rain_light_bonus": 0.05,
            "full_moon_penalty": -0.08,
            "high_pressure_penalty": -0.15,
        },

        "hunting": {
            "seasons": {
                "arc": "septembre",
                "arbalete": "octobre",
                "arme_a_feu": "octobre-novembre",
                "poudre_noire": "novembre",
            },
            "techniques": ["appel", "affut", "traque", "battue"],
            "registration_required": True,
            "permits_required": ["permis_gros_gibier", "cesp_orignal"],
            "bag_limit": 1,
            "jurisdiction_portals": {
                "QC": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse",
                "ON": "https://www.ontario.ca/page/hunting",
            },
        },
    },

    # ──────────────────────────────────────────────────────
    # CERF DE VIRGINIE (White-tailed Deer)
    # ──────────────────────────────────────────────────────
    "cerf_virginie": {
        "id": "cerf_virginie",
        "name_fr": "Cerf de Virginie",
        "name_en": "White-tailed Deer",
        "name_latin": "Odocoileus virginianus",
        "category": "gros_gibier",
        "icon": "deer",
        "color": "#D2691E",
        "map_color": "#CD853F",

        "ecology": {
            "habitat_primary": ["foret_mixte", "foret_feuillue", "lisiere"],
            "habitat_secondary": ["terres_agricoles", "verger", "friche"],
            "altitude_range_m": [0, 800],
            "home_range_km2": {"male": 8, "female": 3},
            "preferred_canopy_pct": [40, 80],
            "water_dependency": "moderate",
            "edge_habitat_preference": "very_high",
        },

        "diet": {
            "type": "herbivore_browser_grazer",
            "primary_foods": ["herbes", "trefle", "luzerne", "glands", "pommes"],
            "secondary_foods": ["champignons", "fougeres", "cedre", "pruche"],
            "mineral_needs": {
                "sodium": "high",
                "calcium": "very_high",
                "phosphorus": "high",
                "magnesium": "moderate",
            },
            "daily_intake_kg": 3,
            "saline_attraction": "high",
            "seasonal_diet": {
                "printemps": "herbes_vertes, trefle, bourgeons",
                "ete": "herbes, fruits, cultures",
                "automne": "glands, pommes, mais, champignons",
                "hiver": "cedre, pruche, ecorces, brout_ligneux",
            },
        },

        "behavior": {
            "activity_pattern": "crepuscular",
            "peak_hours": ["05:30-08:30", "16:30-19:30"],
            "social": "small_groups",
            "rut_period": "novembre",
            "sensitivity_to_pressure": "high",
            "flight_distance_m": 150,
            "nocturnal_shift_threshold": 45,
            "temperature_optimal_c": [0, 20],
            "wind_sensitivity": "high",
            "moon_sensitivity": "high",
        },

        "predictions": {
            "base_success_rate": 0.40,
            "temp_bonus": {"range": [0, 15], "bonus": 0.12},
            "pressure_rising_bonus": 0.12,
            "solunar_major_bonus": 0.15,
            "low_wind_bonus": 0.10,
            "rut_bonus": 0.30,
            "rain_light_bonus": 0.06,
            "full_moon_penalty": -0.10,
            "high_pressure_penalty": -0.18,
        },

        "hunting": {
            "seasons": {
                "arc": "septembre-octobre",
                "arbalete": "octobre",
                "arme_a_feu": "novembre",
                "poudre_noire": "novembre-decembre",
            },
            "techniques": ["affut", "traque", "battue", "approche"],
            "registration_required": True,
            "permits_required": ["permis_gros_gibier", "cesp_cerf"],
            "bag_limit": 2,
            "jurisdiction_portals": {
                "QC": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse",
                "ON": "https://www.ontario.ca/page/hunting",
            },
        },
    },

    # ──────────────────────────────────────────────────────
    # OURS NOIR (Black Bear)
    # ──────────────────────────────────────────────────────
    "ours_noir": {
        "id": "ours_noir",
        "name_fr": "Ours noir",
        "name_en": "Black Bear",
        "name_latin": "Ursus americanus",
        "category": "gros_gibier",
        "icon": "bear",
        "color": "#2C2C2C",
        "map_color": "#4A4A4A",

        "ecology": {
            "habitat_primary": ["foret_boreale", "foret_mixte", "foret_feuillue"],
            "habitat_secondary": ["zone_humide", "brulis", "depot_ordures"],
            "altitude_range_m": [0, 2000],
            "home_range_km2": {"male": 100, "female": 25},
            "preferred_canopy_pct": [50, 90],
            "water_dependency": "moderate",
            "edge_habitat_preference": "moderate",
        },

        "diet": {
            "type": "omnivore",
            "primary_foods": ["baies", "glands", "insectes", "herbes", "charognes"],
            "secondary_foods": ["poissons", "petits_mammiferes", "miel", "racines"],
            "mineral_needs": {
                "sodium": "moderate",
                "calcium": "moderate",
                "phosphorus": "moderate",
                "magnesium": "low",
            },
            "daily_intake_kg": 12,
            "saline_attraction": "moderate",
            "seasonal_diet": {
                "printemps": "herbes, insectes, charognes",
                "ete": "baies, insectes, poissons",
                "automne": "glands, baies, noix (hyperphagie)",
                "hiver": "hibernation",
            },
        },

        "behavior": {
            "activity_pattern": "crepuscular_nocturnal",
            "peak_hours": ["04:30-07:00", "18:00-21:00"],
            "social": "solitary",
            "rut_period": "juin-juillet",
            "sensitivity_to_pressure": "high",
            "flight_distance_m": 300,
            "nocturnal_shift_threshold": 35,
            "temperature_optimal_c": [5, 25],
            "wind_sensitivity": "low",
            "moon_sensitivity": "low",
        },

        "predictions": {
            "base_success_rate": 0.35,
            "temp_bonus": {"range": [10, 25], "bonus": 0.10},
            "pressure_rising_bonus": 0.05,
            "solunar_major_bonus": 0.08,
            "low_wind_bonus": 0.03,
            "rut_bonus": 0.15,
            "rain_light_bonus": 0.04,
            "full_moon_penalty": -0.05,
            "high_pressure_penalty": -0.12,
        },

        "hunting": {
            "seasons": {
                "printemps": "mai-juin",
                "automne": "septembre-novembre",
            },
            "techniques": ["appat", "affut", "chiens", "approche"],
            "registration_required": True,
            "permits_required": ["permis_gros_gibier", "cesp_ours"],
            "bag_limit": 1,
            "jurisdiction_portals": {
                "QC": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse",
            },
        },
    },

    # ──────────────────────────────────────────────────────
    # DINDON SAUVAGE (Wild Turkey)
    # ──────────────────────────────────────────────────────
    "dindon_sauvage": {
        "id": "dindon_sauvage",
        "name_fr": "Dindon sauvage",
        "name_en": "Wild Turkey",
        "name_latin": "Meleagris gallopavo",
        "category": "petit_gibier",
        "icon": "turkey",
        "color": "#8B0000",
        "map_color": "#B22222",

        "ecology": {
            "habitat_primary": ["foret_feuillue", "lisiere", "terres_agricoles"],
            "habitat_secondary": ["verger", "friche", "chenaie"],
            "altitude_range_m": [0, 600],
            "home_range_km2": {"male": 4, "female": 2},
            "preferred_canopy_pct": [30, 70],
            "water_dependency": "low",
            "edge_habitat_preference": "very_high",
        },

        "diet": {
            "type": "omnivore_granivore",
            "primary_foods": ["glands", "noix", "graines", "insectes", "baies"],
            "secondary_foods": ["herbes", "mais", "soja", "petits_reptiles"],
            "mineral_needs": {"sodium": "low", "calcium": "moderate", "phosphorus": "moderate", "magnesium": "low"},
            "daily_intake_kg": 0.4,
            "saline_attraction": "low",
            "seasonal_diet": {
                "printemps": "insectes, herbes, graines",
                "ete": "insectes, baies, herbes",
                "automne": "glands, noix, mais",
                "hiver": "glands, graines, ecorces",
            },
        },

        "behavior": {
            "activity_pattern": "diurnal",
            "peak_hours": ["06:00-10:00", "15:00-18:00"],
            "social": "flocks",
            "rut_period": "avril-mai",
            "sensitivity_to_pressure": "very_high",
            "flight_distance_m": 100,
            "nocturnal_shift_threshold": 30,
            "temperature_optimal_c": [5, 30],
            "wind_sensitivity": "moderate",
            "moon_sensitivity": "low",
        },

        "predictions": {
            "base_success_rate": 0.30,
            "temp_bonus": {"range": [5, 20], "bonus": 0.15},
            "pressure_rising_bonus": 0.08,
            "solunar_major_bonus": 0.06,
            "low_wind_bonus": 0.12,
            "rut_bonus": 0.35,
            "rain_light_bonus": -0.05,
            "full_moon_penalty": -0.03,
            "high_pressure_penalty": -0.20,
        },

        "hunting": {
            "seasons": {"printemps": "mai", "automne": "octobre"},
            "techniques": ["appel", "affut", "approche", "leurre"],
            "registration_required": True,
            "permits_required": ["permis_petit_gibier", "cesp_dindon"],
            "bag_limit": 2,
            "jurisdiction_portals": {
                "QC": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse",
            },
        },
    },

    # ──────────────────────────────────────────────────────
    # CARIBOU (Caribou / Woodland Caribou)
    # ──────────────────────────────────────────────────────
    "caribou": {
        "id": "caribou",
        "name_fr": "Caribou",
        "name_en": "Woodland Caribou",
        "name_latin": "Rangifer tarandus caribou",
        "category": "gros_gibier",
        "icon": "caribou",
        "color": "#696969",
        "map_color": "#808080",

        "ecology": {
            "habitat_primary": ["toundra", "foret_boreale", "tourbiere"],
            "habitat_secondary": ["pessiere", "lande_alpine", "muskegs"],
            "altitude_range_m": [0, 1500],
            "home_range_km2": {"male": 500, "female": 300},
            "preferred_canopy_pct": [10, 50],
            "water_dependency": "moderate",
            "edge_habitat_preference": "low",
        },

        "diet": {
            "type": "herbivore_browser",
            "primary_foods": ["lichens", "mousses", "herbes_arctiques", "saules_nains"],
            "secondary_foods": ["champignons", "carex", "feuilles_bouleau_nain"],
            "mineral_needs": {"sodium": "high", "calcium": "high", "phosphorus": "high", "magnesium": "moderate"},
            "daily_intake_kg": 5,
            "saline_attraction": "high",
            "seasonal_diet": {
                "printemps": "herbes, carex, bourgeons",
                "ete": "herbes, feuilles, champignons",
                "automne": "lichens, champignons, feuilles",
                "hiver": "lichens_arboricoles, mousses",
            },
        },

        "behavior": {
            "activity_pattern": "diurnal",
            "peak_hours": ["06:00-10:00", "14:00-17:00"],
            "social": "herds",
            "rut_period": "octobre",
            "sensitivity_to_pressure": "very_high",
            "flight_distance_m": 500,
            "nocturnal_shift_threshold": 25,
            "temperature_optimal_c": [-20, 10],
            "wind_sensitivity": "moderate",
            "moon_sensitivity": "low",
        },

        "predictions": {
            "base_success_rate": 0.25,
            "temp_bonus": {"range": [-15, 5], "bonus": 0.12},
            "pressure_rising_bonus": 0.06,
            "solunar_major_bonus": 0.05,
            "low_wind_bonus": 0.08,
            "rut_bonus": 0.20,
            "rain_light_bonus": 0.03,
            "full_moon_penalty": -0.04,
            "high_pressure_penalty": -0.22,
        },

        "hunting": {
            "seasons": {"automne": "septembre-octobre (zones specifiques)"},
            "techniques": ["approche", "affut", "traque"],
            "registration_required": True,
            "permits_required": ["permis_gros_gibier", "cesp_caribou", "tirage_au_sort"],
            "bag_limit": 1,
            "legal_note": "Chasse restreinte ou interdite dans certaines zones (population menacee). Verifier reglementation locale.",
            "jurisdiction_portals": {
                "QC": "https://www.quebec.ca/tourisme-et-loisirs/activites-sportives-et-de-plein-air/chasse",
            },
        },
    },

    # ──────────────────────────────────────────────────────
    # WAPITI / ELK
    # ──────────────────────────────────────────────────────
    "wapiti": {
        "id": "wapiti",
        "name_fr": "Wapiti (Elk)",
        "name_en": "Elk",
        "name_latin": "Cervus canadensis",
        "category": "gros_gibier",
        "icon": "elk",
        "color": "#B8860B",
        "map_color": "#DAA520",

        "ecology": {
            "habitat_primary": ["prairie_montagne", "foret_mixte", "lisiere_alpine"],
            "habitat_secondary": ["vallee_fluviale", "coupe_forestiere", "paturage"],
            "altitude_range_m": [200, 3000],
            "home_range_km2": {"male": 50, "female": 20},
            "preferred_canopy_pct": [20, 60],
            "water_dependency": "high",
            "edge_habitat_preference": "high",
        },

        "diet": {
            "type": "herbivore_grazer_browser",
            "primary_foods": ["herbes", "carex", "saules", "trembles"],
            "secondary_foods": ["ecorces", "lichens", "fougeres", "baies"],
            "mineral_needs": {"sodium": "very_high", "calcium": "very_high", "phosphorus": "high", "magnesium": "high"},
            "daily_intake_kg": 10,
            "saline_attraction": "very_high",
            "seasonal_diet": {
                "printemps": "herbes_vertes, carex, bourgeons",
                "ete": "herbes, feuilles, plantes_aquatiques",
                "automne": "herbes, ecorces, champignons",
                "hiver": "ecorces, brout_ligneux, herbes_seches",
            },
        },

        "behavior": {
            "activity_pattern": "crepuscular",
            "peak_hours": ["05:00-08:00", "17:00-20:00"],
            "social": "herds",
            "rut_period": "septembre-octobre",
            "sensitivity_to_pressure": "moderate",
            "flight_distance_m": 400,
            "nocturnal_shift_threshold": 50,
            "temperature_optimal_c": [-10, 20],
            "wind_sensitivity": "moderate",
            "moon_sensitivity": "moderate",
        },

        "predictions": {
            "base_success_rate": 0.35,
            "temp_bonus": {"range": [-5, 15], "bonus": 0.12},
            "pressure_rising_bonus": 0.08,
            "solunar_major_bonus": 0.10,
            "low_wind_bonus": 0.06,
            "rut_bonus": 0.28,
            "rain_light_bonus": 0.04,
            "full_moon_penalty": -0.06,
            "high_pressure_penalty": -0.15,
        },

        "hunting": {
            "seasons": {"arc": "septembre", "arme_a_feu": "octobre-novembre"},
            "techniques": ["appel_bugle", "affut", "approche", "traque"],
            "registration_required": True,
            "permits_required": ["permis_gros_gibier", "cesp_wapiti", "tirage_au_sort"],
            "bag_limit": 1,
            "jurisdiction_portals": {
                "AB": "https://www.alberta.ca/hunting-regulations",
                "BC": "https://www2.gov.bc.ca/gov/content/sports-culture/recreation/fishing-hunting/hunting",
            },
        },
    },

    # ──────────────────────────────────────────────────────
    # CERF MULET (Mule Deer)
    # ──────────────────────────────────────────────────────
    "cerf_mulet": {
        "id": "cerf_mulet",
        "name_fr": "Cerf mulet",
        "name_en": "Mule Deer",
        "name_latin": "Odocoileus hemionus",
        "category": "gros_gibier",
        "icon": "mule_deer",
        "color": "#C4A35A",
        "map_color": "#D4A76A",

        "ecology": {
            "habitat_primary": ["prairie_semi_aride", "foret_conifere", "collines_rocheuses"],
            "habitat_secondary": ["broussailles", "desert_haut", "lisiere_agricole"],
            "altitude_range_m": [300, 3500],
            "home_range_km2": {"male": 15, "female": 5},
            "preferred_canopy_pct": [20, 60],
            "water_dependency": "moderate",
            "edge_habitat_preference": "high",
        },

        "diet": {
            "type": "herbivore_browser",
            "primary_foods": ["armoise", "broussailles", "herbes_seches", "glands"],
            "secondary_foods": ["baies", "cactus", "fougeres", "ecorces"],
            "mineral_needs": {"sodium": "moderate", "calcium": "high", "phosphorus": "moderate", "magnesium": "moderate"},
            "daily_intake_kg": 3.5,
            "saline_attraction": "moderate",
            "seasonal_diet": {
                "printemps": "herbes_vertes, bourgeons, fleurs",
                "ete": "herbes, feuilles, baies",
                "automne": "glands, broussailles, champignons",
                "hiver": "armoise, brout_ligneux, ecorces",
            },
        },

        "behavior": {
            "activity_pattern": "crepuscular",
            "peak_hours": ["05:00-07:30", "17:00-19:30"],
            "social": "small_groups",
            "rut_period": "novembre-decembre",
            "sensitivity_to_pressure": "moderate",
            "flight_distance_m": 250,
            "nocturnal_shift_threshold": 50,
            "temperature_optimal_c": [-5, 25],
            "wind_sensitivity": "moderate",
            "moon_sensitivity": "moderate",
        },

        "predictions": {
            "base_success_rate": 0.38,
            "temp_bonus": {"range": [0, 20], "bonus": 0.10},
            "pressure_rising_bonus": 0.10,
            "solunar_major_bonus": 0.10,
            "low_wind_bonus": 0.08,
            "rut_bonus": 0.25,
            "rain_light_bonus": 0.05,
            "full_moon_penalty": -0.07,
            "high_pressure_penalty": -0.14,
        },

        "hunting": {
            "seasons": {"arc": "septembre", "arme_a_feu": "octobre-novembre"},
            "techniques": ["approche_spot_stalk", "affut", "traque"],
            "registration_required": True,
            "permits_required": ["permis_gros_gibier", "cesp_cerf_mulet"],
            "bag_limit": 2,
            "jurisdiction_portals": {
                "AB": "https://www.alberta.ca/hunting-regulations",
                "BC": "https://www2.gov.bc.ca/gov/content/sports-culture/recreation/fishing-hunting/hunting",
                "SK": "https://www.saskatchewan.ca/residents/parks-culture-and-sport/hunting-and-trapping",
            },
        },
    },

    # ──────────────────────────────────────────────────────
    # ANTILOCAPRE / PRONGHORN
    # ──────────────────────────────────────────────────────
    "pronghorn": {
        "id": "pronghorn",
        "name_fr": "Antilocapre (Pronghorn)",
        "name_en": "Pronghorn",
        "name_latin": "Antilocapra americana",
        "category": "gros_gibier",
        "icon": "pronghorn",
        "color": "#DEB887",
        "map_color": "#F5DEB3",

        "ecology": {
            "habitat_primary": ["prairie_ouverte", "steppe", "plaine_semi_aride"],
            "habitat_secondary": ["desert_haut", "paturage_ouvert"],
            "altitude_range_m": [500, 2500],
            "home_range_km2": {"male": 20, "female": 10},
            "preferred_canopy_pct": [0, 15],
            "water_dependency": "low",
            "edge_habitat_preference": "low",
        },

        "diet": {
            "type": "herbivore_browser_grazer",
            "primary_foods": ["armoise", "herbes_prairie", "fleurs_sauvages"],
            "secondary_foods": ["cactus", "broussailles_basses"],
            "mineral_needs": {"sodium": "low", "calcium": "moderate", "phosphorus": "low", "magnesium": "low"},
            "daily_intake_kg": 2.5,
            "saline_attraction": "low",
            "seasonal_diet": {
                "printemps": "herbes_vertes, fleurs",
                "ete": "herbes, fleurs, broussailles",
                "automne": "armoise, herbes_seches",
                "hiver": "armoise, broussailles",
            },
        },

        "behavior": {
            "activity_pattern": "diurnal",
            "peak_hours": ["06:00-10:00", "15:00-18:00"],
            "social": "herds",
            "rut_period": "septembre-octobre",
            "sensitivity_to_pressure": "very_high",
            "flight_distance_m": 800,
            "nocturnal_shift_threshold": 20,
            "temperature_optimal_c": [-10, 30],
            "wind_sensitivity": "low",
            "moon_sensitivity": "low",
        },

        "predictions": {
            "base_success_rate": 0.40,
            "temp_bonus": {"range": [5, 25], "bonus": 0.08},
            "pressure_rising_bonus": 0.05,
            "solunar_major_bonus": 0.04,
            "low_wind_bonus": 0.06,
            "rut_bonus": 0.18,
            "rain_light_bonus": 0.02,
            "full_moon_penalty": -0.03,
            "high_pressure_penalty": -0.15,
        },

        "hunting": {
            "seasons": {"arme_a_feu": "octobre", "arc": "septembre"},
            "techniques": ["approche_spot_stalk", "affut_point_eau", "decoy"],
            "registration_required": True,
            "permits_required": ["permis_gros_gibier", "cesp_pronghorn", "tirage_au_sort"],
            "bag_limit": 1,
            "jurisdiction_portals": {
                "AB": "https://www.alberta.ca/hunting-regulations",
                "SK": "https://www.saskatchewan.ca/residents/parks-culture-and-sport/hunting-and-trapping",
            },
        },
    },
}


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_all_species() -> List[Dict[str, Any]]:
    """Retourne la liste complete des especes avec infos de base."""
    return [
        {
            "id": sp["id"],
            "name_fr": sp["name_fr"],
            "name_en": sp["name_en"],
            "name_latin": sp["name_latin"],
            "category": sp["category"],
            "color": sp["color"],
            "map_color": sp["map_color"],
        }
        for sp in SPECIES_PROFILES.values()
    ]


def get_species_profile(species_id: str) -> Dict[str, Any]:
    """Retourne le profil complet d'une espece."""
    return SPECIES_PROFILES.get(species_id, SPECIES_PROFILES.get("orignal"))


def get_species_ids() -> List[str]:
    """Retourne la liste des IDs d'especes."""
    return list(SPECIES_PROFILES.keys())


def get_species_for_predictions(species_id: str = None) -> List[str]:
    """Retourne les especes a inclure dans les predictions."""
    if species_id and species_id in SPECIES_PROFILES:
        return [species_id]
    return list(SPECIES_PROFILES.keys())


def get_prediction_params(species_id: str) -> Dict[str, Any]:
    """Retourne les parametres de prediction pour une espece."""
    profile = get_species_profile(species_id)
    return profile.get("predictions", {})


def get_species_behavior(species_id: str) -> Dict[str, Any]:
    """Retourne le profil comportemental d'une espece."""
    profile = get_species_profile(species_id)
    return profile.get("behavior", {})


def get_species_ecology(species_id: str) -> Dict[str, Any]:
    """Retourne le profil ecologique d'une espece."""
    profile = get_species_profile(species_id)
    return profile.get("ecology", {})


def get_species_diet(species_id: str) -> Dict[str, Any]:
    """Retourne le profil alimentaire d'une espece."""
    profile = get_species_profile(species_id)
    return profile.get("diet", {})


def get_species_hunting(species_id: str) -> Dict[str, Any]:
    """Retourne les infos de chasse d'une espece."""
    profile = get_species_profile(species_id)
    return profile.get("hunting", {})


# Total species count
TOTAL_SPECIES = len(SPECIES_PROFILES)
