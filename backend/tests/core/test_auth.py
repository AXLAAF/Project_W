"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test suite for authentication API."""

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        """Test user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@universidad.edu",
                "password": "securepassword123",
                "profile": {
                    "first_name": "Juan",
                    "last_name": "Pérez",
                    "student_id": "A01234567",
                    "program": "Ingeniería en Sistemas",
                },
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@universidad.edu"
        assert "ALUMNO" in data["roles"]
        assert data["profile"]["first_name"] == "Juan"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email fails."""
        user_data = {
            "email": "duplicate@universidad.edu",
            "password": "securepassword123",
            "profile": {
                "first_name": "Juan",
                "last_name": "Pérez",
            },
        }
        
        # First registration should succeed
        response1 = await client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration should fail
        response2 = await client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Test successful login."""
        # First register a user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@universidad.edu",
                "password": "securepassword123",
                "profile": {
                    "first_name": "María",
                    "last_name": "García",
                },
            },
        )
        
        # Then login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@universidad.edu",
                "password": "securepassword123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@universidad.edu",
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient):
        """Test getting current user profile."""
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "profile@universidad.edu",
                "password": "securepassword123",
                "profile": {
                    "first_name": "Carlos",
                    "last_name": "López",
                },
            },
        )
        
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "profile@universidad.edu",
                "password": "securepassword123",
            },
        )
        token = login_response.json()["access_token"]
        
        # Get current user
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "profile@universidad.edu"
        assert data["profile"]["first_name"] == "Carlos"
