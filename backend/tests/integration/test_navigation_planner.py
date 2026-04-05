"""
Test Integration -- Navigation Planner M4-B (T8)
=====================================================
Directive x7100-M4 -- BCE-4X GOLDEN V6+
Couvre: plan-route, get session, optimize, advice, start/end session,
        session status, non-regression M1/M2/M3
"""

import pytest
import httpx
import os
import uuid
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

API_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not API_URL:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                API_URL = line.strip().split("=", 1)[1].rstrip("/")
                break

BASE = f"{API_URL}/api/v1/nav-intel"
M2_BASE = f"{API_URL}/api/v1/poi-graph"
M3_BASE = f"{API_URL}/api/v1/predict-layer"
TEST_USER = "integration_test_m4_nav"
TEST_ZONE = "zone-m4-nav-test"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def setup_and_cleanup(client):
    """Setup test data (POIs in zone) and cleanup after."""
    # Create test POIs in zone via M2
    poi_ids = []
    poi_data_list = [
        {"user_id": TEST_USER, "type": "stand", "name": "NavTest Stand Alpha", "lat": 47.500, "lng": -72.000, "zone_id": TEST_ZONE,
         "properties": {"species_observed": ["orignal"], "frequency": 10, "confidence": 0.7}},
        {"user_id": TEST_USER, "type": "camera", "name": "NavTest Camera Beta", "lat": 47.502, "lng": -71.998, "zone_id": TEST_ZONE,
         "properties": {"species_observed": ["orignal", "chevreuil"], "frequency": 20, "confidence": 0.8}},
        {"user_id": TEST_USER, "type": "point_eau", "name": "NavTest Eau Gamma", "lat": 47.503, "lng": -72.002, "zone_id": TEST_ZONE,
         "properties": {"species_observed": ["orignal"], "frequency": 15, "confidence": 0.6}},
    ]
    for poi_data in poi_data_list:
        r = client.post(f"{M2_BASE}/nodes", json=poi_data)
        if r.status_code == 200 and r.json().get("success"):
            poi_ids.append(r.json()["node"]["poi_id"])

    # Also create profile
    client.get(f"{BASE}/profile/{TEST_USER}")

    yield poi_ids

    # Cleanup
    try:
        from pymongo import MongoClient
        mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.environ.get("DB_NAME", "huntiq_v3")
        mc = MongoClient(mongo_url)
        db = mc[db_name]
        db.hunter_profiles.delete_many({"user_id": {"$regex": "^integration_test_m4"}})
        db.navigation_sessions.delete_many({"user_id": {"$regex": "^integration_test_m4"}})
        for pid in poi_ids:
            db.poi_nodes.delete_one({"poi_id": pid})
        mc.close()
    except Exception:
        pass


