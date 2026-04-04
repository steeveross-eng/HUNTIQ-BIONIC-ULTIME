"""
Test Integration — POI Graph Spatial M2-B (Phase M2)
=======================================================
Directive x6900-M2 — BCE-4X GOLDEN V6+
Couvre: near, edges, create_edge, cluster, score, non-regression M1
"""

import pytest
import httpx
import os

API_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not API_URL:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                API_URL = line.strip().split("=", 1)[1].rstrip("/")
                break

BASE = f"{API_URL}/api/v1/poi-graph"
M1_BASE = f"{API_URL}/api/v1/map-intel"
TEST_USER = "integration_test_m2_spatial"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


@pytest.fixture(scope="module")
def spatial_pois(client):
    """Cree un graphe de 4 POIs connectes."""
    pois = []
    configs = [
        {"type": "stand", "name": "Spatial Stand A", "lat": 48.5, "lng": -73.5,
         "properties": {"species_observed": ["orignal"], "frequency": 15, "confidence": 0.8}},
        {"type": "point_eau", "name": "Spatial Eau B", "lat": 48.503, "lng": -73.497,
         "properties": {"species_observed": ["chevreuil"], "frequency": 30, "confidence": 0.9}},
        {"type": "camera", "name": "Spatial Cam C", "lat": 48.498, "lng": -73.504,
         "properties": {"species_observed": ["orignal", "ours_noir"], "frequency": 50, "confidence": 0.75}},
        {"type": "ravage", "name": "Spatial Ravage D", "lat": 48.505, "lng": -73.501,
         "properties": {"species_observed": ["orignal", "chevreuil"], "frequency": 8, "confidence": 0.6}},
    ]
    for cfg in configs:
        r = client.post(f"{BASE}/nodes", json={
            "user_id": TEST_USER, "zone_id": "zone-spatial-01", **cfg
        })
        assert r.status_code == 200
        pois.append(r.json()["node"])

    # Creer des aretes
    edges_cfg = [
        (0, 1, "proximity", 350),
        (0, 2, "line_of_sight", 420),
        (1, 2, "trail", 550),
        (0, 3, "corridor", 600),
    ]
    edges = []
    for i, j, rel, dist in edges_cfg:
        r = client.post(f"{BASE}/edges", json={
            "from_poi": pois[i]["poi_id"],
            "to_poi": pois[j]["poi_id"],
            "relation_type": rel,
            "distance_m": dist
        })
        assert r.status_code == 200
        assert r.json()["success"] is True
        edges.append(r.json()["edge"])

    yield {"pois": pois, "edges": edges}

    # Cleanup
    for p in pois:
        client.delete(f"{BASE}/nodes/{p['poi_id']}")


class TestM2Near:
    """M2-6: POIs a proximite"""

    def test_near_returns_pois(self, client, spatial_pois):
        r = client.get(f"{BASE}/near/48.5/-73.5?radius_m=5000")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["count"] >= 4

    def test_near_sorted_by_distance(self, client, spatial_pois):
        r = client.get(f"{BASE}/near/48.5/-73.5?radius_m=5000")
        nodes = r.json()["nodes"]
        distances = [n["distance_m"] for n in nodes]
        assert distances == sorted(distances)

    def test_near_with_type_filter(self, client, spatial_pois):
        r = client.get(f"{BASE}/near/48.5/-73.5?radius_m=5000&type=camera")
        data = r.json()
        for n in data["nodes"]:
            assert n["type"] == "camera"

    def test_near_includes_bearing(self, client, spatial_pois):
        r = client.get(f"{BASE}/near/48.5/-73.5?radius_m=5000")
        nodes = r.json()["nodes"]
        for n in nodes:
            assert "bearing_deg" in n
            assert 0 <= n["bearing_deg"] < 360 or n["distance_m"] == 0


