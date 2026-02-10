"""
SQLAlchemy implementation of Assignment repository.
"""
from typing import Optional, Sequence, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.risk.assignment import (
    Assignment,
    AssignmentSubmission,
    AssignmentStats,
)
from app.domain.repositories.risk_repository import IAssignmentRepository
from app.domain.value_objects.risk import SubmissionStatus
from app.infrastructure.persistence.sqlalchemy.risk_mappers import (
    AssignmentMapper,
    AssignmentSubmissionMapper,
)
from app.risk.models.assignment import (
    Assignment as AssignmentModel,
    AssignmentSubmission as AssignmentSubmissionModel,
)


class SQLAlchemyAssignmentRepository(IAssignmentRepository):
    """SQLAlchemy implementation of Assignment repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, assignment_id: int) -> Optional[Assignment]:
        """Get an assignment by ID."""
        result = await self.session.execute(
            select(AssignmentModel).where(AssignmentModel.id == assignment_id)
        )
        model = result.scalar_one_or_none()
        return AssignmentMapper.to_entity(model) if model else None

    async def save(self, assignment: Assignment) -> Assignment:
        """Save a new assignment."""
        model = AssignmentMapper.to_model(assignment)
        self.session.add(model)
        await self.session.flush()
        return AssignmentMapper.to_entity(model)

    async def update(self, assignment: Assignment) -> Assignment:
        """Update an existing assignment."""
        if assignment.id is None:
            raise ValueError("Cannot update assignment without ID")
            
        result = await self.session.execute(
            select(AssignmentModel).where(AssignmentModel.id == assignment.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Assignment with ID {assignment.id} not found")
            
        AssignmentMapper.update_model(model, assignment)
        await self.session.flush()
        return AssignmentMapper.to_entity(model)

    async def delete(self, assignment_id: int) -> bool:
        """Delete an assignment."""
        result = await self.session.execute(
            delete(AssignmentModel).where(AssignmentModel.id == assignment_id)
        )
        return result.rowcount > 0

    async def list_by_group(self, group_id: int) -> Sequence[Assignment]:
        """Get all assignments for a group."""
        result = await self.session.execute(
            select(AssignmentModel)
            .where(AssignmentModel.group_id == group_id)
            .order_by(AssignmentModel.due_date)
        )
        models = result.scalars().all()
        return [AssignmentMapper.to_entity(model) for model in models]

    async def get_submission(
        self,
        assignment_id: int,
        student_id: int,
    ) -> Optional[AssignmentSubmission]:
        """Get a student's submission for an assignment."""
        result = await self.session.execute(
            select(AssignmentSubmissionModel)
            .where(
                AssignmentSubmissionModel.assignment_id == assignment_id,
                AssignmentSubmissionModel.student_id == student_id,
            )
            .options(selectinload(AssignmentSubmissionModel.assignment))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
            
        entity = AssignmentSubmissionMapper.to_entity(model)
        # Populate assignment relation if loaded
        if model.assignment:
            entity.assignment = AssignmentMapper.to_entity(model.assignment)
        return entity

    async def save_submission(
        self,
        submission: AssignmentSubmission,
    ) -> AssignmentSubmission:
        """Save a new submission."""
        model = AssignmentSubmissionMapper.to_model(submission)
        self.session.add(model)
        await self.session.flush()
        return AssignmentSubmissionMapper.to_entity(model)

    async def update_submission(
        self,
        submission: AssignmentSubmission,
    ) -> AssignmentSubmission:
        """Update an existing submission."""
        if submission.id is None:
            raise ValueError("Cannot update submission without ID")
            
        result = await self.session.execute(
            select(AssignmentSubmissionModel)
            .where(AssignmentSubmissionModel.id == submission.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Submission with ID {submission.id} not found")
            
        AssignmentSubmissionMapper.update_model(model, submission)
        await self.session.flush()
        return AssignmentSubmissionMapper.to_entity(model)

    async def list_submissions_by_student(
        self,
        student_id: int,
        group_id: int,
    ) -> Sequence[AssignmentSubmission]:
        """Get all submissions for a student in a group."""
        result = await self.session.execute(
            select(AssignmentSubmissionModel)
            .join(AssignmentModel, AssignmentSubmissionModel.assignment_id == AssignmentModel.id)
            .where(
                AssignmentSubmissionModel.student_id == student_id,
                AssignmentModel.group_id == group_id,
            )
            .options(selectinload(AssignmentSubmissionModel.assignment))
            .order_by(AssignmentModel.due_date)
        )
        models = result.scalars().all()
        
        entities = []
        for model in models:
            entity = AssignmentSubmissionMapper.to_entity(model)
            if model.assignment:
                entity.assignment = AssignmentMapper.to_entity(model.assignment)
            entities.append(entity)
        return entities

    async def get_submission_stats(
        self,
        student_id: int,
        group_id: int,
    ) -> AssignmentStats:
        """Get assignment submission statistics for a student."""
        submissions = await self.list_submissions_by_student(student_id, group_id)
        return AssignmentStats.from_submissions(submissions)
