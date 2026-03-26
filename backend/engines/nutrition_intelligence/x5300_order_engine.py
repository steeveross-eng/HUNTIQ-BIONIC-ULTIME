"""
×5300 — ORDER_ENGINE
Bouton COMMANDE intelligent: contexte site → produit recommande → recapitulatif.
"""
from .x5200_mineral_recommendation import compute_recommendations


def generate_order(species: str, season: str, soil_type: str, mineral_key: str = None, site_minerals: dict = None) -> dict:
    """
    Genere une commande pour un mineral specifique ou le pack complet.
    """
    reco_data = compute_recommendations(species, season, soil_type, site_minerals)
    recommendations = reco_data["recommendations"]

    if mineral_key:
        targets = [r for r in recommendations if r["mineral"] == mineral_key]
    else:
        targets = [r for r in recommendations if r["priority"] in ("CRITIQUE", "RECOMMANDE")]

    items = []
    total_cost = 0.0
    for r in targets:
        qty = 2 if r["priority"] == "CRITIQUE" else 1
        cost = r["price_cad"] * qty
        total_cost += cost
        items.append({
            "mineral": r["mineral"],
            "name": r["name"],
            "product": r["product"],
            "brand": r["brand"],
            "dosage": r["dosage"],
            "quantity": qty,
            "unit_price_cad": r["price_cad"],
            "total_price_cad": round(cost, 2),
            "priority": r["priority"],
            "zone": r["zone"],
        })

    reactivation_weeks = 8 if soil_type in ("sableux", "acide") else 10
    annual_reactivations = int(26 / reactivation_weeks)
    annual_cost = round(total_cost * annual_reactivations, 2)

    return {
        "order_type": "mineral_specifique" if mineral_key else "pack_complet",
        "context": {
            "species": species,
            "season": season,
            "soil_type": soil_type,
        },
        "items": items,
        "summary": {
            "nb_items": len(items),
            "cost_initial_cad": round(total_cost, 2),
            "reactivation_frequency_weeks": reactivation_weeks,
            "annual_reactivations": annual_reactivations,
            "cost_annual_cad": annual_cost,
            "cost_per_visit_cad": round(annual_cost / max(annual_reactivations, 1), 2),
        },
        "score_data": reco_data["score_data"],
    }
