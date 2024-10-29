from app.cruds.users import users_crud
from app.schemas.users_schemas import UserLeaveResponse, UsersLeaveResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import NotFoundError
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto


# 지점 내 유저들의 잔여 연차 수 및 연차 부여 방식 조회
async def get_branch_users_leave(
    *, session: AsyncSession, branch_id: int, search: BaseSearchDto
) -> UsersLeaveResponse:
    users_count = await users_crud.get_users_count(session=session, branch_id=branch_id)
    users = await users_crud.find_all_by_branch_id(session=session, branch_id=branch_id, search=search)
    if not users:
        return UsersLeaveResponse(data=[], pagination=PaginationDto(total_count=users_count, record_size=search.record_size))
    
    return UsersLeaveResponse(data=[
        UserLeaveResponse(id=user.id, 
                          name=user.name, 
                          part_name=user.part.name, 
                          grant_type=user.part.auto_annual_leave_grant, 
                          remaining_annual_leave=user.remaining_annual_leave) for user in users
    ], pagination=PaginationDto(total_record=users_count, record_size=search.record_size))

# 잔여 연차 수 증가
async def plus_remaining_annual_leave(
    *, session: AsyncSession, user_id: int, count: int
) -> bool:
    user = await users_crud.find_by_id(session=session, user_id=user_id)
    if not user:
        raise NotFoundError(detail="유저를 찾을 수 없습니다.")
    await users_crud.plus_remaining_annual_leave(session=session, user=user, count=count)
    return True

# 잔여 연차 수 감소
async def minus_remaining_annual_leave(
    *, session: AsyncSession, user_id: int, count: int
) -> bool:
    user = await users_crud.find_by_id(session=session, user_id=user_id)
    if not user:
        raise NotFoundError(detail="유저를 찾을 수 없습니다.")
    await users_crud.minus_remaining_annual_leave(session=session, user=user, count=count)
    return True