# ==============================================
# T8-01: Plan route with POIs
# ==============================================
def test_m4_plan_route(client, setup_and_cleanup):
    r = client.post(f"{BASE}/plan-route", json={
        "user_id": TEST_USER,
        "target_species": "orignal",
        "zone_id": TEST_ZONE,
        "start_lat": 47.5,
        "start_lng": -72.0
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    session = data["session"]
    assert session["status"] == "planned"
    assert session["user_id"] == TEST_USER
    assert session["target_species"] == "orignal"
    assert session["zone_id"] == TEST_ZONE
    assert "session_id" in session
    assert "waypoints" in session
    assert isinstance(session["waypoints"], list)
    assert session["waypoints_count"] == len(session["waypoints"])
    assert "route_summary" in session
    assert "total_distance_m" in session["route_summary"]
    # POIs should be found in the zone
    assert session["waypoints_count"] >= 1


# ==============================================
# T8-02: Plan route missing fields
# ==============================================
def test_m4_plan_route_missing_fields(client):
    r = client.post(f"{BASE}/plan-route", json={"user_id": TEST_USER})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False
    assert data["error"] == "MISSING_FIELDS"
    assert "target_species" in data["fields"]


# ==============================================
# T8-03: Get session
# ==============================================
def test_m4_get_session(client):
    # Create a session first
    r1 = client.post(f"{BASE}/plan-route", json={
        "user_id": TEST_USER, "target_species": "orignal", "zone_id": TEST_ZONE
    })
    sid = r1.json()["session"]["session_id"]

    r = client.get(f"{BASE}/plan-route/{sid}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["session"]["session_id"] == sid
    assert data["session"]["status"] == "planned"


# ==============================================
# T8-04: Get non-existent session
# ==============================================
def test_m4_get_session_not_found(client):
    r = client.get(f"{BASE}/plan-route/{uuid.uuid4()}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False
    assert data["error"] == "SESSION_NOT_FOUND"


# ==============================================
# T8-05: Optimize route
# ==============================================
def test_m4_optimize(client):
    r1 = client.post(f"{BASE}/plan-route", json={
        "user_id": TEST_USER, "target_species": "orignal", "zone_id": TEST_ZONE
    })
    sid = r1.json()["session"]["session_id"]

    r = client.post(f"{BASE}/optimize", json={"session_id": sid})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["session"]["session_id"] == sid


# ==============================================
# T8-06: Optimize non-existent session
# ==============================================
def test_m4_optimize_not_found(client):
    r = client.post(f"{BASE}/optimize", json={"session_id": str(uuid.uuid4())})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False


# ==============================================
# T8-07: Optimize missing session_id
# ==============================================
def test_m4_optimize_missing_id(client):
    r = client.post(f"{BASE}/optimize", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False
    assert data["error"] == "MISSING_FIELDS"


# ==============================================
# T8-08: Contextual advice
# ==============================================
def test_m4_advice(client):
    r = client.get(f"{BASE}/advice/{TEST_USER}/47.5/-72.0")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "position" in data
    assert data["position"]["lat"] == 47.5
    assert data["position"]["lng"] == -72.0
    assert "species" in data
    assert "prediction" in data
    assert "solunar" in data
    assert "advice" in data
    assert isinstance(data["advice"], list)
    assert "nearby_pois" in data
    assert isinstance(data["nearby_pois"], list)


# ==============================================
# T8-09: Full session lifecycle (plan → start → end)
# ==============================================
def test_m4_session_lifecycle(client):
    # Plan
    r1 = client.post(f"{BASE}/plan-route", json={
        "user_id": TEST_USER, "target_species": "chevreuil", "zone_id": TEST_ZONE
    })
    assert r1.json()["success"] is True
    sid = r1.json()["session"]["session_id"]
    assert r1.json()["session"]["status"] == "planned"

    # Start
    r2 = client.post(f"{BASE}/session/start", json={"session_id": sid})
    assert r2.json()["success"] is True
    assert r2.json()["session"]["status"] == "active"

    # Status
    r3 = client.get(f"{BASE}/session/{sid}/status")
    assert r3.json()["success"] is True
    assert r3.json()["status"] == "active"

    # End
    r4 = client.post(f"{BASE}/session/{sid}/end", json={
        "metrics": {"distance_walked_km": 4.2, "duration_hours": 3.0, "pois_visited": 2}
    })
    assert r4.json()["success"] is True
    assert r4.json()["session"]["status"] == "completed"
    assert r4.json()["session"]["metrics"]["distance_walked_km"] == 4.2


# ==============================================
# T8-10: Start non-planned session (should fail)
# ==============================================
def test_m4_start_completed_session(client):
    # Create and complete a session
    r1 = client.post(f"{BASE}/plan-route", json={
        "user_id": TEST_USER, "target_species": "orignal", "zone_id": TEST_ZONE
    })
    sid = r1.json()["session"]["session_id"]
    client.post(f"{BASE}/session/start", json={"session_id": sid})
    client.post(f"{BASE}/session/{sid}/end", json={"metrics": {}})

    # Try to start again
    r = client.post(f"{BASE}/session/start", json={"session_id": sid})
    assert r.json()["success"] is False


# ==============================================
# T8-11: End non-active session (should fail)
# ==============================================
def test_m4_end_planned_session(client):
    r1 = client.post(f"{BASE}/plan-route", json={
        "user_id": TEST_USER, "target_species": "orignal", "zone_id": TEST_ZONE
    })
    sid = r1.json()["session"]["session_id"]

    r = client.post(f"{BASE}/session/{sid}/end", json={})
    assert r.json()["success"] is False


# ==============================================
# T8-12: Session start missing session_id
# ==============================================
def test_m4_start_missing_id(client):
    r = client.post(f"{BASE}/session/start", json={})
    assert r.json()["success"] is False
    assert r.json()["error"] == "MISSING_FIELDS"


# ==============================================
# T8-13: Session status not found
# ==============================================
def test_m4_status_not_found(client):
    r = client.get(f"{BASE}/session/{uuid.uuid4()}/status")
    assert r.json()["success"] is False


# ==============================================
# NON-REGRESSION: M1, M2, M3 health checks
# ==============================================
def test_nonregression_m1_health(client):
    r = client.get(f"{API_URL}/api/v1/map-intel/health")
    assert r.status_code == 200
    assert r.json()["status"] == "operational"


def test_nonregression_m2_health(client):
    r = client.get(f"{M2_BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "operational"
    assert r.json()["engine"] == "poi_graph_engine"


def test_nonregression_m3_health(client):
    r = client.get(f"{M3_BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "operational"
    assert r.json()["engine"] == "predictive_layer_engine"


def test_nonregression_m4_health(client):
    r = client.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "operational"
    assert r.json()["endpoints"] == 12


# ==============================================
# NON-REGRESSION: M2 POI CRUD still works
# ==============================================
def test_nonregression_m2_crud(client):
    # Create
    r = client.post(f"{M2_BASE}/nodes", json={
        "user_id": "nonreg_m4_test", "type": "stand",
        "name": "NonReg M4 Stand", "lat": 46.0, "lng": -71.0,
        "zone_id": "nonreg-zone"
    })
    assert r.status_code == 200
    assert r.json()["success"] is True
    poi_id = r.json()["node"]["poi_id"]

    # Get
    r2 = client.get(f"{M2_BASE}/nodes/{poi_id}")
    assert r2.json()["success"] is True

    # Delete
    r3 = client.delete(f"{M2_BASE}/nodes/{poi_id}")
    assert r3.json()["success"] is True


# ==============================================
# NON-REGRESSION: M3 zone query still works
# ==============================================
def test_nonregression_m3_zone_query(client):
    r = client.get(f"{M3_BASE}/zone/zone-test/species/orignal")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["species"] == "orignal"
