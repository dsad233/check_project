from datetime import UTC, date, datetime, time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update

from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user_id, validate_token
from app.models.users.overtimes_model import OvertimeCreate, Overtimes

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


# 초과 근무 생성
@router.post("/overtimes")
async def create_overtime(overtime: OvertimeCreate, current_user_id: int = Depends(get_current_user_id)):
    try:
        # 현재 날짜의 시작과 끝 시간 계산
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # 같은 날짜에 이미 초과 근무 기록이 있는지 확인
        existing_overtime = await db.execute(
            select(Overtimes).where(
                Overtimes.applicant_id == current_user_id,
                Overtimes.created_at >= today_start,
                Overtimes.created_at <= today_end,
            )
        )
        existing_overtime = existing_overtime.scalar_one_or_none()
        
        if existing_overtime:
            raise HTTPException(status_code=400, detail="이미 초과 근무 기록이 있습니다.")
        
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
        

