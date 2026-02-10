"""
List Subjects Use Case.
"""
from typing import List, Optional, Tuple

from app.domain.repositories.subject_repository import ISubjectRepository
from app.application.dtos.planning_dtos import SubjectDTO, PrerequisiteDTO
from app.domain.entities.planning.subject import Subject

class ListSubjectsUseCase:
    def __init__(self, subject_repo: ISubjectRepository):
        self.subject_repo = subject_repo

    async def execute(
        self,
        offset: int = 0,
        limit: int = 50,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[SubjectDTO], int]:
        
        subjects, total = await self.subject_repo.list_all(
            offset=offset,
            limit=limit,
            department=department,
            is_active=is_active,
            search=search
        )
        
        dtos = [self._to_dto(s) for s in subjects]
        return dtos, total

    def _to_dto(self, subject: Subject) -> SubjectDTO:
         # Simplified DTO for list (maybe without prerequisites to save DB hits?)
         # But sticking to consistent DTO for now.
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
