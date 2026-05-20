"""
_v12_plus_tables.py — Tables doctrinales V12-SUPRA+ Ω
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_TABLES_Ω · STEEVE-MAX · 2026-02-19
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU

Contient :
  - RATIO_CAP_CIBLE_OMEGA  : ratio Ca:P cible doctrinal par espèce
  - CONSO_KG_MS_JOUR       : consommation matière sèche kg/jour par espèce
  - FOOD_PLOT_SURFACE_M2   : surfaces m² par individu × culture
  - TRACE_PPM_CIBLE        : Zn / Se ppm cibles dans recette saline
  - APPROCHE_VENT_DOCTRINALE : doctrine approche chasse par espèce
  - STRATEGIE_CORRIDORS    : règles corridors approche
  - PLAN_30J_TEMPLATE      : structure plan d'action 30 jours
"""
from typing import Dict, Any

# ═════════════════════════════════════════════════════════════════════
# 1. RATIO Ca:P CIBLE DOCTRINAL (NRC Wildlife Nutrition · 2007)
# ═════════════════════════════════════════════════════════════════════
RATIO_CAP_CIBLE_OMEGA: Dict[str, Dict[str, Any]] = {
    "orignal":        {"ratio": "1.5:1", "ratio_num": 1.5, "justification": "Bois en croissance · gestation"},
    "chevreuil":      {"ratio": "1.5:1", "ratio_num": 1.5, "justification": "Bois + lactation"},
    "cerf":           {"ratio": "1.5:1", "ratio_num": 1.5, "justification": "Bois + lactation"},
    "wapiti":         {"ratio": "1.5:1", "ratio_num": 1.5, "justification": "Bois imposants + masse corporelle"},
    "ours_noir":      {"ratio": "1.2:1", "ratio_num": 1.2, "justification": "Omnivore · hibernation"},
    "ours":           {"ratio": "1.2:1", "ratio_num": 1.2, "justification": "Omnivore · hibernation"},
    "dindon_sauvage": {"ratio": "2.0:1", "ratio_num": 2.0, "justification": "Ponte · coquille calcique"},
    "dindon":         {"ratio": "2.0:1", "ratio_num": 2.0, "justification": "Ponte · coquille calcique"},
    "coyote":         {"ratio": "1.2:1", "ratio_num": 1.2, "justification": "Carnivore (n/a saline)"},
}

# ═════════════════════════════════════════════════════════════════════
# 2. CONSOMMATION MATIÈRE SÈCHE (kg/jour individu adulte)
# Sources : NRC + Manuel Faune QC
# ═════════════════════════════════════════════════════════════════════
CONSO_KG_MS_JOUR: Dict[str, float] = {
    "orignal":        7.0,
    "chevreuil":      1.5,
    "cerf":           2.5,
    "wapiti":         6.0,
    "ours_noir":      4.0,   # automne hyperphagie
    "ours":           4.0,
    "dindon_sauvage": 0.15,
    "dindon":         0.15,
    "coyote":         0.5,   # carnivore — non applicable cultures
}

# ═════════════════════════════════════════════════════════════════════
# 3. SURFACE m² PAR INDIVIDU × CULTURE
# Cible : couvrir 50% de la consommation journalière en plante locale
# ═════════════════════════════════════════════════════════════════════
FOOD_PLOT_SURFACE_M2: Dict[str, Dict[str, int]] = {
    "trefle":    {"orignal": 800, "chevreuil": 400, "wapiti": 700, "ours_noir": 200, "dindon_sauvage": 50, "cerf": 450, "coyote": 0},
    "luzerne":   {"orignal": 1000, "chevreuil": 600, "wapiti": 900, "ours_noir": 250, "dindon_sauvage": 80, "cerf": 650, "coyote": 0},
    "brassicas": {"orignal": 450, "chevreuil": 250, "wapiti": 400, "ours_noir": 150, "dindon_sauvage": 30, "cerf": 280, "coyote": 0},
    "avoine":    {"orignal": 600, "chevreuil": 350, "wapiti": 500, "ours_noir": 180, "dindon_sauvage": 60, "cerf": 380, "coyote": 0},
    "mais":      {"orignal": 900, "chevreuil": 500, "wapiti": 800, "ours_noir": 220, "dindon_sauvage": 100, "cerf": 550, "coyote": 0},
}

