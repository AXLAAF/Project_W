"""
Rule-based Risk Model Adapter.
Implementation of IRiskModel using deterministic rules (heuristic API).
"""
from typing import Dict, List, Any

from app.domain.repositories.risk_model import IRiskModel
from app.domain.value_objects.risk import RiskScore, RiskFactor


class RuleBasedRiskModel(IRiskModel):
    """
    Heuristic-based risk prediction model.
    Does not use heavy ML libraries, but follows the port interface.
    """
    
    VERSION = "v1.0-rules"
    
    async def predict_risk(
        self,
        student_data: Dict[str, Any],
        attendance_stats: Dict[str, float],
        grade_stats: Dict[str, float],
        assignment_stats: Dict[str, float],
    ) -> RiskScore:
        """
        Calculate risk score using weighted heuristics.
        """
        # 1. Attendance Contribution (35%)
        # Low attendance = high risk
        attendance_rate = attendance_stats.get("attendance_rate", 100.0)
        if attendance_rate >= 90:
            attendance_risk = 0
        elif attendance_rate >= 80:
            attendance_risk = 20
        elif attendance_rate >= 70:
            attendance_risk = 50
        else:
            attendance_risk = 100
            
        # 2. Grades Contribution (45%)
        # Low grades = high risk
        avg_grade = grade_stats.get("average_grade", 10.0)
        failing_count = grade_stats.get("failing_count", 0)
        
        if avg_grade >= 8.0:
            grade_risk = 0
        elif avg_grade >= 7.0:
            grade_risk = 20
        elif avg_grade >= 6.0:
            grade_risk = 50
        else:
            grade_risk = 90
            
        # Bonus risk for failing grades
        grade_risk += (failing_count * 10)
        grade_risk = min(100, grade_risk)
        
        # 3. Assignments Contribution (20%)
        # Missing assignments = high risk
        submission_rate = assignment_stats.get("submission_rate", 100.0)
        if submission_rate >= 90:
            assignment_risk = 0
        elif submission_rate >= 70:
            assignment_risk = 30
        else:
            assignment_risk = 80
            
        # Weighted Total (0-100)
        total_risk = (
            (attendance_risk * 0.35) +
            (grade_risk * 0.45) +
            (assignment_risk * 0.20)
        )
        
        return RiskScore(int(total_risk))

    async def analyze_factors(
        self,
        student_data: Dict[str, Any],
        history: List[Any],
    ) -> List[Dict[str, Any]]:
        """Explain the risk factors."""
        # Simple explanation based on logic
        # In a real model, this would use SHAP values or feature importance
        return [
            {"factor": "ATTENDANCE", "weight": 0.35, "description": "Class attendance rate"},
            {"factor": "GRADES", "weight": 0.45, "description": "Average grade and failures"},
            {"factor": "ASSIGNMENTS", "weight": 0.20, "description": "Assignment submission rate"},
        ]

    async def train(self, training_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Dummy training."""
        return {"accuracy": 0.85, "precision": 0.82}
        
    async def get_version(self) -> str:
        return self.VERSION
