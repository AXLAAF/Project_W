"""Risk repository for database operations."""
from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.risk.models.attendance import Attendance
from app.risk.models.grade import PartialGrade
from app.risk.models.assignment import Assignment, AssignmentSubmission, SubmissionStatus
from app.risk.models.risk_assessment import RiskAssessment, RiskLevel


class RiskRepository:
    """Repository for risk-related operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==================== Attendance ====================
    
    async def get_attendance_stats(
        self, student_id: int, group_id: int
    ) -> dict:
        """Get attendance statistics for a student in a group."""
        result = await self.session.execute(
            select(
                func.count(Attendance.id).label("total"),
                func.sum(
                    func.cast(Attendance.status == "PRESENT", Integer)
                ).label("present"),
                func.sum(
                    func.cast(Attendance.status == "ABSENT", Integer)
                ).label("absent"),
                func.sum(
                    func.cast(Attendance.status == "LATE", Integer)
                ).label("late"),
                func.sum(
                    func.cast(Attendance.status == "EXCUSED", Integer)
                ).label("excused"),
            ).where(
                Attendance.student_id == student_id,
                Attendance.group_id == group_id,
            )
        )
        row = result.one()
        total = row.total or 0
        return {
            "total_classes": total,
            "present": row.present or 0,
            "absent": row.absent or 0,
            "late": row.late or 0,
            "excused": row.excused or 0,
            "attendance_rate": (
                ((row.present or 0) + (row.late or 0)) / total * 100
                if total > 0 else 100
            ),
        }

    async def record_attendance(
        self,
        student_id: int,
        group_id: int,
        class_date: date,
        status: str,
        recorded_by: int,
        notes: Optional[str] = None,
    ) -> Attendance:
        """Record attendance for a student."""
        attendance = Attendance(
            student_id=student_id,
            group_id=group_id,
            class_date=class_date,
            status=status,
            recorded_by=recorded_by,
            notes=notes,
        )
        self.session.add(attendance)
        return attendance

    # ==================== Grades ====================
    
    async def get_grades(
        self, student_id: int, group_id: int
    ) -> List[PartialGrade]:
        """Get all grades for a student in a group."""
        result = await self.session.execute(
            select(PartialGrade)
            .where(
                PartialGrade.student_id == student_id,
                PartialGrade.group_id == group_id,
            )
            .order_by(PartialGrade.graded_at)
        )
        return list(result.scalars().all())

    async def get_grade_average(
        self, student_id: int, group_id: int
    ) -> float:
        """Calculate weighted average grade for a student."""
        grades = await self.get_grades(student_id, group_id)
        if not grades:
            return 0.0

        total_weight = sum(float(g.weight) for g in grades)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(
            g.normalized_grade * float(g.weight) for g in grades
        )
        return weighted_sum / total_weight

    async def record_grade(
        self,
        student_id: int,
        group_id: int,
        grade_type: str,
        name: str,
        grade: float,
        recorded_by: int,
        max_grade: float = 10.0,
        weight: float = 1.0,
        feedback: Optional[str] = None,
    ) -> PartialGrade:
        """Record a grade for a student."""
        partial_grade = PartialGrade(
            student_id=student_id,
            group_id=group_id,
            grade_type=grade_type,
            name=name,
            grade=grade,
            max_grade=max_grade,
            weight=weight,
            feedback=feedback,
            graded_at=datetime.now(datetime.now().astimezone().tzinfo),
            recorded_by=recorded_by,
        )
        self.session.add(partial_grade)
        return partial_grade

    # ==================== Assignments ====================
    
    async def get_student_submissions(
        self, student_id: int, group_id: int
    ) -> List[AssignmentSubmission]:
        """Get all assignment submissions for a student in a group."""
        result = await self.session.execute(
            select(AssignmentSubmission)
            .join(Assignment, AssignmentSubmission.assignment_id == Assignment.id)
            .options(selectinload(AssignmentSubmission.assignment))
            .where(
                AssignmentSubmission.student_id == student_id,
                Assignment.group_id == group_id,
            )
            .order_by(Assignment.due_date)
        )
        return list(result.scalars().all())

    async def get_assignment_stats(
        self, student_id: int, group_id: int
    ) -> dict:
        """Get assignment submission statistics."""
        submissions = await self.get_student_submissions(student_id, group_id)
        
        total = len(submissions)
        submitted = sum(1 for s in submissions if s.status in (
            SubmissionStatus.SUBMITTED.value,
            SubmissionStatus.LATE.value,
            SubmissionStatus.GRADED.value,
        ))
        late = sum(1 for s in submissions if s.status == SubmissionStatus.LATE.value)
        missing = sum(1 for s in submissions if s.status == SubmissionStatus.MISSING.value)
        
        return {
            "total_assignments": total,
            "submitted": submitted,
            "late": late,
            "missing": missing,
            "on_time_rate": (submitted - late) / total * 100 if total > 0 else 100,
        }

    # ==================== Risk Assessments ====================
    
    async def get_latest_assessment(
        self, student_id: int, group_id: int
    ) -> Optional[RiskAssessment]:
        """Get the latest risk assessment for a student."""
        result = await self.session.execute(
            select(RiskAssessment)
            .where(
                RiskAssessment.student_id == student_id,
                RiskAssessment.group_id == group_id,
            )
            .order_by(RiskAssessment.assessed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def save_assessment(self, assessment: RiskAssessment) -> RiskAssessment:
        """Save a risk assessment."""
        self.session.add(assessment)
        return assessment

    async def get_at_risk_students(
        self, group_id: int, min_level: RiskLevel = RiskLevel.HIGH
    ) -> List[RiskAssessment]:
        """Get students at or above a risk level in a group."""
        levels = [RiskLevel.CRITICAL.value]
        if min_level in (RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW):
            levels.append(RiskLevel.HIGH.value)
        if min_level in (RiskLevel.MEDIUM, RiskLevel.LOW):
            levels.append(RiskLevel.MEDIUM.value)
        if min_level == RiskLevel.LOW:
            levels.append(RiskLevel.LOW.value)

        # Get latest assessment per student
        subquery = (
            select(
                RiskAssessment.student_id,
                func.max(RiskAssessment.assessed_at).label("max_date"),
            )
            .where(RiskAssessment.group_id == group_id)
            .group_by(RiskAssessment.student_id)
            .subquery()
        )

        result = await self.session.execute(
            select(RiskAssessment)
            .options(selectinload(RiskAssessment.student))
            .join(
                subquery,
                and_(
                    RiskAssessment.student_id == subquery.c.student_id,
                    RiskAssessment.assessed_at == subquery.c.max_date,
                ),
            )
            .where(
                RiskAssessment.group_id == group_id,
                RiskAssessment.risk_level.in_(levels),
            )
            .order_by(RiskAssessment.risk_score.desc())
        )
        return list(result.scalars().all())

    async def get_risk_history(
        self, student_id: int, group_id: int, days: int = 30
    ) -> List[RiskAssessment]:
        """Get risk assessment history for a student."""
        since = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            select(RiskAssessment)
            .where(
                RiskAssessment.student_id == student_id,
                RiskAssessment.group_id == group_id,
                RiskAssessment.assessed_at >= since,
            )
            .order_by(RiskAssessment.assessed_at)
        )
        return list(result.scalars().all())


# Import for type annotation
from sqlalchemy import Integer
