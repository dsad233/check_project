from datetime import UTC, date, datetime, time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update

from app.core.database import async_session
from app.middleware.tokenVerify import get_current_user, get_current_user_id, validate_token
from app.models.users.overtimes_model import OvertimeSelect, OvertimeCreate, OvertimeUpdate, Overtimes
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



# 초과 근무 승인
@router.patch("/approve/{overtime_id}")
async def approve_overtime(overtime_id: int, overtime_select: OvertimeSelect, current_user: Users = Depends(get_current_user)):
    try:
        stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N") & (Overtimes.status == "pending"))
        result = await db.execute(stmt)
        overtime = result.scalar_one_or_none()
        
        if overtime is None:
            raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")

        if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자"]:
            raise HTTPException(status_code=403, detail="관리자만 승인할 수 있습니다.")
        
        overtime.status = "approved"
        overtime.manager_id = current_user.id
        overtime.processed_date = datetime.now(UTC).date()
        overtime.is_approved = "Y"
        overtime.manager_memo = overtime_select.manager_memo
        await db.commit()
        
        return {
            "message": "초과 근무 기록이 승인되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 초과 근무 거절
@router.patch("/reject/{overtime_id}")
async def reject_overtime(overtime_id: int, overtime_select: OvertimeSelect, current_user: Users = Depends(get_current_user)):
    try:
        stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N") & (Overtimes.status == "pending"))
        result = await db.execute(stmt)
        overtime = result.scalar_one_or_none()
        
        if overtime is None:
            raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")

        if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자"]:
            raise HTTPException(status_code=403, detail="관리자만 승인할 수 있습니다.")
        
        overtime.status = "rejected"
        overtime.manager_id = current_user.id
        overtime.processed_date = datetime.now(UTC).date()
        overtime.is_approved = "N"
        overtime.manager_memo = overtime_select.manager_memo
        await db.commit()
        
        return {
            "message": "초과 근무 기록이 거절되었습니다.",
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
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 초과 근무 수정
@router.patch("/{overtime_id}")
async def update_overtime(overtime_id: int, overtime_update: OvertimeUpdate, current_user: Users = Depends(get_current_user)):
    try:
        stmt = select(Overtimes).where((Overtimes.id == overtime_id) & (Overtimes.deleted_yn == "N"))
        result = await db.execute(stmt)
        overtime = result.scalar_one_or_none()

        if overtime is None:
            raise HTTPException(status_code=404, detail="초과 근무 기록을 찾을 수 없습니다.")

        if current_user.role not in ["MSO 최고권한", "최고관리자", "관리자"] or current_user.id != overtime.applicant_id:
            raise HTTPException(status_code=403, detail="관리자 또는 초과 근무 신청자만 수정할 수 있습니다.")

        if overtime.status != "pending":
            raise HTTPException(status_code=400, detail="승인 또는 거절된 초과 근무는 수정할 수 없습니다.")

        update_data = {}

        # 관리자인 경우
        if current_user.role in ["MSO 최고권한", "최고관리자", "관리자"]:
            if overtime_update.overtime_hours is not None:
                update_data["overtime_hours"] = overtime_update.overtime_hours
            if overtime_update.application_memo is not None:
                update_data["application_memo"] = overtime_update.application_memo
            if overtime_update.manager_memo is not None:
                update_data["manager_memo"] = overtime_update.manager_memo

        # 신청자인 경우
        elif current_user.id == overtime.applicant_id:
            if overtime_update.application_memo is not None:
                update_data["application_memo"] = overtime_update.application_memo
        
        else:
            raise HTTPException(status_code=403, detail="초과 근무 기록을 수정할 권한이 없습니다.")

        if not update_data:
            raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")

        update_stmt = update(Overtimes).where(Overtimes.id == overtime_id).values(**update_data)
        await db.execute(update_stmt)
        await db.commit()
        
        return {
            "message": "초과 근무 기록이 수정되었습니다.",
        }
    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
