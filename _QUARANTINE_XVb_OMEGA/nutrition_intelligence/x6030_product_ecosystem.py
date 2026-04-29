"""
x6030 — PRODUCT_ECOSYSTEM_CONNECTOR
Interconnexion totale des produits avec l'ecosysteme BIONIC.
Chaque produit est lie a: Magasin, Fournisseur, Certifications,
Recettes, Couts, Intelligence, Comparez, Commander.
BCE-4X / STEEVE-MAX V6
"""

# Ecosysteme complet par produit
PRODUCT_ECOSYSTEM = {
    "trophy_rock_four65": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/trophy-rock-four65",
            "distributeurs": ["Pronature QC", "La Tuque Chasse", "Bass Pro Shops", "Cabela's"],
            "prix_magasin_cad": 27.99,
        },
        "fournisseur": {
            "nom": "Trophy Rock Products LLC",
            "pays": "USA",
            "importateur_canada": "Pronature Distribution",
            "contact": "info@trophyrock.com",
            "delai_livraison_jours": 5,
        },
        "certifications": ["ACIA enregistre", "Produit naturel", "Sans additif chimique"],
        "recettes_associees": ["Recette Printemps Chevreuil", "Recette Ete Orignal"],
        "modules_lies": ["x5100", "x5200", "x5700", "x5800", "x6000", "x6010", "x6012"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=trophy_rock_four65",
            "comparez": "/nutrition-supra?compare=trophy_rock_four65",
            "commander": "/nutrition-supra?order=trophy_rock_four65",
            "fiche_produit": "/magasin/produit/trophy-rock-four65",
        },
    },
    "pro_cal_lick": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/pro-cal-lick",
            "distributeurs": ["Boutique Plein Air", "Bass Pro Ontario"],
            "prix_magasin_cad": 21.49,
        },
        "fournisseur": {
            "nom": "Ridley Inc.",
            "pays": "Canada",
            "importateur_canada": "Direct",
            "contact": "info@ridleyinc.com",
            "delai_livraison_jours": 3,
        },
        "certifications": ["ACIA enregistre"],
        "recettes_associees": ["Recette Printemps Chevreuil", "Recette Pre-Rut Orignal"],
        "modules_lies": ["x5100", "x5200", "x5700", "x6000"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=pro_cal_lick",
            "comparez": "/nutrition-supra?compare=pro_cal_lick",
            "commander": "/nutrition-supra?order=pro_cal_lick",
            "fiche_produit": "/magasin/produit/pro-cal-lick",
        },
    },
    "purina_antlermax_zn": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/purina-antlermax-zn",
            "distributeurs": ["Purina Canada", "Pronature", "Agri-Marche", "Co-op"],
            "prix_magasin_cad": 28.99,
        },
        "fournisseur": {
            "nom": "Purina Mills LLC (Nestle Purina)",
            "pays": "USA",
            "importateur_canada": "Purina Canada",
            "contact": "purina.ca",
            "delai_livraison_jours": 4,
        },
        "certifications": ["ACIA enregistre", "FDA enregistre", "USDA conforme", "Purina Certified"],
        "recettes_associees": ["Recette Printemps Chevreuil", "Recette Ete Chevreuil", "Recette Printemps Orignal"],
        "modules_lies": ["x5100", "x5200", "x5500", "x5700", "x5800", "x6000", "x6010", "x6012"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=purina_antlermax_zn",
            "comparez": "/nutrition-supra?compare=purina_antlermax_zn",
            "commander": "/nutrition-supra?order=purina_antlermax_zn",
            "fiche_produit": "/magasin/produit/purina-antlermax-zn",
        },
    },
    "purina_antlermax_20": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/purina-antlermax-20",
            "distributeurs": ["Purina Canada", "Agri-Marche", "Co-op Atlantique"],
            "prix_magasin_cad": 34.99,
        },
        "fournisseur": {
            "nom": "Purina Mills LLC (Nestle Purina)",
            "pays": "USA",
            "importateur_canada": "Purina Canada",
            "contact": "purina.ca",
            "delai_livraison_jours": 4,
        },
        "certifications": ["ACIA enregistre", "FDA enregistre", "USDA soja conforme", "Purina Certified"],
        "recettes_associees": ["Recette Printemps Chevreuil Post-Rut", "Recette Ete Orignal"],
        "modules_lies": ["x5100", "x5500", "x5700", "x5800", "x6000", "x6010"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=purina_antlermax_20",
            "comparez": "/nutrition-supra?compare=purina_antlermax_20",
            "commander": "/nutrition-supra?order=purina_antlermax_20",
            "fiche_produit": "/magasin/produit/purina-antlermax-20",
        },
    },
    "evolved_mag_mix": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/evolved-mag-mix",
            "distributeurs": ["Pronature", "Evolved Habitats Direct"],
            "prix_magasin_cad": 18.49,
        },
        "fournisseur": {
            "nom": "Evolved Habitats LLC",
            "pays": "USA",
            "importateur_canada": "Pronature Distribution",
            "contact": "evolvedhabitats.com",
            "delai_livraison_jours": 7,
        },
        "certifications": ["ACIA conforme", "FDA GRAS"],
        "recettes_associees": ["Recette Printemps Chevreuil", "Recette Pre-Rut Chevreuil"],
        "modules_lies": ["x5100", "x5200", "x5700", "x6000"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=evolved_mag_mix",
            "comparez": "/nutrition-supra?compare=evolved_mag_mix",
            "commander": "/nutrition-supra?order=evolved_mag_mix",
            "fiche_produit": "/magasin/produit/evolved-mag-mix",
        },
    },
    "ridley_se_vit": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/ridley-se-vit",
            "distributeurs": ["Ridley Canada", "Agri-Marche"],
            "prix_magasin_cad": 24.99,
        },
        "fournisseur": {
            "nom": "Ridley Inc.",
            "pays": "Canada",
            "importateur_canada": "Direct",
            "contact": "ridleyinc.com",
            "delai_livraison_jours": 3,
        },
        "certifications": ["ACIA conforme", "FDA selenium conforme"],
        "recettes_associees": ["Recette Printemps Chevreuil"],
        "modules_lies": ["x5100", "x5200", "x5700", "x6000", "x6012"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=ridley_se_vit",
            "comparez": "/nutrition-supra?compare=ridley_se_vit",
            "commander": "/nutrition-supra?order=ridley_se_vit",
            "fiche_produit": "/magasin/produit/ridley-se-vit",
        },
    },
    "sportsmans_fe_block": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/sportsmans-fe-block",
            "distributeurs": ["Canadian Tire", "Walmart"],
            "prix_magasin_cad": 12.99,
        },
        "fournisseur": {
            "nom": "Sportsman's Choice",
            "pays": "Canada",
            "importateur_canada": "Direct",
            "contact": "",
            "delai_livraison_jours": 2,
        },
        "certifications": ["Basique conforme"],
        "recettes_associees": [],
        "modules_lies": ["x5100", "x6000"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=sportsmans_fe_block",
            "comparez": "/nutrition-supra?compare=sportsmans_fe_block",
            "commander": "/nutrition-supra?order=sportsmans_fe_block",
            "fiche_produit": "/magasin/produit/sportsmans-fe-block",
        },
    },
    "bear_mineral_attract": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/bear-mineral-attract",
            "distributeurs": ["Pronature", "Bass Pro Shops"],
            "prix_magasin_cad": 19.99,
        },
        "fournisseur": {
            "nom": "Bear Mineral Products",
            "pays": "USA",
            "importateur_canada": "Pronature",
            "contact": "",
            "delai_livraison_jours": 7,
        },
        "certifications": ["ACIA conforme", "Attention: reglemente comme appat QC/ON/BC"],
        "recettes_associees": ["Recette Printemps Ours Noir"],
        "modules_lies": ["x5100", "x6000"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=bear_mineral_attract",
            "comparez": "/nutrition-supra?compare=bear_mineral_attract",
            "commander": "/nutrition-supra?order=bear_mineral_attract",
            "fiche_produit": "/magasin/produit/bear-mineral-attract",
        },
    },
    "biomineral_p_plus": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/biomineral-p-plus",
            "distributeurs": ["Pronature", "La Tuque"],
            "prix_magasin_cad": 23.49,
        },
        "fournisseur": {
            "nom": "BioMineral Canada",
            "pays": "Canada",
            "importateur_canada": "Direct",
            "contact": "",
            "delai_livraison_jours": 3,
        },
        "certifications": ["ACIA enregistre", "MAPAQ conforme"],
        "recettes_associees": ["Recette Printemps Chevreuil"],
        "modules_lies": ["x5100", "x5200", "x6000"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=biomineral_p_plus",
            "comparez": "/nutrition-supra?compare=biomineral_p_plus",
            "commander": "/nutrition-supra?order=biomineral_p_plus",
            "fiche_produit": "/magasin/produit/biomineral-p-plus",
        },
    },
    "whitetail_k_source": {
        "magasin": {
            "disponible_en_ligne": True,
            "url_magasin": "/magasin/produit/whitetail-k-source",
            "distributeurs": ["Whitetail Canada", "Bass Pro Ontario"],
            "prix_magasin_cad": 26.49,
        },
        "fournisseur": {
            "nom": "Whitetail Institute of North America",
            "pays": "USA",
            "importateur_canada": "Whitetail Canada",
            "contact": "whitetailinstitute.com",
            "delai_livraison_jours": 10,
        },
        "certifications": ["FDA enregistre"],
        "recettes_associees": ["Recette Printemps Chevreuil"],
        "modules_lies": ["x5100", "x5200", "x6000"],
        "liens_ecosysteme": {
            "intelligence": "/nutrition-supra?product=whitetail_k_source",
            "comparez": "/nutrition-supra?compare=whitetail_k_source",
            "commander": "/nutrition-supra?order=whitetail_k_source",
            "fiche_produit": "/magasin/produit/whitetail-k-source",
        },
    },
}


