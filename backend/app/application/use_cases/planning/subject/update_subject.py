"""
Update Subject Use Case.
"""
from typing import Optional

from app.domain.repositories.subject_repository import ISubjectRepository
from app.application.dtos.planning_dtos import SubjectDTO, UpdateSubjectDTO, PrerequisiteDTO
from app.domain.entities.planning.subject import Subject
from app.domain.value_objects.planning import Credits

class UpdateSubjectUseCase:
    def __init__(self, subject_repo: ISubjectRepository):
        self.subject_repo = subject_repo

    async def execute(self, subject_id: int, data: UpdateSubjectDTO) -> SubjectDTO:
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Subject with ID {subject_id} not found")

        # Update fields
        if data.name is not None:
            subject.name = data.name
        if data.credits is not None:
            subject.credits = Credits(data.credits)
        if data.hours_theory is not None:
            subject.hours_theory = data.hours_theory
        if data.hours_practice is not None:
            subject.hours_practice = data.hours_practice
        if data.hours_lab is not None:
            subject.hours_lab = data.hours_lab
        if data.description is not None:
            subject.description = data.description
        if data.department is not None:
            subject.department = data.department
        if data.semester_suggested is not None:
            subject.semester_suggested = data.semester_suggested
        if data.is_active is not None:
            subject.is_active = data.is_active

        updated_subject = await self.subject_repo.update(subject)
        return self._to_dto(updated_subject)

    def _to_dto(self, subject: Subject) -> SubjectDTO:
        prereqs_dtos = [
            PrerequisiteDTO(
                id=p.subject.id,
                code=p.subject.code.value,
                name=p.subject.name,
                credits=p.subject.credits.value,
                is_mandatory=p.is_mandatory
            ) for p in subject.prerequisites if p.subject
        ]
        return SubjectDTO(
            id=subject.id,
            code=subject.code.value,
            name=subject.name,
            credits=subject.credits.value,
            hours_theory=subject.hours_theory,
            hours_practice=subject.hours_practice,
            hours_lab=subject.hours_lab,
            total_hours=subject.total_hours,
            description=subject.description,
            department=subject.department,
            semester_suggested=subject.semester_suggested,
            is_active=subject.is_active,
            prerequisites=prereqs_dtos,
            created_at=subject.created_at,
            updated_at=subject.updated_at,
        )
