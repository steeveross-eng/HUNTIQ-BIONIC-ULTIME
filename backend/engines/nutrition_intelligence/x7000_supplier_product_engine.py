"""
x7000 — SUPPLIER_PRODUCT_ENGINE
Pipeline de soumission et validation produits fournisseurs.
Flux: Soumission -> Validation automatique -> Validation humaine -> Activation magasin.
BCE-4X / STEEVE-MAX V6

Ce module gere le cycle de vie complet des soumissions
de produits par les fournisseurs avant leur integration
dans le catalogue BIONIC.
"""

# Statuts du pipeline
PIPELINE_DRAFT = "brouillon"
PIPELINE_SUBMITTED = "soumis"
PIPELINE_AUTO_VALIDATED = "validation_auto_ok"
PIPELINE_AUTO_REJECTED = "validation_auto_rejetee"
PIPELINE_HUMAN_REVIEW = "revue_humaine"
PIPELINE_APPROVED = "approuve"
PIPELINE_REJECTED = "rejete"
PIPELINE_ACTIVE = "actif_magasin"

# Criteres de validation automatique
AUTO_VALIDATION_CRITERIA = {
    "nom_produit_min_length": 5,
    "description_min_length": 20,
    "prix_min_cad": 1.0,
    "prix_max_cad": 500.0,
    "poids_min_kg": 0.1,
    "poids_max_kg": 100.0,
    "certifications_requises": ["ACIA"],
    "categories_valides": [
        "bloc_mineral", "supplement_mineral", "bloc_proteine",
        "melange_fourrager", "semence_nourricier", "attractif",
        "bloc_energetique", "sel_naturel",
    ],
}

# Stockage en memoire des soumissions (POC — remplacer par MongoDB en production)
_submissions_store = {}
_submission_counter = 0


def submit_product(supplier_data: dict) -> dict:
    """Soumission initiale d'un produit par un fournisseur."""
    global _submission_counter
    _submission_counter += 1
    submission_id = f"SUB-{_submission_counter:05d}"

    # Validation automatique
    auto_result = _auto_validate(supplier_data)

    status = PIPELINE_AUTO_VALIDATED if auto_result["passed"] else PIPELINE_AUTO_REJECTED

    submission = {
        "submission_id": submission_id,
        "status": status,
        "supplier": supplier_data.get("supplier_name", "Inconnu"),
        "product": {
            "name": supplier_data.get("product_name", ""),
            "description": supplier_data.get("description", ""),
            "category": supplier_data.get("category", ""),
            "price_cad": supplier_data.get("price_cad", 0),
            "weight_kg": supplier_data.get("weight_kg", 0),
            "minerals": supplier_data.get("minerals", []),
            "certifications": supplier_data.get("certifications", []),
            "species_target": supplier_data.get("species_target", []),
            "brand": supplier_data.get("brand", ""),
        },
        "auto_validation": auto_result,
        "human_review": None,
        "pipeline_history": [
            {"status": PIPELINE_SUBMITTED, "action": "Soumission fournisseur"},
            {"status": status, "action": "Validation automatique"},
        ],
    }

    _submissions_store[submission_id] = submission

    return {
        "submission_id": submission_id,
        "status": status,
        "auto_validation": auto_result,
        "next_step": "revue_humaine" if auto_result["passed"] else "correction_et_resoumission",
    }


