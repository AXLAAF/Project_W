"""
Risk module mappers.
Translate between SQLAlchemy ORM models and domain entities.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from app.risk.models.risk_assessment import RiskAssessment as RiskAssessmentModel
from app.risk.models.attendance import Attendance as AttendanceModel
from app.risk.models.grade import PartialGrade as PartialGradeModel
from app.risk.models.assignment import (
    Assignment as AssignmentModel,
    AssignmentSubmission as AssignmentSubmissionModel,
)

from app.domain.entities.risk.risk_assessment import RiskAssessment as RiskAssessmentEntity
from app.domain.entities.risk.attendance import Attendance as AttendanceEntity
from app.domain.entities.risk.partial_grade import PartialGrade as PartialGradeEntity
from app.domain.entities.risk.assignment import (
    Assignment as AssignmentEntity,
    AssignmentSubmission as AssignmentSubmissionEntity,
)
from app.domain.value_objects.risk import (
    RiskScore,
    RiskLevel,
    AttendanceStatus,
    GradeType,
    SubmissionStatus,
)


class RiskAssessmentMapper:
    """Mapper for RiskAssessment entity <-> model."""
    
    @staticmethod
    def to_entity(model: RiskAssessmentModel) -> RiskAssessmentEntity:
        """Convert ORM model to domain entity."""
        return RiskAssessmentEntity(
            id=model.id,
            student_id=model.student_id,
            group_id=model.group_id,
            risk_score=RiskScore(model.risk_score),
            attendance_score=model.attendance_score,
            grades_score=model.grades_score,
            assignments_score=model.assignments_score,
            factor_details=model.factor_details,
            recommendation=model.recommendation,
            assessed_at=model.assessed_at,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: RiskAssessmentEntity) -> RiskAssessmentModel:
        """Convert domain entity to ORM model."""
        return RiskAssessmentModel(
            id=entity.id,
            student_id=entity.student_id,
            group_id=entity.group_id,
            risk_score=entity.risk_score.value,
            risk_level=entity.risk_level.value,
            attendance_score=entity.attendance_score,
            grades_score=entity.grades_score,
            assignments_score=entity.assignments_score,
            factor_details=entity.factor_details,
            recommendation=entity.recommendation,
            assessed_at=entity.assessed_at,
        )


class AttendanceMapper:
    """Mapper for Attendance entity <-> model."""
    
    @staticmethod
    def to_entity(model: AttendanceModel) -> AttendanceEntity:
        """Convert ORM model to domain entity."""
        return AttendanceEntity(
            id=model.id,
            student_id=model.student_id,
            group_id=model.group_id,
            class_date=model.class_date,
            status=AttendanceStatus(model.status),
            notes=model.notes,
            recorded_by=model.recorded_by,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: AttendanceEntity) -> AttendanceModel:
        """Convert domain entity to ORM model."""
        return AttendanceModel(
            id=entity.id,
            student_id=entity.student_id,
            group_id=entity.group_id,
            class_date=entity.class_date,
            status=entity.status.value,
            notes=entity.notes,
            recorded_by=entity.recorded_by,
        )
    
    @staticmethod
    def update_model(model: AttendanceModel, entity: AttendanceEntity) -> None:
        """Update ORM model from domain entity."""
        model.status = entity.status.value
        model.notes = entity.notes
        model.recorded_by = entity.recorded_by


class PartialGradeMapper:
    """Mapper for PartialGrade entity <-> model."""
    
    @staticmethod
    def to_entity(model: PartialGradeModel) -> PartialGradeEntity:
        """Convert ORM model to domain entity."""
        return PartialGradeEntity(
            id=model.id,
            student_id=model.student_id,
            group_id=model.group_id,
            grade_type=GradeType(model.grade_type),
            name=model.name,
            grade=Decimal(str(model.grade)),
            max_grade=Decimal(str(model.max_grade)),
            weight=Decimal(str(model.weight)),
            feedback=model.feedback,
            graded_at=model.graded_at,
            recorded_by=model.recorded_by,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: PartialGradeEntity) -> PartialGradeModel:
        """Convert domain entity to ORM model."""
        return PartialGradeModel(
            id=entity.id,
            student_id=entity.student_id,
            group_id=entity.group_id,
            grade_type=entity.grade_type.value,
            name=entity.name,
            grade=entity.grade,
            max_grade=entity.max_grade,
            weight=entity.weight,
            feedback=entity.feedback,
            graded_at=entity.graded_at,
            recorded_by=entity.recorded_by,
        )
    
    @staticmethod
    def update_model(model: PartialGradeModel, entity: PartialGradeEntity) -> None:
        """Update ORM model from domain entity."""
        model.grade = entity.grade
        model.feedback = entity.feedback
        model.graded_at = entity.graded_at
        model.recorded_by = entity.recorded_by


class AssignmentMapper:
    """Mapper for Assignment entity <-> model."""
    
    @staticmethod
    def to_entity(model: AssignmentModel) -> AssignmentEntity:
        """Convert ORM model to domain entity."""
        return AssignmentEntity(
            id=model.id,
            group_id=model.group_id,
            title=model.title,
            description=model.description,
            due_date=model.due_date,
            max_score=model.max_score,
            weight=model.weight,
            allows_late=model.allows_late,
            late_penalty_percent=model.late_penalty_percent,
            created_by=model.created_by,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: AssignmentEntity) -> AssignmentModel:
        """Convert domain entity to ORM model."""
        return AssignmentModel(
            id=entity.id,
            group_id=entity.group_id,
            title=entity.title,
            description=entity.description,
            due_date=entity.due_date,
            max_score=entity.max_score,
            weight=entity.weight,
            allows_late=entity.allows_late,
            late_penalty_percent=entity.late_penalty_percent,
            created_by=entity.created_by,
        )
    
    @staticmethod
    def update_model(model: AssignmentModel, entity: AssignmentEntity) -> None:
        """Update ORM model from domain entity."""
        model.title = entity.title
        model.description = entity.description
        model.due_date = entity.due_date
        model.max_score = entity.max_score
        model.weight = entity.weight
        model.allows_late = entity.allows_late
        model.late_penalty_percent = entity.late_penalty_percent


class AssignmentSubmissionMapper:
    """Mapper for AssignmentSubmission entity <-> model."""
    
    @staticmethod
    def to_entity(model: AssignmentSubmissionModel) -> AssignmentSubmissionEntity:
        """Convert ORM model to domain entity."""
        return AssignmentSubmissionEntity(
            id=model.id,
            assignment_id=model.assignment_id,
            student_id=model.student_id,
            status=SubmissionStatus(model.status),
            submitted_at=model.submitted_at,
            file_url=model.file_url,
            comments=model.comments,
            score=model.score,
            feedback=model.feedback,
            graded_at=model.graded_at,
            graded_by=model.graded_by,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: AssignmentSubmissionEntity) -> AssignmentSubmissionModel:
        """Convert domain entity to ORM model."""
        return AssignmentSubmissionModel(
            id=entity.id,
            assignment_id=entity.assignment_id,
            student_id=entity.student_id,
            status=entity.status.value,
            submitted_at=entity.submitted_at,
            file_url=entity.file_url,
            comments=entity.comments,
            score=entity.score,
            feedback=entity.feedback,
            graded_at=entity.graded_at,
            graded_by=entity.graded_by,
        )
    
    @staticmethod
    def update_model(
        model: AssignmentSubmissionModel,
        entity: AssignmentSubmissionEntity,
    ) -> None:
        """Update ORM model from domain entity."""
        model.status = entity.status.value
        model.submitted_at = entity.submitted_at
        model.file_url = entity.file_url
        model.comments = entity.comments
        model.score = entity.score
        model.feedback = entity.feedback
        model.graded_at = entity.graded_at
        model.graded_by = entity.graded_by
