"""
Score consolide BIONIC — Wrapper x4500-ULTRA
==============================================
x4500: Delegue vers core/scoring_pipeline/score_consolide.py (22 moteurs).
Option C: CORE 60%, Nouveaux 40%.
Score reference: 57.6.

Maintient la retrocompatibilite avec les imports existants:
  from modules.score_consolide import compute_consolidated_score, compute_heatmap_grid
"""
from core.scoring_pipeline.score_consolide import (
    compute_consolidated_score,
    compute_heatmap_grid,
    NORMALIZED_WEIGHTS,
    ACTIVE_WEIGHTS,
    _ENGINE_FUNCTIONS,
)
from core.scoring_pipeline.common.constants import ENGINE_WEIGHTS
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed_fn


def _seed(lat, lng, salt=""):
    """Retrocompatibilite pour engine_registry/adapters.py"""
    return _seed_fn(lat, lng, salt)


def _corridor_score_for_point(lat, lng, center_lat, center_lng, species, month, side_m=2000.0):
    """Retrocompatibilite pour engine_registry/adapters.py"""
    from core.scoring_pipeline.corridors_v10.engine import score_point_consolidated
    return score_point_consolidated(lat, lng, center_lat, center_lng, species, month)


def _alimentation_v2_score_for_point(lat, lng, center_lat, center_lng, species, month):
    """Retrocompatibilite pour engine_registry/adapters.py"""
    from core.scoring_pipeline.alimentation_v2.engine import score_point_consolidated
    return score_point_consolidated(lat, lng, center_lat, center_lng, species, month)
