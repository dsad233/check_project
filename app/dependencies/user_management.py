from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.cruds.user_management.base_crud import UserManagementRepository
from app.cruds.user_management.contract_crud import UserManagementContractRepository
from app.cruds.user_management.contract_info_crud import UserManagementContractInfoRepository
from app.cruds.user_management.part_time_contract_crud import UserManagementPartTimeContractRepository
from app.cruds.user_management.salary_contract_crud import UserManagementSalaryContractRepository
from app.cruds.user_management.work_contract_crud import UserManagementWorkContractRepository
from app.cruds.user_management.work_contract_history_crud import UserManagementContractHistoryRepository
from app.dependencies.modusign import get_modusign_document_service, get_modusign_template_service
from app.service.user_management.contract_info_service import UserManagementContractInfoService
from app.service.user_management.contract_service import UserManagementContractService
from app.service.user_management.part_time_contract_service import UserManagementPartTimeContractService
from app.service.user_management.salary_contract_service import UserManagementSalaryContractService
from app.service.user_management.service import UserManagementService, UserQueryService
from app.service.user_management.work_contract_history_service import UserManagementContractHistoryService
from app.service.user_management.work_contract_service import UserManagementWorkContractService

# UserManagement
def get_user_management_repository(session: AsyncSession = Depends(get_db)):
    return UserManagementRepository(session=session)
def get_user_management_service(repository: UserManagementRepository = Depends(get_user_management_repository)):
    return UserManagementService(repository=repository)


# UserManagementWorkContractHistory
def get_user_management_work_contract_history_repository(session: AsyncSession = Depends(get_db)):
    return UserManagementContractHistoryRepository(session=session)

def get_user_management_work_contract_history_service(
        work_contract_history_repository: UserManagementContractHistoryRepository = Depends(get_user_management_work_contract_history_repository)):
    return UserManagementContractHistoryService(contract_history_repository=work_contract_history_repository)

# UserManagementPartTimeContract
def get_user_management_part_time_contract_repository(session: AsyncSession = Depends(get_db)):
    return UserManagementPartTimeContractRepository(session=session)

def get_user_management_part_time_contract_service(
        part_time_contract_repository: UserManagementPartTimeContractRepository = Depends(get_user_management_part_time_contract_repository)):
    return UserManagementPartTimeContractService(part_time_contract_repository=part_time_contract_repository)



# UserManagementWorkContract
def get_user_management_work_contract_repository(session: AsyncSession = Depends(get_db)):
    return UserManagementWorkContractRepository(session=session)

def get_user_management_work_contract_service(
        work_contract_repository: UserManagementWorkContractRepository = Depends(get_user_management_work_contract_repository),
        work_contract_history_service: UserManagementContractHistoryService = Depends(get_user_management_work_contract_history_service)
):
    return UserManagementWorkContractService(
        work_contract_repository=work_contract_repository,
        work_contract_history_service=work_contract_history_service
    )

# UserManagementSalaryContract
def get_user_management_salary_contract_repository(session: AsyncSession = Depends(get_db)):
    return UserManagementSalaryContractRepository(session=session)

def get_user_management_salary_contract_service(
        salary_contract_repository: UserManagementSalaryContractRepository = Depends(get_user_management_salary_contract_repository)):
    return UserManagementSalaryContractService(salary_contract_repository=salary_contract_repository)


# UserManagementContract
def get_user_management_contract_repository(session: AsyncSession = Depends(get_db)):
    return UserManagementContractRepository(session=session)

def get_user_management_contract_service(
        user_management_service: UserManagementService = Depends(get_user_management_service),
        work_contract_service: UserManagementWorkContractService = Depends(get_user_management_work_contract_service),
        salary_contract_service: UserManagementSalaryContractService = Depends(get_user_management_salary_contract_service),
        part_time_contract_service: UserManagementPartTimeContractService = Depends(get_user_management_part_time_contract_service),
        work_contract_history_service: UserManagementContractHistoryService = Depends(get_user_management_work_contract_history_service),
        contract_repository: UserManagementContractRepository = Depends(get_user_management_contract_repository),
        modusign_document_service = Depends(get_modusign_document_service),
        modusign_template_service = Depends(get_modusign_template_service)
):

    return UserManagementContractService(
        service=user_management_service,
        salary_contract_service=salary_contract_service,
        work_contract_service=work_contract_service,
        part_time_contract_service=part_time_contract_service,
        contract_history_service=work_contract_history_service,
        contract_repository=contract_repository,
        modusign_document_service=modusign_document_service,
        modusign_template_service=modusign_template_service
    )

# UserManagementContractInfo
def get_user_management_contract_info_repository(session: AsyncSession = Depends(get_db)):
    return UserManagementContractInfoRepository(session=session)

def get_user_management_contract_info_service(
        user_management_service: UserManagementService = Depends(get_user_management_service),
        contract_service: UserManagementContractService = Depends(get_user_management_contract_service),
        contract_history_service: UserManagementContractHistoryService = Depends(get_user_management_work_contract_history_service),
        contract_info_repository: UserManagementContractInfoRepository = Depends(get_user_management_contract_info_repository)):
    return UserManagementContractInfoService(
        user_management_service=user_management_service,
        contract_service=contract_service,
        contract_history_service=contract_history_service,
        contract_info_repository=contract_info_repository
    )


# UserManagementPartTimeContract
def get_user_management_part_time_contract_repository(session: AsyncSession = Depends(get_db)):
    return UserManagementPartTimeContractRepository(session=session)

def get_user_management_part_time_contract_service(
        part_time_contract_repository: UserManagementPartTimeContractRepository = Depends(get_user_management_part_time_contract_repository)):
    return UserManagementPartTimeContractService(part_time_contract_repository=part_time_contract_repository)



# UserQuery
def get_user_query_service():
    return UserQueryService()
