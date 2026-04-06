"""
test_access_structural.py — Tests structurels access_engine_v6
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX

Valide la logique de couts, pentes, obstacles et classification.
"""
import math
import pytest

from modules.access_engine_v6.access_cost_grid import compute_cell_cost, BASE_COSTS
from modules.access_engine_v6.segment_classifier import classify_path_segments, SEGMENT_TYPES
from modules.access_engine_v6.pathfinder_v6 import astar_grid, dijkstra_trail_graph, find_nearest_trail_node
from modules.access_engine_v6.vegetation_analyzer import analyze_vegetation_corridor


class TestTrailPriority:
    """Verifier que le cout sentier < cout hors-sentier."""

    def test_trail_cost_lower_than_offtrail(self):
        trail_cost = compute_cell_cost(
            is_trail=True, highway_type="path", slope_deg=3,
            canopy_density=0.4, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        offtrail_cost = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=3,
            canopy_density=0.4, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        assert trail_cost < offtrail_cost, f"Trail cost ({trail_cost}) must be < off-trail cost ({offtrail_cost})"

    def test_trail_bonus_factor(self):
        """Le bonus sentier GOLDEN x0.1 doit diviser le cout par 10."""
        trail_cost = compute_cell_cost(
            is_trail=True, highway_type="path", slope_deg=0,
            canopy_density=0.5, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=1000, dist_road_m=500,
        )
        # BASE=1.0 * MULT_PENTE=1.0 * MULT_VEG=1.0 * MULT_OBS=1.0 * GOLDEN=0.1
        assert trail_cost == pytest.approx(0.1, rel=0.01)


class TestSlopePenalty:
    """Verifier que pente >25 deg = cout infini."""

    def test_slope_over_25_is_infinite(self):
        cost = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=30,
            canopy_density=0.3, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        assert cost == float("inf"), "Slope >25 deg must be impassable (inf)"

    def test_slope_exactly_25_is_passable(self):
        cost = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=25,
            canopy_density=0.3, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        assert cost < float("inf"), "Slope =25 deg must be passable"

    def test_steep_slope_higher_cost(self):
        flat_cost = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=3,
            canopy_density=0.5, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        steep_cost = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=20,
            canopy_density=0.5, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        assert steep_cost > flat_cost, f"Steep ({steep_cost}) must be > flat ({flat_cost})"


class TestWaterBlocking:
    """Verifier que is_water = True bloque le passage."""

    def test_water_is_impassable(self):
        cost = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=3,
            canopy_density=0.3, understory_density=0.2, regeneration=0.1,
            is_water=True, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        assert cost == float("inf"), "Water must be impassable (inf)"

    def test_wetland_very_high_cost(self):
        cost_normal = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=3,
            canopy_density=0.3, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        cost_wetland = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=3,
            canopy_density=0.3, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=True, dist_building_m=500, dist_road_m=200,
        )
        assert cost_wetland > cost_normal * 3, "Wetland must have significantly higher cost"


class TestVegetationScoring:
    """Verifier que foret dense > cout foret ouverte."""

    def test_dense_forest_higher_cost(self):
        open_cost = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=3,
            canopy_density=0.2, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        dense_cost = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=3,
            canopy_density=0.9, understory_density=0.2, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        assert dense_cost > open_cost, f"Dense ({dense_cost}) must be > open ({open_cost})"

    def test_understory_penalty(self):
        no_understory = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=3,
            canopy_density=0.5, understory_density=0.3, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        with_understory = compute_cell_cost(
            is_trail=False, highway_type="", slope_deg=3,
            canopy_density=0.5, understory_density=0.8, regeneration=0.1,
            is_water=False, is_wetland=False, dist_building_m=500, dist_road_m=200,
        )
        assert with_understory > no_understory, "Dense understory must increase cost"


class TestSegmentClassification:
    """Verifier la classification couleur des segments."""

    def test_segment_types_defined(self):
        assert "trail" in SEGMENT_TYPES
        assert "hybrid" in SEGMENT_TYPES
        assert "off_trail_optimized" in SEGMENT_TYPES
        assert "non_conformant" in SEGMENT_TYPES

    def test_trail_is_green(self):
        assert SEGMENT_TYPES["trail"]["color"] == "#2ECC71"

    def test_hybrid_is_blue(self):
        assert SEGMENT_TYPES["hybrid"]["color"] == "#3498DB"

    def test_off_trail_is_gold(self):
        assert SEGMENT_TYPES["off_trail_optimized"]["color"] == "#F1C40F"

    def test_non_conformant_is_red(self):
        assert SEGMENT_TYPES["non_conformant"]["color"] == "#E74C3C"


class TestAstarGrid:
    """Verifier le fonctionnement de A* sur grille."""

    def _build_simple_grid(self, size=10):
        grid = {}
        for y in range(size):
            for x in range(size):
                grid[(x, y)] = {
                    "cost": 1.0,
                    "is_trail": False,
                    "highway_type": "",
                    "slope_deg": 0,
                    "canopy": 0.3,
                    "is_water": False,
                }
        return grid

    def test_finds_path_simple_grid(self):
        grid = self._build_simple_grid(10)
        path = astar_grid(grid, (0, 0), (9, 9), 10)
        assert len(path) > 0, "A* must find a path on open grid"
        assert path[0] == (0, 0)
        assert path[-1] == (9, 9)

    def test_no_path_with_wall(self):
        grid = self._build_simple_grid(5)
        for y in range(5):
            del grid[(2, y)]
        path = astar_grid(grid, (0, 0), (4, 4), 5)
        assert len(path) == 0, "No path when wall blocks"


class TestDijkstraTrailGraph:
    """Verifier le Dijkstra sur graphe sentier."""

    def test_simple_trail_path(self):
        nodes = {"1": {"lat": 0, "lng": 0}, "2": {"lat": 0, "lng": 1}, "3": {"lat": 0, "lng": 2}}
        edges = [
            {"from": "1", "to": "2", "distance_m": 100, "cost_mult": 1.0},
            {"from": "2", "to": "3", "distance_m": 100, "cost_mult": 1.0},
        ]
        path = dijkstra_trail_graph(nodes, edges, "1", "3")
        assert path == ["1", "2", "3"]

    def test_no_path_disconnected(self):
        nodes = {"1": {"lat": 0, "lng": 0}, "2": {"lat": 0, "lng": 1}, "3": {"lat": 10, "lng": 10}}
        edges = [
            {"from": "1", "to": "2", "distance_m": 100, "cost_mult": 1.0},
        ]
        path = dijkstra_trail_graph(nodes, edges, "1", "3")
        assert path == []


class TestNearestTrailNode:
    """Verifier la recherche du noeud sentier le plus proche."""

    def test_finds_nearest(self):
        nodes = {
            "1": {"lat": 48.0, "lng": -68.0},
            "2": {"lat": 48.001, "lng": -68.001},
            "3": {"lat": 48.01, "lng": -68.01},
        }
        nearest = find_nearest_trail_node(48.0005, -68.0005, nodes)
        assert nearest in ("1", "2"), f"Should find close node, got {nearest}"


class TestVegetationAnalyzer:
    """Verifier l'analyse vegetation."""

    def test_default_analysis_empty(self):
        result = analyze_vegetation_corridor([], {}, 10, 10, 48.0, -68.0)
        assert result["total_cells_analyzed"] == 0
        assert result["strategy"] == "Donnees insuffisantes — analyse par defaut"
