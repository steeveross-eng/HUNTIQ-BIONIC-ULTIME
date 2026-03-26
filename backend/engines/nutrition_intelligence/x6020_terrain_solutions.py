"""
x6020 — TERRAIN_SOLUTIONS_ENGINE
Association automatique des deficits nutritionnels aux solutions terrain.
Champs nourriciers, blocs mineraux, attractifs naturels.
BCE-4X / STEEVE-MAX V6

Solutions basees sur les pratiques reelles d'amenagement faunique
utilisees au Quebec et dans l'est du Canada.
Sources: MFFP Quebec, MAPAQ, associations regionales de chasse.
"""

# Solutions terrain par type de deficit
TERRAIN_SOLUTIONS = {
    "sodium": {
        "deficit_label": "Carence en sodium (Na)",
        "severity_threshold": 60,
        "solutions": [
            {
                "type": "bloc_mineral",
                "name": "Bloc salin naturel",
                "description": "Sel naturel 100% pour cerfs/orignaux. Dissolution lente sur 6-12 mois.",
                "brands": ["Trophy Rock Four65", "Redmond Natural Salt"],
                "placement": "Sol decouvert, 50-100m du couvert forestier",
                "efficacy_months": 6,
                "cost_range_cad": "12-28$",
                "priority": "CRITIQUE",
            },
            {
                "type": "saline_naturelle",
                "name": "Creation saline artificielle",
                "description": "Excavation 1m x 1m, remplissage argile salee + sel de mer. Recree une saline naturelle permanente.",
                "brands": [],
                "placement": "Pres d'un cours d'eau, sol argileux ideal",
                "efficacy_months": 24,
                "cost_range_cad": "40-80$ (installation)",
                "priority": "RECOMMANDE",
            },
        ],
    },
    "calcium": {
        "deficit_label": "Carence en calcium (Ca)",
        "severity_threshold": 55,
        "solutions": [
            {
                "type": "bloc_mineral",
                "name": "Bloc calcium-phosphore",
                "description": "Supplement Ca/P ratio 2:1 pour croissance osseuse et bois de cerfs.",
                "brands": ["Pro-Cal Lick", "Purina AntlerMax Zn"],
                "placement": "A cote des pistes principales, zone de repos",
                "efficacy_months": 3,
                "cost_range_cad": "18-35$",
                "priority": "CRITIQUE",
            },
            {
                "type": "champ_nourricier",
                "name": "Implantation trefle blanc (Trifolium repens)",
                "description": "Legumineuse riche en calcium, fixatrice d'azote. Attrait printanier et estival.",
                "brands": ["Trefle Ladino geant"],
                "placement": "Clairiere ensoleillée, sol pH 6.0-7.0",
                "efficacy_months": 36,
                "cost_range_cad": "120-200$ / hectare",
                "priority": "RECOMMANDE",
            },
        ],
    },
    "phosphore": {
        "deficit_label": "Carence en phosphore (P)",
        "severity_threshold": 55,
        "solutions": [
            {
                "type": "bloc_mineral",
                "name": "Bloc phosphore enrichi",
                "description": "Phosphore organique haute biodisponibilite pour metabolisme energetique.",
                "brands": ["BioMineral P Plus", "Ridley Phosphorus Block"],
                "placement": "Zone de gagnage, acces facile",
                "efficacy_months": 3,
                "cost_range_cad": "20-38$",
                "priority": "CRITIQUE",
            },
            {
                "type": "champ_nourricier",
                "name": "Implantation chicoree (Cichorium intybus)",
                "description": "Plante riche en phosphore et oligo-elements. Tres attractive pour cerfs.",
                "brands": ["Puna Chicory", "Whitetail Institute Chicory Plus"],
                "placement": "Sol bien draine, ensoleille, pH 5.5-7.0",
                "efficacy_months": 24,
                "cost_range_cad": "150-250$ / hectare",
                "priority": "RECOMMANDE",
            },
        ],
    },
    "potassium": {
        "deficit_label": "Carence en potassium (K)",
        "severity_threshold": 50,
        "solutions": [
            {
                "type": "bloc_mineral",
                "name": "Supplement potassium",
                "description": "Potassium pour fonctions nerveuses et musculaires.",
                "brands": ["Whitetail K-Source"],
                "placement": "Zone d'alimentation reguliere",
                "efficacy_months": 4,
                "cost_range_cad": "15-32$",
                "priority": "RECOMMANDE",
            },
            {
                "type": "champ_nourricier",
                "name": "Implantation luzerne (Medicago sativa)",
                "description": "Reine des fourrageres, tres riche en K, Ca, proteines. Attrait majeur 4 saisons.",
                "brands": ["Luzerne certifiee Quebec"],
                "placement": "Sol bien draine, pH 6.5-7.5, plein soleil",
                "efficacy_months": 60,
                "cost_range_cad": "180-350$ / hectare",
                "priority": "RECOMMANDE",
            },
        ],
    },
    "magnesium": {
        "deficit_label": "Carence en magnesium (Mg)",
        "severity_threshold": 55,
        "solutions": [
            {
                "type": "bloc_mineral",
                "name": "Supplement magnesium",
                "description": "Magnesium chelate pour metabolisme energetique et osseux.",
                "brands": ["Evolved Mag Mix", "Trophy Rock Four65"],
                "placement": "Zone ombragee, pres des sentiers",
                "efficacy_months": 4,
                "cost_range_cad": "14-26$",
                "priority": "RECOMMANDE",
            },
        ],
    },
    "selenium": {
        "deficit_label": "Carence en selenium (Se)",
        "severity_threshold": 45,
        "solutions": [
            {
                "type": "bloc_mineral",
                "name": "Bloc selenium + vitamine E",
                "description": "Se/Vit E essentiel pour immunite et reproduction. Attention dosage reglemente.",
                "brands": ["Ridley Se-Vit Block"],
                "placement": "Zone de repos, acces controle",
                "efficacy_months": 3,
                "cost_range_cad": "22-40$",
                "priority": "CRITIQUE",
            },
        ],
    },
    "fer": {
        "deficit_label": "Carence en fer (Fe)",
        "severity_threshold": 50,
        "solutions": [
            {
                "type": "bloc_mineral",
                "name": "Bloc fer chelate",
                "description": "Fer organique pour hemoglobine et transport d'oxygene.",
                "brands": ["Sportsman's Fe Block"],
                "placement": "Zone de gagnage",
                "efficacy_months": 4,
                "cost_range_cad": "10-18$",
                "priority": "RECOMMANDE",
            },
        ],
    },
    "zinc": {
        "deficit_label": "Carence en zinc (Zn)",
        "severity_threshold": 50,
        "solutions": [
            {
                "type": "bloc_mineral",
                "name": "Bloc zinc chelate premium",
                "description": "Zinc essentiel pour croissance bois, cicatrisation, immunite.",
                "brands": ["Purina AntlerMax Zn"],
                "placement": "Pres des zones de frottis/grattoirs",
                "efficacy_months": 3,
                "cost_range_cad": "25-45$",
                "priority": "CRITIQUE",
            },
        ],
    },
    "energie": {
        "deficit_label": "Deficit energetique saisonnier",
        "severity_threshold": 0,
        "solutions": [
            {
                "type": "champ_nourricier",
                "name": "Implantation brassica (Brassica rapa / napus)",
                "description": "Navets, colza, chou fourrager. Source d'energie automnale/hivernale apres gel.",
                "brands": ["Whitetail Institute Winter-Greens", "Evolved Harvest Fall Brassica"],
                "placement": "Sol fertile, plein soleil, semis mi-juillet",
                "efficacy_months": 6,
                "cost_range_cad": "100-200$ / hectare",
                "priority": "CRITIQUE",
            },
            {
                "type": "champ_nourricier",
                "name": "Implantation avoine (Avena sativa)",
                "description": "Cereale fourragere haute energie. Semis printemps ou automne.",
                "brands": ["Avoine fourragere certifiee"],
                "placement": "Sol bien draine, pH 6.0-7.0",
                "efficacy_months": 4,
                "cost_range_cad": "80-150$ / hectare",
                "priority": "RECOMMANDE",
            },
            {
                "type": "attractif_naturel",
                "name": "Station pommier sauvage",
                "description": "Plantation de pommiers sauvages (Malus sylvestris). Fruits tres attractifs en automne.",
                "brands": [],
                "placement": "Lisiere forestiere, sol profond",
                "efficacy_months": 120,
                "cost_range_cad": "25-50$ / arbre",
                "priority": "RECOMMANDE",
            },
        ],
    },
    "proteines": {
        "deficit_label": "Deficit proteique saisonnier",
        "severity_threshold": 0,
        "solutions": [
            {
                "type": "bloc_mineral",
                "name": "Bloc proteine 20%",
                "description": "Supplement proteine soja/mais pour cerfs en croissance ou post-rut.",
                "brands": ["Purina AntlerMax 20", "Record Rack Protein Block"],
                "placement": "Zone de repos, acces regulier",
                "efficacy_months": 2,
                "cost_range_cad": "28-45$",
                "priority": "CRITIQUE",
            },
            {
                "type": "champ_nourricier",
                "name": "Implantation soja fourrager",
                "description": "Legumineuse haute proteine (35-40%). Attrait estival/automnal.",
                "brands": ["Soja fourrager Eagle Seed"],
                "placement": "Sol fertile, pH 6.0-7.0, plein soleil",
                "efficacy_months": 5,
                "cost_range_cad": "200-350$ / hectare",
                "priority": "RECOMMANDE",
            },
        ],
    },
}


