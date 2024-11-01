from datetime import date, datetime, time
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.middleware.tokenVerify import get_current_user
from app.models.branches.branches_model import Branches
from app.models.branches.commute_policies_model import CommutePolicies
from app.models.commutes.commutes_model import Commutes
from app.models.users.users_model import Users

router = APIRouter()


@router.post("/clock-in", summary="사원용 - 출근 기록")
async def create_employee_clock_in(
        request: Request,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
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

        # 출퇴근 정책 확인
        stmt = select(CommutePolicies).where(CommutePolicies.branch_id == current_user.branch_id)
        result = await db.execute(stmt)
        commute_policy = result.scalar_one_or_none()

        if not commute_policy:
            return {
                "message": "출퇴근 정책이 존재하지 않습니다.",
            }

        # IP 주소 확인
        allowed_ip = commute_policy.allowed_ip_commute.split(",")
        client_ip = request.headers.get("x-real-ip", request.client.host)
        if client_ip not in allowed_ip:
            return {
                "message": "IP 주소가 허용되지 않습니다.",
            }

        # 새 출근 기록 생성
        new_commute = Commutes(
            user_id=current_user.id,
            clock_in=datetime.now()
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
        print(f"Error in create_employee_clock_in: {str(err)}")
        raise HTTPException(status_code=500, detail="출근 기록 생성 중 오류가 발생했습니다.")


@router.post("/clock-out", summary="사원용 - 퇴근 기록")
async def create_employee_clock_out(
        request: Request,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
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

        # 출퇴근 정책 확인
        stmt = select(CommutePolicies).where(CommutePolicies.branch_id == current_user.branch_id)
        result = await db.execute(stmt)
        commute_policy = result.scalar_one_or_none()

        if not commute_policy:
            return {
                "message": "출퇴근 정책이 존재하지 않습니다.",
            }

        # IP 주소 확인
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
        print(f"Error in create_employee_clock_out: {str(err)}")
        raise HTTPException(status_code=500, detail="퇴근 기록 생성 중 오류가 발생했습니다.")