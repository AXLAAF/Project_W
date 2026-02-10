"""Repository for ReservationRule and UserSanction operations."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.reservations.models import ReservationRule, RuleType, UserSanction
from app.reservations.schemas import RuleCreate, RuleUpdate, SanctionCreate


class RuleRepository:
    """Repository for ReservationRule operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: RuleCreate) -> ReservationRule:
        """Create a new rule."""
        rule = ReservationRule(**data.model_dump())
        self.db.add(rule)
        await self.db.flush()
        await self.db.refresh(rule)
        return rule

    async def get_by_id(self, rule_id: int) -> Optional[ReservationRule]:
        """Get a rule by ID."""
        result = await self.db.execute(
            select(ReservationRule).where(ReservationRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    async def get_resource_rules(
        self,
        resource_id: Optional[int] = None,
        rule_type: Optional[RuleType] = None,
        is_active: bool = True,
    ) -> List[ReservationRule]:
        """Get rules for a resource or global rules."""
        conditions = []
        
        if resource_id:
            # Get rules specific to resource OR global rules
            conditions.append(
                (ReservationRule.resource_id == resource_id) | 
                (ReservationRule.resource_id.is_(None))
            )
        else:
            # Get only global rules
            conditions.append(ReservationRule.resource_id.is_(None))
        
        if rule_type:
            conditions.append(ReservationRule.rule_type == rule_type)
        if is_active is not None:
            conditions.append(ReservationRule.is_active == is_active)
        
        query = select(ReservationRule).where(and_(*conditions))
        query = query.order_by(ReservationRule.priority.desc(), ReservationRule.id)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, rule_id: int, data: RuleUpdate) -> Optional[ReservationRule]:
        """Update a rule."""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        await self.db.flush()
        await self.db.refresh(rule)
        return rule

    async def delete(self, rule_id: int) -> bool:
        """Delete a rule."""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return False
        
        await self.db.delete(rule)
        await self.db.flush()
        return True


class SanctionRepository:
    """Repository for UserSanction operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: SanctionCreate, applied_by_id: int) -> UserSanction:
        """Create a new sanction."""
        sanction = UserSanction(
            **data.model_dump(),
            applied_by_id=applied_by_id,
        )
        self.db.add(sanction)
        await self.db.flush()
        await self.db.refresh(sanction)
        return sanction

    async def get_by_id(self, sanction_id: int) -> Optional[UserSanction]:
        """Get a sanction by ID."""
        result = await self.db.execute(
            select(UserSanction).where(UserSanction.id == sanction_id)
        )
        return result.scalar_one_or_none()

    async def get_user_active_sanctions(self, user_id: int) -> List[UserSanction]:
        """Get active sanctions for a user."""
        now = datetime.now()
        result = await self.db.execute(
            select(UserSanction).where(
                and_(
                    UserSanction.user_id == user_id,
                    UserSanction.is_resolved == False,
                    (UserSanction.end_date.is_(None)) | (UserSanction.end_date > now),
                )
            ).order_by(UserSanction.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_sanctions(
        self,
        user_id: int,
        include_resolved: bool = False,
    ) -> List[UserSanction]:
        """Get all sanctions for a user."""
        query = select(UserSanction).where(UserSanction.user_id == user_id)
        
        if not include_resolved:
            query = query.where(UserSanction.is_resolved == False)
        
        query = query.order_by(UserSanction.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def resolve(
        self,
        sanction_id: int,
        resolved_by_id: int,
        resolution_notes: Optional[str] = None,
    ) -> Optional[UserSanction]:
        """Resolve a sanction."""
        sanction = await self.get_by_id(sanction_id)
        if not sanction:
            return None
        
        sanction.is_resolved = True
        sanction.resolved_at = datetime.now()
        sanction.resolved_by_id = resolved_by_id
        sanction.resolution_notes = resolution_notes
        
        await self.db.flush()
        await self.db.refresh(sanction)
        return sanction

    async def user_has_active_sanction(self, user_id: int) -> bool:
        """Check if user has any active sanction."""
        sanctions = await self.get_user_active_sanctions(user_id)
        return len(sanctions) > 0
