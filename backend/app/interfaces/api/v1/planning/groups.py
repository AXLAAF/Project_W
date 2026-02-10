"""
Groups API Router (Hexagonal Architecture).
"""
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.interfaces.dependencies import (
    get_list_groups_use_case,
    get_get_group_use_case,
    get_create_group_use_case,
    get_current_user,
    require_coordinator,
)
from app.application.use_cases.planning.group.list_groups import ListGroupsUseCase
from app.application.use_cases.planning.group.get_group import GetGroupUseCase
from app.application.use_cases.planning.group.create_group import CreateGroupUseCase

from app.domain.entities.user import User
from app.application.dtos.planning_dtos import GroupDTO, CreateGroupDTO
from app.planning.schemas.group import GroupCreate, GroupRead, GroupWithSchedules

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=List[GroupWithSchedules])
async def list_groups(
    use_case: Annotated[ListGroupsUseCase, Depends(get_list_groups_use_case)],
    current_user: Annotated[User, Depends(get_current_user)],
    period_id: Optional[int] = Query(None, description="Filter by period"),
    subject_id: Optional[int] = Query(None, description="Filter by subject"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> List[GroupWithSchedules]:
    """Get all groups with optional filters."""
    dtos, _ = await use_case.execute(
        period_id=period_id,
        subject_id=subject_id,
        offset=offset,
        limit=limit
    )
    
    # Map DTOs to Response Schema
    # GroupWithSchedules expects dict-like structure or object with attributes
    # GroupDTO is a dataclass.
    
    return [
        GroupWithSchedules(
            id=d.id,
            group_number=d.code, # DTO uses 'code', GroupWithSchedules uses 'group_number'
            capacity=d.quota, # DTO uses 'quota', Schema 'capacity'
            classroom=None, # DTO doesn't seem to have classroom at top level, schedules do
            modality="Presencial", # DTO missing modality?
            subject_id=d.subject_id,
            period_id=d.academic_period_id,
            professor_id=d.teacher_id,
            enrolled_count=d.enrolled_count,
            available_spots=d.available_spots,
            is_full=d.is_full,
            is_active=d.is_active,
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
                for s in d.schedules
            ],
            subject={
                "id": d.subject_id, # We don't have full subject access here unless DTO has it
                "code": d.subject_code,
                "name": d.subject_name,
                "credits": 0, # DTO missing credits
            } if d.subject_code else None,
        ) for d in dtos
    ]


@router.get("/{group_id}", response_model=GroupWithSchedules)
async def get_group(
    group_id: int,
    use_case: Annotated[GetGroupUseCase, Depends(get_get_group_use_case)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> GroupWithSchedules:
    """Get a group by ID."""
    try:
        d = await use_case.execute(group_id)
        
        return GroupWithSchedules(
            id=d.id,
            group_number=d.code,
            capacity=d.quota,
            classroom=None,
            modality="Presencial", # Placeholder
            subject_id=d.subject_id,
            period_id=d.academic_period_id,
            professor_id=d.teacher_id,
            enrolled_count=d.enrolled_count,
            available_spots=d.available_spots,
            is_full=d.is_full,
            is_active=d.is_active,
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
                for s in d.schedules
            ],
            subject={
                "id": d.subject_id,
                "code": d.subject_code,
                "name": d.subject_name,
                "credits": 0,
            } if d.subject_code else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
    data: GroupCreate,
    use_case: Annotated[CreateGroupUseCase, Depends(get_create_group_use_case)],
    current_user: Annotated[User, Depends(require_coordinator)],
) -> GroupRead:
    """Create a new group."""
    dto = CreateGroupDTO(
        subject_id=data.subject_id,
        academic_period_id=data.period_id,
        code=data.group_number,
        teacher_id=data.professor_id,
        quota=data.capacity,
        schedule_summary=None,
    )
    
    try:
        result = await use_case.execute(dto)
        return GroupRead(
             id=result.id,
             group_number=result.code,
             capacity=result.quota,
             classroom=None,
             modality="Presencial",
             subject_id=result.subject_id,
             period_id=result.academic_period_id,
             professor_id=result.teacher_id,
             enrolled_count=result.enrolled_count,
             available_spots=result.available_spots,
             is_full=result.is_full,
             is_active=result.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
