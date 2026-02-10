"""
Tests for Applications API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestApplicationsEndpoints:
    """Test suite for applications API."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Register and login a user, return auth headers."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "applicant@universidad.edu",
                "password": "securepassword123",
                "profile": {
                    "first_name": "Estudiante",
                    "last_name": "Aplicante",
                    "student_id": "A01234567",
                },
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "applicant@universidad.edu",
                "password": "securepassword123",
            },
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    async def position_id(self, client: AsyncClient, auth_headers: dict) -> int:
        """Create a company and position, return position ID."""
        # Create company
        company_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers,
            json={
                "name": "Empresa Aplicaciones SA",
                "rfc": "EAP444555666",
                "contact_email": "aplicaciones@empresa.com",
            },
        )
        company_id = company_response.json()["id"]

        # Create position
        position_response = await client.post(
            "/api/v1/internships/positions",
            headers=auth_headers,
            json={
                "company_id": company_id,
                "title": "Desarrollador Full Stack",
                "description": "Desarrollo web completo",
                "duration_months": 6,
                "modality": "HIBRIDO",
                "capacity": 2,
            },
        )
        return position_response.json()["id"]

    @pytest.mark.asyncio
    async def test_apply_to_position(
        self, client: AsyncClient, auth_headers: dict, position_id: int
    ):
        """Test applying to a position."""
        response = await client.post(
            "/api/v1/internships/apply",
            headers=auth_headers,
            json={
                "position_id": position_id,
                "cover_letter": "Estoy muy interesado en esta oportunidad...",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["position_id"] == position_id
        assert data["status"] == "PENDING"

    @pytest.mark.asyncio
    async def test_get_my_applications(
        self, client: AsyncClient, auth_headers: dict, position_id: int
    ):
        """Test getting user's applications."""
        # Apply to position
        await client.post(
            "/api/v1/internships/apply",
            headers=auth_headers,
            json={"position_id": position_id},
        )

        # Get my applications
        response = await client.get(
            "/api/v1/internships/my-applications",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_cancel_application(
        self, client: AsyncClient, auth_headers: dict, position_id: int
    ):
        """Test cancelling an application."""
        # Apply to position
        apply_response = await client.post(
            "/api/v1/internships/apply",
            headers=auth_headers,
            json={"position_id": position_id},
        )
        application_id = apply_response.json()["id"]

        # Cancel application
        response = await client.delete(
            f"/api/v1/internships/applications/{application_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_cannot_apply_twice(
        self, client: AsyncClient, auth_headers: dict, position_id: int
    ):
        """Test that user cannot apply to the same position twice."""
        # First application
        first_response = await client.post(
            "/api/v1/internships/apply",
            headers=auth_headers,
            json={"position_id": position_id},
        )
        assert first_response.status_code == 201

        # Second application should fail
        second_response = await client.post(
            "/api/v1/internships/apply",
            headers=auth_headers,
            json={"position_id": position_id},
        )
        assert second_response.status_code == 400
