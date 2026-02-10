"""
Companies API router.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.dependencies import get_current_active_user
from app.shared.database import get_db
from app.internships.services.company_service import CompanyService, CompanyError
from app.internships.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyRead,
    CompanyList,
    CompanyVerify,
)

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyList])
async def list_companies(
    db: Annotated[AsyncSession, Depends(get_db)],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_verified: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
) -> list[CompanyList]:
    """
    List all companies with pagination and filters.
    """
    service = CompanyService(db)
    companies, _ = await service.get_all(
        offset=offset,
        limit=limit,
        is_verified=is_verified,
        search=search,
    )
    return [CompanyList.model_validate(c) for c in companies]


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CompanyRead:
    """
    Get company details by ID.
    """
    service = CompanyService(db)
    company = await service.get_by_id(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    return CompanyRead.model_validate(company)


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CompanyRead:
    """
    Register a new company.
    """
    service = CompanyService(db)
    try:
        company = await service.create(data)
        await db.commit()
        return CompanyRead.model_validate(company)
    except CompanyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: int,
    data: CompanyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CompanyRead:
    """
    Update company information.
    """
    service = CompanyService(db)
    try:
        company = await service.update(company_id, data)
        await db.commit()
        return CompanyRead.model_validate(company)
    except CompanyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{company_id}/verify", response_model=CompanyRead)
async def verify_company(
    company_id: int,
    data: CompanyVerify,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CompanyRead:
    """
    Verify or unverify a company (admin only).
    """
    # TODO: Add role check for admin
    service = CompanyService(db)
    try:
        company = await service.verify(company_id, data.is_verified)
        await db.commit()
        return CompanyRead.model_validate(company)
    except CompanyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
