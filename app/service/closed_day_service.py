from typing import List
from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.routes.closed_days.dto.closed_days_response_dto import UserClosedDayDetail, UserClosedDayDetailDTO, UserClosedDaySummaryDTO
from app.core.database import get_db
from app.enums.users import Status
from app.models.branches.branches_model import Branches
from app.models.branches.leave_categories_model import LeaveCategory
from app.models.branches.work_policies_model import WorkPolicies, WorkSchedule
from app.models.closed_days.closed_days_model import ClosedDays
from app.models.parts.parts_model import Parts
from app.models.users.leave_histories_model import LeaveHistories
from app.models.users.users_model import Users
from calendar import monthrange
from datetime import date, timedelta

from app.models.users.users_work_contract_model import FixedRestDay, WorkContract

class ClosedDayService:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_all_user_closed_days_group_by_user_id(self, branch_id: int, year: int, month: int) -> dict[int, List[UserClosedDayDetail]]:
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
        query = (
            select(WorkContract.user_id, WorkContract.contract_start_date, FixedRestDay.rest_day, FixedRestDay.every_over_week)
            .join(FixedRestDay, FixedRestDay.work_contract_id == WorkContract.id)
                .filter(
                    and_(
                        WorkContract.user_id.in_(user_ids),
                        WorkContract.is_fixed_rest_day == True
                    )
                )
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
            user_id_to_detail[user_id]["user_closed_days"].sort(key=lambda x: x.closed_date)

        return [
            UserClosedDayDetailDTO(user_id=user_id, **detail)
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
                date_to_users[date_str] = []
            date_to_users[date_str].append(UserClosedDayDetail(
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
                    date_to_users[date_str] = []
                date_to_users[date_str].append(UserClosedDayDetail(
                    user_id=user_id,
                    user_name=user_name,
                    part_name=part_name,
                    category=leave_category_name
                ))
                current_date += timedelta(days=1)
        
        # 정기 휴무 -> fixed_closed_days 조회
        query = (
            select(WorkContract.user_id, WorkContract.contract_start_date, FixedRestDay.rest_day, FixedRestDay.every_over_week, Users.name, Parts.name)
            .join(FixedRestDay, FixedRestDay.work_contract_id == WorkContract.id)
            .join(Users, WorkContract.user_id == Users.id)
            .join(Parts, Users.part_id == Parts.id)
                .filter(
                    and_(
                        Users.branch_id == branch_id,
                        WorkContract.is_fixed_rest_day == True
                    )
                )
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
            select(WorkSchedule.day_of_week)
            .select_from(Branches)
            .join(WorkPolicies, Branches.id == WorkPolicies.branch_id)
                .filter(Branches.id == branch_id)
            .join(WorkSchedule, WorkPolicies.id == WorkSchedule.work_policy_id)
                .filter(WorkSchedule.is_holiday == True)
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
        





        
        
        

        