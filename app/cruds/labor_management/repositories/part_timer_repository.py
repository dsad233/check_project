from typing import List

from app.api.routes.labor_management.dto.part_timer_commute_history_correction_request import PartTimerCommuteHistoryCorrectionRequestDTO
from app.api.routes.labor_management.dto.part_timer_commute_history_correction_response import PartTimerCommuteHistoryCorrectionResponseDTO
from app.cruds.labor_management.repositories.part_timer_repository_interface import IPartTimerRepository
from app.cruds.labor_management.dto.part_timer_work_history_response_dto import PartTimerWorkHistoryDTO, PartTimerWorkHistorySummaryDTO
from app.cruds.labor_management.dto.part_timers_response_dto import PartTimerSummaryResponseDTO

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums.users import EmploymentStatus
from app.models.users.users_model import Users
from sqlalchemy import Select, and_, case, extract, func, select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.users_model import Users
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.commutes.commutes_model import Commutes
from app.models.users.part_timer.users_part_timer_work_contract_model import PartTimerAdditionalInfo, PartTimerHourlyWage, PartTimerWorkContract, PartTimerWorkingTime
from app.models.branches.rest_days_model import RestDays

# TODO: 실제 DB 레포지토리 구현
class PartTimerRepository(IPartTimerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_part_timers(self, year: int, month: int, page_num: int, page_size: int) -> List[PartTimerSummaryResponseDTO]:
        part_timer_summary = await self.get_part_timer_summaries(year, month)
        part_timer_work_hour_and_total_wage = await self.get_part_timer_work_hours_and_total_wage(year, month)
        return PartTimerSummaryResponseDTO.get_part_timer_summaries_response(part_timer_summary, part_timer_work_hour_and_total_wage)

    '''
    출퇴근 기반 근무 내역 조회
    '''
    async def get_part_timer_work_histories(self, user_id: int, year: int, month: int) -> List[PartTimerWorkHistoryDTO]:
        query = (self.get_part_timer_work_history_summary_select_query()
            .join(Parts, Parts.id == Commutes.part_id)
                .filter(Commutes.user_id == user_id)
                .filter(extract('year', Commutes.clock_in) == year)
                .filter(extract('month', Commutes.clock_in) == month)
            .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Commutes.user_id)
                .filter(extract('dow', Commutes.clock_in) == PartTimerWorkContract.weekly_work_days)
            .join(PartTimerWorkingTime, PartTimerWorkingTime.part_timer_work_contract_id == PartTimerWorkContract.id)
            .join(PartTimerHourlyWage, PartTimerHourlyWage.part_timer_work_contract_id == PartTimerWorkContract.id)
        )

        result = await self.session.execute(query)
        records = result.all()

        return [PartTimerWorkHistoryDTO(**record._asdict()) for record in records]
    
    '''
    계약서 기반 근무 내역 조회
    '''
    async def get_part_timer_work_histories_by_contract(self, user_id: int, year: int, month: int) -> List[PartTimerWorkHistoryDTO]:
        query = (self.get_part_timer_work_history_summary_select_query_by_contract()
            .join(Parts, Parts.id == Commutes.part_id)
                .filter(Commutes.user_id == user_id)
                .filter(extract('year', Commutes.clock_in) == year)
                .filter(extract('month', Commutes.clock_in) == month)
            .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Commutes.user_id)
                .filter(extract('dow', Commutes.clock_in) == PartTimerWorkContract.weekly_work_days)
            .join(PartTimerWorkingTime, PartTimerWorkingTime.part_timer_work_contract_id == PartTimerWorkContract.id)
            .join(PartTimerHourlyWage, PartTimerHourlyWage.part_timer_work_contract_id == PartTimerWorkContract.id)
            .outerjoin(PartTimerAdditionalInfo, PartTimerAdditionalInfo.commute_id == Commutes.id)
        )

        result = await self.session.execute(query)
        records = result.all()

        return [PartTimerWorkHistoryDTO(**record._asdict()) for record in records]
    
    async def get_all_part_timers_by_branch_id(self, branch_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        summary = await self.get_part_timer_summaries_by_branch_id(branch_id, year, month)
        work_hour_and_total_wage = await self.get_part_timer_work_hours_and_total_wage_by_branch_id(branch_id, year, month)
        return PartTimerSummaryResponseDTO.get_part_timer_list_response(summary, work_hour_and_total_wage)
    
    async def get_all_part_timers_by_branch_id_and_part_id(self, branch_id: int, part_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        summary = await self.get_part_timer_summaries_by_branch_id_and_part_id(branch_id, part_id, year, month)
        work_hour_and_total_wage = await self.get_part_timer_work_hours_and_total_wage_by_branch_id_and_part_id(branch_id, part_id, year, month)
        return PartTimerSummaryResponseDTO.get_part_timer_list_response(summary, work_hour_and_total_wage)
    
    async def get_part_timer_work_history_summary_by_user_id(self, user_id: int, year: int, month: int) -> PartTimerWorkHistorySummaryDTO:
        raise NotImplementedError
    
    async def get_part_timer_by_user_info(self, year: int, month: int, user_name: str | None, phone_number: str | None, branch_id: int, part_id: int) -> List[PartTimerSummaryResponseDTO]:
        summary = await self.get_part_timer_summaries_by_user_info(year, month, user_name, phone_number, branch_id, part_id)
        work_hour_and_total_wage = await self.get_part_timer_work_hours_and_total_wage_by_branch_id_and_part_id_and_user_info(branch_id, part_id, year, month, user_name, phone_number)
        return PartTimerSummaryResponseDTO.get_part_timer_list_response(summary, work_hour_and_total_wage)  

    async def update_part_timer_work_history(self, commute_id: int, correction_data: PartTimerCommuteHistoryCorrectionRequestDTO) -> PartTimerCommuteHistoryCorrectionResponseDTO:       
        response = PartTimerCommuteHistoryCorrectionResponseDTO()
        response.commute_id = commute_id
        query = (
            update(Commutes)
            .where(Commutes.id == commute_id)
            .values(
                clock_in=correction_data.work_start_set_time,
                clock_out=correction_data.work_end_set_time
            )
        )

        await self.session.execute(query)
        await self.session.commit()

        response.work_start_set_time = correction_data.work_start_set_time
        response.work_end_set_time = correction_data.work_end_set_time
        response.work_hours = correction_data.work_end_set_time - correction_data.work_start_set_time - correction_data.rest_minutes
        
        query = (
            update(PartTimerAdditionalInfo)
            .where(PartTimerAdditionalInfo.commute_id == commute_id)
            .values(
                rest_minutes=correction_data.rest_minutes,
                part_detail=correction_data.part_detail
            )
        )
        
        response.part_detail = correction_data.part_detail
        response.rest_minutes = correction_data.rest_minutes

        await self.session.execute(query)
        await self.session.commit()
        return response
    
    async def exist_part_timer_work_history(self, commute_id: int) -> bool:
        query = select(Commutes.id).filter(Commutes.id == commute_id).exists()
        result = await self.session.execute(query)
        return result.scalar()

    def get_summary_select_query(self) -> Select:
        return select(
            Users.id.label('user_id'),
            Users.gender.label('gender'),
            Branches.name.label('branch_name'),
            Users.name.label('user_name'),
            Parts.name.label('part_name'),
            func.count(Commutes.user_id).label('work_days'),
            Users.phone_number,
            Branches.id.label('branch_id'),
            Parts.id.label('part_id')
        )
    
    def get_work_hours_and_total_wage_select_query(self) -> Select:
        return select(
            Users.id.label('user_id'),
            func.coalesce(func.sum(case((RestDays.id == None, Commutes.work_hours), else_=0)), 0).label('hospital_work_hours'),
            func.coalesce(func.sum(case((RestDays.is_paid == True, Commutes.work_hours), else_=0)), 0).label('holiday_work_hours'),
            func.coalesce(func.sum(Commutes.work_hours), 0).label('total_work_hours'),
            func.coalesce(func.sum(case(
                (RestDays.id == None, Commutes.work_hours * PartTimerHourlyWage.hourly_wage),
                else_=case(
                    (Commutes.work_hours >= 8, Commutes.work_hours * PartTimerHourlyWage.hourly_wage * 1.5 + (Commutes.work_hours - 8) * PartTimerHourlyWage.hourly_wage * 2),
                    else_=Commutes.work_hours * PartTimerHourlyWage.hourly_wage * 1.5))), 0).label('total_wage')
        )
    
    '''
    출퇴근 기반 근무 내역 조회 Select Query
    '''
    def get_part_timer_work_history_summary_select_query(self) -> Select:
        # 휴게시간을 변경한 기록이 있다면 변경된 휴게시간을 사용하고, 없다면 계약서에 있는 휴게시간을 사용  
        rest_minutes = case((PartTimerAdditionalInfo.rest_minutes != None, PartTimerAdditionalInfo.rest_minutes), else_=PartTimerWorkContract.rest_minutes)
        work_start_set_time = case((PartTimerWorkingTime.work_start_time == None, Commutes.clock_in), else_=PartTimerWorkingTime.work_start_time)
        work_end_set_time = case((PartTimerWorkingTime.work_end_time == None, Commutes.clock_out), else_=PartTimerWorkingTime.work_end_time)

        return select(
            Commutes.id.label('commute_id'),
            Parts.name.label('part_name'),
            Parts.task,
            Commutes.clock_in.label('work_start_time'),
            Commutes.clock_out.label('work_end_time'),
            work_start_set_time.label('work_start_set_time'),
            work_end_set_time.label('work_end_set_time'),
            (work_end_set_time - work_start_set_time - rest_minutes).label('work_hours'),
            rest_minutes.label('rest_minutes'),
            (PartTimerHourlyWage.hourly_wage * (work_end_set_time - work_start_set_time - rest_minutes)).label('total_wage'),
            Commutes.created_at
        )
    
    '''
    계약서 기반 근무 내역 조회 Select Query
    '''
    def get_part_timer_work_history_summary_select_query_by_contract(self) -> Select:
        # 휴게시간을 변경한 기록이 있다면 변경된 휴게시간을 사용하고, 없다면 계약서에 있는 휴게시간을 사용  
        rest_minutes = case((PartTimerAdditionalInfo.rest_minutes != None, PartTimerAdditionalInfo.rest_minutes), else_=PartTimerWorkContract.rest_minutes)
        work_start_set_time = case((PartTimerWorkingTime.work_start_time == None, Commutes.clock_in), else_=PartTimerWorkingTime.work_start_time)
        work_end_set_time = case((PartTimerWorkingTime.work_end_time == None, Commutes.clock_out), else_=PartTimerWorkingTime.work_end_time)
        return select(
            Commutes.id.label('commute_id'),
            Parts.name.label('part_name'),
            Parts.task,
            Commutes.clock_in.label('work_start_time'),
            Commutes.clock_out.label('work_end_time'),
            work_end_set_time.label('work_end_set_time'),
            (work_end_set_time - work_start_set_time - rest_minutes).label('work_hours'),
            rest_minutes.label('rest_minutes'),
            (PartTimerHourlyWage.hourly_wage * (work_end_set_time - work_start_set_time - rest_minutes)).label('total_wage'),
            Commutes.created_at
        )
    
    '''
    파트타이머 요약 정보 목록 조회
    '''
    async def get_part_timer_summaries(self, year: int, month: int):
        part_timer_summary_query = self.get_summary_select_query() \
            .join(Branches, Branches.id == Users.branch_id) \
            .filter(Users.employment_status == EmploymentStatus.TEMPORARY) \
            .join(Parts, Parts.id == Users.part_id) \
            .join(Commutes, Commutes.user_id == Users.id) \
            .filter(func.extract('year', Commutes.clock_in) == year) \
            .filter(func.extract('month', Commutes.clock_in) == month) \
            .group_by(Users.id, Users.name, Branches.name, Parts.name)
        
        result = await self.session.execute(part_timer_summary_query)
        return result.all()
        
    '''
    지점별 파트타이머 요약 정보 목록 조회
    '''
    async def get_part_timer_summaries_by_branch_id(self, branch_id: int, year: int, month: int):
        part_timer_summary_query = self.get_summary_select_query() \
            .join(Branches, Branches.id == Users.branch_id) \
                .filter(Branches.id == branch_id) \
                .filter(Users.employment_status == EmploymentStatus.TEMPORARY) \
            .join(Parts, Parts.id == Users.part_id) \
            .join(Commutes, Commutes.user_id == Users.id) \
            .filter(func.extract('year', Commutes.clock_in) == year) \
            .filter(func.extract('month', Commutes.clock_in) == month) \
            .group_by(Users.id, Users.name, Branches.name, Parts.name)
        
        result = await self.session.execute(part_timer_summary_query)
        return result.all()

    '''
    지점별 및 파트별 파트타이머 요약 정보 목록 조회
    '''
    async def get_part_timer_summaries_by_branch_id_and_part_id(self, branch_id: int, part_id: int, year: int, month: int):
        part_timer_summary_query = self.get_summary_select_query() \
            .join(Branches, Branches.id == Users.branch_id) \
                .filter(Branches.id == branch_id) \
                .filter(Users.employment_status == EmploymentStatus.TEMPORARY) \
            .join(Parts, Parts.id == Users.part_id) \
                .filter(Parts.id == part_id) \
            .join(Commutes, Commutes.user_id == Users.id) \
                .filter(func.extract('year', Commutes.clock_in) == year) \
                .filter(func.extract('month', Commutes.clock_in) == month) \
            .group_by(Users.id, Users.name, Branches.name, Parts.name)
        
        result = await self.session.execute(part_timer_summary_query)
        return result.all()
        
    '''
    특정 직원의 파트타이머 요약 정보 조회
    '''
    async def get_part_timer_summaries_by_user_id(self, user_id: int, year: int, month: int):
        part_timer_summary_query = self.get_summary_select_query() \
            .join(Branches, Branches.id == Users.branch_id) \
                .filter(Users.id == user_id) \
                .filter(Users.employment_status == EmploymentStatus.TEMPORARY) \
            .join(Parts, Parts.id == Users.part_id) \
            .join(Commutes, Commutes.user_id == Users.id) \
                .filter(func.extract('year', Commutes.clock_in) == year) \
                .filter(func.extract('month', Commutes.clock_in) == month) \
        
        result = await self.session.execute(part_timer_summary_query)
        return result.all()
    
    '''
    이름과 전화번호로 특정 파트타이머 요약 정보 조회
    '''
    async def get_part_timer_summaries_by_user_info(self, year: int, month: int, user_name: str | None, phone_number: str | None, branch_id: int, part_id: int):
        if user_name and phone_number:
            query_condition = or_(Users.name == user_name, Users.phone_number == phone_number)
        elif user_name:
            query_condition = Users.name == user_name
        elif phone_number:
            query_condition = Users.phone_number == phone_number

        part_timer_summary_query = self.get_summary_select_query() \
            .join(Branches, Branches.id == Users.branch_id) \
                .filter(Branches.id == branch_id) \
                .filter(Users.employment_status == EmploymentStatus.TEMPORARY) \
                .filter(query_condition) \
            .join(Parts, Parts.id == Users.part_id) \
                .filter(Parts.id == part_id) \
            .join(Commutes, Commutes.user_id == Users.id) \
                .filter(func.extract('year', Commutes.clock_in) == year) \
                .filter(func.extract('month', Commutes.clock_in) == month) \
            .group_by(Users.id, Users.name, Branches.name, Parts.name)
        
        result = await self.session.execute(part_timer_summary_query)
        return result.all()

    '''
    특정 월에 대한 모든 파트 타이머의 근무 시간 및 총 급여 조회
    '''
    async def get_part_timer_work_hours_and_total_wage(self, year: int, month: int):
        query = self.get_work_hours_and_total_wage_select_query() \
            .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id) \
            .join(PartTimerHourlyWage, (PartTimerHourlyWage.part_timer_work_contract_id == PartTimerWorkContract.id)) \
            .join(Commutes, Commutes.user_id == Users.id) \
                .filter(func.extract('year', Commutes.clock_in) == year) \
                .filter(func.extract('month', Commutes.clock_in) == month) \
            .outerjoin(RestDays, (RestDays.date == func.date(Commutes.clock_in))) \
            .group_by(Users.id)
        
        result = await self.session.execute(query)
        return result.all()

    '''
    지점별 유저 근무 시간 및 총 급여 조회
    '''
    async def get_part_timer_work_hours_and_total_wage_by_branch_id(self, branch_id: int, year: int, month: int):
        query = self.get_work_hours_and_total_wage_select_query() \
            .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id) \
                .filter(Users.branch_id == branch_id) \
            .join(PartTimerHourlyWage, (PartTimerHourlyWage.part_timer_work_contract_id == PartTimerWorkContract.id)) \
            .join(Commutes, Commutes.user_id == Users.id) \
                .filter(func.extract('year', Commutes.clock_in) == year) \
                .filter(func.extract('month', Commutes.clock_in) == month) \
            .outerjoin(RestDays, (RestDays.date == func.date(Commutes.clock_in)) & (RestDays.branch_id == branch_id)) \
            .group_by(Users.id)

        result = await self.session.execute(query)
        return result.all()

    '''
    지점별 및 파트별 유저 근무 시간 및 총 급여 조회
    '''
    async def get_part_timer_work_hours_and_total_wage_by_branch_id_and_part_id(self, branch_id: int, part_id: int, year: int, month: int):
        query = self.get_work_hours_and_total_wage_select_query() \
            .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id) \
                .filter(Users.branch_id == branch_id) \
                .filter(Users.part_id == part_id) \
            .join(PartTimerHourlyWage, (PartTimerHourlyWage.part_timer_work_contract_id == PartTimerWorkContract.id)) \
            .join(Commutes, Commutes.user_id == Users.id) \
                .filter(func.extract('year', Commutes.clock_in) == year) \
                .filter(func.extract('month', Commutes.clock_in) == month) \
            .outerjoin(RestDays, (RestDays.date == func.date(Commutes.clock_in)) & (RestDays.branch_id == branch_id)) \
            .group_by(Users.id)

        result = await self.session.execute(query)
        return result.all()
    
    '''
    특정 직원의 근무 시간 및 총 급여 조회
    '''
    async def get_part_timer_work_hours_and_total_wage_by_branch_id_and_part_id_and_user_info(self, branch_id: int, part_id: int, year: int, month: int, user_name: str | None, phone_number: str | None):
        if user_name and phone_number:
            query_condition = or_(Users.name == user_name, Users.phone_number == phone_number)
        elif user_name:
            query_condition = Users.name == user_name
        elif phone_number:
            query_condition = Users.phone_number == phone_number

        query = self.get_work_hours_and_total_wage_select_query() \
            .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id) \
                .filter(Users.branch_id == branch_id) \
                .filter(Users.part_id == part_id) \
                .filter(query_condition) \
            .join(PartTimerHourlyWage, (PartTimerHourlyWage.part_timer_work_contract_id == PartTimerWorkContract.id)) \
            .join(Commutes, Commutes.user_id == Users.id) \
                .filter(func.extract('year', Commutes.clock_in) == year) \
                .filter(func.extract('month', Commutes.clock_in) == month) \
            .outerjoin(RestDays, (RestDays.date == func.date(Commutes.clock_in)) & (RestDays.branch_id == branch_id)) \
            .group_by(Users.id)

        result = await self.session.execute(query)
        return result.all()

