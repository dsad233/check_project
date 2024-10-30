from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Annotated, Any, Dict, List, Optional
from datetime import date, datetime, UTC, time
from calendar import calendar, day_name, monthrange
from sqlalchemy import and_, func, or_
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions.auth_utils import available_higher_than
from app.middleware.tokenVerify import validate_token
from app.enums.users import Role, StatusKor
from app.models.branches.work_policies_model import WorkPolicies, WorkSchedule
from app.models.users.users_model import Users
from app.models.commutes.commutes_model import Commutes
from app.models.users.leave_histories_model import LeaveHistories
from app.models.closed_days.closed_days_model import ClosedDays
from app.models.users.users_work_contract_model import WorkContract
from app.models.users.overtimes_model import OverTime_History, Overtimes

router = APIRouter(dependencies=[Depends(validate_token)])


async def get_user_query(session, branch_id, part_id, user_name, phone_number):
    # part_id가 있는데 branch_id가 없으면 에러
    if part_id and not branch_id:
        raise HTTPException(
            status_code=400,
            detail="지점을 선택하지 않고 파트를 선택할 수 없습니다."
        )
        
    query = (
        select(Users)
        .options(
            selectinload(Users.branch),
            selectinload(Users.part),
        )
        .where(Users.deleted_yn == "N")
    )

    if branch_id:
        query = query.where(Users.branch_id == branch_id)
    if part_id:
        query = query.where(Users.part_id == part_id)
    if user_name:
        query = query.where(Users.name == user_name)
    if phone_number:
        query = query.where(Users.phone_number == phone_number)

    return query


async def get_date_range(year: Optional[int], month: Optional[int]):
    today = datetime.now(UTC)

    # year나 month가 None이면 현재 년월 사용
    if year is None or month is None:
        year, month = today.year, today.month

    # month가 1-12 범위인지 확인
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="올바른 월이 아닙니다. (1-12)")

    _, last_day = monthrange(year, month)

    return (
        datetime(year, month, 1, tzinfo=UTC),
        datetime(year, month, last_day, 23, 59, 59, tzinfo=UTC),
        last_day,
    )


async def get_user_data(session, user_id, branch_id, start_date, end_date):
    # 근로계약 정보 조회 및 즉시 가져오기
    contract_result = await session.execute(
        select(WorkContract)
        .where(
            and_(
                WorkContract.user_id == user_id,
                WorkContract.contract_start_date <= end_date.date(),
                or_(
                    WorkContract.contract_end_date.is_(None),
                    WorkContract.contract_end_date >= start_date.date(),
                )
            )
        )
        .order_by(WorkContract.contract_start_date.desc())
        .limit(1)
    )
    contract = contract_result.scalar_one_or_none()

    # 근무 정책 조회
    work_policy_result = await session.execute(
        select(WorkPolicies)
        .options(selectinload(WorkPolicies.work_schedules))
        .where(and_(WorkPolicies.branch_id == branch_id, WorkPolicies.deleted_yn == "N"))
    )
    work_policy = work_policy_result.scalar_one_or_none()

    # 출퇴근 기록 조회
    commutes_result = await session.execute(
        select(Commutes).where(
            and_(
                Commutes.user_id == user_id,
                Commutes.clock_in >= start_date,
                Commutes.clock_in <= end_date,
                Commutes.deleted_yn == "N",
            )
        )
    )
    commutes = commutes_result.scalars().all()

    # 휴가 기록 조회
    leaves_result = await session.execute(
        select(LeaveHistories)
        .options(joinedload(LeaveHistories.leave_category))
        .where(
            and_(
                LeaveHistories.user_id == user_id,
                LeaveHistories.application_date >= start_date.date(),
                LeaveHistories.application_date <= end_date.date(),
                LeaveHistories.status == StatusKor.APPROVED,
                LeaveHistories.deleted_yn == "N",
            )
        )
    )
    leaves = leaves_result.scalars().all()

    # 휴점일 조회
    closed_days_result = await session.execute(
        select(ClosedDays).where(
            and_(
                ClosedDays.branch_id == branch_id,
                ClosedDays.closed_day_date >= start_date.date(),
                ClosedDays.closed_day_date <= end_date.date(),
                ClosedDays.deleted_yn == "N",
            )
        )
    )
    closed_days = closed_days_result.scalars().all()

    # 초과근무 기록 조회
    overtimes_result = await session.execute(
        select(Overtimes).where(
            and_(
                Overtimes.applicant_id == user_id,
                Overtimes.application_date >= start_date.date(),
                Overtimes.application_date <= end_date.date(),
                Overtimes.deleted_yn == "N",
            )
        )
    )
    overtimes = overtimes_result.scalars().all()

    return {
        "contract": contract,
        "work_policy": work_policy,
        "commutes": commutes,
        "leaves": leaves,
        "closed_days": closed_days,
        "overtimes": overtimes,
    }


