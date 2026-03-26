"""
×5500 — ENERGY_PROTEIN_ENGINE
Analyse saisonniere energie/proteines.
Besoins physiologiques: croissance bois, lactation, rut, hiver.
"""

ENERGY_PROTEIN_PROFILES = {
    "chevreuil": {
        "printemps": {
            "phase": "Croissance des bois + recuperation hivernale",
            "energy_need": "ELEVE",
            "protein_need": "TRES ELEVE",
            "energy_blocks": [
                {"name": "Bloc energetique avoine-melasse", "brand": "Sportsman's Choice Energy", "price_cad": 16.99, "duration_weeks": 6},
            ],
            "protein_blocks": [
                {"name": "Bloc proteine 20% soja", "brand": "Purina AntlerMax 20", "price_cad": 34.99, "duration_weeks": 8},
            ],
            "seasonal_mix": {
                "name": "Melange Printemps Chevreuil",
                "ingredients": ["Avoine roulee 40%", "Tourteau soja 25%", "Mais concasse 20%", "Melasse 10%", "Minerals 5%"],
                "cost_per_25kg_cad": 42.99,
                "coverage_m2": 4,
            },
        },
        "pre_rut": {
            "phase": "Pre-rut: stockage energetique + marquage territorial",
            "energy_need": "TRES ELEVE",
            "protein_need": "ELEVE",
            "energy_blocks": [
                {"name": "Bloc energetique mais-melasse haute densite", "brand": "Evolved Habitats Deer Cane", "price_cad": 19.99, "duration_weeks": 4},
            ],
            "protein_blocks": [
                {"name": "Bloc proteine 16% multi-source", "brand": "Whitetail Institute 30-06", "price_cad": 29.99, "duration_weeks": 6},
            ],
            "seasonal_mix": {
                "name": "Melange Pre-Rut Chevreuil",
                "ingredients": ["Mais concasse 35%", "Avoine 25%", "Tourteau soja 20%", "Pommes sechees 10%", "Melasse 5%", "Minerals 5%"],
                "cost_per_25kg_cad": 48.99,
                "coverage_m2": 4,
            },
        },
        "ete": {
            "phase": "Ete: croissance bois active + lactation biches",
            "energy_need": "MODERE",
            "protein_need": "ELEVE",
            "energy_blocks": [
                {"name": "Bloc energetique standard", "brand": "Trophy Rock Energy", "price_cad": 14.99, "duration_weeks": 8},
            ],
            "protein_blocks": [
                {"name": "Bloc proteine 18% luzerne", "brand": "Record Rack Protein", "price_cad": 27.99, "duration_weeks": 8},
            ],
            "seasonal_mix": {
                "name": "Melange Ete Chevreuil",
                "ingredients": ["Luzerne deshydratee 30%", "Avoine 25%", "Tourteau soja 20%", "Mais 15%", "Minerals 10%"],
                "cost_per_25kg_cad": 39.99,
                "coverage_m2": 4,
            },
        },
        "rut": {
            "phase": "Rut: depense energetique extreme, males en deficit",
            "energy_need": "EXTREME",
            "protein_need": "MODERE",
            "energy_blocks": [
                {"name": "Bloc energetique haute densite rut", "brand": "C'Mere Deer Rut Energy", "price_cad": 22.99, "duration_weeks": 3},
            ],
            "protein_blocks": [
                {"name": "Bloc proteine maintenance", "brand": "Purina Quick Draw", "price_cad": 24.99, "duration_weeks": 6},
            ],
            "seasonal_mix": {
                "name": "Melange Rut Chevreuil",
                "ingredients": ["Mais haute energie 45%", "Avoine 20%", "Melasse 15%", "Gras vegetal 10%", "Minerals 10%"],
                "cost_per_25kg_cad": 52.99,
                "coverage_m2": 4,
            },
        },
        "post_rut": {
            "phase": "Post-rut: recuperation males + gestation femelles",
            "energy_need": "ELEVE",
            "protein_need": "ELEVE",
            "energy_blocks": [
                {"name": "Bloc energetique recuperation", "brand": "Evolved Habitats Black Magic", "price_cad": 17.99, "duration_weeks": 6},
            ],
            "protein_blocks": [
                {"name": "Bloc proteine 20% recuperation", "brand": "Ridley Recovery Block", "price_cad": 31.99, "duration_weeks": 8},
            ],
            "seasonal_mix": {
                "name": "Melange Post-Rut Chevreuil",
                "ingredients": ["Avoine 30%", "Tourteau soja 25%", "Mais 20%", "Luzerne 15%", "Minerals 10%"],
                "cost_per_25kg_cad": 44.99,
                "coverage_m2": 4,
            },
        },
        "hiver": {
            "phase": "Hiver: survie, conservation energetique, gestation",
            "energy_need": "CRITIQUE",
            "protein_need": "MODERE",
            "energy_blocks": [
                {"name": "Bloc energetique hiver survie", "brand": "Wildgame Innovations Winter", "price_cad": 21.99, "duration_weeks": 4},
            ],
            "protein_blocks": [
                {"name": "Bloc proteine hiver basse temperature", "brand": "Purina WinterCare", "price_cad": 26.99, "duration_weeks": 8},
            ],
            "seasonal_mix": {
                "name": "Melange Hiver Chevreuil",
                "ingredients": ["Mais haute energie 50%", "Avoine 20%", "Gras vegetal 15%", "Melasse 10%", "Minerals 5%"],
                "cost_per_25kg_cad": 46.99,
                "coverage_m2": 4,
            },
        },
    },
}


def compute_energy_protein(species: str, season: str) -> dict:
    sp_data = ENERGY_PROTEIN_PROFILES.get(species, ENERGY_PROTEIN_PROFILES.get("chevreuil"))
    season_data = sp_data.get(season, sp_data.get("ete"))
    return {
        "species": species,
        "season": season,
        "phase": season_data["phase"],
        "energy_need": season_data["energy_need"],
        "protein_need": season_data["protein_need"],
        "energy_blocks": season_data["energy_blocks"],
        "protein_blocks": season_data["protein_blocks"],
        "seasonal_mix": season_data["seasonal_mix"],
    }
