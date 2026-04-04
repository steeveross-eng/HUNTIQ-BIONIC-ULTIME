"""
Test Integration — E-Commerce Pipeline (Phase II)
===================================================
Directive x5400 Phase V — BCE-4X
Couvre: payment→orders, freemium→upsell trigger, upsell-events
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
TEST_USER = "integration_test_ecom"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


class TestFreemiumUpsellBridge:
    """II-2: Freemium → Upsell trigger via upsell_notifier"""

    def test_upsell_events_empty_user(self, client):
        """Utilisateur sans evenements upsell"""
        r = client.get(f"{BASE}/v1/freemium/upsell-events/{TEST_USER}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert data["events"] == []
        assert data["source"] == "upsell_notifier"

    def test_quota_increment_triggers_upsell(self, client):
        """Increment quota → evenement upsell si limite atteinte"""
        for _ in range(5):
            r = client.post(f"{BASE}/v1/freemium/quota/{TEST_USER}/daily_analysis/increment")
            assert r.status_code == 200

    def test_check_access_blocked_feature(self, client):
        """Feature bloquee retourne upgrade_required"""
        r = client.post(f"{BASE}/v1/freemium/check-access",
                        json={"user_id": TEST_USER, "feature": "supra_analysis"})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "can_access" in data


class TestNonRegressionP5:
    """Non-regression: endpoints existants P5"""

    def test_payment_info(self, client):
        r = client.get(f"{BASE}/v1/payments/")
        assert r.status_code == 200

    def test_payment_packages(self, client):
        r = client.get(f"{BASE}/v1/payments/packages")
        assert r.status_code == 200
        data = r.json()
        assert "packages" in data
        assert len(data["packages"]) >= 4

    def test_freemium_info(self, client):
        r = client.get(f"{BASE}/v1/freemium/")
        assert r.status_code == 200

    def test_freemium_pricing(self, client):
        r = client.get(f"{BASE}/v1/freemium/pricing")
        assert r.status_code == 200

    def test_freemium_tiers_compare(self, client):
        r = client.get(f"{BASE}/v1/freemium/tiers/compare")
        assert r.status_code == 200
