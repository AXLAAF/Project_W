"""
SQLAlchemy implementation of Attendance repository.
"""
from typing import Optional, Sequence, List
from datetime import date

from sqlalchemy import select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.risk.attendance import Attendance, AttendanceStats
from app.domain.repositories.risk_repository import IAttendanceRepository
from app.infrastructure.persistence.sqlalchemy.risk_mappers import AttendanceMapper
from app.risk.models.attendance import Attendance as AttendanceModel


class SQLAlchemyAttendanceRepository(IAttendanceRepository):
    """SQLAlchemy implementation of Attendance repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, attendance_id: int) -> Optional[Attendance]:
        """Get an attendance record by ID."""
        result = await self.session.execute(
            select(AttendanceModel).where(AttendanceModel.id == attendance_id)
        )
        model = result.scalar_one_or_none()
        return AttendanceMapper.to_entity(model) if model else None

    async def save(self, attendance: Attendance) -> Attendance:
        """Save a new attendance record."""
        model = AttendanceMapper.to_model(attendance)
        self.session.add(model)
        await self.session.flush()
        return AttendanceMapper.to_entity(model)

    async def update(self, attendance: Attendance) -> Attendance:
        """Update an existing attendance record."""
        # Typically we fetch, update fields, then flush/commit
        # But for this implementation, we can just merge or update if attached
        if attendance.id is None:
            raise ValueError("Cannot update attendance without ID")
            
        result = await self.session.execute(
            select(AttendanceModel).where(AttendanceModel.id == attendance.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Attendance with ID {attendance.id} not found")
            
        AttendanceMapper.update_model(model, attendance)
        await self.session.flush()
        return AttendanceMapper.to_entity(model)

    async def get_by_student_and_date(
        self,
        student_id: int,
        group_id: int,
        class_date: date,
    ) -> Optional[Attendance]:
        """Get attendance for a specific student on a specific date."""
        result = await self.session.execute(
            select(AttendanceModel).where(
                AttendanceModel.student_id == student_id,
                AttendanceModel.group_id == group_id,
                AttendanceModel.class_date == class_date,
            )
        )
        model = result.scalar_one_or_none()
        return AttendanceMapper.to_entity(model) if model else None

    async def list_by_student(
        self,
        student_id: int,
        group_id: int,
    ) -> Sequence[Attendance]:
        """Get all attendance records for a student in a group."""
        result = await self.session.execute(
            select(AttendanceModel)
            .where(
                AttendanceModel.student_id == student_id,
                AttendanceModel.group_id == group_id,
            )
            .order_by(AttendanceModel.class_date)
        )
        models = result.scalars().all()
        return [AttendanceMapper.to_entity(model) for model in models]

    async def list_by_group_and_date(
        self,
        group_id: int,
        class_date: date,
    ) -> Sequence[Attendance]:
        """Get all attendance records for a group on a date."""
        result = await self.session.execute(
            select(AttendanceModel)
            .where(
                AttendanceModel.group_id == group_id,
                AttendanceModel.class_date == class_date,
            )
            .order_by(AttendanceModel.student_id)
        )
        models = result.scalars().all()
        return [AttendanceMapper.to_entity(model) for model in models]

    async def get_stats(
        self,
        student_id: int,
        group_id: int,
    ) -> AttendanceStats:
        """Get attendance statistics for a student."""
        result = await self.session.execute(
            select(
                func.count(AttendanceModel.id).label("total"),
                func.sum(
                    func.cast(AttendanceModel.status == "PRESENT", Integer)
                ).label("present"),
                func.sum(
                    func.cast(AttendanceModel.status == "ABSENT", Integer)
                ).label("absent"),
                func.sum(
                    func.cast(AttendanceModel.status == "LATE", Integer)
                ).label("late"),
                func.sum(
                    func.cast(AttendanceModel.status == "EXCUSED", Integer)
                ).label("excused"),
            ).where(
                AttendanceModel.student_id == student_id,
                AttendanceModel.group_id == group_id,
            )
        )
        row = result.one()
        
        # Helper to safely convert SQL/None result to int
        def safe_int(val):
            return int(val) if val is not None else 0

        return AttendanceStats(
            total_classes=safe_int(row.total),
            present=safe_int(row.present),
            absent=safe_int(row.absent),
            late=safe_int(row.late),
            excused=safe_int(row.excused),
        )
