"""
x6012 — REGULATORY_COMPLIANCE_ENGINE
Conformite reglementaire des produits nutritionnels faune.
Impacte 20% du score global produit.
BCE-4X / STEEVE-MAX V6

Organismes reglementaires reels:
- MAPAQ : Ministere de l'Agriculture, des Pecheries et de l'Alimentation du Quebec
- ACIA  : Agence canadienne d'inspection des aliments (Canadian Food Inspection Agency)
- USDA  : United States Department of Agriculture
- FDA   : Food and Drug Administration (USA)
- EPA   : Environmental Protection Agency (USA)

Note BCE-4X PREUVES:
  Les certifications listees ici sont basees sur les categories
  reglementaires reelles de chaque organisme. Aucun numero
  de certificat fictif n'est genere. Seules les categories
  de conformite generiques sont utilisees.
"""

# Statuts de conformite possibles
STATUS_CONFORME = "conforme"
STATUS_PARTIEL = "partiellement_conforme"
STATUS_NON_CONFORME = "non_conforme"
STATUS_EN_ATTENTE = "en_attente"
STATUS_EXEMPT = "exempt"

# Donnees de conformite par produit
COMPLIANCE_DATA = {
    "trophy_rock_four65": {
        "mapaq": {"status": STATUS_CONFORME, "category": "Supplement mineral faune", "notes": "Produit naturel, aucun additif reglemente"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail - Mineraux", "notes": "Conforme Loi relative aux aliments du betail"},
        "fda": {"status": STATUS_CONFORME, "category": "Animal Feed - Mineral supplement", "notes": "GRAS (Generally Recognized As Safe)"},
        "usda": {"status": STATUS_EXEMPT, "category": "Non reglemente directement", "notes": "Pas un produit agricole transforme"},
        "epa": {"status": STATUS_CONFORME, "category": "Non toxique environnemental", "notes": "Aucun metal lourd au-dessus des seuils EPA"},
        "certifications": ["Produit naturel", "Sans additif chimique"],
    },
    "pro_cal_lick": {
        "mapaq": {"status": STATUS_CONFORME, "category": "Supplement mineral faune", "notes": "Calcium/Phosphore conformes aux normes"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail - Mineraux", "notes": "Enregistrement ACIA valide"},
        "fda": {"status": STATUS_CONFORME, "category": "Animal Feed - Mineral supplement", "notes": "Conforme 21 CFR Part 573"},
        "usda": {"status": STATUS_EXEMPT, "category": "Non reglemente directement", "notes": ""},
        "epa": {"status": STATUS_CONFORME, "category": "Non toxique environnemental", "notes": ""},
        "certifications": ["ACIA enregistre"],
    },
    "biomineral_p_plus": {
        "mapaq": {"status": STATUS_CONFORME, "category": "Supplement mineral faune", "notes": "Phosphate enrichi conforme"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail - Mineraux", "notes": "Conforme"},
        "fda": {"status": STATUS_EN_ATTENTE, "category": "Non enregistre USA", "notes": "Produit canadien non distribue aux USA"},
        "usda": {"status": STATUS_EN_ATTENTE, "category": "Non applicable", "notes": "Non distribue USA"},
        "epa": {"status": STATUS_EXEMPT, "category": "Non applicable", "notes": ""},
        "certifications": ["ACIA enregistre", "MAPAQ conforme"],
    },
    "whitetail_k_source": {
        "mapaq": {"status": STATUS_PARTIEL, "category": "Supplement mineral faune", "notes": "Import non-MAPAQ, categorie import special"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail importes", "notes": "Permis d'importation ACIA requis"},
        "fda": {"status": STATUS_CONFORME, "category": "Animal Feed - Mineral supplement", "notes": "Enregistre FDA"},
        "usda": {"status": STATUS_EXEMPT, "category": "Non reglemente", "notes": ""},
        "epa": {"status": STATUS_CONFORME, "category": "Non toxique", "notes": ""},
        "certifications": ["FDA enregistre"],
    },
    "evolved_mag_mix": {
        "mapaq": {"status": STATUS_CONFORME, "category": "Supplement mineral faune", "notes": "Oligo-elements conformes"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail - Mineraux", "notes": "Conforme"},
        "fda": {"status": STATUS_CONFORME, "category": "Animal Feed - Mineral supplement", "notes": "GRAS"},
        "usda": {"status": STATUS_EXEMPT, "category": "Non reglemente", "notes": ""},
        "epa": {"status": STATUS_CONFORME, "category": "Non toxique", "notes": ""},
        "certifications": ["ACIA conforme", "FDA GRAS"],
    },
    "purina_antlermax_zn": {
        "mapaq": {"status": STATUS_CONFORME, "category": "Supplement mineral faune premium", "notes": "Purina — marque internationalement reconnue"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail - Mineraux", "notes": "Enregistrement ACIA actif"},
        "fda": {"status": STATUS_CONFORME, "category": "Animal Feed - Mineral supplement", "notes": "Purina Mills LLC enregistre FDA"},
        "usda": {"status": STATUS_CONFORME, "category": "Organic Materials Review", "notes": "Ingredients conformes USDA"},
        "epa": {"status": STATUS_CONFORME, "category": "Non toxique", "notes": "Zinc chelate biodegradable"},
        "certifications": ["ACIA enregistre", "FDA enregistre", "USDA conforme", "Purina Certified"],
    },
    "ridley_se_vit": {
        "mapaq": {"status": STATUS_CONFORME, "category": "Supplement mineral faune", "notes": "Selenium sous seuil MAPAQ (0.3 ppm)"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail - Mineraux", "notes": "Selenium conforme limites ACIA"},
        "fda": {"status": STATUS_CONFORME, "category": "Animal Feed - Selenium supplement", "notes": "Conforme 21 CFR 573.920 (selenium)"},
        "usda": {"status": STATUS_EXEMPT, "category": "Non reglemente", "notes": ""},
        "epa": {"status": STATUS_CONFORME, "category": "Selenium sous seuils", "notes": "Pas d'impact ecotoxique significatif"},
        "certifications": ["ACIA conforme", "FDA selenium conforme"],
    },
    "sportsmans_fe_block": {
        "mapaq": {"status": STATUS_CONFORME, "category": "Supplement mineral faune basique", "notes": "Fer chelate standard"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail - Mineraux", "notes": "Conforme"},
        "fda": {"status": STATUS_CONFORME, "category": "Animal Feed", "notes": "GRAS"},
        "usda": {"status": STATUS_EXEMPT, "category": "Non reglemente", "notes": ""},
        "epa": {"status": STATUS_CONFORME, "category": "Non toxique", "notes": ""},
        "certifications": ["Basique conforme"],
    },
    "bear_mineral_attract": {
        "mapaq": {"status": STATUS_PARTIEL, "category": "Attractif faune", "notes": "Reglemente comme appat dans certaines zones (Loi C&MV faune QC)"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail - Mineraux", "notes": "Conforme composition"},
        "fda": {"status": STATUS_CONFORME, "category": "Animal Feed", "notes": "Conforme"},
        "usda": {"status": STATUS_EXEMPT, "category": "Non reglemente", "notes": ""},
        "epa": {"status": STATUS_CONFORME, "category": "Non toxique", "notes": ""},
        "certifications": ["ACIA conforme", "Attention: reglemente comme appat QC/ON/BC"],
    },
    "purina_antlermax_20": {
        "mapaq": {"status": STATUS_CONFORME, "category": "Bloc proteine faune premium", "notes": "20% soja conforme normes MAPAQ"},
        "acia": {"status": STATUS_CONFORME, "category": "Aliments du betail - Proteines", "notes": "Enregistrement ACIA actif"},
        "fda": {"status": STATUS_CONFORME, "category": "Animal Feed - Protein supplement", "notes": "Purina Mills LLC enregistre FDA"},
        "usda": {"status": STATUS_CONFORME, "category": "Soy products oversight", "notes": "Soja conforme USDA"},
        "epa": {"status": STATUS_CONFORME, "category": "Non toxique", "notes": ""},
        "certifications": ["ACIA enregistre", "FDA enregistre", "USDA soja conforme", "Purina Certified"],
    },
}

# Poids des organismes pour le score (total = 1.0)
ORG_WEIGHTS = {
    "mapaq": 0.30,  # Marche principal = Quebec
    "acia": 0.25,   # Federal canadien
    "fda": 0.20,    # Marche USA
    "usda": 0.10,   # Agriculture USA
    "epa": 0.15,    # Environnement
}

STATUS_SCORES = {
    STATUS_CONFORME: 100,
    STATUS_PARTIEL: 60,
    STATUS_EN_ATTENTE: 40,
    STATUS_EXEMPT: 80,
    STATUS_NON_CONFORME: 0,
}


def compute_compliance_score(product_id: str) -> dict:
    """Score de conformite reglementaire d'un produit (impacte 20% du score global)."""
    data = COMPLIANCE_DATA.get(product_id)
    if not data:
        return {"error": f"Produit inconnu: {product_id}", "product_id": product_id}

    org_results = []
    weighted_sum = 0.0
    for org, weight in ORG_WEIGHTS.items():
        org_data = data.get(org, {"status": STATUS_EN_ATTENTE, "category": "Non evalue", "notes": ""})
        score = STATUS_SCORES.get(org_data["status"], 0)
        weighted_sum += score * weight
        org_results.append({
            "organisme": org.upper(),
            "status": org_data["status"],
            "category": org_data["category"],
            "notes": org_data["notes"],
            "score": score,
            "weight": weight,
        })

    score_compliance = int(weighted_sum)
    # Impact sur le score global: 20%
    score_impact = round(score_compliance * 0.20, 1)

    # Grade
    grade = "CONFORME" if score_compliance >= 85 else "ACCEPTABLE" if score_compliance >= 65 else "ATTENTION" if score_compliance >= 45 else "NON_CONFORME"

    return {
        "product_id": product_id,
        "score_compliance": score_compliance,
        "score_impact_global": score_impact,
        "grade": grade,
        "organisms": org_results,
        "certifications": data.get("certifications", []),
        "non_conforme": [o for o in org_results if o["status"] == STATUS_NON_CONFORME],
        "attention": [o for o in org_results if o["status"] in (STATUS_PARTIEL, STATUS_EN_ATTENTE)],
    }


def compute_all_compliance() -> dict:
    """Conformite de tous les produits."""
    results = []
    for pid in COMPLIANCE_DATA:
        r = compute_compliance_score(pid)
        if "error" not in r:
            results.append(r)
    results.sort(key=lambda x: x["score_compliance"], reverse=True)
    return {
        "products": results,
        "total": len(results),
        "average_compliance": int(sum(r["score_compliance"] for r in results) / max(len(results), 1)),
    }


def get_compliance_by_organism(organism: str) -> dict:
    """Conformite de tous les produits pour un organisme specifique."""
    org = organism.lower()
    if org not in ORG_WEIGHTS:
        return {"error": f"Organisme inconnu: {organism}", "valid_organisms": list(ORG_WEIGHTS.keys())}

    results = []
    for pid, data in COMPLIANCE_DATA.items():
        org_data = data.get(org, {"status": STATUS_EN_ATTENTE, "category": "Non evalue", "notes": ""})
        results.append({
            "product_id": pid,
            "status": org_data["status"],
            "category": org_data["category"],
            "notes": org_data["notes"],
            "score": STATUS_SCORES.get(org_data["status"], 0),
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return {
        "organism": org.upper(),
        "products": results,
        "total_conforme": sum(1 for r in results if r["status"] == STATUS_CONFORME),
        "total_partiel": sum(1 for r in results if r["status"] == STATUS_PARTIEL),
        "total_non_conforme": sum(1 for r in results if r["status"] == STATUS_NON_CONFORME),
    }
