from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.branches.leave_excluded_parts_model import LeaveExcludedPart


async def find_all_by_leave_category_id(
    *, session: AsyncSession, leave_category_id: int
) -> list[LeaveExcludedPart]:
    
    stmt = select(LeaveExcludedPart).where(LeaveExcludedPart.leave_category_id == leave_category_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_all_part_id(
    *, session: AsyncSession, leave_category_id: int, part_ids: list[int]
) -> list[int]:

    # 벌크 삽입 사용
    insert_stmt = insert(LeaveExcludedPart).values([
        {"leave_category_id": leave_category_id, "part_id": part_id}
        for part_id in part_ids
    ])
    await session.execute(insert_stmt)
    await session.commit()

    return part_ids


async def delete_all_part_id(
    *, session: AsyncSession, leave_category_id: int, part_ids: list[int]
) -> list[int]:

    # 벌크 삭제 사용
    delete_stmt = delete(LeaveExcludedPart).where(
        (LeaveExcludedPart.leave_category_id == leave_category_id) & 
        (LeaveExcludedPart.part_id.in_(part_ids))
    )
    await session.execute(delete_stmt)
    await session.commit()

    return part_ids
