"""
test_access_engine_v6_api.py — API Integration Tests for access_engine_v6
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX

Tests HTTP endpoints:
  - GET /api/v6/access/health
  - POST /api/v6/access/compute
  - POST /api/v6/access/compute-batch
  - Cache hit verification
"""
import os
import pytest
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Create session with retry logic for flaky network
def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Quebec hunting area test coordinates
TEST_ORIGIN = {"lat": 48.4284, "lng": -68.5214}
TEST_DESTINATION_1 = {"lat": 48.4350, "lng": -68.5100}
TEST_DESTINATION_2 = {"lat": 48.4300, "lng": -68.5050}


class TestAccessHealthEndpoint:
    """Test GET /api/v6/access/health endpoint"""

    def test_health_returns_200(self):
        """Health endpoint should return 200 OK"""
        session = get_session()
        resp = session.get(f"{BASE_URL}/api/v6/access/health", timeout=60)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    def test_health_returns_operational_status(self):
        """Health endpoint should return operational status"""
        session = get_session()
        resp = session.get(f"{BASE_URL}/api/v6/access/health", timeout=60)
        data = resp.json()
        assert data["status"] == "operational", f"Expected operational, got {data.get('status')}"
        assert data["module"] == "access_engine_v6"
        assert data["protocol"] == "BIONIC GOLDEN"
        assert "Trail-First Dijkstra" in data["pipeline"]


