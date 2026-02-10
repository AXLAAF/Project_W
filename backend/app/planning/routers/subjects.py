"""Subjects API router."""
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db
from app.dependencies import get_current_user, require_role
from app.core.models.user import User
from app.planning.schemas.subject import (
    SubjectCreate,
    SubjectRead,
    SubjectUpdate,
    SubjectWithPrerequisites,
    PrerequisiteCreate,
)
from app.planning.services.subject_service import (
    SubjectService,
    SubjectNotFoundError,
    DuplicateSubjectError,
)

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=List[SubjectRead])
async def list_subjects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    department: Optional[str] = Query(None, description="Filter by department"),
    semester: Optional[int] = Query(None, ge=1, le=15, description="Filter by suggested semester"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> List[SubjectRead]:
    """Get all subjects with optional filters."""
    service = SubjectService(db)
    subjects = await service.list_subjects(
        department=department,
        semester=semester,
        offset=offset,
        limit=limit,
    )
    return [SubjectRead.model_validate(s) for s in subjects]


@router.get("/search", response_model=List[SubjectRead])
async def search_subjects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    q: str = Query(..., min_length=2, description="Search query"),
) -> List[SubjectRead]:
    """Search subjects by name or code."""
    service = SubjectService(db)
    subjects = await service.search_subjects(q)
    return [SubjectRead.model_validate(s) for s in subjects]


@router.get("/departments", response_model=List[str])
async def get_departments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[str]:
    """Get all available departments."""
    service = SubjectService(db)
    return await service.get_departments()


@router.get("/{subject_id}", response_model=SubjectWithPrerequisites)
async def get_subject(
    subject_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SubjectWithPrerequisites:
    """Get a subject by ID with prerequisites."""
    service = SubjectService(db)
    try:
        subject = await service.get_subject(subject_id)
        prerequisites = await service.get_prerequisites(subject_id)

        return SubjectWithPrerequisites(
            **SubjectRead.model_validate(subject).model_dump(),
            prerequisites=[
                {"id": p.id, "code": p.code, "name": p.name, "credits": p.credits}
                for p in prerequisites
            ],
            required_by=[],  # Could load if needed
        )
    except SubjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
async def create_subject(
    data: SubjectCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["COORDINADOR", "ADMIN_SISTEMA"]))],
) -> SubjectRead:
    """Create a new subject. Requires COORDINADOR or ADMIN role."""
    service = SubjectService(db)
    try:
        subject = await service.create_subject(data)
        await db.commit()
        return SubjectRead.model_validate(subject)
    except DuplicateSubjectError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SubjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{subject_id}", response_model=SubjectRead)
async def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["COORDINADOR", "ADMIN_SISTEMA"]))],
) -> SubjectRead:
    """Update a subject. Requires COORDINADOR or ADMIN role."""
    service = SubjectService(db)
    try:
        subject = await service.update_subject(subject_id, data)
        await db.commit()
        return SubjectRead.model_validate(subject)
    except SubjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{subject_id}/prerequisites", status_code=status.HTTP_201_CREATED)
async def add_prerequisite(
    subject_id: int,
    data: PrerequisiteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role(["COORDINADOR", "ADMIN_SISTEMA"]))],
) -> dict:
    """Add a prerequisite to a subject."""
    service = SubjectService(db)
    try:
        await service.add_prerequisite(
            subject_id, data.prerequisite_id, data.is_mandatory
        )
        await db.commit()
        return {"message": "Prerequisite added successfully"}
    except SubjectNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
