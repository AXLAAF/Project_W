"""
Tests for Positions API endpoints.
"""
import pytest
from httpx import AsyncClient


class TestPositionsEndpoints:
    """Test suite for positions API."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Register and login a user, return auth headers."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "position_tester@universidad.edu",
                "password": "securepassword123",
                "profile": {
                    "first_name": "Tester",
                    "last_name": "Posiciones",
                },
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "position_tester@universidad.edu",
                "password": "securepassword123",
            },
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    async def company_id(self, client: AsyncClient, auth_headers: dict) -> int:
        """Create a company and return its ID."""
        response = await client.post(
            "/api/v1/companies",
            headers=auth_headers,
            json={
                "name": "Empresa para Posiciones SA",
                "rfc": "EPS111222333",
                "contact_email": "posiciones@empresa.com",
            },
        )
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_create_position(
        self, client: AsyncClient, auth_headers: dict, company_id: int
    ):
        """Test creating a new position."""
        response = await client.post(
            "/api/v1/internships/positions",
            headers=auth_headers,
            json={
                "company_id": company_id,
                "title": "Desarrollador Backend Jr",
                "description": "Desarrollo de APIs con Python y FastAPI",
                "requirements": "Python, SQL, Git",
                "benefits": "Horario flexible, capacitación",
                "duration_months": 6,
                "modality": "HIBRIDO",
                "location": "Monterrey, NL",
                "capacity": 3,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Desarrollador Backend Jr"
        assert data["modality"] == "HIBRIDO"
        assert data["capacity"] == 3
        assert data["filled_count"] == 0

    @pytest.mark.asyncio
    async def test_list_positions(
        self, client: AsyncClient, auth_headers: dict, company_id: int
    ):
        """Test listing positions."""
        # Create a position
        await client.post(
            "/api/v1/internships/positions",
            headers=auth_headers,
            json={
                "company_id": company_id,
                "title": "QA Tester Jr",
                "description": "Testing de aplicaciones",
                "duration_months": 4,
                "modality": "PRESENCIAL",
                "capacity": 2,
            },
        )

        response = await client.get(
            "/api/v1/internships/positions",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_filter_positions_by_modality(
        self, client: AsyncClient, auth_headers: dict, company_id: int
    ):
        """Test filtering positions by modality."""
        # Create positions with different modalities
        await client.post(
            "/api/v1/internships/positions",
            headers=auth_headers,
            json={
                "company_id": company_id,
                "title": "Posición Remota",
                "description": "Trabajo 100% remoto",
                "duration_months": 6,
                "modality": "REMOTO",
                "capacity": 5,
            },
        )

        response = await client.get(
            "/api/v1/internships/positions",
            headers=auth_headers,
            params={"modality": "REMOTO"},
        )

        assert response.status_code == 200
        data = response.json()
        assert all(pos["modality"] == "REMOTO" for pos in data)

    @pytest.mark.asyncio
    async def test_get_position(
        self, client: AsyncClient, auth_headers: dict, company_id: int
    ):
        """Test getting a single position."""
        # Create position
        create_response = await client.post(
            "/api/v1/internships/positions",
            headers=auth_headers,
            json={
                "company_id": company_id,
                "title": "Posición Detalle",
                "description": "Para ver detalle",
                "duration_months": 3,
                "modality": "PRESENCIAL",
                "capacity": 1,
            },
        )
        position_id = create_response.json()["id"]

        # Get position
        response = await client.get(
            f"/api/v1/internships/positions/{position_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == position_id
        assert data["title"] == "Posición Detalle"

    @pytest.mark.asyncio
    async def test_update_position(
        self, client: AsyncClient, auth_headers: dict, company_id: int
    ):
        """Test updating a position."""
        # Create position
        create_response = await client.post(
            "/api/v1/internships/positions",
            headers=auth_headers,
            json={
                "company_id": company_id,
                "title": "Posición Original",
                "description": "Descripción original",
                "duration_months": 4,
                "modality": "PRESENCIAL",
                "capacity": 2,
            },
        )
        position_id = create_response.json()["id"]

        # Update position
        response = await client.put(
            f"/api/v1/internships/positions/{position_id}",
            headers=auth_headers,
            json={
                "title": "Posición Actualizada",
                "capacity": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Posición Actualizada"
        assert data["capacity"] == 5
