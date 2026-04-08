"""
RSF ENGINE — Coefficients beta par espece (13 covariables)
===========================================================
BCE-4X ULTIME ABSOLU x3 — COMMANDANT STEEVE-MAX
Chaque espece a un vecteur de coefficients calibres sur la litterature scientifique.
w(x) = exp(beta1*x1 + beta2*x2 + ... + betaN*xN)
"""

RSF_COEFFICIENTS = {
    "CERF": {
        "couvert_conifere": -0.15,
        "couvert_feuillu": 0.45,
        "couvert_mixte": 0.30,
        "lisiere_100m": 0.65,
        "friche_regeneration": 0.55,
        "culture_proximite": 0.40,
        "distance_eau_log": -0.20,
        "distance_route_log": 0.35,
        "pente_deg": -0.08,
        "altitude_m": -0.005,
        "densite_route_km2": -0.45,
        "marecage": -0.10,
        "exposition_sud": 0.25,
    },
    "ORIGNAL": {
        "couvert_conifere": 0.35,
        "couvert_feuillu": 0.15,
        "couvert_mixte": 0.40,
        "lisiere_100m": 0.20,
        "friche_regeneration": 0.60,
        "culture_proximite": -0.30,
        "distance_eau_log": -0.55,
        "distance_route_log": 0.50,
        "pente_deg": -0.04,
        "altitude_m": 0.002,
        "densite_route_km2": -0.60,
        "marecage": 0.45,
        "exposition_sud": 0.10,
    },
    "OURS": {
        "couvert_conifere": 0.20,
        "couvert_feuillu": 0.40,
        "couvert_mixte": 0.35,
        "lisiere_100m": 0.15,
        "friche_regeneration": 0.70,
        "culture_proximite": 0.20,
        "distance_eau_log": -0.30,
        "distance_route_log": 0.40,
        "pente_deg": 0.05,
        "altitude_m": 0.003,
        "densite_route_km2": -0.55,
        "marecage": 0.10,
        "exposition_sud": 0.15,
    },
    "DINDON": {
        "couvert_conifere": -0.20,
        "couvert_feuillu": 0.55,
        "couvert_mixte": 0.30,
        "lisiere_100m": 0.50,
        "friche_regeneration": 0.25,
        "culture_proximite": 0.45,
        "distance_eau_log": -0.15,
        "distance_route_log": 0.20,
        "pente_deg": -0.12,
        "altitude_m": -0.008,
        "densite_route_km2": -0.30,
        "marecage": -0.25,
        "exposition_sud": 0.30,
    },
    "WAPITI": {
        "couvert_conifere": 0.10,
        "couvert_feuillu": 0.25,
        "couvert_mixte": 0.35,
        "lisiere_100m": 0.40,
        "friche_regeneration": 0.45,
        "culture_proximite": 0.15,
        "distance_eau_log": -0.35,
        "distance_route_log": 0.45,
        "pente_deg": -0.03,
        "altitude_m": 0.004,
        "densite_route_km2": -0.50,
        "marecage": 0.05,
        "exposition_sud": 0.20,
    },
}

BREEDING_PERIODS = {
    "CERF": {
        "pre_rut": {"mois": [9, 10], "mobilite": 1.3, "agressivite": 0.6},
        "rut": {"mois": [11], "mobilite": 1.8, "agressivite": 1.0},
        "post_rut": {"mois": [12], "mobilite": 0.6, "agressivite": 0.2},
    },
    "ORIGNAL": {
        "pre_rut": {"mois": [8, 9], "mobilite": 1.2, "agressivite": 0.5},
        "rut": {"mois": [9, 10], "mobilite": 1.6, "agressivite": 1.0},
        "post_rut": {"mois": [11], "mobilite": 0.5, "agressivite": 0.1},
    },
    "OURS": {
        "pre_rut": {"mois": [5], "mobilite": 1.1, "agressivite": 0.4},
        "rut": {"mois": [6, 7], "mobilite": 1.5, "agressivite": 0.8},
        "post_rut": {"mois": [8], "mobilite": 0.9, "agressivite": 0.2},
        "hyperphagie": {"mois": [9, 10, 11], "mobilite": 1.4, "alimentation": 2.5},
        "hibernation": {"mois": [12, 1, 2, 3], "mobilite": 0.01, "alimentation": 0.0},
    },
    "DINDON": {
        "pre_rut": {"mois": [3], "mobilite": 1.1, "vocalisation": 0.6},
        "rut": {"mois": [4, 5], "mobilite": 1.3, "vocalisation": 1.0},
        "post_rut": {"mois": [6], "mobilite": 0.8, "vocalisation": 0.2},
        "elevage": {"mois": [6, 7, 8], "mobilite": 0.5, "couvert": 1.5},
    },
    "WAPITI": {
        "pre_rut": {"mois": [8], "mobilite": 1.2, "bugling": 0.5},
        "rut": {"mois": [9, 10], "mobilite": 1.7, "bugling": 1.0},
        "post_rut": {"mois": [11], "mobilite": 0.6, "bugling": 0.1},
    },
}