def get_product_ecosystem(product_id: str) -> dict:
    """Interconnexion complete d'un produit avec l'ecosysteme BIONIC."""
    data = PRODUCT_ECOSYSTEM.get(product_id)
    if not data:
        return {"error": f"Produit inconnu: {product_id}", "product_id": product_id}
    return {
        "product_id": product_id,
        **data,
        "connections_count": len(data.get("modules_lies", [])),
    }


def get_all_ecosystems() -> dict:
    """Interconnexion de tous les produits."""
    results = []
    for pid in PRODUCT_ECOSYSTEM:
        eco = get_product_ecosystem(pid)
        if "error" not in eco:
            results.append(eco)
    return {
        "products": results,
        "total": len(results),
    }


def get_product_tracability(product_id: str) -> dict:
    """Tracabilite complete d'un produit dans l'ecosysteme."""
    data = PRODUCT_ECOSYSTEM.get(product_id)
    if not data:
        return {"error": f"Produit inconnu: {product_id}", "product_id": product_id}
    return {
        "product_id": product_id,
        "fournisseur": data["fournisseur"],
        "certifications": data["certifications"],
        "modules_lies": data["modules_lies"],
        "recettes_associees": data["recettes_associees"],
        "magasin": data["magasin"],
        "tracabilite_complete": True,
    }
