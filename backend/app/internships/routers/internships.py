"""
Internships API router.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.dependencies import get_current_active_user
from app.shared.database import get_db
from app.internships.models.internship import InternshipStatus
from app.internships.services.internship_service import InternshipService, InternshipError
from app.internships.schemas.internship import (
    InternshipCreate,
    InternshipRead,
    InternshipWithReports,
    InternshipComplete,
)
from app.internships.schemas.report import ReportCreate, ReportRead, ReportReview

router = APIRouter(prefix="/internships", tags=["internships"])


@router.get("/active", response_model=Optional[InternshipWithReports])
async def get_active_internship(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Optional[InternshipWithReports]:
    """
    Get current user's active internship (if any).
    """
    service = InternshipService(db)
    internship = await service.get_active_by_user(current_user.id)
    if not internship:
        return None
    return InternshipWithReports.model_validate(internship)


@router.get("/my-internships", response_model=list[InternshipRead])
async def get_my_internships(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    status: Optional[InternshipStatus] = Query(None),
) -> list[InternshipRead]:
    """
    Get current user's internships.
    """
    service = InternshipService(db)
    internships = await service.get_by_user(current_user.id, status)
    return [InternshipRead.model_validate(i) for i in internships]


@router.post("", response_model=InternshipRead, status_code=status.HTTP_201_CREATED)
async def create_internship(
    data: InternshipCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> InternshipRead:
    """
    Create a new internship from approved application.
    """
    # TODO: Add role check for admin/reviewer
    service = InternshipService(db)
    try:
        internship = await service.create_from_application(data)
        await db.commit()
        return InternshipRead.model_validate(internship)
    except InternshipError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{internship_id}", response_model=InternshipWithReports)
async def get_internship(
    internship_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> InternshipWithReports:
    """
    Get internship details by ID.
    """
    service = InternshipService(db)
    internship = await service.get_by_id(internship_id)
    if not internship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internship not found",
        )
    return InternshipWithReports.model_validate(internship)


@router.put("/{internship_id}/complete", response_model=InternshipRead)
async def complete_internship(
    internship_id: int,
    data: InternshipComplete,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> InternshipRead:
    """
    Complete an internship.
    """
    # TODO: Add role check for admin/supervisor
    service = InternshipService(db)
    try:
        internship = await service.complete(internship_id, data)
        await db.commit()
        return InternshipRead.model_validate(internship)
    except InternshipError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Report endpoints
@router.post("/{internship_id}/reports", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    internship_id: int,
    data: ReportCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ReportRead:
    """
    Create a new monthly report.
    """
    # Override internship_id from path
    data.internship_id = internship_id
    
    service = InternshipService(db)
    try:
        report = await service.create_report(current_user.id, data)
        await db.commit()
        return ReportRead.model_validate(report)
    except InternshipError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{internship_id}/reports", response_model=list[ReportRead])
async def get_reports(
    internship_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[ReportRead]:
    """
    Get all reports for an internship.
    """
    service = InternshipService(db)
    reports = await service.get_reports(internship_id)
    return [ReportRead.model_validate(r) for r in reports]


@router.put("/{internship_id}/reports/{report_id}/submit", response_model=ReportRead)
async def submit_report(
    internship_id: int,
    report_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ReportRead:
    """
    Submit a report for review.
    """
    service = InternshipService(db)
    try:
        report = await service.submit_report(report_id, current_user.id)
        await db.commit()
        return ReportRead.model_validate(report)
    except InternshipError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{internship_id}/reports/{report_id}/review", response_model=ReportRead)
async def review_report(
    internship_id: int,
    report_id: int,
    data: ReportReview,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ReportRead:
    """
    Review a submitted report (supervisor/admin).
    """
    # TODO: Add role check for supervisor/admin
    service = InternshipService(db)
    try:
        report = await service.review_report(report_id, data)
        await db.commit()
        return ReportRead.model_validate(report)
    except InternshipError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
