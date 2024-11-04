import asyncio
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.cruds.user_management.contract_crud import UserManagementContractRepository
from app.enums.user_management import ContractType
from app.models.users.part_timer.users_part_timer_work_contract_model import PartTimerWorkContract
from app.models.users.users_contract_model import Contract
from app.models.users.users_model import Users
from app.models.users.users_salary_contract_model import SalaryContract
from app.models.users.users_work_contract_history_model import ContractHistory
from app.models.users.users_work_contract_model import WorkContract
from app.schemas.user_management.part_timers_contract_schemas import PartTimerWorkContractDto
from app.schemas.user_management.salary_contract import SalaryContractDto
from app.schemas.user_work_contract_schemas import WorkContractDto
from app.service.template_service import TemplateService as ModusignTemplateService
from app.service.document_service import DocumentService as ModusignDocumentService
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
            contract_repository: UserManagementContractRepository,
    ):
        self.service = service
        self.salary_contract_service = salary_contract_service
        self.work_contract_service = work_contract_service
        self.part_time_contract_service = part_time_contract_service

        self.contract_history_service = contract_history_service
        self.modusign_template_service = ModusignTemplateService()
        self.modusign_document_service = ModusignDocumentService()

        self.contract_repository = contract_repository

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

        work_contract_contract_id, salary_contract_contract_id = asyncio.gather(
            self.create_contract(contract=work_contract_contract),
            self.create_contract(contract=salary_contract_contract)
        )

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

        contract_history = ContractHistory(
            contract_info_id=contract_info_id,
            change_reason=change_reason,
            note=note
        )

        await self.contract_history_service.create_contract_history(contract_history=contract_history)
        return part_time_contract_contract_id

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
    async def create_contract(self, contract: Contract) -> int:
        return await self.contract_repository.add_contract(contract=contract)

    # Contract History
    async def get_contract_histories_by_user_id(self, user_id: int) -> list[ContractHistory]:
        return await self.contract_history_service.get_contract_histories_by_user_id(user_id=user_id)



    async def create_contract2(self, user_id: int, manager_id: int, work_contract_history_id: int) -> int:
        ...
        # user = await self.service.get_user(user_id=user_id)
        # modusign_result = await self.request_contract_by_modusign(user=user)
        #
        # modusign_id = modusign_result.get("id")
        # contract_name = modusign_result.get("title")
        # contract_url = modusign_result.get("file").get("downloadUrl")
        #
        # work_contract_history = self.work_contract_history_service.get_work_contract_history_by_id(
        #     work_contract_histories_id=work_contract_history_id
        # )
        #
        # contract = Contract(
        #     user_id=user_id,
        #     manager_id=manager_id,
        #     work_contract_id=work_contract_history.work_contract.id,
        #     modusign_id=modusign_id,
        #     contract_name=contract_name,
        #     contract_url=contract_url,
        # )
        #
        # contract_id = await add_contract(contract=contract)
        # return contract_id

    async def request_contract_by_modusign(self, user: Users) -> dict:
        template_response = await self.modusign_template_service.get_template(template_id=SAMPLE_TEMPLATE_ID)

        document_data = ModuSignGenerator.convert_template_response_to_document_data(
            template_response=template_response,
            user=user
        )

        result = await self.modusign_document_service.create_document_with_template(document_data=document_data)
        return result

    async def approve_contract(self, modusign_document_id: str, session: AsyncSession):
        """
        계약을 승인하는 로직
        """

        # contract = await find_contract_by_modusign_id(
        #     modusign_id=modusign_document_id,
        #     session=session
        # )
        # if not contract:
        #     return
        #
        # await self.service.update_user_role(
        #     user_id=contract.user_id,
        #     session=session
        # )
        ...
