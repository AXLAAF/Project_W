"""
Add Prerequisite Use Case.
"""
from app.domain.repositories.subject_repository import ISubjectRepository

class AddPrerequisiteUseCase:
    def __init__(self, subject_repo: ISubjectRepository):
        self.subject_repo = subject_repo

    async def execute(self, subject_id: int, prerequisite_id: int, is_mandatory: bool = True) -> None:
        if subject_id == prerequisite_id:
            raise ValueError("A subject cannot be its own prerequisite")

        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise ValueError(f"Subject with ID {subject_id} not found")

        prereq = await self.subject_repo.get_by_id(prerequisite_id)
        if not prereq:
            raise ValueError(f"Prerequisite with ID {prerequisite_id} not found")

        # Domain logic to add prerequisite
        subject.add_prerequisite(prereq, is_mandatory)
        
        # Save updates
        await self.subject_repo.update(subject)
