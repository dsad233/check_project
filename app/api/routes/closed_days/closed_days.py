from fastapi import APIRouter, Depends, HTTPException

from app.api.routes.closed_days.schema.closed_day_schema import ClosedDayCreate
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


# 휴일 생성
@router.post("")
async def create_closed_day(closed_day: ClosedDayCreate):
    try:
        new_closed_day = ClosedDays(
            closed_day_date=closed_day.closed_day_date,
            memo=closed_day.memo,
        )

        db.add(new_closed_day)
        await db.commit()
        await db.refresh(new_closed_day)

        return {
            "message": "휴무일이 성공적으로 생성되었습니다.",
            "data": new_closed_day,
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
