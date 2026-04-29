"""
x6000 — PRODUCT_SCORE_ENGINE
Score d'adequation produit % : espece, saison, sol, type de site.
Classement intelligent des produits mineraux et supplements.
BCE-4X / STEEVE-MAX V6
"""

PRODUCT_CATALOG = {
    "trophy_rock_four65": {
        "name": "Trophy Rock Four65",
        "type": "bloc_mineral",
        "minerals": ["Na", "Ca", "P", "Mg", "Zn", "Fe"],
        "price_cad": 24.99,
        "weight_kg": 9,
        "duration_weeks": 8,
        "species_affinity": {"chevreuil": 0.95, "orignal": 0.90, "wapiti": 0.92, "ours_noir": 0.70},
        "season_affinity": {"printemps": 0.95, "ete": 0.80, "pre_rut": 0.90, "rut": 0.85, "post_rut": 0.88, "hiver": 0.92},
        "soil_affinity": {"acide": 0.95, "loam": 0.85, "coniferes": 0.92, "mixte": 0.88, "sableux": 0.90},
        "description": "Bloc mineral naturel multi-elements. Attraction naturelle, liberation progressive.",
        "tags": ["best-seller", "multi-mineral", "naturel"],
    },
    "pro_cal_lick": {
        "name": "Mineral Lick Pro-Cal",
        "type": "supplement_mineral",
        "minerals": ["Ca", "P"],
        "price_cad": 18.99,
        "weight_kg": 10,
        "duration_weeks": 10,
        "species_affinity": {"chevreuil": 0.90, "orignal": 0.95, "wapiti": 0.93, "ours_noir": 0.60},
        "season_affinity": {"printemps": 0.98, "ete": 0.85, "pre_rut": 0.92, "rut": 0.80, "post_rut": 0.75, "hiver": 0.70},
        "soil_affinity": {"acide": 0.95, "loam": 0.75, "coniferes": 0.98, "mixte": 0.82, "sableux": 0.88},
        "description": "Supplement calcium-phosphore. Essentiel pour croissance des bois et squelette.",
        "tags": ["croissance-bois", "calcium", "phosphore"],
    },
    "biomineral_p_plus": {
        "name": "BioMineral P-Plus",
        "type": "supplement_mineral",
        "minerals": ["P", "Ca", "Mg"],
        "price_cad": 22.49,
        "weight_kg": 8,
        "duration_weeks": 8,
        "species_affinity": {"chevreuil": 0.88, "orignal": 0.92, "wapiti": 0.90, "ours_noir": 0.55},
        "season_affinity": {"printemps": 0.95, "ete": 0.80, "pre_rut": 0.88, "rut": 0.75, "post_rut": 0.82, "hiver": 0.78},
        "soil_affinity": {"acide": 0.98, "loam": 0.70, "coniferes": 0.95, "mixte": 0.80, "sableux": 0.92},
        "description": "Phosphate enrichi pour sols acides. Compense les deficits chroniques en P.",
        "tags": ["phosphore", "sol-acide", "enrichi"],
    },
    "whitetail_k_source": {
        "name": "Whitetail Institute K-Source",
        "type": "supplement_mineral",
        "minerals": ["K", "Na"],
        "price_cad": 15.99,
        "weight_kg": 5,
        "duration_weeks": 6,
        "species_affinity": {"chevreuil": 0.92, "orignal": 0.85, "wapiti": 0.88, "ours_noir": 0.65},
        "season_affinity": {"printemps": 0.80, "ete": 0.85, "pre_rut": 0.78, "rut": 0.75, "post_rut": 0.90, "hiver": 0.95},
        "soil_affinity": {"acide": 0.70, "loam": 0.90, "coniferes": 0.65, "mixte": 0.88, "sableux": 0.82},
        "description": "Source de potassium naturel. Equilibre electrolytique post-rut et hiver.",
        "tags": ["potassium", "hiver", "equilibre"],
    },
    "evolved_mag_mix": {
        "name": "Evolved Habitats Mag-Mix",
        "type": "supplement_mineral",
        "minerals": ["Mg", "Zn", "Se"],
        "price_cad": 19.99,
        "weight_kg": 7,
        "duration_weeks": 8,
        "species_affinity": {"chevreuil": 0.90, "orignal": 0.88, "wapiti": 0.85, "ours_noir": 0.72},
        "season_affinity": {"printemps": 0.92, "ete": 0.85, "pre_rut": 0.88, "rut": 0.80, "post_rut": 0.85, "hiver": 0.90},
        "soil_affinity": {"acide": 0.95, "loam": 0.80, "coniferes": 0.92, "mixte": 0.85, "sableux": 0.90},
        "description": "Melange magnesium + oligo-elements. Prevention tetanie, soutien immunitaire.",
        "tags": ["magnesium", "oligo-elements", "immunite"],
    },
    "purina_antlermax_zn": {
        "name": "Purina AntlerMax Zn",
        "type": "supplement_mineral",
        "minerals": ["Zn", "Ca", "P"],
        "price_cad": 28.99,
        "weight_kg": 10,
        "duration_weeks": 10,
        "species_affinity": {"chevreuil": 0.95, "orignal": 0.92, "wapiti": 0.94, "ours_noir": 0.50},
        "season_affinity": {"printemps": 0.98, "ete": 0.90, "pre_rut": 0.95, "rut": 0.85, "post_rut": 0.80, "hiver": 0.75},
        "soil_affinity": {"acide": 0.92, "loam": 0.85, "coniferes": 0.90, "mixte": 0.88, "sableux": 0.85},
        "description": "Zinc chelate premium. Mineralisation bois + systeme immunitaire.",
        "tags": ["zinc", "premium", "croissance-bois"],
    },
    "ridley_se_vit": {
        "name": "Ridley Se-Vit Block",
        "type": "bloc_mineral",
        "minerals": ["Se", "Fe"],
        "price_cad": 32.99,
        "weight_kg": 10,
        "duration_weeks": 8,
        "species_affinity": {"chevreuil": 0.88, "orignal": 0.90, "wapiti": 0.87, "ours_noir": 0.75},
        "season_affinity": {"printemps": 0.90, "ete": 0.82, "pre_rut": 0.85, "rut": 0.80, "post_rut": 0.88, "hiver": 0.95},
        "soil_affinity": {"acide": 0.98, "loam": 0.75, "coniferes": 0.95, "mixte": 0.80, "sableux": 0.92},
        "description": "Selenium + Vitamine E. Critique pour regions a sol acide/bouclier canadien.",
        "tags": ["selenium", "vitamine-e", "bouclier-canadien"],
    },
    "sportsmans_fe_block": {
        "name": "Sportsman's Choice Fe-Block",
        "type": "bloc_mineral",
        "minerals": ["Fe", "Mg"],
        "price_cad": 14.99,
        "weight_kg": 5,
        "duration_weeks": 10,
        "species_affinity": {"chevreuil": 0.82, "orignal": 0.85, "wapiti": 0.80, "ours_noir": 0.78},
        "season_affinity": {"printemps": 0.85, "ete": 0.80, "pre_rut": 0.82, "rut": 0.78, "post_rut": 0.85, "hiver": 0.88},
        "soil_affinity": {"acide": 0.70, "loam": 0.90, "coniferes": 0.72, "mixte": 0.85, "sableux": 0.80},
        "description": "Fer chelate + magnesium. Economique, convient a tous les sites.",
        "tags": ["fer", "economique", "universel"],
    },
    "bear_mineral_attract": {
        "name": "Bear Mineral Attract",
        "type": "bloc_mineral",
        "minerals": ["Na", "Ca", "K", "Mg"],
        "price_cad": 19.99,
        "weight_kg": 8,
        "duration_weeks": 6,
        "species_affinity": {"chevreuil": 0.60, "orignal": 0.65, "wapiti": 0.62, "ours_noir": 0.98},
        "season_affinity": {"printemps": 0.98, "ete": 0.90, "pre_rut": 0.75, "rut": 0.70, "post_rut": 0.85, "hiver": 0.30},
        "soil_affinity": {"acide": 0.85, "loam": 0.88, "coniferes": 0.82, "mixte": 0.90, "sableux": 0.85},
        "description": "Formule specifique ours. Haute teneur en mineraux attractifs post-hibernation.",
        "tags": ["ours-noir", "post-hibernation", "attractif"],
    },
    "purina_antlermax_20": {
        "name": "Purina AntlerMax 20",
        "type": "bloc_proteine",
        "minerals": [],
        "price_cad": 34.99,
        "weight_kg": 12,
        "duration_weeks": 8,
        "species_affinity": {"chevreuil": 0.95, "orignal": 0.90, "wapiti": 0.92, "ours_noir": 0.60},
        "season_affinity": {"printemps": 0.98, "ete": 0.88, "pre_rut": 0.90, "rut": 0.75, "post_rut": 0.82, "hiver": 0.80},
        "soil_affinity": {"acide": 0.85, "loam": 0.85, "coniferes": 0.85, "mixte": 0.85, "sableux": 0.85},
        "description": "Bloc proteine 20% soja. Performance croissance bois et lactation.",
        "tags": ["proteine", "croissance-bois", "lactation"],
    },
}


