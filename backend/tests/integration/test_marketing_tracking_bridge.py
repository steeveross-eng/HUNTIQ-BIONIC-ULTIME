"""
Test Integration — Marketing Tracking Bridge (Phase III)
=========================================================
Directive x5400 Phase V — BCE-4X
Couvre: share→tracking, marketing→analytics feed
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
TEST_USER = "integration_test_mkt"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


class TestShareTrackingBridge:
    """III-1: Share → Tracking bridge via tracking_bridge"""

    def test_share_track_creates_tracking_event(self, client):
        """Un partage cree un evenement tracking"""
        r = client.post(f"{BASE}/share/track",
                        json={
                            "channel": "facebook",
                            "template": "default",
                            "page_context": "test_integration",
                            "species": "deer",
                            "user_id": TEST_USER
                        })
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "tracked" or "success" in data

    def test_share_track_different_channels(self, client):
        """Partage sur differents canaux"""
        for channel in ["instagram", "whatsapp", "email"]:
            r = client.post(f"{BASE}/share/track",
                            json={
                                "channel": channel,
                                "template": "default",
                                "page_context": "test",
                                "species": "moose",
                                "user_id": TEST_USER
                            })
            assert r.status_code == 200


class TestMarketingAnalyticsFeed:
    """III-2: Marketing → Analytics via analytics_feed"""

    def test_analytics_feed_default_period(self, client):
        """Analytics feed avec periode par defaut (30j)"""
        r = client.get(f"{BASE}/v1/marketing/analytics-feed")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "analytics" in data
        analytics = data["analytics"]
        assert "period_days" in analytics
        assert analytics["period_days"] == 30
        assert "total_events" in analytics
        assert "by_type" in analytics
        assert "by_channel" in analytics

    def test_analytics_feed_custom_period(self, client):
        """Analytics feed avec periode personnalisee"""
        r = client.get(f"{BASE}/v1/marketing/analytics-feed?period=7")
        assert r.status_code == 200
        data = r.json()
        assert data["analytics"]["period_days"] == 7

    def test_analytics_feed_max_period(self, client):
        """Analytics feed avec periode max"""
        r = client.get(f"{BASE}/v1/marketing/analytics-feed?period=365")
        assert r.status_code == 200


class TestNonRegressionP3:
    """Non-regression: endpoints existants P3"""

    def test_share_stats(self, client):
        r = client.get(f"{BASE}/share/stats")
        assert r.status_code == 200

    def test_marketing_info(self, client):
        r = client.get(f"{BASE}/v1/marketing/")
        assert r.status_code == 200

    def test_share_master_switch(self, client):
        """Non-regression: master-switch endpoint"""
        r = client.get(f"{BASE}/share/master-switch")
        assert r.status_code == 200

    def test_health(self, client):
        r = client.get(f"{BASE}/health")
        assert r.status_code == 200
