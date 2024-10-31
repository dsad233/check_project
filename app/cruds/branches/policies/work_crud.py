import logging
from datetime import datetime, time
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.branches.work_policies_model import (
    WorkPolicies,
    WorkPoliciesDto,
    WorkPoliciesUpdateDto,
    WorkSchedule,
    WorkScheduleDto,
    BreakTime,
    BreakTimeDto,
)
from app.exceptions.exceptions import BadRequestError, NotFoundError
from app.enums.users import Weekday
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


def generate_break_times(work_policy_id: int) -> list[BreakTime]:
    break_times = []
    for is_doctor in [True, False]:
        for break_type, start, end in [
            ("점심", time(12, 0), time(13, 0)),
            ("저녁", time(18, 0), time(19, 0)),
        ]:
            break_time = BreakTime(
                work_policy_id=work_policy_id,
                is_doctor=is_doctor,
                break_type=break_type,
                start_time=start,
                end_time=end,
            )
            break_times.append(break_time)
    return break_times


async def create(
    *,
    session: AsyncSession,
    branch_id: int,
) -> WorkPolicies:
    # 기존 정책 존재 여부 확인
    if await find_by_branch_id(session=session, branch_id=branch_id) is not None:
        raise BadRequestError(f"{branch_id}번 지점의 근무 정책이 이미 존재합니다.")

    # WorkPolicies 객체 생성
    work_policies = WorkPolicies(
        branch_id=branch_id,
        weekly_work_days=5,  # 기본값
        created_at=datetime.now(),
        updated_at=datetime.now(),
        deleted_yn="N",
    )

    session.add(work_policies)
    await session.commit()
    await session.flush()
    await session.refresh(work_policies)

    # 월요일부터 일요일까지의 WorkSchedule 생성
    for day in Weekday:
        work_schedule = WorkSchedule(
            work_policy_id=work_policies.id,
            day_of_week=day,
            start_time=time(9, 0),
            end_time=time(18, 0),
            is_holiday=(day in [Weekday.SATURDAY, Weekday.SUNDAY]),
        )
        session.add(work_schedule)

    # BreakTime 4개 생성
    break_times = generate_break_times(work_policies.id)
    for break_time in break_times:
        session.add(break_time)

    await session.commit()
    return work_policies


async def update(
    *,
    session: AsyncSession,
    branch_id: int,
    work_policies_update: WorkPoliciesUpdateDto,
) -> None:
    # 기존 정책 조회
    work_policies = await find_by_branch_id(session=session, branch_id=branch_id)
    if work_policies is None:
        raise NotFoundError(f"{branch_id}번 지점의 근무 정책이 존재하지 않습니다.")

    # WorkPolicies 직접 업데이트 - weekly_work_days가 있을 때만 업데이트
    if work_policies_update.weekly_work_days is not None:
        work_policies.weekly_work_days = work_policies_update.weekly_work_days
    work_policies.updated_at = datetime.now()

    # WorkSchedule 업데이트
    if work_policies_update.work_schedules:
        existing_schedules = await session.execute(
            select(WorkSchedule).where(WorkSchedule.work_policy_id == work_policies.id)
        )
        existing_schedules = existing_schedules.scalars().all()

        for i, new_schedule in enumerate(work_policies_update.work_schedules):
            if i < len(existing_schedules):
                schedule = existing_schedules[i]
                # 각 필드가 있을 때만 업데이트
                if new_schedule.day_of_week is not None:
                    schedule.day_of_week = new_schedule.day_of_week
                if new_schedule.start_time is not None:
                    schedule.start_time = new_schedule.start_time
                if new_schedule.end_time is not None:
                    schedule.end_time = new_schedule.end_time
                if new_schedule.is_holiday is not None:
                    schedule.is_holiday = new_schedule.is_holiday
                schedule.updated_at = datetime.now()

    # BreakTime 업데이트
    if work_policies_update.break_times:
        existing_breaks = await session.execute(
            select(BreakTime).where(BreakTime.work_policy_id == work_policies.id)
        )
        existing_breaks = existing_breaks.scalars().all()

        for i, new_break in enumerate(work_policies_update.break_times):
            if i < len(existing_breaks):
                break_time = existing_breaks[i]
                # 각 필드가 있을 때만 업데이트
                if new_break.is_doctor is not None:
                    break_time.is_doctor = new_break.is_doctor
                if new_break.break_type is not None:
                    break_time.break_type = new_break.break_type
                if new_break.start_time is not None:
                    break_time.start_time = new_break.start_time
                if new_break.end_time is not None:
                    break_time.end_time = new_break.end_time
                break_time.updated_at = datetime.now()

    await session.commit()


async def find_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[WorkPolicies]:

    stmt = select(WorkPolicies).where(WorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    return db_obj


async def get_work_policies(*, session: AsyncSession, branch_id: int) -> WorkPolicies:
    stmt = (
        select(WorkPolicies)
        .where(WorkPolicies.branch_id == branch_id, WorkPolicies.deleted_yn == "N")
        .options(
            selectinload(WorkPolicies.work_schedules),
            selectinload(WorkPolicies.break_times),
        )
    )

    result = await session.execute(stmt)
    work_policies = result.scalar_one_or_none()

    if not work_policies:
        raise HTTPException(status_code=404, detail="Work policies not found")

    return work_policies
