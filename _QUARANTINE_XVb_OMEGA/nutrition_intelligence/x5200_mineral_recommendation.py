"""
×5200 — MINERAL_RECOMMENDATION_ENGINE
Analyse des deficits et exces par mineral.
Recommandations intelligentes selon sol, saison, espece.
"""
from .x5100_mineral_score import compute_mineral_score, MINERAL_NAMES

MINERAL_PRODUCTS = {
    "Na": {
        "product": "Bloc mineral sel gemme pur",
        "brand": "Trophy Rock Four65",
        "dosage": "1 bloc 9kg / 6-8 semaines",
        "price_cad": 24.99,
    },
    "Ca": {
        "product": "Supplement calcium + phosphore",
        "brand": "Mineral Lick Pro-Cal",
        "dosage": "2kg / m2 / saison",
        "price_cad": 18.99,
    },
    "P": {
        "product": "Phosphate mineral enrichi",
        "brand": "BioMineral P-Plus",
        "dosage": "1.5kg / m2 / saison",
        "price_cad": 22.49,
    },
    "K": {
        "product": "Potassium mineral naturel",
        "brand": "Whitetail Institute K-Source",
        "dosage": "1kg / m2 / saison",
        "price_cad": 15.99,
    },
    "Mg": {
        "product": "Magnesium + oligo-elements",
        "brand": "Evolved Habitats Mag-Mix",
        "dosage": "1.5kg / m2 / saison",
        "price_cad": 19.99,
    },
    "Zn": {
        "product": "Zinc chelate supplement",
        "brand": "Purina AntlerMax Zn",
        "dosage": "500g / bloc / saison",
        "price_cad": 28.99,
    },
    "Se": {
        "product": "Selenium + Vitamine E",
        "brand": "Ridley Se-Vit Block",
        "dosage": "1 bloc 10kg / 8 semaines",
        "price_cad": 32.99,
    },
    "Fe": {
        "product": "Fer chelate mineral",
        "brand": "Sportsman's Choice Fe-Block",
        "dosage": "1 bloc 5kg / 10 semaines",
        "price_cad": 14.99,
    },
}

SOIL_RECOMMENDATIONS = {
    "acide": "Sol acide (pH < 5.5): forte lixiviation des cations. Prioriser Na, Ca, Mg. Utiliser souche bois mou pour liberation progressive.",
    "loam": "Sol loam equilibre: bonne retention minerale. Completer les deficits specifiques. Souche bois dur ou bois mou selon preference.",
    "coniferes": "Sol sous coniferes: acidification naturelle, faible biodisponibilite P et Se. Priorite absolue: P, Se, Ca.",
    "mixte": "Sol mixte: disponibilite moyenne. Ajuster selon carences mesurees. Les deux types de souche conviennent.",
    "sableux": "Sol sableux: drainage rapide, pertes minerales frequentes. Reactivations plus frequentes. Souche bois mou recommandee.",
}


def compute_recommendations(species: str, season: str, soil_type: str, site_minerals: dict = None) -> dict:
    """
    Genere les recommandations minerales basees sur le score engine.
    """
    score_data = compute_mineral_score(species, season, soil_type, site_minerals)
    minerals = score_data["scores_par_mineral"]

    recommendations = []
    for mineral_key, data in minerals.items():
        zone = data["zone"]
        product = MINERAL_PRODUCTS.get(mineral_key, {})

        if zone == "rouge":
            priority = "CRITIQUE"
            action = f"Supplementation immediate en {data['name']}. Deficit severe ({data['score']}%)."
        elif zone == "jaune":
            priority = "RECOMMANDE"
            action = f"Supplementation conseillee en {data['name']}. Zone marginale ({data['score']}%)."
        else:
            priority = "OPTIONNEL"
            action = f"{data['name']} en zone verte ({data['score']}%). Maintien par bloc mineral standard."

        recommendations.append({
            "mineral": mineral_key,
            "name": data["name"],
            "score": data["score"],
            "zone": zone,
            "priority": priority,
            "action": action,
            "product": product.get("product", "N/A"),
            "brand": product.get("brand", "N/A"),
            "dosage": product.get("dosage", "N/A"),
            "price_cad": product.get("price_cad", 0),
        })

    recommendations.sort(key=lambda r: {"CRITIQUE": 0, "RECOMMANDE": 1, "OPTIONNEL": 2}[r["priority"]])

    return {
        "score_data": score_data,
        "recommendations": recommendations,
        "soil_advice": SOIL_RECOMMENDATIONS.get(soil_type, SOIL_RECOMMENDATIONS["mixte"]),
        "critical_count": sum(1 for r in recommendations if r["priority"] == "CRITIQUE"),
        "recommended_count": sum(1 for r in recommendations if r["priority"] == "RECOMMANDE"),
    }