async def process_daily_record(
    current_date,
    user_id,
    work_policy,
    contract,
    commutes,
    leaves,
    closed_days,
    overtimes,
):
    record_data = {"date": current_date.strftime("%Y-%m-%d")}

    # 정기휴무 체크 수정
    if work_policy and work_policy.work_schedules:
        holiday_schedule = next(
            (
                schedule
                for schedule in work_policy.work_schedules
                if schedule.day_of_week == day_name[current_date.weekday()].lower()
                and schedule.is_holiday
            ),
            None,
        )
        if holiday_schedule:
            record_data["status"] = "병원 정기휴무"
            return record_data

    # 휴점일 체크
    closed_day = next(
        (cd for cd in closed_days if cd.closed_day_date == current_date), None
    )
    if closed_day:
        record_data.update({"status": "휴점"})
        return record_data

    # 계약상 정기휴무 체크
    if contract:
        if current_date > contract.contract_end_date:
            record_data["status"] = "퇴사자"
            return record_data

        weekday = current_date.weekday()
        if (
            (weekday == 6 and contract.sunday_is_rest)
            or (weekday == 5 and contract.saturday_is_rest)
            or (weekday < 5 and contract.weekly_is_rest)
        ):
            record_data["status"] = "직원 정기휴무"
            return record_data
        
    # 출근 기록 체크
    commute = next((c for c in commutes if c.clock_in.date() == current_date), None)
    if commute:
        record_data.update(
            {
                "status": "출근",
                "clock_in": commute.clock_in.strftime("%H:%M:%S"),
                "clock_out": (
                    commute.clock_out.strftime("%H:%M:%S")
                    if commute.clock_out
                    else None
                ),
                "work_hours": (
                    round(commute.work_hours, 2) if commute.work_hours else None
                ),
                "late": False,
                "overtime": False,
            }
        )

        # 지각 체크
        if contract and contract.weekly_work_start_time:
            weekday = current_date.weekday()
            
            # 근무일인지 체크 (휴무일이 아닌 날)
            should_check_attendance = False  # 기본값을 False로
            if (weekday < 5 and not contract.weekly_is_rest) or \
               (weekday == 5 and not contract.saturday_is_rest) or \
               (weekday == 6 and not contract.sunday_is_rest):
                should_check_attendance = True  # 근무일인 경우에만 True

            if should_check_attendance:
                clock_in_time = commute.clock_in.replace(tzinfo=None).time()
                is_late = clock_in_time > contract.weekly_work_start_time
                record_data["late"] = is_late

        # 초과근무 체크
        if commute.clock_out and contract and contract.weekly_work_end_time:
            weekday = current_date.weekday()
            
            # 근무일인지 체크 (휴무일이 아닌 날)
            should_check_overtime = False  # 기본값을 False로
            if (weekday < 5 and not contract.weekly_is_rest) or \
               (weekday == 5 and not contract.saturday_is_rest) or \
               (weekday == 6 and not contract.sunday_is_rest):
                should_check_overtime = True  # 근무일인 경우에만 True

            if should_check_overtime:
                clock_out_time = commute.clock_out.replace(tzinfo=None).time()
                
                # 해당 날짜의 승인된 초과근무가 있는지 확인
                approved_overtime = next(
                    (ot for ot in overtimes 
                     if ot.application_date == current_date 
                     and ot.is_approved == "Y"), 
                    None
                )
                
                # 초과근무가 승인되었고, 퇴근 시간이 정규 근무 종료 시간을 초과한 경우
                is_overtime = True if approved_overtime and clock_out_time > contract.weekly_work_end_time else False
                
                record_data["overtime"] = is_overtime

        return record_data

    # 휴가 체크
    leave = next((l for l in leaves if l.application_date == current_date), None)
    if leave:
        record_data.update({"status": f"{leave.leave_category.name}"})
        return record_data

    return record_data


@router.get("/commutes-manager", response_model=Dict[str, Any])
async def get_commutes_manager(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    branch_id: Optional[int] = Query(None, description="지점 ID"),
    part_id: Optional[int] = Query(None, description="파트 ID"),
    user_name: Optional[str] = Query(None, description="사용자 이름"),
    phone_number: Optional[str] = Query(None, description="사용자 전화번호"),
    year: Optional[int] = Query(None, description="조회 년도"),
    month: Optional[int] = Query(None, description="조회 월"),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
):
    try:
        async with db as session:
            # 날짜 범위 설정
            start_date, end_date, last_day = await get_date_range(year, month)
            today = datetime.now(UTC).date()

            if end_date.date() > today:
                end_date = datetime.combine(today, time(23, 59, 59, tzinfo=UTC))

            # 사용자 쿼리 생성 및 실행
            query = await get_user_query(
                session=session,
                branch_id=branch_id,
                part_id=part_id,
                user_name=user_name,
                phone_number=phone_number,
            )
            total_count = await session.scalar(
                select(func.count()).select_from(query.subquery())
            )
            users = await session.execute(query.offset((page - 1) * size).limit(size))
            users = users.scalars().unique().all()

            result = []
            for user in users:
                # 사용자 관련 데이터 조회
                user_data = await get_user_data(
                    session, user.id, user.branch_id, start_date, end_date
                )

                daily_records = []
                current_date = start_date.date()
                while current_date <= end_date.date():
                    if current_date <= today:
                        record = await process_daily_record(
                            current_date,
                            user,
                            user_data["work_policy"],
                            user_data["contract"],
                            user_data["commutes"],
                            user_data["leaves"],
                            user_data["closed_days"],
                            user_data["overtimes"],
                        )
                        if record and "status" in record:
                            daily_records.append(record)
                    current_date = date.fromordinal(current_date.toordinal() + 1)

                if daily_records:
                    result.append(
                        {
                            "user_id": user.id,
                            "user_name": user.name,
                            "gender": user.gender,
                            "branch_id": user.branch_id,
                            "branch_name": user.branch.name,
                            "weekly_work_days": user_data[
                                "work_policy"
                            ].weekly_work_days,
                            "part_id": user.part_id,
                            "part_name": user.part.name,
                            "commute_records": daily_records,
                        }
                    )

            return {
                "message": "출퇴근 기록 조회 성공",
                "data": result,
                "pagination": {"total": total_count, "page": page, "size": size},
                "last_day": last_day,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"출퇴근 기록 조회 실패: {str(e)}")
