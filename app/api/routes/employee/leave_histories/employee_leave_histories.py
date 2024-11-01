from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.middleware.tokenVerify import get_current_user
from app.models.users.leave_histories_model import LeaveHistories, LeaveHistoriesCreate
from app.models.users.users_model import Users
from app.models.branches.user_leaves_days import UserLeavesDays
from app.models.branches.leave_categories_model import LeaveCategory
from app.enums.users import Status

router = APIRouter()


@router.get("", summary="사원용 - 본인 연차 신청 내역 조회")
async def get_employee_leave_histories(
        date: Optional[date] = Query(None, description="조회할 날짜 (미입력시 이번주)"),
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        # 날짜 계산
        if date is None:
            date_obj = datetime.now().date()
        else:
            date_obj = date

        current_weekday = date_obj.weekday()
        date_start_day = date_obj - timedelta(days=current_weekday)
        date_end_day = date_start_day + timedelta(days=6)

        # 본인의 연차 기록만 조회
        base_query = select(LeaveHistories).where(
            LeaveHistories.deleted_yn == 'N',
            LeaveHistories.user_id == current_user.id,
            LeaveHistories.application_date >= date_start_day,
            LeaveHistories.application_date <= date_end_day
        )

        # 페이징 처리
        skip = (page - 1) * size
        result = await db.execute(
            base_query.order_by(LeaveHistories.created_at.desc())
            .offset(skip)
            .limit(size)
        )
        leave_histories = result.scalars().all()

        # 응답 데이터 포맷팅
        formatted_data = []
        for leave_history in leave_histories:
            # 연차 카테고리 정보 조회
            category_query = select(LeaveCategory).where(
                LeaveCategory.id == leave_history.leave_category_id
            )
            category_result = await db.execute(category_query)
            leave_category = category_result.scalar_one_or_none()

            formatted_data.append({
                "id": leave_history.id,
                "application_date": leave_history.application_date,
                "start_date": leave_history.start_date,
                "end_date": leave_history.end_date,
                "leave_category_name": leave_category.name if leave_category else None,
                "decreased_days": float(leave_history.decreased_days) if leave_history.decreased_days else 0.0,
                "status": leave_history.status,
                "applicant_description": leave_history.applicant_description,
                "admin_description": leave_history.admin_description,
                "approve_date": leave_history.approve_date
            })

        # 전체 개수 조회
        count_query = base_query.with_only_columns(func.count())
        total_count = await db.execute(count_query)
        total_count = total_count.scalar_one()

        return {
            "message": "연차 신청 내역을 조회했습니다.",
            "data": formatted_data,
            "pagination": {
                "total": total_count,
                "page": page,
                "size": size,
                "total_pages": (total_count + size - 1) // size
            }
        }

    except Exception as err:
        print(f"연차 내역 조회 중 오류: {err}")
        raise HTTPException(status_code=500, detail="연차 내역 조회 중 오류가 발생했습니다.")


@router.post("", summary="사원용 - 연차 신청")
async def create_employee_leave_history(
        leave_create: LeaveHistoriesCreate,
        decreased_days: float = Query(..., description="사용할 연차 일수"),
        start_date: date = Query(..., description="시작일"),
        end_date: date = Query(..., description="종료일"),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        # 같은 날짜에 이미 연차 신청이 있는지 확인
        existing_leave = await db.execute(
            select(LeaveHistories).where(
                LeaveHistories.user_id == current_user.id,
                LeaveHistories.start_date <= end_date,
                LeaveHistories.end_date >= start_date,
                LeaveHistories.deleted_yn == "N",
                LeaveHistories.status != "rejected"
            )
        )
        if existing_leave.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"해당 기간({start_date} ~ {end_date})에 이미 신청된 연차가 있습니다."            )

        # 연차 카테고리 확인
        category_query = select(LeaveCategory).where(
            LeaveCategory.id == leave_create.leave_category_id,
            LeaveCategory.branch_id == current_user.branch_id,
            LeaveCategory.deleted_yn == "N"
        )
        category = await db.execute(category_query)
        if not category.scalar_one_or_none():
            # 사용 가능한 카테고리 목록 조회
            available_categories = await db.execute(
                select(LeaveCategory).where(
                    LeaveCategory.branch_id == current_user.branch_id,
                    LeaveCategory.deleted_yn == "N"
                )
            )
            categories = available_categories.scalars().all()
            category_ids = [c.id for c in categories]

            raise HTTPException(
                status_code=404,
                detail=f"유효하지 않은 연차 카테고리입니다. (사용 가능한 카테고리: {category_ids})"
            )

        # 사용 가능한 연차 일수 확인
        leaves_query = select(UserLeavesDays).where(
            UserLeavesDays.user_id == current_user.id,
            UserLeavesDays.deleted_yn == "N"
        )
        user_leaves = await db.execute(leaves_query)
        user_leaves = user_leaves.scalar_one_or_none()

        if not user_leaves or user_leaves.total_leave_days < decreased_days:
            raise HTTPException(
                status_code=400,
                detail=f"연차 잔여일수가 부족합니다. (잔여: {user_leaves.total_leave_days if user_leaves else 0}일)"
            )

        # 연차 신청 생성
        new_leave = LeaveHistories(
            branch_id=current_user.branch_id,
            part_id=current_user.part_id,
            user_id=current_user.id,
            leave_category_id=leave_create.leave_category_id,
            decreased_days=decreased_days,
            start_date=start_date,
            end_date=end_date,
            application_date=datetime.now().date(),
            applicant_description=leave_create.applicant_description,
            status=Status.PENDING
        )

        db.add(new_leave)
        await db.commit()
        await db.refresh(new_leave)

        return {
            "message": "연차 신청이 완료되었습니다.",
            "leave_history_id": new_leave.id
        }

    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print(f"연차 신청 중 오류: {err}")
        if "Duplicate entry" in str(err):
            raise HTTPException(
                status_code=400,
                detail="이미 같은 날짜에 연차 신청이 존재합니다."
            )
        raise HTTPException(status_code=500, detail="연차 신청 중 오류가 발생했습니다.")