from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from datetime import datetime, date, timedelta
from typing import Optional

from app.core.database import async_session
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.models.users.leave_histories_model import LeaveHistories, LeaveHistoriesResponse, LeaveHistoriesCreate, LeaveHistoriesListResponse, LeaveHistoriesSearchDto, LeaveHistoriesApprove, LeaveHistoriesUpdate
from app.models.branches.user_leaves_days import UserLeavesDays, UserLeavesDaysResponse
from app.models.users.users_model import Users
from app.common.dto.pagination_dto import PaginationDto
from app.enums.users import StatusKor

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

# 현재 사용자의 연차 일수 정보 조회
@router.get("/current-user-leaves", response_model=UserLeavesDaysResponse)
async def get_current_user_leaves(
    *,
    branch_id: int,
    year: Optional[int] = None,
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        # 연도가 지정되지 않은 경우 현재 연도 사용
        if year is None:
            year = date.today().year

        # 연차 정보 조회
        leave_query = select(UserLeavesDays).where(
            UserLeavesDays.user_id == current_user_id,
            UserLeavesDays.branch_id == branch_id,
            UserLeavesDays.deleted_yn == 'N'
        ).order_by(UserLeavesDays.created_at.desc())
        leave_result = await db.execute(leave_query)
        leave_info = leave_result.first()

        if not leave_info:
            raise HTTPException(status_code=404, detail="해당 연도의 연차 정보를 찾을 수 없습니다.")

        return UserLeavesDaysResponse(
            user_id=current_user_id,
            branch_id=branch_id, 
            year=year,
            increased_days=float(leave_info.increased_days),
            decreased_days=float(leave_info.decreased_days),
            total_leave_days=float(leave_info.total_leave_days),
            leave_category_id=leave_info.leave_category_id
        )

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

@router.get("/list", response_model=LeaveHistoriesListResponse)
async def get_leave_histories(
    search: LeaveHistoriesSearchDto = Depends(), # 검색 조건
    start: Optional[date] = None, # 시작일
    end: Optional[date] = None, # 종료일
    branch: Optional[int] = None, # 지점
    part: Optional[str] = None, # 파트
    search_name: Optional[str] = None, # 이름
    search_phone: Optional[str] = None, # 전화번호
    current_user_id: int = Depends(get_current_user_id)
) -> LeaveHistoriesListResponse:
    try:
        # 사용자 권한 확인
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 최고권한":
            pass

        # 쿼리 구성
        query = select(LeaveHistories).options(
            joinedload(LeaveHistories.user).joinedload(Users.part),
            joinedload(LeaveHistories.user),
            joinedload(LeaveHistories.leave_category),
            joinedload(LeaveHistories.branch)
        ).where(
            LeaveHistories.deleted_yn == 'N'
        )
        
        if branch:
            query = query.filter(LeaveHistories.branch_id.like(f"%{branch}%"))
        
        # 기존 필터 적용
        if search.kind:
            query = query.join(LeaveHistories.leave_category).filter(LeaveHistories.leave_category.has(name=search.kind))
        if search.status:
            query = query.filter(LeaveHistories.status == search.status)

        # 새로운 필터 적용
        if start and end:
            query = query.filter(LeaveHistories.application_date.between(start, end))
        if part:
            query = query.join(LeaveHistories.user).join(Users.part).filter(Users.part.has(name=part))
        if search_name:
            query = query.join(LeaveHistories.user).filter(Users.name.ilike(f"%{search_name}%"))
        if search_phone:
            query = query.join(LeaveHistories.user).filter(Users.phone_number.ilike(f"%{search_phone}%"))

        # 전체 레코드 수 계산
        count_query = query.with_only_columns(func.count())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar_one()

        # 페이지네이션 적용
        query = query.offset(search.offset).limit(search.record_size)

        # 결과 조회
        result = await db.execute(query)
        leave_histories = result.scalars().all()

        leave_history_dtos = []
        for history in leave_histories:
            dto = LeaveHistoriesResponse(
                id=history.id,
                branch_name=history.branch.name,
                user_name=history.user.name,
                part_name=history.user.part.name,
                application_date=history.application_date,
                leave_category_name=history.leave_category.name,
                decreased_days=float(history.decreased_days) if history.decreased_days is not None else 0.0,
                status=history.status,
                applicant_description=history.applicant_description,
                admin_description=history.admin_description,
                approve_date=history.approve_date
            )
            leave_history_dtos.append(dto)

        pagination = PaginationDto(total_record=total_count)
        leave_list_response = LeaveHistoriesListResponse(list=leave_history_dtos, pagination=pagination)
        return leave_list_response

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.post("")
async def create_leave_history(
    branch_id: int,
    leave_create: LeaveHistoriesCreate,
    decreased_days: float,
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")

        create = LeaveHistories(
            branch_id=branch_id,
            user_id=current_user.id,
            leave_category_id=leave_create.leave_category_id,
            decreased_days=decreased_days,
            application_date=leave_create.date,
            applicant_description=leave_create.applicant_description or None,
            status = "확인중"
        )

        db.add(create)
        await db.flush()
        
        user_leaves_days = UserLeavesDays(
            user_id=current_user.id,
            branch_id=branch_id,
            leave_category_id=leave_create.leave_category_id,
            increased_days=0.00,
            decreased_days=decreased_days,
            description=leave_create.applicant_description or None,
            is_paid=False,
            is_approved=True,
            leave_history_id=create.id
        )
        
        db.add(user_leaves_days)
        
        await db.commit()
        return {"message": "연차 생성에 성공하였습니다."}
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/{leave_id}")
async def approve_leave(
    leave_id: int,
    branch_id: int,
    leave_approve: LeaveHistoriesApprove,
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.role.strip() == "사원":
            raise HTTPException(status_code=403, detail="사원은 연차를 승인할 수 없습니다.")
        elif current_user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")

        query = select(LeaveHistories).where(LeaveHistories.id == leave_id, LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == 'N')
        result = await db.execute(query)
        leave_history = result.scalar_one_or_none()

        if not leave_history:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

        now = datetime.now().date()
        
        if leave_history.application_date >= now:
            leave_history.status = leave_approve.status
            leave_history.admin_description = leave_approve.admin_description or None
            leave_history.approve_date = datetime.now()
            await db.commit()
            return {"message": "연차 승인/반려에 성공하였습니다."}
        else:
            raise HTTPException(status_code=400, detail="날짜가 지났습니다.")
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


# @router.patch("/{leave_id}")
# async def update_leave(
#     branch_id: int,
#     leave_id: int,
#     leave_update: LeaveHistoriesUpdate,
#     current_user_id: int = Depends(get_current_user_id),
# ):
#     try:
#         user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
#         user_result = await db.execute(user_query)
#         current_user = user_result.scalar_one_or_none()

#         if current_user.role.strip() == "MSO 관리자":
#             pass
#         elif current_user.branch_id != branch_id:
#             raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")

#         query = select(LeaveHistories).where(LeaveHistories.id == leave_id, LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == 'N')
#         result = await db.execute(query)
#         leave_history = result.scalar_one_or_none()

#         if not leave_history:
#             raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

#         if leave_history.user_id != current_user.id and current_user.role.strip() not in ["MSO 최고권한", "최고관리자", "통합관리자"]:
#             raise HTTPException(status_code=403, detail="연차를 삭제할 권한이 없습니다.")

#         if leave_history.status.strip() != "확인중":
#             raise HTTPException(status_code=400, detail="승인/반려된 연차는 삭제할 수 없습니다.")

#         if leave_update.leave_category_id:
#             leave_history.leave_category_id = leave_update.leave_category_id
#         if leave_update.date:
#             leave_history.application_date = leave_update.date
#         if leave_update.applicant_description:
#             leave_history.applicant_description = leave_update.applicant_description
            
#         await db.commit()
#         return {"message": "연차 수정에 성공하였습니다."}
#     except Exception as err:
#         await db.rollback()
#         print(err)
#         raise HTTPException(status_code=500, detail=str(err))



@router.patch("/{leave_id}")
async def update_leave(
    branch_id: int,
    leave_id: int,
    leave_update: LeaveHistoriesUpdate,
    current_user_id: int = Depends(get_current_user_id),
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")

        query = select(LeaveHistories).where(LeaveHistories.id == leave_id, LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == 'N')
        result = await db.execute(query)
        leave_history = result.scalar_one_or_none()

        if not leave_history:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

        is_admin = current_user.role.strip() in ["MSO 최고권한", "최고관리자", "통합관리자"]

        if leave_history.user_id != current_user.id and not is_admin:
            raise HTTPException(status_code=403, detail="연차를 수정할 권한이 없습니다.")

        status_changed = False
        new_status = None
        if leave_update.status:
            if leave_update.status not in [status.value for status in StatusKor]:
                raise HTTPException(status_code=400, detail="유효하지 않은 상태값입니다.")
            
            if leave_history.status != leave_update.status:
                status_changed = True
                new_status = leave_update.status
                leave_history.status = new_status
                raise HTTPException(status_code=400, detail="유효하지 않은 상태값입니다.")
            
            if leave_history.status == StatusKor.PENDING.value:
                if leave_update.status in [StatusKor.APPROVED.value, StatusKor.REJECTED.value] and not is_admin:
                    raise HTTPException(status_code=403, detail="승인 또는 반려는 관리자만 가능합니다.")
            elif leave_history.status in [StatusKor.APPROVED.value, StatusKor.REJECTED.value]:
                if not is_admin:
                    raise HTTPException(status_code=400, detail="승인/반려된 연차는 관리자만 수정할 수 있습니다.")
            
            leave_history.status = leave_update.status

        if leave_update.leave_category_id:
            leave_history.leave_category_id = leave_update.leave_category_id
        if leave_update.date:
            leave_history.application_date = leave_update.date
        if leave_update.applicant_description:
            leave_history.applicant_description = leave_update.applicant_description
        if leave_update.approver_description and is_admin:
            leave_history.approver_description = leave_update.approver_description
            
        await db.commit()
        
        if status_changed:
            if new_status == StatusKor.PENDING.value:
                return {"message": "연차가 확인중 상태로 변경되었습니다."}
            elif new_status == StatusKor.APPROVED.value:
                return {"message": "연차가 승인되었습니다."}
            elif new_status == StatusKor.REJECTED.value:
                return {"message": "연차가 반려되었습니다."}
        else:
            return {"message": "연차 수정에 성공하였습니다."}
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

@router.delete("/{leave_id}")
async def delete_leave(
    branch_id: int, leave_id: int, current_user_id: int = Depends(get_current_user_id)
):
    try:
        user_query = select(Users).where(Users.id == current_user_id, Users.deleted_yn == 'N')
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.branch_id != branch_id:
            raise HTTPException(status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다.")

        query = select(LeaveHistories).where(LeaveHistories.id == leave_id, LeaveHistories.branch_id == branch_id, LeaveHistories.deleted_yn == 'N')
        result = await db.execute(query)
        leave_history = result.scalar_one_or_none()

        if not leave_history:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

        if leave_history.user_id != current_user.id and current_user.role.strip() not in ["MSO 최고권한", "최고관리자", "통합관리자"]:
            raise HTTPException(
                status_code=403, detail="연차를 삭제할 권한이 없습니다."
            )

        if leave_history.status.strip() != "확인중":
            raise HTTPException(
                status_code=400, detail="승인/반려된 연차는 삭제할 수 없습니다."
            )

        leave_history.deleted_yn = "Y"
        await db.commit()
        return {"message": "연차 삭제에 성공하였습니다."}
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))
