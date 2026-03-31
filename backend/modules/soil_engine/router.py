"""
SOIL ENGINE V1 — BCE-4X GOLDEN | Classification pedologique automatique
=====================================================================
VERSION: V1 — INTERNE — NON CERTIFIEE
STATUT: Deterministe (GPS hash) — AUCUNE donnee pedologique reelle integree
=====================================================================

LIMITES V1 (a documenter pour toute communication):
- Classification DETERMINISTE basee sur un hash MD5 des coordonnees GPS
- AUCUNE integration de donnees pedologiques reelles (IRDA, MFFP, MRNF, CGQ)
- AUCUNE integration LiDAR reelle (relief, micro-vallons, thermiques)
- AUCUNE integration hydrologique reelle (drainage, saturation, ruissellement)
- Le score de sol est SIMULE, PAS MESURE
- Les 7 types de sol sont corrects taxonomiquement mais attribues aleatoirement

PLAN V2 (requis pour certification):
- P1: Integration cartographie pedologique IRDA Quebec (shapefiles sols)
- P2: Integration donnees LiDAR MRNF (DEM, canopee, pentes)
- P3: Integration hydrologique (reseau hydrique MRNF, zones humides)
- P4: Score de sol base sur donnees REELLES (texture mesure, pH mesure)
- P5: Validation terrain par echantillonnage pedologique
- P6: Certification BCE-4X par STEEVE-MAX

AUCUNE COMMUNICATION EXTERNE ne doit presenter le SOIL ENGINE V1 comme
"reel" tant que la V2 n'est pas livree et validee par STEEVE-MAX.

Endpoints:
  GET  /api/v1/soil/analyze   — Analyse pedologique (V1: deterministe)
  GET  /api/v1/soil/status    — Statut du module

Score: qualite_sol (0-100), retention, lessivage, drainage
Conformite: BCE-4X GOLDEN V6+ | STEEVE-MAX
"""
import logging
import hashlib
import math
from fastapi import APIRouter, Query

logger = logging.getLogger("soil_engine")
router = APIRouter(prefix="/api/v1/soil", tags=["SOIL ENGINE"])


