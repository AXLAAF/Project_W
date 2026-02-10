import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.domain.entities.user import User
from app.interfaces.api.v1.risk import router
from app.interfaces.dependencies import get_current_active_user, get_risk_repository
from app.domain.repositories.risk_repository import IRiskRepository
from app.domain.entities.risk.risk_assessment import RiskAssessment

# Mock user
mock_user = User(
    id=1,
    email="professor@test.com",
    is_active=True,
    roles=["PROFESOR"]
)

# Mock Repository
class MockRiskRepository(IRiskRepository):
    async def save(self, assessment: RiskAssessment) -> RiskAssessment:
        assessment.id = 999
        return assessment
    
    async def get_by_student_and_group(self, student_id: int, group_id: int):
        return None
    
    async def get_history_by_student(self, student_id: int, limit: int = 10):
        return []
        
    async def get_high_risk_students(self, group_id: int):
        return []

async def override_get_current_active_user():
    return mock_user

def override_get_risk_repository():
    return MockRiskRepository()

app.dependency_overrides[get_current_active_user] = override_get_current_active_user
app.dependency_overrides[get_risk_repository] = override_get_risk_repository

client = TestClient(app)

def test_calculate_risk():
    print("Testing Risk Calculation Endpoint...")
    
    # Payload
    payload = {
        "student_id": 123,
        "group_id": 456,
        "attendance_rate": 60.0,  # Should trigger High Risk
        "average_grade": 50.0,
        "missed_assignments": 3
    }
    
    try:
        response = client.post("/api/v1/risk/calculate", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Risk Score: {data['risk_score']}")
            print(f"Risk Level: {data['risk_level']}")
            print(f"Details: {data}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_calculate_risk()
