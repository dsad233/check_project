from calendar import monthcalendar
from datetime import datetime, timedelta
from datetime import date as dt
from typing import Dict, List, Optional, Tuple
from fastapi import Depends
from sqlalchemy import and_, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.routes.commutes_manager.dto.commutes_manager_response_dto import AttendanceStatus, CommuteRecord, Weekday
from app.core.database import get_db
from app.models.branches.branches_model import Branches
from app.models.branches.leave_categories_model import LeaveCategory
from app.models.parts.parts_model import Parts
from app.models.users.leave_histories_model import LeaveHistories
from app.models.users.time_off_model import TimeOff
from app.models.users.users_model import Users
from app.models.commutes.commutes_model import Commutes
from app.models.closed_days.closed_days_model import ClosedDays
from app.models.branches.work_policies_model import WorkPolicies
from app.models.users.users_work_contract_model import FixedRestDay


class CommutesManagerService:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session
    
    # 휴직 기간 조회
    async def get_time_off_periods(self, user_id: int, year: int, month: int) -> Dict[str, CommuteRecord]:
        query = select(TimeOff).where(
            and_(
                TimeOff.user_id == user_id,
                TimeOff.deleted_yn == "N",
                extract('year', TimeOff.start_date) == year,
                extract('month', TimeOff.start_date) == month
            )
        )
        
        result = await self.session.execute(query)
        time_off_records = {}
        
        for time_off in result.scalars():
            if time_off.start_date.year == year and time_off.start_date.month == month:
                time_off_records[time_off.start_date.strftime("%Y-%m-%d")] = CommuteRecord(
                    clock_in=None,
                    clock_out=None,
                    status=AttendanceStatus.TIME_OFF_START
                )
            
            if time_off.end_date.year == year and time_off.end_date.month == month:
                time_off_records[time_off.end_date.strftime("%Y-%m-%d")] = CommuteRecord(
                    clock_in=None,
                    clock_out=None,
                    status=AttendanceStatus.TIME_OFF_END
                )
                
        return time_off_records
    
    # 지점의 고정 휴점일 조회
    async def get_fixed_closed_days(self, branch_id: int, year: int, month: int) -> List[dt]:
        work_policy = await self.get_work_policy(branch_id)
        if not work_policy:
            return []
            
        fixed_closed_days = []
        for schedule in work_policy.work_schedules:
            if schedule.is_holiday:  # 휴점일로 설정된 요일
                weekday_value = Weekday[schedule.day_of_week.name]
                # 해당 월의 모든 날짜를 순회하며 같은 요일인 날짜 추가
                current = dt(year, month, 1)
                while current.month == month:
                    if current.weekday() == weekday_value:
                        fixed_closed_days.append(current)
                    current += timedelta(days=1)
                
        return fixed_closed_days


    # 지점 휴무일 조회 (branch_id가 일치하고 user_id가 None인 데이터)
    async def get_branch_closed_days(self, branch_id: int, year: int, month: int) -> List[dt]:
        closed_days_query = select(ClosedDays).where(
            and_(
                ClosedDays.branch_id == branch_id,
                ClosedDays.user_id.is_(None),
                extract('year', ClosedDays.closed_day_date) == year,
                extract('month', ClosedDays.closed_day_date) == month,
                ClosedDays.deleted_yn == "N"
            )
        ).order_by(ClosedDays.closed_day_date)  # 날짜순 정렬 추가
        
        result = await self.session.execute(closed_days_query)
        return [day.closed_day_date for day in result.scalars().all()]

    # 사용자별 휴무일 조회
    async def get_user_closed_days(self, user_id: int, branch_id: int, year: int, month: int) -> List[dt]:
        closed_days_query = select(ClosedDays).where(
            and_(
                ClosedDays.branch_id == branch_id,
                ClosedDays.user_id == user_id,
                extract('year', ClosedDays.closed_day_date) == year,
                extract('month', ClosedDays.closed_day_date) == month,
                ClosedDays.deleted_yn == "N"
            )
        ).order_by(ClosedDays.closed_day_date)  # 날짜순 정렬 추가
        
        result = await self.session.execute(closed_days_query)
        return [day.closed_day_date for day in result.scalars().all()]

    # 지점 근무 정책 조회
    async def get_work_policy(self, branch_id: int) -> Optional[WorkPolicies]:
        query = select(WorkPolicies).where(WorkPolicies.branch_id == branch_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    # 승인된 휴가 기록 조회
    async def get_approved_leaves(self, user_id: int, year: int, month: int) -> Dict[str, str]:
        query = (
            select(LeaveHistories, LeaveCategory)
            .join(LeaveCategory, LeaveHistories.leave_category_id == LeaveCategory.id)
            .where(
                and_(
                    LeaveHistories.user_id == user_id,
                    LeaveHistories.status == "approved",
                    extract('year', LeaveHistories.application_date) == year,
                    extract('month', LeaveHistories.application_date) == month,
                    LeaveHistories.deleted_yn == "N"
                )
            )
        )
        
        result = await self.session.execute(query)
        leave_records = {}
        
        for leave, category in result:
            leave_records[leave.application_date.strftime("%Y-%m-%d")] = category.name
            
        return leave_records
    
    # 사용자의 고정 휴무일 조회
    # async def get_user_fixed_rest_days(self, user_id: int, year: int, month: int) -> List[date]:
    #     query = select(FixedRestDay).where(FixedRestDay.work_contract_id == user_id)
    #     result = await self.session.execute(query)
    #     fixed_rest_days = result.scalars().all()
        
    #     user_fixed_rest_days = []
    #     for fixed_rest in fixed_rest_days:
    #         current = date(year, month, 1)
    #         while current.month == month:
    #             if current.weekday() == WeekDay[fixed_rest.rest_day.name].value:
    #                 user_fixed_rest_days.append(current)
    #             current += timedelta(days=1)
                    
    #     return user_fixed_rest_days
    
    
    async def get_commute_records(self, user_id: int, branch_id: int, year: int, month: int) -> Dict[str, CommuteRecord]:
        # # 직원 고정 휴무일 조회
        # user_fixed_rest_days = await self.get_user_fixed_rest_days(user_id, year, month)
        # user_fixed_rest_records = {
        #     d.strftime("%Y-%m-%d"): CommuteRecord(status=AttendanceStatus.FIXED_OFF)
        #     for d in user_fixed_rest_days
        # }
        
        # 사용자 정보 조회
        user = await self.session.execute(
            select(Users).where(Users.id == user_id)
        )
        user = user.scalar_one()
        
        not_hire_records = {}
        
        # 미입사 상태 처리
        if user.hire_date:
            current_month_start = dt(year, month, 1)
            current_date = current_month_start
            
            while current_date < user.hire_date and current_date.month == month:
                date_str = current_date.strftime("%Y-%m-%d")
                not_hire_records[date_str] = CommuteRecord(
                    clock_in=None,
                    clock_out=None,
                    status=AttendanceStatus.NOT_HIRE
                )
                current_date += timedelta(days=1)
        
        
        resignation_records = {}  # 퇴사 상태를 저장할 딕셔너리 초기화
        
        # 퇴사일 처리
        if user.resignation_date:
            current_month_start = dt(year, month, 1)
            next_month_start = dt(year, month + 1, 1) if month < 12 else dt(year + 1, 1, 1)
            
            # 퇴사일이 현재 조회 월과 관련있는 경우
            if current_month_start <= user.resignation_date < next_month_start:
                resignation_next_day = user.resignation_date + timedelta(days=1)
                current_date = resignation_next_day
                
                # 퇴사 다음날부터 월말까지 퇴사 상태로 설정
                while current_date < next_month_start:
                    date_str = current_date.strftime("%Y-%m-%d")
                    resignation_records[date_str] = CommuteRecord(
                        clock_in=None,
                        clock_out=None,
                        status=AttendanceStatus.RESIGNATION
                    )
                    current_date += timedelta(days=1)
        
        # 휴직 기간 처리
        time_off_records = await self.get_time_off_periods(user_id, year, month)
        for record_date, status in time_off_records.items():
            resignation_records[record_date] = CommuteRecord(
                clock_in=None,
                clock_out=None,
                status=AttendanceStatus.TIME_OFF_START if status == "휴직 시작" else AttendanceStatus.TIME_OFF_END
        )
        
        
        # 고정 휴점일 조회
        fixed_closed_days = await self.get_fixed_closed_days(branch_id, year, month)
        fixed_closed_records = {
            d.strftime("%Y-%m-%d"): CommuteRecord(status=AttendanceStatus.FIXED_CLOSED)
            for d in fixed_closed_days
        }
        
        # 지점 휴점일 조회
        branch_closed_days = await self.get_branch_closed_days(branch_id, year, month)
        branch_closed_records = {
            d.strftime("%Y-%m-%d"): CommuteRecord(status=AttendanceStatus.CLOSED)
            for d in branch_closed_days
        }
        
        # 개인 휴무일 조회
        user_closed_days = await self.get_user_closed_days(user_id, branch_id, year, month)
        user_closed_records = {
            d.strftime("%Y-%m-%d"): CommuteRecord(status=AttendanceStatus.OFF)
            for d in user_closed_days
            if d.strftime("%Y-%m-%d") not in fixed_closed_records  # 고정 휴점일과 겹치지 않는 경우
            and d.strftime("%Y-%m-%d") not in branch_closed_records  # 지점 휴점일과 겹치지 않는 경우
        }
        
        # 승인된 휴가 기록 조회
        leave_records = await self.get_approved_leaves(user_id, year, month)
        leave_records_formatted = {
            record_date: CommuteRecord(status=status)
            for record_date, status in leave_records.items()
        }
        
        # 출퇴근 기록 조회 (기존 코드와 동일)
        commutes_query = select(Commutes).where(
            and_(
                Commutes.user_id == user_id,
                Commutes.clock_in >= datetime(year, month, 1),
                Commutes.clock_in < datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1),
                Commutes.deleted_yn == "N"
            )
        )
        commutes_result = await self.session.execute(commutes_query)
        commute_records = {
            commute.clock_in.strftime("%Y-%m-%d"): CommuteRecord(
                clock_in=commute.clock_in.time(),
                clock_out=commute.clock_out.time() if commute.clock_out else None,
                status=AttendanceStatus.WORK
            )
            for commute in commutes_result.scalars().all()
            if commute.clock_in.strftime("%Y-%m-%d") not in fixed_closed_records  # 고정 휴점일과 겹치지 않는 경우
            and commute.clock_in.strftime("%Y-%m-%d") not in branch_closed_records  # 지점 휴점일과 겹치지 않는 경우
            and commute.clock_in.strftime("%Y-%m-%d") not in user_closed_records  # 개인 휴무일과 겹치지 않는 경우
        }
        
        
        # 모든 기록 병합 (우선순위: 고정 휴점일 > 지점 휴점일 > 직원 고정 휴무일 > 개인 휴무일 > 출퇴근 기록)
        records = {
            **commute_records, # 최하위 우선순위
            **leave_records_formatted,
            **user_closed_records,
            **branch_closed_records,
            **fixed_closed_records,
            **time_off_records, 
            **not_hire_records,
            **resignation_records, # 최우선 순위
            # **user_fixed_rest_records,
        }
        sorted_records = dict(sorted(records.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")))
        return sorted_records

    async def get_user_commutes(
        self,
        branch_id: Optional[int],
        part_id: Optional[int],
        user_name: Optional[str],
        phone_number: Optional[str],
        year: int,
        month: int,
        page: int,
        size: int,
    ) -> Tuple[List[dict], dict]:
        
        target_date = dt(year, month, 1)
        last_date = dt(year, month + 1, 1) if month < 12 else dt(year + 1, 1, 1)
        
        query = (
            select(Users, Branches, Parts)
            .join(Branches, Users.branch_id == Branches.id)
            .join(Parts, Users.part_id == Parts.id)
            .where(
                and_(
                    Users.deleted_yn == "N",
                    Users.hire_date < last_date,  # 해당 월 이전에 입사한 사람
                    or_(
                        Users.resignation_date == None,  # 퇴사일이 없거나
                        Users.resignation_date >= target_date  # 해당 월에 퇴사한 사람도 포함
                    )
                )
            )
        )

        if branch_id:
            query = query.where(Users.branch_id == branch_id)
        if part_id:
            query = query.where(Users.part_id == part_id)
        if user_name:
            query = query.where(Users.name.like(f"%{user_name}%"))
        if phone_number:
            query = query.where(Users.phone_number.like(f"%{phone_number}%"))

        total = await self.session.scalar(select(func.count()).select_from(query.subquery()))
        result = await self.session.execute(query.offset((page - 1) * size).limit(size))
        
        users_data = []
        for user, branch, part in result:
            work_policy = await self.get_work_policy(branch.id)
            weekly_work_days = work_policy.weekly_work_days if work_policy else 5
            
            commute_records = await self.get_commute_records(
                user_id=user.id,
                branch_id=branch.id,
                year=year,
                month=month
            )
            
            users_data.append({
                "user_id": user.id,
                "user_name": user.name,
                "gender": user.gender,
                "branch_id": branch.id,
                "branch_name": branch.name,
                "part_id": part.id,
                "part_name": part.name,
                "weekly_work_days": weekly_work_days,
                "commute_records": commute_records
            })

        return users_data, {"total": total, "page": page, "size": size}