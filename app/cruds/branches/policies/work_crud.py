import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.branches.work_policies_model import WorkPolicies
from app.exceptions.exceptions import BadRequestError, NotFoundError

logger = logging.getLogger(__name__)

async def create(
    *, session: AsyncSession, branch_id: int, work_policies_create: WorkPolicies = WorkPolicies()
) -> WorkPolicies:

    if await find_by_branch_id(session=session, branch_id=branch_id) is not None:
        raise BadRequestError(f"{branch_id}번 지점의 근무 정책이 이미 존재합니다.")
    if work_policies_create.branch_id is None:
        work_policies_create.branch_id = branch_id
    session.add(work_policies_create)
    await session.commit()
    await session.flush()
    await session.refresh(work_policies_create)
    return work_policies_create

async def update(
    *, session: AsyncSession, branch_id: int, work_policies_update: WorkPolicies
) -> None:

    # 기존 정책 조회
    work_policies = await find_by_branch_id(session=session, branch_id=branch_id)

    if work_policies is None:
        raise NotFoundError(f"{branch_id}번 지점의 근무 정책이 존재하지 않습니다.")
    
    # 변경된 필드만 업데이트
    changed_fields = {}
    for column in WorkPolicies.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at', 'deleted_yn']:
            new_value = getattr(work_policies_update, column.name)
            if new_value is not None and getattr(work_policies, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(WorkPolicies).where(WorkPolicies.branch_id == branch_id).values(**changed_fields)
        await session.execute(stmt)
        work_policies.updated_at = datetime.now()
        await session.commit()
        await session.refresh(work_policies)
    else:
        pass



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