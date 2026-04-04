"""
Test Integration — AI Strategy Recommender (Phase I)
=====================================================
Directive x5400 Phase V — BCE-4X
Couvre: strategy_recommender service, stockage MongoDB, recommandations
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
TEST_USER = "integration_test_ai"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


class TestStrategyRecommenderFlow:
    """Flux complet: generation → stockage → recuperation"""

    def test_step1_generate_recommendations(self, client):
        """Generer des recommandations (sans donnees = no_data)"""
        r = client.post(f"{BASE}/v1/ai/recommend/strategy",
                        json={"user_id": TEST_USER, "species": "deer"})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["stored"] >= 1
        assert data["directive"] == "x5400-Phase-I"

    def test_step2_retrieve_recommendations(self, client):
        """Verifier que les recommandations sont persistees"""
        r = client.get(f"{BASE}/v1/ai/recommendations/{TEST_USER}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["count"] >= 1
        for rec in data["recommendations"]:
            assert "recommendation_type" in rec
            assert "content" in rec
            assert "confidence" in rec
            assert "created_at" in rec

    def test_step3_generate_multiple_species(self, client):
        """Generer recommandations pour plusieurs especes"""
        for sp in ["moose", "bear"]:
            r = client.post(f"{BASE}/v1/ai/recommend/strategy",
                            json={"user_id": TEST_USER, "species": sp})
            assert r.status_code == 200
            assert r.json()["species"] == sp

    def test_step4_filter_by_species(self, client):
        """Filtrer par espece"""
        r = client.get(f"{BASE}/v1/ai/recommendations/{TEST_USER}?species=moose")
        assert r.status_code == 200
        data = r.json()
        assert data["species_filter"] == "moose"
        for rec in data["recommendations"]:
            assert rec["species"] == "moose"

    def test_step5_different_users_isolated(self, client):
        """Les recommandations sont isolees par utilisateur"""
        r = client.get(f"{BASE}/v1/ai/recommendations/nonexistent_user_xyz")
        assert r.status_code == 200
        assert r.json()["count"] == 0
