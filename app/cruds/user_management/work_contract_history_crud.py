from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.users.users_work_contract_history_model import WorkContractHistory



async def find_work_contract_history_by_id(
    *,
    session: AsyncSession,
    work_contract_history_id: int
) -> WorkContractHistory:
    stmt = (select(WorkContractHistory)
            .options(selectinload(WorkContractHistory.user))
            .options(selectinload(WorkContractHistory.work_contract))
            .where(WorkContractHistory.id == work_contract_history_id)
            .where(WorkContractHistory.deleted_yn == "N"))

    result = await session.execute(stmt)
    return result.scalar_one_or_none()



async def find_work_contract_histories_by_user_id(
    *,
    session: AsyncSession,
    user_id: int
) -> list[WorkContractHistory]:
    stmt = (
        select(WorkContractHistory)
        .where(WorkContractHistory.user_id == user_id)
        .order_by(WorkContractHistory.created_at.desc())  # 최신순 정렬
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())  # 모든 결과 반환


async def add_work_contract_history(
    *,
    session: AsyncSession,
    work_contract_history: WorkContractHistory
) -> int:
    try:
        session.add(work_contract_history)
        await session.commit()
        await session.refresh(work_contract_history)
        return work_contract_history.id
    except Exception as e:
        await session.rollback()