class TestAccessComputeEndpoint:
    """Test POST /api/v6/access/compute endpoint"""

    def test_compute_returns_200(self):
        """Compute endpoint should return 200 OK"""
        session = get_session()
        payload = {
            "origin": TEST_ORIGIN,
            "destination": TEST_DESTINATION_1,
            "month": 10,
            "species": "orignal"
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=90
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    def test_compute_returns_route_structure(self):
        """Compute endpoint should return proper route structure"""
        session = get_session()
        payload = {
            "origin": TEST_ORIGIN,
            "destination": TEST_DESTINATION_1,
            "month": 10,
            "species": "orignal"
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=90
        )
        data = resp.json()
        
        # Status check
        assert data["status"] == "ok", f"Expected status=ok, got {data.get('status')}"
        
        # Route structure
        assert "route" in data, "Response must contain 'route' key"
        route = data["route"]
        
        # Required route fields
        assert "total_distance_m" in route, "Route must have total_distance_m"
        assert "total_cost" in route, "Route must have total_cost"
        assert "estimated_time_min" in route, "Route must have estimated_time_min"
        assert "trail_percentage" in route, "Route must have trail_percentage"
        assert "segments" in route, "Route must have segments"
        assert "vegetation_analysis" in route, "Route must have vegetation_analysis"

    def test_compute_returns_segments_with_colors(self):
        """Compute endpoint should return segments with 4-color classification"""
        session = get_session()
        payload = {
            "origin": TEST_ORIGIN,
            "destination": TEST_DESTINATION_1,
            "month": 10,
            "species": "orignal"
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=90
        )
        data = resp.json()
        segments = data["route"]["segments"]
        
        assert len(segments) > 0, "Route must have at least one segment"
        
        # Valid colors per GOLDEN protocol
        valid_colors = {"#2ECC71", "#3498DB", "#F1C40F", "#E74C3C"}
        valid_types = {"trail", "hybrid", "off_trail_optimized", "non_conformant"}
        
        for seg in segments:
            assert "type" in seg, "Segment must have type"
            assert "color" in seg, "Segment must have color"
            assert "coordinates" in seg, "Segment must have coordinates"
            assert seg["type"] in valid_types, f"Invalid segment type: {seg['type']}"
            assert seg["color"] in valid_colors, f"Invalid segment color: {seg['color']}"

    def test_compute_returns_vegetation_analysis(self):
        """Compute endpoint should return vegetation analysis for off-trail segments"""
        session = get_session()
        payload = {
            "origin": TEST_ORIGIN,
            "destination": TEST_DESTINATION_1,
            "month": 10,
            "species": "orignal"
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=90
        )
        data = resp.json()
        
        # Check vegetation_analysis in route
        veg_analysis = data["route"]["vegetation_analysis"]
        assert "favorable_zones" in veg_analysis
        assert "unfavorable_zones" in veg_analysis
        assert "dominant_strategy" in veg_analysis

    def test_compute_with_options(self):
        """Compute endpoint should accept custom options"""
        session = get_session()
        payload = {
            "origin": TEST_ORIGIN,
            "destination": TEST_DESTINATION_1,
            "month": 11,
            "species": "cerf",
            "options": {
                "max_off_trail_km": 3.0,
                "prefer_trails": True,
                "analysis_radius_m": 4000
            }
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=90
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestAccessCacheHit:
    """Test cache functionality"""

    def test_cache_hit_on_second_call(self):
        """Second identical call should return cache_hit=true"""
        session = get_session()
        # Use unique coordinates to avoid interference from other tests
        unique_origin = {"lat": 48.5000, "lng": -68.6000}
        unique_dest = {"lat": 48.5050, "lng": -68.5950}
        
        payload = {
            "origin": unique_origin,
            "destination": unique_dest,
            "month": 10,
            "species": "orignal"
        }
        
        # First call - should compute fresh
        resp1 = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=90
        )
        assert resp1.status_code == 200
        data1 = resp1.json()
        # First call may or may not be cache hit depending on previous runs
        
        # Second call - should be cache hit
        resp2 = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=90
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2.get("cache_hit") == True, f"Expected cache_hit=True, got {data2.get('cache_hit')}"


class TestAccessBatchEndpoint:
    """Test POST /api/v6/access/compute-batch endpoint"""

    def test_batch_returns_200(self):
        """Batch endpoint should return 200 OK"""
        session = get_session()
        payload = {
            "origin": TEST_ORIGIN,
            "destinations": [
                {"id": "stand_1", "lat": TEST_DESTINATION_1["lat"], "lng": TEST_DESTINATION_1["lng"]},
                {"id": "stand_2", "lat": TEST_DESTINATION_2["lat"], "lng": TEST_DESTINATION_2["lng"]}
            ],
            "month": 10,
            "species": "orignal"
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute-batch",
            json=payload,
            timeout=120
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    def test_batch_returns_multiple_routes(self):
        """Batch endpoint should return routes for all destinations"""
        session = get_session()
        payload = {
            "origin": TEST_ORIGIN,
            "destinations": [
                {"id": "stand_1", "lat": TEST_DESTINATION_1["lat"], "lng": TEST_DESTINATION_1["lng"]},
                {"id": "stand_2", "lat": TEST_DESTINATION_2["lat"], "lng": TEST_DESTINATION_2["lng"]}
            ],
            "month": 10,
            "species": "orignal"
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute-batch",
            json=payload,
            timeout=120
        )
        data = resp.json()
        
        assert "routes" in data, "Response must contain 'routes' key"
        routes = data["routes"]
        assert len(routes) == 2, f"Expected 2 routes, got {len(routes)}"
        
        # Check each route has stand_id and route data
        stand_ids = {r["stand_id"] for r in routes}
        assert "stand_1" in stand_ids
        assert "stand_2" in stand_ids
        
        for route_item in routes:
            assert "stand_id" in route_item
            assert "route" in route_item
            if route_item["route"]:
                assert "total_distance_m" in route_item["route"]
                assert "segments" in route_item["route"]


class TestAccessValidation:
    """Test input validation"""

    def test_invalid_latitude_rejected(self):
        """Invalid latitude should be rejected"""
        session = get_session()
        payload = {
            "origin": {"lat": 100.0, "lng": -68.5214},  # Invalid lat > 90
            "destination": TEST_DESTINATION_1,
            "month": 10,
            "species": "orignal"
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=30
        )
        assert resp.status_code == 422, f"Expected 422 validation error, got {resp.status_code}"

    def test_invalid_month_rejected(self):
        """Invalid month should be rejected"""
        session = get_session()
        payload = {
            "origin": TEST_ORIGIN,
            "destination": TEST_DESTINATION_1,
            "month": 13,  # Invalid month > 12
            "species": "orignal"
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=30
        )
        assert resp.status_code == 422, f"Expected 422 validation error, got {resp.status_code}"

    def test_missing_origin_rejected(self):
        """Missing origin should be rejected"""
        session = get_session()
        payload = {
            "destination": TEST_DESTINATION_1,
            "month": 10,
            "species": "orignal"
        }
        resp = session.post(
            f"{BASE_URL}/api/v6/access/compute",
            json=payload,
            timeout=30
        )
        assert resp.status_code == 422, f"Expected 422 validation error, got {resp.status_code}"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session
