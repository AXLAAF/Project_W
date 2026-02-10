"""
Tests for Resources API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestResourcesEndpoints:
    """Test suite for resources API."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Register and login a user, return auth headers."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "resource_tester@universidad.edu",
                "password": "securepassword123",
                "profile": {
                    "first_name": "Tester",
                    "last_name": "Recursos",
                },
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "resource_tester@universidad.edu",
                "password": "securepassword123",
            },
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_create_resource(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new resource."""
        response = await client.post(
            "/api/v1/resources",
            headers=auth_headers,
            json={
                "name": "Sala de Conferencias A",
                "code": "CONF-A",
                "resource_type": "SALA_CONFERENCIAS",
                "location": "Edificio Principal, Piso 2",
                "capacity": 20,
                "min_reservation_minutes": 30,
                "max_reservation_minutes": 180,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Sala de Conferencias A"
        assert data["code"] == "CONF-A"
        assert data["status"] == "DISPONIBLE"

    @pytest.mark.asyncio
    async def test_list_resources(self, client: AsyncClient, auth_headers: dict):
        """Test listing resources."""
        # Create a resource first
        await client.post(
            "/api/v1/resources",
            headers=auth_headers,
            json={
                "name": "Laboratorio de Cómputo",
                "code": "LAB-01",
                "resource_type": "LABORATORIO",
                "capacity": 30,
            },
        )

        response = await client.get("/api/v1/resources", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_resource(self, client: AsyncClient, auth_headers: dict):
        """Test getting a single resource."""
        # Create resource
        create_response = await client.post(
            "/api/v1/resources",
            headers=auth_headers,
            json={
                "name": "Auditorio Principal",
                "code": "AUD-01",
                "resource_type": "AUDITORIO",
                "capacity": 100,
            },
        )
        resource_id = create_response.json()["id"]

        # Get resource
        response = await client.get(
            f"/api/v1/resources/{resource_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resource_id
        assert data["name"] == "Auditorio Principal"

    @pytest.mark.asyncio
    async def test_update_resource(self, client: AsyncClient, auth_headers: dict):
        """Test updating a resource."""
        # Create resource
        create_response = await client.post(
            "/api/v1/resources",
            headers=auth_headers,
            json={
                "name": "Sala Estudio Original",
                "code": "EST-01",
                "resource_type": "SALA_ESTUDIO",
            },
        )
        resource_id = create_response.json()["id"]

        # Update resource
        response = await client.put(
            f"/api/v1/resources/{resource_id}",
            headers=auth_headers,
            json={
                "name": "Sala Estudio Renovada",
                "capacity": 10,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Sala Estudio Renovada"
        assert data["capacity"] == 10

    @pytest.mark.asyncio
    async def test_filter_resources_by_type(self, client: AsyncClient, auth_headers: dict):
        """Test filtering resources by type."""
        # Create resources
        await client.post(
            "/api/v1/resources",
            headers=auth_headers,
            json={"name": "Lab Química", "code": "LAB-QUI", "resource_type": "LABORATORIO"},
        )
        await client.post(
            "/api/v1/resources",
            headers=auth_headers,
            json={"name": "Sala Juntas", "code": "JNT-01", "resource_type": "SALA_CONFERENCIAS"},
        )

        # Filter by LABORATORIO
        response = await client.get(
            "/api/v1/resources",
            headers=auth_headers,
            params={"resource_type": "LABORATORIO"},
        )

        assert response.status_code == 200
        data = response.json()
        assert all(r["resource_type"] == "LABORATORIO" for r in data)

    @pytest.mark.asyncio
    async def test_duplicate_code_fails(self, client: AsyncClient, auth_headers: dict):
        """Test that duplicate code is rejected."""
        # Create first resource
        await client.post(
            "/api/v1/resources",
            headers=auth_headers,
            json={"name": "Recurso Original", "code": "DUP-001", "resource_type": "OTRO"},
        )

        # Try to create with same code
        response = await client.post(
            "/api/v1/resources",
            headers=auth_headers,
            json={"name": "Recurso Duplicado", "code": "DUP-001", "resource_type": "OTRO"},
        )

        assert response.status_code == 400
