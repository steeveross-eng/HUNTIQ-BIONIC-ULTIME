"""
Test Integration -- Adaptive User Profile M4-A (T7)
=====================================================
Directive x7100-M4 -- BCE-4X GOLDEN V6+
Couvre: health, create/get profile, update preferences, apprentissage, suggestions, affinity
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

BASE = f"{API_URL}/api/v1/nav-intel"
TEST_USER = "integration_test_m4_profile"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


# --- Cleanup ---
@pytest.fixture(scope="module", autouse=True)
def cleanup_after(client):
    """Cleanup test data after all tests."""
    yield
    # Delete test profile
    try:
        from pymongo import MongoClient
        mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.environ.get("DB_NAME", "huntiq_v3")
        mc = MongoClient(mongo_url)
        db = mc[db_name]
        db.hunter_profiles.delete_many({"user_id": {"$regex": "^integration_test_m4"}})
        db.navigation_sessions.delete_many({"user_id": {"$regex": "^integration_test_m4"}})
        mc.close()
    except Exception:
        pass


# ==============================================
# T7-01: Health
# ==============================================
def test_m4_health(client):
    r = client.get(f"{BASE}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "operational"
    assert data["engine"] == "adaptive_navigation_engine"
    assert data["version"] == "1.0.0"
    assert data["phase"] == "M4-MAP-INTELLIGENCE"
    assert data["directive"] == "x7100-M4"
    assert data["endpoints"] == 12
    assert data["fusion_points"] == 19
    assert len(data["services"]) == 4
    assert "UserProfileLearner" in data["services"]
    assert "NavigationPlanner" in data["services"]
    assert "RouteOptimizer" in data["services"]
    assert "ContextualAdvisor" in data["services"]


# ==============================================
# T7-02: Create profile (auto-create via GET)
# ==============================================
def test_m4_get_or_create_profile(client):
    r = client.get(f"{BASE}/profile/{TEST_USER}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    profile = data["profile"]
    assert profile["user_id"] == TEST_USER
    assert "profile_id" in profile
    assert profile["skill_level"] == "intermediaire"
    assert isinstance(profile["species_preferences"], list)
    assert isinstance(profile["zone_preferences"], list)
    assert isinstance(profile["time_preferences"], dict)
    assert isinstance(profile["meteo_preferences"], dict)
    assert isinstance(profile["equipment"], dict)
    assert isinstance(profile["history_stats"], dict)
    assert "created_at" in profile
    assert "updated_at" in profile
    # Verify affinity returned
    assert "species_affinity" in data


# ==============================================
# T7-03: Idempotent GET profile (same profile_id)
# ==============================================
def test_m4_idempotent_profile(client):
    r1 = client.get(f"{BASE}/profile/{TEST_USER}")
    r2 = client.get(f"{BASE}/profile/{TEST_USER}")
    assert r1.json()["profile"]["profile_id"] == r2.json()["profile"]["profile_id"]


# ==============================================
# T7-04: Update preferences (PATCH)
# ==============================================
def test_m4_update_preferences(client):
    r = client.patch(f"{BASE}/profile/{TEST_USER}", json={
        "equipment": {"has_gps": True, "has_radio": True, "mobility": "vtt"},
        "meteo_preferences": {"min_temp_c": -10, "max_temp_c": 20, "wind_tolerance_kmh": 30, "rain_tolerance": "moderate"}
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["profile"]["equipment"]["mobility"] == "vtt"
    assert data["profile"]["equipment"]["has_radio"] is True
    assert data["profile"]["meteo_preferences"]["min_temp_c"] == -10
    assert data["profile"]["meteo_preferences"]["rain_tolerance"] == "moderate"


# ==============================================
# T7-05: Update species preferences
# ==============================================
def test_m4_update_species_preferences(client):
    r = client.patch(f"{BASE}/profile/{TEST_USER}", json={
        "species_preferences": [
            {"species": "orignal", "frequency": 0.6, "success_rate": 0.2, "preferred_weapon": "arme_feu", "preferred_zones": ["zone-A"]},
            {"species": "chevreuil", "frequency": 0.3, "success_rate": 0.4, "preferred_weapon": "arc", "preferred_zones": ["zone-B"]}
        ]
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    prefs = data["profile"]["species_preferences"]
    assert len(prefs) == 2
    assert prefs[0]["species"] == "orignal"
    assert prefs[1]["species"] == "chevreuil"


# ==============================================
# T7-06: Disallowed fields are ignored
# ==============================================
def test_m4_patch_ignores_protected(client):
    r = client.patch(f"{BASE}/profile/{TEST_USER}", json={
        "skill_level": "expert",  # Should be ignored
        "history_stats": {"total_trips": 999},  # Should be ignored
        "user_id": "hacker"  # Should be ignored
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    # Protected fields unchanged
    assert data["profile"]["user_id"] == TEST_USER
    assert data["profile"]["skill_level"] == "intermediaire"  # Not changed to expert


# ==============================================
# T7-07: Learn from history (no trips)
# ==============================================
def test_m4_learn_no_trips(client):
    r = client.post(f"{BASE}/profile/{TEST_USER}/learn")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["trips_analyzed"] == 0
    assert data["learning_applied"] is False
    assert data["reason"] == "NO_TRIPS_FOUND"


# ==============================================
# T7-08: Learn from history (with mock trips)
# ==============================================
def test_m4_learn_with_trips(client):
    # Insert mock hunting trips
    from pymongo import MongoClient
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DB_NAME", "huntiq_v3")
    mc = MongoClient(mongo_url)
    db = mc[db_name]

    test_trips = [
        {"user_id": TEST_USER, "species": "orignal", "zone_id": "zone-A", "start_hour": 6, "duration_hours": 3, "distance_km": 5, "success": True},
        {"user_id": TEST_USER, "species": "orignal", "zone_id": "zone-A", "start_hour": 5, "duration_hours": 4, "distance_km": 7, "success": False},
        {"user_id": TEST_USER, "species": "chevreuil", "zone_id": "zone-B", "start_hour": 16, "duration_hours": 2, "distance_km": 3, "success": True},
        {"user_id": TEST_USER, "species": "orignal", "zone_id": "zone-A", "start_hour": 6, "duration_hours": 5, "distance_km": 8, "success": True},
        {"user_id": TEST_USER, "species": "chevreuil", "zone_id": "zone-C", "start_hour": 17, "duration_hours": 3, "distance_km": 4, "success": False},
        {"user_id": TEST_USER, "species": "orignal", "zone_id": "zone-A", "start_hour": 7, "duration_hours": 4, "distance_km": 6, "success": True},
    ]
    db.hunting_trips.insert_many(test_trips)
    mc.close()

    r = client.post(f"{BASE}/profile/{TEST_USER}/learn")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["trips_analyzed"] == 6
    assert data["learning_applied"] is True
    assert data["species_learned"] == 2
    assert data["zones_learned"] >= 2

    # Verify profile was updated
    r2 = client.get(f"{BASE}/profile/{TEST_USER}")
    profile = r2.json()["profile"]
    assert profile["skill_level"] in ["debutant", "intermediaire", "avance", "expert"]
    assert profile["history_stats"]["total_trips"] == 6
    assert len(profile["species_preferences"]) == 2

    # Cleanup
    mc2 = MongoClient(mongo_url)
    mc2[db_name].hunting_trips.delete_many({"user_id": TEST_USER})
    mc2.close()


# ==============================================
# T7-09: Suggestions
# ==============================================
def test_m4_suggestions(client):
    r = client.get(f"{BASE}/suggestions/{TEST_USER}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    assert data["count"] >= 0
    assert "profile_skill" in data


# ==============================================
# T7-10: Suggestions with rich profile
# ==============================================
def test_m4_suggestions_with_species(client):
    # Ensure profile has species preferences
    client.patch(f"{BASE}/profile/{TEST_USER}", json={
        "species_preferences": [
            {"species": "orignal", "frequency": 0.7, "success_rate": 0.35, "preferred_weapon": "arme_feu", "preferred_zones": []},
        ],
        "zone_preferences": [
            {"zone_id": "zone-QC-01", "visit_count": 12, "last_visit": "2026-01-01T00:00:00", "satisfaction_score": 0.85}
        ]
    })

    r = client.get(f"{BASE}/suggestions/{TEST_USER}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["count"] >= 3  # species + timing + zone + progression at minimum
    types = [s["type"] for s in data["suggestions"]]
    assert "species" in types
    assert "zone" in types
    assert "progression" in types


# ==============================================
# T7-11: Profile for new user (auto-create)
# ==============================================
def test_m4_new_user_profile(client):
    new_user = "integration_test_m4_new_user"
    r = client.get(f"{BASE}/profile/{new_user}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    p = data["profile"]
    assert p["user_id"] == new_user
    assert p["skill_level"] == "intermediaire"  # Default regional QC
    assert p["equipment"]["has_gps"] is True
    assert p["time_preferences"]["preferred_hours"] == [5, 6, 7, 16, 17, 18]


# ==============================================
# T7-12: PATCH on non-existent user (auto-creates)
# ==============================================
def test_m4_patch_nonexistent(client):
    user = "integration_test_m4_ghost"
    r = client.patch(f"{BASE}/profile/{user}", json={
        "equipment": {"has_gps": False, "has_radio": True, "mobility": "canot"}
    })
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["profile"]["equipment"]["mobility"] == "canot"
