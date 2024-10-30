import logging
from datetime import datetime, time
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.models.branches.work_policies_model import WorkPolicies
from app.exceptions.exceptions import BadRequestError, NotFoundError
from app.models.branches.work_policies_model import WorkSchedule
from app.enums.users import Weekday
from app.models.branches.work_policies_model import BreakTime
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

def generate_break_times(work_policy_id: int) -> list[BreakTime]:
    break_times = []
    for is_doctor in [True, False]:
        for break_type, start, end in [("점심", time(12, 0), time(13, 0)), ("저녁", time(18, 0), time(19, 0))]:
            break_time = BreakTime(
                work_policy_id=work_policy_id,
                is_doctor=is_doctor,
                break_type=break_type,
                start_time=start,
                end_time=end
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
        deleted_yn="N"
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
            is_holiday=(day in [Weekday.SATURDAY, Weekday.SUNDAY])
        )
        session.add(work_schedule)

    # BreakTime 4개 생성
    break_times = generate_break_times(work_policies.id)
    for break_time in break_times:
        session.add(break_time)

    await session.commit()
    return work_policies


async def update(*, session: AsyncSession, branch_id: int, work_policies_update: WorkPolicies) -> None:
    # 기존 정책 조회
    work_policies = await find_by_branch_id(session=session, branch_id=branch_id)
    if work_policies is None:
        raise NotFoundError(f"{branch_id}번 지점의 근무 정책이 존재하지 않습니다.")
    
    # WorkPolicies 업데이트
    changed_fields = {}
    for column in WorkPolicies.__table__.columns:
        if column.name not in ['id', 'branch_id', 'created_at', 'updated_at']:
            new_value = getattr(work_policies_update, column.name)
            if new_value is not None and getattr(work_policies, column.name) != new_value:
                changed_fields[column.name] = new_value

    if changed_fields:
        # 변경된 필드가 있을 경우에만 업데이트 수행
        stmt = sa_update(WorkPolicies).where(
            WorkPolicies.branch_id == branch_id,
            WorkPolicies.deleted_yn == 'N'  # deleted_yn 조건 추가
        ).values(**changed_fields)
        await session.execute(stmt)
        work_policies.updated_at = datetime.now()
        await session.commit()
        await session.refresh(work_policies)
    else:
        pass
    
    # WorkSchedule 업데이트
    if work_policies_update.work_schedules:
        # 기존 스케줄 삭제
        await session.execute(
            sa_update(WorkSchedule)
            .where(WorkSchedule.work_policy_id == work_policies.id)
            .values(deleted_yn='Y')
        )
        
        # 새로운 스케줄 추가
        for schedule in work_policies_update.work_schedules:
            new_schedule = WorkSchedule(
                work_policy_id=work_policies.id,
                day_of_week=schedule.day_of_week,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                is_holiday=schedule.is_holiday
            )
            session.add(new_schedule)
    
    # BreakTime 업데이트
    if work_policies_update.break_times:
        # 기존 휴게시간 삭제
        await session.execute(
            sa_update(BreakTime)
            .where(BreakTime.work_policy_id == work_policies.id)
            .values(deleted_yn='Y')
        )
        
        # 새로운 휴게시간 추가
        for break_time in work_policies_update.break_times:
            new_break = BreakTime(
                work_policy_id=work_policies.id,
                is_doctor=break_time.is_doctor,
                break_type=break_time.break_type,
                start_time=break_time.start_time,
                end_time=break_time.end_time
            )
            session.add(new_break)
    
    work_policies.updated_at = datetime.now()
    await session.commit()
    await session.refresh(work_policies)



async def find_by_branch_id(
    *, session: AsyncSession, branch_id: int
) -> Optional[WorkPolicies]:

    stmt = select(WorkPolicies).where(WorkPolicies.branch_id == branch_id)
    result = await session.execute(stmt)
    db_obj = result.scalar_one_or_none()
    return db_obj

async def get_work_policies(*, session: AsyncSession, branch_id: int) -> WorkPolicies:
    stmt = select(WorkPolicies).where(
        WorkPolicies.branch_id == branch_id,
        WorkPolicies.deleted_yn == 'N'
    ).options(
        selectinload(WorkPolicies.work_schedules),
        selectinload(WorkPolicies.break_times)
    )
    
    result = await session.execute(stmt)
    work_policies = result.scalar_one_or_none()
    
    if not work_policies:
        raise HTTPException(status_code=404, detail="Work policies not found")
        
    return work_policies

