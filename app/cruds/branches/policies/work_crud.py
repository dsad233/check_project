import logging
from datetime import datetime, time
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.branches.work_policies_model import (
    WorkPolicies,
    BranchWorkSchedule,
    BranchBreakTime,
)
from app.schemas.branches_schemas import WorkPoliciesUpdateDto, WorkPoliciesUpdateDto, WorkPoliciesDto
from app.exceptions.exceptions import BadRequestError, NotFoundError
from app.enums.users import Weekday
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


def generate_break_times() -> list[BranchBreakTime]:
    break_times = []
    for is_doctor in [True, False]:
        for break_type, start, end in [
            ("점심", time(12, 0), time(13, 0)),
            ("저녁", time(18, 0), time(19, 0)),
        ]:
            break_time = BranchBreakTime(
                is_doctor=is_doctor,
                break_type=break_type,
                start_time=start,
                end_time=end,
            )
            break_times.append(break_time)
    return break_times


def generate_work_schedules() -> list[BranchWorkSchedule]:
    work_schedules = []
    for day in Weekday:
        work_schedule = BranchWorkSchedule(
            day_of_week=day,
            start_time=time(9, 0),
            end_time=time(18, 0),
            is_holiday=(day in [Weekday.SATURDAY, Weekday.SUNDAY]),
        )
        work_schedules.append(work_schedule)
    return work_schedules


async def create(
    *,
    session: AsyncSession,
    branch_id: int,
    request: WorkPoliciesDto = WorkPoliciesDto(),
) -> WorkPolicies:
    
    work_policies = WorkPolicies(branch_id=branch_id, weekly_work_days=request.weekly_work_days)
    session.add(work_policies)
    await session.flush()
    await session.refresh(work_policies)
    work_policies_id = work_policies.id

    # 월요일부터 일요일까지의 WorkSchedule 생성
    work_schedules = generate_work_schedules() if not request.work_schedules else [BranchWorkSchedule(**work_schedule.model_dump()) for work_schedule in request.work_schedules]
    for work_schedule in work_schedules:
        work_schedule.work_policy_id = work_policies_id
        session.add(work_schedule)

    # BreakTime 4개 생성
    break_times = generate_break_times() if not request.break_times else [BranchBreakTime(**break_time.model_dump()) for break_time in request.break_times]
    for break_time in break_times:
        break_time.work_policy_id = work_policies_id
        session.add(break_time)

    await session.flush()
    return request


async def update(
    *,
    session: AsyncSession,
    branch_id: int,
    request: WorkPoliciesDto,
    old: WorkPolicies,
) -> bool:

    # WorkPolicies 직접 업데이트 - weekly_work_days가 있을 때만 업데이트
    if old.weekly_work_days != request.weekly_work_days:
        old.weekly_work_days = request.weekly_work_days
        old.updated_at = datetime.now()

    # WorkSchedule 업데이트
    old_schedules_dict = {
        schedule.day_of_week: schedule 
        for schedule in old.work_schedules
    }
    
    updated_schedules = []
    for new_schedule in request.work_schedules:
        old_schedule = old_schedules_dict.get(new_schedule.day_of_week)
        if old_schedule:
            # 실제 변경사항이 있는 경우만 업데이트
            if (old_schedule.start_time != new_schedule.start_time or
                old_schedule.end_time != new_schedule.end_time or
                old_schedule.is_holiday != new_schedule.is_holiday):
                
                old_schedule.start_time = new_schedule.start_time
                old_schedule.end_time = new_schedule.end_time
                old_schedule.is_holiday = new_schedule.is_holiday
                old_schedule.updated_at = datetime.now()
                updated_schedules.append(old_schedule)
        else:
            new_schedule_obj = BranchWorkSchedule(
                work_policy_id=old.id,
                **new_schedule.model_dump()
            )
            updated_schedules.append(new_schedule_obj)

    # BreakTime 업데이트
    old_break_times_dict = {
        (break_time.is_doctor, break_time.break_type): break_time 
        for break_time in old.break_times
    }
    
    updated_break_times = []
    for new_break_time in request.break_times:
        key = (new_break_time.is_doctor, new_break_time.break_type)
        old_break_time = old_break_times_dict.get(key)
        if old_break_time:
            # 실제 변경사항이 있는 경우만 업데이트
            if (old_break_time.start_time != new_break_time.start_time or
                old_break_time.end_time != new_break_time.end_time):
                
                old_break_time.start_time = new_break_time.start_time
                old_break_time.end_time = new_break_time.end_time
                old_break_time.updated_at = datetime.now()
                updated_break_times.append(old_break_time)
        else:
            new_break_time_obj = BranchBreakTime(
                work_policy_id=old.id,
                **new_break_time.model_dump()
            )
            updated_break_times.append(new_break_time_obj)

    if updated_schedules:
        session.add_all(updated_schedules)
    if updated_break_times:
        session.add_all(updated_break_times)

    await session.flush()


async def find_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[WorkPolicies]:

    stmt = select(WorkPolicies).where(WorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    return db_obj


async def get_work_policies_with_break_times_and_schedules(*, session: AsyncSession, branch_id: int) -> WorkPolicies:
    stmt = (
        select(WorkPolicies)
        .where(WorkPolicies.branch_id == branch_id)
        .options(selectinload(WorkPolicies.break_times), selectinload(WorkPolicies.work_schedules))
    )

    result = await session.execute(stmt)
    work_policies = result.scalar_one_or_none()

    return work_policies


# 근무 캘린더에서 고정 휴점일을 변경할 때 사용
async def update_schedule_holiday(
    *,
    session: AsyncSession,
    branch_id: int,
    work_policies_update: WorkPoliciesUpdateDto,
) -> None:
    work_policies = await find_by_branch_id(session=session, branch_id=branch_id)
    if work_policies is None:
        raise NotFoundError(f"{branch_id}번 지점의 근무 정책이 존재하지 않습니다.")

    if work_policies_update.weekly_work_days is not None:
        work_policies.weekly_work_days = work_policies_update.weekly_work_days
    work_policies.updated_at = datetime.now()

    if work_policies_update.work_schedules:
        existing_schedules = await session.execute(
            select(BranchWorkSchedule)
            .where(BranchWorkSchedule.work_policy_id == work_policies.id)
        )
        existing_schedules = existing_schedules.scalars().all()
        
        # 기존 스케줄을 day_of_week를 키로 하는 딕셔너리로 변환
        schedule_dict = {schedule.day_of_week: schedule for schedule in existing_schedules}
        
        for new_schedule in work_policies_update.work_schedules:
            if new_schedule.day_of_week in schedule_dict:
                # 기존 요일이 있으면 업데이트
                schedule = schedule_dict[new_schedule.day_of_week]
                if new_schedule.start_time is not None:
                    schedule.start_time = new_schedule.start_time
                if new_schedule.end_time is not None:
                    schedule.end_time = new_schedule.end_time
                if new_schedule.is_holiday is not None:
                    schedule.is_holiday = new_schedule.is_holiday
                schedule.updated_at = datetime.now()
            else:
                # 새로운 요일이면 생성
                new_schedule_obj = BranchWorkSchedule(
                    work_policy_id=work_policies.id,
                    day_of_week=new_schedule.day_of_week,
                    start_time=new_schedule.start_time or time(9, 0),  # 기본값 설정
                    end_time=new_schedule.end_time or time(18, 0),     # 기본값 설정
                    is_holiday=new_schedule.is_holiday
                )
                session.add(new_schedule_obj)