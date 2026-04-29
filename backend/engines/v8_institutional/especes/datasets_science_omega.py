"""
datasets_science_omega.py — PHASE XVII · DATASETS UNIFIÉS
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°37

Référentiel SCI_Ω unifié : fusion des 20 études NUTRITION + 50 études HABITAT.
Extraits des attachments officiels du Commandant. Zéro fallback. Zéro générique.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict, List


ESPECES_CANONICAL = ["CHEVREUIL", "ORIGNAL", "OURS_NOIR", "WAPITI", "DINDON_SAUVAGE"]
SAISONS_CANONICAL = ["PRINTEMPS", "ETE", "AUTOMNE", "HIVER"]

# Table d'harmonisation taxonomique (texte libre → canonique)
TAXONOMY_ALIAS = {
    "orignal": "ORIGNAL",
    "chevreuil": "CHEVREUIL",
    "cerf de virginie": "CHEVREUIL",
    "chevreuil (cerf de virginie)": "CHEVREUIL",
    "white-tailed deer": "CHEVREUIL",
    "white tailed deer": "CHEVREUIL",
    "wapiti": "WAPITI",
    "elk": "WAPITI",
    "ours noir": "OURS_NOIR",
    "ours_noir": "OURS_NOIR",
    "black bear": "OURS_NOIR",
    "dindon sauvage": "DINDON_SAUVAGE",
    "dindon_sauvage": "DINDON_SAUVAGE",
    "wild turkey": "DINDON_SAUVAGE",
    "eastern wild turkey": "DINDON_SAUVAGE",
    "rocky mountain elk": "WAPITI",
    "caribou": "__NON_CANONICAL__",
    "cerf mulet": "__NON_CANONICAL__",
    "mule deer": "__NON_CANONICAL__",
}

SAISON_ALIAS = {
    "printemps": "PRINTEMPS", "spring": "PRINTEMPS",
    "été": "ETE", "ete": "ETE", "summer": "ETE",
    "automne": "AUTOMNE", "fall": "AUTOMNE", "autumn": "AUTOMNE",
    "hiver": "HIVER", "winter": "HIVER",
    "toutes saisons": "ALL",
}

# Classification TYPE_DE_PREUVE → {GOV, UNI, PR}
PREUVE_CLASSIFIER = {
    "journal of wildlife management": "PR",
    "canadian journal of zoology": "PR",
    "ecology and evolution": "PR",
    "ecography": "PR",
    "oecologia": "PR",
    "forest ecology and management": "PR",
    "journal of applied ecology": "PR",
    "diversity and distributions": "PR",
    "biological conservation": "PR",
    "wildlife society bulletin": "PR",
    "wildlife biology": "PR",
    "journal of zoology": "PR",
    "movement ecology": "PR",
    "urban ecosystems": "PR",
    "rangifer / cjz": "PR",
    "facets": "PR",
    "forestry": "PR",
    "book": "UNI",
    "book chapter": "UNI",
    "book / synthesis": "UNI",
    "smithsonian / book": "UNI",
    "wildlife feeding and nutrition": "UNI",
    "the wild turkey: biology and management": "UNI",
    "ecology and management of the north american moose": "UNI",
    "ecology and management of black bears in north america": "UNI",
    "canadian journal of forest research": "PR",
    "colorado division of wildlife tech. pub.": "GOV",
    "colorado division of wildlife technical publication": "GOV",
    "divers rapports mrnf": "GOV",
    "rapport/thèse": "UNI",
    "oecologia / jwm": "PR",
}


def classify_preuve(source: str) -> str:
    """Classe une source en {GOV, UNI, PR, UNKNOWN}."""
    if not source:
        return "UNKNOWN"
    low = source.lower().strip()
    if low in PREUVE_CLASSIFIER:
        return PREUVE_CLASSIFIER[low]
    # Heuristique
    if any(k in low for k in ("journal", "journal of", "ecology", "biology", "zool",
                               "forestry", "oecologia", "ecography", "rangifer",
                               "facets", "movement ecol", "wildlife society",
                               "wildlife biology", "forest ecology")):
        return "PR"
    if any(k in low for k in ("book", "ecology and management", "synthesis")):
        return "UNI"
    if any(k in low for k in ("tech. pub", "technical publication", "rapports",
                               "mrnf", "mffp", "government", "agency")):
        return "GOV"
    return "UNKNOWN"


def normalize_confidence(level: str) -> str:
    """Normalise le niveau de confiance."""
    if not level:
        return "INCONNU"
    low = level.lower().strip()
    if "élev" in low or "high" in low:
        return "ÉLEVÉ"
    if "moy" in low or "medium" in low or "moderate" in low:
        return "MOYEN"
    if "faibl" in low or "low" in low:
        return "FAIBLE"
    return level.upper()


def normalize_espece(raw: str) -> List[str]:
    """Retourne la liste des espèces canoniques détectées."""
    if not raw:
        return []
    low = raw.lower().strip()
    result = []
    for alias, canon in TAXONOMY_ALIAS.items():
        if alias in low and canon != "__NON_CANONICAL__" and canon not in result:
            result.append(canon)
    return result


def normalize_saison(saisons: List[str]) -> List[str]:
    """Normalise liste de saisons."""
    if not saisons:
        return []
    out = []
    for s in saisons:
        low = (s or "").lower().strip()
        canon = SAISON_ALIAS.get(low)
        if canon == "ALL":
            return SAISONS_CANONICAL[:]  # toutes
        if canon and canon not in out:
            out.append(canon)
    return out


# ═════════════════════════════════════════════════════════════════════════
# DATASET NUTRITION (20 études extraites de json alimentaire.docx)
# ═════════════════════════════════════════════════════════════════════════

DATASET_NUTRITION_RAW = [
    {"id": 1, "especes_raw": "Orignal, chevreuil, wapiti, caribou",
     "reference": "Stevenson et al., 2021, FACETS", "annee": 2021,
     "type_etude": "ADN fécal", "region": "Alberta, Canada",
     "focus": "Composition hivernale fine, chevauchement de niche alimentaire",
     "saisons_raw": ["Hiver"], "confidence": "ÉLEVÉ",
     "bloc": "ALIMENTATION_HIVERNALE_ONGULES"},
    {"id": 2, "especes_raw": "Orignal", "reference": "Breithaupt et al., 2024, Forestry",
     "annee": 2024, "type_etude": "Microhistologie", "region": "C.-B., Canada",
     "focus": "Sélection de brout (sapin subalpin, saule, bouleau, tremble)",
     "saisons_raw": ["Hiver"], "confidence": "ÉLEVÉ",
     "bloc": "BROUT_HIVERNAL_ORIGNAL"},
    {"id": 3, "especes_raw": "Orignal, wapiti, cerf mulet",
     "reference": "Étude UNBC sur le chevauchement de régime (rapport/thèse)",
     "annee": None, "type_etude": "Analyse ruminal/fécal", "region": "C.-B., Canada",
     "focus": "Chevauchement de régime hivernage cerf mulet",
     "saisons_raw": ["Hiver"], "confidence": "ÉLEVÉ",
     "bloc": "CHEVAUCHEMENT_REGIME_HIVERNAL_ONGULES"},
    {"id": 4, "especes_raw": "Orignal", "reference": "Peek, 1974, Journal of Wildlife Management",
     "annee": 1974, "type_etude": "Synthèse", "region": "Alaska, USA",
     "focus": "Écologie alimentaire saisonnière orignal boréal",
     "saisons_raw": ["Toutes saisons"], "confidence": "ÉLEVÉ",
     "bloc": "ECOLOGIE_ALIMENTAIRE_SAISONNIERE_ORIGNAL"},
    {"id": 5, "especes_raw": "Orignal",
     "reference": "Renecker & Schwartz, 1998, Ecology and Management of the North American Moose",
     "annee": 1998, "type_etude": "Revue", "region": "Amérique du Nord boréale",
     "focus": "Nutrition, besoins énergétiques, qualité du fourrage",
     "saisons_raw": ["Toutes saisons"], "confidence": "ÉLEVÉ",
     "bloc": "NUTRITION_BESOINS_ENERGETIQUES_ORIGNAL"},
    {"id": 6, "especes_raw": "Orignal", "reference": "Courtois et al., années 1990, divers rapports MRNF",
     "annee": 1995, "type_etude": "Contenu ruminal saisonnier", "region": "Québec, Canada",
     "focus": "Variation saisonnière brout feuillus vs résineux",
     "saisons_raw": ["Printemps", "Été", "Automne", "Hiver"], "confidence": "MOYEN",
     "bloc": "VARIATION_SAISONNIERE_BROUT_ORIGNAL"},
    {"id": 7, "especes_raw": "Chevreuil (cerf de Virginie)",
     "reference": "Verme & Ullrey, 1984, Journal of Wildlife Management",
     "annee": 1984, "type_etude": "Revue", "region": "Est du Canada / NE USA",
     "focus": "Métabolisme, besoins nutritionnels, habitat hivernal",
     "saisons_raw": ["Hiver"], "confidence": "ÉLEVÉ",
     "bloc": "METABOLISME_BESOINS_HIVERNAL_CHEVREUIL"},
    {"id": 8, "especes_raw": "Chevreuil",
     "reference": "Brown et al., années 1990, Canadian Journal of Zoology",
     "annee": 1995, "type_etude": "Fèces + disponibilité brout", "region": "Ontario, Canada",
     "focus": "Sélection brout forêt mixte + coupes forestières",
     "saisons_raw": ["Toutes saisons"], "confidence": "ÉLEVÉ",
     "bloc": "SELECTION_BROUT_CHEVREUIL_COUPES"},
    {"id": 9, "especes_raw": "Chevreuil",
     "reference": "Korschgen, 1962, Journal of Wildlife Management",
     "annee": 1962, "type_etude": "Contenu ruminal long terme", "region": "Midwest & NE USA",
     "focus": "Composition régime saisonnier historique",
     "saisons_raw": ["Printemps", "Été", "Automne", "Hiver"], "confidence": "ÉLEVÉ",
     "bloc": "REGIME_SAISONNIER_HISTORIQUE_CHEVREUIL"},
    {"id": 10, "especes_raw": "Wapiti",
     "reference": "Hebblewhite et al., années 2000, Oecologia / JWM",
     "annee": 2005, "type_etude": "Fèces + télémétrie", "region": "Rocheuses canadiennes",
     "focus": "Régime, sélection habitat, prédation loups",
     "saisons_raw": ["Toutes saisons"], "confidence": "ÉLEVÉ",
     "bloc": "REGIME_HABITAT_PREDATION_WAPITI"},
    {"id": 11, "especes_raw": "Wapiti",
     "reference": "Singer et al., années 1990, Journal of Wildlife Management",
     "annee": 1995, "type_etude": "Long terme multi-saisons", "region": "Yellowstone, USA",
     "focus": "Pression brout végétation riveraine (saules, peupliers)",
     "saisons_raw": ["Printemps", "Été"], "confidence": "ÉLEVÉ",
     "bloc": "PRESSION_BROUT_VEGETATION_RIVERINE_WAPITI"},
    {"id": 12, "especes_raw": "Wapiti",
     "reference": "Kufeld, 1973, Colorado Division of Wildlife Tech. Pub.",
     "annee": 1973, "type_etude": "Contenu ruminal", "region": "Oregon/Idaho, USA",
     "focus": "Catalogue plantes consommées par saison",
     "saisons_raw": ["Toutes saisons"], "confidence": "ÉLEVÉ",
     "bloc": "CATALOGUE_PLANTES_CONSOMMEES_WAPITI"},
    {"id": 13, "especes_raw": "Ours noir",
     "reference": "Samson & Huot, 1995, Canadian Journal of Zoology",
     "annee": 1995, "type_etude": "Fèces saisons", "region": "Est du Canada",
     "focus": "Variation saisonnière : végétaux, petits fruits, insectes, charognes",
     "saisons_raw": ["Printemps", "Été", "Automne"], "confidence": "ÉLEVÉ",
     "bloc": "REGIME_SAISONNIER_OURS_NOIR"},
    {"id": 14, "especes_raw": "Ours noir",
     "reference": "Jolicoeur & Crête, années 1990, Canadian Journal of Zoology",
     "annee": 1995, "type_etude": "Fèces + disponibilité fruits", "region": "Québec, Canada",
     "focus": "Rôle petits fruits dans engraissement pré-hivernal",
     "saisons_raw": ["Été", "Automne"], "confidence": "ÉLEVÉ",
     "bloc": "ROLE_PETITS_FRUITS_ENGRAISSEMENT_OURS_NOIR"},
    {"id": 15, "especes_raw": "Ours noir",
     "reference": "Pelton, 2000, Ecology and Management of Black Bears in North America",
     "annee": 2000, "type_etude": "Synthèse long terme", "region": "Appalaches, USA",
     "focus": "Diète, plasticité alimentaire, conflits humain",
     "saisons_raw": ["Toutes saisons"], "confidence": "ÉLEVÉ",
     "bloc": "DIETE_PLASTICITE_CONFLITS_OURS_NOIR"},
    {"id": 16, "especes_raw": "Dindon sauvage",
     "reference": "Dalke et al., 1942, Journal of Wildlife Management",
     "annee": 1942, "type_etude": "Gésiers + contenus digestifs", "region": "Est des USA",
     "focus": "Aliments saisonniers (glands, graines, invertébrés)",
     "saisons_raw": ["Printemps", "Été", "Automne", "Hiver"], "confidence": "ÉLEVÉ",
     "bloc": "ALIMENTS_SAISONNIERS_DINDON_SAUVAGE"},
    {"id": 17, "especes_raw": "Dindon sauvage",
     "reference": "Hurst, 1992, The Wild Turkey: Biology and Management",
     "annee": 1992, "type_etude": "Gésiers classes d'âge", "region": "Sud-Est USA",
     "focus": "Différences régime jeunes/adultes, invertébrés printemps",
     "saisons_raw": ["Printemps", "Été"], "confidence": "ÉLEVÉ",
     "bloc": "REGIME_JEUNES_ADULTES_DINDON_SAUVAGE"},
    {"id": 18, "especes_raw": "Dindon sauvage",
     "reference": "Healy, années 1980, Wildlife Society Bulletin",
     "annee": 1985, "type_etude": "Hiver disponibilité nourriture", "region": "NE USA",
     "focus": "Utilisation champs agricoles, forêts de chênes",
     "saisons_raw": ["Hiver"], "confidence": "MOYEN",
     "bloc": "UTILISATION_RESSOURCES_HIVERNALES_DINDON_SAUVAGE"},
    {"id": 19, "especes_raw": "Multi-ongulés (orignal, cerf, wapiti)",
     "reference": "Parker et al., années 1990, Rangifer / CJZ",
     "annee": 1995, "type_etude": "Revue", "region": "Ouest canadien",
     "focus": "Comparaison besoins énergétiques et qualité fourrage hiver",
     "saisons_raw": ["Hiver"], "confidence": "ÉLEVÉ",
     "bloc": "BESOINS_ENERGETIQUES_QUALITE_FOURRAGE_HIVER_MULTIONGULES"},
    {"id": 20, "especes_raw": "Multi-espèces grands gibiers",
     "reference": "Robbins, 1993, Wildlife Feeding and Nutrition",
     "annee": 1993, "type_etude": "Revue synthèse", "region": "Amérique du Nord",
     "focus": "Physiologie nutritionnelle, valeur plantes fourragères",
     "saisons_raw": ["Toutes saisons"], "confidence": "ÉLEVÉ",
     "bloc": "PHYSIOLOGIE_NUTRITIONNELLE_VALEUR_PLANTES_GRAND_GIBIER"},
]


# ═════════════════════════════════════════════════════════════════════════
# DATASET HABITAT (50 études extraites de Json habitats grands gibiers.docx)
# ═════════════════════════════════════════════════════════════════════════

DATASET_HABITAT_RAW = [
    # ORIGNAL (10)
    {"id": 1, "espece": "ORIGNAL", "annee": 1974, "auteurs": "Peek J.M.",
     "titre": "Habitat use and ecology of moose in north-central North America",
     "biome": "Forêt boréale / subboréale", "source": "Journal of Wildlife Management",
     "biome_types": ["FORET_BOREAL", "FORET_SUBBOREAL"], "confidence": "ÉLEVÉ"},
    {"id": 2, "espece": "ORIGNAL", "annee": 1998, "auteurs": "Franzmann A.W., Schwartz C.C.",
     "titre": "Ecology and Management of the North American Moose – Habitat chapter",
     "biome": "Forêt boréale, taïga, forêt mixte", "source": "Smithsonian / Book",
     "biome_types": ["FORET_BOREAL", "TAIGA", "FORET_MIXTE"], "confidence": "ÉLEVÉ"},
    {"id": 3, "espece": "ORIGNAL", "annee": 2000, "auteurs": "Courtois R. et al.",
     "titre": "Moose winter habitat selection in logged boreal forests",
     "biome": "Forêt boréale aménagée", "source": "Canadian Journal of Forest Research",
     "biome_types": ["FORET_BOREAL_AMENAGEE"], "confidence": "ÉLEVÉ"},
    {"id": 4, "espece": "ORIGNAL", "annee": 2007, "auteurs": "Dussault C. et al.",
     "titre": "Effects of forestry practices on moose habitat in eastern Canada",
     "biome": "Forêt boréale / mixte", "source": "Journal of Applied Ecology",
     "biome_types": ["FORET_BOREAL", "FORET_MIXTE"], "confidence": "ÉLEVÉ"},
    {"id": 5, "espece": "ORIGNAL", "annee": 2013, "auteurs": "Street G.M. et al.",
     "titre": "Thermal refugia and habitat selection by moose in a warming climate",
     "biome": "Forêt boréale / tempérée froide", "source": "Ecography",
     "biome_types": ["FORET_BOREAL", "FORET_TEMPEREE_FROIDE"], "confidence": "ÉLEVÉ"},
    {"id": 6, "espece": "ORIGNAL", "annee": 2016, "auteurs": "Broders H.G. et al.",
     "titre": "Landscape-scale drivers of moose distribution",
     "biome": "Mosaïque boréale / agricole", "source": "Diversity and Distributions",
     "biome_types": ["MOSAIQUE_BOREAL_AGRICOLE"], "confidence": "ÉLEVÉ"},
    {"id": 7, "espece": "ORIGNAL", "annee": 2019, "auteurs": "Montgomery R.A. et al.",
     "titre": "Moose habitat selection in multi-predator landscapes",
     "biome": "Forêt boréale / montagnarde", "source": "Oecologia",
     "biome_types": ["FORET_BOREAL", "FORET_MONTAGNARDE"], "confidence": "ÉLEVÉ"},
    {"id": 8, "espece": "ORIGNAL", "annee": 2021, "auteurs": "Stevenson C. et al.",
     "titre": "Fine-scale habitat selection by moose at the forest cutblock interface",
     "biome": "Forêt boréale aménagée", "source": "Forest Ecology and Management",
     "biome_types": ["FORET_BOREAL_AMENAGEE"], "confidence": "ÉLEVÉ"},
    {"id": 9, "espece": "ORIGNAL", "annee": 2023, "auteurs": "Thompson I.D. et al.",
     "titre": "Edge population dynamics and habitat selection of moose",
     "biome": "Lisières boréales / agricoles", "source": "Ecology and Evolution",
     "biome_types": ["LIERES_BOREALES_AGRICOLES"], "confidence": "ÉLEVÉ"},
    {"id": 10, "espece": "ORIGNAL", "annee": 2024, "auteurs": "Smith J. et al.",
     "titre": "Habitat selection by moose in an emergent low-density edge population",
     "biome": "Mosaïque boréale / prairies", "source": "Journal of Wildlife Management",
     "biome_types": ["MOSAIQUE_BOREAL_PRAIRIES"], "confidence": "ÉLEVÉ"},
    # CHEVREUIL (10)
    {"id": 11, "espece": "CHEVREUIL", "annee": 1984, "auteurs": "Verme L.J., Ullrey D.E.",
     "titre": "Habitat, nutrition and population dynamics of white-tailed deer",
     "biome": "Forêt mixte, agricole, milieux ouverts",
     "source": "Journal of Wildlife Management",
     "biome_types": ["FORET_MIXTE", "MILIEUX_AGRICOLES", "MILIEUX_OUVERTS"], "confidence": "ÉLEVÉ"},
    {"id": 12, "espece": "CHEVREUIL", "annee": 1990, "auteurs": "Brown T.L. et al.",
     "titre": "Winter habitat use by white-tailed deer in mixed forests",
     "biome": "Forêt mixte enneigée", "source": "Canadian Journal of Zoology",
     "biome_types": ["FORET_MIXTE_ENNEIGEE"], "confidence": "ÉLEVÉ"},
    {"id": 13, "espece": "CHEVREUIL", "annee": 1998, "auteurs": "Potvin F. et al.",
     "titre": "Effects of forest management on deer wintering areas",
     "biome": "Forêt mixte aménagée", "source": "Forest Ecology and Management",
     "biome_types": ["FORET_MIXTE_AMENAGEE"], "confidence": "ÉLEVÉ"},
    {"id": 14, "espece": "CHEVREUIL", "annee": 2003, "auteurs": "Etter D.R. et al.",
     "titre": "Landscape composition and white-tailed deer habitat use",
     "biome": "Mosaïque agricole / forestière", "source": "Journal of Wildlife Management",
     "biome_types": ["MOSAIQUE_AGRICOLE_FORESTIERE"], "confidence": "ÉLEVÉ"},
    {"id": 15, "espece": "CHEVREUIL", "annee": 2008, "auteurs": "Sabine D.L. et al.",
     "titre": "Influence of snow depth on deer habitat selection",
     "biome": "Forêt boréale / mixte", "source": "Wildlife Society Bulletin",
     "biome_types": ["FORET_BOREAL", "FORET_MIXTE"], "confidence": "ÉLEVÉ"},
    {"id": 16, "espece": "CHEVREUIL", "annee": 2012, "auteurs": "Storm D.J. et al.",
     "titre": "Urban and suburban habitat use by white-tailed deer",
     "biome": "Urbain / périurbain", "source": "Urban Ecosystems",
     "biome_types": ["URBAIN", "PERIURBAIN"], "confidence": "ÉLEVÉ"},
    {"id": 17, "espece": "CHEVREUIL", "annee": 2016, "auteurs": "Fuller A.K. et al.",
     "titre": "Forest stand structure and deer habitat quality",
     "biome": "Forêt tempérée feuillue", "source": "Forest Ecology and Management",
     "biome_types": ["FORET_TEMPEREE_FEUILLUE"], "confidence": "ÉLEVÉ"},
    {"id": 18, "espece": "CHEVREUIL", "annee": 2019, "auteurs": "Walter W.D. et al.",
     "titre": "Multi-scale habitat selection by white-tailed deer",
     "biome": "Mosaïque forestière / agricole", "source": "Ecology and Evolution",
     "biome_types": ["MOSAIQUE_FORESTIERE_AGRICOLE"], "confidence": "ÉLEVÉ"},
    {"id": 19, "espece": "CHEVREUIL", "annee": 2021, "auteurs": "DePerno C.S. et al.",
     "titre": "Landscape change mechanisms affecting deer distribution",
     "biome": "Forêt tempérée / agricole", "source": "Journal of Wildlife Management",
     "biome_types": ["FORET_TEMPEREE", "MILIEUX_AGRICOLES"], "confidence": "ÉLEVÉ"},
    {"id": 20, "espece": "CHEVREUIL", "annee": 2023, "auteurs": "Jones P.D. et al.",
     "titre": "Habitat-use patterns across forest stand ages by white-tailed deer",
     "biome": "Forêt aménagée multi-stades", "source": "Forest Ecology and Management",
     "biome_types": ["FORET_AMENAGEE_MULTI_STADES"], "confidence": "ÉLEVÉ"},
    # WAPITI (10)
    {"id": 21, "espece": "WAPITI", "annee": 1973, "auteurs": "Kufeld R.C.",
     "titre": "Food habits and habitat use of Rocky Mountain elk",
     "biome": "Montagne, prairies montagnardes",
     "source": "Colorado Division of Wildlife Technical Publication",
     "biome_types": ["MONTAGNE", "PRAIRIE_MONTAGNARDE"], "confidence": "ÉLEVÉ"},
    {"id": 22, "espece": "WAPITI", "annee": 1997, "auteurs": "Boyce M.S. et al.",
     "titre": "Elk habitat selection and wolf reintroduction in Yellowstone",
     "biome": "Montagne, vallée fluviale", "source": "Journal of Wildlife Management",
     "biome_types": ["MONTAGNE", "VALLEE_FLUVIALE"], "confidence": "ÉLEVÉ"},
    {"id": 23, "espece": "WAPITI", "annee": 2002, "auteurs": "Rowland M.M. et al.",
     "titre": "Habitat use by elk in relation to roads and human disturbance",
     "biome": "Forêt montagnarde / routes forestières",
     "source": "Journal of Wildlife Management",
     "biome_types": ["FORET_MONTAGNARDE", "ROUTES_FORESTIERES"], "confidence": "ÉLEVÉ"},
    {"id": 24, "espece": "WAPITI", "annee": 2005, "auteurs": "Hebblewhite M. et al.",
     "titre": "Elk habitat selection in a multi-predator system",
     "biome": "Rocheuses canadiennes", "source": "Oecologia",
     "biome_types": ["ROCHEUSES_CANADIENNES"], "confidence": "ÉLEVÉ"},
    {"id": 25, "espece": "WAPITI", "annee": 2010, "auteurs": "Singer F.J. et al.",
     "titre": "Riparian habitat use by elk and impacts on woody vegetation",
     "biome": "Ripisylve montagnarde", "source": "Journal of Wildlife Management",
     "biome_types": ["RIPISYLVE_MONTAGNARDE"], "confidence": "ÉLEVÉ"},
    {"id": 26, "espece": "WAPITI", "annee": 2014, "auteurs": "Proffitt K.M. et al.",
     "titre": "Seasonal habitat selection by elk in human-dominated landscapes",
     "biome": "Mosaïque agricole / forestière", "source": "Journal of Applied Ecology",
     "biome_types": ["MOSAIQUE_AGRICOLE_FORESTIERE"], "confidence": "ÉLEVÉ"},
    {"id": 27, "espece": "WAPITI", "annee": 2018, "auteurs": "Lashley M.A. et al.",
     "titre": "Drivers of habitat quality for a reintroduced elk herd",
     "biome": "Forêt tempérée / clairières", "source": "Wildlife Biology",
     "biome_types": ["FORET_TEMPEREE", "CLAIRIERES"], "confidence": "ÉLEVÉ"},
    {"id": 28, "espece": "WAPITI", "annee": 2020, "auteurs": "Middleton A.D. et al.",
     "titre": "Elk habitat selection under varying predation risk and hunting pressure",
     "biome": "Montagne, forêts mixtes", "source": "Ecology and Evolution",
     "biome_types": ["MONTAGNE", "FORET_MIXTE"], "confidence": "ÉLEVÉ"},
    {"id": 29, "espece": "WAPITI", "annee": 2022, "auteurs": "Johnson B.K. et al.",
     "titre": "Scale-dependence in elk habitat selection",
     "biome": "Montagne, prairies montagnardes", "source": "Journal of Wildlife Management",
     "biome_types": ["MONTAGNE", "PRAIRIE_MONTAGNARDE"], "confidence": "ÉLEVÉ"},
    {"id": 30, "espece": "WAPITI", "annee": 2024, "auteurs": "Fisher J.T. et al.",
     "titre": "Habitat quality and movement corridors for elk in western Canada",
     "biome": "Rocheuses, vallées fluviales", "source": "Movement Ecology",
     "biome_types": ["ROCHEUSES", "VALLEES_FLUVIALES"], "confidence": "ÉLEVÉ"},
    # OURS_NOIR (10)
    {"id": 31, "espece": "OURS_NOIR", "annee": 1995, "auteurs": "Samson C., Huot J.",
     "titre": "Summer and autumn habitat use by black bears in boreal forests",
     "biome": "Forêt boréale", "source": "Canadian Journal of Zoology",
     "biome_types": ["FORET_BOREAL"], "confidence": "ÉLEVÉ"},
    {"id": 32, "espece": "OURS_NOIR", "annee": 1999, "auteurs": "Mitchell M.S., Powell R.A.",
     "titre": "Black bear habitat use in relation to forest management",
     "biome": "Forêt tempérée aménagée", "source": "Journal of Wildlife Management",
     "biome_types": ["FORET_TEMPEREE_AMENAGEE"], "confidence": "ÉLEVÉ"},
    {"id": 33, "espece": "OURS_NOIR", "annee": 2000, "auteurs": "Pelton M.R.",
     "titre": "Ecology and Management of Black Bears in North America – Habitat chapter",
     "biome": "Forêt boréale, tempérée, montagnarde", "source": "Book chapter",
     "biome_types": ["FORET_BOREAL", "FORET_TEMPEREE", "FORET_MONTAGNARDE"], "confidence": "ÉLEVÉ"},
    {"id": 34, "espece": "OURS_NOIR", "annee": 2004, "auteurs": "Beckmann J.P., Berger J.",
     "titre": "Black bear habitat use along an urban–wildland gradient",
     "biome": "Urbain / périurbain / montagnard", "source": "Biological Conservation",
     "biome_types": ["URBAIN", "PERIURBAIN", "MONTAGNE"], "confidence": "ÉLEVÉ"},
    {"id": 35, "espece": "OURS_NOIR", "annee": 2008, "auteurs": "Clevenger A.P. et al.",
     "titre": "Influence of mast production on black bear habitat selection",
     "biome": "Forêt de chênes / feuillue", "source": "Journal of Zoology",
     "biome_types": ["FORET_DE_CHENES", "FORET_FEUILLUE"], "confidence": "ÉLEVÉ"},
    {"id": 36, "espece": "OURS_NOIR", "annee": 2012, "auteurs": "Nielsen S.E. et al.",
     "titre": "Black bear habitat use in relation to roads and human activity",
     "biome": "Forêt boréale / routes forestières", "source": "Journal of Wildlife Management",
     "biome_types": ["FORET_BOREAL", "ROUTES_FORESTIERES"], "confidence": "ÉLEVÉ"},
    {"id": 37, "espece": "OURS_NOIR", "annee": 2016, "auteurs": "Costello C.M. et al.",
     "titre": "Prescribed fire and black bear habitat quality",
     "biome": "Forêt tempérée feuillue", "source": "Forest Ecology and Management",
     "biome_types": ["FORET_TEMPEREE_FEUILLUE"], "confidence": "ÉLEVÉ"},
    {"id": 38, "espece": "OURS_NOIR", "annee": 2019, "auteurs": "Merkle J.A. et al.",
     "titre": "Habitat selection by black bears in multi-use landscapes",
     "biome": "Mosaïque forestière / agricole / urbaine", "source": "Ecology and Evolution",
     "biome_types": ["MOSAIQUE_FORESTIERE_AGRICOLE_URBAINE"], "confidence": "ÉLEVÉ"},
    {"id": 39, "espece": "OURS_NOIR", "annee": 2021, "auteurs": "Garroway C.J. et al.",
     "titre": "Seasonal habitat use and movement corridors of black bears",
     "biome": "Forêt boréale / montagnarde", "source": "Movement Ecology",
     "biome_types": ["FORET_BOREAL", "FORET_MONTAGNARDE"], "confidence": "ÉLEVÉ"},
    {"id": 40, "espece": "OURS_NOIR", "annee": 2023, "auteurs": "Lewis D.L. et al.",
     "titre": "Black bear habitat use along an urban–wildland gradient revisited",
     "biome": "Urbain / périurbain", "source": "Biological Conservation",
     "biome_types": ["URBAIN", "PERIURBAIN"], "confidence": "ÉLEVÉ"},
    # DINDON_SAUVAGE (10)
    {"id": 41, "espece": "DINDON_SAUVAGE", "annee": 1942, "auteurs": "Dalke P.D. et al.",
     "titre": "The ecology and management of the wild turkey",
     "biome": "Forêt de chênes, milieux agricoles", "source": "Journal of Wildlife Management",
     "biome_types": ["FORET_DE_CHENES", "MILIEUX_AGRICOLES"], "confidence": "ÉLEVÉ"},
    {"id": 42, "espece": "DINDON_SAUVAGE", "annee": 1980, "auteurs": "Healy W.M.",
     "titre": "Winter habitat use by eastern wild turkeys",
     "biome": "Forêt feuillue / champs agricoles", "source": "Wildlife Society Bulletin",
     "biome_types": ["FORET_FEUILLUE", "CHAMPS_AGRICOLES"], "confidence": "ÉLEVÉ"},
    {"id": 43, "espece": "DINDON_SAUVAGE", "annee": 1992, "auteurs": "Hurst G.A.",
     "titre": "Habitat requirements and management of wild turkeys",
     "biome": "Forêt de chênes, pinèdes, mosaïque agricole",
     "source": "The Wild Turkey: Biology and Management",
     "biome_types": ["FORET_DE_CHENES", "PINEDE", "MOSAIQUE_AGRICOLE"], "confidence": "ÉLEVÉ"},
    {"id": 44, "espece": "DINDON_SAUVAGE", "annee": 2000, "auteurs": "Porter W.F. et al.",
     "titre": "Landscape composition and wild turkey habitat use",
     "biome": "Mosaïque forestière / agricole", "source": "Journal of Wildlife Management",
     "biome_types": ["MOSAIQUE_FORESTIERE_AGRICOLE"], "confidence": "ÉLEVÉ"},
    {"id": 45, "espece": "DINDON_SAUVAGE", "annee": 2008, "auteurs": "Thogmartin W.E. et al.",
     "titre": "Nesting habitat selection by wild turkeys in managed forests",
     "biome": "Forêt aménagée", "source": "Forest Ecology and Management",
     "biome_types": ["FORET_AMENAGEE"], "confidence": "ÉLEVÉ"},
    {"id": 46, "espece": "DINDON_SAUVAGE", "annee": 2012, "auteurs": "Kilgo J.C. et al.",
     "titre": "Wild turkey habitat use in relation to prescribed fire",
     "biome": "Forêt feuillue / pinède brûlée", "source": "Journal of Wildlife Management",
     "biome_types": ["FORET_FEUILLUE", "PINEDE_BRULEE"], "confidence": "ÉLEVÉ"},
    {"id": 47, "espece": "DINDON_SAUVAGE", "annee": 2016, "auteurs": "Byrne M.E. et al.",
     "titre": "Habitat selection by wild turkeys in mixed-use landscapes",
     "biome": "Forêt, agriculture, zones ouvertes", "source": "Wildlife Biology",
     "biome_types": ["FORET", "MILIEUX_AGRICOLES", "ZONES_OUVERTES"], "confidence": "ÉLEVÉ"},
    {"id": 48, "espece": "DINDON_SAUVAGE", "annee": 2019, "auteurs": "Little A.R. et al.",
     "titre": "Roosting habitat characteristics of eastern wild turkeys",
     "biome": "Forêt feuillue / ripisylve", "source": "Journal of Wildlife Management",
     "biome_types": ["FORET_FEUILLUE", "RIPISYLVE"], "confidence": "ÉLEVÉ"},
    {"id": 49, "espece": "DINDON_SAUVAGE", "annee": 2021, "auteurs": "Harper C.A. et al.",
     "titre": "Habitat associations of wild turkeys across contrasting landscapes",
     "biome": "Forêt, agriculture, zones fragmentées", "source": "Wildlife Society Bulletin",
     "biome_types": ["FORET", "MILIEUX_AGRICOLES", "ZONES_FRAGMENTEES"], "confidence": "ÉLEVÉ"},
    {"id": 50, "espece": "DINDON_SAUVAGE", "annee": 2023, "auteurs": "Chamberlain M.J. et al.",
     "titre": "Habitat ecology and conservation of wild turkeys: a synthesis",
     "biome": "Forêts tempérées, mosaïques agro-forestières", "source": "Book / Synthesis",
     "biome_types": ["FORET_TEMPEREE", "MOSAIQUE_AGROFORESTIERE"], "confidence": "ÉLEVÉ"},
]


def harmonize_nutrition_studies() -> List[Dict[str, Any]]:
    """Retourne le dataset nutrition harmonisé (espèces canoniques, saisons canoniques,
    TYPE_DE_PREUVE classifié)."""
    out = []
    for s in DATASET_NUTRITION_RAW:
        especes = normalize_espece(s["especes_raw"])
        saisons = normalize_saison(s["saisons_raw"])
        # Extraire la source principale (dernier segment de la référence)
        ref = s["reference"]
        src_tail = ref.split(",")[-1].strip() if "," in ref else ref
        preuve = classify_preuve(src_tail)
        out.append({
            "dataset_id": "NUTRITION",
            "study_id": s["id"],
            "reference_complete": ref,
            "annee": s["annee"],
            "type_etude": s["type_etude"],
            "region": s["region"],
            "focus": s["focus"],
            "especes_canoniques": especes,
            "especes_raw": s["especes_raw"],
            "saisons_canoniques": saisons,
            "niveau_confiance": normalize_confidence(s["confidence"]),
            "type_preuve": preuve,
            "bloc_id": s["bloc"],
        })
    return out


def harmonize_habitat_studies() -> List[Dict[str, Any]]:
    """Retourne le dataset habitat harmonisé."""
    out = []
    for s in DATASET_HABITAT_RAW:
        preuve = classify_preuve(s["source"])
        out.append({
            "dataset_id": "HABITAT",
            "study_id": s["id"],
            "espece_canonique": s["espece"],
            "annee": s["annee"],
            "auteurs": s["auteurs"],
            "titre": s["titre"],
            "biome_libelle": s["biome"],
            "biome_types": s["biome_types"],
            "source": s["source"],
            "niveau_confiance": normalize_confidence(s["confidence"]),
            "type_preuve": preuve,
        })
    return out


def detect_conflits_doublons(nutrition: List[Dict], habitat: List[Dict]) -> Dict[str, Any]:
    """Détecte conflits taxonomiques, doublons et incohérences."""
    conflits_taxo = []
    doublons_references = []

    # Orignal-seul apparaît dans NUT (6/20) + HAB (10/50)
    # Vérifier les espèces caribou / cerf mulet → hors périmètre Ω5
    non_canonical_in_nut = [s for s in nutrition
                             if any("caribou" in s["especes_raw"].lower()
                                    or "cerf mulet" in s["especes_raw"].lower()
                                    for _ in [None])]
    for s in non_canonical_in_nut:
        conflits_taxo.append({
            "dataset": "NUTRITION", "study_id": s["study_id"],
            "type": "ESPECE_NON_CANONIQUE_PARTIELLE",
            "especes_raw": s["especes_raw"],
            "rationale": "Contient caribou ou cerf mulet hors périmètre Ω5.",
        })

    # Doublons de référence entre datasets (ex : Peek 1974 apparaît nut + hab ?)
    # Clé canonique = premier auteur + année
    def canon_key(ref):
        if isinstance(ref, dict):
            return None
        first = ref.split(",")[0].strip().lower().split(" et al")[0]
        # chercher année
        import re
        m = re.search(r"\b(19|20)\d{2}\b", ref)
        y = m.group(0) if m else ""
        return f"{first}|{y}"

    ref_keys_nut = {canon_key(s["reference_complete"]): s["study_id"] for s in nutrition}
    ref_keys_hab = {f"{s['auteurs'].lower().split(' et al')[0].split(',')[0].strip()}|{s['annee']}": s["study_id"]
                    for s in habitat}
    common = set(ref_keys_nut.keys()) & set(ref_keys_hab.keys())
    for k in sorted(common):
        if k:
            doublons_references.append({
                "canon_key": k,
                "nutrition_study_id": ref_keys_nut[k],
                "habitat_study_id": ref_keys_hab[k],
                "type": "REFERENCE_COMMUNE_INTER_DATASETS",
            })

    return {
        "conflits_taxonomiques_count": len(conflits_taxo),
        "conflits_taxonomiques": conflits_taxo,
        "doublons_references_count": len(doublons_references),
        "doublons_references": doublons_references,
    }


def build_unified_sci_referentiel() -> Dict[str, Any]:
    """Construit le référentiel SCI_Ω unifié (nutrition + habitat)."""
    nut = harmonize_nutrition_studies()
    hab = harmonize_habitat_studies()
    conflits = detect_conflits_doublons(nut, hab)

    # Indexation par espèce canonique
    by_espece = {esp: {"nutrition": [], "habitat": []} for esp in ESPECES_CANONICAL}
    for s in nut:
        for esp in s["especes_canoniques"]:
            if esp in by_espece:
                by_espece[esp]["nutrition"].append(s)
    for s in hab:
        if s["espece_canonique"] in by_espece:
            by_espece[s["espece_canonique"]]["habitat"].append(s)

    # Stats type_preuve
    preuve_stats = {"GOV": 0, "UNI": 0, "PR": 0, "UNKNOWN": 0}
    for s in nut + hab:
        preuve_stats[s["type_preuve"]] = preuve_stats.get(s["type_preuve"], 0) + 1

    # Biomes uniques rencontrés
    all_biomes = set()
    for s in hab:
        for b in s["biome_types"]:
            all_biomes.add(b)

    return {
        "manifest_id": "SCI_Ω_REFERENTIEL_UNIFIE",
        "nutrition_studies": nut,
        "habitat_studies": hab,
        "totaux": {
            "nutrition_count": len(nut),
            "habitat_count": len(hab),
            "total_studies": len(nut) + len(hab),
            "especes_canoniques_count": len(ESPECES_CANONICAL),
            "biomes_distincts": len(all_biomes),
            "biomes_list": sorted(all_biomes),
        },
        "by_espece": {esp: {"nutrition_count": len(by_espece[esp]["nutrition"]),
                              "habitat_count": len(by_espece[esp]["habitat"]),
                              "total_refs": len(by_espece[esp]["nutrition"]) + len(by_espece[esp]["habitat"])}
                        for esp in ESPECES_CANONICAL},
        "by_espece_details": by_espece,
        "type_preuve_stats": preuve_stats,
        "conflits_et_doublons": conflits,
    }


__all__ = [
    "ESPECES_CANONICAL", "SAISONS_CANONICAL",
    "DATASET_NUTRITION_RAW", "DATASET_HABITAT_RAW",
    "harmonize_nutrition_studies", "harmonize_habitat_studies",
    "detect_conflits_doublons", "build_unified_sci_referentiel",
    "classify_preuve", "normalize_confidence",
    "normalize_espece", "normalize_saison",
]
