"""
ALIMENTATION-V1 — Profils d'espèces
=====================================
5 profils: CERF, ORIGNAL, OURS, DINDON, WAPITI
Chaque profil définit les sources nutritionnelles, sécurité et effort.
"""

ALIM_PROFILES = {
    "CERF": {
        "id": "cerf",
        "nom_fr": "Cerf de Virginie",
        "nom_scientifique": "Odocoileus virginianus",
        "sources_proteines": {
            "friches": 0.85,
            "legumineuses": 0.90,
            "arbustes": 0.80,
            "jeunes_feuillus_1_3m": 0.75,
            "herbes": 0.60,
        },
        "sources_energie": {
            "mast_chene": 0.95,
            "mast_hetre": 0.90,
            "mast_pommier": 0.85,
            "cultures_energetiques": 0.70,
            "glands": 0.92,
        },
        "sources_mineraux": {
            "jeunes_feuillus_ca_p": 0.80,
            "zones_humides_na": 0.75,
            "sols_calcaires": 0.60,
        },
        "securite": {
            "couvert_coniferien_dense_150m": 0.90,
            "lisieres": 0.85,
            "distance_route_min_m": 150,
            "distance_batiment_min_m": 200,
        },
        "effort": {
            "pente_optimale_deg": 5,
            "pente_max_deg": 15,
            "tolerance_obstacles": 0.3,
        },
        "saisonnalite": {
            "printemps": {"proteines": 0.85, "energie": 0.50, "mineraux": 0.90},
            "ete": {"proteines": 0.90, "energie": 0.60, "mineraux": 0.70},
            "automne": {"proteines": 0.60, "energie": 0.95, "mineraux": 0.50},
            "hiver": {"proteines": 0.40, "energie": 0.90, "mineraux": 0.30},
        },
    },
    "ORIGNAL": {
        "id": "orignal",
        "nom_fr": "Orignal",
        "nom_scientifique": "Alces americanus",
        "sources_proteines": {
            "jeunes_feuillus_bouleau": 0.90,
            "jeunes_feuillus_saule": 0.95,
            "vegetation_aquatique": 0.85,
            "repousses_ligneuses": 0.75,
        },
        "sources_energie": {
            "repousses_ligneuses": 0.80,
            "mast_secondaire": 0.55,
            "ecorce": 0.60,
            "vegetation_aquatique": 0.70,
        },
        "sources_mineraux": {
            "zones_humides_na": 0.95,
            "suintements": 0.90,
            "salines_naturelles": 0.85,
        },
        "securite": {
            "grands_massifs_forestiers": 0.85,
            "distance_route_min_m": 300,
            "distance_batiment_min_m": 400,
            "couvert_dense": 0.70,
        },
        "effort": {
            "pente_optimale_deg": 8,
            "pente_max_deg": 25,
            "tolerance_obstacles": 0.6,
        },
        "saisonnalite": {
            "printemps": {"proteines": 0.90, "energie": 0.50, "mineraux": 0.95},
            "ete": {"proteines": 0.85, "energie": 0.55, "mineraux": 0.80},
            "automne": {"proteines": 0.65, "energie": 0.85, "mineraux": 0.60},
            "hiver": {"proteines": 0.35, "energie": 0.90, "mineraux": 0.30},
        },
    },
    "OURS": {
        "id": "ours",
        "nom_fr": "Ours noir",
        "nom_scientifique": "Ursus americanus",
        "sources_proteines": {
            "insectes": 0.85,
            "herbacees_printanieres": 0.80,
            "larves": 0.75,
            "charognes": 0.65,
        },
        "sources_energie": {
            "baies": 0.95,
            "fruits": 0.90,
            "mast_glands": 0.85,
            "mais_hyperphagie": 0.92,
            "miel": 0.80,
        },
        "sources_mineraux": {
            "faible_ponderation": 0.30,
            "sols_riches": 0.40,
        },
        "securite": {
            "couvert_dense": 0.90,
            "eloignement_humain": 0.95,
            "distance_route_min_m": 200,
            "distance_batiment_min_m": 300,
        },
        "effort": {
            "pente_optimale_deg": 12,
            "pente_max_deg": 35,
            "tolerance_obstacles": 0.8,
        },
        "saisonnalite": {
            "printemps": {"proteines": 0.90, "energie": 0.40, "mineraux": 0.30},
            "ete": {"proteines": 0.70, "energie": 0.85, "mineraux": 0.25},
            "automne": {"proteines": 0.50, "energie": 0.98, "mineraux": 0.20},
            "hiver": {"proteines": 0.10, "energie": 0.10, "mineraux": 0.05},
        },
    },
    "DINDON": {
        "id": "dindon",
        "nom_fr": "Dindon sauvage",
        "nom_scientifique": "Meleagris gallopavo",
        "sources_proteines": {
            "insectes": 0.90,
            "herbes": 0.75,
            "graines": 0.80,
            "invertebres": 0.70,
        },
        "sources_energie": {
            "cereales": 0.90,
            "glands": 0.95,
            "fruits": 0.80,
            "mais": 0.85,
        },
        "sources_mineraux": {
            "sols_nus": 0.80,
            "zones_grattage": 0.85,
            "gravier": 0.75,
        },
        "securite": {
            "mosaique_lisiere_bosquets": 0.90,
            "perchoirs": 0.95,
            "distance_route_min_m": 100,
            "distance_batiment_min_m": 150,
        },
        "effort": {
            "pente_optimale_deg": 3,
            "pente_max_deg": 12,
            "tolerance_obstacles": 0.2,
        },
        "saisonnalite": {
            "printemps": {"proteines": 0.90, "energie": 0.60, "mineraux": 0.70},
            "ete": {"proteines": 0.85, "energie": 0.70, "mineraux": 0.60},
            "automne": {"proteines": 0.65, "energie": 0.95, "mineraux": 0.55},
            "hiver": {"proteines": 0.30, "energie": 0.85, "mineraux": 0.40},
        },
    },
    "WAPITI": {
        "id": "wapiti",
        "nom_fr": "Wapiti",
        "nom_scientifique": "Cervus canadensis",
        "sources_proteines": {
            "herbacees": 0.90,
            "graminees": 0.85,
            "jeunes_pousses": 0.80,
            "arbustes": 0.75,
        },
        "sources_energie": {
            "mast_glands": 0.85,
            "mast_hetre": 0.80,
            "cultures_energetiques_mais": 0.90,
            "cereales": 0.85,
        },
        "sources_mineraux": {
            "jeunes_feuillus_ca_p": 0.80,
            "zones_humides_na": 0.75,
            "salines_naturelles": 0.70,
        },
        "securite": {
            "mosaique_foret_lisiere_clairiere": 0.85,
            "vigilance_elevee": 0.90,
            "distance_route_min_m": 250,
            "distance_batiment_min_m": 350,
        },
        "effort": {
            "pente_optimale_deg": 8,
            "pente_max_deg": 22,
            "tolerance_obstacles": 0.5,
        },
        "saisonnalite": {
            "printemps": {"proteines": 0.90, "energie": 0.50, "mineraux": 0.85},
            "ete": {"proteines": 0.85, "energie": 0.60, "mineraux": 0.70},
            "automne": {"proteines": 0.60, "energie": 0.90, "mineraux": 0.55},
            "hiver": {"proteines": 0.35, "energie": 0.85, "mineraux": 0.30},
        },
    },
    # P22ΩΩ_ADD_COYOTE_TO_MULTI_SPECIES_Ω (2026-05-21 · COMMANDANT STEEVE-MAX)
    # Coyote (Canis latrans) — carnivore opportuniste, régime omnivore strict :
    # micromammifères, ongulés (charogne / faons), petits gibiers, fruits sauvages
    # automne. AUCUNE saline doctrinale (carnivore — recettes minérales n/a) :
    # `sources_mineraux` reste défini par cohérence structurelle mais à scores faibles.
    "COYOTE": {
        "id": "coyote",
        "nom_fr": "Coyote",
        "nom_scientifique": "Canis latrans",
        "sources_proteines": {
            "micromammiferes": 0.95,
            "charogne_ongules": 0.85,
            "faons_chevreuil": 0.80,
            "petits_gibiers": 0.75,
            "insectes": 0.40,
        },
        "sources_energie": {
            "fruits_sauvages_automne": 0.70,
            "charogne_grosse": 0.85,
            "dechets_anthropiques": 0.50,
        },
        "sources_mineraux": {
            "os_charogne_ca": 0.40,
            "sols_nus": 0.10,
        },
        "securite": {
            "lisiere_friche_taillis": 0.90,
            "vigilance_haute": 0.95,
            "distance_route_min_m": 50,
            "distance_batiment_min_m": 100,
        },
        "effort": {
            "pente_optimale_deg": 12,
            "pente_max_deg": 35,
            "tolerance_obstacles": 0.80,
        },
        "saisonnalite": {
            "printemps": {"proteines": 0.95, "energie": 0.55, "mineraux": 0.30},
            "ete": {"proteines": 0.90, "energie": 0.60, "mineraux": 0.25},
            "automne": {"proteines": 0.80, "energie": 0.85, "mineraux": 0.30},
            "hiver": {"proteines": 0.95, "energie": 0.90, "mineraux": 0.25},
        },
    },
}

SPECIES_LIST = list(ALIM_PROFILES.keys())

# x3205: Importe depuis common/seasons.py (source unique)
from core.scoring_pipeline.common.seasons import MONTH_TO_SEASON, get_season  # noqa: F401


def get_profile(species: str) -> dict:
    return ALIM_PROFILES.get(species.upper(), ALIM_PROFILES["CERF"])
