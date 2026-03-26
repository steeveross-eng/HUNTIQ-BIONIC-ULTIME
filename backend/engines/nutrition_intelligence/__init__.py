"""Nutrition Intelligence Engine Package — ×5000 SUPRA"""
from .x5100_mineral_score import compute_mineral_score
from .x5200_mineral_recommendation import compute_recommendations
from .x5300_order_engine import generate_order
from .x5500_energy_protein import compute_energy_protein
from .x5600_site_guide import generate_site_guide
from .x5700_cost_engine import compute_costs, compare_substrates
from .x5800_recipe_engine import generate_recipe
from .x5900_evidence_engine import get_evidence, get_evidence_for_recipe
