from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.parts import parts_crud
from app.models.parts.parts_model import Parts
from app.schemas.parts_schemas import PartRequest, PartResponse
from app.exceptions.exceptions import NotFoundError, InvalidEnumValueError, BadRequestError
from app.enums.parts import PartAutoAnnualLeaveGrant
from app.cruds.branches.policies import salary_polices_crud

async def get_part_by_id(
    *, session: AsyncSession, part_id: int
) -> Parts:
    part = await parts_crud.find_by_id(session=session, part_id=part_id)
    if part is None:
        raise NotFoundError(detail=f"{part_id}번 파트가 존재하지 않습니다.")
    return part

async def get_parts_by_auto_annual_leave_grant(
    *, session: AsyncSession, auto_annual_leave_grant: PartAutoAnnualLeaveGrant
) -> list[Parts]:
    parts = await parts_crud.find_all_by_auto_annual_leave_grant(session=session, auto_annual_leave_grant=auto_annual_leave_grant)
    if not parts:
        return []
    return parts


async def update_auto_annual_leave_grant(
    *, session: AsyncSession, part_id: int, request: str
) -> bool:
    part = await get_part_by_id(session=session, part_id=part_id)
    if part is None:
        raise NotFoundError(detail=f"{part_id}번 파트가 존재하지 않습니다.")
    if request not in PartAutoAnnualLeaveGrant:
        raise InvalidEnumValueError(f"잘못된 자동 부여 정책 ENUM 입니다: {request}")
    
    return await parts_crud.update_auto_annual_leave_grant(session=session, part_id=part_id, request=request, old=part)


async def get_parts_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> list[PartResponse]:
    parts = await parts_crud.find_all_by_branch_id(session=session, branch_id=branch_id)
    if not parts:
        return []
    return parts


async def delete_part(
    *, session: AsyncSession, part_id: int
) -> bool:
    part = await get_part_by_id(session=session, part_id=part_id)
    if part is None:
        raise NotFoundError(detail=f"{part_id}번 파트가 존재하지 않습니다.")
    return await parts_crud.delete_part(session=session, part_id=part_id)


async def update_part(
    *, session: AsyncSession, part_id: int, request: PartRequest, branch_id: int
) -> bool:
    
    part = await get_part_by_id(session=session, part_id=part_id)
    if part is None:
        raise NotFoundError(detail=f"{part_id}번 파트가 존재하지 않습니다.")
    
    if part.name != request.name:
        duplicate_part = await parts_crud.find_by_name_and_branch_id(session=session, name=request.name, branch_id=branch_id)
        if duplicate_part is not None:
            raise BadRequestError(detail=f"{request.name}은(는) 이미 존재합니다.")
    
    return await parts_crud.update_part(session=session, part_id=part_id, request=Parts(**request.model_dump(exclude_none=True)), old=part)


async def create_part(
    *, session: AsyncSession, request: PartRequest, branch_id: int
) -> PartResponse:
    duplicate_part = await parts_crud.find_by_name_and_branch_id(session=session, name=request.name, branch_id=branch_id)
    if duplicate_part is not None:
        raise BadRequestError(detail=f"{request.name}은(는) 이미 존재합니다.")
    
    part = await parts_crud.create_part(session=session, request=Parts(branch_id=branch_id, **request.model_dump()))
    part_id = part.id

    await salary_polices_crud.create_salary_templates_policies(db=session, part_ids=[part_id], branch_id=branch_id)
    return part
