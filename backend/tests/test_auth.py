"""Tests for authentication endpoints."""


class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    def test_login_success(self, client, manager_user):
        """Login with valid credentials returns tokens."""
        response = client.post("/api/v1/auth/login", json={
            "email": "manager@test.com",
            "password": "password123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, manager_user):
        """Login with wrong password returns 401."""
        response = client.post("/api/v1/auth/login", json={
            "email": "manager@test.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Login with non-existent email returns 401."""
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com",
            "password": "password123",
        })
        assert response.status_code == 401

    def test_login_inactive_user(self, client, db):
        """Login with deactivated account returns 401."""
        from app.models.user import User, UserRole
        from app.utils.security import hash_password

        user = User(
            email="inactive@test.com",
            hashed_password=hash_password("password123"),
            full_name="Inactive User",
            role=UserRole.staff,
            is_active=False,
        )
        db.add(user)
        db.commit()

        response = client.post("/api/v1/auth/login", json={
            "email": "inactive@test.com",
            "password": "password123",
        })
        assert response.status_code == 401


class TestGetMe:
    """Tests for GET /api/v1/auth/me."""

    def test_get_me_authenticated(self, client, manager_headers, manager_user):
        """Authenticated user can get their own profile."""
        response = client.get("/api/v1/auth/me", headers=manager_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "manager@test.com"
        assert data["full_name"] == "Test Manager"

    def test_get_me_no_token(self, client):
        """Request without token returns 403 (HTTPBearer rejects missing credentials)."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403


class TestRegister:
    """Tests for POST /api/v1/auth/register."""

    def test_register_as_manager(self, client, manager_headers):
        """Manager can register a new user."""
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "newpass123",
            "full_name": "New User",
            "role": "staff",
        }, headers=manager_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "staff"

    def test_register_as_staff_forbidden(self, client, staff_headers):
        """Staff cannot register new users."""
        response = client.post("/api/v1/auth/register", json={
            "email": "another@test.com",
            "password": "pass123",
            "full_name": "Another User",
            "role": "staff",
        }, headers=staff_headers)
        assert response.status_code == 403

    def test_register_duplicate_email(self, client, manager_headers, manager_user):
        """Cannot register with an existing email."""
        response = client.post("/api/v1/auth/register", json={
            "email": "manager@test.com",
            "password": "pass123",
            "full_name": "Duplicate",
            "role": "staff",
        }, headers=manager_headers)
        assert response.status_code == 409

    def test_register_no_auth(self, client):
        """Cannot register without authentication (HTTPBearer returns 403)."""
        response = client.post("/api/v1/auth/register", json={
            "email": "anon@test.com",
            "password": "pass123",
            "full_name": "Anon",
            "role": "staff",
        })
        assert response.status_code == 403
