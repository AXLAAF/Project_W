"""
End-to-end tests for complete user workflows.
"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient


class TestCompleteUserWorkflows:
    """End-to-end tests for complete user journeys across modules."""

    @pytest.fixture
    async def student_auth(self, client: AsyncClient) -> dict:
        """Register and login a student user."""
        email = f"student_{datetime.now().timestamp()}@universidad.edu"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "student123",
                "profile": {"first_name": "Estudiante", "last_name": "Prueba"},
            },
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "student123"},
        )
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    @pytest.mark.asyncio
    async def test_complete_internship_workflow(
        self, client: AsyncClient, student_auth: dict
    ):
        """Test complete internship workflow from company to application."""
        # 1. Admin creates a company
        company_response = await client.post(
            "/api/v1/internships/companies",
            headers=student_auth,
            json={
                "name": "Tech Corp E2E",
                "rfc": "TCE123456789",
                "industry": "Tecnología",
                "contact_email": "rh@techcorp.com",
                "address": "Av. Principal 123",
                "is_active": True,
            },
        )
        assert company_response.status_code == 201
        company_id = company_response.json()["id"]

        # 2. Create a position in the company
        position_response = await client.post(
            "/api/v1/internships/positions",
            headers=student_auth,
            json={
                "company_id": company_id,
                "title": "Desarrollador Full Stack",
                "description": "Práctica en desarrollo web",
                "requirements": "Python, JavaScript",
                "modality": "HIBRIDO",
                "hours_per_week": 20,
                "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "slots_available": 3,
            },
        )
        assert position_response.status_code == 201
        position_id = position_response.json()["id"]

        # 3. Student applies to the position
        application_response = await client.post(
            "/api/v1/internships/applications",
            headers=student_auth,
            json={
                "position_id": position_id,
                "cover_letter": "Me interesa esta posición porque tengo experiencia en desarrollo web.",
            },
        )
        assert application_response.status_code == 201
        assert application_response.json()["status"] == "ENVIADA"

        # 4. Get user applications
        my_apps = await client.get(
            "/api/v1/internships/applications/mine",
            headers=student_auth,
        )
        assert my_apps.status_code == 200
        assert len(my_apps.json()) >= 1

    @pytest.mark.asyncio
    async def test_complete_reservation_workflow(
        self, client: AsyncClient, student_auth: dict
    ):
        """Test complete reservation workflow from resource creation to check-out."""
        # 1. Create a resource
        resource_response = await client.post(
            "/api/v1/resources",
            headers=student_auth,
            json={
                "name": "Sala E2E Test",
                "code": f"E2E-{datetime.now().timestamp()}",
                "resource_type": "SALA_CONFERENCIAS",
                "capacity": 10,
                "requires_approval": False,
            },
        )
        assert resource_response.status_code == 201
        resource_id = resource_response.json()["id"]

        # 2. Create a reservation
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=2)
        
        reservation_response = await client.post(
            "/api/v1/reservations",
            headers=student_auth,
            json={
                "resource_id": resource_id,
                "start_time": start.isoformat(),
                "end_time": end.isoformat(),
                "title": "Sesión de estudio E2E",
            },
        )
        assert reservation_response.status_code == 201
        reservation_id = reservation_response.json()["id"]
        assert reservation_response.json()["status"] == "APPROVED"

        # 3. Check in to reservation
        checkin = await client.post(
            f"/api/v1/reservations/{reservation_id}/check-in",
            headers=student_auth,
        )
        assert checkin.status_code == 200
        assert checkin.json()["checked_in_at"] is not None

        # 4. Check out of reservation
        checkout = await client.post(
            f"/api/v1/reservations/{reservation_id}/check-out",
            headers=student_auth,
        )
        assert checkout.status_code == 200
        assert checkout.json()["status"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_planning_workflow(self, client: AsyncClient, student_auth: dict):
        """Test academic planning workflow."""
        subjects = await client.get("/api/v1/planning/subjects", headers=student_auth)
        assert subjects.status_code == 200

        profile = await client.get("/api/v1/auth/me", headers=student_auth)
        assert profile.status_code == 200


class TestCrossModuleIntegration:
    """Tests for integration between different modules."""

    @pytest.fixture
    async def auth_headers(self, client: AsyncClient) -> dict:
        """Create authenticated user."""
        email = f"cross_module_{datetime.now().timestamp()}@universidad.edu"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "crosstest123",
                "profile": {"first_name": "Cross", "last_name": "Module"},
            },
        )
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "crosstest123"},
        )
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    @pytest.mark.asyncio
    async def test_user_across_modules(self, client: AsyncClient, auth_headers: dict):
        """Test that the same user can interact with all modules."""
        subjects = await client.get("/api/v1/planning/subjects", headers=auth_headers)
        assert subjects.status_code == 200

        risk = await client.get("/api/v1/risk/assessment", headers=auth_headers)
        assert risk.status_code in [200, 404]

        resources = await client.get("/api/v1/resources", headers=auth_headers)
        assert resources.status_code == 200

        companies = await client.get("/api/v1/internships/companies", headers=auth_headers)
        assert companies.status_code == 200

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