SPECIES_DISTURBANCE_TOLERANCE = {
    "CERF":    {"route_buffer_m": 150, "batiment_buffer_m": 200, "sentier_buffer_m": 80, "sensibilite": 0.75},
    "ORIGNAL": {"route_buffer_m": 300, "batiment_buffer_m": 400, "sentier_buffer_m": 150, "sensibilite": 0.80},
    "OURS":    {"route_buffer_m": 200, "batiment_buffer_m": 300, "sentier_buffer_m": 120, "sensibilite": 0.85},
    "DINDON":  {"route_buffer_m": 100, "batiment_buffer_m": 150, "sentier_buffer_m": 60, "sensibilite": 0.65},
    "WAPITI":  {"route_buffer_m": 250, "batiment_buffer_m": 350, "sentier_buffer_m": 130, "sensibilite": 0.70},
}

SPECIES_WATER_DEPENDENCY = {
    "CERF":    {"distance_optimale_m": 200, "penalite_max": 0.25, "affinite": 0.60},
    "ORIGNAL": {"distance_optimale_m": 100, "penalite_max": 0.50, "affinite": 0.85},
    "OURS":    {"distance_optimale_m": 300, "penalite_max": 0.15, "affinite": 0.50},
    "DINDON":  {"distance_optimale_m": 400, "penalite_max": 0.10, "affinite": 0.35},
    "WAPITI":  {"distance_optimale_m": 250, "penalite_max": 0.30, "affinite": 0.55},
}

SPECIES_THERMAL_PREFERENCE = {
    "CERF":    {"temp_confort_min": -15, "temp_confort_max": 25, "sensibilite_chaleur": 0.6},
    "ORIGNAL": {"temp_confort_min": -30, "temp_confort_max": 15, "sensibilite_chaleur": 0.9},
    "OURS":    {"temp_confort_min": -10, "temp_confort_max": 30, "sensibilite_chaleur": 0.4},
    "DINDON":  {"temp_confort_min": -20, "temp_confort_max": 30, "sensibilite_chaleur": 0.3},
    "WAPITI":  {"temp_confort_min": -25, "temp_confort_max": 20, "sensibilite_chaleur": 0.7},
}

SPECIES_CIRCADIAN = {
    "CERF":    {"type": "crepusculaire", "pic_activite": [5, 6, 17, 18, 19], "repos": [11, 12, 13, 14, 1, 2, 3]},
    "ORIGNAL": {"type": "crepusculaire", "pic_activite": [4, 5, 6, 18, 19, 20], "repos": [11, 12, 13, 14, 0, 1, 2]},
    "OURS":    {"type": "diurne", "pic_activite": [7, 8, 9, 10, 15, 16, 17], "repos": [22, 23, 0, 1, 2, 3, 4]},
    "DINDON":  {"type": "diurne", "pic_activite": [6, 7, 8, 9, 15, 16, 17], "repos": [20, 21, 22, 23, 0, 1, 2, 3, 4]},
    "WAPITI":  {"type": "crepusculaire", "pic_activite": [5, 6, 7, 17, 18, 19], "repos": [11, 12, 13, 0, 1, 2, 3]},
}

SALINE_POSITIONING_PROFILES = {
    "CERF": {
        "eau_optimal_m": (100, 250),
        "eau_penalite_m": 400,
        "couvert_optimal_pct": (30, 50),
        "pente_optimal_deg": (0, 8),
        "distance_route_min_m": 150,
        "vegetation_preference": "lisiere_mixte",
        "topographie_preference": "plateau_replat",
        "espacement_salines_m": 250,
    },
    "ORIGNAL": {
        "eau_optimal_m": (30, 80),
        "eau_penalite_m": 200,
        "couvert_optimal_pct": (60, 80),
        "pente_optimal_deg": (5, 15),
        "distance_route_min_m": 300,
        "vegetation_preference": "regeneration_conifere",
        "topographie_preference": "fond_vallee",
        "espacement_salines_m": 500,
    },
    "WAPITI": {
        "eau_optimal_m": (80, 200),
        "eau_penalite_m": 350,
        "couvert_optimal_pct": (20, 40),
        "pente_optimal_deg": (3, 12),
        "distance_route_min_m": 250,
        "vegetation_preference": "prairie_clairiere",
        "topographie_preference": "plaine",
        "espacement_salines_m": 400,
    },
}
