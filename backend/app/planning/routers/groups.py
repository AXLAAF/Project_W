"""Groups API router."""
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db
from app.dependencies import get_current_user, require_role
from app.core.models.user import User
from app.planning.schemas.group import GroupCreate, GroupRead, GroupWithSchedules
from app.planning.repositories.group_repository import GroupRepository

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=List[GroupWithSchedules])
async def list_groups(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    period_id: Optional[int] = Query(None, description="Filter by period"),
    subject_id: Optional[int] = Query(None, description="Filter by subject"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> List[GroupWithSchedules]:
    """Get all groups with optional filters."""
    repo = GroupRepository(db)

    if period_id and subject_id:
        groups = await repo.get_by_subject_and_period(subject_id, period_id)
    elif period_id:
        groups = await repo.get_by_period(period_id, offset, limit)
    else:
        # Get current period if not specified
        current_period = await repo.get_current_period()
        if current_period:
            groups = await repo.get_by_period(current_period.id, offset, limit)
        else:
            groups = []

    return [
        GroupWithSchedules(
            id=g.id,
            group_number=g.group_number,
            capacity=g.capacity,
            classroom=g.classroom,
            modality=g.modality,
            subject_id=g.subject_id,
            period_id=g.period_id,
            professor_id=g.professor_id,
            enrolled_count=g.enrolled_count,
            available_spots=g.available_spots,
            is_full=g.is_full,
            is_active=g.is_active,
            schedules=[
                {
                    "id": s.id,
                    "group_id": s.group_id,
                    "day_of_week": s.day_of_week,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "classroom": s.classroom,
                    "schedule_type": s.schedule_type,
                    "day_name": s.day_name,
                    "time_range": s.time_range,
                }
                for s in g.schedules
            ],
            subject={
                "id": g.subject.id,
                "code": g.subject.code,
                "name": g.subject.name,
                "credits": g.subject.credits,
            } if g.subject else None,
        )
        for g in groups
    ]


@router.get("/available", response_model=List[GroupWithSchedules])
async def get_available_groups(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    period_id: Optional[int] = Query(None, description="Period ID"),
) -> List[GroupWithSchedules]:
    """Get groups with available spots."""
    repo = GroupRepository(db)

    if not period_id:
        current_period = await repo.get_current_period()
        period_id = current_period.id if current_period else None

    if not period_id:
        return []

    groups = await repo.get_available_groups(period_id)
    return [
        GroupWithSchedules(
            id=g.id,
            group_number=g.group_number,
            capacity=g.capacity,
            classroom=g.classroom,
            modality=g.modality,
            subject_id=g.subject_id,
            period_id=g.period_id,
            professor_id=g.professor_id,
            enrolled_count=g.enrolled_count,
            available_spots=g.available_spots,
            is_full=g.is_full,
            is_active=g.is_active,
            schedules=[
                {
                    "id": s.id,
                    "group_id": s.group_id,
                    "day_of_week": s.day_of_week,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "classroom": s.classroom,
                    "schedule_type": s.schedule_type,
                    "day_name": s.day_name,
                    "time_range": s.time_range,
                }
                for s in g.schedules
            ],
            subject={
                "id": g.subject.id,
                "code": g.subject.code,
                "name": g.subject.name,
                "credits": g.subject.credits,
            } if g.subject else None,
        )
        for g in groups
    ]


@router.get("/{group_id}", response_model=GroupWithSchedules)
async def get_group(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> GroupWithSchedules:
    """Get a group by ID."""
    repo = GroupRepository(db)
    group = await repo.get_by_id(group_id)

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found",
        )

    return GroupWithSchedules(
        id=group.id,
        group_number=group.group_number,
        capacity=group.capacity,
        classroom=group.classroom,
        modality=group.modality,
        subject_id=group.subject_id,
        period_id=group.period_id,
        professor_id=group.professor_id,
        enrolled_count=group.enrolled_count,
        available_spots=group.available_spots,
        is_full=group.is_full,
        is_active=group.is_active,
        schedules=[
            {
                "id": s.id,
                "group_id": s.group_id,
                "day_of_week": s.day_of_week,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "classroom": s.classroom,
                "schedule_type": s.schedule_type,
                "day_name": s.day_name,
                "time_range": s.time_range,
            }
            for s in group.schedules
        ],
        subject={
            "id": group.subject.id,
            "code": group.subject.code,
            "name": group.subject.name,
            "credits": group.subject.credits,
        } if group.subject else None,
    )


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
    data: GroupCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["COORDINADOR", "ADMIN_SISTEMA"]))],
) -> GroupRead:
    """Create a new group. Requires COORDINADOR or ADMIN role."""
    repo = GroupRepository(db)
    group = await repo.create(data)
    await db.commit()
    return GroupRead.model_validate(group)