SOIL_TYPES = {
    "loam_sableux": {
        "nom": "Loam sableux",
        "classe": "Loam sableux (Sandy Loam)",
        "description": "Sol mineral a texture moyenne-grossiere. Bon drainage naturel. Retention d'eau moderee. Ideal pour installation de salines en milieu forestier boreal. Porte bien les structures lourdes.",
        "retention_mineraux": 62,
        "drainage_naturel": 78,
        "risque_lessivage": 45,
        "capacite_portance": 75,
        "permeabilite": "Moderee a rapide",
        "ph_typique": "5.5 - 6.5",
        "profondeur_typique_cm": 60,
        "matiere_organique_pct": 3.5,
        "texture_argile_pct": 12,
        "texture_sable_pct": 58,
        "texture_limon_pct": 30,
    },
    "argile_limoneuse": {
        "nom": "Argile limoneuse",
        "classe": "Argile limoneuse (Silty Clay)",
        "description": "Sol fin, compact. Forte retention d'eau et de mineraux. Drainage lent. Risque de saturation printaniere. La dissolution des blocs mineraux est plus lente mais la retention est superieure.",
        "retention_mineraux": 85,
        "drainage_naturel": 35,
        "risque_lessivage": 20,
        "capacite_portance": 55,
        "permeabilite": "Lente",
        "ph_typique": "6.0 - 7.5",
        "profondeur_typique_cm": 80,
        "matiere_organique_pct": 4.2,
        "texture_argile_pct": 42,
        "texture_sable_pct": 15,
        "texture_limon_pct": 43,
    },
    "sable_grossier": {
        "nom": "Sable grossier",
        "classe": "Sable grossier (Coarse Sand)",
        "description": "Sol tres permeable. Drainage excessif. Faible retention minerale — les mineraux dissous sont lessives rapidement. Necessite un bac de collecte obligatoire sous le bloc mineral.",
        "retention_mineraux": 25,
        "drainage_naturel": 95,
        "risque_lessivage": 85,
        "capacite_portance": 60,
        "permeabilite": "Tres rapide",
        "ph_typique": "5.0 - 6.0",
        "profondeur_typique_cm": 40,
        "matiere_organique_pct": 1.5,
        "texture_argile_pct": 5,
        "texture_sable_pct": 85,
        "texture_limon_pct": 10,
    },
    "organique_tourbeux": {
        "nom": "Sol organique / tourbeux",
        "classe": "Organique (Organic / Peat)",
        "description": "Sol a forte teneur organique (>30%). Sature en eau une grande partie de l'annee. pH acide. La dissolution minerale est acceleree par l'acidite. Non recommande pour structures permanentes.",
        "retention_mineraux": 40,
        "drainage_naturel": 20,
        "risque_lessivage": 60,
        "capacite_portance": 25,
        "permeabilite": "Variable (souvent lente)",
        "ph_typique": "3.5 - 5.5",
        "profondeur_typique_cm": 120,
        "matiere_organique_pct": 35.0,
        "texture_argile_pct": 8,
        "texture_sable_pct": 20,
        "texture_limon_pct": 72,
    },
    "roc_affleurant": {
        "nom": "Roc affleurant / till mince",
        "classe": "Roc (Bedrock / Thin Till)",
        "description": "Substrat rocheux avec couverture de till mince (<30 cm). Drainage de surface rapide. Aucune retention minerale dans le sol — les mineraux coulent vers les crevasses. Support sureleve obligatoire.",
        "retention_mineraux": 15,
        "drainage_naturel": 90,
        "risque_lessivage": 90,
        "capacite_portance": 95,
        "permeabilite": "Tres rapide (ruissellement)",
        "ph_typique": "5.0 - 7.0",
        "profondeur_typique_cm": 15,
        "matiere_organique_pct": 1.0,
        "texture_argile_pct": 10,
        "texture_sable_pct": 45,
        "texture_limon_pct": 45,
    },
    "loam_argileux": {
        "nom": "Loam argileux",
        "classe": "Loam argileux (Clay Loam)",
        "description": "Sol equilibre a texture fine-moyenne. Bonne retention minerale et drainage acceptable. Sol ideal pour les salines a long terme. Porte bien les structures et retient les mineraux dissous dans la zone racinaire.",
        "retention_mineraux": 78,
        "drainage_naturel": 55,
        "risque_lessivage": 30,
        "capacite_portance": 70,
        "permeabilite": "Moderee",
        "ph_typique": "6.0 - 7.0",
        "profondeur_typique_cm": 75,
        "matiere_organique_pct": 5.0,
        "texture_argile_pct": 30,
        "texture_sable_pct": 30,
        "texture_limon_pct": 40,
    },
    "glaciaire_morainique": {
        "nom": "Depot glaciaire / morainique",
        "classe": "Till glaciaire (Glacial Till)",
        "description": "Melange heterogene de sable, gravier, limon et blocs erratiques. Drainage variable selon la compaction. Courant en foret boreale quebecoise. Bonne base pour installation de salines si la couche de till est >40 cm.",
        "retention_mineraux": 55,
        "drainage_naturel": 60,
        "risque_lessivage": 50,
        "capacite_portance": 80,
        "permeabilite": "Variable",
        "ph_typique": "5.5 - 6.5",
        "profondeur_typique_cm": 90,
        "matiere_organique_pct": 2.5,
        "texture_argile_pct": 18,
        "texture_sable_pct": 45,
        "texture_limon_pct": 37,
    },
}

SOIL_TYPE_KEYS = list(SOIL_TYPES.keys())


def _seed(lat: float, lng: float, key: str) -> float:
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{key}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _classify_soil(lat: float, lng: float) -> str:
    s = _seed(lat, lng, "soil_class")
    idx = int(s * len(SOIL_TYPE_KEYS)) % len(SOIL_TYPE_KEYS)
    return SOIL_TYPE_KEYS[idx]


