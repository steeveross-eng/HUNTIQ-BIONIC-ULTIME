"""
Test Integration — Predictive Layer M3-A (Phase M3)
======================================================
Directive x7000-M3 — BCE-4X GOLDEN V6+
Couvre: health, predictive layer zone, prediction GPS, heatmap, best-times, admin compute
Non-regression: M1, M2
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

BASE = f"{API_URL}/api/v1/predict-layer"
M2_BASE = f"{API_URL}/api/v1/poi-graph"
M1_BASE = f"{API_URL}/api/v1/map-intel"
TEST_ZONE = "zone-m3-test-predictive"
TEST_USER = "integration_test_m3_predict"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=20) as c:
        yield c


@pytest.fixture(scope="module")
def test_pois(client):
    """Cree des POIs M2 dans la zone de test pour la heatmap."""
    pois = []
    configs = [
        {"type": "stand", "name": "M3 Stand Test", "lat": 47.0, "lng": -72.5,
         "properties": {"species_observed": ["orignal"], "frequency": 20, "confidence": 0.8}},
        {"type": "camera", "name": "M3 Camera Test", "lat": 47.002, "lng": -72.498,
         "properties": {"species_observed": ["chevreuil", "orignal"], "frequency": 40, "confidence": 0.9}},
        {"type": "point_eau", "name": "M3 Eau Test", "lat": 46.998, "lng": -72.503,
         "properties": {"species_observed": ["chevreuil"], "frequency": 15, "confidence": 0.7}},
    ]
    for cfg in configs:
        r = client.post(f"{M2_BASE}/nodes", json={
            "user_id": TEST_USER, "zone_id": TEST_ZONE, **cfg
        })
        assert r.status_code == 200
        pois.append(r.json()["node"])
    yield pois
    for p in pois:
        client.delete(f"{M2_BASE}/nodes/{p['poi_id']}")


class TestM3Health:
    """M3-0: Health endpoint"""

    def test_health_operational(self, client):
        r = client.get(f"{BASE}/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "operational"
        assert data["engine"] == "predictive_layer_engine"
        assert data["phase"] == "M3-MAP-INTELLIGENCE"
        assert data["directive"] == "x7000-M3"
        assert data["endpoints"] == 10
        assert data["fusion_points"] == 22

    def test_health_services(self, client):
        r = client.get(f"{BASE}/health")
        data = r.json()
        assert len(data["services"]) == 4
        assert "PredictiveLayerComputer" in data["services"]
        assert "TimeSeriesCollector" in data["services"]

    def test_health_anti_doublon(self, client):
        r = client.get(f"{BASE}/health")
        anti = r.json()["anti_doublon"]
        assert "predictive_engine" in anti
        assert "solunar" in anti
        assert "weather_fauna_simulation_engine" in anti

    def test_health_factor_weights(self, client):
        r = client.get(f"{BASE}/health")
        w = r.json()["factor_weights"]
        total = sum(w.values())
        assert abs(total - 1.0) < 0.01


class TestM3PredictiveLayer:
    """M3-1: Couche predictive zone"""

    def test_layer_zone(self, client):
        r = client.get(f"{BASE}/zone/{TEST_ZONE}/species/orignal?lat=47.0&lng=-72.5")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["zone_id"] == TEST_ZONE
        assert data["species"] == "orignal"
        assert len(data["predictions"]) == 24

    def test_layer_has_aggregation(self, client):
        r = client.get(f"{BASE}/zone/{TEST_ZONE}/species/orignal")
        agg = r.json()["aggregation"]
        assert "peak_probability" in agg
        assert "peak_hour" in agg
        assert "best_window" in agg
        assert "trend" in agg
        assert agg["trend"] in ["increasing", "stable", "decreasing"]

    def test_layer_has_solunar_context(self, client):
        r = client.get(f"{BASE}/zone/{TEST_ZONE}/species/orignal")
        sol = r.json()["solunar_context"]
        assert "phase_name" in sol
        assert "solunar_score" in sol

    def test_layer_has_6_data_sources(self, client):
        r = client.get(f"{BASE}/zone/{TEST_ZONE}/species/orignal")
        sources = r.json()["data_sources"]
        assert len(sources) == 6
        assert "predictive_engine" in sources
        assert "solunar" in sources
        assert "nutrition_v6" in sources

    def test_layer_prediction_factors(self, client):
        r = client.get(f"{BASE}/zone/{TEST_ZONE}/species/orignal")
        pred = r.json()["predictions"][0]
        assert "factors" in pred
        factors = pred["factors"]
        assert "base_activity" in factors
        assert "season" in factors
        assert "solunar" in factors
        assert "meteo" in factors
        assert "historical" in factors
        assert "nutrition" in factors

    def test_layer_invalid_species(self, client):
        r = client.get(f"{BASE}/zone/{TEST_ZONE}/species/INVALID")
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "INVALID_SPECIES"


class TestM3PredictAtPoint:
    """M3-2: Prediction au point GPS"""

    def test_predict_at_point(self, client):
        r = client.get(f"{BASE}/at/46.85/-71.25/species/chevreuil")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert 0 <= data["probability"] <= 1.0
        assert data["province"] == "QC"

    def test_predict_has_factors(self, client):
        r = client.get(f"{BASE}/at/46.85/-71.25/species/orignal")
        factors = r.json()["factors"]
        assert all(k in factors for k in ["base_activity", "season", "solunar", "meteo", "nutrition"])

    def test_predict_has_weights(self, client):
        r = client.get(f"{BASE}/at/46.85/-71.25/species/orignal")
        w = r.json()["weights"]
        assert abs(sum(w.values()) - 1.0) < 0.01


class TestM3Heatmap:
    """M3-3: Heatmap de probabilite"""

    def test_heatmap_with_pois(self, client, test_pois):
        r = client.get(f"{BASE}/heatmap/{TEST_ZONE}?species=orignal")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["total_pois"] >= 3

    def test_heatmap_intensity(self, client, test_pois):
        r = client.get(f"{BASE}/heatmap/{TEST_ZONE}?species=orignal")
        points = r.json()["points"]
        for p in points:
            assert p["intensity"] in ["high", "medium", "low"]
            assert 0 <= p["probability"] <= 1.0

    def test_heatmap_sorted_by_probability(self, client, test_pois):
        r = client.get(f"{BASE}/heatmap/{TEST_ZONE}?species=orignal")
        probs = [p["probability"] for p in r.json()["points"]]
        assert probs == sorted(probs, reverse=True)

    def test_heatmap_empty_zone(self, client):
        r = client.get(f"{BASE}/heatmap/empty-zone-xyz?species=orignal")
        data = r.json()
        assert data["success"] is True
        assert data["total_pois"] == 0


class TestM3BestTimes:
    """M3-4: Meilleurs creneaux"""

    def test_best_times(self, client):
        r = client.get(f"{BASE}/best-times/{TEST_ZONE}/orignal?lat=47.0&lng=-72.5")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert len(data["best_windows"]) >= 1
        assert "recommendation" in data

    def test_best_times_has_solunar(self, client):
        r = client.get(f"{BASE}/best-times/{TEST_ZONE}/orignal")
        data = r.json()
        assert "solunar_windows" in data

    def test_best_times_window_structure(self, client):
        r = client.get(f"{BASE}/best-times/{TEST_ZONE}/orignal")
        w = r.json()["best_windows"][0]
        assert "start_hour" in w
        assert "end_hour" in w
        assert "period" in w
        assert "avg_probability" in w
        assert "dominant_factor" in w


class TestM3AdminCompute:
    """M3-9: Admin force recompute"""

    def test_admin_compute(self, client):
        r = client.post(f"{BASE}/compute/{TEST_ZONE}", json={
            "species": "orignal", "lat": 47.0, "lng": -72.5
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["action"] == "FORCE_RECOMPUTE"
        assert len(data["predictions"]) == 24


class TestM1NonRegression:
    """Non-regression M1"""

    def test_m1_health(self, client):
        r = client.get(f"{M1_BASE}/health")
        assert r.status_code == 200
        assert r.json()["status"] == "operational"

    def test_m1_boundaries(self, client):
        r = client.get(f"{M1_BASE}/boundaries/at/46.85/-71.25")
        assert r.status_code == 200
        assert r.json()["province"] == "QC"


class TestM2NonRegression:
    """Non-regression M2"""

    def test_m2_health(self, client):
        r = client.get(f"{M2_BASE}/health")
        assert r.status_code == 200
        assert r.json()["status"] == "operational"

    def test_m2_nodes(self, client, test_pois):
        r = client.get(f"{M2_BASE}/nodes?zone_id={TEST_ZONE}")
        assert r.status_code == 200
        assert r.json()["count"] >= 3
