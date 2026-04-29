"""
V8-NATIONAL — Referentiels nationaux pancanadiens
=====================================================
9 biomes, 6 regimes fauniques, 4 regimes de neige, 5 regimes forestiers.
Normalisation inter-provinciale pour 10 provinces + 3 territoires.
"""

# ═══════════════════════════════════════════════════════
# 9 BIOMES CANADIENS
# ═══════════════════════════════════════════════════════

BIOMES = {
    "boreal_coniferous": {
        "name": "Boreal conifere",
        "provinces": ["qc", "on", "mb", "sk", "ab", "bc", "nl", "yt", "nt"],
        "ndvi_range": [0.35, 0.65], "canopy_range": [8, 22],
        "dominant_species": ["orignal", "ours_noir", "caribou"],
        "soil_orders": ["podzol", "luvisol", "organic"],
        "snow_regime": "continental", "fire_cycle_yr": 80,
    },
    "boreal_mixed": {
        "name": "Boreal mixte",
        "provinces": ["qc", "on", "nb", "ns", "nl", "pei"],
        "ndvi_range": [0.40, 0.70], "canopy_range": [10, 25],
        "dominant_species": ["cerf", "orignal", "ours_noir", "dindon_sauvage"],
        "soil_orders": ["podzol", "luvisol", "brunisol"],
        "snow_regime": "maritime_continental", "fire_cycle_yr": 150,
    },
    "temperate_deciduous": {
        "name": "Tempere decidue",
        "provinces": ["on", "qc", "nb", "ns", "pei"],
        "ndvi_range": [0.50, 0.80], "canopy_range": [15, 30],
        "dominant_species": ["cerf", "dindon_sauvage", "ours_noir"],
        "soil_orders": ["luvisol", "brunisol", "gleysol"],
        "snow_regime": "maritime", "fire_cycle_yr": 300,
    },
    "prairie_grassland": {
        "name": "Prairie herbeuse",
        "provinces": ["sk", "ab", "mb"],
        "ndvi_range": [0.25, 0.55], "canopy_range": [0, 5],
        "dominant_species": ["cerf", "wapiti", "antilope"],
        "soil_orders": ["chernozem", "solonetz"],
        "snow_regime": "continental_sec", "fire_cycle_yr": 15,
    },
    "pacific_rainforest": {
        "name": "Foret pluviale pacifique",
        "provinces": ["bc"],
        "ndvi_range": [0.55, 0.85], "canopy_range": [20, 45],
        "dominant_species": ["cerf_mulet", "ours_noir", "wapiti"],
        "soil_orders": ["podzol", "brunisol"],
        "snow_regime": "maritime_doux", "fire_cycle_yr": 250,
    },
    "montane_subalpine": {
        "name": "Montagnard subalpin",
        "provinces": ["bc", "ab", "yt"],
        "ndvi_range": [0.20, 0.50], "canopy_range": [5, 18],
        "dominant_species": ["chevre_montagne", "mouflon", "grizzly", "wapiti"],
        "soil_orders": ["brunisol", "regosol", "cryosol"],
        "snow_regime": "alpin", "fire_cycle_yr": 120,
    },
    "taiga_subarctic": {
        "name": "Taiga subarctique",
        "provinces": ["qc", "on", "mb", "sk", "nt", "yt", "nl"],
        "ndvi_range": [0.15, 0.40], "canopy_range": [2, 10],
        "dominant_species": ["caribou", "orignal"],
        "soil_orders": ["cryosol", "organic"],
        "snow_regime": "subarctique", "fire_cycle_yr": 60,
    },
    "arctic_tundra": {
        "name": "Toundra arctique",
        "provinces": ["nu", "nt", "yt", "qc", "nl"],
        "ndvi_range": [0.02, 0.20], "canopy_range": [0, 1],
        "dominant_species": ["caribou", "boeuf_musque"],
        "soil_orders": ["cryosol"],
        "snow_regime": "arctique", "fire_cycle_yr": 500,
    },
    "atlantic_maritime": {
        "name": "Maritime atlantique",
        "provinces": ["nb", "ns", "pei", "nl"],
        "ndvi_range": [0.40, 0.70], "canopy_range": [12, 22],
        "dominant_species": ["cerf", "orignal", "ours_noir"],
        "soil_orders": ["podzol", "gleysol", "luvisol"],
        "snow_regime": "maritime", "fire_cycle_yr": 200,
    },
}


# ═══════════════════════════════════════════════════════
# 6 REGIMES FAUNIQUES
# ═══════════════════════════════════════════════════════

