from fastapi import HTTPException

from app.cruds.user_management.salary_contract_crud import UserManagementSalaryContractRepository
from app.models.users.users_salary_contract_model import SalaryContract
from app.schemas.user_management.salary_contract import SalaryContractDto


class UserManagementSalaryContractService:
    def __init__(self, salary_contract_repository: UserManagementSalaryContractRepository):
        self.salary_contract_repository = salary_contract_repository

    async def get_salary_contract_by_user_id(self, user_id: int) -> SalaryContractDto:
        return await self.salary_contract_repository.find_dto_by_user_id(
            user_id=user_id
        )

    async def create_salary_contract(self, salary_contract: SalaryContract) -> SalaryContract:
        return await self.salary_contract_repository.create(
            salary_contract=salary_contract
        )

    async def partial_update_salary_contract(self, salary_contract_id: int, user_id: int, update_params: dict) -> SalaryContractDto:
        return await self.salary_contract_repository.partial_update(
            salary_contract_id=salary_contract_id,
            user_id=user_id,
            update_params=update_params
        )