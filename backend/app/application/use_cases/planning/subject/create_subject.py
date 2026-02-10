"""
Create Subject Use Case.
"""
from typing import List

from app.domain.repositories.subject_repository import ISubjectRepository
from app.application.dtos.planning_dtos import CreateSubjectDTO, SubjectDTO, PrerequisiteDTO
from app.domain.entities.planning.subject import Subject
from app.domain.value_objects.subject_code import SubjectCode
from app.domain.value_objects.planning import Credits

class CreateSubjectUseCase:
    def __init__(self, subject_repo: ISubjectRepository):
        self.subject_repo = subject_repo

    async def execute(self, data: CreateSubjectDTO) -> SubjectDTO:
        # Check specific validation rules via domain objects/repository
        existing = await self.subject_repo.get_by_code(data.code)
        if existing:
            raise ValueError(f"Subject with code '{data.code}' already exists")

        # Create entity
        subject = Subject(
            code=SubjectCode(data.code),
            name=data.name,
            credits=Credits(data.credits),
            hours_theory=data.hours_theory,
            hours_practice=data.hours_practice,
            hours_lab=data.hours_lab,
            description=data.description,
            department=data.department,
            semester_suggested=data.semester_suggested,
            # Prerequisites are handled separately or assume implementation handles IDs?
            # Domain Entity manages prerequisites via `add_prerequisite`.
            # For simplicity, we create subject first, then add prerequisites if needed.
        )

        # Save
        saved_subject = await self.subject_repo.save(subject)

        # Handle prerequisites (if passed as IDs)
        # This requires fetching prereq subjects and adding them.
        # This logic should be in the UseCase.
        if data.prerequisite_ids:
            for prereq_id in data.prerequisite_ids:
                prereq = await self.subject_repo.get_by_id(prereq_id)
                if not prereq:
                    raise ValueError(f"Prerequisite ID {prereq_id} not found")
                # Domain logic to add prerequisite
                saved_subject.add_prerequisite(prereq) # Assume this method exists on Entity
                # We might need to save relationship
                # If repository handles relationship update on save, we save again
            
            saved_subject = await self.subject_repo.update(saved_subject)

        # Transform to DTO
        return self._to_dto(saved_subject)

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
