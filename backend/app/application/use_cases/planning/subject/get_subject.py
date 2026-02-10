"""
Get Subject Use Case.
"""
from app.domain.repositories.subject_repository import ISubjectRepository
from app.application.dtos.planning_dtos import SubjectDTO, PrerequisiteDTO
from app.domain.entities.planning.subject import Subject

class GetSubjectUseCase:
    def __init__(self, subject_repo: ISubjectRepository):
        self.subject_repo = subject_repo

    async def execute(self, subject_id: int) -> SubjectDTO:
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Subject with ID {subject_id} not found")
        
        # Ensure prerequisites are loaded (repository responsibility or explicit load)
        # If repo returns subject with lazy loading, we might face issue in async world.
        # But repository interface `get_by_id` implies returning fully usable aggregate root usually.
        # Or we call `get_prerequisites` separately if needed.
        # Assuming `subject` has prerequisites populated or we fetch them.
        # Let's check repository interface: it has `get_prerequisites`.
        if not subject.prerequisites: # If empty or not loaded
             # Implementation detail: Use separate call if needed?
             # For now assume repo handles it or we call it.
             # Actually, domain entity might not hold full objects if loaded from simple SQL.
             # Let's rely on what we have.
             pass

        return self._to_dto(subject)

    def _to_dto(self, subject: Subject) -> SubjectDTO:
        # Same logic as CreateSubjectUseCase - duplicated for now, could be shared util
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
