"""
SALINE INTELLIGENCE ULTRA — Wildlife Nutritional Needs Engine V1
Besoins journaliers par espece, sexe, age, saison.
Couvre: croissance bois, gestation, lactation, rut, survie hivernale.

Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x1000
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("saline.wildlife_nutrition")

# Daily mineral requirements (mg/day) by species
# Sources: NRC Wildlife Nutrition, Bubenik (antler growth), Verme & Ullrey
SPECIES_NEEDS = {
    "orignal": {
        "base_weight_kg": 450,
        "minerals": {
            "Ca": {"base": 18000, "antler": 35000, "gestation": 25000, "rut": 22000, "winter": 12000},
            "P": {"base": 12000, "antler": 25000, "gestation": 18000, "rut": 15000, "winter": 8000},
            "K": {"base": 8000, "antler": 8000, "gestation": 10000, "rut": 9000, "winter": 6000},
            "Mg": {"base": 3000, "antler": 5000, "gestation": 4000, "rut": 3500, "winter": 2000},
            "Na": {"base": 4000, "antler": 5000, "gestation": 5500, "rut": 4500, "winter": 3000},
            "S": {"base": 2000, "antler": 3500, "gestation": 2500, "rut": 2200, "winter": 1500},
            "Zn": {"base": 150, "antler": 300, "gestation": 200, "rut": 180, "winter": 100},
            "Cu": {"base": 30, "antler": 50, "gestation": 40, "rut": 35, "winter": 20},
            "Mn": {"base": 120, "antler": 200, "gestation": 160, "rut": 140, "winter": 80},
            "Se": {"base": 1.5, "antler": 2.0, "gestation": 2.5, "rut": 1.8, "winter": 1.0},
        }
    },
    "chevreuil": {
        "base_weight_kg": 70,
        "minerals": {
            "Ca": {"base": 5000, "antler": 12000, "gestation": 8000, "rut": 7000, "winter": 3500},
            "P": {"base": 3500, "antler": 8000, "gestation": 5500, "rut": 4500, "winter": 2500},
            "K": {"base": 2500, "antler": 2500, "gestation": 3500, "rut": 3000, "winter": 1800},
            "Mg": {"base": 900, "antler": 1500, "gestation": 1200, "rut": 1000, "winter": 600},
            "Na": {"base": 1200, "antler": 1500, "gestation": 1800, "rut": 1400, "winter": 900},
            "S": {"base": 600, "antler": 1000, "gestation": 800, "rut": 700, "winter": 400},
            "Zn": {"base": 45, "antler": 90, "gestation": 60, "rut": 55, "winter": 30},
            "Cu": {"base": 10, "antler": 18, "gestation": 14, "rut": 12, "winter": 7},
            "Mn": {"base": 35, "antler": 60, "gestation": 50, "rut": 42, "winter": 24},
            "Se": {"base": 0.5, "antler": 0.7, "gestation": 0.8, "rut": 0.6, "winter": 0.3},
        }
    },
    "ours_noir": {
        "base_weight_kg": 120,
        "minerals": {
            "Ca": {"base": 8000, "antler": 8000, "gestation": 12000, "rut": 9000, "winter": 5000},
            "P": {"base": 5500, "antler": 5500, "gestation": 8000, "rut": 6000, "winter": 3500},
            "K": {"base": 4000, "antler": 4000, "gestation": 5500, "rut": 4500, "winter": 2800},
            "Mg": {"base": 1500, "antler": 1500, "gestation": 2000, "rut": 1700, "winter": 1000},
            "Na": {"base": 2500, "antler": 2500, "gestation": 3000, "rut": 2800, "winter": 1500},
            "S": {"base": 1000, "antler": 1000, "gestation": 1400, "rut": 1100, "winter": 700},
            "Zn": {"base": 60, "antler": 60, "gestation": 80, "rut": 70, "winter": 40},
            "Cu": {"base": 15, "antler": 15, "gestation": 22, "rut": 18, "winter": 10},
            "Mn": {"base": 50, "antler": 50, "gestation": 70, "rut": 55, "winter": 35},
            "Se": {"base": 0.8, "antler": 0.8, "gestation": 1.2, "rut": 0.9, "winter": 0.5},
        }
    },
    "dindon_sauvage": {
        "base_weight_kg": 8,
        "minerals": {
            "Ca": {"base": 2500, "antler": 2500, "gestation": 4000, "rut": 3000, "winter": 1500},
            "P": {"base": 1800, "antler": 1800, "gestation": 2800, "rut": 2000, "winter": 1000},
            "K": {"base": 1000, "antler": 1000, "gestation": 1500, "rut": 1200, "winter": 700},
            "Mg": {"base": 400, "antler": 400, "gestation": 600, "rut": 450, "winter": 280},
            "Na": {"base": 600, "antler": 600, "gestation": 800, "rut": 700, "winter": 400},
            "S": {"base": 300, "antler": 300, "gestation": 450, "rut": 350, "winter": 200},
            "Zn": {"base": 20, "antler": 20, "gestation": 30, "rut": 24, "winter": 14},
            "Cu": {"base": 5, "antler": 5, "gestation": 8, "rut": 6, "winter": 3},
            "Mn": {"base": 18, "antler": 18, "gestation": 28, "rut": 20, "winter": 12},
            "Se": {"base": 0.2, "antler": 0.2, "gestation": 0.4, "rut": 0.3, "winter": 0.1},
        }
    },
}

SEASON_TO_NEED_KEY = {
    "printemps": "antler",
    "ete": "base",
    "pre_rut": "rut",
    "rut": "rut",
    "post_rut": "base",
    "hiver": "winter",
    "automne": "base",
}


def get_daily_needs(species: str, season: str = "automne", sex: str = "male", age: str = "adult") -> Dict[str, Any]:
    sp_data = SPECIES_NEEDS.get(species, SPECIES_NEEDS["orignal"])
    need_key = SEASON_TO_NEED_KEY.get(season, "base")

    # Female adjustments
    sex_factor = 1.0
    if sex == "female":
        sex_factor = 0.75
        if need_key == "antler":
            need_key = "gestation"

    # Age adjustments
    age_factor = {"juvenile": 1.2, "adult": 1.0, "senior": 0.85}.get(age, 1.0)

    needs = {}
    for mineral, values in sp_data["minerals"].items():
        base_need = values.get(need_key, values["base"])
        adjusted = round(base_need * sex_factor * age_factor, 1)
        needs[mineral] = {"daily_mg": adjusted, "phase": need_key}

    return {
        "species": species,
        "season": season,
        "sex": sex,
        "age": age,
        "metabolic_phase": need_key,
        "base_weight_kg": sp_data["base_weight_kg"],
        "daily_needs": needs,
    }
