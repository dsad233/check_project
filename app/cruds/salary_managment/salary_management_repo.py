
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.salary_managment.dto.fixed_salary_info_dto import FixedSalaryInfoDTO
from app.enums.user_management import ContractStatus, ContractType
from app.models.branches.branches_model import Branches
from app.models.parts.parts_model import Parts
from app.models.users.users_contract_info_model import ContractInfo
from app.models.users.users_contract_model import Contract
from app.models.users.users_model import Users
from app.models.users.users_salary_contract_model import SalaryContract

class SalaryManagementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_fixed_salary_info_by_branch(self, branch_id: int) -> list[FixedSalaryInfoDTO]:
        """
        근로시간과 상관없는 고정된 정보 조회
        """
        salary_columns = [
            ContractInfo.hire_date,
            ContractInfo.resignation_date,
            SalaryContract.monthly_salary,
            SalaryContract.annual_leave_allowance,
            SalaryContract.annual_leave_count,
            SalaryContract.annual_leave_hour_per_day,
            SalaryContract.duty_allowance,
            SalaryContract.meal_allowance,
            SalaryContract.vehicle_maintenance_allowance,
            SalaryContract.weekly_rest_hours
        ]

        user_salary_contract_subquery = (
            select(ContractInfo.user_id, *salary_columns)
            .join(Contract, ContractInfo.id == Contract.contract_info_id)
            .filter(
                Contract.contract_type == ContractType.SALARY,
                Contract.contract_status == ContractStatus.APPROVE
            )
            .join(SalaryContract, Contract.contract_id == SalaryContract.id)
        ).subquery()

        # 근로시간과 상관없는 고정된 정보 조회 (월급, 연차 정보 etc)
        query = (
            select(Users.id, Users.remaining_annual_leave, Parts.name, *salary_columns)
            .join(Branches, Users.id == Branches.user_id)
                .filter(Branches.id == branch_id)
            .join(Parts, Users.part_id == Parts.id)
            .join(user_salary_contract_subquery, Users.id == user_salary_contract_subquery.c.user_id)
        )
        
        result = await self.session.execute(query)
        return [FixedSalaryInfoDTO.to_DTO(row) for row in result.all()]
    
    def get_user_salary_contract_info_by_branch(self, branch_id: int, year: int, month: int):
        """
        근로시간과 상관있는 정보 조회
        """
        # TODO: 월간 직원별 근로시간 조회
        ## user_id, clock_in, clock_out

        # TODO: 각 날짜별로 어떤 근무였는지 분류, 휴일인지 아닌지 확인
        ## clock_in, clock_out, is_holiday

        # TODO: 근무 시간 계산
        ## normal_work_hours, overtime_work_hours, night_work_hours, holiday_work_hours

        # TODO: 각 근무별 수당 계산
        ## normal_work_allowance, overtime_work_allowance, night_work_allowance, holiday_work_allowance




        