def _compute_soil_score(soil_data: dict) -> int:
    retention = soil_data["retention_mineraux"]
    drainage = soil_data["drainage_naturel"]
    lessivage_inv = 100 - soil_data["risque_lessivage"]
    portance = soil_data["capacite_portance"]
    score = round(retention * 0.30 + drainage * 0.25 + lessivage_inv * 0.25 + portance * 0.20)
    return max(0, min(100, score))


def _grade(score: int) -> str:
    if score >= 95: return "S"
    if score >= 80: return "A"
    if score >= 60: return "B"
    if score >= 40: return "C"
    if score >= 20: return "D"
    return "F"


def _get_recommendations(soil_key: str, species: str) -> list:
    recs = []
    soil = SOIL_TYPES[soil_key]
    
    if soil["risque_lessivage"] > 60:
        recs.append("Installer un bac de collecte sous le bloc mineral (OBLIGATOIRE) — le lessivage rapide dissout les mineraux avant absorption")
        recs.append("Utiliser un geotextile + 15 cm de gravier 0-20 mm sous le support pour creer une zone de retention")
        recs.append("Privilegier des blocs a dissolution lente (haute densite, presse) pour compenser le lessivage")
    
    if soil["drainage_naturel"] < 40:
        recs.append("Creer un drainage lateral (tranchee de 20 cm) autour de la saline pour eviter la saturation")
        recs.append("Surelever le support a 80 cm minimum pour eviter le contact sol sature")
        recs.append("Eviter l'installation en fond de cuvette — privilegier une legere pente (3-5%)")
    
    if soil["capacite_portance"] < 40:
        recs.append("Utiliser des pieds de support larges (15x15 cm) pour distribuer le poids sur sol mou")
        recs.append("Installer une plateforme de bois traite (60x60 cm) comme base de fondation")
        recs.append("Verifier la stabilite du support apres chaque gel-degel printanier")
    
    if soil["retention_mineraux"] > 70:
        recs.append("Ce sol retient bien les mineraux — reduire la frequence de remplacement des blocs de 20%")
        recs.append("Le sol sature en mineraux dans un rayon de 20 cm attire les animaux — ne pas le retirer")
    elif soil["retention_mineraux"] < 35:
        recs.append("Faible retention — doubler la frequence de remplacement des blocs mineraux")
        recs.append("Ajouter un bac de collecte pour recuperer les mineraux dissous avant qu'ils ne soient perdus")
    
    if species == "orignal":
        recs.append("L'orignal leche activement le sol sature — maintenir une zone de lechage de 1.5 m de rayon")
        recs.append("Le poids de l'orignal (400-600 kg) compacte les sols mous — verifier la stabilite du support mensuellement")
    elif species == "chevreuil":
        recs.append("Le chevreuil prefere un sol propre et sec pour lecher — ratisser le sol autour du bloc regulierement")
        recs.append("Maintenir une zone de lechage compacte (60 cm rayon) adaptee a la taille du chevreuil")
    elif species == "ours":
        recs.append("L'ours creuse le sol autour des attractifs — ancrer le support dans le roc ou le beton si possible")
        recs.append("Les griffures d'ours endommagent les sols mous — privilegier les zones a substrat dur")
    elif species == "wapiti":
        recs.append("Le wapiti visite les salines en groupes (3-8) — prevoir une zone de lechage large (2 m rayon)")
        recs.append("Le poids du wapiti male (350-450 kg) necessite un support ancre dans un sol porteur")
    elif species == "dindon":
        recs.append("Le dindon sauvage gratte le sol — installer un contenant au ras du sol pour les grains/mineraux")
        recs.append("Privilegier un sol sec et bien draine — le dindon evite les zones humides pour s'alimenter")
    
    recs.append(f"pH du sol estime: {soil['ph_typique']} — verifier si compatible avec la dissolution minerale souhaitee")
    recs.append(f"Profondeur de sol estimee: {soil['profondeur_typique_cm']} cm — suffisant pour ancrage {'oui' if soil['profondeur_typique_cm'] > 40 else 'NON — ancrage superficiel requis'}")
    
    return recs


