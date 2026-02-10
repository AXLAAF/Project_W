"""
Tests for Reservations API endpoints.
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


class TestReservationsEndpoints:
    """Test suite for reservations API."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Register and login a user, return auth headers."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "reservation_user@universidad.edu",
                "password": "securepassword123",
                "profile": {
                    "first_name": "Usuario",
                    "last_name": "Reservación",
                },
            },
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "reservation_user@universidad.edu",
                "password": "securepassword123",
            },
        )
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    async def resource_id(self, client: AsyncClient, auth_headers: dict) -> int:
        """Create a resource and return its ID."""
        response = await client.post(
            "/api/v1/resources",
            headers=auth_headers,
            json={
                "name": "Sala para Reservaciones",
                "code": f"RES-{datetime.now().timestamp()}",
                "resource_type": "SALA_CONFERENCIAS",
                "capacity": 15,
                "min_reservation_minutes": 30,
                "max_reservation_minutes": 180,
                "advance_booking_days": 14,
            },
        )
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_create_reservation(
        self, client: AsyncClient, auth_headers: dict, resource_id: int
    ):
        """Test creating a new reservation."""
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        response = await client.post(
            "/api/v1/reservations",
            headers=auth_headers,
            json={
                "resource_id": resource_id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "title": "Reunión de equipo",
                "description": "Planeación semanal",
                "attendees_count": 10,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Reunión de equipo"
        assert data["status"] in ["PENDING", "APPROVED"]

    @pytest.mark.asyncio
    async def test_get_my_reservations(
        self, client: AsyncClient, auth_headers: dict, resource_id: int
    ):
        """Test getting user's reservations."""
        # Create a reservation first
        start = datetime.now() + timedelta(days=2)
        end = start + timedelta(hours=1)
        
        await client.post(
            "/api/v1/reservations",
            headers=auth_headers,
            json={
                "resource_id": resource_id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "title": "Mi reservación",
            },
        )

        response = await client.get(
            "/api/v1/reservations/my-reservations",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_cancel_reservation(
        self, client: AsyncClient, auth_headers: dict, resource_id: int
    ):
        """Test cancelling a reservation."""
        # Create reservation
        start = datetime.now() + timedelta(days=3)
        end = start + timedelta(hours=1)
        
        create_response = await client.post(
            "/api/v1/reservations",
            headers=auth_headers,
            json={
                "resource_id": resource_id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "title": "Reservación para cancelar",
            },
        )
        reservation_id = create_response.json()["id"]

        # Cancel reservation
        response = await client.delete(
            f"/api/v1/reservations/{reservation_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_conflict_detection(
        self, client: AsyncClient, auth_headers: dict, resource_id: int
    ):
        """Test that conflicting reservations are rejected."""
        # Create first reservation
        start = datetime.now() + timedelta(days=4)
        end = start + timedelta(hours=2)
        
        await client.post(
            "/api/v1/reservations",
            headers=auth_headers,
            json={
                "resource_id": resource_id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "title": "Primera reservación",
            },
        )

        # Try to create overlapping reservation
        overlap_start = start + timedelta(minutes=30)
        overlap_end = overlap_start + timedelta(hours=1)
        
        response = await client.post(
            "/api/v1/reservations",
            headers=auth_headers,
            json={
                "resource_id": resource_id,
                "start_time": overlap_start.isoformat(),
                "end_time": overlap_end.isoformat(),
                "title": "Reservación conflictiva",
            },
        )

        assert response.status_code == 409  # Conflict

    @pytest.mark.asyncio
    async def test_get_resource_calendar(
        self, client: AsyncClient, auth_headers: dict, resource_id: int
    ):
        """Test getting resource calendar."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        response = await client.get(
            f"/api/v1/reservations/calendar/{resource_id}",
            headers=auth_headers,
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
