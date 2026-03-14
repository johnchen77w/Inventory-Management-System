"""Tests for category CRUD endpoints."""


class TestCreateCategory:
    """Tests for POST /api/v1/categories."""

    def test_create_category_as_manager(self, client, manager_headers):
        """Manager can create a category."""
        response = client.post("/api/v1/categories", json={
            "name": "Electronics",
            "description": "Electronic components",
        }, headers=manager_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Electronics"
        assert data["description"] == "Electronic components"

    def test_create_category_as_staff_forbidden(self, client, staff_headers):
        """Staff cannot create categories."""
        response = client.post("/api/v1/categories", json={
            "name": "Forbidden",
        }, headers=staff_headers)
        assert response.status_code == 403


class TestListCategories:
    """Tests for GET /api/v1/categories."""

    def test_list_categories_empty(self, client, manager_headers):
        """List returns empty when no categories exist."""
        response = client.get("/api/v1/categories", headers=manager_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_categories_with_data(self, client, manager_headers):
        """List returns created categories."""
        client.post("/api/v1/categories", json={"name": "Cat A"}, headers=manager_headers)
        client.post("/api/v1/categories", json={"name": "Cat B"}, headers=manager_headers)

        response = client.get("/api/v1/categories", headers=manager_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_categories_as_staff(self, client, manager_headers, staff_headers):
        """Staff can list categories."""
        client.post("/api/v1/categories", json={"name": "Visible"}, headers=manager_headers)
        response = client.get("/api/v1/categories", headers=staff_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestDeleteCategory:
    """Tests for DELETE /api/v1/categories/{id}."""

    def test_delete_category(self, client, manager_headers):
        """Manager can delete a category."""
        resp = client.post("/api/v1/categories", json={"name": "ToDelete"}, headers=manager_headers)
        cat_id = resp.json()["id"]

        response = client.delete(f"/api/v1/categories/{cat_id}", headers=manager_headers)
        assert response.status_code == 204

    def test_delete_category_as_staff_forbidden(self, client, manager_headers, staff_headers):
        """Staff cannot delete categories."""
        resp = client.post("/api/v1/categories", json={"name": "Protected"}, headers=manager_headers)
        cat_id = resp.json()["id"]

        response = client.delete(f"/api/v1/categories/{cat_id}", headers=staff_headers)
        assert response.status_code == 403