def _auto_validate(data: dict) -> dict:
    """Validation automatique du produit soumis."""
    checks = []
    passed = True

    # Nom du produit
    name = data.get("product_name", "")
    name_ok = len(name) >= AUTO_VALIDATION_CRITERIA["nom_produit_min_length"]
    checks.append({"criteria": "Nom du produit (min 5 car.)", "passed": name_ok})
    if not name_ok:
        passed = False

    # Description
    desc = data.get("description", "")
    desc_ok = len(desc) >= AUTO_VALIDATION_CRITERIA["description_min_length"]
    checks.append({"criteria": "Description (min 20 car.)", "passed": desc_ok})
    if not desc_ok:
        passed = False

    # Prix
    price = data.get("price_cad", 0)
    price_ok = AUTO_VALIDATION_CRITERIA["prix_min_cad"] <= price <= AUTO_VALIDATION_CRITERIA["prix_max_cad"]
    checks.append({"criteria": f"Prix ({AUTO_VALIDATION_CRITERIA['prix_min_cad']}-{AUTO_VALIDATION_CRITERIA['prix_max_cad']}$)", "passed": price_ok})
    if not price_ok:
        passed = False

    # Poids
    weight = data.get("weight_kg", 0)
    weight_ok = AUTO_VALIDATION_CRITERIA["poids_min_kg"] <= weight <= AUTO_VALIDATION_CRITERIA["poids_max_kg"]
    checks.append({"criteria": f"Poids ({AUTO_VALIDATION_CRITERIA['poids_min_kg']}-{AUTO_VALIDATION_CRITERIA['poids_max_kg']}kg)", "passed": weight_ok})
    if not weight_ok:
        passed = False

    # Categorie
    cat = data.get("category", "")
    cat_ok = cat in AUTO_VALIDATION_CRITERIA["categories_valides"]
    checks.append({"criteria": "Categorie valide", "passed": cat_ok})
    if not cat_ok:
        passed = False

    # Certifications (au moins ACIA)
    certs = data.get("certifications", [])
    cert_ok = any("ACIA" in c.upper() for c in certs)
    checks.append({"criteria": "Certification ACIA requise", "passed": cert_ok})
    if not cert_ok:
        passed = False

    return {
        "passed": passed,
        "checks": checks,
        "total_checks": len(checks),
        "passed_checks": sum(1 for c in checks if c["passed"]),
    }


def review_submission(submission_id: str, approved: bool, reviewer_notes: str = "") -> dict:
    """Revue humaine d'une soumission."""
    submission = _submissions_store.get(submission_id)
    if not submission:
        return {"error": f"Soumission introuvable: {submission_id}"}

    new_status = PIPELINE_APPROVED if approved else PIPELINE_REJECTED

    submission["status"] = new_status
    submission["human_review"] = {
        "approved": approved,
        "notes": reviewer_notes,
        "reviewer": "STEEVE-MAX",
    }
    submission["pipeline_history"].append({
        "status": new_status,
        "action": f"Revue humaine: {'Approuve' if approved else 'Rejete'}",
    })

    return {
        "submission_id": submission_id,
        "status": new_status,
        "human_review": submission["human_review"],
        "next_step": "activation_magasin" if approved else "archive",
    }


def activate_product(submission_id: str) -> dict:
    """Activation d'un produit approuve dans le magasin."""
    submission = _submissions_store.get(submission_id)
    if not submission:
        return {"error": f"Soumission introuvable: {submission_id}"}

    if submission["status"] != PIPELINE_APPROVED:
        return {"error": f"Soumission non approuvee (status: {submission['status']})"}

    submission["status"] = PIPELINE_ACTIVE
    submission["pipeline_history"].append({
        "status": PIPELINE_ACTIVE,
        "action": "Produit active dans le magasin BIONIC",
    })

    return {
        "submission_id": submission_id,
        "status": PIPELINE_ACTIVE,
        "product": submission["product"],
        "message": "Produit active avec succes dans le magasin BIONIC",
    }


def get_submission(submission_id: str) -> dict:
    """Recupere une soumission par ID."""
    submission = _submissions_store.get(submission_id)
    if not submission:
        return {"error": f"Soumission introuvable: {submission_id}"}
    return submission


def get_all_submissions(status_filter: str = None) -> dict:
    """Liste toutes les soumissions avec filtre optionnel par statut."""
    results = list(_submissions_store.values())
    if status_filter:
        results = [s for s in results if s["status"] == status_filter]
    return {
        "submissions": results,
        "total": len(results),
        "status_filter": status_filter,
    }


def get_pipeline_stats() -> dict:
    """Statistiques du pipeline de soumission."""
    all_subs = list(_submissions_store.values())
    stats = {}
    for s in all_subs:
        stats[s["status"]] = stats.get(s["status"], 0) + 1
    return {
        "total_submissions": len(all_subs),
        "by_status": stats,
        "auto_validation_criteria": AUTO_VALIDATION_CRITERIA,
    }
