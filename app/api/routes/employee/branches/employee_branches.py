from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.branches.branches_model import Branches
from app.schemas.branches_schemas import BranchResponse


router = APIRouter()


@router.get("/my-branch", response_model=BranchResponse, summary="내 소속 지점 정보 조회")
async def read_my_branch(
        *, context: Request, session: AsyncSession = Depends(get_db)
) -> BranchResponse:
    """
    현재 로그인한 사용자의 소속 지점 정보를 조회합니다.
    """
    query = select(Branches).where(
        Branches.id == context.state.user.branch_id,
        Branches.deleted_yn == "N"
    )

    result = await session.execute(query)
    branch = result.scalar_one_or_none()

    if not branch:
        raise HTTPException(
            status_code=404,
            detail="지점을 찾을 수 없습니다."
        )

    return BranchResponse.model_validate(branch)