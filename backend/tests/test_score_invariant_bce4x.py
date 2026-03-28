"""
BCE-4X-MAX — Tests unitaires INVARIANT SCORE=0ELEMENT
Phase 3.3-U-PRIME — Consolidation structurelle
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from core.scoring_pipeline.score_consolide import compute_consolidated_score


class TestScoreConsolideMetaExclusion:
    """Verifier que score-consolide retourne 0 + EXCLU en zone urbaine."""

    def test_urban_centre_ville_returns_exclu(self):
        result = compute_consolidated_score(46.8139, -71.208, "CERF", 3)
        assert result["meta_excluded"] is True
        assert result["score"] == 0.0
        assert result["classe"] == "EXCLU"
        assert result["label"] == "Zone urbaine"

    def test_urban_beauport_returns_exclu(self):
        result = compute_consolidated_score(46.84, -71.19, "CERF", 3)
        assert result["meta_excluded"] is True
        assert result["score"] == 0.0
        assert result["classe"] == "EXCLU"

    def test_forest_returns_normal_score(self):
        result = compute_consolidated_score(47.25, -71.40, "CERF", 3)
        assert result.get("meta_excluded") is not True
        assert result["score"] > 0
        assert result["classe"] != "EXCLU"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