WILDLIFE_REGIMES = {
    "cervide_tempere": {
        "name": "Cervide tempere",
        "species": ["cerf", "chevreuil"],
        "biomes": ["boreal_mixed", "temperate_deciduous", "atlantic_maritime"],
        "optimal_habitat": {"canopy": [40, 75], "ndvi": [0.45, 0.75], "slope_max": 25},
        "rut_peak_doy": 310, "crepuscular": True,
        "mineral_priority": ["Na", "Ca", "P"],
    },
    "cervide_boreal": {
        "name": "Cervide boreal",
        "species": ["orignal", "caribou"],
        "biomes": ["boreal_coniferous", "taiga_subarctic", "boreal_mixed"],
        "optimal_habitat": {"canopy": [30, 70], "ndvi": [0.30, 0.60], "slope_max": 30},
        "rut_peak_doy": 275, "crepuscular": True,
        "mineral_priority": ["Na", "Ca", "Mg"],
    },
    "cervide_montagnard": {
        "name": "Cervide montagnard",
        "species": ["wapiti", "cerf_mulet"],
        "biomes": ["montane_subalpine", "pacific_rainforest", "prairie_grassland"],
        "optimal_habitat": {"canopy": [20, 60], "ndvi": [0.25, 0.55], "slope_max": 40},
        "rut_peak_doy": 280, "crepuscular": True,
        "mineral_priority": ["Na", "Ca", "P", "Se"],
    },
    "omnivore_forestier": {
        "name": "Omnivore forestier",
        "species": ["ours_noir"],
        "biomes": ["boreal_coniferous", "boreal_mixed", "temperate_deciduous", "pacific_rainforest"],
        "optimal_habitat": {"canopy": [50, 90], "ndvi": [0.40, 0.80], "slope_max": 35},
        "rut_peak_doy": 170, "crepuscular": False,
        "mineral_priority": ["Ca", "Na", "K"],
    },
    "gallinace_forestier": {
        "name": "Gallinace forestier",
        "species": ["dindon_sauvage", "gelinotte"],
        "biomes": ["temperate_deciduous", "boreal_mixed", "atlantic_maritime"],
        "optimal_habitat": {"canopy": [30, 65], "ndvi": [0.45, 0.75], "slope_max": 15},
        "rut_peak_doy": 130, "crepuscular": False,
        "mineral_priority": ["Ca", "P", "K"],
    },
    "arctique_toundra": {
        "name": "Arctique toundra",
        "species": ["caribou", "boeuf_musque"],
        "biomes": ["arctic_tundra", "taiga_subarctic"],
        "optimal_habitat": {"canopy": [0, 15], "ndvi": [0.05, 0.30], "slope_max": 20},
        "rut_peak_doy": 290, "crepuscular": True,
        "mineral_priority": ["Na", "Ca", "Se"],
    },
}


# ═══════════════════════════════════════════════════════
# 4 REGIMES DE NEIGE
# ═══════════════════════════════════════════════════════

SNOW_REGIMES = {
    "maritime": {
        "name": "Maritime",
        "provinces": ["bc", "ns", "nb", "pei", "nl"],
        "avg_depth_cm": 80, "season_months": [11, 12, 1, 2, 3],
        "melt_month": 4, "impact_mobility": 0.15,
    },
    "continental": {
        "name": "Continental",
        "provinces": ["qc", "on", "mb", "sk", "ab"],
        "avg_depth_cm": 120, "season_months": [11, 12, 1, 2, 3, 4],
        "melt_month": 4, "impact_mobility": 0.25,
    },
    "subarctique": {
        "name": "Subarctique",
        "provinces": ["nt", "yt", "nu", "qc", "nl"],
        "avg_depth_cm": 60, "season_months": [10, 11, 12, 1, 2, 3, 4, 5],
        "melt_month": 6, "impact_mobility": 0.35,
    },
    "alpin": {
        "name": "Alpin",
        "provinces": ["bc", "ab", "yt"],
        "avg_depth_cm": 200, "season_months": [10, 11, 12, 1, 2, 3, 4, 5],
        "melt_month": 6, "impact_mobility": 0.40,
    },
}


# ═══════════════════════════════════════════════════════
# 5 REGIMES FORESTIERS
# ═══════════════════════════════════════════════════════

FOREST_REGIMES = {
    "conifere_boreal": {
        "name": "Conifere boreal",
        "dominant": ["epinette_noire", "sapin_baumier", "pin_gris"],
        "canopy_avg": 55, "understory_density": 40,
        "browse_quality": 45, "mast_production": 15,
    },
    "mixte_tempere": {
        "name": "Mixte tempere",
        "dominant": ["erable_sucre", "bouleau_jaune", "sapin", "epinette"],
        "canopy_avg": 65, "understory_density": 55,
        "browse_quality": 70, "mast_production": 60,
    },
    "feuillu_meridional": {
        "name": "Feuillu meridional",
        "dominant": ["chene_rouge", "erable", "hetre", "noyer"],
        "canopy_avg": 75, "understory_density": 50,
        "browse_quality": 80, "mast_production": 75,
    },
    "pluvial_pacifique": {
        "name": "Pluvial pacifique",
        "dominant": ["douglas", "cedre_rouge", "pruche"],
        "canopy_avg": 80, "understory_density": 35,
        "browse_quality": 55, "mast_production": 30,
    },
    "taiga_lichen": {
        "name": "Taiga-lichen",
        "dominant": ["epinette_noire", "meleze", "lichen"],
        "canopy_avg": 20, "understory_density": 60,
        "browse_quality": 30, "mast_production": 5,
    },
}


