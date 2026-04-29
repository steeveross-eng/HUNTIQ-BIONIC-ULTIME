"""
x6010 — PRODUCT_QUALITY_ANALYZER
12 criteres d'analyse qualite + ratio cout/efficacite
pour chaque produit du catalogue x6000.
BCE-4X / STEEVE-MAX V6

CRITERES (12):
  1. purete_minerale — Concentration minerale effective (% poids actif)
  2. biodisponibilite — Forme chelate vs oxide (assimilation reelle)
  3. duree_terrain — Resistance intemperies, dissolution progressive
  4. attractivite — Attrait olfactif et gustatif pour l'espece
  5. securite_toxicologique — Absence de metaux lourds, contaminants
  6. homogeneite — Uniformite de la composition dans le bloc/supplement
  7. conditionnement — Qualite emballage, protection humidite
  8. tracabilite — Lot, origine matieres premieres, chaine de production
  9. rendement_surface — m2 couverts par unite de produit
  10. rapport_cout_efficacite — Score global / prix par semaine
  11. stabilite_stockage — Duree de vie en entrepot (mois)
  12. impact_environnemental — Residus sol, lessivage, ecotoxicite
"""

# Donnees qualite par produit (valeurs 0-100 pour chaque critere)
QUALITY_DATA = {
    "trophy_rock_four65": {
        "purete_minerale": 82, "biodisponibilite": 78, "duree_terrain": 90,
        "attractivite": 95, "securite_toxicologique": 88, "homogeneite": 75,
        "conditionnement": 80, "tracabilite": 85, "rendement_surface": 72,
        "rapport_cout_efficacite": 88, "stabilite_stockage": 85, "impact_environnemental": 82,
    },
    "pro_cal_lick": {
        "purete_minerale": 90, "biodisponibilite": 85, "duree_terrain": 80,
        "attractivite": 78, "securite_toxicologique": 92, "homogeneite": 88,
        "conditionnement": 82, "tracabilite": 80, "rendement_surface": 85,
        "rapport_cout_efficacite": 90, "stabilite_stockage": 88, "impact_environnemental": 85,
    },
    "biomineral_p_plus": {
        "purete_minerale": 88, "biodisponibilite": 90, "duree_terrain": 78,
        "attractivite": 72, "securite_toxicologique": 90, "homogeneite": 92,
        "conditionnement": 85, "tracabilite": 88, "rendement_surface": 80,
        "rapport_cout_efficacite": 82, "stabilite_stockage": 85, "impact_environnemental": 78,
    },
    "whitetail_k_source": {
        "purete_minerale": 80, "biodisponibilite": 75, "duree_terrain": 70,
        "attractivite": 82, "securite_toxicologique": 85, "homogeneite": 78,
        "conditionnement": 75, "tracabilite": 72, "rendement_surface": 68,
        "rapport_cout_efficacite": 85, "stabilite_stockage": 80, "impact_environnemental": 80,
    },
    "evolved_mag_mix": {
        "purete_minerale": 85, "biodisponibilite": 82, "duree_terrain": 82,
        "attractivite": 80, "securite_toxicologique": 88, "homogeneite": 85,
        "conditionnement": 80, "tracabilite": 82, "rendement_surface": 78,
        "rapport_cout_efficacite": 85, "stabilite_stockage": 82, "impact_environnemental": 82,
    },
    "purina_antlermax_zn": {
        "purete_minerale": 92, "biodisponibilite": 95, "duree_terrain": 85,
        "attractivite": 88, "securite_toxicologique": 95, "homogeneite": 92,
        "conditionnement": 90, "tracabilite": 92, "rendement_surface": 82,
        "rapport_cout_efficacite": 80, "stabilite_stockage": 90, "impact_environnemental": 88,
    },
    "ridley_se_vit": {
        "purete_minerale": 88, "biodisponibilite": 85, "duree_terrain": 88,
        "attractivite": 75, "securite_toxicologique": 90, "homogeneite": 85,
        "conditionnement": 82, "tracabilite": 88, "rendement_surface": 80,
        "rapport_cout_efficacite": 75, "stabilite_stockage": 88, "impact_environnemental": 85,
    },
    "sportsmans_fe_block": {
        "purete_minerale": 72, "biodisponibilite": 68, "duree_terrain": 85,
        "attractivite": 70, "securite_toxicologique": 80, "homogeneite": 75,
        "conditionnement": 70, "tracabilite": 68, "rendement_surface": 72,
        "rapport_cout_efficacite": 92, "stabilite_stockage": 82, "impact_environnemental": 78,
    },
    "bear_mineral_attract": {
        "purete_minerale": 78, "biodisponibilite": 75, "duree_terrain": 72,
        "attractivite": 95, "securite_toxicologique": 82, "homogeneite": 78,
        "conditionnement": 75, "tracabilite": 75, "rendement_surface": 70,
        "rapport_cout_efficacite": 80, "stabilite_stockage": 78, "impact_environnemental": 72,
    },
    "purina_antlermax_20": {
        "purete_minerale": 90, "biodisponibilite": 88, "duree_terrain": 80,
        "attractivite": 85, "securite_toxicologique": 92, "homogeneite": 90,
        "conditionnement": 88, "tracabilite": 90, "rendement_surface": 78,
        "rapport_cout_efficacite": 78, "stabilite_stockage": 85, "impact_environnemental": 82,
    },
}

