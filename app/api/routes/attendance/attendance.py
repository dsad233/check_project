from calendar import monthrange
from datetime import date, datetime, timedelta
import re
from typing import Annotated, Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import Date, Row, and_, case, cast, distinct, func, text
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dto.pagination_dto import PaginationDto
from app.core.database import async_session, get_db
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.models.branches.allowance_policies_model import AllowancePolicies
from app.models.branches.branches_model import Branches
from app.models.branches.leave_categories_model import LeaveCategory
from app.models.branches.rest_days_model import RestDays
from app.models.closed_days.closed_days_model import ClosedDays
from app.models.parts.parts_model import Parts
from app.models.users.users_model import Users
from app.models.branches.work_policies_model import WorkPolicies
from app.models.users.overtimes_model import Overtimes
from app.models.commutes.commutes_model import Commutes
from app.models.users.leave_histories_model import LeaveHistories
from app.models.branches.overtime_policies_model import OverTimePolicies
from app.middleware.tokenVerify import validate_token, get_current_user
from sqlalchemy.orm import joinedload

router = APIRouter()

def calculate_total_ot(is_doctor: bool, record: Row) -> int:
    """
    OT 총액을 계산하는 함수
    """
    if is_doctor:
        total = (
            ((record.ot_30_count or 0) * (record.doctor_ot_30 or 0)) +
            ((record.ot_60_count or 0) * (record.doctor_ot_60 or 0)) +
            ((record.ot_90_count or 0) * (record.doctor_ot_90 or 0)) +
            ((record.ot_120_count or 0) * (record.doctor_ot_120 or 0))
        )
    else:
        total = (
            ((record.ot_30_count or 0) * (record.common_ot_30 or 0)) +
            ((record.ot_60_count or 0) * (record.common_ot_60 or 0)) +
            ((record.ot_90_count or 0) * (record.common_ot_90 or 0)) +
            ((record.ot_120_count or 0) * (record.common_ot_120 or 0))
        )
    
    return int(total)

def count_sundays(start_date: date, end_date: date) -> int:
    current_date = start_date
    sunday_count = 0
    
    while current_date <= end_date:
        if current_date.weekday() == 6:  # 0=월요일, 6=일요일
            sunday_count += 1
        current_date += timedelta(days=1)
    
    return sunday_count



