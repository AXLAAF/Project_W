"""
Tests for Auth API v1 (Hexagonal).
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_login_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register
        reg_data = {
            "email": "hex_user@example.com",
            "password": "password123",
            "profile": {
                "first_name": "Hex",
                "last_name": "User",
                "department": "Engineering"
            }
        }
        resp = await ac.post("/api/v1/auth/register", json=reg_data)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "hex_user@example.com"
        assert data["profile"]["first_name"] == "Hex"

        # 2. Login
        login_data = {
            "email": "hex_user@example.com",
            "password": "password123"
        }
        resp = await ac.post("/api/v1/auth/login", json=login_data)
        assert resp.status_code == 200
        tokens = resp.json()
        assert "access_token" in tokens
        access_token = tokens["access_token"]

        # 3. Get Me
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = await ac.get("/api/v1/users/me", headers=headers)
        assert resp.status_code == 200
        me_data = resp.json()
        assert me_data["email"] == "hex_user@example.com"
