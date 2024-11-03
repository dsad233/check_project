import asyncio

from app.core.database import get_db
from app.cruds.user_management.contract_info_crud import UserManagementContractInfoRepository
from app.enums.user_management import ContractType
from app.enums.users import EmploymentStatus
from app.models.users.users_contract_info_model import ContractInfo
from app.schemas.user_management.contract_info import ResponseTotalContractInfo, ContractInfoDto
from app.service.user_management.contract_service import UserManagementContractService
from app.service.user_management.service import UserManagementService


class UserManagementContractInfoService:
    def __init__(
            self,
            user_management_service: UserManagementService,
            contract_service: UserManagementContractService,
            contract_info_repository: UserManagementContractInfoRepository
    ):
        self.user_management_service = user_management_service
        self.contract_service = contract_service

        self.contract_info_repository = contract_info_repository

    async def get_total_contract_info(self, user_id: int, contract_info_id: int) -> ResponseTotalContractInfo:
        user = await self.user_management_service.get_user(user_id, session=get_db())
        contract_info = await self.contract_info_repository.find_by_id(contract_info_id)

        for contract in contract_info.contracts:
            if contract.contract_type == ContractType.WORK:
                work_contract = await self.contract_service.get_work_contract_by_id(user_id)

            if contract.contract_type == ContractType.SALARY:
                salary_contract = await self.contract_service.get_salary_contract_by_id(user_id)

            # if contract.contract_type == ContractType.PART_TIME:
            #     part_time_contract = await self.contract_service.get_part_time_contract_by_id(user_id)

        if user.employment_status == EmploymentStatus.PERMANENT:
            data = ResponseTotalContractInfo.build(
                contract_info=ContractInfoDto.build(contract_info),
                work_contract=work_contract,
                salary_contract=salary_contract
            )
        else:
            # data = ResponseTotalContractInfo.build(
            #     contract_info=ContractInfoDto.build(contract_info),
            #     part_time_contract=part_time_contract
            # )
            raise NotImplementedError("임시직은 아직 지원하지 않습니다.")

        return data


    async def add_contract_info(self, contract_info: ContractInfo) -> int:
        created_contract_info_id = await self.contract_info_repository.create(contract_info)
        return created_contract_info_id

    async def update_contract_info(self, user_id: int, contract_info_id: int, update_params: dict):
        ...
