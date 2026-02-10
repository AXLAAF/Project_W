"""
Tests for Internships API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestInternshipsEndpoints:
    """Test suite for internships API."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Register and login a user, return auth headers."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "intern@universidad.edu",
                "password": "securepassword123",
                "profile": {
                    "first_name": "Practicante",
                    "last_name": "Activo",
                    "student_id": "A09876543",
                },
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "intern@universidad.edu",
                "password": "securepassword123",
            },
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_get_active_internship_none(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting active internship when none exists."""
        response = await client.get(
            "/api/v1/internships/active",
            headers=auth_headers,
        )

        assert response.status_code == 200
        # Should return null or empty when no active internship
        data = response.json()
        assert data is None or data == {}

    @pytest.mark.asyncio
    async def test_get_my_internships_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting user's internships when none exist."""
        response = await client.get(
            "/api/v1/internships/my-internships",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
