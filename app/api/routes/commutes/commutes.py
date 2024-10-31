from datetime import date, datetime, time
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy import func, select, update

from app.core.database import async_session, get_db
from app.middleware.tokenVerify import get_current_user, get_current_user_id, validate_token
from app.models.branches.branches_model import Branches
from app.models.branches.commute_policies_model import CommutePolicies
from app.models.commutes.commutes_model import Commutes, CommuteUpdate, Commutes_clock_in, Commutes_clock_out
from app.models.users.users_model import Users
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
# db = async_session()


# 출근 기록 생성
@router.post("/clock-in")
async def create_clock_in(request: Request, current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        # 현재 날짜의 시작과 끝 시간 계산
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        # 같은 날짜에 이미 출근 기록이 있는지 확인
        existing_commute = await db.execute(
            select(Commutes)
            .join(Branches, current_user.branch_id == Branches.id)
            .where(
                Commutes.user_id == current_user.id,
                Commutes.clock_in >= today_start,
                Commutes.clock_in <= today_end,
            )
        )
        existing_commute = existing_commute.scalar_one_or_none()

        if existing_commute:
            return {
                "message": "이미 오늘의 출근 기록이 존재합니다.",
                "data": existing_commute,
            }
        
        stmt = select(CommutePolicies).where(CommutePolicies.branch_id == current_user.branch_id)
        result = await db.execute(stmt)
        commute_policy = result.scalar_one_or_none()

        if not commute_policy:
            return {
                "message": "출퇴근 정책이 존재하지 않습니다.",
            }

        allowed_ip = commute_policy.allowed_ip_commute.split(",")
        client_ip = request.headers.get("x-real-ip", request.client.host)
        if client_ip not in allowed_ip:
            return {
                "message": "IP 주소가 허용되지 않습니다.",
            }

        # 새 출근 기록 생성
        new_commute = Commutes(
            user_id=current_user.id, clock_in=datetime.now()  # 현재 시간으로 설정
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

# 퇴근 기록 생성 (기존의 출근 기록 수정)
@router.post("/clock-out")
async def create_clock_out(request: Request, current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        # 현재 날짜의 시작과 끝 시간 계산
        today = date.today()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)

        # 오늘의 출근 기록 조회
        stmt = select(Commutes).where(
            (Commutes.user_id == current_user.id)
            & (Commutes.clock_in >= today_start)
            & (Commutes.clock_in <= today_end)
            & (Commutes.deleted_yn == "N")
        ).order_by(Commutes.clock_in.desc())
        result = await db.execute(stmt)
        commute = result.scalar_one_or_none()

        if not commute:
            return {
                "message": "오늘의 출근 기록을 찾을 수 없습니다.",
            }
        
        stmt = select(CommutePolicies).where(CommutePolicies.branch_id == current_user.branch_id)
        result = await db.execute(stmt)
        commute_policy = result.scalar_one_or_none()

        if not commute_policy:
            return {    
                "message": "출퇴근 정책이 존재하지 않습니다.",
            }
        
        allowed_ip = commute_policy.allowed_ip_commute.split(",")
        client_ip = request.headers.get("x-real-ip", request.client.host)
        if client_ip not in allowed_ip:
            return {
                "message": "IP 주소가 허용되지 않습니다.",
            }

        # 현재 시간을 퇴근 시간으로 설정
        clock_out = datetime.now()
        work_hours = (clock_out - commute.clock_in).total_seconds() / 3600

        # 출퇴근 기록 업데이트
        update_data = {
            "clock_out": clock_out,
            "work_hours": int(work_hours),
            "updated_at": clock_out,
        }
        update_stmt = (
            update(Commutes).where(Commutes.id == commute.id).values(**update_data)
        )
        await db.execute(update_stmt)
        await db.commit()

        return {
            "message": "퇴근 기록이 성공적으로 생성되었습니다.",
            "data": update_data,
        }

    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 출퇴근 기록 목록 조회
@router.get("")
async def get_commute_records(
    current_user_id: int = Depends(get_current_user_id), skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    try:
        # 전체 출퇴근 기록 수 조회
        count_query = (
            select(func.count()).select_from(Commutes).where(Commutes.deleted_yn == "N")
        )
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
            "limit": limit,
        }

    except Exception as err:
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 출퇴근 기록 수정
@router.patch("/{commute_id}")
async def update_commute_record(
    commute_id: int,
    commute_update: CommuteUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        # 업데이트할 필드만 선택
        update_data = commute_update.model_dump(exclude_unset=True)

        print(update_data)
        print(commute_id)
        print(current_user_id)

        if not update_data:
            raise HTTPException(
                status_code=400, detail="업데이트할 정보가 제공되지 않았습니다."
            )

        # 출퇴근 기록 존재 여부 확인
        stmt = select(Commutes).where(
            (Commutes.id == commute_id)
            & (Commutes.user_id == current_user_id)
            & (Commutes.deleted_yn == "N")
        )
        result = await db.execute(stmt)
        commute = result.scalar_one_or_none()

        if not commute:
            raise HTTPException(
                status_code=404, detail="해당 출퇴근 기록을 찾을 수 없습니다."
            )

        # 퇴근 시간 유효성 검사
        if "clock_out" in update_data:
            if update_data["clock_out"] <= commute.clock_in:
                raise HTTPException(
                    status_code=400, detail="퇴근 시간은 출근 시간보다 늦어야 합니다."
                )
            # 근무 시간 자동 계산
            work_hours = (
                update_data["clock_out"] - commute.clock_in
            ).total_seconds() / 3600
            update_data["work_hours"] = round(work_hours, 2)

        # 업데이트 데이터에 수정 시간 추가
        update_data["updated_at"] = datetime.now()

        # 출퇴근 기록 업데이트
        update_stmt = (
            update(Commutes).where(Commutes.id == commute_id).values(**update_data)
        )
        await db.execute(update_stmt)
        await db.commit()

        return {
            "message": "출퇴근 기록이 성공적으로 수정되었습니다.",
        }

    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


# 출퇴근 기록 삭제
@router.delete("/{commute_id}")
async def delete_commute_record(
    commute_id: int, current_user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)
):
    try:
        # 출퇴근 기록 존재 여부 확인
        stmt = select(Commutes).where(
            (Commutes.id == commute_id)
            & (Commutes.user_id == current_user_id)
            & (Commutes.deleted_yn == "N")
        )
        result = await db.execute(stmt)
        commute = result.scalar_one_or_none()

        if not commute:
            raise HTTPException(
                status_code=404, detail="해당 출퇴근 기록을 찾을 수 없습니다."
            )

        # 출퇴근 기록 소프트 삭제
        update_data = {"deleted_yn": "Y", "updated_at": datetime.now()}
        update_stmt = (
            update(Commutes).where(Commutes.id == commute_id).values(**update_data)
        )
        await db.execute(update_stmt)
        await db.commit()

        return {
            "message": "출퇴근 기록이 성공적으로 삭제되었습니다.",
        }

    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        print("에러가 발생하였습니다.")
        print(err)
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
