from datetime import datetime, date, timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.middleware.tokenVerify import get_current_user, get_current_user_id
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.leave_histories_model import LeaveHistories, LeaveHistoriesCreate, LeaveHistoriesSearchDto, LeaveHistoriesUpdate
from app.models.users.users_model import Users
from app.models.branches.user_leaves_days import UserLeavesDays, UserLeavesDaysResponse
from app.models.branches.leave_categories_model import LeaveCategory
from app.enums.users import Status

router = APIRouter()


# @router.get("", summary="사원용 - 본인 연차 신청 내역 조회")
# async def get_employee_leave_histories(
#         date: Optional[date] = Query(None, description="조회할 날짜 (미입력시 이번주)"),
#         page: int = Query(1, gt=0),
#         size: int = Query(10, gt=0),
#         current_user: Users = Depends(get_current_user),
#         db: AsyncSession = Depends(get_db)
# ):
#     try:
#         # 날짜 계산
#         if date is None:
#             date_obj = datetime.now().date()
#         else:
#             date_obj = date

#         current_weekday = date_obj.weekday()
#         date_start_day = date_obj - timedelta(days=current_weekday)
#         date_end_day = date_start_day + timedelta(days=6)

#         # 본인의 연차 기록만 조회
#         base_query = select(LeaveHistories).where(
#             LeaveHistories.deleted_yn == 'N',
#             LeaveHistories.user_id == current_user.id,
#             LeaveHistories.application_date >= date_start_day,
#             LeaveHistories.application_date <= date_end_day
#         )

#         # 페이징 처리
#         skip = (page - 1) * size
#         result = await db.execute(
#             base_query.order_by(LeaveHistories.created_at.desc())
#             .offset(skip)
#             .limit(size)
#         )
#         leave_histories = result.scalars().all()

#         # 응답 데이터 포맷팅
#         formatted_data = []
#         for leave_history in leave_histories:
#             # 연차 카테고리 정보 조회
#             category_query = select(LeaveCategory).where(
#                 LeaveCategory.id == leave_history.leave_category_id
#             )
#             category_result = await db.execute(category_query)
#             leave_category = category_result.scalar_one_or_none()

#             formatted_data.append({
#                 "id": leave_history.id,
#                 "application_date": leave_history.application_date,
#                 "start_date": leave_history.start_date,
#                 "end_date": leave_history.end_date,
#                 "leave_category_name": leave_category.name if leave_category else None,
#                 "decreased_days": float(leave_history.decreased_days) if leave_history.decreased_days else 0.0,
#                 "status": leave_history.status,
#                 "applicant_description": leave_history.applicant_description,
#                 "admin_description": leave_history.admin_description,
#                 "approve_date": leave_history.approve_date
#             })

#         # 전체 개수 조회
#         count_query = base_query.with_only_columns(func.count())
#         total_count = await db.execute(count_query)
#         total_count = total_count.scalar_one()

#         return {
#             "message": "연차 신청 내역을 조회했습니다.",
#             "data": formatted_data,
#             "pagination": {
#                 "total": total_count,
#                 "page": page,
#                 "size": size,
#                 "total_pages": (total_count + size - 1) // size
#             }
#         }

#     except Exception as err:
#         print(f"연차 내역 조회 중 오류: {err}")
#         raise HTTPException(status_code=500, detail="연차 내역 조회 중 오류가 발생했습니다.")


