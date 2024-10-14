from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from app.middleware.tokenVerify import validate_token, get_current_user_id
from app.api.routes.commutes.schema.commute_schema import CommuteCreate, CommuteResponse
from app.core.database import async_session
from app.models.models import Commutes

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


# 출퇴근 기록 생성
@router.post("")
async def create_clock_in(
    commute: CommuteCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        new_commute = Commutes(
            user_id=current_user_id,
            clock_in=commute.clock_in,
        )

        db.add(new_commute)
        await db.commit()
        await db.refresh(new_commute)

        return {
            "message": "출근 기록이 성공적으로 생성되었습니다.",
            "data": new_commute,
        }
    
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 출퇴근 기록 목록 조회
@router.get("")
async def get_commute_records(
    current_user_id: int = Depends(get_current_user_id),
    skip: int = 0,
    limit: int = 100
):
    try:
        # 전체 출퇴근 기록 수 조회
        count_query = select(func.count()).select_from(Commutes).where(Commutes.deleted_yn == "N")
        total_count = await db.execute(count_query)
        total_count = total_count.scalar_one()

        stmt = (
            select(Commutes)
            .where((Commutes.user_id == current_user_id) & (Commutes.deleted_yn == "N"))
            .order_by(Commutes.clock_in.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        commutes = result.scalars().all()

        return {
            "message": "출퇴근 기록을 정상적으로 전체 조회를 완료하였습니다.",
            "data": commutes,
            "total": total_count,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")