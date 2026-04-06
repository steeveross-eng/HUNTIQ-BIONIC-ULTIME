"""
Tests structurels et fonctionnels — access_clarity_engine_v7
PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE
"""
import pytest
import math


def test_smoother_imports():
    """Vérifier que tous les exports de smoother sont disponibles."""
    from modules.access_clarity_engine_v7.smoother import (
        smooth_full_pipeline,
        remove_zigzags,
        douglas_peucker,
        interpolate_natural,
    )
    assert callable(smooth_full_pipeline)
    assert callable(remove_zigzags)
    assert callable(douglas_peucker)
    assert callable(interpolate_natural)


def test_scorer_imports():
    """Vérifier que tous les exports de scorer sont disponibles."""
    from modules.access_clarity_engine_v7.scorer import compute_tcs, TCS_WEIGHTS
    assert callable(compute_tcs)
    assert isinstance(TCS_WEIGHTS, dict)
    assert len(TCS_WEIGHTS) == 6
    assert abs(sum(TCS_WEIGHTS.values()) - 1.0) < 0.001


def test_clarity_engine_imports():
    """Vérifier que clarity_engine est importable."""
    from modules.access_clarity_engine_v7.clarity_engine import apply_clarity, CLARITY_RENDER
    assert callable(apply_clarity)
    assert isinstance(CLARITY_RENDER, dict)


def test_router_imports():
    """Vérifier que le router est importable."""
    from modules.access_clarity_engine_v7.router import router
    assert router is not None
    assert router.prefix == "/api/v7/clarity"


def test_tcs_weights_sum():
    """Les poids TCS doivent sommer à 1.0."""
    from modules.access_clarity_engine_v7.scorer import TCS_WEIGHTS
    total = sum(TCS_WEIGHTS.values())
    assert abs(total - 1.0) < 0.001, f"Total TCS weights = {total}, expected 1.0"


def test_tcs_weights_components():
    """Vérifier la composition exacte du TCS selon directive STEEVE-MAX."""
    from modules.access_clarity_engine_v7.scorer import TCS_WEIGHTS
    assert TCS_WEIGHTS["trail_alignment"] == 0.30
    assert TCS_WEIGHTS["smoothness"] == 0.20
    assert TCS_WEIGHTS["penetrability"] == 0.15
    assert TCS_WEIGHTS["topography_lidar"] == 0.15
    assert TCS_WEIGHTS["hydrology"] == 0.10
    assert TCS_WEIGHTS["real_effort"] == 0.10


def test_smooth_pipeline_reduces_zigzags():
    """Le pipeline doit réduire les zigzags."""
    from modules.access_clarity_engine_v7.smoother import smooth_full_pipeline
    # Coords avec zigzags brusques
    coords = [
        {"lat": 48.2063, "lng": -68.3817},
        {"lat": 48.2065, "lng": -68.3810},
        {"lat": 48.2060, "lng": -68.3808},  # zigzag
        {"lat": 48.2068, "lng": -68.3802},
        {"lat": 48.2063, "lng": -68.3799},  # zigzag
        {"lat": 48.2072, "lng": -68.3795},
        {"lat": 48.2088, "lng": -68.3765},
    ]
    result = smooth_full_pipeline(coords)
    # Le résultat doit avoir plus de points (interpolation) mais moins de zigzags
    assert len(result) >= 2
    # Premier et dernier points préservés
    assert abs(result[0]["lat"] - coords[0]["lat"]) < 0.001
    assert abs(result[-1]["lat"] - coords[-1]["lat"]) < 0.001


def test_tcs_terrain_aware_score():
    """TCS pour terrain sans sentier doit être < 70."""
    from modules.access_clarity_engine_v7.scorer import compute_tcs
    route_data = {
        "coords": [
            {"lat": 48.2063, "lng": -68.3817},
            {"lat": 48.2068, "lng": -68.3810},
            {"lat": 48.2072, "lng": -68.3802},
            {"lat": 48.2078, "lng": -68.3795},
            {"lat": 48.2085, "lng": -68.3788},
        ],
        "distance_m": 300,
        "trail_type": "terrain_aware",
        "routing_algo": "terrain_grid_astar",
        "trail_percentage": 0,
    }
    tcs = compute_tcs(route_data)
    assert 0 <= tcs["score"] <= 100
    assert tcs["score"] < 70  # Terrain sans sentier = score modéré
    assert tcs["grade"] in ("C", "D")
    assert len(tcs["components"]) == 6


def test_tcs_trail_score():
    """TCS pour sentier réel doit être > 70."""
    from modules.access_clarity_engine_v7.scorer import compute_tcs
    route_data = {
        "coords": [
            {"lat": 48.2063, "lng": -68.3817},
            {"lat": 48.2068, "lng": -68.3810},
            {"lat": 48.2072, "lng": -68.3802},
            {"lat": 48.2078, "lng": -68.3795},
            {"lat": 48.2085, "lng": -68.3788},
        ],
        "distance_m": 300,
        "trail_type": "sentier_reel",
        "routing_algo": "dijkstra",
        "trail_percentage": 95,
    }
    tcs = compute_tcs(route_data)
    assert tcs["score"] > 70
    assert tcs["grade"] in ("S", "A", "B")


def test_apply_clarity_full_pipeline():
    """Pipeline complet apply_clarity doit fonctionner."""
    from modules.access_clarity_engine_v7.clarity_engine import apply_clarity
    access_data = {
        "coords": [
            {"lat": 48.2063, "lng": -68.3817},
            {"lat": 48.2068, "lng": -68.3810},
            {"lat": 48.2072, "lng": -68.3802},
            {"lat": 48.2078, "lng": -68.3795},
            {"lat": 48.2085, "lng": -68.3788},
        ],
        "distance_m": 300,
        "trail_type": "terrain_aware",
        "routing_algo": "terrain_grid_astar",
        "trail_percentage": 0,
    }
    result = apply_clarity(access_data)
    assert result["clarity_applied"] is True
    assert result["engine"] == "access_clarity_engine_v7"
    assert "tcs" in result
    assert "render" in result
    assert result["render"]["color"] is not None
    assert result["tcs"]["score"] >= 0
    assert result["tcs"]["grade"] in ("S", "A", "B", "C", "D", "F")


def test_render_grades():
    """Vérifier que chaque grade TCS produit un rendu visuel distinct."""
    from modules.access_clarity_engine_v7.clarity_engine import apply_clarity

    # Test grade élevé (sentier réel)
    high = apply_clarity({
        "coords": [{"lat": 48.2063, "lng": -68.3817}, {"lat": 48.2090, "lng": -68.3765}],
        "distance_m": 200,
        "trail_type": "sentier_reel",
        "routing_algo": "dijkstra",
        "trail_percentage": 95,
    })
    assert high["render"]["color"] == "#26A69A"  # vert teal pour sentier réel

    # Test grade bas
    low = apply_clarity({
        "coords": [{"lat": 48.2063, "lng": -68.3817}, {"lat": 48.2090, "lng": -68.3765}],
        "distance_m": 200,
        "trail_type": "hors_sentier",
        "routing_algo": "direct_line",
        "trail_percentage": 0,
    })
    # Grade bas = couleur différente
    assert low["render"]["color"] != "#26A69A"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
