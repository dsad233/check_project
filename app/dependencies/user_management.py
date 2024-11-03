from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.cruds.user_management.salary_contract_crud import UserManagementSalaryContractRepository
from app.service.user_management.salary_contract_service import UserManagementSalaryContractService


# UserManagementSalaryContract
def get_user_management_salary_contract_repository(session: AsyncSession = Depends(get_db)):
    return UserManagementSalaryContractRepository(
        session=session
    )

def get_user_management_salary_contract_service(salary_contract_repository: UserManagementSalaryContractRepository = Depends(get_user_management_salary_contract_repository)):
    return UserManagementSalaryContractService(
        salary_contract_repository=salary_contract_repository
    )
