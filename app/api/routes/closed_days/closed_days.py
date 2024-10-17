from datetime import UTC, datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import select, extract

from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user, validate_token
from app.models.closed_days.closed_days_model import ClosedDays, ClosedDayCreate, ClosedDayUpdate
from app.models.branches.work_policies_model import WorkPolicies
from app.models.users.users_model import Users
from calendar import monthrange, weekday

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


# 휴무일 지점 생성
@router.post("/{branch_id}/closed_days")
async def create_branch_closed_day(branch_id : int, closed_day: ClosedDayCreate, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role.strip() != "최고관리자") :
            raise HTTPException(status_code=403, detail="생성 권한이 없습니다.")

        new_closed_day = ClosedDays(
            branch_id=branch_id,
            user_id = token.id,
            closed_day_date=closed_day.closed_day_date,
            memo=closed_day.memo,
        )

        db.add(new_closed_day)
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
        raise HTTPException(status_code=500, detail="휴무일 생성에 실패하였습니다.")

# 휴무일 파트 생성
@router.post("/{branch_id}/parts/{part_id}/closed_days/{user_id}")
async def create_part_closed_day(branch_id : int, part_id : int, user_id : int, closed_day: ClosedDayCreate, token : Annotated[Users, Depends(get_current_user)]):
    try:

        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id or token.part_id != part_id and token.role.strip() not in ["최고관리자", "관리자", "사원", "통합 관리자"]):
            raise HTTPException(status_code=400, detail="생성 권한이 없습니다.")

        
        new_closed_day = ClosedDays(
            branch_id=branch_id,
            part_id = part_id,
            user_id = user_id,
            closed_day_date=closed_day.closed_day_date,
            memo=closed_day.memo,
        )

        db.add(new_closed_day)
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
        raise HTTPException(status_code=500, detail="휴무일 생성에 실패하였습니다.")
    