# Ponderation des 12 criteres
WEIGHTS = {
    "purete_minerale": 0.12,
    "biodisponibilite": 0.15,
    "duree_terrain": 0.08,
    "attractivite": 0.10,
    "securite_toxicologique": 0.12,
    "homogeneite": 0.05,
    "conditionnement": 0.04,
    "tracabilite": 0.06,
    "rendement_surface": 0.06,
    "rapport_cout_efficacite": 0.10,
    "stabilite_stockage": 0.05,
    "impact_environnemental": 0.07,
}

CRITERIA_LABELS = {
    "purete_minerale": "Purete minerale",
    "biodisponibilite": "Biodisponibilite",
    "duree_terrain": "Duree terrain",
    "attractivite": "Attractivite",
    "securite_toxicologique": "Securite toxicologique",
    "homogeneite": "Homogeneite",
    "conditionnement": "Conditionnement",
    "tracabilite": "Tracabilite",
    "rendement_surface": "Rendement surface",
    "rapport_cout_efficacite": "Rapport cout/efficacite",
    "stabilite_stockage": "Stabilite stockage",
    "impact_environnemental": "Impact environnemental",
}


def analyze_product_quality(product_id: str) -> dict:
    """Analyse qualite complete d'un produit (12 criteres)."""
    data = QUALITY_DATA.get(product_id)
    if not data:
        return {"error": f"Produit inconnu: {product_id}", "product_id": product_id}

    criteria = []
    weighted_sum = 0.0
    for key, weight in WEIGHTS.items():
        val = data.get(key, 50)
        weighted_sum += val * weight
        zone = "vert" if val >= 80 else "jaune" if val >= 60 else "rouge"
        criteria.append({
            "key": key,
            "label": CRITERIA_LABELS.get(key, key),
            "score": val,
            "weight": weight,
            "zone": zone,
        })

    score_global = int(weighted_sum)
    grade = "EXCELLENT" if score_global >= 85 else "BON" if score_global >= 70 else "MODERE" if score_global >= 55 else "INSUFFISANT"

    # Ratio cout/efficacite
    from engines.nutrition_intelligence.x6000_product_score import PRODUCT_CATALOG
    product = PRODUCT_CATALOG.get(product_id, {})
    price = product.get("price_cad", 1)
    duration = product.get("duration_weeks", 1)
    cost_per_week = round(price / max(duration, 1), 2)
    efficiency_ratio = round(score_global / max(cost_per_week, 0.01), 1)

    return {
        "product_id": product_id,
        "score_qualite": score_global,
        "grade": grade,
        "criteria": criteria,
        "cost_per_week_cad": cost_per_week,
        "efficiency_ratio": efficiency_ratio,
        "top_strengths": sorted(criteria, key=lambda c: c["score"], reverse=True)[:3],
        "weaknesses": [c for c in criteria if c["zone"] == "rouge"],
    }


def analyze_all_quality() -> dict:
    """Analyse qualite de tous les produits du catalogue."""
    results = []
    for pid in QUALITY_DATA:
        r = analyze_product_quality(pid)
        if "error" not in r:
            results.append(r)
    results.sort(key=lambda x: x["score_qualite"], reverse=True)
    return {
        "products": results,
        "total": len(results),
        "average_quality": int(sum(r["score_qualite"] for r in results) / max(len(results), 1)),
    }
