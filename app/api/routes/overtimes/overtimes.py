from datetime import UTC, date, datetime, time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update

from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user, get_current_user_id, validate_token
from app.models.users.overtimes_model import OvertimeCreate, Overtimes
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


# 초과 근무 생성
@router.post("")
async def create_overtime(overtime: OvertimeCreate, current_user_id: int = Depends(get_current_user_id)):
    try:        
        new_overtime = Overtimes(
            applicant_id=current_user_id,
            overtime_hours=overtime.overtime_hours,
            application_memo=overtime.application_memo,
        )

        db.add(new_overtime)
        await db.commit()
        await db.refresh(new_overtime)
        
        return {
            "message": "초과 근무 기록이 성공적으로 생성되었습니다.",
            "data": new_overtime,
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
        

# 초과 근무 목록 조회
@router.get("")
async def get_overtimes(current_user: Users = Depends(get_current_user), skip: int = 0, limit: int = 100):
    try:
        stmt = None
        if current_user.role == "사원":
            stmt = (
                select(Overtimes)
                .where((Overtimes.applicant_id == current_user.id) & (Overtimes.deleted_yn == "N"))
                .order_by(Overtimes.application_date.desc())
                .offset(skip)
                .limit(limit)
            )
        else:
            stmt = (
                select(Overtimes)
                .where((Overtimes.deleted_yn == "N"))
                .order_by(Overtimes.application_date.desc())
                .offset(skip)
                .limit(limit)
            )

        if stmt is None:
            raise HTTPException(status_code=400, detail="권한이 없습니다.")
        
        result = await db.execute(stmt)
        overtimes = result.scalars().all()

        count_query = select(func.count()).select_from(Overtimes).where(Overtimes.deleted_yn == "N")
        total_count = await db.execute(count_query)
        total_count = total_count.scalar_one()

        return {
            "message": "초과 근무 기록을 정상적으로 조회하였습니다.",
            "data": overtimes,
            "total": total_count,
            "skip": skip,
            "limit": limit,
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")