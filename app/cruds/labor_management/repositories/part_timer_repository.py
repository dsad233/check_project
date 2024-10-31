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
from sqlalchemy import Select, Time, and_, case, exists, extract, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users.users_model import Users
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.commutes.commutes_model import Commutes
from app.models.users.part_timer.users_part_timer_work_contract_model import PartTimerAdditionalInfo, PartTimerHourlyWage, PartTimerWorkContract

class PartTimerRepository(IPartTimerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def calculate_hours_and_wage(self, year: int, month: int, user_id_subquery: Select) -> List[PartTimerSummaryResponseDTO]:
        '''
        주어진 연도와 월에 해당하는 파트 타이머들의 근무 시간과 임금을 계산합니다.

        Args:
            year (int): 연도
            month (int): 월
            user_id_subquery (Select): 파트 타이머의 user_id를 갖고 있는 서브쿼리(컬럼명 : id)

        Returns:
            List[PartTimerSummaryResponseDTO]: 파트 타이머들의 근무 시간과 임금 정보를 담은 DTO 리스트
        '''
        work_hours = func.TIME_TO_SEC(
            func.TIMEDIFF(
                PartTimerAdditionalInfo.work_set_end_time,
                PartTimerAdditionalInfo.work_set_start_time
            )
        ) / 3600
        rest_hours = PartTimerAdditionalInfo.rest_minutes / 60

        query = (
            select(
                Users.id.label('user_id'),
                Users.gender.label('gender'),
                Branches.name.label('branch_name'),
                Users.name.label('user_name'),
                Parts.name.label('part_name'),
                func.count(Commutes.user_id).label('work_days'),
                Users.phone_number,
                Branches.id.label('branch_id'),
                Parts.id.label('part_id'),
                func.sum(
                    case(
                        (PartTimerAdditionalInfo.work_type == 'HOSPITAL', work_hours - rest_hours),
                        else_=0
                    )
                ).label('hospital_work_hours'),
                func.sum(
                    case(
                        (PartTimerAdditionalInfo.work_type == 'HOLIDAY', work_hours - rest_hours),
                        else_=0
                    )
                ).label('holiday_work_hours'),
                func.sum(work_hours - rest_hours).label('total_work_hours'),
                func.sum((work_hours - rest_hours) * PartTimerHourlyWage.hourly_wage).label('total_wage'),
            )
            .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
            .join(Branches, Branches.id == Users.branch_id)
            .join(Parts, Parts.id == Users.part_id)
            .join(Commutes, Commutes.user_id == Users.id)
                .filter(
                    and_(
                        Users.id.in_(select(user_id_subquery.columns.id)),
                        extract('year', Commutes.clock_in) == year,
                        extract('month', Commutes.clock_in) == month
                    )
                )
            .join(PartTimerAdditionalInfo, PartTimerAdditionalInfo.commute_id == Commutes.id)
            .join(PartTimerHourlyWage, PartTimerHourlyWage.part_timer_work_contract_id == PartTimerWorkContract.id)
                .filter(
                    and_(
                        PartTimerAdditionalInfo.work_set_start_time >= PartTimerHourlyWage.calculate_start_time,
                        PartTimerAdditionalInfo.work_set_start_time <= PartTimerHourlyWage.calculate_end_time
                    )
                )
            .group_by(Users.id)
        )

        result = await self.session.execute(query)

        return [PartTimerSummaryResponseDTO(**record._asdict()) for record in result.all()]

    async def get_all_part_timers(self, year: int, month: int, page_num: int, page_size: int) -> List[PartTimerSummaryResponseDTO]:
        '''
        모든 파트 타이머의 요약 정보를 페이지네이션하여 가져옵니다.

        Args:
            year (int): 연도
            month (int): 월
            page_num (int): 페이지 번호
            page_size (int): 페이지 크기

        Returns:
            List[PartTimerSummaryResponseDTO]: 파트 타이머들의 요약 정보 리스트
        '''
        part_timer_find_subquery = (
            select(Users.id)
                .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
                .join(Branches, Branches.id == Users.branch_id)
                .join(Parts, Parts.id == Users.part_id)
                .join(Commutes, Commutes.user_id == Users.id)
            .group_by(Users.id)
            .offset((page_num - 1) * page_size)
            .limit(page_size)
        ).subquery()

        return await self.calculate_hours_and_wage(year, month, part_timer_find_subquery)

    '''
    특정 직원의 근무 내역 조회
    '''
    async def get_part_timer_work_histories(self, user_id: int, year: int, month: int) -> List[PartTimerWorkHistoryDTO]:
        '''
        특정 직원의 근무 내역을 조회합니다.

        Args:
            user_id (int): 직원의 ID
            year (int): 연도
            month (int): 월

        Returns:
            List[PartTimerWorkHistoryDTO]: 직원의 근무 내역 리스트
        '''
        query = (self.get_part_timer_work_history_summary_select_query()
            .select_from(Users)
            .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
            .join(Branches, Branches.id == Users.branch_id)
            .join(Parts, Parts.id == Users.part_id)
            .join(Commutes, Commutes.user_id == Users.id)
                .filter(
                    and_(
                        Commutes.user_id == user_id,
                        extract('year', Commutes.clock_in) == year,
                        extract('month', Commutes.clock_in) == month
                    )
                )
            .join(PartTimerAdditionalInfo, PartTimerAdditionalInfo.commute_id == Commutes.id)
            .join(PartTimerHourlyWage, PartTimerHourlyWage.part_timer_work_contract_id == PartTimerWorkContract.id)
                .filter(
                    and_(
                        PartTimerAdditionalInfo.work_set_start_time >= PartTimerHourlyWage.calculate_start_time,
                        PartTimerAdditionalInfo.work_set_start_time <= PartTimerHourlyWage.calculate_end_time
                    )
                )
        )

        result = await self.session.execute(query)
        records = result.all()

        return [PartTimerWorkHistoryDTO(**record._asdict()) for record in records]
    
    async def get_all_part_timers_by_branch_id(self, branch_id: int, year: int, month: int, page_num: int, page_size: int) -> List[PartTimerSummaryResponseDTO]:
        '''
        특정 지점의 모든 파트 타이머의 요약 정보를 페이지네이션하여 가져옵니다.

        Args:
            branch_id (int): 지점 ID
            year (int): 연도
            month (int): 월
            page_num (int): 페이지 번호
            page_size (int): 페이지 크기

        Returns:
            List[PartTimerSummaryResponseDTO]: 파트 타이머들의 요약 정보 리스트
        '''
        part_timer_find_subquery = (
            select(Users.id)
                .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
                .join(Branches, Branches.id == Users.branch_id)
                    .filter(Branches.id == branch_id)
                .join(Parts, Parts.id == Users.part_id)
                .join(Commutes, Commutes.user_id == Users.id)
            .group_by(Users.id)
                .offset((page_num - 1) * page_size)
                .limit(page_size)
        ).subquery()

        return await self.calculate_hours_and_wage(year, month, part_timer_find_subquery)
    
    async def get_all_part_timers_by_branch_id_and_part_id(self, branch_id: int, part_id: int, year: int, month: int, page_num: int, page_size: int) -> List[PartTimerSummaryResponseDTO]:
        '''
        특정 지점 및 파트의 모든 파트 타이머의 요약 정보를 페이지네이션하여 가져옵니다.

        Args:
            branch_id (int): 지점 ID
            part_id (int): 파트 ID
            year (int): 연도
            month (int): 월
            page_num (int): 페이지 번호
            page_size (int): 페이지 크기

        Returns:
            List[PartTimerSummaryResponseDTO]: 파트 타이머들의 요약 정보 리스트
        '''
        part_timer_find_subquery = (
            select(Users.id)
                .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
                .join(Branches, Branches.id == Users.branch_id)
                    .filter(Branches.id == branch_id)
                .join(Parts, Parts.id == Users.part_id)
                    .filter(Parts.id == part_id)
                .join(Commutes, Commutes.user_id == Users.id)
            .group_by(Users.id)
                .offset((page_num - 1) * page_size)
                .limit(page_size)
        ).subquery()

        return await self.calculate_hours_and_wage(year, month, part_timer_find_subquery)
    
    async def get_part_timer_work_history_summary_by_user_id(self, user_id: int, year: int, month: int) -> PartTimerWorkHistorySummaryDTO:
        '''
        특정 직원의 근무 내역 요약 정보를 조회합니다.

        Args:
            user_id (int): 직원의 ID
            year (int): 연도
            month (int): 월

        Returns:
            PartTimerWorkHistorySummaryDTO: 직원의 근무 내역 요약 정보
        '''
        work_hours = func.TIME_TO_SEC(
            func.TIMEDIFF(
                PartTimerAdditionalInfo.work_set_end_time,
                PartTimerAdditionalInfo.work_set_start_time
            )
        ) / 3600
        rest_hours = PartTimerAdditionalInfo.rest_minutes / 60

        query = (
            select(
                func.count(Commutes.user_id).label('total_work_days'),
                func.sum(
                    case(
                        (PartTimerAdditionalInfo.work_type == 'HOSPITAL', work_hours - rest_hours),
                        else_=0
                    )
                ).label('total_hospital_work_hours'),
                func.sum(
                    case(
                        (PartTimerAdditionalInfo.work_type == 'HOLIDAY', work_hours - rest_hours),
                        else_=0
                    )
                ).label('total_holiday_work_hours'),
                func.sum(work_hours - rest_hours).label('total_work_hours'),
                func.sum((work_hours - rest_hours) * PartTimerHourlyWage.hourly_wage).label('total_wage'),
            )
            .select_from(Users)
            .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
                .filter(PartTimerWorkContract.user_id == user_id)
            .join(Commutes, Commutes.user_id == Users.id)
                .filter(
                    and_(
                        Users.id == user_id,
                        extract('year', Commutes.clock_in) == year,
                        extract('month', Commutes.clock_in) == month
                    )
                )
            .join(PartTimerAdditionalInfo, PartTimerAdditionalInfo.commute_id == Commutes.id)
            .join(PartTimerHourlyWage, PartTimerHourlyWage.part_timer_work_contract_id == PartTimerWorkContract.id)
                .filter(
                    and_(
                        PartTimerAdditionalInfo.work_set_start_time >= PartTimerHourlyWage.calculate_start_time,
                        PartTimerAdditionalInfo.work_set_start_time <= PartTimerHourlyWage.calculate_end_time
                    )
                )
        )

        result = await self.session.execute(query)

        return PartTimerWorkHistorySummaryDTO(**result.first()._asdict())
    
    async def get_part_timer_by_user_info(self, year: int, month: int, user_name: str | None, phone_number: str | None, branch_id: int, part_id: int) -> List[PartTimerSummaryResponseDTO]:
        '''
        사용자 이름 또는 전화번호로 파트 타이머를 검색하여 요약 정보를 가져옵니다.

        Args:
            year (int): 연도
            month (int): 월
            user_name (str | None): 사용자 이름 (옵션)
            phone_number (str | None): 전화번호 (옵션)
            branch_id (int): 지점 ID
            part_id (int): 파트 ID

        Returns:
            List[PartTimerSummaryResponseDTO]: 검색된 파트 타이머들의 요약 정보 리스트
        '''
        condition = []
        if user_name:
            condition.append(Users.name.ilike(f'%{user_name}%'))
        if phone_number:
            condition.append(Users.phone_number.ilike(f'%{phone_number}%'))

        part_timer_find_subquery = (
            select(Users.id)
                .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
                    .filter(and_(*condition))
                .join(Branches, Branches.id == Users.branch_id)
                    .filter(Branches.id == branch_id)
                .join(Parts, Parts.id == Users.part_id)
                    .filter(Parts.id == part_id)
                .join(Commutes, Commutes.user_id == Users.id)
            .group_by(Users.id)
        ).subquery()
        
        return await self.calculate_hours_and_wage(year, month, part_timer_find_subquery)

    async def update_part_timer_work_history(self, commute_id: int, correction_data: PartTimerCommuteHistoryCorrectionRequestDTO) -> PartTimerCommuteHistoryCorrectionResponseDTO:       
        '''
        특정 근무내역을 수정합니다.
        * 프론트에서 모든 내역을 다시 불러오기 때문에 총 급여는 따로 계산하지 않고 있습니다.
        
        Args:
            commute_id (int): 근무내역 ID
            correction_data (PartTimerCommuteHistoryCorrectionRequestDTO): 수정할 데이터

        Returns:
            PartTimerCommuteHistoryCorrectionResponseDTO: 수정된 근무내역 정보
        '''
        response = PartTimerCommuteHistoryCorrectionResponseDTO.Builder(commute_id, correction_data) \
            .set_work_time(correction_data.work_start_set_time, correction_data.work_end_set_time) \
            .set_rest_minutes(correction_data.rest_minutes) \
            .build()
        
        query = (
            update(PartTimerAdditionalInfo)
            .where(PartTimerAdditionalInfo.commute_id == commute_id)
            .values(
                work_type=correction_data.work_type,
                rest_minutes=correction_data.rest_minutes,
                work_set_start_time=correction_data.work_start_set_time,
                work_set_end_time=correction_data.work_end_set_time
            )
        )

        await self.session.execute(query)
        await self.session.commit()

        return response
    
    async def exist_part_timer_work_history(self, commute_id: int) -> bool:
        '''
        특정 근무내역이 존재하는지 확인합니다.

        Args:
            commute_id (int): 근무내역 ID

        Returns:
            bool: 근무내역 존재 여부
        '''
        query = select(exists().where(PartTimerAdditionalInfo.commute_id == commute_id))
        result = await self.session.execute(query)
        return result.scalar()
    
    async def get_total_count_part_timers(self, year: int, month: int) -> int:
        '''
        주어진 연도와 월에 해당하는 모든 파트 타이머의 총 수를 반환합니다.

        Args:
            year (int): 연도
            month (int): 월

        Returns:
            int: 파트 타이머의 총 수
        '''
        query = (
            select(func.count(Users.id))
                .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
                .join(Branches, Branches.id == Users.branch_id)
                .join(Parts, Parts.id == Users.part_id)
                .join(Commutes, Commutes.user_id == Users.id)
                    .filter(
                        and_(
                            func.extract('year', Commutes.clock_in) == year,
                            func.extract('month', Commutes.clock_in) == month
                        )
                    )
            .group_by(Users.id)
        )

        result = await self.session.execute(query)
        return result.scalar()
    
    async def get_total_count_part_timers_by_branch_id(self, branch_id: int, year: int, month: int) -> int:
        '''
        특정 지점의 주어진 연도와 월에 해당하는 파트 타이머의 총 수를 반환합니다.

        Args:
            branch_id (int): 지점 ID
            year (int): 연도
            month (int): 월

        Returns:
            int: 파트 타이머의 총 수
        '''
        query = (
            select(func.count(Users.id))
                .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
                .join(Branches, Branches.id == Users.branch_id)
                    .filter(Branches.id == branch_id)
                .join(Parts, Parts.id == Users.part_id)
                .join(Commutes, Commutes.user_id == Users.id)
                    .filter(
                        and_(
                            func.extract('year', Commutes.clock_in) == year,
                            func.extract('month', Commutes.clock_in) == month
                        )
                    )
            .group_by(Users.id)
        )

        result = await self.session.execute(query)
        return result.scalar()
    
    async def get_total_count_part_timers_by_branch_id_and_part_id(self, branch_id: int, part_id: int, year: int, month: int) -> int:
        '''
        특정 지점 및 파트의 주어진 연도와 월에 해당하는 파트 타이머의 총 수를 반환합니다.

        Args:
            branch_id (int): 지점 ID
            part_id (int): 파트 ID
            year (int): 연도
            month (int): 월

        Returns:
            int: 파트 타이머의 총 수
        '''
        query = (
            select(func.count(Users.id))
                .join(PartTimerWorkContract, PartTimerWorkContract.user_id == Users.id)
                .join(Branches, Branches.id == Users.branch_id)
                    .filter(Branches.id == branch_id)
                .join(Parts, Parts.id == Users.part_id)
                    .filter(Parts.id == part_id)    
                .join(Commutes, Commutes.user_id == Users.id)
                    .filter(
                        and_(
                            func.extract('year', Commutes.clock_in) == year,
                            func.extract('month', Commutes.clock_in) == month
                        )
                    )
            .group_by(Users.id)
        )

        result = await self.session.execute(query)
        return result.scalar()
    
    # ----------------------------------------------------------------------------------------------------------------------------

    def get_summary_select_query(self) -> Select:
        '''
        파트 타이머 요약 정보를 가져오는 Select 쿼리를 반환합니다.

        Returns:
            Select: 파트 타이머 요약 정보 쿼리
        '''
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
    
    '''
    근무 내역 조회 Select Query
    '''
    def get_part_timer_work_history_summary_select_query(self) -> Select:
        '''
        근무 내역 조회를 위한 Select 쿼리를 반환합니다.

        Returns:
            Select: 근무 내역 조회 쿼리
        '''
        work_hours = func.TIME_TO_SEC(
            func.TIMEDIFF(
                PartTimerAdditionalInfo.work_set_end_time,
                PartTimerAdditionalInfo.work_set_start_time
            )
        ) / 3600
        rest_hours = PartTimerAdditionalInfo.rest_minutes / 60

        return select(
            Commutes.id.label('commute_id'),
            Parts.name.label('part_name'),
            PartTimerAdditionalInfo.work_type,
            func.cast(Commutes.clock_in, Time).label('work_start_time'),
            func.cast(Commutes.clock_out, Time).label('work_end_time'),
            PartTimerAdditionalInfo.work_set_start_time.label('work_start_set_time'),
            PartTimerAdditionalInfo.work_set_end_time.label('work_end_set_time'),
            (work_hours - rest_hours).label('work_hours'),
            PartTimerAdditionalInfo.rest_minutes,
            (PartTimerHourlyWage.hourly_wage * (work_hours - rest_hours)).label('total_wage'),
            Commutes.created_at
        )
    
    '''
    파트타이머 요약 정보 목록 조회
    '''
    async def get_part_timer_summaries(self, year: int, month: int):
        '''
        주어진 연도와 월에 해당하는 파트 타이머 요약 정보를 가져옵니다.

        Args:
            year (int): 연도
            month (int): 월

        Returns:
            List: 파트 타이머 요약 정보 리스트
        '''
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
        '''
        특정 지점의 주어진 연도와 월에 해당하는 파트 타이머 요약 정보를 가져옵니다.

        Args:
            branch_id (int): 지점 ID
            year (int): 연도
            month (int): 월

        Returns:
            List: 파트 타이머 요약 정보 리스트
        '''
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
        '''
        특정 지점 및 파트의 주어진 연도와 월에 해당하는 파트 타이머 요약 정보를 가져옵니다.

        Args:
            branch_id (int): 지점 ID
            part_id (int): 파트 ID
            year (int): 연도
            month (int): 월

        Returns:
            List: 파트 타이머 요약 정보 리스트
        '''
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
        '''
        특정 직원의 주어진 연도와 월에 해당하는 파트 타이머 요약 정보를 가져옵니다.

        Args:
            user_id (int): 직원 ID
            year (int): 연도
            month (int): 월

        Returns:
            List: 파트 타이머 요약 정보 리스트
        '''
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

