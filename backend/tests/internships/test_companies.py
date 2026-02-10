"""
Tests for Companies API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestCompaniesEndpoints:
    """Test suite for companies API."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Register and login a user, return auth headers."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "company_tester@universidad.edu",
                "password": "securepassword123",
                "profile": {
                    "first_name": "Tester",
                    "last_name": "Prácticas",
                },
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "company_tester@universidad.edu",
                "password": "securepassword123",
            },
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_create_company(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new company."""
        response = await client.post(
            "/api/v1/companies",
            headers=auth_headers,
            json={
                "name": "Empresa de Prueba SA",
                "rfc": "EPR123456789",
                "contact_email": "contacto@empresa.com",
                "address": "Calle Principal 123",
                "description": "Empresa de desarrollo de software",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Empresa de Prueba SA"
        assert data["rfc"] == "EPR123456789"
        assert data["is_verified"] is False

    @pytest.mark.asyncio
    async def test_list_companies(self, client: AsyncClient, auth_headers: dict):
        """Test listing companies."""
        # Create a company first
        await client.post(
            "/api/v1/companies",
            headers=auth_headers,
            json={
                "name": "Empresa Lista SA",
                "rfc": "ELS987654321",
                "contact_email": "lista@empresa.com",
            },
        )

        response = await client.get("/api/v1/companies", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_company(self, client: AsyncClient, auth_headers: dict):
        """Test getting a single company."""
        # Create a company
        create_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers,
            json={
                "name": "Empresa Detalle SA",
                "rfc": "EDE111222333",
                "contact_email": "detalle@empresa.com",
            },
        )
        company_id = create_response.json()["id"]

        # Get the company
        response = await client.get(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == company_id
        assert data["name"] == "Empresa Detalle SA"

    @pytest.mark.asyncio
    async def test_update_company(self, client: AsyncClient, auth_headers: dict):
        """Test updating a company."""
        # Create a company
        create_response = await client.post(
            "/api/v1/companies",
            headers=auth_headers,
            json={
                "name": "Empresa Actualizar SA",
                "rfc": "EAC444555666",
                "contact_email": "actualizar@empresa.com",
            },
        )
        company_id = create_response.json()["id"]

        # Update the company
        response = await client.put(
            f"/api/v1/companies/{company_id}",
            headers=auth_headers,
            json={
                "name": "Empresa Actualizada SA",
                "address": "Nueva Dirección 456",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Empresa Actualizada SA"
        assert data["address"] == "Nueva Dirección 456"

    @pytest.mark.asyncio
    async def test_duplicate_rfc_fails(self, client: AsyncClient, auth_headers: dict):
        """Test that duplicate RFC is rejected."""
        # Create first company
        await client.post(
            "/api/v1/companies",
            headers=auth_headers,
            json={
                "name": "Empresa Original",
                "rfc": "DUP777888999",
                "contact_email": "original@empresa.com",
            },
        )

        # Try to create second company with same RFC
        response = await client.post(
            "/api/v1/companies",
            headers=auth_headers,
            json={
                "name": "Empresa Duplicada",
                "rfc": "DUP777888999",
                "contact_email": "duplicada@empresa.com",
            },
        )

        assert response.status_code == 400
