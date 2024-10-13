from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Branches
from sqlalchemy import select, func
from datetime import datetime
from app.api.routes.branches.schema.branch_schema import BranchCreate, BranchDelete, BranchListResponse, BranchResponse

async def create_branch(*, session: AsyncSession, branch_create: BranchCreate) -> Branches:
    db_obj = Branches(**branch_create.model_dump())

    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def find_branch_all(*, session: AsyncSession, skip: int = 0, limit: int = 10) -> list[Branches]:
    statement = select(Branches).filter(Branches.deleted_yn == "N").offset(skip).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()

async def find_branch_deleted_all(*, session: AsyncSession, skip: int = 0, limit: int = 10) -> list[Branches]:
    statement = select(Branches).filter(Branches.deleted_yn == "Y").offset(skip).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()

async def count_branch_all(*, session: AsyncSession) -> int:
    statement = select(func.count()).select_from(Branches)
    result = await session.execute(statement)
    return result.scalar_one()

async def find_branch_by_id(*, session: AsyncSession, branch_id: int) -> Branches | None:
    statement = select(Branches).filter(Branches.id == branch_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def delete_branch(*, session: AsyncSession, branch: Branches) -> None:
    # 브랜치 객체 업데이트
    branch.deleted_yn = "Y"
    branch.updated_at = datetime.now()  # 업데이트 시간도 함께 변경

    # 데이터베이스에 변경사항 반영
    await session.commit()