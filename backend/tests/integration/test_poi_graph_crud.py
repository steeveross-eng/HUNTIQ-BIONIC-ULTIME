"""
Test Integration — POI Graph CRUD M2-A (Phase M2)
=====================================================
Directive x6900-M2 — BCE-4X GOLDEN V6+
Couvre: health, create_poi, get_poi, update_poi, delete_poi, list_pois, filters
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
TEST_USER = "integration_test_m2_crud"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


@pytest.fixture(scope="module")
def created_pois(client):
    """Cree 3 POIs de test et les nettoie apres."""
    pois = []

    # POI 1 - stand
    r1 = client.post(f"{BASE}/nodes", json={
        "user_id": TEST_USER, "type": "stand",
        "name": "Test Stand Alpha", "lat": 47.5, "lng": -72.0,
        "description": "Stand de test CRUD", "altitude_m": 250,
        "zone_id": "zone-test-01",
        "properties": {"species_observed": ["orignal"], "frequency": 10, "confidence": 0.7}
    })
    assert r1.status_code == 200
    pois.append(r1.json()["node"])

    # POI 2 - camera
    r2 = client.post(f"{BASE}/nodes", json={
        "user_id": TEST_USER, "type": "camera",
        "name": "Test Camera Beta", "lat": 47.502, "lng": -71.998,
        "zone_id": "zone-test-01",
        "properties": {"species_observed": ["chevreuil", "orignal"], "frequency": 30, "confidence": 0.9}
    })
    assert r2.status_code == 200
    pois.append(r2.json()["node"])

    # POI 3 - point_eau
    r3 = client.post(f"{BASE}/nodes", json={
        "user_id": TEST_USER, "type": "point_eau",
        "name": "Test Ruisseau Gamma", "lat": 47.498, "lng": -72.003,
        "zone_id": "zone-test-01",
        "properties": {"species_observed": ["chevreuil"], "frequency": 20, "confidence": 0.8}
    })
    assert r3.status_code == 200
    pois.append(r3.json()["node"])

    yield pois

    # Cleanup
    for p in pois:
        client.delete(f"{BASE}/nodes/{p['poi_id']}")


class TestM2Health:
    """M2-0: Health endpoint"""

    def test_health_operational(self, client):
        r = client.get(f"{BASE}/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "operational"
        assert data["engine"] == "poi_graph_engine"
        assert data["phase"] == "M2-MAP-INTELLIGENCE"
        assert data["directive"] == "x6900-M2"
        assert data["endpoints"] == 11
        assert data["fusion_points"] == 14

    def test_health_anti_doublon(self, client):
        r = client.get(f"{BASE}/health")
        data = r.json()
        anti = data["anti_doublon"]
        assert "waypoint_scoring_engine" in anti
        assert "scoring_engine" in anti
        assert "geo_engine" in anti
        assert "geospatial_engine" in anti
        assert "territory_engine" in anti


class TestM2CreateNode:
    """M2-2: Creation de POIs"""

    def test_create_valid_poi(self, client, created_pois):
        poi = created_pois[0]
        assert poi["type"] == "stand"
        assert poi["name"] == "Test Stand Alpha"
        assert poi["poi_id"]
        assert poi["user_id"] == TEST_USER
        assert poi["location"]["type"] == "Point"
        assert poi["location"]["coordinates"] == [-72.0, 47.5]

    def test_create_enriches_province(self, client, created_pois):
        """PF-M1 : province resolue via M1 boundary_resolver"""
        poi = created_pois[0]
        assert poi["province"] == "QC"

    def test_create_initializes_score(self, client, created_pois):
        poi = created_pois[0]
        assert "score" in poi
        assert poi["score"]["global"] == 0.0

    def test_create_initializes_nutrition(self, client, created_pois):
        poi = created_pois[0]
        assert "nutrition" in poi
        assert poi["nutrition"]["source"] == "nutrition_v6_interface"

    def test_create_invalid_type(self, client):
        r = client.post(f"{BASE}/nodes", json={
            "user_id": TEST_USER, "type": "INVALID_TYPE",
            "name": "Bad", "lat": 47.0, "lng": -72.0
        })
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "INVALID_POI_TYPE"

    def test_create_missing_fields(self, client):
        r = client.post(f"{BASE}/nodes", json={"user_id": TEST_USER})
        data = r.json()
        assert data["success"] is False
        assert "MISSING_FIELDS" in data["error"]


class TestM2GetNode:
    """M2-3: Recuperation detail POI"""

    def test_get_existing_poi(self, client, created_pois):
        poi_id = created_pois[0]["poi_id"]
        r = client.get(f"{BASE}/nodes/{poi_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["node"]["poi_id"] == poi_id
        assert data["node"]["name"] == "Test Stand Alpha"

    def test_get_nonexistent_poi(self, client):
        r = client.get(f"{BASE}/nodes/nonexistent-id-xyz")
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "POI_NOT_FOUND"


class TestM2UpdateNode:
    """M2-4: Mise a jour POI"""

    def test_patch_description(self, client, created_pois):
        poi_id = created_pois[0]["poi_id"]
        r = client.patch(f"{BASE}/nodes/{poi_id}", json={
            "description": "Description mise a jour via test"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "mise a jour" in data["node"]["description"]

    def test_patch_nonexistent(self, client):
        r = client.patch(f"{BASE}/nodes/nonexistent-id", json={"description": "x"})
        data = r.json()
        assert data["success"] is False


class TestM2ListNodes:
    """M2-1: Liste et filtres"""

    def test_list_all_user(self, client, created_pois):
        r = client.get(f"{BASE}/nodes?user_id={TEST_USER}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["count"] >= 3

    def test_filter_by_type(self, client, created_pois):
        r = client.get(f"{BASE}/nodes?type=camera&user_id={TEST_USER}")
        data = r.json()
        assert data["count"] >= 1
        for n in data["nodes"]:
            assert n["type"] == "camera"

    def test_filter_by_zone(self, client, created_pois):
        r = client.get(f"{BASE}/nodes?zone_id=zone-test-01&user_id={TEST_USER}")
        data = r.json()
        assert data["count"] >= 3

    def test_filter_by_species(self, client, created_pois):
        r = client.get(f"{BASE}/nodes?species=orignal&user_id={TEST_USER}")
        data = r.json()
        assert data["count"] >= 1

    def test_pagination(self, client, created_pois):
        r = client.get(f"{BASE}/nodes?user_id={TEST_USER}&limit=1&skip=0")
        data = r.json()
        assert data["count"] == 1
        assert data["limit"] == 1
        assert data["skip"] == 0


class TestM2DeleteNode:
    """M2-5: Suppression POI"""

    def test_delete_with_cleanup(self, client):
        # Creer un POI temporaire
        r = client.post(f"{BASE}/nodes", json={
            "user_id": "test-delete-m2", "type": "saline",
            "name": "Temp Delete Test", "lat": 48.0, "lng": -73.0
        })
        poi_id = r.json()["node"]["poi_id"]

        # Supprimer
        r2 = client.delete(f"{BASE}/nodes/{poi_id}")
        data = r2.json()
        assert data["success"] is True
        assert data["deleted"] is True

        # Verifier suppression
        r3 = client.get(f"{BASE}/nodes/{poi_id}")
        assert r3.json()["success"] is False
