from datetime import UTC, datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.enums.users import Status
from app.middleware.tokenVerify import get_current_user, get_current_user_id
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.overtimes_model import OvertimeCreate, Overtimes
from app.models.users.users_model import Users


router = APIRouter()


@router.post("", response_model=dict, summary="사원용 - 초과근무 신청")
async def create_employee_overtime(
        overtime: OvertimeCreate,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    try:        
        existing_overtime = await db.execute(
            select(Overtimes)
            .where(
                Overtimes.status.in_([Status.PENDING, Status.APPROVED]),
                Overtimes.applicant_id == current_user.id,
                Overtimes.application_date == datetime.now(UTC).date(),
                Overtimes.deleted_yn == "N"
            )
            .order_by(Overtimes.created_at.desc())
        )

        result_existing_overtime = existing_overtime.first()

        if result_existing_overtime is not None:
            raise HTTPException(status_code=400, detail=f"이미 처리중이거나 승인된 초과근무 신청이 있습니다.")
            
        new_overtime = Overtimes(
            applicant_id=current_user.id,
            application_date = overtime.application_date,
            overtime_hours=overtime.overtime_hours,
            application_memo=overtime.application_memo,
        )

        db.add(new_overtime)
        await db.commit()
        
        return {
            "message": "초과 근무 기록이 성공적으로 생성되었습니다.",
        }
        
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다. Error : {str(err)}")


@router.get("", summary="사원용 - 본인 초과근무 내역 조회")
async def get_employee_overtimes(
        date: Optional[date] = None,
        page: int = 1,
        size: int = 10,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        # 날짜 계산
        if date is None:
            date_obj = datetime.now().date()
        else:
            date_obj = date

        current_weekday = (date_obj.weekday() + 1) % 7
        date_start_day = date_obj - timedelta(days=current_weekday)
        date_end_day = date_start_day + timedelta(days=6)

        # 본인의 기록만 조회
        base_query = select(Overtimes).where(
            Overtimes.deleted_yn == "N",
            Overtimes.applicant_id == current_user.id,
            Overtimes.application_date >= date_start_day,
            Overtimes.application_date <= date_end_day
        )

        # 페이징 처리
        skip = (page - 1) * size
        result = await db.execute(
            base_query.order_by(Overtimes.created_at.desc())
            .offset(skip)
            .limit(size)
        )
        overtimes = result.scalars().all()

        formatted_data = []
        for overtime in overtimes:
            user_query = select(Users, Branches, Parts).join(
                Branches, Users.branch_id == Branches.id
            ).join(
                Parts, Users.part_id == Parts.id
            ).where(Users.id == overtime.applicant_id)
            
            user_result = await db.execute(user_query)
            user, branch, part = user_result.first()
            
            overtime_data = {
                "id": overtime.id,
                "applicant_id": user.id,
                "user_name": user.name,
                "user_phone_number": user.phone_number,
                "user_gender": user.gender,
                "user_hire_date": user.hire_date,
                "user_resignation_date": user.resignation_date,
                "branch_id": branch.id,
                "branch_name": branch.name,
                "part_id": part.id,
                "part_name": part.name,
                "application_date": overtime.application_date,
                "overtime_hours": overtime.overtime_hours,
                "application_memo": overtime.application_memo,
                "manager_memo": overtime.manager_memo,
                "status": overtime.status,
                "manager_id": overtime.manager_id,
                "manager_name": overtime.manager_name,
                "processed_date": overtime.processed_date,
                "is_approved": overtime.is_approved
            }
            formatted_data.append(overtime_data)

        # 전체 레코드 수 조회
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await db.execute(count_query)
        total_count = total_count.scalar_one()

        return {
            "message": "초과 근무 기록을 정상적으로 조회하였습니다.",
            "pagination": {
                "total": total_count,
                "page": page,
                "size": size,
                "total_pages": (total_count + size - 1) // size,
            },
            "data": formatted_data,
        }

    except Exception as err:
        raise HTTPException(status_code=500, detail="초과 근무 조회 중 오류가 발생했습니다.")