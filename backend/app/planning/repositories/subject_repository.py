"""Subject repository for database operations."""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.planning.models.subject import Subject, SubjectPrerequisite
from app.planning.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectRepository:
    """Repository for Subject operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: SubjectCreate) -> Subject:
        """Create a new subject."""
        subject = Subject(
            code=data.code,
            name=data.name,
            credits=data.credits,
            hours_theory=data.hours_theory,
            hours_practice=data.hours_practice,
            hours_lab=data.hours_lab,
            description=data.description,
            department=data.department,
            semester_suggested=data.semester_suggested,
        )
        self.session.add(subject)
        await self.session.flush()

        # Add prerequisites
        for prereq_id in data.prerequisite_ids:
            prereq = SubjectPrerequisite(
                subject_id=subject.id,
                prerequisite_id=prereq_id,
            )
            self.session.add(prereq)

        return subject

    async def get_by_id(self, subject_id: int) -> Optional[Subject]:
        """Get subject by ID."""
        result = await self.session.execute(
            select(Subject)
            .options(selectinload(Subject.prerequisites).selectinload(SubjectPrerequisite.prerequisite))
            .where(Subject.id == subject_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Subject]:
        """Get subject by code."""
        result = await self.session.execute(
            select(Subject).where(Subject.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        department: Optional[str] = None,
        semester: Optional[int] = None,
        is_active: bool = True,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Subject]:
        """Get all subjects with optional filters."""
        query = select(Subject).where(Subject.is_active == is_active)

        if department:
            query = query.where(Subject.department == department)
        if semester:
            query = query.where(Subject.semester_suggested == semester)

        query = query.order_by(Subject.code).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search(self, query: str, limit: int = 20) -> List[Subject]:
        """Search subjects by name or code."""
        search_query = f"%{query}%"
        result = await self.session.execute(
            select(Subject)
            .where(
                Subject.is_active == True,
                (Subject.name.ilike(search_query) | Subject.code.ilike(search_query))
            )
            .order_by(Subject.code)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, subject_id: int, data: SubjectUpdate) -> Optional[Subject]:
        """Update a subject."""
        subject = await self.get_by_id(subject_id)
        if not subject:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(subject, key, value)

        return subject

    async def add_prerequisite(
        self, subject_id: int, prerequisite_id: int, is_mandatory: bool = True
    ) -> SubjectPrerequisite:
        """Add a prerequisite to a subject."""
        prereq = SubjectPrerequisite(
            subject_id=subject_id,
            prerequisite_id=prerequisite_id,
            is_mandatory=is_mandatory,
        )
        self.session.add(prereq)
        return prereq

    async def remove_prerequisite(self, subject_id: int, prerequisite_id: int) -> bool:
        """Remove a prerequisite from a subject."""
        result = await self.session.execute(
            select(SubjectPrerequisite).where(
                SubjectPrerequisite.subject_id == subject_id,
                SubjectPrerequisite.prerequisite_id == prerequisite_id,
            )
        )
        prereq = result.scalar_one_or_none()
        if prereq:
            await self.session.delete(prereq)
            return True
        return False

    async def get_prerequisites(self, subject_id: int) -> List[Subject]:
        """Get all prerequisites for a subject."""
        result = await self.session.execute(
            select(Subject)
            .join(SubjectPrerequisite, SubjectPrerequisite.prerequisite_id == Subject.id)
            .where(SubjectPrerequisite.subject_id == subject_id)
        )
        return list(result.scalars().all())

    async def get_departments(self) -> List[str]:
        """Get all unique departments."""
        result = await self.session.execute(
            select(Subject.department)
            .where(Subject.department.isnot(None))
            .distinct()
            .order_by(Subject.department)
        )
        return [row[0] for row in result.all() if row[0]]
