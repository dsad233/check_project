from datetime import datetime

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dto.search_dto import BaseSearchDto
from app.models.parts.parts_model import Parts


async def get_name_by_branch_id_and_part_id(
    *, session: AsyncSession, branch_id: int, part_id: int
) -> str | None:
    stmt = select(Parts.name).where(Parts.id == part_id).where(Parts.deleted_yn == "N")
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
