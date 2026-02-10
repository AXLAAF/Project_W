"""Subject service for business logic."""
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.planning.models.subject import Subject
from app.planning.repositories.subject_repository import SubjectRepository
from app.planning.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectNotFoundError(Exception):
    """Raised when a subject is not found."""
    pass


class DuplicateSubjectError(Exception):
    """Raised when subject code already exists."""
    pass


class SubjectService:
    """Service for Subject operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SubjectRepository(session)

    async def create_subject(self, data: SubjectCreate) -> Subject:
        """Create a new subject."""
        # Check for duplicate code
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise DuplicateSubjectError(f"Subject with code '{data.code}' already exists")

        # Validate prerequisites exist
        for prereq_id in data.prerequisite_ids:
            prereq = await self.repo.get_by_id(prereq_id)
            if not prereq:
                raise SubjectNotFoundError(f"Prerequisite with ID {prereq_id} not found")

        return await self.repo.create(data)

    async def get_subject(self, subject_id: int) -> Subject:
        """Get a subject by ID."""
        subject = await self.repo.get_by_id(subject_id)
        if not subject:
            raise SubjectNotFoundError(f"Subject with ID {subject_id} not found")
        return subject

    async def get_subject_by_code(self, code: str) -> Subject:
        """Get a subject by code."""
        subject = await self.repo.get_by_code(code)
        if not subject:
            raise SubjectNotFoundError(f"Subject with code '{code}' not found")
        return subject

    async def list_subjects(
        self,
        department: Optional[str] = None,
        semester: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Subject]:
        """List subjects with optional filters."""
        return await self.repo.get_all(
            department=department,
            semester=semester,
            offset=offset,
            limit=limit,
        )

    async def search_subjects(self, query: str) -> List[Subject]:
        """Search subjects by name or code."""
        return await self.repo.search(query)

    async def update_subject(self, subject_id: int, data: SubjectUpdate) -> Subject:
        """Update a subject."""
        subject = await self.repo.update(subject_id, data)
        if not subject:
            raise SubjectNotFoundError(f"Subject with ID {subject_id} not found")
        return subject

    async def get_prerequisites(self, subject_id: int) -> List[Subject]:
        """Get prerequisites for a subject."""
        # Verify subject exists
        await self.get_subject(subject_id)
        return await self.repo.get_prerequisites(subject_id)

    async def add_prerequisite(
        self, subject_id: int, prerequisite_id: int, is_mandatory: bool = True
    ) -> None:
        """Add a prerequisite to a subject."""
        # Verify both subjects exist
        await self.get_subject(subject_id)
        await self.get_subject(prerequisite_id)

        # Prevent self-referencing
        if subject_id == prerequisite_id:
            raise ValueError("A subject cannot be its own prerequisite")

        await self.repo.add_prerequisite(subject_id, prerequisite_id, is_mandatory)

    async def get_departments(self) -> List[str]:
        """Get all available departments."""
        return await self.repo.get_departments()

    async def check_prerequisites_met(
        self, student_id: int, subject_id: int, passed_subject_ids: List[int]
    ) -> tuple[bool, List[str]]:
        """Check if a student has met all prerequisites for a subject."""
        prerequisites = await self.repo.get_prerequisites(subject_id)
        missing = []

        for prereq in prerequisites:
            if prereq.id not in passed_subject_ids:
                missing.append(f"{prereq.code}: {prereq.name}")

        return len(missing) == 0, missing
