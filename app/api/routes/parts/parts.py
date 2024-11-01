import asyncio
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.parts_schemas import PartRequest, PartResponse
from app.service import parts_service
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role


router = APIRouter()
# 세마포어를 사용하여 동시 접근 제어
semaphore = asyncio.Semaphore(1)

@router.get("", response_model=list[PartResponse], summary="부서 조회")
@available_higher_than(Role.EMPLOYEE)
async def get_parts(
    context: Request,
    branch_id: int,
    session: AsyncSession = Depends(get_db)
) -> list[PartResponse]:
    
    return await parts_service.get_parts_by_branch_id(session=session, branch_id=branch_id)


@router.post("", response_model=PartResponse, summary="부서 생성")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_part(
    context: Request,
    branch_id: int,
    request: PartRequest,
    session: AsyncSession = Depends(get_db)
) -> PartResponse:
    
    async with semaphore:  # 세마포어를 사용하여 동시 접근 제어
        return await parts_service.create_part(session=session, request=request, branch_id=branch_id)


@router.delete("/{part_id}", response_model=bool, summary="부서 삭제")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_part(
    context: Request,
    branch_id: int,
    part_id: int,
    session: AsyncSession = Depends(get_db)
) -> bool:
    
    return await parts_service.delete_part(session=session, part_id=part_id)


@router.patch("/{part_id}", response_model=bool, summary="부서 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_part(
    context: Request,
    branch_id: int,
    part_id: int,
    request: PartRequest,
    session: AsyncSession = Depends(get_db)
) -> bool:
    
    return await parts_service.update_part(session=session, part_id=part_id, request=request, branch_id=branch_id)