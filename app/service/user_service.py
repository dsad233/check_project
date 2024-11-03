from app.cruds.users import users_crud
from app.cruds.branches import branches_crud
from app.schemas.users_schemas import (
    UserLeaveResponse, UsersLeaveResponse, PersonnelRecordHistoryResponse, 
    PersonnelRecordHistoriesResponse, PersonnelRecordHistoryCreateRequest, PersonnelRecordHistoryUpdateRequest,
    PersonnelRecordHistoryCreateResponse, PersonnelRecordUsersRequest, PersonnelRecordUsersResponse, PersonnelRecordUserResponse,
    UsersNameResponse, UserNameResponse
)
from app.schemas.branches_schemas import ManualGrantRequest
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.exceptions import NotFoundError, BadRequestError
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.models.users.users_model import Users, PersonnelRecordHistory


MAX_ANNUAL_LEAVE_DAYS = 25

async def get_branch_users_leave(
    *, session: AsyncSession, branch_id: int, request: BaseSearchDto
) -> UsersLeaveResponse:
    """지점 내 유저들의 잔여 연차 수 및 연차 부여 방식 조회"""
    users, total_cnt = await users_crud.get_branch_users(session=session, request=request, branch_id=branch_id)
    if not users:
        return UsersLeaveResponse(data=[], pagination=PaginationDto(total_record=total_cnt, record_size=request.record_size))
    
    return UsersLeaveResponse(data=[
        UserLeaveResponse(id=user.id, 
                          name=user.name, 
                          part_name=user.part.name, 
                          grant_type=user.part.auto_annual_leave_grant, 
                          total_leave_days=user.total_leave_days) for user in users
    ], pagination=PaginationDto(total_record=total_cnt, record_size=request.record_size))


async def plus_total_leave_days(
    *, session: AsyncSession, request: ManualGrantRequest
) -> bool:
    """잔여 연차 수 증가"""
    if request.user_ids:
        for user_id in request.user_ids:
            user = await users_crud.find_by_id(session=session, user_id=user_id)
            if not user:
                raise NotFoundError(detail=f"{user_id}번 유저를 찾을 수 없습니다.")
            updated_total_leave_days = user.total_leave_days + request.count
            if updated_total_leave_days > MAX_ANNUAL_LEAVE_DAYS:
                raise BadRequestError(detail=f"{user.name}의 최대 연차 수를 초과했습니다.")
            await users_crud.update_total_leave_days(session=session, user_id=user_id, count=updated_total_leave_days)
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
            updated_total_leave_days = user.total_leave_days - request.count
            if updated_total_leave_days < 0:
                raise BadRequestError(detail="잔여 연차가 부족합니다.")
            await users_crud.update_total_leave_days(session=session, user_id=user_id, count=updated_total_leave_days)
    return True


async def get_user_by_id(
    *, session: AsyncSession, user_id: int
) -> Users:
    """유저 조회"""
    user = await users_crud.find_by_id(session=session, user_id=user_id)
    if not user:
        raise NotFoundError(detail="유저를 찾을 수 없습니다.")
    return user


async def create_personnel_record_history(
    *, session: AsyncSession, request: PersonnelRecordHistoryCreateRequest, created_by: int, user_id: int
) -> PersonnelRecordHistoryCreateResponse:
    
    return await users_crud.create_personnel_record_history(
        session=session, 
        request=PersonnelRecordHistory(
            created_by=created_by, 
            user_id=user_id,
            **request.model_dump()
        )
    )


async def get_personnel_record_histories(
    *, session: AsyncSession, request: BaseSearchDto, user_id: int
) -> PersonnelRecordHistoriesResponse:
    rows = await users_crud.get_personnel_record_histories(session=session, request=request, user_id=user_id)
    total_cnt = await users_crud.get_personnel_record_histories_count(session=session, user_id=user_id)
    if not rows:
        return PersonnelRecordHistoriesResponse(data=[], pagination=PaginationDto(total_record=total_cnt))
    
    return PersonnelRecordHistoriesResponse(
        data=[PersonnelRecordHistoryResponse(
            id=row.id,
            user_name=row.user.name,
            created_by_user_name=row.created_by_user.name,
            personnel_record_category_name=row.personnel_record_category.name,
            worker_comment=row.worker_comment,
            admin_comment=row.admin_comment,
            created_at=row.created_at
        ) for row in rows], 
        pagination=PaginationDto(total_record=total_cnt)
    )


async def get_personnel_record_history(
    *, session: AsyncSession, personnel_record_history_id: int
) -> PersonnelRecordHistoryResponse:
    personnel_record_history = await users_crud.get_personnel_record_history(session=session, id=personnel_record_history_id)
    if personnel_record_history is None:
        raise NotFoundError(detail=f"{personnel_record_history_id}번 인사기록이 없습니다.")
    return PersonnelRecordHistoryResponse(
        id=personnel_record_history.id,
        user_name=personnel_record_history.user.name,
        created_by_user_name=personnel_record_history.created_by_user.name,
        personnel_record_category_name=personnel_record_history.personnel_record_category.name,
        worker_comment=personnel_record_history.worker_comment,
        admin_comment=personnel_record_history.admin_comment,
        created_at=personnel_record_history.created_at
    )


async def update_personnel_record_history(
    *, session: AsyncSession, personnel_record_history_id: int, request: PersonnelRecordHistoryUpdateRequest, created_by: int
) -> bool:
    personnel_record_history = await users_crud.get_personnel_record_history(session=session, id=personnel_record_history_id)
    if personnel_record_history is None:
        raise NotFoundError(detail=f"{personnel_record_history_id}번 인사기록이 없습니다.")
    
    personnel_record_history.created_by = created_by

    return await users_crud.update_personnel_record_history(
        session=session, old=personnel_record_history, request=request.model_dump(exclude_unset=True)
    )
    

async def delete_personnel_record_history(
    *, session: AsyncSession, id: int
) -> bool:
    return await users_crud.delete_personnel_record_history(session=session, id=id)


async def get_personnel_record_users(
    *, session: AsyncSession, request: PersonnelRecordUsersRequest
) -> PersonnelRecordUsersResponse:
    
    users, total_cnt = await users_crud.get_personnel_record_users(session=session, request=request)

    return PersonnelRecordUsersResponse(
        data=[PersonnelRecordUserResponse(
            id=user.id, 
            name=user.name, 
            gender=user.gender, 
            branch_name=user.branch.name, 
            part_name=user.part.name, 
            weekly_work_days=user.branch.work_policies.weekly_work_days if user.branch.work_policies else 5,
            recent_personnel_record_history_date=user.personnel_record_histories[0].created_at if user.personnel_record_histories else None
        ) for user in users], 
        pagination=PaginationDto(total_record=total_cnt, record_size=request.record_size)
    )
    

async def get_branch_users_name(
    *, session: AsyncSession, request: BaseSearchDto, branch_id: int
) -> UsersNameResponse:
    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if not branch:
        raise NotFoundError(detail=f"{branch_id}번 지점을 찾을 수 없습니다.")
    
    users, total_cnt = await users_crud.get_branch_users(session=session, request=request, branch_id=branch_id)

    return UsersNameResponse(
        data=[UserNameResponse(name=user.name) for user in users], 
        pagination=PaginationDto(total_record=total_cnt, record_size=request.record_size)
    )
