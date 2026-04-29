"""
x6011 — MARKET_AVAILABILITY_ENGINE
Disponibilite des produits au Canada et aux USA.
Restrictions provinciales (QC, ON, BC, AB...) et reglementaires (FDA/USDA).
BCE-4X / STEEVE-MAX V6

Sources reglementaires reelles:
- MAPAQ (Ministere de l'Agriculture, des Pecheries et de l'Alimentation du Quebec)
- ACIA (Agence canadienne d'inspection des aliments)
- Provincial Wildlife Acts (Loi sur la conservation et la mise en valeur de la faune)
- FDA Title 21 CFR (Food and Drug Administration)
"""

# Disponibilite par produit et par region
AVAILABILITY_DATA = {
    "trophy_rock_four65": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "disponible", "restrictions": [], "distributeurs": ["La Tuque Chasse", "Pronature"]},
                "ON": {"status": "disponible", "restrictions": [], "distributeurs": ["Bass Pro Ontario"]},
                "NB": {"status": "disponible", "restrictions": [], "distributeurs": ["Canadian Tire NB"]},
                "AB": {"status": "disponible", "restrictions": [], "distributeurs": ["Cabela's Alberta"]},
                "BC": {"status": "restreint", "restrictions": ["Zone faune protegee interdit"], "distributeurs": []},
                "SK": {"status": "disponible", "restrictions": [], "distributeurs": ["Wholesale Sports"]},
                "MB": {"status": "disponible", "restrictions": [], "distributeurs": ["Bass Pro Winnipeg"]},
            },
        },
        "usa": {
            "available": True,
            "states_restricted": ["NY", "VT", "MI"],
            "restriction_reason": "CWD (Chronic Wasting Disease) prevention zones",
            "distributor_usa": "Bass Pro Shops, Cabela's",
        },
    },
    "pro_cal_lick": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "disponible", "restrictions": [], "distributeurs": ["Boutique Plein Air"]},
                "ON": {"status": "disponible", "restrictions": [], "distributeurs": ["Bass Pro Ontario"]},
                "NB": {"status": "disponible", "restrictions": [], "distributeurs": ["Chasse NB"]},
                "AB": {"status": "disponible", "restrictions": [], "distributeurs": ["Cabela's Alberta"]},
                "BC": {"status": "disponible", "restrictions": [], "distributeurs": ["Island Outfitters"]},
                "SK": {"status": "disponible", "restrictions": [], "distributeurs": ["Wholesale Sports"]},
                "MB": {"status": "disponible", "restrictions": [], "distributeurs": ["Bass Pro Winnipeg"]},
            },
        },
        "usa": {
            "available": True,
            "states_restricted": ["NY"],
            "restriction_reason": "Restrictions blocs mineraux terres publiques",
            "distributor_usa": "Tractor Supply, Amazon USA",
        },
    },
    "biomineral_p_plus": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "disponible", "restrictions": [], "distributeurs": ["Pronature", "La Tuque"]},
                "ON": {"status": "disponible", "restrictions": [], "distributeurs": ["Canadian Tire"]},
                "NB": {"status": "disponible", "restrictions": [], "distributeurs": []},
                "AB": {"status": "import_requis", "restrictions": ["Delai 2-3 semaines"], "distributeurs": []},
                "BC": {"status": "restreint", "restrictions": ["Non distribue localement"], "distributeurs": []},
            },
        },
        "usa": {
            "available": False,
            "states_restricted": [],
            "restriction_reason": "Non distribue aux USA",
            "distributor_usa": "",
        },
    },
    "whitetail_k_source": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "import_requis", "restrictions": ["Commande speciale via distributeur"], "distributeurs": ["Whitetail Canada"]},
                "ON": {"status": "disponible", "restrictions": [], "distributeurs": ["Bass Pro Ontario"]},
                "NB": {"status": "disponible", "restrictions": [], "distributeurs": []},
                "AB": {"status": "disponible", "restrictions": [], "distributeurs": ["Cabela's"]},
            },
        },
        "usa": {
            "available": True,
            "states_restricted": [],
            "restriction_reason": "",
            "distributor_usa": "Whitetail Institute Direct, Amazon",
        },
    },
    "evolved_mag_mix": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "disponible", "restrictions": [], "distributeurs": ["Pronature"]},
                "ON": {"status": "disponible", "restrictions": [], "distributeurs": ["Bass Pro"]},
                "NB": {"status": "disponible", "restrictions": [], "distributeurs": []},
                "AB": {"status": "disponible", "restrictions": [], "distributeurs": ["Cabela's"]},
                "BC": {"status": "disponible", "restrictions": [], "distributeurs": []},
            },
        },
        "usa": {
            "available": True,
            "states_restricted": ["MI", "WI"],
            "restriction_reason": "CWD zones — attractifs interdits",
            "distributor_usa": "Evolved Habitats Direct",
        },
    },
    "purina_antlermax_zn": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina Canada", "Pronature", "Agri-Marche"]},
                "ON": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina Canada", "Co-op"]},
                "NB": {"status": "disponible", "restrictions": [], "distributeurs": ["Co-op Atlantique"]},
                "AB": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina Canada West"]},
                "BC": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina Canada West"]},
                "SK": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina SK"]},
                "MB": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina MB"]},
            },
        },
        "usa": {
            "available": True,
            "states_restricted": [],
            "restriction_reason": "",
            "distributor_usa": "Purina Mills, Tractor Supply, Bass Pro Shops",
        },
    },
    "ridley_se_vit": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "disponible", "restrictions": [], "distributeurs": ["Ridley Canada", "Agri-Marche"]},
                "ON": {"status": "disponible", "restrictions": [], "distributeurs": ["Ridley Canada"]},
                "AB": {"status": "disponible", "restrictions": [], "distributeurs": ["Ridley Canada West"]},
            },
        },
        "usa": {
            "available": True,
            "states_restricted": [],
            "restriction_reason": "",
            "distributor_usa": "Ridley Block, Tractor Supply",
        },
    },
    "sportsmans_fe_block": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "disponible", "restrictions": [], "distributeurs": ["Canadian Tire", "Walmart"]},
                "ON": {"status": "disponible", "restrictions": [], "distributeurs": ["Canadian Tire"]},
                "NB": {"status": "disponible", "restrictions": [], "distributeurs": ["Canadian Tire"]},
                "AB": {"status": "disponible", "restrictions": [], "distributeurs": ["Canadian Tire"]},
            },
        },
        "usa": {
            "available": True,
            "states_restricted": [],
            "restriction_reason": "",
            "distributor_usa": "Walmart, Amazon",
        },
    },
    "bear_mineral_attract": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "restreint", "restrictions": ["Appats ours interdits zone 10"], "distributeurs": ["Pronature"]},
                "ON": {"status": "restreint", "restrictions": ["Appats ours reglementees (WMU specific)"], "distributeurs": ["Bass Pro"]},
                "NB": {"status": "disponible", "restrictions": [], "distributeurs": []},
                "AB": {"status": "disponible", "restrictions": [], "distributeurs": ["Cabela's"]},
                "BC": {"status": "restreint", "restrictions": ["Attractifs ours interdits zones protegees"], "distributeurs": []},
            },
        },
        "usa": {
            "available": True,
            "states_restricted": ["WA", "OR", "CA"],
            "restriction_reason": "Bear baiting interdit dans ces etats",
            "distributor_usa": "Bass Pro Shops",
        },
    },
    "purina_antlermax_20": {
        "canada": {
            "available": True,
            "provinces": {
                "QC": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina Canada", "Agri-Marche"]},
                "ON": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina Canada", "Co-op"]},
                "NB": {"status": "disponible", "restrictions": [], "distributeurs": ["Co-op Atlantique"]},
                "AB": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina Canada"]},
                "BC": {"status": "disponible", "restrictions": [], "distributeurs": ["Purina Canada"]},
            },
        },
        "usa": {
            "available": True,
            "states_restricted": [],
            "restriction_reason": "",
            "distributor_usa": "Purina Mills, Tractor Supply, Bass Pro Shops",
        },
    },
}


