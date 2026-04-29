"""
×5700 — COST_ENGINE
Couts unitaires + couts totaux. Initial, reactivations, annuel, par visite.
Comparaison scenarios bois mou vs bois dur.
"""
from .x5200_mineral_recommendation import compute_recommendations
from .x5500_energy_protein import compute_energy_protein
from .x5600_site_guide import SUBSTRATE_OPTIONS


def compute_costs(species: str, season: str, soil_type: str, substrate: str = "bois_mou", site_minerals: dict = None) -> dict:
    """Calcul complet des couts."""
    reco = compute_recommendations(species, season, soil_type, site_minerals)
    energy = compute_energy_protein(species, season)
    sub = SUBSTRATE_OPTIONS.get(substrate, SUBSTRATE_OPTIONS["bois_mou"])

    mineral_cost = 0
    mineral_items = []
    for r in reco["recommendations"]:
        if r["priority"] in ("CRITIQUE", "RECOMMANDE"):
            qty = 2 if r["priority"] == "CRITIQUE" else 1
            cost = r["price_cad"] * qty
            mineral_cost += cost
            mineral_items.append({
                "name": r["name"],
                "product": r["brand"],
                "qty": qty,
                "unit_cad": r["price_cad"],
                "total_cad": round(cost, 2),
                "priority": r["priority"],
            })

    energy_cost = sum(b["price_cad"] for b in energy["energy_blocks"])
    protein_cost = sum(b["price_cad"] for b in energy["protein_blocks"])
    mix_cost = energy["seasonal_mix"]["cost_per_25kg_cad"]
    supplement_cost = round(energy_cost + protein_cost + mix_cost, 2)

    initial_cost = round(mineral_cost + supplement_cost, 2)

    react_weeks = sub["reactivation_weeks"]
    annual_reactivations = int(26 / react_weeks)
    reactivation_cost = round(mineral_cost * 0.6, 2)
    annual_cost = round(initial_cost + (reactivation_cost * annual_reactivations), 2)
    cost_per_visit = round(annual_cost / max(annual_reactivations + 1, 1), 2)

    return {
        "substrate": substrate,
        "substrate_name": sub["name"],
        "mineral_items": mineral_items,
        "mineral_cost_initial_cad": round(mineral_cost, 2),
        "supplement_cost_cad": supplement_cost,
        "initial_cost_cad": initial_cost,
        "reactivation_frequency_weeks": react_weeks,
        "annual_reactivations": annual_reactivations,
        "reactivation_cost_cad": reactivation_cost,
        "annual_cost_cad": annual_cost,
        "cost_per_visit_cad": cost_per_visit,
        "score_data": reco["score_data"],
    }


def compare_substrates(species: str, season: str, soil_type: str, site_minerals: dict = None) -> dict:
    """Comparaison bois mou vs bois dur."""
    bois_mou = compute_costs(species, season, soil_type, "bois_mou", site_minerals)
    bois_dur = compute_costs(species, season, soil_type, "bois_dur", site_minerals)

    return {
        "bois_mou": bois_mou,
        "bois_dur": bois_dur,
        "savings_annual_cad": round(abs(bois_dur["annual_cost_cad"] - bois_mou["annual_cost_cad"]), 2),
        "recommended": "bois_mou" if bois_mou["annual_cost_cad"] <= bois_dur["annual_cost_cad"] else "bois_dur",
        "recommendation_reason": "Liberation progressive = moins de reactivations" if bois_mou["annual_cost_cad"] <= bois_dur["annual_cost_cad"] else "Cout initial inferieur malgre reactivations plus frequentes",
    }
