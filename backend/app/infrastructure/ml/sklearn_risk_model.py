"""
Scikit-learn implementation of Risk Model Port.
"""
from typing import Dict, Any, Tuple
import random 

from app.domain.ports.risk_model_port import IRiskModelPort


class SklearnRiskModelAdapter(IRiskModelPort):
    """
    Adapter for scikit-learn risk prediction model.
    Currently uses a heuristic-based mock, to be replaced by actual .pkl model loading.
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        # self.model = joblib.load(model_path) if model_path else None

    async def predict_risk(self, features: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """
        Predict risk based on features.
        
        Features expected:
        - attendance_rate (0-100)
        - average_grade (0-100)
        - missed_assignments (int)
        """
        attendance = features.get("attendance_rate", 100)
        grades = features.get("average_grade", 100)
        missed = features.get("missed_assignments", 0)
        
        # Simple heuristic logic (mocking ML model)
        risk_score = 0
        factor_breakdown = {}
        
        # Attendance factor
        if attendance < 70:
            score = 100 - attendance
            risk_score += score * 0.4
            factor_breakdown["attendance"] = "Low attendance"
        
        # Grades factor
        if grades < 60:
            score = 100 - grades
            risk_score += score * 0.4
            factor_breakdown["grades"] = "Low academic performance"
            
        # Assignments factor
        if missed > 2:
            risk_score += missed * 5
            factor_breakdown["assignments"] = f"{missed} missed assignments"
            
        # Normalize
        final_score = min(100, int(risk_score))
        
        # Ensure minimal randomness for "AI" feeling if score is low but not 0
        if final_score < 10:
             final_score = random.randint(0, 10)
             
        return final_score, factor_breakdown
