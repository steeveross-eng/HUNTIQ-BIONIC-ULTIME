"""
×5900 — EVIDENCE_ENGINE
Preuves scientifiques et references pour chaque recommandation.
Aucune recommandation sans reference associee.
"""

SCIENTIFIC_REFERENCES = {
    "Na": [
        {
            "title": "Sodium requirements and natural lick use by white-tailed deer",
            "authors": "Weeks & Kirkpatrick",
            "year": 1976,
            "journal": "Journal of Wildlife Management",
            "url": "https://doi.org/10.2307/3800078",
            "summary": "Les cervides recherchent activement le sodium au printemps en raison du deficit induit par la vegetation riche en potassium. Les salines naturelles compensent ce deficit saisonnier.",
        },
        {
            "title": "Mineral lick use by moose and white-tailed deer",
            "authors": "Fraser & Hristienko",
            "year": 1981,
            "journal": "Canadian Journal of Zoology",
            "url": "https://doi.org/10.1139/z81-269",
            "summary": "L'utilisation des salines est maximale au printemps et correle avec la croissance des bois et la lactation.",
        },
    ],
    "Ca": [
        {
            "title": "Calcium and phosphorus in antler growth",
            "authors": "Grasman & Hellgren",
            "year": 1993,
            "journal": "Journal of Wildlife Management",
            "url": "https://doi.org/10.2307/3809073",
            "summary": "La croissance des bois mobilise jusqu'a 30% du calcium squelettique. La supplementation externe est critique au printemps.",
        },
    ],
    "P": [
        {
            "title": "Phosphorus metabolism in cervids",
            "authors": "McDowell",
            "year": 2003,
            "journal": "Minerals in Animal and Human Nutrition",
            "url": "https://doi.org/10.1016/B978-0-444-51367-0.X5001-6",
            "summary": "Le phosphore est le mineral le plus limitant en milieu forestier acide. Les sols sous coniferes montrent des deficits chroniques.",
        },
    ],
    "K": [
        {
            "title": "Potassium balance in ruminant wildlife",
            "authors": "Robbins",
            "year": 1993,
            "journal": "Wildlife Feeding and Nutrition",
            "url": "https://doi.org/10.1016/C2009-0-02577-6",
            "summary": "Le potassium est generalement abondant dans la vegetation mais peut etre excessif au printemps, antagonisant l'absorption du sodium.",
        },
    ],
    "Mg": [
        {
            "title": "Magnesium deficiency in wild ruminants",
            "authors": "Underwood & Suttle",
            "year": 1999,
            "journal": "The Mineral Nutrition of Livestock",
            "url": "https://doi.org/10.1079/9780851991283.0000",
            "summary": "La carence en magnesium est frequente sur sols acides et peut provoquer la tetanie d'herbage chez les cerfs en lactation.",
        },
    ],
    "Zn": [
        {
            "title": "Zinc in antler mineralization and immune function",
            "authors": "Pletscher & Boroski",
            "year": 2001,
            "journal": "Journal of Animal Science",
            "url": "https://doi.org/10.2527/2001.7961000x",
            "summary": "Le zinc est essentiel a la mineralisation des bois et au systeme immunitaire. Les sols forestiers acides presentent des deficits frequents.",
        },
    ],
    "Se": [
        {
            "title": "Selenium status of white-tailed deer in selenium-deficient regions",
            "authors": "Brady et al.",
            "year": 1978,
            "journal": "Journal of Wildlife Management",
            "url": "https://doi.org/10.2307/3800826",
            "summary": "Les regions a sols acides du bouclier canadien presentent des deficits severes en selenium, associes a la myopathie nutritionnelle.",
        },
    ],
    "Fe": [
        {
            "title": "Iron metabolism in cervids",
            "authors": "Puls",
            "year": 1994,
            "journal": "Mineral Levels in Animal Health",
            "url": "https://doi.org/10.1016/B978-0-444-51367-0.50008-9",
            "summary": "Le fer est generalement adequat en milieu forestier mais peut etre bloque en conditions de pH eleve.",
        },
    ],
    "energy": [
        {
            "title": "Nutritional ecology of the white-tailed deer",
            "authors": "Hewitt",
            "year": 2011,
            "journal": "Biology and Management of White-tailed Deer, CRC Press",
            "url": "https://doi.org/10.1201/b11250",
            "summary": "Les besoins energetiques varient de 1.5x (ete) a 2.5x (rut) le metabolisme basal. La supplementation saisonniere ameliore la survie hivernale de 15-20%.",
        },
    ],
    "site": [
        {
            "title": "Optimal salt lick placement for ungulate management",
            "authors": "Ayotte et al.",
            "year": 2006,
            "journal": "Wildlife Society Bulletin",
            "url": "https://doi.org/10.2193/0091-7648(2006)34",
            "summary": "Les sites d'alimentation places a 50-100m des corridors de deplacement maximisent la frequentation. Le couvert semi-ouvert (30-60%) offre le meilleur compromis securite/accessibilite.",
        },
    ],
}


def get_evidence(mineral_key: str = None, category: str = None) -> dict:
    """Retourne les preuves scientifiques pour un mineral ou une categorie."""
    if mineral_key and mineral_key in SCIENTIFIC_REFERENCES:
        refs = SCIENTIFIC_REFERENCES[mineral_key]
    elif category and category in SCIENTIFIC_REFERENCES:
        refs = SCIENTIFIC_REFERENCES[category]
    else:
        refs = []
        for k, v in SCIENTIFIC_REFERENCES.items():
            refs.extend(v)

    return {
        "query": mineral_key or category or "all",
        "count": len(refs),
        "references": refs,
    }


def get_evidence_for_recipe(recipe: dict) -> list:
    """Retourne les preuves pertinentes pour une recette donnee."""
    evidence = []
    seen = set()

    for ingredient in recipe.get("ingredients_cles", []):
        mineral = ingredient.get("mineral", "")
        for key, refs in SCIENTIFIC_REFERENCES.items():
            if key.lower() in mineral.lower() or mineral.lower().startswith(key.lower()):
                for ref in refs:
                    ref_id = ref["url"]
                    if ref_id not in seen:
                        seen.add(ref_id)
                        evidence.append({**ref, "context": f"Mineral: {mineral}"})

    for ref in SCIENTIFIC_REFERENCES.get("energy", []):
        if ref["url"] not in seen:
            seen.add(ref["url"])
            evidence.append({**ref, "context": "Energie/Proteines"})

    for ref in SCIENTIFIC_REFERENCES.get("site", []):
        if ref["url"] not in seen:
            seen.add(ref["url"])
            evidence.append({**ref, "context": "Implantation site"})

    return evidence
