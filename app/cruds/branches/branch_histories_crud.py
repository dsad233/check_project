from app.enums.branches import BranchHistoryType
from app.models.histories.branch_histories_model import BranchHistories
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from app.common.dto.search_dto import BaseSearchDto
from app.schemas.branches_schemas import BranchHistoryResponse


async def create_branch_history(
        session: AsyncSession, 
        branch_id: int, 
        history_create: BranchHistories
) -> BranchHistories:
    
    session.add(history_create)
    await session.commit()
    await session.refresh(history_create)
    return history_create


async def get_branch_histories(
        session: AsyncSession, 
        branch_id: int, 
        history_type: BranchHistoryType,
        request: BaseSearchDto
) -> list[BranchHistories]:
    # snapshot_id 별로 그룹화
    snapshot_subquery = (
        select(BranchHistories.snapshot_id)
        .where(
            BranchHistories.branch_id == branch_id,
            BranchHistories.history_type == history_type
        )
        .group_by(BranchHistories.snapshot_id)
        .order_by(func.max(BranchHistories.created_at).desc())
        .scalar_subquery()
    )


    stmt = (
        select(BranchHistories)
        .where(
            BranchHistories.branch_id == branch_id,
            BranchHistories.history_type == history_type,
            BranchHistories.snapshot_id.in_(snapshot_subquery)
        )
        .order_by(BranchHistories.created_at.desc())
        .limit(request.record_size)
        .offset(request.offset)
    )
    result = await session.execute(stmt)
    return result.scalars().all()
    

async def get_total_cnt(
        session: AsyncSession, 
        branch_id: int, 
        history_type: BranchHistoryType
) -> int:
    return await session.scalar(select(func.count(BranchHistories.snapshot_id)).where(
        BranchHistories.branch_id == branch_id
    ).where(BranchHistories.history_type == history_type))

