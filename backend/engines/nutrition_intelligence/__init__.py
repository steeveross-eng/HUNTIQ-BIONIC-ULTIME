"""Nutrition Intelligence Engine Package — x5000 SUPRA + x6000 + x6010-x6012

P22ΩΩ_DEPLOYMENT_FIX_Ω (2026-05-22) — Imports rendus **tolérants** aux modules
manquants : seul `x5100_mineral_score` est garanti opérationnel ; les autres
sont importés best-effort avec stub `None` si le fichier n'existe pas (évite
le crash de boot `ImportError` lors du déploiement). Les exports publics
restent identiques par rétro-compatibilité (callers vérifient `is None` si
besoin).
"""
import logging as _logging

_logger = _logging.getLogger("bionic.nutrition_intelligence")


def _safe_import(module_name: str, *symbols: str):
    """Import best-effort : retourne None pour chaque symbole si module absent."""
    try:
        mod = __import__(f"{__name__}.{module_name}", fromlist=symbols)
        return tuple(getattr(mod, s, None) for s in symbols)
    except ImportError as e:
        _logger.warning(f"[NUTRITION-INTELLIGENCE] module optionnel manquant: {module_name} ({e})")
        return tuple(None for _ in symbols)


# ─── Module canonique : DOIT exister (créé par P22ΩΩ_DEPLOYMENT_FIX_Ω) ───
from .x5100_mineral_score import compute_mineral_score  # noqa: E402

# ─── Modules optionnels : best-effort imports (None si fichier manquant) ───
(compute_recommendations,) = _safe_import("x5200_mineral_recommendation", "compute_recommendations")
(generate_order,) = _safe_import("x5300_order_engine", "generate_order")
(compute_energy_protein,) = _safe_import("x5500_energy_protein", "compute_energy_protein")
(generate_site_guide, get_ecological_zones) = _safe_import(
    "x5600_site_guide", "generate_site_guide", "get_ecological_zones"
)
(compute_costs, compare_substrates) = _safe_import(
    "x5700_cost_engine", "compute_costs", "compare_substrates"
)
(generate_recipe,) = _safe_import("x5800_recipe_engine", "generate_recipe")
(get_evidence, get_evidence_for_recipe) = _safe_import(
    "x5900_evidence_engine", "get_evidence", "get_evidence_for_recipe"
)
(compute_product_score, score_all_products, compare_products, get_shop_products) = _safe_import(
    "x6000_product_score", "compute_product_score", "score_all_products", "compare_products", "get_shop_products"
)
(analyze_product_quality, analyze_all_quality) = _safe_import(
    "x6010_product_quality_analyzer", "analyze_product_quality", "analyze_all_quality"
)
(get_product_availability, get_all_availability, get_provincial_restrictions) = _safe_import(
    "x6011_market_availability_engine", "get_product_availability", "get_all_availability", "get_provincial_restrictions"
)

# x6012 + x7000 ont des fichiers présents → import direct
try:
    from .x6012_regulatory_compliance_engine import (  # noqa: E402
        compute_compliance_score, compute_all_compliance, get_compliance_by_organism
    )
except ImportError as e:
    _logger.warning(f"[NUTRITION-INTELLIGENCE] x6012 import failed: {e}")
    compute_compliance_score = compute_all_compliance = get_compliance_by_organism = None

(get_solutions_for_deficits, get_all_terrain_solutions) = _safe_import(
    "x6020_terrain_solutions", "get_solutions_for_deficits", "get_all_terrain_solutions"
)
(get_product_ecosystem, get_all_ecosystems, get_product_tracability) = _safe_import(
    "x6030_product_ecosystem", "get_product_ecosystem", "get_all_ecosystems", "get_product_tracability"
)

try:
    from .x7000_supplier_product_engine import (  # noqa: E402
        submit_product, review_submission, activate_product,
        get_submission, get_all_submissions, get_pipeline_stats,
    )
except ImportError as e:
    _logger.warning(f"[NUTRITION-INTELLIGENCE] x7000 import failed: {e}")
    submit_product = review_submission = activate_product = None
    get_submission = get_all_submissions = get_pipeline_stats = None
