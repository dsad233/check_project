from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update as sa_update
from datetime import datetime
from app.models.branches.account_based_annual_leave_grant_model import AccountBasedAnnualLeaveGrant
from app.exceptions.exceptions import NotFoundError, BadRequestError


async def find_by_branch_id(*, session: AsyncSession, branch_id: int) -> Optional[AccountBasedAnnualLeaveGrant]:

    stmt = (
        select(AccountBasedAnnualLeaveGrant)
        .where(AccountBasedAnnualLeaveGrant.branch_id == branch_id)
        .where(AccountBasedAnnualLeaveGrant.deleted_yn == 'N')
    )
    result = await session.execute(stmt)
    policy = result.scalar_one_or_none()

    return policy

async def create(*, session: AsyncSession, branch_id: int, account_based_annual_leave_grant_create: AccountBasedAnnualLeaveGrant = AccountBasedAnnualLeaveGrant()) -> AccountBasedAnnualLeaveGrant:

    if await find_by_branch_id(session=session, branch_id=branch_id) is not None:
        raise BadRequestError(f"{branch_id}번 지점의 자동 부여 정책이 이미 존재합니다.")
    if account_based_annual_leave_grant_create.branch_id is None:
        account_based_annual_leave_grant_create.branch_id = branch_id
    session.add(account_based_annual_leave_grant_create)
    await session.commit()
    await session.refresh(account_based_annual_leave_grant_create)
    return account_based_annual_leave_grant_create
    
async def update(*, session: AsyncSession, branch_id: int, account_based_annual_leave_grant_update: AccountBasedAnnualLeaveGrant) -> AccountBasedAnnualLeaveGrant:

    # 기존 정책 조회
    account_based_annual_leave_grant = await find_by_branch_id(session=session, branch_id=branch_id)

    if account_based_annual_leave_grant is None:
        raise NotFoundError(f"{branch_id}번 지점의 자동 부여 정책이 존재하지 않습니다.")
    
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in AccountBasedAnnualLeaveGrant.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(account_based_annual_leave_grant_update, column.name)
            if new_value is not None and getattr(account_based_annual_leave_grant, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(AccountBasedAnnualLeaveGrant).where(AccountBasedAnnualLeaveGrant.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        account_based_annual_leave_grant.updated_at = datetime.now()
        await session.commit()
        await session.refresh(account_based_annual_leave_grant)
    else:
        pass

    return account_based_annual_leave_grant
