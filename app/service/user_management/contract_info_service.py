import asyncio
from typing import Optional

from fastapi import Depends

from app.core.database import get_db
from app.cruds.user_management.contract_info_crud import UserManagementContractInfoRepository
from app.enums.user_management import ContractType
from app.enums.users import EmploymentStatus
from app.models.users.users_contract_info_model import ContractInfo
from app.models.users.users_work_contract_history_model import ContractHistory
from app.schemas.user_management.contract_info import ResponseTotalContractInfo, ContractInfoDto
from app.service.user_management.contract_service import UserManagementContractService
from app.service.user_management.service import UserManagementService
from app.service.user_management.work_contract_history_service import UserManagementContractHistoryService


class UserManagementContractInfoService:
    def __init__(
            self,
            user_management_service: UserManagementService,
            contract_service: UserManagementContractService,
            contract_history_service: UserManagementContractHistoryService,
            contract_info_repository: UserManagementContractInfoRepository,
    ):
        self.user_management_service = user_management_service
        self.contract_service = contract_service
        self.contract_history_service = contract_history_service
        self.contract_info_repository = contract_info_repository

    async def get_total_contract_info(self, user_id: int, contract_info_id: int) -> ResponseTotalContractInfo:
        work_contract, salary_contract, part_time_contract = None, None, None
        user = await self.user_management_service.get_user(user_id)
        contract_info = await self.contract_info_repository.find_by_id(contract_info_id)

        for contract in contract_info.contracts:
            if contract.contract_type == ContractType.WORK:
                work_contract = await self.contract_service.get_work_contract_by_id(user_id)

            if contract.contract_type == ContractType.SALARY:
                salary_contract = await self.contract_service.get_salary_contract_by_id(user_id)

            if contract.contract_type == ContractType.PART_TIME:
                part_time_contract = await self.contract_service.get_part_time_contract_by_id(user_id)

        if user.employment_status == EmploymentStatus.PERMANENT:
            data = ResponseTotalContractInfo.build(
                contract_info=ContractInfoDto.build(contract_info),
                work_contract=work_contract,
                salary_contract=salary_contract,
                part_time_contract=None
            )
        else:
            data = ResponseTotalContractInfo.build(
                contract_info=ContractInfoDto.build(contract_info),
                work_contract=None,
                salary_contract=None,
                part_time_contract=part_time_contract
            )

        return data

    async def add_contract_info(self, contract_info: ContractInfo) -> int:
        created_contract_info_id = await self.contract_info_repository.create(contract_info)
        return created_contract_info_id

    async def update_contract_info(
            self,
            contract_info_id: int,
            update_params: dict,
            change_reason: str,
            note: Optional[str] = None
    ):
        contract_id_map = {
            ContractType.WORK: None,
            ContractType.SALARY: None,
            ContractType.PART_TIME: None
        }

        contracts = await self.contract_info_repository.find_by_id(contract_info_id).contracts
        for contract in contracts:
            contract_id_map[contract.contract_type] = contract.id

        # 비동기 작업 목록 생성
        update_tasks = []
        for contract_type, contract_id in contract_id_map.items():
            contract_data = update_params.get(contract_type.value.lower() + "_contract")
            if contract_data and contract_id:
                update_tasks.append(
                    self.contract_service.update_contract(
                        contract_id=contract_id,
                        contract_type=contract_type,
                        update_params_dict=contract_data
                    )
                )

        # 비동기 작업을 병렬로 실행
        await asyncio.gather(*update_tasks)

        contract_history = ContractHistory(
            contract_info_id=contract_info_id,
            change_reason=change_reason,
            note=note
        )

        # 계약 정보 업데이트
        await self.contract_history_service.create_contract_history(
            contract_history=contract_history
        )

        return True

    async def send_contracts(self, user_id: int, contract_info_id: int):
        contract_info = await self.contract_info_repository.find_by_id(contract_info_id)

        for contract in contract_info.contracts:
            await self.contract_service.send_contract_by_modusign(
                user_id=user_id,
                contract=contract
            )