class TestM2Edges:
    """M2-7/8: Aretes du graphe"""

    def test_get_edges(self, client, spatial_pois):
        poi_id = spatial_pois["pois"][0]["poi_id"]
        r = client.get(f"{BASE}/edges/{poi_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 3  # stand A connecte a B, C, D

    def test_edge_has_relation_type(self, client, spatial_pois):
        poi_id = spatial_pois["pois"][0]["poi_id"]
        r = client.get(f"{BASE}/edges/{poi_id}")
        for e in r.json()["edges"]:
            assert e["relation_type"] in ["proximity", "corridor", "line_of_sight", "water_flow", "trail"]

    def test_create_edge_invalid_relation(self, client, spatial_pois):
        r = client.post(f"{BASE}/edges", json={
            "from_poi": spatial_pois["pois"][0]["poi_id"],
            "to_poi": spatial_pois["pois"][1]["poi_id"],
            "relation_type": "INVALID"
        })
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "INVALID_RELATION_TYPE"

    def test_create_edge_nonexistent_poi(self, client, spatial_pois):
        r = client.post(f"{BASE}/edges", json={
            "from_poi": "nonexistent-from",
            "to_poi": spatial_pois["pois"][0]["poi_id"],
            "relation_type": "proximity"
        })
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "POI_NOT_FOUND"

    def test_create_edge_missing_fields(self, client):
        r = client.post(f"{BASE}/edges", json={"from_poi": "a"})
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "MISSING_FIELDS"


class TestM2Cluster:
    """M2-9: Cluster de POIs"""

    def test_cluster_returns_all(self, client, spatial_pois):
        r = client.get(f"{BASE}/cluster/48.5/-73.5/5000")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["poi_count"] >= 4

    def test_cluster_type_breakdown(self, client, spatial_pois):
        r = client.get(f"{BASE}/cluster/48.5/-73.5/5000")
        types = r.json()["types"]
        assert "stand" in types
        assert "point_eau" in types
        assert "camera" in types
        assert "ravage" in types

    def test_cluster_density(self, client, spatial_pois):
        r = client.get(f"{BASE}/cluster/48.5/-73.5/5000")
        data = r.json()
        assert data["density_per_km2"] > 0

    def test_cluster_empty_area(self, client):
        r = client.get(f"{BASE}/cluster/0.0/0.0/100")
        data = r.json()
        assert data["poi_count"] == 0


class TestM2Score:
    """M2-10: Score detaille"""

    def test_score_detailed(self, client, spatial_pois):
        poi_id = spatial_pois["pois"][0]["poi_id"]
        r = client.get(f"{BASE}/score/{poi_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "score" in data
        assert "decomposition" in data

    def test_score_has_4_criteria(self, client, spatial_pois):
        poi_id = spatial_pois["pois"][0]["poi_id"]
        r = client.get(f"{BASE}/score/{poi_id}")
        decomp = r.json()["decomposition"]
        assert "accessibility" in decomp
        assert "activity" in decomp
        assert "strategic" in decomp
        assert "nutrition" in decomp

    def test_score_weights_sum_to_1(self, client, spatial_pois):
        poi_id = spatial_pois["pois"][0]["poi_id"]
        r = client.get(f"{BASE}/score/{poi_id}")
        weights = r.json()["weights"]
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01

    def test_score_nutrition_source(self, client, spatial_pois):
        poi_id = spatial_pois["pois"][0]["poi_id"]
        r = client.get(f"{BASE}/score/{poi_id}")
        data = r.json()
        assert data["nutrition_source"]["source"] == "nutrition_v6_interface"

    def test_score_nonexistent(self, client):
        r = client.get(f"{BASE}/score/nonexistent-poi")
        data = r.json()
        assert data["success"] is False


class TestM1NonRegression:
    """Non-regression M1 — ZERO modification modules existants"""

    def test_m1_health(self, client):
        r = client.get(f"{M1_BASE}/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "operational"
        assert data["engine"] == "national_data_harvester"

    def test_m1_boundaries(self, client):
        r = client.get(f"{M1_BASE}/boundaries")
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_m1_legal_check(self, client):
        r = client.get(f"{M1_BASE}/legal-check/46.85/-71.25/orignal")
        assert r.status_code == 200
        data = r.json()
        assert "legal" in data
        assert data["species"] == "orignal"

    def test_m1_boundaries_at_point(self, client):
        r = client.get(f"{M1_BASE}/boundaries/at/46.85/-71.25")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["province"] == "QC"
