from app.cruds.users import users_crud
from app.schemas.users_schemas import UserLeaveResponse, UsersLeaveResponse
from app.schemas.branches_schemas import ManualGrantRequest
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import NotFoundError, BadRequestError
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.models.users.users_model import Users


async def get_branch_users_leave(
    *, session: AsyncSession, branch_id: int, request: BaseSearchDto
) -> UsersLeaveResponse:
    """지점 내 유저들의 잔여 연차 수 및 연차 부여 방식 조회"""
    users_count = await users_crud.get_users_count(session=session, branch_id=branch_id)
    users = await users_crud.find_all_by_branch_id(session=session, branch_id=branch_id, request=request)
    if not users:
        return UsersLeaveResponse(data=[], pagination=PaginationDto(total_count=users_count, record_size=request.record_size))
    
    return UsersLeaveResponse(data=[
        UserLeaveResponse(id=user.id, 
                          name=user.name, 
                          part_name=user.part.name, 
                          grant_type=user.part.auto_annual_leave_grant, 
                          total_leave_days=user.total_leave_days) for user in users
    ], pagination=PaginationDto(total_record=users_count, record_size=request.record_size))


async def plus_total_leave_days(
    *, session: AsyncSession, request: ManualGrantRequest
) -> bool:
    """잔여 연차 수 증가"""
    if request.user_ids:
        for user_id in request.user_ids:
            user = await users_crud.find_by_id(session=session, user_id=user_id)
            if not user:
                raise NotFoundError(detail=f"{user_id}번 유저를 찾을 수 없습니다.")
            await users_crud.plus_total_leave_days(session=session, user_id=user_id, count=request.count)
    return True


async def minus_total_leave_days(
    *, session: AsyncSession, request: ManualGrantRequest
) -> bool:
    """잔여 연차 수 감소"""
    if request.user_ids:
        for user_id in request.user_ids:
            user = await users_crud.find_by_id(session=session, user_id=user_id)
            if not user:
                raise NotFoundError(detail=f"{user_id}번 유저를 찾을 수 없습니다.")
            if user.total_leave_days < request.count:
                raise BadRequestError(detail="잔여 연차가 부족합니다.")
            await users_crud.minus_total_leave_days(session=session, user_id=user_id, count=request.count)
    return True


async def get_user_by_id(
    *, session: AsyncSession, user_id: int
) -> Users:
    """유저 조회"""
    user = await users_crud.find_by_id(session=session, user_id=user_id)
    if not user:
        raise NotFoundError(detail="유저를 찾을 수 없습니다.")
    return user
