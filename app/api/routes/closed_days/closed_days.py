from datetime import UTC, datetime, timedelta
from typing import Annotated, List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy import and_, func, select, extract, update

from app.core.database import async_session, get_db
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.middleware.tokenVerify import get_current_user, validate_token
from app.models.closed_days.closed_days_model import ClosedDays, BranchClosedDay
from app.models.branches.work_policies_model import WorkPolicies
from app.models.users.users_model import Users
from calendar import monthrange
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(dependencies=[Depends(validate_token)])


# 지점 휴점일 생성 (관리자)
@router.post("/{branch_id}/closed-days", status_code=201)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def create_branch_closed_day(
    request: Request,
    branch_id: int,
    closed_days: BranchClosedDay,
    db: AsyncSession = Depends(get_db),
):
    try:
        for day_item in closed_days.hospital_closed_days:
            # 기존 삭제된 데이터가 있는지 확인
            stmt = select(ClosedDays).where(
                and_(
                    ClosedDays.branch_id == branch_id,
                    ClosedDays.closed_day_date == day_item,
                    ClosedDays.user_id.is_(None),
                    ClosedDays.deleted_yn == 'Y'
                )
            )
            result = await db.execute(stmt)
            existing_closed_day = result.scalar_one_or_none()

            if existing_closed_day:
                # 기존 데이터가 있다면 복구
                existing_closed_day.deleted_yn = 'N'
                existing_closed_day.memo = "임시 휴점"
            else:
                # 새로운 데이터 생성
                new_closed_day = ClosedDays(
                    branch_id=branch_id,
                    closed_day_date=day_item,
                    memo = "임시 휴점",
                )
                db.add(new_closed_day)

        await db.commit()
        return {"message": "휴무일이 성공적으로 생성되었습니다."}
    except Exception as err:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(err))


# 지점 휴점일 삭제 (관리자)
@router.delete("/{branch_id}/closed-days")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def delete_branch_closed_days(
    request: Request,
    branch_id: int,
    closed_days: BranchClosedDay,
    db: AsyncSession = Depends(get_db),
):
    try:
        dates_to_delete = closed_days.hospital_closed_days

        # 먼저 해당 레코드들이 존재하는지 확인
        stmt = select(ClosedDays.closed_day_date).where(
            and_(
                ClosedDays.branch_id == branch_id,
                ClosedDays.closed_day_date.in_(dates_to_delete),
                ClosedDays.user_id.is_(None),
                ClosedDays.deleted_yn == "N",
            )
        )
        result = await db.execute(stmt)
        existing_dates = result.scalars().all()

        if not existing_dates:
            raise HTTPException(
                status_code=404, detail="삭제할 휴무일을 찾을 수 없습니다."
            )

        # UPDATE 실행
        update_stmt = (
            update(ClosedDays)
            .where(
                and_(
                    ClosedDays.branch_id == branch_id,
                    ClosedDays.closed_day_date.in_(dates_to_delete),
                    ClosedDays.user_id.is_(None),
                    ClosedDays.deleted_yn == "N",
                )
            )
            .values(deleted_yn="Y")
        )
        await db.execute(update_stmt)
        await db.commit()

        return {"message": "휴무일이 성공적으로 삭제되었습니다."}

    except HTTPException as http_err:
        await db.rollback()
        raise http_err
    except Exception as err:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail="휴무일 삭제 중 오류가 발생했습니다."
        )
