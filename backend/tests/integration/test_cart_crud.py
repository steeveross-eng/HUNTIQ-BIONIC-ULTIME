"""
Test Integration — Cart CRUD V2 (Phase P5-A)
===============================================
Directive x5400-F Phase P5-E — BCE-4X
Couvre: get_or_create, add_item, update_qty, remove_item, clear, summary
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
TEST_USER = "integration_test_cart_v2"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(timeout=15) as c:
        yield c


@pytest.fixture(autouse=True, scope="module")
def cleanup_cart(client):
    """Nettoie le panier avant les tests."""
    client.delete(f"{BASE}/v1/cart/user/{TEST_USER}/clear")
    yield
    client.delete(f"{BASE}/v1/cart/user/{TEST_USER}/clear")


class TestCartCreation:
    """P5-A: Creation automatique du panier"""

    def test_get_creates_cart(self, client):
        """GET sur user sans panier cree automatiquement"""
        r = client.get(f"{BASE}/v1/cart/user/{TEST_USER}")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["cart"]["user_id"] == TEST_USER
        assert data["cart"]["status"] == "active"
        assert data["cart"]["items"] == []
        assert data["cart"]["total"] == 0.0
        assert data["source"] == "cart_engine_v2"

    def test_get_returns_same_cart(self, client):
        """GET consecutif retourne le meme panier"""
        r1 = client.get(f"{BASE}/v1/cart/user/{TEST_USER}")
        r2 = client.get(f"{BASE}/v1/cart/user/{TEST_USER}")
        assert r1.json()["cart"]["cart_id"] == r2.json()["cart"]["cart_id"]


class TestCartAddItem:
    """P5-A: Ajout d'articles"""

    def test_add_first_item(self, client):
        """Ajout du premier article"""
        r = client.post(f"{BASE}/v1/cart/user/{TEST_USER}/items", json={
            "product_type": "package",
            "product_id": "premium_monthly",
            "name": "Premium Mensuel",
            "unit_price": 19.99,
            "quantity": 1
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["cart"]["item_count"] == 1
        assert data["cart"]["total"] == 19.99

    def test_add_second_item(self, client):
        """Ajout d'un second article"""
        r = client.post(f"{BASE}/v1/cart/user/{TEST_USER}/items", json={
            "product_type": "addon",
            "product_id": "supra_addon",
            "name": "SUPRA Addon",
            "unit_price": 9.99,
            "quantity": 2
        })
        assert r.status_code == 200
        data = r.json()
        assert data["cart"]["item_count"] == 2
        assert data["cart"]["total"] == 39.97

    def test_add_duplicate_merges(self, client):
        """Ajout d'un article existant merge les quantites"""
        r = client.post(f"{BASE}/v1/cart/user/{TEST_USER}/items", json={
            "product_type": "addon",
            "product_id": "supra_addon",
            "name": "SUPRA Addon",
            "unit_price": 9.99,
            "quantity": 1
        })
        assert r.status_code == 200
        data = r.json()
        assert data["cart"]["item_count"] == 2
        addon = [i for i in data["cart"]["items"] if i["product_id"] == "supra_addon"][0]
        assert addon["quantity"] == 3


class TestCartUpdateQuantity:
    """P5-A: Modification des quantites"""

    def test_update_quantity(self, client):
        """Mise a jour de la quantite"""
        cart = client.get(f"{BASE}/v1/cart/user/{TEST_USER}").json()["cart"]
        item_id = cart["items"][0]["item_id"]

        r = client.patch(f"{BASE}/v1/cart/user/{TEST_USER}/items/{item_id}",
                         json={"quantity": 3})
        assert r.status_code == 200
        assert r.json()["success"] is True

    def test_update_nonexistent_item(self, client):
        """Mise a jour d'un item inexistant retourne 404"""
        r = client.patch(f"{BASE}/v1/cart/user/{TEST_USER}/items/nonexistent",
                         json={"quantity": 5})
        assert r.status_code == 404


class TestCartRemoveItem:
    """P5-A: Suppression d'articles"""

    def test_remove_item(self, client):
        """Suppression d'un article"""
        cart = client.get(f"{BASE}/v1/cart/user/{TEST_USER}").json()["cart"]
        item_id = cart["items"][-1]["item_id"]
        initial_count = len(cart["items"])

        r = client.delete(f"{BASE}/v1/cart/user/{TEST_USER}/items/{item_id}")
        assert r.status_code == 200
        assert r.json()["cart"]["item_count"] == initial_count - 1

    def test_remove_nonexistent_item(self, client):
        """Suppression d'un item inexistant retourne 404"""
        r = client.delete(f"{BASE}/v1/cart/user/{TEST_USER}/items/nonexistent")
        assert r.status_code == 404


class TestCartClearAndSummary:
    """P5-A: Vidage et resume"""

    def test_summary(self, client):
        """Resume du panier"""
        r = client.get(f"{BASE}/v1/cart/user/{TEST_USER}/summary")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        summary = data["summary"]
        assert "cart_id" in summary
        assert "subtotal" in summary
        assert "total" in summary
        assert summary["currency"] == "CAD"

    def test_clear_cart(self, client):
        """Vidage du panier"""
        r = client.delete(f"{BASE}/v1/cart/user/{TEST_USER}/clear")
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["cart"]["item_count"] == 0
        assert data["cart"]["total"] == 0.0


class TestNonRegressionV1:
    """Non-regression: endpoints V1"""

    def test_v1_health(self, client):
        r = client.get(f"{BASE}/v1/cart/health")
        assert r.status_code == 200
        assert r.json()["status"] == "operational"

    def test_v1_stats(self, client):
        r = client.get(f"{BASE}/v1/cart/stats")
        assert r.status_code == 200
        assert r.json()["engine"] == "cart_engine"
