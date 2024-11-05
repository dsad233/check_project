from typing import List
from fastapi import Depends, HTTPException
from sqlalchemy import and_, func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.routes.closed_days.dto.closed_days_response_dto import EarlyClockInResponseDTO, UserClosedDayDetail, UserClosedDayDetailDTO, UserClosedDaySummaryDTO
from app.core.database import get_db
from app.enums.user_management import ContractStatus, ContractType
from app.enums.users import EmploymentStatus, Status
from app.exceptions.exceptions import ForbiddenError, NotFoundError
from app.models.branches.branches_model import Branches
from app.models.branches.leave_categories_model import LeaveCategory
from app.models.branches.work_policies_model import BranchWorkSchedule, WorkPolicies
from app.models.closed_days.closed_days_model import ClosedDays, EarlyClockIn, UserEarlyClockIn
from app.models.parts.parts_model import Parts
from app.models.users.leave_histories_model import LeaveHistories
from app.models.users.users_contract_info_model import ContractInfo
from app.models.users.users_contract_model import Contract
from app.models.users.users_model import Users
from calendar import monthrange
from datetime import date, datetime, timedelta

from app.models.users.users_work_contract_model import FixedRestDay, WorkContract

class ClosedDayService:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_all_user_closed_days_group_by_user_id(self, branch_id: int, year: int, month: int) -> List[UserClosedDayDetail]:
        '''
        특정 지점에서 모든 직원의 월간 휴무일 조회를 user_id별로 조회
        '''
        # 직원의 특정 휴무일 조회
        query = (
            select(ClosedDays.closed_day_date, Users.id, Users.name, Parts.name)
            .join(Users, ClosedDays.user_id == Users.id)
                .filter(
                    and_(
                        ClosedDays.branch_id == branch_id,
                        ClosedDays.user_id != None,
                        func.extract('year', ClosedDays.closed_day_date) == year,
                        func.extract('month', ClosedDays.closed_day_date) == month,
                        ClosedDays.deleted_yn == "N"
                    )
                )
            .join(Parts, Users.part_id == Parts.id)
        )
        result = await self.session.execute(query)
        closed_days = result.fetchall()

        user_id_to_detail = {}
        for closed_day_date, user_id, user_name, part_name in closed_days:
            if user_id not in user_id_to_detail:
                user_id_to_detail[user_id] = {
                    "user_name": user_name,
                    "part_name": part_name,
                    "user_closed_days": []
                }
            user_id_to_detail[user_id]["user_closed_days"].append(UserClosedDaySummaryDTO.to_DTO(closed_day_date.strftime("%Y-%m-%d"), "휴무"))

        # 연차 조회
        user_ids = list(user_id_to_detail.keys())
        query = (
            select(LeaveHistories.user_id, LeaveHistories.start_date, LeaveHistories.end_date, LeaveCategory.name)
            .join(LeaveCategory, LeaveHistories.leave_category_id == LeaveCategory.id)
                .filter(LeaveHistories.status == Status.APPROVED)
                .filter(func.extract('year', LeaveHistories.start_date) == year)
                .filter(func.extract('month', LeaveHistories.start_date) == month)
                .filter(LeaveHistories.user_id.in_(user_ids))
        )
        result = await self.session.execute(query)
        leave_histories = result.fetchall()

        for leave_history in leave_histories:
            user_id, start_date, end_date, leave_category_name = leave_history
            current_date = start_date
            while current_date <= end_date:
                user_id_to_detail[user_id]["user_closed_days"].append(UserClosedDaySummaryDTO.to_DTO(current_date.strftime("%Y-%m-%d"), leave_category_name))
                current_date += timedelta(days=1)
        
        # 정기 휴무 -> fixed_closed_days 조회
        # 날짜만 구하기
        ## 유저별 최신 WORK 타입 계약 테이블에서 정기 휴무일 조회
        latest_contracts = (
            select(
                ContractInfo.user_id,
                func.max(Contract.created_at).label('max_date')
            )
            .select_from(Contract)
            .join(ContractInfo, Contract.contract_info_id == ContractInfo.id)
                .filter(ContractInfo.user_id.in_(user_ids))
            .where(Contract.contract_type == ContractType.WORK)
            .group_by(ContractInfo.user_id)
            .subquery()
        )
    
        ## 유저별 최신 WORK 타입 계약 테이블
        current_contract_table = (
            select(
                ContractInfo.user_id,
                Contract.contract_type,
                Contract.created_at,
                Contract.contract_id,
                ContractInfo.hire_date
            )
            .select_from(Contract)
            .join(ContractInfo, Contract.contract_info_id == ContractInfo.id)
                .filter(ContractInfo.employ_status == EmploymentStatus.PERMANENT)
            .where(
                and_(
                    Contract.contract_type == ContractType.WORK,
                    Contract.contract_status == ContractStatus.APPROVE,
                    tuple_(ContractInfo.user_id, Contract.created_at).in_(
                        select(
                            latest_contracts.c.user_id,
                            latest_contracts.c.max_date
                        ).select_from(latest_contracts)
                    ),
                )
            )
            .subquery()
        )

        query = (
            select(current_contract_table.c.user_id, current_contract_table.c.hire_date, FixedRestDay.rest_day, FixedRestDay.every_over_week)
            .select_from(current_contract_table)
            .join(WorkContract, current_contract_table.c.contract_id == WorkContract.id)
                .filter(
                    WorkContract.is_fixed_rest_day == True,
                    WorkContract.deleted_yn == "n"
                )
            .join(FixedRestDay, WorkContract.id == FixedRestDay.work_contract_id)
        )

        result = await self.session.execute(query)
        fixed_rest_days = result.fetchall()

        for user_id, contract_start_date, rest_day, every_over_week in fixed_rest_days:
            first_day_of_month = date(year, month, 1)
            days_in_month = monthrange(year, month)[1]

            for day in range(days_in_month):
                current_day = first_day_of_month + timedelta(days=day)
                if current_day.strftime('%A').upper() == rest_day.name and current_day >= contract_start_date:
                    # 격주 휴무인 경우, 짝수 주차에만 휴무 추가 
                    if every_over_week:
                        # 계약 시작일로부터 몇 주차인지 계산
                        weeks_since_start = ((current_day - contract_start_date).days // 7)
                        if weeks_since_start % 2 == 0:
                            user_id_to_detail[user_id]["user_closed_days"].append(UserClosedDaySummaryDTO.to_DTO(current_day.strftime('%Y-%m-%d'), "정규휴무"))
                    else:
                        user_id_to_detail[user_id]["user_closed_days"].append(UserClosedDaySummaryDTO.to_DTO(current_day.strftime('%Y-%m-%d'), "정규휴무"))

        # 날짜별로 정렬
        for user_id in user_id_to_detail:
            user_id_to_detail[user_id]["user_closed_days"] = set(user_id_to_detail[user_id]["user_closed_days"])

        return [
            UserClosedDayDetailDTO.to_DTO(user_id, **detail)
            for user_id, detail in user_id_to_detail.items()
        ]
    
    async def get_all_user_closed_days_group_by_date(self, branch_id: int, year: int, month: int) -> dict[str, List[UserClosedDayDetail]]:
        '''
        특정 지점에서 모든 직원의 월간 휴무일 조회를 날짜별로 조회
        '''
        # 직원의 특정 휴무일 조회
        query = (
            select(ClosedDays.closed_day_date, Users.id, Users.name, Parts.name)
            .join(Users, ClosedDays.user_id == Users.id)
                .filter(
                    and_(
                        ClosedDays.branch_id == branch_id,
                        ClosedDays.user_id != None,
                        func.extract('year', ClosedDays.closed_day_date) == year,
                        func.extract('month', ClosedDays.closed_day_date) == month,
                        ClosedDays.deleted_yn == "N"
                    )
                )
            .join(Parts, Users.part_id == Parts.id)
        )

        result = await self.session.execute(query)
        closed_days = result.fetchall()

        date_to_users = {}
        for closed_day_date, user_id, user_name, part_name in closed_days:
            date_str = closed_day_date.strftime("%Y-%m-%d")
            if date_str not in date_to_users:
                date_to_users[date_str] = set()
            date_to_users[date_str].add(UserClosedDayDetail(
                user_id=user_id,
                user_name=user_name,
                part_name=part_name,
                category="휴무"
            ))

        # 연차 조회
        query = (
            select(LeaveHistories.user_id, LeaveHistories.start_date, LeaveHistories.end_date, LeaveCategory.name, Users.name, Parts.name)
            .join(LeaveCategory, LeaveHistories.leave_category_id == LeaveCategory.id)
            .join(Users, LeaveHistories.user_id == Users.id)
            .join(Parts, Users.part_id == Parts.id)
                .filter(
                    and_(
                        LeaveHistories.status == Status.APPROVED,
                        func.extract('year', LeaveHistories.start_date) == year,
                        func.extract('month', LeaveHistories.start_date) == month,
                        Users.branch_id == branch_id
                    )
                )
        )
        result = await self.session.execute(query)
        leave_histories = result.fetchall()

        for leave_history in leave_histories:
            user_id, start_date, end_date, leave_category_name, user_name, part_name = leave_history
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                if date_str not in date_to_users:
                    date_to_users[date_str] = set()
                date_to_users[date_str].add(UserClosedDayDetail(
                    user_id=user_id,
                    user_name=user_name,
                    part_name=part_name,
                    category=leave_category_name
                ))
                current_date += timedelta(days=1)
        
        # 정기 휴무 -> fixed_closed_days 조회
        ## 각 user_id별 최신 created_at을 찾는 쿼리
        latest_contracts = (
            select(
                ContractInfo.user_id,
                func.max(Contract.created_at).label('max_date')
            )
            .select_from(Contract)
            .join(ContractInfo, Contract.contract_info_id == ContractInfo.id)
            .where(Contract.contract_type == ContractType.WORK)
            .group_by(ContractInfo.user_id)
            .subquery()
        )
    
        ## 유저별 최신 WORK 타입 계약 테이블
        current_contract_table = (
            select(
                ContractInfo.user_id,
                Contract.contract_type,
                Contract.created_at,
                Contract.contract_id,
                ContractInfo.hire_date
            )
            .select_from(Contract)
            .join(ContractInfo, Contract.contract_info_id == ContractInfo.id)
                .filter(ContractInfo.employ_status == EmploymentStatus.PERMANENT)
            .where(
                and_(
                    Contract.contract_type == ContractType.WORK,
                    Contract.contract_status == ContractStatus.APPROVE,
                    tuple_(ContractInfo.user_id, Contract.created_at).in_(
                        select(
                            latest_contracts.c.user_id,
                            latest_contracts.c.max_date
                        ).select_from(latest_contracts)
                    )
                )
            )
            .subquery()
        )

        query = (
            select(current_contract_table.c.user_id, current_contract_table.c.hire_date, FixedRestDay.rest_day, FixedRestDay.every_over_week, Users.name, Parts.name)
            .select_from(current_contract_table)
            .join(Users, current_contract_table.c.user_id == Users.id)
            .join(Parts, Users.part_id == Parts.id)
                .filter(Parts.branch_id == branch_id) # Users에서 Branch_id가 빠질 경우를 대비하여 Parts에서 조회
            .join(WorkContract, current_contract_table.c.contract_id == WorkContract.id)
                .filter(
                    WorkContract.is_fixed_rest_day == True,
                    WorkContract.deleted_yn == "n"
                )
            .join(FixedRestDay, WorkContract.id == FixedRestDay.work_contract_id)
        )

        result = await self.session.execute(query)
        fixed_rest_days = result.fetchall()

        for user_id, contract_start_date, rest_day, every_over_week, user_name, part_name in fixed_rest_days:
            first_day_of_month = date(year, month, 1)
            days_in_month = monthrange(year, month)[1]

            for day in range(days_in_month):
                current_day = first_day_of_month + timedelta(days=day)
                if current_day.strftime('%A').upper() != rest_day.name or current_day < contract_start_date:
                    continue
                
                date_str = current_day.strftime('%Y-%m-%d')
                if every_over_week:
                    weeks_since_start = ((current_day - contract_start_date).days // 7)
                    if weeks_since_start % 2 == 0:
                        if date_str not in date_to_users:
                            date_to_users[date_str] = set()
                        date_to_users[date_str].add(UserClosedDayDetail(
                            user_id=user_id,
                            user_name=user_name,
                            part_name=part_name,
                            category="정규휴무"
                        ))
                else:
                    if date_str not in date_to_users:
                        date_to_users[date_str] = set()
                    date_to_users[date_str].add(UserClosedDayDetail(
                        user_id=user_id,
                        user_name=user_name,
                        part_name=part_name,
                        category="정규휴무"
                    ))

        return dict(sorted(date_to_users.items()))

    async def get_all_hospital_closed_days(self, branch_id: int, year: int, month: int) -> List[str]:
        '''
        특정 지점 월간 병원 휴무일 조회 (날짜만, 정규휴무와 특정 휴무)
        '''
        # 병원 특정 휴무일 조회
        query = (
            select(ClosedDays.closed_day_date)
            .filter(
                and_(
                    ClosedDays.branch_id == branch_id,
                    ClosedDays.user_id == None,
                    func.extract('year', ClosedDays.closed_day_date) == year,
                    func.extract('month', ClosedDays.closed_day_date) == month,
                    ClosedDays.deleted_yn == "N"
                )
            )
        )

        result = await self.session.execute(query)
        closed_days = set([closed_day.closed_day_date.strftime("%Y-%m-%d") for closed_day in result.fetchall()])

        # 병원 정기 휴무일 조회
        query = (
            select(BranchWorkSchedule.day_of_week)
            .select_from(Branches)
            .join(WorkPolicies, Branches.id == WorkPolicies.branch_id)
                .filter(Branches.id == branch_id)
            .join(BranchWorkSchedule, WorkPolicies.id == BranchWorkSchedule.work_policy_id)
                .filter(BranchWorkSchedule.is_holiday == True)
        )

        result = await self.session.execute(query)
        
        days_of_week = [day.day_of_week for day in result.fetchall()]

        for day_of_week in days_of_week:
            first_day_of_month = date(year, month, 1)
            days_in_month = monthrange(year, month)[1]

            for day in range(days_in_month):
                current_day = first_day_of_month + timedelta(days=day)
                if current_day.strftime('%A').upper() == day_of_week.name:
                    closed_days.add(current_day.strftime('%Y-%m-%d'))
        
        return sorted(closed_days)
        
    async def get_user_and_hospital_closed_days(self, branch_id: int, user_id: int, year: int, month: int) -> tuple[dict[str, List[UserClosedDayDetail]], List[str]]:
        '''
        사용자의 특정 휴무일과 병원 휴무일을 조회
        '''
        # 직원의 특정 휴무일 조회
        query = (
            select(ClosedDays.closed_day_date, Users.id, Users.name, Parts.name)
            .join(Users, ClosedDays.user_id == Users.id)
            .filter(
                and_(
                    ClosedDays.branch_id == branch_id,
                    ClosedDays.user_id == user_id,  # 본인 것만 조회
                    func.extract('year', ClosedDays.closed_day_date) == year,
                    func.extract('month', ClosedDays.closed_day_date) == month,
                    ClosedDays.deleted_yn == "N"
                )
            )
            .join(Parts, Users.part_id == Parts.id)
        )
        result = await self.session.execute(query)
        closed_days = result.fetchall()

        date_to_users = {}
        for closed_day_date, user_id, user_name, part_name in closed_days:
            date_str = closed_day_date.strftime("%Y-%m-%d")
            if date_str not in date_to_users:
                date_to_users[date_str] = []
            date_to_users[date_str].append(UserClosedDayDetail(
                user_id=user_id,
                user_name=user_name,
                part_name=part_name,
                category="휴무"
            ))

        # 연차 조회
        query = (
            select(LeaveHistories.start_date, LeaveHistories.end_date, LeaveCategory.name, Users.name, Parts.name)
            .join(LeaveCategory, LeaveHistories.leave_category_id == LeaveCategory.id)
            .join(Users, LeaveHistories.user_id == Users.id)
            .join(Parts, Users.part_id == Parts.id)
            .filter(
                and_(
                    LeaveHistories.status == Status.APPROVED,
                    LeaveHistories.user_id == user_id,  # 본인 것만 조회
                    func.extract('year', LeaveHistories.start_date) == year,
                    func.extract('month', LeaveHistories.start_date) == month
                )
            )
        )
        result = await self.session.execute(query)
        leave_histories = result.fetchall()

        for start_date, end_date, leave_category_name, user_name, part_name in leave_histories:
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                if date_str not in date_to_users:
                    date_to_users[date_str] = []
                date_to_users[date_str].append(UserClosedDayDetail(
                    user_id=user_id,
                    user_name=user_name,
                    part_name=part_name,
                    category=leave_category_name
                ))
                current_date += timedelta(days=1)

        # 정기 휴무 조회
        query = (
            select(WorkContract.contract_start_date, FixedRestDay.rest_day, FixedRestDay.every_over_week, Users.name, Parts.name)
            .join(FixedRestDay, FixedRestDay.work_contract_id == WorkContract.id)
            .join(Users, WorkContract.user_id == Users.id)
            .join(Parts, Users.part_id == Parts.id)
            .filter(
                and_(
                    WorkContract.user_id == user_id,  # 본인 것만 조회
                    WorkContract.is_fixed_rest_day == True
                )
            )
        )

        result = await self.session.execute(query)
        fixed_rest_days = result.fetchall()

        for contract_start_date, rest_day, every_over_week, user_name, part_name in fixed_rest_days:
            first_day_of_month = date(year, month, 1)
            days_in_month = monthrange(year, month)[1]

            for day in range(days_in_month):
                current_day = first_day_of_month + timedelta(days=day)
                if current_day.strftime('%A').upper() == rest_day.name and current_day >= contract_start_date:
                    date_str = current_day.strftime('%Y-%m-%d')
                    if every_over_week:
                        weeks_since_start = ((current_day - contract_start_date).days // 7)
                        if weeks_since_start % 2 == 0:
                            if date_str not in date_to_users:
                                date_to_users[date_str] = []
                            date_to_users[date_str].append(UserClosedDayDetail(
                                user_id=user_id,
                                user_name=user_name,
                                part_name=part_name,
                                category="정규휴무"
                            ))
                    else:
                        if date_str not in date_to_users:
                            date_to_users[date_str] = []
                        date_to_users[date_str].append(UserClosedDayDetail(
                            user_id=user_id,
                            user_name=user_name,
                            part_name=part_name,
                            category="정규휴무"
                        ))

        # 병원 휴무일 조회
        hospital_closed_days = await self.get_all_hospital_closed_days(branch_id, year, month)

        return dict(sorted(date_to_users.items())), hospital_closed_days
    
    async def get_all_user_early_clock_ins_group_by_date(self, branch_id: int, year: int, month: int) -> dict[str, EarlyClockInResponseDTO]:
        """
        특정 지점의 모든 직원의 월간 조기 출근 기록 조회
        """
        query = (
            select(EarlyClockIn.early_clock_in, Users.id, Users.name, Parts.name)
            .join(Users, EarlyClockIn.user_id == Users.id)
            .join(Parts, Users.part_id == Parts.id)
            .filter(
                and_(
                    Users.branch_id == branch_id,
                    func.extract('year', EarlyClockIn.early_clock_in) == year,
                    func.extract('month', EarlyClockIn.early_clock_in) == month,
                    EarlyClockIn.deleted_yn == "N"
                )
            )
        )
        
        result = await self.session.execute(query)
        early_clock_ins = result.fetchall()
        
        early_clock_in_days = {}
        for clock_in_time, user_id, user_name, part_name in early_clock_ins:
            date_str = clock_in_time.strftime("%Y-%m-%d")
            time_str = clock_in_time.strftime("%H:%M")
            
            early_clock_in_days[date_str] = EarlyClockInResponseDTO(
                user_id=user_id,
                user_name=f"[{time_str}]{user_name}",
                part_name=part_name
            )
        
        return early_clock_in_days

    async def get_user_early_clock_in(self, branch_id: int, user_id: int, year: int, month: int) -> dict[str, EarlyClockInResponseDTO]:
        """
        특정 직원의 월간 조기 출근 기록 조회
        """
        query = (
            select(EarlyClockIn.early_clock_in, Users.id, Users.name, Parts.name)
            .join(Users, EarlyClockIn.user_id == Users.id)
            .join(Parts, Users.part_id == Parts.id)
            .filter(
                and_(
                    Users.branch_id == branch_id,
                    EarlyClockIn.user_id == user_id,
                    func.extract('year', EarlyClockIn.early_clock_in) == year,
                    func.extract('month', EarlyClockIn.early_clock_in) == month,
                    EarlyClockIn.deleted_yn == "N"
                )
            )
        )
        
        result = await self.session.execute(query)
        early_clock_ins = result.fetchall()
        
        early_clock_in_days = {}
        for clock_in_time, user_id, user_name, part_name in early_clock_ins:
            date_str = clock_in_time.strftime("%Y-%m-%d")
            time_str = clock_in_time.strftime("%H:%M")
            
            early_clock_in_days[date_str] = EarlyClockInResponseDTO(
                user_id=user_id,
                user_name=f"[{time_str}]{user_name}",
                part_name=part_name
            )
        
        return early_clock_in_days


    async def get_user_early_clock_in_dates(self, branch_id: int, user_id: int, year: int, month: int) -> List[str]:
        """
        특정 직원의 월간 조기 출근 날짜만 조회
        """
        today = date.today()
        
        query = (
            select(EarlyClockIn.early_clock_in)
            .filter(
                and_(
                    EarlyClockIn.branch_id == branch_id,
                    EarlyClockIn.user_id == user_id,
                    func.extract('year', EarlyClockIn.early_clock_in) == year,
                    func.extract('month', EarlyClockIn.early_clock_in) == month,
                    func.date(EarlyClockIn.early_clock_in) >= today,
                    EarlyClockIn.deleted_yn == "N"
                )
            )
        )
        
        result = await self.session.execute(query)
        early_clock_ins = result.fetchall()
        
        return sorted([clock_in.early_clock_in.strftime("%Y-%m-%d") for clock_in in early_clock_ins])

    async def delete_early_clock_in(self, branch_id: int, early_clock_in: UserEarlyClockIn) -> bool:
        """
        직원의 조기 출근 시간을 삭제 처리
        """
        try:
            for user_id, dates in early_clock_in.early_clock_in_users.items():
                # 해당 직원이 이 지점 소속인지 확인
                stmt = select(Users).where(
                    and_(
                        Users.id == user_id,
                        Users.branch_id == branch_id,
                        Users.deleted_yn == 'N'
                    )
                )
                result = await self.session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if not user:
                    raise ForbiddenError(
                        detail=f"사용자 ID {user_id}는 해당 지점의 직원이 아닙니다."
                    )

                # 삭제할 레코드 조회
                stmt = (
                    select(EarlyClockIn)
                    .where(
                        and_(
                            EarlyClockIn.user_id == user_id,
                            EarlyClockIn.branch_id == branch_id,
                            EarlyClockIn.early_clock_in.in_(dates),
                            EarlyClockIn.deleted_yn == "N"
                        )
                    )
                )
                result = await self.session.execute(stmt)
                records = result.scalars().all()
                # 삭제 처리
                for record in records:
                    record.deleted_yn = "Y"
                    record.updated_at = datetime.now()

            await self.session.commit()
            return True
        except HTTPException as http_err:
            await self.session.rollback()
            raise http_err
        except Exception as err:
            await self.session.rollback()
            
            

            