def get_product_availability(product_id: str, province: str = None) -> dict:
    """Disponibilite d'un produit avec details par province/etat."""
    data = AVAILABILITY_DATA.get(product_id)
    if not data:
        return {"error": f"Produit inconnu: {product_id}", "product_id": product_id}

    result = {
        "product_id": product_id,
        "canada": data["canada"],
        "usa": data["usa"],
    }

    # Filtrage par province
    if province and province in data["canada"].get("provinces", {}):
        prov_data = data["canada"]["provinces"][province]
        result["province_detail"] = {
            "province": province,
            **prov_data,
            "available_now": prov_data["status"] == "disponible",
        }
    elif province:
        result["province_detail"] = {
            "province": province,
            "status": "non_couvert",
            "restrictions": ["Province non repertoriee"],
            "distributeurs": [],
            "available_now": False,
        }

    # Score de disponibilite
    provinces = data["canada"].get("provinces", {})
    total = len(provinces)
    available_count = sum(1 for p in provinces.values() if p["status"] == "disponible")
    restricted_count = sum(1 for p in provinces.values() if p["status"] == "restreint")
    score_dispo = int((available_count / max(total, 1)) * 100) if total > 0 else 0

    result["availability_score"] = {
        "canada_score": score_dispo,
        "usa_available": data["usa"]["available"],
        "provinces_available": available_count,
        "provinces_restricted": restricted_count,
        "provinces_total": total,
    }

    return result


def get_all_availability(province: str = None) -> dict:
    """Disponibilite de tous les produits."""
    results = []
    for pid in AVAILABILITY_DATA:
        r = get_product_availability(pid, province)
        if "error" not in r:
            results.append(r)
    results.sort(key=lambda x: x["availability_score"]["canada_score"], reverse=True)
    return {
        "products": results,
        "total": len(results),
        "province_filter": province,
    }


def get_provincial_restrictions(province: str) -> dict:
    """Toutes les restrictions pour une province donnee."""
    restrictions = []
    for pid, data in AVAILABILITY_DATA.items():
        provinces = data["canada"].get("provinces", {})
        if province in provinces:
            prov = provinces[province]
            if prov["restrictions"]:
                restrictions.append({
                    "product_id": pid,
                    "status": prov["status"],
                    "restrictions": prov["restrictions"],
                })
    return {
        "province": province,
        "restrictions": restrictions,
        "total_restricted": len(restrictions),
    }
