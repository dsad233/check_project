from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update

from app.api.routes.closed_days.schema.closed_day_schema import ClosedDayCreate, ClosedDayUpdate
from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user_id, validate_token
from app.models.closed_days.closed_days_model import ClosedDays
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


# 휴일 생성
@router.post("")
async def create_closed_day(closed_day: ClosedDayCreate, current_user_id: dict = Depends(get_current_user_id)):
    try:
        stmt = select(Users).where(Users.id == current_user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        new_closed_day = ClosedDays(
            branch_id=user.branch_id,
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


# 휴일 목록 조회
@router.get("")
async def get_closed_days():
    try:
        stmt = select(ClosedDays)
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        return {
            "message": "휴무일 목록을 성공적으로 조회했습니다.",
            "data": closed_days,
        }
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 휴무일 수정
@router.patch("/{closed_day_id}")
async def update_closed_day(closed_day_id: int, closed_day_update: ClosedDayUpdate):
    try:
        # 업데이트할 필드만 선택
        update_data = closed_day_update.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400, detail="업데이트할 정보가 제공되지 않았습니다."
            )

        # 휴무일 존재 여부 확인
        stmt = select(ClosedDays).where(ClosedDays.id == closed_day_id)
        result = await db.execute(stmt)
        closed_day = result.scalars().first()

        if not closed_day:
            raise HTTPException(
                status_code=404, detail="해당 ID의 휴무일이 존재하지 않습니다."
            )

        # 휴무일 정보 업데이트
        update_stmt = (
            update(ClosedDays)
            .where(ClosedDays.id == closed_day_id)
            .values(**update_data)
        )
        await db.execute(update_stmt)
        await db.commit()

        return {
            "message": "휴무일 정보가 성공적으로 업데이트되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 휴무일 삭제
@router.delete("/{closed_day_id}")
async def delete_closed_day(closed_day_id: int):
    try:
        # 휴무일 존재 여부 확인
        stmt = select(ClosedDays).where(ClosedDays.id == closed_day_id)
        result = await db.execute(stmt)
        closed_day = result.scalars().first()

        if not closed_day:
            raise HTTPException(
                status_code=404, detail="해당 ID의 휴무일이 존재하지 않습니다."
            )

        # 휴무일 삭제
        update_stmt = (
            update(ClosedDays)
            .where(ClosedDays.id == closed_day_id)
            .values(deleted_yn="Y", updated_at=datetime.now(UTC))
        )
        await db.execute(update_stmt)
        await db.commit()

        return {
            "message": "휴무일이 성공적으로 삭제되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
