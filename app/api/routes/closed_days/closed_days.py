from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, extract

from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user_id, validate_token
from app.models.closed_days.closed_days_model import ClosedDays, ClosedDayCreate, ClosedDayUpdate
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


# 휴일 생성
@router.post("/{branch_id}/closed_days")
async def create_closed_day(branch_id : int, closed_day: ClosedDayCreate, token=Annotated[Users, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자" :
            raise HTTPException(status_code=403, detail="생성 권한이 없습니다.")
        
        new_closed_day = ClosedDays(
            branch_id=branch_id,
            closed_day_date=closed_day.closed_day_date,
            memo=closed_day.memo,
        )

        await db.add(new_closed_day)
        await db.commit()
        await db.refresh(new_closed_day)

        return {
            "message": "휴무일이 성공적으로 생성되었습니다."
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일이 생성에 오류가 발생하였습니다.")


# 휴일 전체 조회
@router.get("/closed_days/{date}")
async def get_closed_days(date : datetime, token=Annotated[Users, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="생성 권한이 없습니다.")
        
        date_year = datetime.strptime(date, "%Y").date()
        date_month = datetime.strptime(date, "%m").date()
        

        stmt = select(ClosedDays).where(extract("year", ClosedDays.created_at) == date_year, extract("month", ClosedDays.created_at) == date_month, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 전체 조회에 실패하였습니다.")
    
# 휴일 삭제리스트 전체 조회
@router.get("/closed_days/deleted")
async def get_closed_days():
    try:
        stmt = select(ClosedDays).where(ClosedDays.deleted_yn == "Y")
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 삭제 정보가 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 삭제리스트 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 전체 조회에 실패하였습니다.")


# 휴일 지점별 조회
@router.get("/{branch_id}/closed_days")
async def get_closed_days(branch_id : int):
    try:
        now_date_year = datetime.now().year
        now_date_month = datetime.now().month
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, now_date_year, now_date_month, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 지점별 조회에 실패하였습니다.")
    
# # 휴일 파트별 조회
# @router.get("/{branch_id}/closed_days")
# async def get_closed_days(branch_id : int):
#     try:
#         now_date_year = datetime.now().year
#         now_date_month = datetime.now().month
#         stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, now_date_year, now_date_month, ClosedDays.deleted_yn == "N")
#         result = await db.execute(stmt)
#         closed_days = result.scalars().all()

#         if len(closed_days) == 0:
#             raise HTTPException(
#                 status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
#             )

#         return {
#             "message": "휴무일 목록을 성공적으로 전체 조회하였습니다.",
#             "data": closed_days,
#         }
#     except Exception as err:
#         print(err)
#         raise HTTPException(status_code=500, detail="휴무일 전체 조회에 실패하였습니다.")
    
# 휴일 목록 상세 조회
@router.get("/{branch_id}/closed_days/{id}")
async def get_closed_days(branch_id : int, id : int):
    try:
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalar_one_or_none()

        if not closed_days:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 목록을 성공적으로 상세 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 상세 조회에 실패하였습니다.")
    

# 휴일 삭제리스트 상세 조회
@router.get("/{branch_id}/closed_days/deleted/{id}")
async def get_closed_days(branch_id : int, id : int):
    try:
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.id == id, ClosedDays.deleted_yn == "Y")
        result = await db.execute(stmt)
        closed_days = result.scalar_one_or_none()

        if not closed_days:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 삭제 정보가 존재하지 않습니다."
            )

        return {
            "message": "성공적으로 삭제리스트 상세 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 상세 조회에 실패하였습니다.")
    
    

# 휴무일 수정
@router.patch("/{branch_id}/closed_days/{id}")
async def update_closed_day(branch_id: int, id : int, closed_day_update: ClosedDayUpdate, token=Annotated[Users, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자" :
            raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")
        
        find_one_closed_day = await db.execute(select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N"))
        result = find_one_closed_day.scalar_one_or_none()

        if not result:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )
        
        result.closed_day_date == closed_day_update.closed_day_date if(closed_day_update.closed_day_date != None) else result.closed_day_date
        result.memo = closed_day_update.memo

        await db.commit()

        return {
            "message": "휴무일 정보가 성공적으로 업데이트되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 수정에 실패하였습니다.")


# 휴무일 삭제
@router.delete("/{branch_id}/closed_days/{id}")
async def delete_closed_day(branch_id: int, id : int, token=Annotated[Users, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자":
            raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")
        # 휴무일 존재 여부 확인
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_day = result.scalar_one_or_none()

        if not closed_day:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )

        await db.delete(closed_day)
        await db.commit()

        return {
            "message": "휴무일이 성공적으로 삭제되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 삭제에 실패하였습니다.")
    


# 휴무일 소프트 삭제
@router.patch("/{branch_id}/closed_days/softdelete/{id}")
async def delete_closed_day(branch_id: int, id : int, token=Annotated[Users, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자" :
            raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")
        # 휴무일 존재 여부 확인
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_day = result.scalar_one_or_none()

        if not closed_day:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )
        
        closed_day.deleted_yn = "Y"

        await db.commit()

        return {
            "message": "휴무일이 성공적으로 삭제되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 삭제에 실패하였습니다.")


# 휴무일 복구
@router.patch("/{branch_id}/closed_days/restore/{id}")
async def delete_closed_day(branch_id: int, id : int, token=Annotated[Users, Depends(validate_token)]):
    try:
        if token.role != "MSO 최고권한" | token.role != "최고관리자" :
            raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")
        # 휴무일 존재 여부 확인
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_day = result.scalar_one_or_none()

        if not closed_day:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )
        
        closed_day.deleted_yn = "Y"

        await db.commit()

        return {
            "message": "휴무일이 성공적으로 삭제되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 삭제에 실패하였습니다.")