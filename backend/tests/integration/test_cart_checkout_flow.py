"""
Test Integration — Cart Checkout Flow (Phase P5-B/C)
=====================================================
Directive x5400-F Phase P5-E — BCE-4X
Couvre: validation, promotions, checkout, sync, suggestions
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
TEST_USER = "integration_test_checkout"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


@pytest.fixture(autouse=True, scope="module")
def setup_cart(client):
    """Prepare un panier avec des articles pour le checkout."""
    client.delete(f"{BASE}/v1/cart/user/{TEST_USER}/clear")
    client.post(f"{BASE}/v1/cart/user/{TEST_USER}/items", json={
        "product_type": "package",
        "product_id": "pro_monthly",
        "name": "Pro Mensuel",
        "unit_price": 49.99,
        "quantity": 1
    })
    client.post(f"{BASE}/v1/cart/user/{TEST_USER}/items", json={
        "product_type": "addon",
        "product_id": "supra_advanced",
        "name": "SUPRA Avance",
        "unit_price": 14.99,
        "quantity": 1
    })
    yield
    client.delete(f"{BASE}/v1/cart/user/{TEST_USER}/clear")


class TestCartValidation:
    """P5-B: Validation pre-checkout"""

    def test_validate_cart_with_items(self, client):
        """Validation d'un panier avec articles"""
        r = client.post(f"{BASE}/v1/cart/user/{TEST_USER}/validate")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["validation"]["valid"] is True
        assert data["validation"]["item_count"] == 2
        assert data["validation"]["total"] > 0

    def test_validate_empty_cart(self, client):
        """Validation d'un panier vide"""
        empty_user = "integration_test_empty_checkout"
        client.delete(f"{BASE}/v1/cart/user/{empty_user}/clear")
        r = client.post(f"{BASE}/v1/cart/user/{empty_user}/validate")
        assert r.status_code == 200
        data = r.json()
        assert data["validation"]["valid"] is False
        assert data["validation"]["errors"][0]["code"] == "EMPTY_CART"


class TestCartPromotions:
    """P5-B: Promotions"""

    def test_apply_invalid_promo(self, client):
        """Appliquer un code promo invalide"""
        r = client.post(f"{BASE}/v1/cart/user/{TEST_USER}/promotions",
                        json={"promo_code": "INVALID_CODE_XYZ"})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "CODE_NOT_FOUND"

    def test_remove_nonexistent_promo(self, client):
        """Retirer un code promo non applique"""
        r = client.delete(f"{BASE}/v1/cart/user/{TEST_USER}/promotions/FAKE_CODE")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is False


class TestCartSync:
    """P5-C: Synchronisation"""

    def test_sync_cart(self, client):
        """Synchronisation avec freemium"""
        r = client.post(f"{BASE}/v1/cart/user/{TEST_USER}/sync")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "freemium_status" in data
        assert "cart" in data
        assert data["directive"] == "x5400-F-P5C"

    def test_get_suggestions(self, client):
        """Suggestions upsell"""
        r = client.get(f"{BASE}/v1/cart/user/{TEST_USER}/suggestions")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert isinstance(data["suggestions"], list)
        assert "suggestion_count" in data


class TestCartCheckout:
    """P5-B: Checkout complet"""

    def test_checkout_creates_order(self, client):
        """Checkout cree une commande et change le statut"""
        r = client.post(f"{BASE}/v1/cart/user/{TEST_USER}/checkout")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "order_id" in data
        assert data["total"] > 0
        assert data["currency"] == "CAD"
        assert data["directive"] == "x5400-F-P5B"

    def test_checkout_empty_cart_fails(self, client):
        """Checkout d'un panier vide echoue"""
        empty_user = "integration_test_empty_co"
        client.delete(f"{BASE}/v1/cart/user/{empty_user}/clear")
        r = client.post(f"{BASE}/v1/cart/user/{empty_user}/checkout")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is False
        assert data["error"] == "VALIDATION_FAILED"


class TestNonRegressionPayment:
    """Non-regression: payment engine V1"""

    def test_payment_info(self, client):
        r = client.get(f"{BASE}/v1/payments/")
        assert r.status_code == 200

    def test_payment_packages(self, client):
        r = client.get(f"{BASE}/v1/payments/packages")
        assert r.status_code == 200
        assert "packages" in r.json()

    def test_freemium_info(self, client):
        r = client.get(f"{BASE}/v1/freemium/")
        assert r.status_code == 200

    def test_health(self, client):
        r = client.get(f"{BASE}/health")
        assert r.status_code == 200