# 휴무일 다중 휴무 생성
@router.post("/{branch_id}/parts/{part_id}/closed_days/arrays/users/{user_id}")
async def create_part_arrays_closed_day(branch_id : int, part_id : int, user_id : int, token : Annotated[Users, Depends(get_current_user)], array_list : list[ClosedDayCreate] = Body(...)):
    try:

        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id or token.part_id != part_id and token.role.strip() not in ["최고관리자", "관리자", "사원", "통합 관리자"]):
            raise HTTPException(status_code=400, detail="생성 권한이 없습니다.")
        
        
        results = []
        for data in array_list:
            new_closed_day = ClosedDays(
                branch_id=branch_id,
                part_id = part_id,
                user_id = user_id,
                closed_day_date=data.closed_day_date,
                memo=data.memo,
            )
            results.append(new_closed_day)

        db.add_all(results)
        await db.commit()
        await db.refresh(results)

        return {
            "message": "다중 휴무일이 성공적으로 생성되었습니다."
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 생성에 실패하였습니다.")

# 휴일 전체 조회 [어드민만]
@router.get("/closed_days")
async def get_all_closed_days(token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            raise HTTPException(status_code=403, detail="조회 권한이 존재하지 없습니다.")
        
        
        stmt = select(ClosedDays).where(ClosedDays.deleted_yn == "N").offset(0).limit(100)
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
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 전체 조회에 실패하였습니다.")

# 휴일 데이트 전체 입력 조회 [어드민만]
@router.get("/closed_days/{date}")
async def get_all_date_closed_days(date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            raise HTTPException(status_code=403, detail="조회 권한이 존재하지 없습니다.")
        
        if isinstance(date, str):
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        elif isinstance(date, datetime):
            date_obj = date.date()
        
        date_year = date_obj.year
        date_month = date_obj.month
        
        
        stmt = select(ClosedDays).where(extract("year", ClosedDays.closed_day_date) == date_year, extract("month", ClosedDays.closed_day_date) == date_month, ClosedDays.deleted_yn == "N").offset(0).limit(100)
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
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 전체 조회에 실패하였습니다.")

# 휴일 월간 전체 조회 [어드민만]
@router.get("/closed_days/month/{date}")
async def get_month_closed_days(date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            raise HTTPException(status_code=403, detail="조회 권한이 존재하지 없습니다.")
        
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)
        

        stmt = select(ClosedDays).where(ClosedDays.closed_day_date >= date_start_day, ClosedDays.closed_day_date <= date_end_day, ClosedDays.deleted_yn == "N").offset(0).limit(100)
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 월간 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 월간 전체 조회에 실패하였습니다.")
    

# 휴일 주간 전체 조회 [어드민만]
@router.get("/closed_days/week/{date}")
async def get_week_closed_days(date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            raise HTTPException(status_code=403, detail="조회 권한이 존재하지 없습니다.")
        
        kr_tz = ZoneInfo("Asia/Seoul")
        date_obj = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=kr_tz)
        
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        date_start = start_of_week - timedelta(days=3)
        date_end = end_of_week + timedelta(days=2)

        stmt = select(ClosedDays).where(ClosedDays.closed_day_date >= date_start.date(), ClosedDays.closed_day_date <= date_end.date(), ClosedDays.deleted_yn == "N").offset(0).limit(100)
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 주간 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 주간 전체 조회에 실패하였습니다.")
    

# 휴일 지점 월간 전체 조회 [어드민만]
@router.get("/{branch_id}/closed_days/branch_month/{date}")
async def get_branch_month_closed_days(branch_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role.strip() != "최고관리자"):
            raise HTTPException(status_code=403, detail="조회 권한이 존재하지 없습니다.")
        
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.closed_day_date >= date_start_day, ClosedDays.closed_day_date <= date_end_day, ClosedDays.deleted_yn == "N").offset(0).limit(100)
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 월간 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 월간 전체 조회에 실패하였습니다.")


# 휴일 지점 월간 전체 조회 [어드민만]
@router.get("/{branch_id}/closed_days/branch_month/{date}")
async def get_branch_month_closed_days(branch_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role.strip() != "최고관리자"):
            raise HTTPException(status_code=403, detail="조회 권한이 존재하지 없습니다.")
        
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)
        

        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.closed_day_date >= date_start_day, ClosedDays.closed_day_date <= date_end_day, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 월간 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 월간 전체 조회에 실패하였습니다.")  
    
# 휴일 파트 월간 전체 조회 [어드민만]
@router.get("/{branch_id}/parts/{part_id}/closed_days/part_month/{date}")
async def get_month_closed_days(branch_id : int, part_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            if token.branch_id != branch_id and token.role != "최고관리자":
                if token.role != "통합 관리자" or token.part_id != part_id:
                    raise HTTPException(status_code=403, detail="조회 권한이 없습니다.")
        
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)
        

        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.part_id == part_id, ClosedDays.closed_day_date >= date_start_day, ClosedDays.closed_day_date <= date_end_day, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 월간 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 월간 전체 조회에 실패하였습니다.")

# 휴일 지점 일요일만 월간 전체 조회 [어드민만]
@router.get("/{branch_id}/closed_days/branch_sunday/{date}")
async def get_branch_month_sunday_closed_days(branch_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role.strip() != "최고관리자"):
            raise HTTPException(status_code=403, detail="조회 권한이 존재하지 없습니다.")
        
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        date_start_day = date_obj.replace(day=1)
        
        _, last_day = monthrange(date_obj.year, date_obj.month)
        date_end_day = date_obj.replace(day=last_day)

        stmt = select(ClosedDays).join(WorkPolicies, WorkPolicies.branch_id == branch_id).where(ClosedDays.branch_id == branch_id, ClosedDays.closed_day_date >= date_start_day, WorkPolicies.sunday_is_holiday == True, ClosedDays.closed_day_date <= date_end_day, ClosedDays.deleted_yn == "N").offset(0).limit(100)
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 월간 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 월간 전체 조회에 실패하였습니다.")
    

# 휴일 지점 일요일 휴무 지정 [어드민만]
@router.patch("/{branch_id}/closed_days/sunday_result")
async def branch_sunday_result_closed_days(branch_id : int, id : int, token : Annotated[Users, Depends(get_current_user)], sundayOff: bool):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role.strip() != "최고관리자"):
            raise HTTPException(status_code=403, detail="조회 권한이 존재하지 않습니다.")

        stmt = select(ClosedDays).join(WorkPolicies, WorkPolicies.branch_id == id).where(ClosedDays.branch_id == branch_id, WorkPolicies.branch_id == id, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalar_one_or_none()

        if closed_days == None:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )
        
        stmt2 = select(WorkPolicies).where(WorkPolicies.branch_id == branch_id)
        result2 = await db.execute(stmt2)
        work_policy2 = result2.scalar_one_or_none()

        if work_policy2 is None:
            raise HTTPException(
                status_code=404, detail="해당 지점의 근무 정책을 찾을 수 없습니다."
            )
        
        work_policy2.sunday_is_holiday = sundayOff
        await db.commit()

        return {
            "message": "성공적으로 지점 휴무일로 지정 하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 월간 전체 조회에 실패하였습니다.")

    