def get_solutions_for_deficits(mineral_scores: dict, energy_need: str = None, protein_need: str = None) -> dict:
    """
    Associe automatiquement les deficits nutritionnels aux solutions terrain.
    mineral_scores: dict {mineral_key: {score, zone, name}}
    energy_need: str (EXTREME, CRITIQUE, ELEVE, etc.)
    protein_need: str
    """
    solutions = []
    total_cost_min = 0.0
    total_cost_max = 0.0

    # Solutions minerales (basees sur les scores)
    for key, mineral in mineral_scores.items():
        mineral_key = key.lower()
        score = mineral.get("score", 100)
        zone = mineral.get("zone", "vert")

        if mineral_key in TERRAIN_SOLUTIONS:
            ts = TERRAIN_SOLUTIONS[mineral_key]
            if score < ts["severity_threshold"] or zone in ("rouge", "jaune"):
                for sol in ts["solutions"]:
                    cost_parts = sol["cost_range_cad"].replace("$", "").replace(" (installation)", "").split("-")
                    cost_min = float(cost_parts[0]) if cost_parts[0] else 0
                    cost_max = float(cost_parts[1]) if len(cost_parts) > 1 else cost_min
                    total_cost_min += cost_min
                    total_cost_max += cost_max
                    solutions.append({
                        "deficit": ts["deficit_label"],
                        "mineral_score": score,
                        "zone": zone,
                        **sol,
                    })

    # Solutions energetiques
    if energy_need and energy_need in ("EXTREME", "CRITIQUE", "TRES ELEVE"):
        for sol in TERRAIN_SOLUTIONS.get("energie", {}).get("solutions", []):
            cost_parts = sol["cost_range_cad"].replace("$", "").replace(" / hectare", "").replace(" / arbre", "").split("-")
            cost_min = float(cost_parts[0]) if cost_parts[0] else 0
            cost_max = float(cost_parts[1]) if len(cost_parts) > 1 else cost_min
            total_cost_min += cost_min
            total_cost_max += cost_max
            solutions.append({
                "deficit": "Deficit energetique saisonnier",
                "mineral_score": None,
                "zone": "rouge" if energy_need == "EXTREME" else "jaune",
                **sol,
            })

    # Solutions proteiques
    if protein_need and protein_need in ("EXTREME", "TRES ELEVE"):
        for sol in TERRAIN_SOLUTIONS.get("proteines", {}).get("solutions", []):
            cost_parts = sol["cost_range_cad"].replace("$", "").replace(" / hectare", "").split("-")
            cost_min = float(cost_parts[0]) if cost_parts[0] else 0
            cost_max = float(cost_parts[1]) if len(cost_parts) > 1 else cost_min
            total_cost_min += cost_min
            total_cost_max += cost_max
            solutions.append({
                "deficit": "Deficit proteique saisonnier",
                "mineral_score": None,
                "zone": "rouge" if protein_need == "EXTREME" else "jaune",
                **sol,
            })

    # Trier par priorite (CRITIQUE > RECOMMANDE)
    priority_order = {"CRITIQUE": 0, "RECOMMANDE": 1, "OPTIONNEL": 2}
    solutions.sort(key=lambda s: priority_order.get(s.get("priority", "OPTIONNEL"), 2))

    critiques = [s for s in solutions if s.get("priority") == "CRITIQUE"]
    recommandees = [s for s in solutions if s.get("priority") == "RECOMMANDE"]

    return {
        "solutions": solutions,
        "total": len(solutions),
        "critiques": len(critiques),
        "recommandees": len(recommandees),
        "cost_estimate_min_cad": round(total_cost_min, 2),
        "cost_estimate_max_cad": round(total_cost_max, 2),
        "categories": {
            "blocs_mineraux": [s for s in solutions if s["type"] == "bloc_mineral"],
            "champs_nourriciers": [s for s in solutions if s["type"] == "champ_nourricier"],
            "salines": [s for s in solutions if s["type"] == "saline_naturelle"],
            "attractifs": [s for s in solutions if s["type"] == "attractif_naturel"],
        },
    }


def get_all_terrain_solutions() -> dict:
    """Retourne le catalogue complet de solutions terrain."""
    all_solutions = []
    for key, data in TERRAIN_SOLUTIONS.items():
        for sol in data["solutions"]:
            all_solutions.append({
                "deficit_key": key,
                "deficit_label": data["deficit_label"],
                **sol,
            })
    return {
        "solutions": all_solutions,
        "total": len(all_solutions),
    }
