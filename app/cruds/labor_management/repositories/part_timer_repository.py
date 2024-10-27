from typing import List
from app.cruds.labor_management.repositories.part_timer_repository_interface import IPartTimerRepository
from app.cruds.labor_management.dto.part_timer_work_history_response_dto import PartTimerWorkHistoryResponseDTO
from app.cruds.labor_management.dto.part_timers_response_dto import PartTimerSummaryResponseDTO

from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users.users_model import Users
from fastapi import HTTPException, logger
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.users_model import Users
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.commutes.commutes_model import Commutes
from app.models.parts.hour_wage_template_model import HourWageTemplate
from app.models.users.users_work_contract_model import WorkContract
from app.models.branches.rest_days_model import RestDays


class PartTimerRepository(IPartTimerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_part_timers(self, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        part_timer_summary = await self.get_part_timer_summaries(self.session, year, month)
        part_timer_work_hour_and_total_wage = await self.get_part_timer_work_hours_and_total_wage(self.session, year, month)
        return PartTimerSummaryResponseDTO.get_part_timer_list_response(part_timer_summary, part_timer_work_hour_and_total_wage)

    async def get_part_timer_work_history(self, user_id: int, year: int, month: int) -> List[PartTimerWorkHistoryResponseDTO]:
        return []
    
    async def get_all_part_timers_by_branch_id(self, branch_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        return []

    async def get_all_part_timers_by_part_id(self, part_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        return []


    '''
    파트타이머 요약 정보 목록 조회
    '''
    async def get_part_timer_summaries(self, year: int, month: int):
        try:
            part_timer_summary_query = select(
                Users.id.label('user_id'),
                Users.gender.label('gender'),
                Branches.name.label('branch_name'),
                Users.name.label('user_name'),
                Parts.name.label('part_name'),
                func.count(Commutes.user_id).label('work_count')
            ).join(WorkContract, WorkContract.user_id == Users.id) \
                .filter(WorkContract.is_part_timer == True) \
                .join(Branches, Branches.id == Users.branch_id) \
                .join(Parts, Parts.id == Users.part_id) \
                .join(Commutes, Commutes.user_id == Users.id) \
                .filter(func.extract('year', Commutes.clock_in) == year) \
                .filter(func.extract('month', Commutes.clock_in) == month) \
                .group_by(Users.id, Users.name, Branches.name, Parts.name)
            
            result = await self.session.execute(part_timer_summary_query)
            return result.all()
        except Exception as e:
            logger.debug(e.with_traceback())
            raise HTTPException(status_code=500, detail="파트타이머 정보 목록 조회에 실패했습니다.")

    '''
    유저 근무 시간 및 총 급여 조회
    '''
    async def get_part_timer_work_hours_and_total_wage(self, year: int, month: int):
        try:
            query = (
                select(
                    Users.id.label('user_id'),
                    func.coalesce(func.sum(
                        case(
                            (RestDays.id == None, Commutes.work_hours), 
                            else_=0
                        )
                    ), 0).label('regular_work_hours'),
                    func.coalesce(func.sum(
                        case(
                            (RestDays.is_paid == True, Commutes.work_hours), 
                            else_=0
                        )
                    ), 0).label('holiday_work_hours'),
                    func.coalesce(func.sum(Commutes.work_hours), 0).label('total_work_hours'),
                    func.coalesce(func.sum(
                        case(
                            (RestDays.id == None, Commutes.work_hours * HourWageTemplate.hour_wage),
                            else_=Commutes.work_hours * 1.5
                        )
                    ), 0).label('total_wage')
                )
                .join(WorkContract, WorkContract.user_id == Users.id)
                .filter(WorkContract.is_part_timer == True)
                .join(Commutes, Commutes.user_id == Users.id)
                .outerjoin(RestDays, (RestDays.date == func.date(Commutes.clock_in)) & (RestDays.branch_id == Users.branch_id))
                .join(HourWageTemplate, (HourWageTemplate.part_id == Users.part_id) & (HourWageTemplate.branch_id == Users.branch_id))
                .filter(func.extract('year', Commutes.clock_in) == year)
                .filter(func.extract('month', Commutes.clock_in) == month)
                .group_by(Users.id)
            )

            result = await self.session.execute(query)
            return result.all()
        except Exception as e:
            print(e)
            logger.debug(e.with_traceback())
            raise HTTPException(status_code=500, detail="근로 시간 및 급여 정보 조회에 실패했습니다.")
