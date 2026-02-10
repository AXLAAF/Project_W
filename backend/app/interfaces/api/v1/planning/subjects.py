"""
Subjects API Router (Hexagonal Architecture).
"""
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.interfaces.dependencies import (
    get_create_subject_use_case,
    get_get_subject_use_case,
    get_list_subjects_use_case,
    get_update_subject_use_case,
    get_add_prerequisite_use_case,
    get_current_user,
    require_coordinator,
    require_admin,
)
from app.application.use_cases.planning.subject.create_subject import CreateSubjectUseCase
from app.application.use_cases.planning.subject.get_subject import GetSubjectUseCase
from app.application.use_cases.planning.subject.list_subjects import ListSubjectsUseCase
from app.application.use_cases.planning.subject.update_subject import UpdateSubjectUseCase
from app.application.use_cases.planning.subject.add_prerequisite import AddPrerequisiteUseCase

from app.domain.entities.user import User

# Schemas and DTOs
from app.planning.schemas.subject import (
    SubjectCreate,
    SubjectRead,
    SubjectUpdate,
    SubjectWithPrerequisites,
    PrerequisiteCreate,
    PrerequisiteRead,
)
from app.application.dtos.planning_dtos import CreateSubjectDTO, UpdateSubjectDTO

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.get("", response_model=List[SubjectRead])
async def list_subjects(
    use_case: Annotated[ListSubjectsUseCase, Depends(get_list_subjects_use_case)],
    current_user: Annotated[User, Depends(get_current_user)],
    department: Optional[str] = Query(None, description="Filter by department"),
    # semester: Optional[int] = Query(None, ge=1, le=15), # Not in UseCase yet, assuming simplified list first
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> List[SubjectRead]:
    """List subjects."""
    # Mapping params to use case args
    # TODO: Update use case to support semester filtering if needed
    dtos, _ = await use_case.execute(offset=offset, limit=limit, department=department)
    
    # Map DTOs to Schema
    return [
        SubjectRead(
            id=d.id,
            code=d.code,
            name=d.name,
            credits=d.credits,
            hours_theory=d.hours_theory,
            hours_practice=d.hours_practice,
            hours_lab=d.hours_lab,
            total_hours=d.total_hours,
            description=d.description,
            department=d.department,
            semester_suggested=d.semester_suggested,
            is_active=d.is_active,
        ) for d in dtos
    ]

@router.get("/{subject_id}", response_model=SubjectWithPrerequisites)
async def get_subject(
    subject_id: int,
    use_case: Annotated[GetSubjectUseCase, Depends(get_get_subject_use_case)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SubjectWithPrerequisites:
    """Get subject details."""
    try:
        dto = await use_case.execute(subject_id)
        
        prereqs = [
            PrerequisiteRead(
                id=p.id, # Note: PrerequisiteDTO has id of the subject
                code=p.code,
                name=p.name,
                credits=p.credits,
                # is_mandatory is in PrerequisiteDTO but PrerequisiteRead might not have it or structure differs
                # PrerequisiteRead schema: id, code, name, credits.
                # It does not have is_mandatory.
            ) for p in dto.prerequisites
        ]
        
        return SubjectWithPrerequisites(
            id=dto.id,
            code=dto.code,
            name=dto.name,
            credits=dto.credits,
            hours_theory=dto.hours_theory,
            hours_practice=dto.hours_practice,
            hours_lab=dto.hours_lab,
            total_hours=dto.total_hours,
            description=dto.description,
            department=dto.department,
            semester_suggested=dto.semester_suggested,
            is_active=dto.is_active,
            prerequisites=prereqs,
            required_by=[]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
async def create_subject(
    data: SubjectCreate,
    use_case: Annotated[CreateSubjectUseCase, Depends(get_create_subject_use_case)],
    current_user: Annotated[User, Depends(require_coordinator)],
) -> SubjectRead:
    """Create subject."""
    dto = CreateSubjectDTO(
        code=data.code,
        name=data.name,
        credits=data.credits,
        hours_theory=data.hours_theory,
        hours_practice=data.hours_practice,
        hours_lab=data.hours_lab,
        description=data.description,
        department=data.department,
        semester_suggested=data.semester_suggested,
        prerequisite_ids=data.prerequisite_ids,
    )
    
    try:
        result = await use_case.execute(dto)
        return SubjectRead(
            id=result.id,
            code=result.code,
            name=result.name,
            credits=result.credits,
            hours_theory=result.hours_theory,
            hours_practice=result.hours_practice,
            hours_lab=result.hours_lab,
            total_hours=result.total_hours,
            description=result.description,
            department=result.department,
            semester_suggested=result.semester_suggested,
            is_active=result.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{subject_id}", response_model=SubjectRead)
async def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    use_case: Annotated[UpdateSubjectUseCase, Depends(get_update_subject_use_case)],
    current_user: Annotated[User, Depends(require_coordinator)],
) -> SubjectRead:
    """Update subject."""
    dto = UpdateSubjectDTO(
        name=data.name,
        credits=data.credits,
        hours_theory=data.hours_theory,
        hours_practice=data.hours_practice,
        hours_lab=data.hours_lab,
        description=data.description,
        department=data.department,
        semester_suggested=data.semester_suggested,
        is_active=data.is_active,
    )
    
    try:
        result = await use_case.execute(subject_id, dto)
        return SubjectRead(
            id=result.id,
            code=result.code,
            name=result.name,
            credits=result.credits,
            hours_theory=result.hours_theory,
            hours_practice=result.hours_practice,
            hours_lab=result.hours_lab,
            total_hours=result.total_hours,
            description=result.description,
            department=result.department,
            semester_suggested=result.semester_suggested,
            is_active=result.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{subject_id}/prerequisites", status_code=status.HTTP_201_CREATED)
async def add_prerequisite(
    subject_id: int,
    data: PrerequisiteCreate,
    use_case: Annotated[AddPrerequisiteUseCase, Depends(get_add_prerequisite_use_case)],
    current_user: Annotated[User, Depends(require_coordinator)],
) -> dict:
    """Add prerequisite."""
    try:
        await use_case.execute(subject_id, data.prerequisite_id, data.is_mandatory)
        return {"message": "Prerequisite added successfully"}
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))
