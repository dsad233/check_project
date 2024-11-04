import asyncio
from typing import Optional

from fastapi import Depends

from app.core.database import get_db
from app.cruds.user_management.contract_crud import UserManagementContractRepository
from app.enums.user_management import ContractType, ContractStatus
from app.models.users.part_timer.users_part_timer_work_contract_model import PartTimerWorkContract
from app.models.users.users_contract_model import Contract
from app.models.users.users_salary_contract_model import SalaryContract
from app.models.users.users_work_contract_history_model import ContractHistory
from app.models.users.users_work_contract_model import WorkContract
from app.schemas.modusign_schemas import TemplateResponse
from app.schemas.user_management.part_timers_contract_schemas import PartTimerWorkContractDto
from app.schemas.user_management.salary_contract import SalaryContractDto
from app.schemas.user_work_contract_schemas import WorkContractDto
from app.service.template_service import TemplateService as ModusignTemplateService
from app.service.document_service import DocumentService as ModusignDocumentService
from app.service.user_management.part_time_contract_service import UserManagementPartTimeContractService
from app.service.user_management.salary_contract_service import UserManagementSalaryContractService
from app.service.user_management.service import UserManagementService
from app.service.user_management.work_contract_history_service import UserManagementContractHistoryService
from app.service.user_management.work_contract_service import UserManagementWorkContractService
from app.utils.modusign_utils import ModuSignGenerator


SAMPLE_TEMPLATE_ID = "e7193300-96da-11ef-8b54-adaae74d0aa0"

