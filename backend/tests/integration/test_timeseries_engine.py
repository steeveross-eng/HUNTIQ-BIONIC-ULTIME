"""
Test Integration — TimeSeries + Trends + Correlation M3-B (Phase M3)
======================================================================
Directive x7000-M3 — BCE-4X GOLDEN V6+
Couvre: record, timeseries, trends, meteo correlation, validation errors
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
TEST_ZONE = "zone-m3-test-timeseries"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=20) as c:
        yield c


@pytest.fixture(scope="module")
def seeded_ts(client):
    """Seed des points de series temporelles pour les tests."""
    records = [
        {"zone_id": TEST_ZONE, "species": "orignal", "metric": "activity_index",
         "value": 0.75, "source": "manual", "timestamp": "2026-04-01T06:00:00Z"},
        {"zone_id": TEST_ZONE, "species": "orignal", "metric": "activity_index",
         "value": 0.82, "source": "manual", "timestamp": "2026-04-01T07:00:00Z"},
        {"zone_id": TEST_ZONE, "species": "orignal", "metric": "activity_index",
         "value": 0.65, "source": "manual", "timestamp": "2026-04-01T12:00:00Z"},
        {"zone_id": TEST_ZONE, "species": "orignal", "metric": "observation_count",
         "value": 3, "source": "poi_graph"},
        {"zone_id": TEST_ZONE, "species": "chevreuil", "metric": "camera_detection",
         "value": 7, "source": "poi_graph"},
    ]
    for rec in records:
        r = client.post(f"{BASE}/timeseries/record", json=rec)
        assert r.status_code == 200
        assert r.json()["success"] is True
    yield records


class TestM3RecordTimeSeries:
    """M3-6: Enregistrer points de serie"""

    def test_record_valid(self, client):
        r = client.post(f"{BASE}/timeseries/record", json={
            "zone_id": "zone-record-test",
            "species": "chevreuil",
            "metric": "activity_index",
            "value": 0.55,
            "source": "manual"
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["recorded"] is True
        assert data["metric"] == "activity_index"

    def test_record_invalid_metric(self, client):
        r = client.post(f"{BASE}/timeseries/record", json={
            "zone_id": "zone-x", "species": "orignal",
            "metric": "INVALID_METRIC", "value": 1.0
        })
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "INVALID_METRIC"

    def test_record_invalid_source(self, client):
        r = client.post(f"{BASE}/timeseries/record", json={
            "zone_id": "zone-x", "species": "orignal",
            "metric": "activity_index", "value": 1.0,
            "source": "INVALID_SRC"
        })
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "INVALID_SOURCE"

    def test_record_missing_fields(self, client):
        r = client.post(f"{BASE}/timeseries/record", json={"zone_id": "z"})
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "MISSING_FIELDS"

    def test_record_with_poi_id(self, client):
        r = client.post(f"{BASE}/timeseries/record", json={
            "zone_id": "zone-poi-record",
            "species": "orignal",
            "metric": "poi_frequency",
            "value": 5,
            "source": "poi_graph",
            "poi_id": "fake-poi-123"
        })
        data = r.json()
        assert data["success"] is True


class TestM3GetTimeSeries:
    """M3-5: Recuperer series temporelles"""

    def test_get_existing(self, client, seeded_ts):
        r = client.get(f"{BASE}/timeseries/{TEST_ZONE}/orignal?metric=activity_index")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["total_points"] >= 3
        assert len(data["values"]) >= 3

    def test_get_empty(self, client):
        r = client.get(f"{BASE}/timeseries/nonexistent-zone/orignal")
        data = r.json()
        assert data["success"] is True
        assert data["total_points"] == 0
        assert data["message"] == "NO_DATA"

    def test_get_different_metric(self, client, seeded_ts):
        r = client.get(f"{BASE}/timeseries/{TEST_ZONE}/orignal?metric=observation_count")
        data = r.json()
        assert data["success"] is True
        assert data["total_points"] >= 1

    def test_get_different_species(self, client, seeded_ts):
        r = client.get(f"{BASE}/timeseries/{TEST_ZONE}/chevreuil?metric=camera_detection")
        data = r.json()
        assert data["success"] is True
        assert data["total_points"] >= 1


class TestM3Trends:
    """M3-7: Tendances saisonnieres"""

    def test_trends_basic(self, client, seeded_ts):
        r = client.get(f"{BASE}/trends/orignal?zone_id={TEST_ZONE}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert len(data["monthly_patterns"]) == 12

    def test_trends_annual_summary(self, client, seeded_ts):
        r = client.get(f"{BASE}/trends/orignal?zone_id={TEST_ZONE}")
        summary = r.json()["annual_summary"]
        assert "peak_month" in summary
        assert "peak_activity" in summary
        assert "low_month" in summary
        assert "avg_activity" in summary
        assert summary["peak_activity"] > summary["low_activity"]

    def test_trends_monthly_structure(self, client, seeded_ts):
        r = client.get(f"{BASE}/trends/orignal?zone_id={TEST_ZONE}")
        mp = r.json()["monthly_patterns"][0]
        assert "month" in mp
        assert "activity_index" in mp
        assert "peak_hours" in mp
        assert "baseline_factor" in mp
        assert "confidence" in mp

    def test_trends_baseline_from_predictive_engine(self, client, seeded_ts):
        """PF3-S2 : Baseline saisonniere lue depuis predictive_engine."""
        r = client.get(f"{BASE}/trends/orignal?zone_id={TEST_ZONE}")
        patterns = r.json()["monthly_patterns"]
        oct_pattern = patterns[9]  # Month 10
        assert oct_pattern["baseline_factor"] == 0.95  # From SEASON_FACTORS


class TestM3MeteoCorrelation:
    """M3-8: Correlations meteo-faune"""

    def test_correlation_basic(self, client, seeded_ts):
        r = client.get(f"{BASE}/correlation/meteo/{TEST_ZONE}?species=orignal")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["species"] == "orignal"
        assert "correlation_matrix" in data

    def test_correlation_6_factors(self, client, seeded_ts):
        r = client.get(f"{BASE}/correlation/meteo/{TEST_ZONE}?species=orignal")
        matrix = r.json()["correlation_matrix"]
        expected = ["temperature", "barometric_pressure", "wind_speed",
                    "precipitation", "lunar_phase", "humidity"]
        for f in expected:
            assert f in matrix
            assert "correlation_strength" in matrix[f]
            assert "impact" in matrix[f]

    def test_correlation_optimal_from_weather_sim(self, client, seeded_ts):
        """PF3-MET1 : Conditions optimales lues depuis weather_fauna_simulation."""
        r = client.get(f"{BASE}/correlation/meteo/{TEST_ZONE}?species=orignal")
        opt = r.json()["optimal_conditions"]
        assert opt["source"] == "weather_fauna_simulation_engine"
        assert opt["optimal_temp_min"] == -5.0  # moose optimal
        assert opt["optimal_temp_max"] == 10.0

    def test_correlation_solunar_context(self, client, seeded_ts):
        """PF3-LUN1/LUN3 : Contexte solunaire."""
        r = client.get(f"{BASE}/correlation/meteo/{TEST_ZONE}?species=orignal")
        sol = r.json()["solunar_context"]
        assert sol["source"] == "solunar_engine"
        assert "phase_name" in sol
        assert "solunar_score" in sol

    def test_correlation_data_richness(self, client, seeded_ts):
        r = client.get(f"{BASE}/correlation/meteo/{TEST_ZONE}?species=orignal")
        data = r.json()
        assert 0 <= data["data_richness"] <= 1.0
        assert 0 <= data["confidence"] <= 1.0

    def test_correlation_chevreuil(self, client, seeded_ts):
        r = client.get(f"{BASE}/correlation/meteo/{TEST_ZONE}?species=chevreuil")
        data = r.json()
        assert data["success"] is True
        opt = data["optimal_conditions"]
        assert opt["optimal_temp_min"] == 2  # deer optimal


class TestM3Validation:
    """Tests de validation croisee"""

    def test_prediction_probability_range(self, client):
        r = client.get(f"{BASE}/at/46.85/-71.25/species/orignal")
        data = r.json()
        assert 0 <= data["probability"] <= 1.0

    def test_all_species_valid(self, client):
        for species in ["orignal", "chevreuil", "ours_noir", "dindon_sauvage"]:
            r = client.get(f"{BASE}/at/46.85/-71.25/species/{species}")
            assert r.json()["success"] is True, f"Failed for {species}"