# @router.post("", summary="사원용 - 연차 신청")
# async def create_employee_leave_history(
#         leave_create: LeaveHistoriesCreate,
#         decreased_days: float = Query(..., description="사용할 연차 일수"),
#         start_date: date = Query(..., description="시작일"),
#         end_date: date = Query(..., description="종료일"),
#         current_user: Users = Depends(get_current_user),
#         db: AsyncSession = Depends(get_db)
# ):
#     try:
#         # 같은 날짜에 이미 연차 신청이 있는지 확인
#         existing_leave = await db.execute(
#             select(LeaveHistories).where(
#                 LeaveHistories.user_id == current_user.id,
#                 LeaveHistories.start_date <= end_date,
#                 LeaveHistories.end_date >= start_date,
#                 LeaveHistories.deleted_yn == "N",
#                 LeaveHistories.status != "rejected"
#             )
#         )
#         if existing_leave.scalar_one_or_none():
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"해당 기간({start_date} ~ {end_date})에 이미 신청된 연차가 있습니다."            )

#         # 연차 카테고리 확인
#         category_query = select(LeaveCategory).where(
#             LeaveCategory.id == leave_create.leave_category_id,
#             LeaveCategory.branch_id == current_user.branch_id,
#             LeaveCategory.deleted_yn == "N"
#         )
#         category = await db.execute(category_query)
#         if not category.scalar_one_or_none():
#             # 사용 가능한 카테고리 목록 조회
#             available_categories = await db.execute(
#                 select(LeaveCategory).where(
#                     LeaveCategory.branch_id == current_user.branch_id,
#                     LeaveCategory.deleted_yn == "N"
#                 )
#             )
#             categories = available_categories.scalars().all()
#             category_ids = [c.id for c in categories]

#             raise HTTPException(
#                 status_code=404,
#                 detail=f"유효하지 않은 연차 카테고리입니다. (사용 가능한 카테고리: {category_ids})"
#             )

#         # 사용 가능한 연차 일수 확인
#         leaves_query = select(UserLeavesDays).where(
#             UserLeavesDays.user_id == current_user.id,
#             UserLeavesDays.deleted_yn == "N"
#         )
#         user_leaves = await db.execute(leaves_query)
#         user_leaves = user_leaves.scalar_one_or_none()

#         if not user_leaves or user_leaves.total_leave_days < decreased_days:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"연차 잔여일수가 부족합니다. (잔여: {user_leaves.total_leave_days if user_leaves else 0}일)"
#             )

#         # 연차 신청 생성
#         new_leave = LeaveHistories(
#             branch_id=current_user.branch_id,
#             part_id=current_user.part_id,
#             user_id=current_user.id,
#             leave_category_id=leave_create.leave_category_id,
#             decreased_days=decreased_days,
#             start_date=start_date,
#             end_date=end_date,
#             application_date=datetime.now().date(),
#             applicant_description=leave_create.applicant_description,
#             status=Status.PENDING
#         )

#         db.add(new_leave)
#         await db.commit()
#         await db.refresh(new_leave)

#         return {
#             "message": "연차 신청이 완료되었습니다.",
#             "leave_history_id": new_leave.id
#         }

#     except HTTPException as http_err:
#         await db.rollback()
#         raise http_err
#     except Exception as err:
#         await db.rollback()
#         print(f"연차 신청 중 오류: {err}")
#         if "Duplicate entry" in str(err):
#             raise HTTPException(
#                 status_code=400,
#                 detail="이미 같은 날짜에 연차 신청이 존재합니다."
#             )
#         raise HTTPException(status_code=500, detail="연차 신청 중 오류가 발생했습니다.")
    
