from typing import List
from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.routes.closed_days.dto.closed_days_response_dto import UserClosedDayDetailDTO
from app.core.database import get_db
from app.models.branches.branches_model import Branches
from app.models.branches.work_policies_model import WorkPolicies, WorkSchedule
from app.models.closed_days.closed_days_model import ClosedDays
from app.models.parts.parts_model import Parts
from app.models.users.users_model import Users
from calendar import monthrange
from datetime import date, timedelta

class ClosedDayService:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def get_all_user_closed_dates(self, branch_id: int, year: int, month: int) -> List[UserClosedDayDetailDTO]:
        '''
        특정 지점에서 모든 직원의 월간 휴무일 조회 (휴가 x)
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
            user_id_to_detail[user_id]["user_closed_days"].append(closed_day_date.strftime("%Y-%m-%d"))

        # TODO: 연차, 정기 휴무 조회 추가
        # 연차 -> leave_history 조회
        # 정기 휴무 -> fixed_closed_days 조회
        # 날짜만 구하기   

        return [
            UserClosedDayDetailDTO(user_id=user_id, **detail)
            for user_id, detail in user_id_to_detail.items()
        ]
        

    async def get_all_hospital_closed_days(self, branch_id: int, year: int, month: int) -> List[str]:
        # 특정 지점에서 병원의 특정 휴무일 조회
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
        





        
        
        

        