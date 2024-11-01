from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users.users_salary_contract_model import SalaryContract
from app.schemas.user_management.salary_contract import SalaryContractDto


class UserManagementSalaryContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, id: int) -> SalaryContract:
        stmt = (
            select(SalaryContract)
            .filter(
                SalaryContract.id == id,
                SalaryContract.deleted_yn == "N"
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().one()

    async def find_by_user_id(self, user_id: int) -> SalaryContract:
        stmt = (
            select(SalaryContract)
            .filter(
                SalaryContract.user_id == user_id,
                SalaryContract.deleted_yn == "N"
            )
        )

        result = await self.session.execute(stmt)
        return result.scalars().one()

    async def find_dto_by_user_id(self, user_id: int) -> SalaryContractDto:
        salary_contract = await self.find_by_user_id(user_id)
        return SalaryContractDto.build(salary_contract=salary_contract)

    async def create(self, salary_contract: SalaryContract):
        self.session.add(salary_contract)
        await self.session.commit()
        await self.session.refresh(salary_contract)
        return salary_contract

    async def partial_update(self, user_id: int, update_params: dict) -> SalaryContractDto:
        salary_contract = await self.find_by_user_id(user_id)

        for key, value in update_params.items():
            setattr(salary_contract, key, value)

        await self.session.commit()
        return SalaryContractDto.build(salary_contract=salary_contract)