@router.post("", summary="사원용 - 연차 신청", description="사원용 - 연차를 신청합니다.")
async def create_employee_leave_history(
    context: Request,
    leave_create: LeaveHistoriesCreate,
    branch_id: int = Query(description="현재 사용자가 포함된 지점 ID를 입력합니다."),
    decreased_days: float = Query(
        description="사용할 연차 일수를 입력합니다. 타입은 float입니다. 예) 1.0"
    ),
    start_date: date = Query(description="시작일을 입력합니다. 예) YYYY-MM-DD"),
    end_date: date = Query(description="종료일을 입력합니다. 예) YYYY-MM-DD"),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        user_query = select(Users).where(
            Users.id == current_user_id, Users.deleted_yn == "N"
        )
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.branch_id != branch_id:
            raise HTTPException(
                status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다."
            )
            
        if current_user.role not in ["MSO 최고권한", "최고관리자", "통합관리자", "사원"]:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        # LeaveHistories 생성 및 flush
        create = LeaveHistories(
            branch_id=branch_id,
            part_id=current_user.part_id,
            user_id=current_user_id,
            leave_category_id=leave_create.leave_category_id,
            decreased_days=decreased_days,
            increased_days=0.00,
            start_date=start_date,
            end_date=end_date,
            application_date=datetime.now().date(),
            applicant_description=leave_create.applicant_description or None,
            status=Status.PENDING,
        )
        db.add(create)
        await db.flush()
        await db.refresh(create)

        # ID 값을 미리 저장
        leave_history_id = create.id

        # UserLeavesDays 조회
        leave_history_query = select(UserLeavesDays).where(
            UserLeavesDays.user_id == current_user_id, UserLeavesDays.deleted_yn == "N"
        )

        leave_history_result = await db.execute(leave_history_query)
        user_leaves_days_record = leave_history_result.scalar_one_or_none()

        if user_leaves_days_record is None:
            user_leaves_days = UserLeavesDays(
                user_id=current_user_id,
                branch_id=branch_id,
                part_id=current_user.part_id,
                increased_days=0.00,
                decreased_days=0.00,
                deleted_yn="N",
            )
            db.add(user_leaves_days)
            await db.flush()

        await db.commit()

        return {
            "message": "연차 생성에 성공하였습니다.",
            "leave_history_id": leave_history_id,
        }

    except Exception as err:
        await db.rollback()
        print(f"연차 생성 중 오류 발생: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    
@router.get(
    "",
    summary="사원용 - 연차 신청 목록 조회",
    description="사원용 - 연차 신청 목록을 조회합니다.",
)
async def get_employee_leave_histories(
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    search: LeaveHistoriesSearchDto = Depends(),
    date: Optional[date] = Query(
        None,
        description="시작일 계산을 위한 날짜를 입력합니다. 공백인 경우 오늘을 포함한 주의 일요일-토요일 기간을 조회합니다. 예) YYYY-MM-DD",
    ),
    branch_id: Optional[int] = Query(
        None, description="검색할 지점 ID를 입력합니다. 공백인 경우 전체 조회합니다."
    ),
    page: int = Query(
        1, gt=0, description="페이지 번호를 입력합니다. 기본값은 1입니다."
    ),
    size: int = Query(
        10, gt=0, description="페이지당 레코드 수를 입력합니다. 기본값은 10입니다."
    ),
):
    try:
        if current_user.role not in [
            "MSO 최고권한",
            "최고관리자",
            "관리자",
            "통합관리자",
            "사원",
        ]:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        if date is None:
            # 날짜가 없으면 현재 날짜 기준으로 해당 주의 일요일-토요일
            date_obj = datetime.now().date()
            current_weekday = date_obj.weekday()
            # 현재 날짜에서 현재 요일만큼 빼서 일요일을 구함
            date_start_day = date_obj - timedelta(days=current_weekday)
            # 일요일부터 6일을 더해서 토요일을 구함
            date_end_day = date_start_day + timedelta(days=6)
        else:
            date_obj = date
            current_weekday = date_obj.weekday()
            date_start_day = date_obj - timedelta(days=current_weekday)
            date_end_day = date_start_day + timedelta(days=6)

        base_query = select(LeaveHistories).where(
            LeaveHistories.deleted_yn == "N",
            LeaveHistories.application_date >= date_start_day,
            LeaveHistories.application_date <= date_end_day,
        )

        # 사원인 경우 자신의 연차 신청 내역만 조회 가능하도록 필터 추가
        if current_user.role == "사원":
            base_query = base_query.where(LeaveHistories.user_id == current_user.id)

        if base_query is None:
            raise HTTPException(
                status_code=404, detail="연차 신청 목록을 찾을 수 없습니다."
            )

        stmt = None

        if branch_id:
            base_query = base_query.join(
                Branches, LeaveHistories.branch_id == Branches.id
            ).where(Branches.id == branch_id)
        if search.kind:
            base_query = base_query.join(LeaveHistories.leave_category).where(
                LeaveCategory.name.ilike(f"%{search.kind}%")
            )
        if search.status:
            base_query = base_query.where(
                LeaveHistories.status.ilike(f"%{search.status}%")
            )

        skip = (page - 1) * size
        stmt = (
            base_query.order_by(LeaveHistories.created_at.desc())
            .offset(skip)
            .limit(size)
        )

        result = await db.execute(stmt)
        leave_histories = result.scalars().all()

        formatted_data = []
        for leave_history in leave_histories:
            user_result = await db.execute(
                select(Users, Branches, Parts)
                .join(Branches, Users.branch_id == Branches.id)
                .join(Parts, Users.part_id == Parts.id)
                .where(Users.id == leave_history.user_id)
            )
            user, branch, part = user_result.first()
            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"사용자 ID {leave_history.user_id}에 대한 정보를 찾을 수 없습니다.",
                )

            category_query = select(LeaveCategory).where(
                LeaveCategory.id == leave_history.leave_category_id
            )
            category_result = await db.execute(category_query)
            leave_category = category_result.scalar_one_or_none()

            leave_history_data = {
                "id": leave_history.id,
                "search_branch_id": branch.id,
                "branch_name": branch.name,
                "user_id": user.id,
                "user_name": user.name,
                "part_id": part.id,
                "part_name": part.name,
                "application_date": leave_history.application_date,
                "start_date": leave_history.start_date,
                "end_date": leave_history.end_date,
                "leave_category_id": leave_history.leave_category_id,
                "leave_category_name": leave_category.name,
                "decreased_days": (
                    float(leave_history.decreased_days)
                    if leave_history.decreased_days is not None
                    else 0.0
                ),
                "status": leave_history.status,
                "applicant_description": leave_history.applicant_description,
                "manager_id": leave_history.manager_id,
                "manager_name": leave_history.manager_name,
                "admin_description": leave_history.admin_description,
                "approve_date": leave_history.approve_date,
            }
            formatted_data.append(leave_history_data)

        # 전체 레코드 수 계산
        count_query = base_query.with_only_columns(func.count())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar_one()

        return {
            "list": formatted_data,
            "pagination": {
                "total": total_count,
                "page": page,
                "size": size,
                "total_pages": (total_count + size - 1) // size,
            },
            "message": "연차 신청 목록을 정상적으로 조회하였습니다.",
        }

    except Exception as err:
        print(f"에러가 발생하였습니다: {err}")
        raise HTTPException(status_code=500, detail=str(err))

# 현재 사용자의 연차 일수 정보 조회
@router.get(
    "/current-user-leaves",
    response_model=UserLeavesDaysResponse,
    summary="사원용 - 현재 사용자의 연차 일수 정보 조회",
    description="사원용 - 현재 사용자의 연차 일수 정보를 조회합니다.",
)
async def get_current_user_leaves(
    *,
    branch_id: Annotated[int, Query(description="지점 ID를 입력합니다.")],
    year: Annotated[
        Optional[int], Query(description="연도를 입력합니다. 예) 2024")
    ] = None,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        if year is None:
            year = date.today().year

        # 해당 연도의 시작일과 종료일 설정
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        # 모든 기록 조회
        leave_query = (
            select(UserLeavesDays)
            .where(
                UserLeavesDays.user_id == current_user_id,
                UserLeavesDays.branch_id == branch_id,
                UserLeavesDays.deleted_yn == "N",
                UserLeavesDays.created_at >= start_date,
                UserLeavesDays.created_at <= end_date,
            )
            .order_by(UserLeavesDays.created_at.desc())
        )
        result = await db.execute(leave_query)
        leave_info = result.scalar_one_or_none()

        user_query = select(Users).where(Users.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not leave_info:
            return {
                "user_id": current_user_id,
                "branch_id": branch_id,
                "year": year,
                "increased_days": 0.0,
                "decreased_days": 0.0,
                "total_leave_days": user.total_leave_days,
                "message": f"{year}년도의 연차 정보가 없습니다.",
            }

        # 모든 increased_days 합산
        total_increased = (
            float(leave_info.increased_days)
            if leave_info.increased_days is not None
            else 0.0
        )
        total_decreased = (
            float(leave_info.decreased_days)
            if leave_info.decreased_days is not None
            else 0.0
        )

        return UserLeavesDaysResponse(
            user_id=current_user_id,
            branch_id=branch_id,
            year=year,
            increased_days=float(leave_info.increased_days),
            decreased_days=float(leave_info.decreased_days),
            total_leave_days=total_increased - float(leave_info.decreased_days),
        )

    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))

@router.patch(
    "/{leave_id}", summary="사원용 - 연차 수정", description="사원용 - 연차를 수정합니다."
)
async def update_employee_leave(
    leave_update: LeaveHistoriesUpdate,
    branch_id: int = Query(description="현재 사용자가 포함된 지점 ID를 입력합니다."),
    leave_id: int = Path(description="수정할 연차 ID를 입력합니다."),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        user_query = select(Users).where(
            Users.id == current_user_id, Users.deleted_yn == "N"
        )
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.branch_id != branch_id:
            raise HTTPException(
                status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다."
            )

        query = select(LeaveHistories).where(
            LeaveHistories.id == leave_id,
            LeaveHistories.branch_id == branch_id,
            LeaveHistories.deleted_yn == "N",
        )
        result = await db.execute(query)
        leave_history = result.scalar_one_or_none()

        if not leave_history:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

        # 현재 사용자의 user_id와 연차 기록의 user_id가 일치하는지 확인
        if leave_history.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="연차를 수정할 권한이 없습니다."
            )

        if leave_update.leave_category_id:
            leave_history.leave_category_id = leave_update.leave_category_id
        if leave_update.date:
            leave_history.application_date = leave_update.date
        if leave_update.applicant_description:
            leave_history.applicant_description = leave_update.applicant_description

        await db.commit()
        return {"message": "연차 수정에 성공하였습니다."}

    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.delete(
    "/{leave_id}", summary="사원용 - 연차 삭제", description="사원용 - 연차를 삭제합니다."
)
async def delete_employee_leave(
    branch_id: int = Query(
        ..., description="현재 사용자가 포함된 지점 ID를 입력합니다."
    ),
    leave_id: int = Path(..., description="삭제할 연차 ID를 입력합니다."),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        user_query = select(Users).where(
            Users.id == current_user_id, Users.deleted_yn == "N"
        )
        user_result = await db.execute(user_query)
        current_user = user_result.scalar_one_or_none()

        if current_user.role.strip() == "MSO 관리자":
            pass
        elif current_user.branch_id != branch_id:
            raise HTTPException(
                status_code=403, detail="다른 지점의 정보에 접근할 수 없습니다."
            )

        query = select(LeaveHistories).where(
            LeaveHistories.id == leave_id,
            LeaveHistories.branch_id == branch_id,
            LeaveHistories.deleted_yn == "N",
        )
        result = await db.execute(query)
        leave_history = result.scalar_one_or_none()

        if not leave_history:
            raise HTTPException(status_code=404, detail="해당 연차를 찾을 수 없습니다.")

        if (
            leave_history.request_user_id != current_user.id
            and current_user.role.strip()
            not in ["MSO 최고권한", "최고관리자", "통합관리자"]
        ):
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