def compute_product_score(product_id: str, species: str, season: str, soil_type: str) -> dict:
    """Score d'adequation d'un produit pour un contexte donne."""
    product = PRODUCT_CATALOG.get(product_id)
    if not product:
        return {"error": f"Produit inconnu: {product_id}"}

    sp_score = product["species_affinity"].get(species, 0.5)
    se_score = product["season_affinity"].get(season, 0.5)
    so_score = product["soil_affinity"].get(soil_type, 0.5)

    global_score = int((sp_score * 0.4 + se_score * 0.35 + so_score * 0.25) * 100)

    optimal_for = []
    if sp_score >= 0.90:
        optimal_for.append(f"espece:{species}")
    if se_score >= 0.90:
        optimal_for.append(f"saison:{season}")
    if so_score >= 0.90:
        optimal_for.append(f"sol:{soil_type}")

    return {
        "product_id": product_id,
        "name": product["name"],
        "type": product["type"],
        "score_global": global_score,
        "score_species": int(sp_score * 100),
        "score_season": int(se_score * 100),
        "score_soil": int(so_score * 100),
        "price_cad": product["price_cad"],
        "weight_kg": product["weight_kg"],
        "duration_weeks": product["duration_weeks"],
        "minerals": product["minerals"],
        "description": product["description"],
        "tags": product["tags"],
        "optimal_for": optimal_for,
    }