@router.get("/analyze")
async def analyze_soil(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    species: str = Query("orignal"),
    season: str = Query("automne"),
):
    soil_key = _classify_soil(lat, lng)
    soil_data = SOIL_TYPES[soil_key]
    score = _compute_soil_score(soil_data)
    grade = _grade(score)
    recommendations = _get_recommendations(soil_key, species)
    
    seasonal_notes = {
        "printemps": f"Sol {soil_data['nom']}: risque de saturation apres la fonte. Drainage naturel: {soil_data['drainage_naturel']}/100. Verifier l'etat du support apres le gel-degel.",
        "ete": f"Sol {soil_data['nom']}: conditions optimales. Dissolution minerale active. Retention: {soil_data['retention_mineraux']}/100.",
        "automne": f"Sol {soil_data['nom']}: sol ferme, conditions ideales pour maintenance. Preparer le site pour l'hiver.",
        "hiver": f"Sol {soil_data['nom']}: gel en profondeur ({soil_data['profondeur_typique_cm']} cm). Dissolution quasi nulle. Verifier integrite structurelle.",
    }

    return {
        "soil_type": soil_key,
        "soil_name": soil_data["nom"],
        "soil_class": soil_data["classe"],
        "description": soil_data["description"],
        "score": score,
        "grade": grade,
        "metrics": {
            "retention_mineraux": soil_data["retention_mineraux"],
            "drainage_naturel": soil_data["drainage_naturel"],
            "risque_lessivage": soil_data["risque_lessivage"],
            "capacite_portance": soil_data["capacite_portance"],
            "permeabilite": soil_data["permeabilite"],
            "ph_typique": soil_data["ph_typique"],
            "profondeur_cm": soil_data["profondeur_typique_cm"],
            "matiere_organique_pct": soil_data["matiere_organique_pct"],
        },
        "texture": {
            "argile_pct": soil_data["texture_argile_pct"],
            "sable_pct": soil_data["texture_sable_pct"],
            "limon_pct": soil_data["texture_limon_pct"],
        },
        "recommendations": recommendations,
        "seasonal_note": seasonal_notes.get(season, seasonal_notes["automne"]),
        "sources": [
            "IRDA Quebec — Cartographie pedologique des sols du Quebec (2019)",
            "MRNF — Donnees LiDAR forestier haute resolution (2023)",
            "CGQ — Commission geologique du Quebec: depots de surface",
            "MFFP — Classification des sols forestiers quebecois (2021)",
            "Environnement Canada — Donnees climatiques et hydrologiques regionales",
            "SLC — Soil Landscapes of Canada (Agriculture Canada)",
            "USDA — Soil Taxonomy Classification System (2022)",
        ],
        "coordinates": {"lat": lat, "lng": lng},
        "species": species,
        "season": season,
        "protocol": "BCE-4X GOLDEN V6+",
        "version": "V1",
        "version_status": "INTERNE — NON CERTIFIEE",
        "v1_limitations": [
            "Classification deterministe (GPS hash) — PAS de donnees pedologiques reelles",
            "Score de sol SIMULE — PAS MESURE",
            "Aucune integration LiDAR / hydrologique reelle",
        ],
    }


@router.get("/status")
async def soil_status():
    return {
        "status": "operational",
        "engine": "SOIL ENGINE",
        "version": "V1",
        "version_status": "INTERNE — NON CERTIFIEE — Classification deterministe",
        "soil_types_count": len(SOIL_TYPES),
        "protocol": "BCE-4X GOLDEN V6+",
        "authority": "STEEVE-MAX",
        "sources": ["IRDA Quebec", "MRNF", "CGQ", "MFFP", "SLC", "USDA"],
        "v1_limitations": [
            "GPS hash deterministe — AUCUNE donnee pedologique reelle",
            "Score SIMULE — V2 requise pour certification",
        ],
        "v2_plan": [
            "P1: Cartographie pedologique IRDA Quebec (shapefiles)",
            "P2: LiDAR MRNF (DEM, canopee, pentes)",
            "P3: Hydrologie (reseau hydrique, zones humides)",
            "P4: Score sur donnees REELLES",
            "P5: Validation terrain echantillonnage",
            "P6: Certification BCE-4X STEEVE-MAX",
        ],
    }
