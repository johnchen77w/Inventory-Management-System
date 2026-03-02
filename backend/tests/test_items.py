"""Tests for item CRUD and inventory operations."""
import pytest


@pytest.fixture
def sample_item(client, manager_headers):
    """Create a sample item and return the response data."""
    response = client.post("/api/v1/items", json={
        "sku": "TEST-001",
        "name": "Test Widget",
        "description": "A test item",
        "quantity": 100,
        "unit": "pcs",
        "price": "9.99",
        "low_stock_threshold": 10,
    }, headers=manager_headers)
    assert response.status_code == 201
    return response.json()


class TestCreateItem:
    """Tests for POST /api/v1/items."""

    def test_create_item_as_manager(self, client, manager_headers):
        """Manager can create a new item."""
        response = client.post("/api/v1/items", json={
            "sku": "ITEM-001",
            "name": "Widget A",
            "quantity": 50,
        }, headers=manager_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == "ITEM-001"
        assert data["name"] == "Widget A"
        assert data["quantity"] == 50

    def test_create_item_as_staff_forbidden(self, client, staff_headers):
        """Staff cannot create items."""
        response = client.post("/api/v1/items", json={
            "sku": "ITEM-002",
            "name": "Widget B",
        }, headers=staff_headers)
        assert response.status_code == 403

    def test_create_item_no_auth(self, client):
        """Cannot create items without auth (HTTPBearer returns 403)."""
        response = client.post("/api/v1/items", json={
            "sku": "ITEM-003",
            "name": "Widget C",
        })
        assert response.status_code == 403


class TestListItems:
    """Tests for GET /api/v1/items."""

    def test_list_items_empty(self, client, manager_headers):
        """List items returns empty when no items exist."""
        response = client.get("/api/v1/items", headers=manager_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_items_with_data(self, client, manager_headers, sample_item):
        """List items returns created items."""
        response = client.get("/api/v1/items", headers=manager_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["sku"] == "TEST-001"

    def test_list_items_as_staff(self, client, staff_headers, sample_item):
        """Staff can list items."""
        response = client.get("/api/v1/items", headers=staff_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1


class TestGetItem:
    """Tests for GET /api/v1/items/{id}."""

    def test_get_item(self, client, manager_headers, sample_item):
        """Get item by ID."""
        item_id = sample_item["id"]
        response = client.get(f"/api/v1/items/{item_id}", headers=manager_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Test Widget"

    def test_get_item_not_found(self, client, manager_headers):
        """Get non-existent item returns 404."""
        response = client.get("/api/v1/items/9999", headers=manager_headers)
        assert response.status_code == 404


class TestUpdateItem:
    """Tests for PUT /api/v1/items/{id}."""

    def test_update_item(self, client, manager_headers, sample_item):
        """Manager can update an item."""
        item_id = sample_item["id"]
        response = client.put(f"/api/v1/items/{item_id}", json={
            "name": "Updated Widget",
        }, headers=manager_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Widget"

    def test_update_item_as_staff_forbidden(self, client, staff_headers, sample_item):
        """Staff cannot update items via PUT."""
        item_id = sample_item["id"]
        response = client.put(f"/api/v1/items/{item_id}", json={
            "name": "Staff Update",
        }, headers=staff_headers)
        assert response.status_code == 403


class TestDeleteItem:
    """Tests for DELETE /api/v1/items/{id}."""

    def test_delete_item(self, client, manager_headers, sample_item):
        """Manager can delete an item."""
        item_id = sample_item["id"]
        response = client.delete(f"/api/v1/items/{item_id}", headers=manager_headers)
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/api/v1/items/{item_id}", headers=manager_headers)
        assert response.status_code == 404

    def test_delete_item_as_staff_forbidden(self, client, staff_headers, sample_item):
        """Staff cannot delete items."""
        item_id = sample_item["id"]
        response = client.delete(f"/api/v1/items/{item_id}", headers=staff_headers)
        assert response.status_code == 403


class TestRestock:
    """Tests for POST /api/v1/items/{id}/restock."""

    def test_restock_item(self, client, manager_headers, sample_item):
        """Restock increases quantity."""
        item_id = sample_item["id"]
        response = client.post(f"/api/v1/items/{item_id}/restock", json={
            "quantity": 50,
            "notes": "Restocking from supplier",
        }, headers=manager_headers)
        assert response.status_code == 200
        assert response.json()["quantity"] == 150  # 100 + 50

    def test_restock_as_staff(self, client, staff_headers, sample_item):
        """Staff can restock items."""
        item_id = sample_item["id"]
        response = client.post(f"/api/v1/items/{item_id}/restock", json={
            "quantity": 25,
        }, headers=staff_headers)
        assert response.status_code == 200
        assert response.json()["quantity"] == 125  # 100 + 25


class TestWithdraw:
    """Tests for POST /api/v1/items/{id}/withdraw."""

    def test_withdraw_item(self, client, manager_headers, sample_item):
        """Withdraw decreases quantity."""
        item_id = sample_item["id"]
        response = client.post(f"/api/v1/items/{item_id}/withdraw", json={
            "quantity": 30,
            "notes": "Order fulfillment",
        }, headers=manager_headers)
        assert response.status_code == 200
        assert response.json()["quantity"] == 70  # 100 - 30

    def test_withdraw_insufficient_stock(self, client, manager_headers, sample_item):
        """Cannot withdraw more than available."""
        item_id = sample_item["id"]
        response = client.post(f"/api/v1/items/{item_id}/withdraw", json={
            "quantity": 999,
        }, headers=manager_headers)
        assert response.status_code == 400
