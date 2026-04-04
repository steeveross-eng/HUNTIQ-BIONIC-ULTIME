"""
Test Integration — SUPRA Strategy Bridge (Phase I)
====================================================
Directive x5400 Phase V — BCE-4X
Couvre: supra_bridge, strategy_recommender, predict-from-history
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

BASE = f"{API_URL}/api"
TEST_USER = "integration_test_supra"
TEST_SPECIES = "moose"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


class TestSupraStrategyBridge:
    """I-1: Pipeline SUPRA → Strategy Master via supra_bridge"""

    def test_generate_from_supra_no_data(self, client):
        """Sans donnees pipeline, retourne no_analysis"""
        r = client.post(f"{BASE}/v1/strategy-master/strategy/generate-from-supra",
                        json={"user_id": TEST_USER, "species": TEST_SPECIES})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "no_analysis"

    def test_analysis_history_empty(self, client):
        """Historique vide pour utilisateur inconnu"""
        r = client.get(f"{BASE}/v1/strategy-master/analysis-history/{TEST_USER}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["analyses"] == []
        assert data["source"] == "supra_bridge"

    def test_analysis_history_with_limit(self, client):
        """Parametre limit respecte"""
        r = client.get(f"{BASE}/v1/strategy-master/analysis-history/{TEST_USER}?limit=5")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True


class TestAIStrategyRecommender:
    """I-2: Bridge IA → Strategie via strategy_recommender"""

    def test_recommend_strategy_no_data(self, client):
        """Recommandation sans historique → type no_data"""
        r = client.post(f"{BASE}/v1/ai/recommend/strategy",
                        json={"user_id": TEST_USER, "species": TEST_SPECIES})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["count"] >= 1
        assert data["recommendations"][0]["recommendation_type"] == "no_data"
        assert data["source"] == "strategy_recommender"

    def test_recommendations_list(self, client):
        """Recuperation des recommandations stockees"""
        r = client.get(f"{BASE}/v1/ai/recommendations/{TEST_USER}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert isinstance(data["recommendations"], list)

    def test_recommendations_filter_species(self, client):
        """Filtrage par espece"""
        r = client.get(f"{BASE}/v1/ai/recommendations/{TEST_USER}?species={TEST_SPECIES}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["species_filter"] == TEST_SPECIES


class TestPredictiveHistoryBridge:
    """I-3: Predictive feed depuis historique pipeline"""

    def test_predict_from_history(self, client):
        """Prediction avec historique"""
        r = client.post(f"{BASE}/v1/predictive/predict-from-history",
                        json={"user_id": TEST_USER, "species": "deer", "lat": 46.8, "lng": -71.2})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "prediction" in data
        assert "probability_24h" in data["prediction"]
        assert 0 <= data["prediction"]["probability_24h"] <= 100
        assert data["source"] == "predictive_history_bridge"

    def test_predict_different_species(self, client):
        """Prediction pour differentes especes"""
        for sp in ["moose", "bear", "deer"]:
            r = client.post(f"{BASE}/v1/predictive/predict-from-history",
                            json={"user_id": TEST_USER, "species": sp, "lat": 46.8, "lng": -71.2})
            assert r.status_code == 200
            assert r.json()["species"] == sp


class TestNonRegressionP4:
    """Non-regression: endpoints existants P4"""

    def test_strategy_master_info(self, client):
        r = client.get(f"{BASE}/v1/strategy-master/")
        assert r.status_code == 200

    def test_ai_info(self, client):
        r = client.get(f"{BASE}/v1/ai/")
        assert r.status_code == 200

    def test_predictive_info(self, client):
        r = client.get(f"{BASE}/v1/predictive/")
        assert r.status_code == 200