class UserManagementContractService:
    def __init__(
            self,
            service: UserManagementService,
            salary_contract_service: UserManagementSalaryContractService,
            work_contract_service: UserManagementWorkContractService,
            part_time_contract_service: UserManagementPartTimeContractService,
            contract_history_service: UserManagementContractHistoryService,
            modusign_template_service: ModusignTemplateService,
            modusign_document_service: ModusignDocumentService,
            contract_repository: UserManagementContractRepository,
    ):
        self.service = service
        self.salary_contract_service = salary_contract_service
        self.work_contract_service = work_contract_service
        self.part_time_contract_service = part_time_contract_service

        self.contract_history_service = contract_history_service
        self.modusign_template_service = modusign_template_service
        self.modusign_document_service = modusign_document_service

        self.contract_repository = contract_repository

    # Contract Register
    async def register_permanent_contract(
            self,
            contract_info_id: int,
            work_contract: WorkContract,
            salary_contract: SalaryContract,
            note: Optional[str],
            change_reason: Optional[str],
    ) -> bool:
        work_contract_id = await self.create_work_contract(work_contract=work_contract)
        salary_contract_id = await self.create_salary_contract(salary_contract=salary_contract)

        work_contract_contract = Contract(
            contract_info_id=contract_info_id,
            contract_type=ContractType.WORK,
            contract_id=work_contract_id,
        )
        salary_contract_contract = Contract(
            contract_info_id=contract_info_id,
            contract_type=ContractType.SALARY,
            contract_id=salary_contract_id,
        )

        # gather 메시지는 일단 Transaction 에러 발생 가능성으로 인해 보류
        # await asyncio.gather(
        #     self.create_contract(contract=work_contract_contract),
        #     self.create_contract(contract=salary_contract_contract)
        # )

        await self.create_contract(contract=work_contract_contract),
        await self.create_contract(contract=salary_contract_contract)


        contract_history = ContractHistory(
            contract_info_id=contract_info_id,
            change_reason=change_reason,
            note=note
        )

        await self.contract_history_service.create_contract_history(contract_history=contract_history)
        return True


    async def register_temporary_contract(
            self,
            contract_info_id: int,
            part_time_contract: PartTimerWorkContract,
            note: Optional[str],
            change_reason: Optional[str]
    ) -> int:
        part_time_contract_id = await self.create_part_time_contract(part_time_contract=part_time_contract)

        part_time_contract_contract = Contract(
            contract_info_id=contract_info_id,
            contract_type=ContractType.PART_TIME,
            contract_id=part_time_contract_id,
        )

        part_time_contract_contract_id = await self.create_contract(contract=part_time_contract_contract)
        contract_history = ContractHistory(contract_info_id=contract_info_id, change_reason=change_reason, note=note)
        await self.contract_history_service.create_contract_history(contract_history=contract_history)
        return part_time_contract_contract_id


    # Contract Update
    async def update_contract(
            self,
            contract_id: int,
            contract_type: ContractType,
            update_params_dict: dict,
    ) -> bool:
        if contract_type == ContractType.WORK:
            work_contract = await self.work_contract_service.get_work_contract_by_id(work_contract_id=contract_id)
            await self.work_contract_service.partial_update_work_contract(
                work_contract_id=contract_id,
                update_params=update_params_dict
            )

        if contract_type == ContractType.SALARY:
            salary_contract = await self.salary_contract_service.get_salary_contract_by_id(salary_contract_id=contract_id)
            await self.salary_contract_service.partial_update_salary_contract(
                salary_contract_id=contract_id,
                update_params=update_params_dict
            )

        if contract_type == ContractType.PART_TIME:
            part_time_contract = await self.part_time_contract_service.get_part_time_contract_by_id(part_time_contract_id=contract_id)
            await self.part_time_contract_service.partial_update_part_time_contract(
                part_time_contract_id=contract_id,
                update_params=update_params_dict
            )

        return True

    # Part Time Contract
    async def get_part_time_contract_by_id(self, part_time_contract_id: int) -> PartTimerWorkContractDto:
        return await self.part_time_contract_service.get_part_time_contract_by_id(part_time_contract_id=part_time_contract_id)
    async def create_part_time_contract(self, part_time_contract: PartTimerWorkContract) -> int:
        return await self.part_time_contract_service.create_part_time_contract(part_time_contract=part_time_contract)

    # Work Contract
    async def get_work_contract_by_id(self, work_contract_id: int) -> WorkContractDto:
        return await self.work_contract_service.get_work_contract_by_id(work_contract_id=work_contract_id)
    async def create_work_contract(self, work_contract: WorkContract) -> int:
        return await self.work_contract_service.create_work_contract(work_contract=work_contract)

    # Salary Contract
    async def get_salary_contract_by_id(self, salary_contract_id: int) -> SalaryContractDto:
        return await self.salary_contract_service.get_salary_contract_by_id(salary_contract_id=salary_contract_id)
    async def create_salary_contract(self, salary_contract: SalaryContract) -> int:
        return await self.salary_contract_service.create_salary_contract(salary_contract=salary_contract)

    # Contract
    async def get_contract_by_modusign_id(self, modusign_id: str) -> Contract:
        return await self.contract_repository.find_contract_by_modusign_id(modusign_id=modusign_id)
    async def create_contract(self, contract: Contract) -> int:
        return await self.contract_repository.add_contract(contract=contract)

    # Contract History
    async def get_contract_histories_by_user_id(self, user_id: int) -> list[ContractHistory]:
        return await self.contract_history_service.get_contract_histories_by_user_id(user_id=user_id)

    # Send Contract By Modusign
    async def send_contract_by_modusign(
            self,
            user_id: int,
            contract: Contract,
            modusign_template_id: str = SAMPLE_TEMPLATE_ID,
    ):
        user = await self.service.get_user(user_id=user_id)

        if contract.contract_type != ContractType.WORK:
            return False

        template_response = await self.get_modusign_template_by_id(template_id=modusign_template_id)

        document_data = ModuSignGenerator.convert_template_response_to_document_data(
            template_response=template_response,
            user=user
        )

        modusign_result = await self.modusign_document_service.create_document_with_template(document_data=document_data)
        # TODO : modusign result에 따라 분기 처리

        update_params = {
            "modusign_id": modusign_result.get("id"),
            "contract_name": modusign_result.get("title"),
            "contract_url": modusign_result.get("file").get("downloadUrl")
        }

        await self.contract_repository.update_contract(
            contract_id=contract.id,
            update_params=update_params
        )

        return True

    async def get_modusign_template_by_id(self, template_id: str) -> TemplateResponse:
        return await self.modusign_template_service.get_template(template_id=template_id)

    async def callback_by_modusign(self, modusign_document_id: str) -> bool:
        contract = await self.get_contract_by_modusign_id(modusign_id=modusign_document_id)
        result = await self.update_contract_status(
            contract_id=contract.id,
            contract_status=ContractStatus.APPROVE
        )

        if not result:
            return False

        session = get_db()

        if await self.__check_all_signed(contract_info_id=contract.contract_info_id):
            await self.service.update_user_role(
                user_id=contract.contract_info.user.id,
                session=session,
                role=contract.contract_info.role
            )

    async def __check_all_signed(self, contract_info_id: int) -> bool:
        contracts = await self.contract_repository.find_contracts_by_contract_info_id(contract_info_id=contract_info_id)
        for contract in contracts:
            if contract.contract_status != ContractStatus.APPROVE:
                return False
        return True

    async def update_contract_status(
            self,
            contract_id: int,
            contract_status: ContractStatus = ContractStatus.APPROVE
    ) -> bool:
        update_params = {
            "contract_status": contract_status
        }

        return await self.contract_repository.update_contract(
            contract_id=contract_id,
            update_params=update_params
        )


    # async def approve_contract(
    #         self,
    #         user_id: int,
    #         contract: Contract,
    # ) -> bool:
    #     """
    #     계약을 발송하는 로직
    #     """
    #     user: Users = await self.service.get_user(user_id=user_id)
    #     contract_type = contract.contract_type
    #
    #     if contract_type == ContractType.WORK:
    #         ...
    #
    #     if contract_type == ContractType.SALARY:
    #         ...
    #
    #     if contract_type == ContractType.PART_TIME:
    #         ...
    #
    #
    #     return True

    # async def create_contract2(self, user_id: int, manager_id: int, work_contract_history_id: int) -> int:
    #     user = await self.service.get_user(user_id=user_id)
    #     modusign_result = await self.request_contract_by_modusign(user=user)
    #
    #     modusign_id = modusign_result.get("id")
    #     contract_name = modusign_result.get("title")
    #     contract_url = modusign_result.get("file").get("downloadUrl")
    #
    #     work_contract_history = self.work_contract_history_service.get_work_contract_history_by_id(
    #         work_contract_histories_id=work_contract_history_id
    #     )
    #
    #     contract = Contract(
    #         user_id=user_id,
    #         manager_id=manager_id,
    #         work_contract_id=work_contract_history.work_contract.id,
    #         modusign_id=modusign_id,
    #         contract_name=contract_name,
    #         contract_url=contract_url,
    #     )
    #
    #     contract_id = await add_contract(contract=contract)
    #     return contract_id

    # async def request_contract_by_modusign(self, user: Users) -> dict:
    #     template_response = await self.modusign_template_service.get_template(template_id=SAMPLE_TEMPLATE_ID)
    #
    #     document_data = ModuSignGenerator.convert_template_response_to_document_data(
    #         template_response=template_response,
    #         user=user
    #     )
    #
    #     result = await self.modusign_document_service.create_document_with_template(document_data=document_data)
    #     return result

