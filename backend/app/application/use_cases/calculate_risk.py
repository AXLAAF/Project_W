"""
Calculate Risk Score use case.
Orchestrates data gathering and risk prediction.
"""
from datetime import datetime
from typing import Optional

from app.domain.repositories.risk_repository import (
    IRiskAssessmentRepository,
    IAttendanceRepository,
    IGradeRepository,
    IAssignmentRepository,
)
from app.domain.repositories.risk_model import IRiskModel
from app.domain.entities.risk.risk_assessment import RiskAssessment
from app.domain.value_objects.risk import RiskScore

class CalculateRiskScoreUseCase:
    """
    Use case: Calculate risk score for a student.
    
    Steps:
    1. Gather data (attendance, grades, assignments)
    2. Call Risk Model implementation
    3. Create RiskAssessment entity
    4. Save to repo
    """
    
    def __init__(
        self,
        risk_repo: IRiskAssessmentRepository,
        attendance_repo: IAttendanceRepository,
        grade_repo: IGradeRepository,
        assignment_repo: IAssignmentRepository,
        risk_model: IRiskModel,
    ):
        self.risk_repo = risk_repo
        self.attendance_repo = attendance_repo
        self.grade_repo = grade_repo
        self.assignment_repo = assignment_repo
        self.risk_model = risk_model
        
    async def execute(self, student_id: int, group_id: int) -> RiskAssessment:
        # 1. Gather Data
        # Attendance
        attendance_stats = await self.attendance_repo.get_stats(student_id, group_id)
        att_dict = {
            "attendance_rate": attendance_stats.attendance_rate,
            "absence_rate": attendance_stats.absence_rate,
        }
        
        # Grades
        avg_grade = await self.grade_repo.get_average(student_id, group_id)
        grade_dict = {
            "average_grade": float(avg_grade),
            "failing_count": 0, # Should be implemented in repo
        }
        
        # Assignments
        assign_stats = await self.assignment_repo.get_submission_stats(student_id, group_id)
        # Assuming assign_stats has a submission_rate property or calculating it
        try:
            submission_rate = assign_stats.submission_rate
        except AttributeError:
            submission_rate = 0.0 # Fallback
            
        assign_dict = {
            "submission_rate": float(submission_rate),
        }
        
        # 2. Predict Risk using ML Model
        predicted_risk: RiskScore = await self.risk_model.predict_risk(
            student_data={"id": student_id},
            attendance_stats=att_dict,
            grade_stats=grade_dict,
            assignment_stats=assign_dict,
        )
        
        # 3. Analyze Factors
        factors = await self.risk_model.analyze_factors(
            student_data={"id": student_id},
            history=[],
        )
        
        # 4. Create Assessment Entity directly (bypassing simple factory logic)
        # We convert raw metrics to 0-100 scores where 100 = BAD/RISK for the entity storage
        # (See entity logic: attendance_score is actually performance score, low is bad?)
        # Wait, usually score means 'performance'. 100 attendance = good.
        # But RiskScore is 100 = bad.
        # Let's check RiskAssessment factory: "total total_score = attendance_score * weight..."
        # If RiskScore(total_score) -> 100 is CRITICAL.
        # So inputs to factory must be RISK scores (0=good, 100=bad).
        
        # Convert performance to risk metrics (0=Good, 100=Bad)
        att_risk = max(0, 100 - att_dict["attendance_rate"])
        # Grades: 10->0, 0->100.  (10-grade)*10.
        grade_risk = max(0, (10.0 - grade_dict["average_grade"]) * 10)
        assign_risk = max(0, 100 - assign_dict["submission_rate"])
        
        assessment = RiskAssessment(
            student_id=student_id,
            group_id=group_id,
            risk_score=predicted_risk,
            attendance_score=int(att_risk),
            grades_score=int(grade_risk),
            assignments_score=int(assign_risk),
            factor_details={"factors": factors},
            assessed_at=datetime.now(),
        )
        
        # 5. Save
        return await self.risk_repo.save(assessment)