# 휴일 지점 주간 조회 [어드민만]
@router.get("/{branch_id}/closed_days/branch_week/{date}")
async def get_week_closed_days(branch_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role.strip() != "최고관리자"):
            raise HTTPException(status_code=403, detail="조회 권한이 존재하지 않습니다.")

        
        kr_tz = ZoneInfo("Asia/Seoul")
        date_obj = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=kr_tz)
        
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        date_start = start_of_week - timedelta(days=3)
        date_end = end_of_week + timedelta(days=2)

        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.closed_day_date >= date_start, ClosedDays.closed_day_date <= date_end, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 주간 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 주간 전체 조회에 실패하였습니다.")
    

# 휴일 파트 주간 조회 [어드민만]
@router.get("/{branch_id}/parts/{part_id}/closed_days/part_week/{date}")
async def get_week_closed_days(branch_id : int, part_id : int, date : str, token : Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            if token.branch_id != branch_id and token.role != "최고관리자":
                if token.role != "통합 관리자" or token.part_id != part_id:
                    raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")
        
        kr_tz = ZoneInfo("Asia/Seoul")
        date_obj = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=kr_tz)
        
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        date_start = start_of_week - timedelta(days=3)
        date_end = end_of_week + timedelta(days=2)

        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.part_id == part_id, ClosedDays.closed_day_date >= date_start.date(), ClosedDays.closed_day_date <= date_end.date(), ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalars().all()

        if len(closed_days) == 0:
            raise HTTPException(
                status_code=404, detail="휴일 정책들의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 주간 목록을 성공적으로 전체 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 주간 전체 조회에 실패하였습니다.")
    

# 휴일 지점별 전체 조회 
@router.get("/{branch_id}/closed_days/get_date/{date}")
async def get_branch_closed_days(branch_id : int, date : str):
    try:
        date_start_day = datetime.strptime(date, "%Y-%m-%d").date()
        now_date_year = date_start_day.year
        now_date_month = date_start_day.month

        stmt = select(ClosedDays).where(extract("year", ClosedDays.closed_day_date) == now_date_year,
                                        extract("month", ClosedDays.closed_day_date) == now_date_month,
        ClosedDays.branch_id == branch_id, ClosedDays.deleted_yn == "N")
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
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 지점별 조회에 실패하였습니다.")
    

# 휴일 파트별 전체 조회
@router.get("/{branch_id}/parts/{part_id}/closed_days/{date}")
async def get_part_closed_days(branch_id : int, part_id : int, date : str):
    try:
        date_start_day = datetime.strptime(date, "%Y-%m-%d").date()
        now_date_year = date_start_day.year
        now_date_month = date_start_day.month

        stmt = select(ClosedDays).where(extract("year", ClosedDays.closed_day_date) == now_date_year,
                                        extract("month", ClosedDays.closed_day_date) == now_date_month,
        ClosedDays.branch_id == branch_id, ClosedDays.part_id == part_id, ClosedDays.deleted_yn == "N")
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
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 파트별 조회에 실패하였습니다.")
    

    
# 휴일 지점 상세 조회
@router.get("/{branch_id}/closed_days/get_id/{id}")
async def get_one_closed_days(branch_id : int, id : int):
    try:
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalar_one_or_none()

        if not closed_days:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 지점 목록을 성공적으로 상세 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 상세 조회에 실패하였습니다.")
    

