import logging
from datetime import datetime
from sqlite3 import IntegrityError
from typing import List, Optional
from fastapi import Depends
from sqlalchemy import func, select, exists
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from app.common.dto.search_dto import BaseSearchDto
from app.models.branches.auto_annual_leave_approval_model import AutoAnnualLeaveApproval
from app.exceptions.exceptions import NotFoundError, BadRequestError
from datetime import datetime

logger = logging.getLogger(__name__)

async def find_by_branch_id(*, session: AsyncSession, branch_id: int) -> Optional[AutoAnnualLeaveApproval]:
    
    stmt = (
        select(AutoAnnualLeaveApproval)
        .where(AutoAnnualLeaveApproval.branch_id == branch_id)
        .where(AutoAnnualLeaveApproval.deleted_yn == 'N')
    )
    result = await session.execute(stmt)
    policy = result.scalar_one_or_none()
    
    
    return policy

async def create(*, session: AsyncSession, branch_id: int, request: AutoAnnualLeaveApproval = AutoAnnualLeaveApproval()) -> AutoAnnualLeaveApproval:

    if request.branch_id is None:
        request.branch_id = branch_id
    session.add(request)
    await session.flush()
    await session.refresh(request)
    return request

async def update(*, session: AsyncSession, branch_id: int, request: AutoAnnualLeaveApproval, old: AutoAnnualLeaveApproval) -> bool:
    
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in AutoAnnualLeaveApproval.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(request, column.name)
            if new_value is not None and getattr(old, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(AutoAnnualLeaveApproval).where(AutoAnnualLeaveApproval.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        old.updated_at = datetime.now()
        await session.flush()
        await session.refresh(old)
    else:
        pass

    return True