# ═════════════════════════════════════════════════════════════════════
# 4. TRACE MINÉRAUX ppm CIBLES (recette saline)
# Sources : NRC Wildlife Nutrition + Bubenik (Zn antler), Pugh (Se cervids)
# ═════════════════════════════════════════════════════════════════════
TRACE_PPM_CIBLE: Dict[str, Dict[str, int]] = {
    "orignal":        {"Zn_ppm": 450, "Se_ppm": 22, "Cu_ppm": 15, "I_ppm": 5},
    "chevreuil":      {"Zn_ppm": 420, "Se_ppm": 18, "Cu_ppm": 12, "I_ppm": 4},
    "cerf":           {"Zn_ppm": 420, "Se_ppm": 18, "Cu_ppm": 12, "I_ppm": 4},
    "wapiti":         {"Zn_ppm": 440, "Se_ppm": 20, "Cu_ppm": 14, "I_ppm": 5},
    "ours_noir":      {"Zn_ppm": 320, "Se_ppm": 14, "Cu_ppm": 10, "I_ppm": 3},
    "ours":           {"Zn_ppm": 320, "Se_ppm": 14, "Cu_ppm": 10, "I_ppm": 3},
    "dindon_sauvage": {"Zn_ppm": 380, "Se_ppm": 12, "Cu_ppm": 18, "I_ppm": 2},
    "dindon":         {"Zn_ppm": 380, "Se_ppm": 12, "Cu_ppm": 18, "I_ppm": 2},
}

# ═════════════════════════════════════════════════════════════════════
# 5. DOCTRINE APPROCHE VENT (chasse)
# ═════════════════════════════════════════════════════════════════════
APPROCHE_VENT_DOCTRINALE: Dict[str, Dict[str, Any]] = {
    "orignal": {
        "approche_vent": "Sous le vent strict",
        "distance_min_m": 80,
        "distance_optimale_m": 30,
        "olfaction": "EXTRÊME (>1 km)",
        "ouie": "EXCELLENTE",
        "vue": "MOYENNE (mouvement)",
        "vent_critique_deg": 45,
    },
    "chevreuil": {
        "approche_vent": "Sous le vent · vent croisé acceptable",
        "distance_min_m": 50,
        "distance_optimale_m": 20,
        "olfaction": "EXCELLENTE (500m)",
        "ouie": "EXCELLENTE",
        "vue": "BONNE (mouvement + couleurs UV)",
        "vent_critique_deg": 60,
    },
    "wapiti": {
        "approche_vent": "Sous le vent absolu",
        "distance_min_m": 100,
        "distance_optimale_m": 40,
        "olfaction": "EXTRÊME (>1.5 km)",
        "ouie": "EXTRÊME",
        "vue": "EXCELLENTE",
        "vent_critique_deg": 30,
    },
    "ours_noir": {
        "approche_vent": "Sous le vent · brises thermiques critiques",
        "distance_min_m": 30,
        "distance_optimale_m": 15,
        "olfaction": "SURNATURELLE (>2 km)",
        "ouie": "BONNE",
        "vue": "MOYENNE (faible profondeur)",
        "vent_critique_deg": 25,
    },
    "ours": {
        "approche_vent": "Sous le vent · brises thermiques critiques",
        "distance_min_m": 30,
        "distance_optimale_m": 15,
        "olfaction": "SURNATURELLE (>2 km)",
        "ouie": "BONNE",
        "vue": "MOYENNE (faible profondeur)",
        "vent_critique_deg": 25,
    },
    "dindon_sauvage": {
        "approche_vent": "Toute direction · camouflage critique",
        "distance_min_m": 30,
        "distance_optimale_m": 15,
        "olfaction": "FAIBLE",
        "ouie": "BONNE",
        "vue": "VISION TÉTRAGRAPHIQUE EXCEPTIONNELLE (UV + mouvements)",
        "vent_critique_deg": 90,
    },
    "dindon": {
        "approche_vent": "Toute direction · camouflage critique",
        "distance_min_m": 30,
        "distance_optimale_m": 15,
        "olfaction": "FAIBLE",
        "ouie": "BONNE",
        "vue": "VISION TÉTRAGRAPHIQUE EXCEPTIONNELLE (UV + mouvements)",
        "vent_critique_deg": 90,
    },
    "coyote": {
        "approche_vent": "Sous le vent · embuscade",
        "distance_min_m": 80,
        "distance_optimale_m": 50,
        "olfaction": "EXCELLENTE",
        "ouie": "EXTRÊME",
        "vue": "EXCELLENTE (mouvements)",
        "vent_critique_deg": 45,
    },
}