# 휴일 파트 상세 조회
@router.get("/{branch_id}/parts/{part_id}/closed_days/{id}")
async def get_one_closed_days(branch_id : int, part_id : int, id : int):                                               
    try:
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.part_id == part_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_days = result.scalar_one_or_none()

        if not closed_days:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )

        return {
            "message": "휴무일 파트 목록을 성공적으로 상세 조회하였습니다.",
            "data": closed_days,
        }
    except Exception as err:
        await db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="휴무일 상세 조회에 실패하였습니다.")
    

# 휴무일 지점 수정 [어드민만]
@router.patch("/{branch_id}/closed_days/{id}")
async def update_closed_day(branch_id: int, id : int, closed_day_update: ClosedDayUpdate, token:Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role != "최고관리자") :
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
    

# 휴무일 파트 수정 [어드민만]
@router.patch("/{branch_id}/parts/{part_id}/closed_days/{id}")
async def update_part_closed_day(branch_id: int, part_id : int, id : int, closed_day_update: ClosedDayUpdate, token:Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            if token.branch_id != branch_id and token.role != "최고관리자":
                if token.role != "통합 관리자" or token.part_id != part_id:
                    raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")
        
        find_one_closed_day = await db.execute(select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.part_id == part_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N"))
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
    
# 휴무일 지점 삭제 [어드민만]
@router.delete("/{branch_id}/closed_days/{id}")
async def delete_branch_closed_day(branch_id: int, id : int, token:Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role.strip() != "최고관리자"):
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
    
# 휴무일 파트 삭제 [어드민만]
@router.delete("/{branch_id}/parts/{part_id}/closed_days/{id}")
async def delete_part_closed_day(branch_id: int, part_id : int, id : int, token:Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            if token.branch_id != branch_id and token.role.strip() != "최고관리자":
                if token.role.strip() != "통합 관리자" or token.part_id != part_id:
                    raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")
        # 휴무일 존재 여부 확인
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.part_id == part_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
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

# 휴무일 지점 소프트 삭제 [어드민만]
@router.patch("/{branch_id}/closed_days/softdelete/{id}")
async def branch_soft_delete_closed_day(branch_id: int, id : int, token:Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role.strip() != "최고관리자") :
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
    
# 휴무일 파트 소프트 삭제 [어드민만]
@router.patch("/{branch_id}/parts/{part_id}/closed_days/softdelete/{id}")
async def part_soft_delete_closed_day(branch_id: int, part_id : int, id : int, token:Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            if token.branch_id != branch_id and token.role != "최고관리자":
                if token.role.strip() != "통합 관리자" or token.part_id != part_id:
                    raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")
        # 휴무일 존재 여부 확인
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.part_id == part_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
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
    

# 휴무일 지점 복구 [어드민만]
@router.patch("/{branch_id}/closed_days/restore/{id}")
async def branch_restore_closed_day(branch_id: int, id : int, token:Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한" or (token.branch_id != branch_id and token.role.strip() != "최고관리자") :
            raise HTTPException(status_code=403, detail="복구 권한이 없습니다.")
        # 휴무일 존재 여부 확인
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_day = result.scalar_one_or_none()

        if not closed_day:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )
        
        closed_day.deleted_yn = "N"

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


# 휴무일 파트 복구 [어드민만]
@router.patch("/{branch_id}/parts/{part_id}/closed_days/restore/{id}")
async def part_resotre_closed_day(branch_id: int, part_id : int, id : int, token:Annotated[Users, Depends(get_current_user)]):
    try:
        if token.role.strip() != "MSO 최고권한":
            if token.branch_id != branch_id and token.role.strip() != "최고관리자":
                if token.role.strip() != "통합 관리자" or token.part_id != part_id:
                    raise HTTPException(status_code=403, detail="복구 권한이 없습니다.")
        # 휴무일 존재 여부 확인
        stmt = select(ClosedDays).where(ClosedDays.branch_id == branch_id, ClosedDays.part_id == part_id, ClosedDays.id == id, ClosedDays.deleted_yn == "N")
        result = await db.execute(stmt)
        closed_day = result.scalar_one_or_none()

        if not closed_day:
            raise HTTPException(
                status_code=404, detail="휴일 정책의 정보가 존재하지 않습니다."
            )
        
        closed_day.deleted_yn = "N"

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
    