# ═══════════════════════════════════════════════════════
# SPECIES DATABASE V8 — Catalogue national
# ═══════════════════════════════════════════════════════

SPECIES_V8 = {
    "cerf": {"name_fr": "Cerf de Virginie", "name_en": "White-tailed Deer", "name_sci": "Odocoileus virginianus", "regime": "cervide_tempere", "weight_kg": [60, 130], "provinces": ["qc", "on", "nb", "ns", "pei", "mb", "sk", "ab", "bc"]},
    "orignal": {"name_fr": "Orignal", "name_en": "Moose", "name_sci": "Alces americanus", "regime": "cervide_boreal", "weight_kg": [350, 600], "provinces": ["qc", "on", "nb", "ns", "nl", "mb", "sk", "ab", "bc", "yt", "nt"]},
    "ours_noir": {"name_fr": "Ours noir", "name_en": "Black Bear", "name_sci": "Ursus americanus", "regime": "omnivore_forestier", "weight_kg": [90, 270], "provinces": ["qc", "on", "nb", "ns", "nl", "mb", "sk", "ab", "bc", "yt", "nt"]},
    "wapiti": {"name_fr": "Wapiti", "name_en": "Elk", "name_sci": "Cervus canadensis", "regime": "cervide_montagnard", "weight_kg": [230, 450], "provinces": ["ab", "bc", "sk", "mb", "on"]},
    "caribou": {"name_fr": "Caribou", "name_en": "Caribou", "name_sci": "Rangifer tarandus", "regime": "cervide_boreal", "weight_kg": [110, 210], "provinces": ["qc", "nl", "bc", "yt", "nt", "nu"]},
    "dindon_sauvage": {"name_fr": "Dindon sauvage", "name_en": "Wild Turkey", "name_sci": "Meleagris gallopavo", "regime": "gallinace_forestier", "weight_kg": [5, 11], "provinces": ["qc", "on", "nb", "ns", "mb"]},
    "cerf_mulet": {"name_fr": "Cerf mulet", "name_en": "Mule Deer", "name_sci": "Odocoileus hemionus", "regime": "cervide_montagnard", "weight_kg": [55, 120], "provinces": ["ab", "bc", "sk", "mb", "yt"]},
    "boeuf_musque": {"name_fr": "Boeuf musque", "name_en": "Muskox", "name_sci": "Ovibos moschatus", "regime": "arctique_toundra", "weight_kg": [250, 400], "provinces": ["nu", "nt"]},
}


def detect_biome(lat: float, lng: float, province: str) -> str:
    """Detecte le biome a partir de la position et province."""
    if lat > 68: return "arctic_tundra"
    if lat > 58: return "taiga_subarctic"
    if province == "bc":
        if lng < -125: return "pacific_rainforest"
        if lat > 52: return "montane_subalpine"
        return "pacific_rainforest"
    if province in ["ab", "sk", "mb"] and lat < 52:
        return "prairie_grassland"
    if province in ["nb", "ns", "pei", "nl"]:
        return "atlantic_maritime"
    if province in ["on", "qc"] and lat < 48:
        return "boreal_mixed"
    return "boreal_coniferous"


def detect_wildlife_regime(species: str) -> dict:
    """Retourne le regime faunique pour une espece."""
    sp = SPECIES_V8.get(species.lower())
    if not sp: return WILDLIFE_REGIMES.get("cervide_tempere", {})
    return WILDLIFE_REGIMES.get(sp.get("regime", "cervide_tempere"), {})


def detect_snow_regime(province: str, lat: float) -> dict:
    """Retourne le regime de neige."""
    if lat > 60: return SNOW_REGIMES["subarctique"]
    if province in ["bc"] and lat < 52: return SNOW_REGIMES["maritime"]
    if province in ["bc", "ab"] and lat > 52: return SNOW_REGIMES["alpin"]
    if province in ["nb", "ns", "pei", "nl"]: return SNOW_REGIMES["maritime"]
    return SNOW_REGIMES["continental"]


def detect_forest_regime(biome: str) -> dict:
    """Retourne le regime forestier."""
    mapping = {
        "boreal_coniferous": "conifere_boreal", "boreal_mixed": "mixte_tempere",
        "temperate_deciduous": "feuillu_meridional", "pacific_rainforest": "pluvial_pacifique",
        "montane_subalpine": "conifere_boreal", "taiga_subarctic": "taiga_lichen",
        "arctic_tundra": "taiga_lichen", "prairie_grassland": "mixte_tempere",
        "atlantic_maritime": "mixte_tempere",
    }
    return FOREST_REGIMES.get(mapping.get(biome, "conifere_boreal"), {})