# ═════════════════════════════════════════════════════════════════════
# 6. STRATÉGIE CORRIDORS (par espèce)
# ═════════════════════════════════════════════════════════════════════
STRATEGIE_CORRIDORS: Dict[str, Dict[str, Any]] = {
    "orignal": {
        "approche_corridor": "Couper transversal · jamais dans l'axe",
        "heure_optimale": "Aube (5h-7h) et crépuscule (18h-20h)",
        "vegetation_couvert": "Aulnaies, jeunes coupes, marécages",
        "type_terrain_optimal": "Bas-fonds humides, lisières mixtes",
    },
    "chevreuil": {
        "approche_corridor": "Lisière de couvert · proximité abri",
        "heure_optimale": "Aube et crépuscule + nuit pleine lune",
        "vegetation_couvert": "Jeunes feuillus, brûlis, taillis",
        "type_terrain_optimal": "Mosaïque champ-forêt, lisières",
    },
    "wapiti": {
        "approche_corridor": "Couper crête · sous le vent dominant",
        "heure_optimale": "Aube et soirée fin de jour",
        "vegetation_couvert": "Vieilles forêts mixtes, prairies subalpines",
        "type_terrain_optimal": "Crêtes, clairières altitudinales",
    },
    "ours_noir": {
        "approche_corridor": "Près des sources nourriture (baies, charognes)",
        "heure_optimale": "Crépuscule (17h-21h) et tôt matin",
        "vegetation_couvert": "Champs de bleuets, framboisières, vieux brûlis",
        "type_terrain_optimal": "Coupes anciennes, lisières productives",
    },
    "ours": {
        "approche_corridor": "Près des sources nourriture (baies, charognes)",
        "heure_optimale": "Crépuscule (17h-21h) et tôt matin",
        "vegetation_couvert": "Champs de bleuets, framboisières, vieux brûlis",
        "type_terrain_optimal": "Coupes anciennes, lisières productives",
    },
    "dindon_sauvage": {
        "approche_corridor": "Près des arbres dortoirs · clairières d'alimentation",
        "heure_optimale": "Aube (perchage descente) et fin de jour (montée)",
        "vegetation_couvert": "Forêts mixtes avec dortoirs · clairières",
        "type_terrain_optimal": "Lisières champs-bois, chemins forestiers",
    },
    "dindon": {
        "approche_corridor": "Près des arbres dortoirs · clairières d'alimentation",
        "heure_optimale": "Aube (perchage descente) et fin de jour (montée)",
        "vegetation_couvert": "Forêts mixtes avec dortoirs · clairières",
        "type_terrain_optimal": "Lisières champs-bois, chemins forestiers",
    },
    "coyote": {
        "approche_corridor": "Embuscade lisière · appels imitations",
        "heure_optimale": "Nuit + crépuscule + aube",
        "vegetation_couvert": "Lisières, terres agricoles, friches",
        "type_terrain_optimal": "Mosaïque agro-forestière",
    },
}

# ═════════════════════════════════════════════════════════════════════
# 7. PLAN 30 JOURS TEMPLATE (structure générique)
# ═════════════════════════════════════════════════════════════════════
PLAN_30J_PHASES = [
    {
        "phase": "J-30 à J-21",
        "objectif": "Préparation site",
        "actions": [
            "Repérage saline · validation accès et vent dominants",
            "Installation saline minérale (recette V12+)",
            "Préparation champ nourricier (semis/fertilisation si saison)",
        ],
    },
    {
        "phase": "J-20 à J-11",
        "objectif": "Habituation animale",
        "actions": [
            "Visite hebdomadaire saline · contrôle consommation",
            "Caméra-piège pour identification individus",
            "Aucune chasse · habituation présence humaine résiduelle",
        ],
    },
    {
        "phase": "J-10 à J-1",
        "objectif": "Fenêtre tactique",
        "actions": [
            "Affût opérationnel · vérifier vent + thermique",
            "Surveillance pattern individus (caméra + observation)",
            "Ajustement saline si consommation < cible",
        ],
    },
    {
        "phase": "J0 (jour de chasse)",
        "objectif": "Tir éthique",
        "actions": [
            "Vérifier vent < {vent_critique_deg}° décalage axe",
            "Affût {heure_optimale}",
            "Distance optimale {distance_optimale_m} m",
        ],
    },
]


def get_table_value(table: Dict[str, Any], species: str, default: Any = None) -> Any:
    """Lookup espèce avec normalisation (sauvage, noir suffixes)."""
    if not species:
        return default
    key = str(species).lower().strip()
    return (
        table.get(key)
        or table.get(key.replace("_sauvage", ""))
        or table.get(key.replace("_noir", ""))
        or default
    )


# ═════════════════════════════════════════════════════════════════════
# 8. SIGNATURE DOCTRINALE
# ═════════════════════════════════════════════════════════════════════
TABLES_DOCTRINE = "P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_TABLES_Ω"
TABLES_VERSION = "V12+-2026-02-T1"
