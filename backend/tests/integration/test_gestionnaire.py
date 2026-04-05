"""
Test Integration -- Gestionnaire Engine Phase C (T9)
=====================================================
Directive x7100-M4 Phase C | BCE-4X GOLDEN V6+
Couvre: health, position LIVE, sectors, emergency, consent, non-regression
"""

import pytest
import httpx
import os
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

API_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not API_URL:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                API_URL = line.strip().split("=", 1)[1].rstrip("/")
                break

BASE = f"{API_URL}/api/v1/gestionnaire"
M4_BASE = f"{API_URL}/api/v1/nav-intel"
TEST_USER = "integration_test_gestionnaire"
TEST_TERRITORY = "zec-test-gestionnaire"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def cleanup(client):
    yield
    try:
        from pymongo import MongoClient
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        mc = MongoClient(mongo_url)
        db = mc[db_name]
        db.live_positions.delete_many({"user_id": {"$regex": "^integration_test_"}})
        db.position_history.delete_many({"user_id": {"$regex": "^integration_test_"}})
        db.sectors.delete_many({"territory_id": TEST_TERRITORY})
        db.emergency_alerts.delete_many({"territory_id": TEST_TERRITORY})
        db.gps_consents.delete_many({"user_id": {"$regex": "^integration_test_"}})
        mc.close()
    except Exception:
        pass


# ==============================================
# T9-01: Health
# ==============================================
def test_gestionnaire_health(client):
    r = client.get(f"{BASE}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "operational"
    assert data["engine"] == "gestionnaire_engine"
    assert data["endpoints"] == 12
    assert "PositionLive" in data["services"]
    assert "EmergencySecours" in data["services"]


# ==============================================
# T9-02: Consent registration
# ==============================================
def test_consent_permanent(client):
    r = client.post(f"{BASE}/consent", json={
        "user_id": TEST_USER, "consent": "permanent", "territory_id": TEST_TERRITORY
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["consent"] == "permanent"
    assert len(data["advantages"]) == 6


def test_consent_none(client):
    r = client.post(f"{BASE}/consent", json={
        "user_id": f"{TEST_USER}_noconsent", "consent": "none"
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["advantages"] == []


# ==============================================
# T9-03: Position LIVE
# ==============================================
def test_position_live(client):
    r = client.post(f"{BASE}/position", json={
        "user_id": TEST_USER, "lat": 47.5, "lng": -72.0,
        "accuracy": 5, "speed": 1.2, "consent": "permanent",
        "territory_id": TEST_TERRITORY
    })
    assert r.status_code == 200
    assert r.json()["success"] is True


def test_position_missing_user(client):
    r = client.post(f"{BASE}/position", json={"lat": 47.5, "lng": -72.0})
    assert r.status_code == 200
    assert r.json()["success"] is False


def test_get_territory_positions(client):
    r = client.get(f"{BASE}/positions/{TEST_TERRITORY}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["count"] >= 1
    assert data["positions"][0]["user_id"] == TEST_USER


# ==============================================
# T9-04: Sectors
# ==============================================
def test_sectors_empty(client):
    r = client.get(f"{BASE}/sectors/{TEST_TERRITORY}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert isinstance(data["sectors"], list)


def test_sector_status_not_found(client):
    r = client.post(f"{BASE}/sectors/nonexistent/status", json={"status": "libre"})
    assert r.status_code == 200
    assert r.json()["success"] is False


# ==============================================
# T9-05: Emergency SECOURS
# ==============================================
def test_emergency_trigger(client):
    r = client.post(f"{BASE}/emergency", json={
        "user_id": TEST_USER, "user_name": "TestHunter",
        "position": {"lat": 47.5, "lng": -72.0, "accuracy": 5},
        "message": "Test urgence", "territory_id": TEST_TERRITORY
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["alert"]["status"] == "active"
    assert data["alert"]["type"] == "secours"


def test_emergency_active(client):
    r = client.get(f"{BASE}/emergency/active/{TEST_TERRITORY}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["count"] >= 1


def test_emergency_acknowledge(client):
    # Create an alert first
    r1 = client.post(f"{BASE}/emergency", json={
        "user_id": f"{TEST_USER}_ack", "user_name": "AckTest",
        "position": {"lat": 47.5, "lng": -72.0, "accuracy": 5},
        "message": "Ack test", "territory_id": TEST_TERRITORY
    })
    alert_id = r1.json()["alert"]["alert_id"]

    r = client.post(f"{BASE}/emergency/{alert_id}/ack", json={
        "user_id": "responder_01", "name": "Gestionnaire Jean"
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert len(data["alert"]["responders"]) >= 1


def test_emergency_resolve(client):
    r1 = client.post(f"{BASE}/emergency", json={
        "user_id": f"{TEST_USER}_resolve", "user_name": "ResolveTest",
        "position": {"lat": 47.5, "lng": -72.0, "accuracy": 5},
        "message": "Resolve test", "territory_id": TEST_TERRITORY
    })
    alert_id = r1.json()["alert"]["alert_id"]

    r = client.post(f"{BASE}/emergency/{alert_id}/resolve", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["alert"]["status"] == "resolved"


# ==============================================
# NON-REGRESSION M4, M3, M2
# ==============================================
def test_nonreg_m4_health(client):
    r = client.get(f"{M4_BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "operational"


def test_nonreg_gestionnaire_m4_coexist(client):
    """M4 et Gestionnaire coexistent sans conflit."""
    r1 = client.get(f"{M4_BASE}/health")
    r2 = client.get(f"{BASE}/health")
    assert r1.json()["engine"] == "adaptive_navigation_engine"
    assert r2.json()["engine"] == "gestionnaire_engine"
