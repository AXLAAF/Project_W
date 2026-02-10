"""
Calculate Student Risk Use Case.
Orchestrates the calculation and persistence of student risk assessments.
"""
from datetime import date
from typing import Optional

from app.domain.repositories.risk_repository import (
    IRiskAssessmentRepository,
    IAttendanceRepository,
    IGradeRepository,
    IAssignmentRepository,
)
from app.domain.services.risk_score_calculator import RiskScoreCalculator
from app.domain.entities.risk.risk_assessment import RiskAssessment


class CalculateStudentRiskUseCase:
    """Use case for calculating a student's academic risk."""

    def __init__(
        self,
        risk_repo: IRiskAssessmentRepository,
        attendance_repo: IAttendanceRepository,
        grade_repo: IGradeRepository,
        assignment_repo: IAssignmentRepository,
        calculator: Optional[RiskScoreCalculator] = None,
    ):
        self.risk_repo = risk_repo
        self.attendance_repo = attendance_repo
        self.grade_repo = grade_repo
        self.assignment_repo = assignment_repo
        self.calculator = calculator or RiskScoreCalculator()

    async def execute(self, student_id: int, group_id: int) -> RiskAssessment:
        """
        Calculate and save risk assessment for a student.
        """
        # 1. Gather data from repositories
        attendance_stats = await self.attendance_repo.get_stats(student_id, group_id)
        grade_average = await self.grade_repo.get_average(student_id, group_id)
        assignment_stats = await self.assignment_repo.get_submission_stats(student_id, group_id)

        # 2. Calculate risk using domain service
        assessment = self.calculator.assess(
            student_id=student_id,
            group_id=group_id,
            attendance_stats=attendance_stats,
            grade_average=grade_average,
            assignment_stats=assignment_stats,
        )

        # 3. Persist the assessment
        saved_assessment = await self.risk_repo.save(assessment)
        
        return saved_assessment