@router.get("/attendance", response_model=Dict[str, Any])
@available_higher_than(Role.ADMIN)
async def find_attendance(
    request: Request,
    db: Annotated[AsyncSession,Depends(get_db)],
    branch: Optional[int] = Query(None, description="지점 ID"),
    part: Optional[int] = Query(None, description="파트 ID"),
    name: Optional[str] = Query(None, description="사용자 이름"),
    phone_number: Optional[str] = Query(None, description="전화번호"),
    year_month: Optional[str] = Query(None, description="조회 년월 (YYYY-MM 형식)"),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
):
    
    if part and not branch:
        raise HTTPException(status_code=400, detail="지점 정보가 필요합니다.")
    
    try:
        async with db as session:
            if year_month:
                if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", year_month):
                    raise HTTPException(
                        status_code=400, detail="올바른 년월 형식이 아닙니다. (YYYY-MM)"
                    )
                date_obj = datetime.strptime(year_month, "%Y-%m")
            else:
                date_obj = datetime.now()

            start_date = date(date_obj.year, date_obj.month, 1)
            _, last_day = monthrange(date_obj.year, date_obj.month)
            end_date = date(date_obj.year, date_obj.month, last_day)

            # 기본 사용자 정보 쿼리
            base_query = (
                select(
                    Users.id,
                    Users.name.label("user_name"),
                    Users.gender.label("user_gender"),
                    Users.phone_number.label("user_phone_number"),
                    Branches.id.label("branch_id"),
                    Branches.name.label("branch_name"),
                    Parts.id.label("part_id"),
                    Parts.name.label("part_name"),
                )
                .select_from(Users)
                .join(Branches, Users.branch_id == Branches.id)
                .join(Parts, Users.part_id == Parts.id)
                .where(Users.deleted_yn == "N")
            )

            # 필터 조건 추가
            if branch:
                base_query = base_query.where(Users.branch_id == branch)
            if part:
                base_query = base_query.where(Users.part_id == part)
            if name:
                base_query = base_query.where(Users.name.like(f"%{name}%"))
            if phone_number:
                base_query = base_query.where(Users.phone_number.like(f"{phone_number}"))

            base_query = base_query.subquery()
            

            # 근무일수 서브쿼리
            work_days_subq = (
                select(
                    Commutes.user_id,
                    func.count(distinct(Commutes.clock_in)).label("work_days"),
                )
                .where(
                    Commutes.clock_in.between(start_date, end_date),
                    Commutes.deleted_yn == "N",
                )
                .group_by(Commutes.user_id)
            ).subquery()

            # 정규 휴무일수 계산 (closed_days + 일요일)
            regular_leave_days = (
                select(
                    Users.id.label("user_id"),
                    (
                        # 해당 월의 일요일 수를 계산
                        func.coalesce(count_sundays(start_date, end_date), 0) +
                        # closed_days 수 계산
                        func.count(distinct(
                            case(
                                (ClosedDays.closed_day_date.isnot(None), ClosedDays.closed_day_date),
                                else_=None
                            )
                        ))
                    ).label("regular_leave_days")
                )
                .select_from(Users)
                .outerjoin(ClosedDays, and_(
                    Users.branch_id == ClosedDays.branch_id,
                    ClosedDays.closed_day_date.between(start_date, end_date),
                    ClosedDays.deleted_yn == "N"
                ))
                .group_by(Users.id)
            ).subquery()

            # 연차 사용일수
            annual_leave_days = (
                select(
                    LeaveHistories.user_id,
                    func.count(distinct(LeaveHistories.application_date)).label("annual_leave_days")
                )
                .join(LeaveCategory)
                .where(
                    LeaveHistories.application_date.between(start_date, end_date),
                    LeaveHistories.status == "승인",
                    LeaveCategory.is_paid == True
                )
                .group_by(LeaveHistories.user_id)
            ).subquery()

            # 무급 휴가 사용일수
            unpaid_leave_days = (
                select(
                    LeaveHistories.user_id,
                    func.count(distinct(LeaveHistories.application_date)).label("unpaid_leave_days")
                )
                .join(LeaveCategory)
                .where(
                    LeaveHistories.application_date.between(start_date, end_date),
                    LeaveHistories.status == "승인",
                    LeaveCategory.is_paid == False
                )
                .group_by(LeaveHistories.user_id)
            ).subquery()

            # 휴일 근무일수
            holiday_work_days = (
                select(
                    Commutes.user_id,
                    func.count(distinct(Commutes.clock_in)).label("holiday_work_days")
                )
                .select_from(Commutes)
                .join(Users, Users.id == Commutes.user_id)
                .join(
                    RestDays,
                    and_(
                        cast(Commutes.clock_in, Date) == RestDays.date,
                        Users.branch_id == RestDays.branch_id
                    )
                )
                .where(
                    and_(
                        Commutes.clock_in.between(start_date, end_date),
                        RestDays.rest_type == "공휴일",
                        Commutes.deleted_yn == "N",
                        RestDays.deleted_yn == "N"
                    )
                )
                .group_by(Commutes.user_id)
            ).subquery()

            # 주말 근무 시간
            weekend_work_hours = (
                select(
                    Commutes.user_id,
                    func.sum(Commutes.work_hours).label("weekend_work_hours")
                )
                .select_from(Commutes)
                .join(Users, Users.id == Commutes.user_id)
                .join(
                    RestDays,
                    and_(
                        cast(Commutes.clock_in, Date) == RestDays.date,
                        Users.branch_id == RestDays.branch_id
                    )
                )
                .where(
                    and_(
                        Commutes.clock_in.between(start_date, end_date),
                        RestDays.rest_type == "주말",
                        Commutes.deleted_yn == "N",
                        RestDays.deleted_yn == "N"
                    )
                )
                .group_by(Commutes.user_id)
            ).subquery()

            # overtime_counts 서브쿼리
            overtime_counts = (
                select(
                    Overtimes.applicant_id.label('user_id'),
                    func.count(case((Overtimes.overtime_hours == '30', 1), else_=0)).label("ot_30_count"),
                    func.count(case((Overtimes.overtime_hours == '60', 1), else_=0)).label("ot_60_count"),
                    func.count(case((Overtimes.overtime_hours == '90', 1), else_=0)).label("ot_90_count"),
                    func.count(case((Overtimes.overtime_hours == '120', 1), else_=0)).label("ot_120_count")
                )
                .where(
                    and_(
                        Overtimes.application_date.between(start_date, end_date),
                        Overtimes.is_approved == "Y",
                        Overtimes.deleted_yn == "N"
                    )
                )
                .group_by(Overtimes.applicant_id)
            ).subquery()
            
            overtime_policy = (
                select(
                    OverTimePolicies.branch_id,
                    # 의사 OT 금액들
                    OverTimePolicies.doctor_ot_30,
                    OverTimePolicies.doctor_ot_60,
                    OverTimePolicies.doctor_ot_90,
                    OverTimePolicies.doctor_ot_120,
                    # 일반 직원 OT 금액들
                    OverTimePolicies.common_ot_30,
                    OverTimePolicies.common_ot_60,
                    OverTimePolicies.common_ot_90,
                    OverTimePolicies.common_ot_120
                )
                .where(OverTimePolicies.deleted_yn == "N")
            ).subquery()

            # 최종 쿼리 (기존 + 새로운 필드들)
            final_query = (
                select(
                    base_query,
                    work_days_subq.c.work_days,
                    regular_leave_days.c.regular_leave_days,
                    annual_leave_days.c.annual_leave_days,
                    unpaid_leave_days.c.unpaid_leave_days,
                    holiday_work_days.c.holiday_work_days,
                    weekend_work_hours.c.weekend_work_hours,
                    overtime_counts.c.ot_30_count,
                    overtime_counts.c.ot_60_count,
                    overtime_counts.c.ot_90_count,
                    overtime_counts.c.ot_120_count,
                    overtime_policy.c.doctor_ot_30,
                    overtime_policy.c.doctor_ot_60,
                    overtime_policy.c.doctor_ot_90,
                    overtime_policy.c.doctor_ot_120,
                    overtime_policy.c.common_ot_30,
                    overtime_policy.c.common_ot_60,
                    overtime_policy.c.common_ot_90,
                    overtime_policy.c.common_ot_120,
                    Parts.is_doctor
                )
                .outerjoin(work_days_subq, base_query.c.id == work_days_subq.c.user_id)
                .outerjoin(regular_leave_days, base_query.c.id == regular_leave_days.c.user_id)
                .outerjoin(annual_leave_days, base_query.c.id == annual_leave_days.c.user_id)
                .outerjoin(unpaid_leave_days, base_query.c.id == unpaid_leave_days.c.user_id)
                .outerjoin(holiday_work_days, base_query.c.id == holiday_work_days.c.user_id)
                .outerjoin(weekend_work_hours, base_query.c.id == weekend_work_hours.c.user_id)
                .outerjoin(overtime_counts, base_query.c.id == overtime_counts.c.user_id)
                .outerjoin(overtime_policy, base_query.c.branch_id == overtime_policy.c.branch_id)
                .join(Parts, base_query.c.part_id == Parts.id)
            )

            total_count = await session.scalar(
                select(func.count()).select_from(final_query.subquery())
            )

            # 페이지네이션 처리
            pagination = PaginationDto(
                total_record=total_count,
                record_size=size
            )

            # offset, limit 계산에도 pagination 값 사용
            final_query = final_query.offset((page - 1) * pagination.record_size).limit(pagination.record_size)

            result = await session.execute(final_query)
            records = result.fetchall()

            # 응답 데이터 포맷팅 (기존 + 새로운 필드들)
            formatted_data = [
                {
                    "id": record.id,
                    "branch_id": record.branch_id,
                    "branch_name": record.branch_name,
                    "user_name": record.user_name,
                    "user_gender": record.user_gender,
                    "user_phone_number": record.user_phone_number,
                    "part_id": record.part_id,
                    "part_name": record.part_name,
                    "work_days": record.work_days or 0, # 근무 일자
                    "regular_leave_days": record.regular_leave_days or 0, # 정규 휴무일수   
                    "annual_leave_days": record.annual_leave_days or 0, # 연차 사용일수
                    "unpaid_leave_days": record.unpaid_leave_days or 0, # 무급 휴가 사용일수
                    "holiday_work_days": record.holiday_work_days or 0, # 휴일 근무일수
                    "weekend_work_hours": float(record.weekend_work_hours or 0), # 주말 근무 시간
                    "ot_30_count": record.ot_30_count or 0, # 30분 근무 횟수
                    "ot_60_count": record.ot_60_count or 0, # 60분 근무 횟수    
                    "ot_90_count": record.ot_90_count or 0, # 90분 근무 횟수
                    "ot_120_count": record.ot_120_count or 0, # 120분 근무 횟수
                    "total_OT": calculate_total_ot(
                        record.is_doctor,
                        record
                    )
                }
                for record in records
            ]

            return {
                "message": "근태 기록 조회 성공",
                "data": formatted_data,
                "pagination": {
                    "total": pagination.total_record,
                    "page": page,
                    "size": pagination.record_size,
                },
            }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"근태 기록 조회 실패: {str(e)}")