def score_all_products(species: str, season: str, soil_type: str) -> dict:
    """Score et classement de tous les produits pour un contexte."""
    results = []
    for pid in PRODUCT_CATALOG:
        score = compute_product_score(pid, species, season, soil_type)
        if "error" not in score:
            results.append(score)

    results.sort(key=lambda x: x["score_global"], reverse=True)
    return {
        "context": {"species": species, "season": season, "soil_type": soil_type},
        "products": results,
        "total": len(results),
    }


def compare_products(product_ids: list, species: str, season: str, soil_type: str) -> dict:
    """Comparaison cote a cote de 2-4 produits."""
    compared = []
    for pid in product_ids[:4]:
        score = compute_product_score(pid, species, season, soil_type)
        if "error" not in score:
            compared.append(score)

    if not compared:
        return {"error": "Aucun produit valide pour comparaison"}

    best = max(compared, key=lambda x: x["score_global"])
    return {
        "context": {"species": species, "season": season, "soil_type": soil_type},
        "products": compared,
        "best_product": best["product_id"],
        "best_score": best["score_global"],
    }


def get_shop_products(species: str = None, season: str = None, soil_type: str = None,
                      min_score: int = 0, product_type: str = None) -> dict:
    """Liste produits filtrable pour le magasin intelligent."""
    results = []
    for pid, product in PRODUCT_CATALOG.items():
        if product_type and product["type"] != product_type:
            continue

        sp = species or "chevreuil"
        se = season or "printemps"
        so = soil_type or "mixte"

        score_data = compute_product_score(pid, sp, se, so)
        if score_data.get("score_global", 0) >= min_score:
            results.append(score_data)

    results.sort(key=lambda x: x["score_global"], reverse=True)
    return {
        "filters": {
            "species": species, "season": season, "soil_type": soil_type,
            "min_score": min_score, "product_type": product_type,
        },
        "products": results,
        "total": len(results),
    }
