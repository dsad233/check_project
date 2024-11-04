from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users.users_salary_contract_model import SalaryContract
from app.schemas.user_management.salary_contract import SalaryContractDto


class UserManagementSalaryContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, salary_contract_id: int) -> SalaryContract:
        stmt = (
            select(SalaryContract)
            .filter(
                SalaryContract.id == salary_contract_id,
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

    async def find_dto_by_id(self, salary_contract_id: int) -> SalaryContractDto:
        salary_contract = await self.find_by_id(salary_contract_id=salary_contract_id)
        return SalaryContractDto.build(salary_contract=salary_contract)

    async def find_dto_by_user_id(self, user_id: int) -> SalaryContractDto:
        salary_contract = await self.find_by_user_id(user_id)
        return SalaryContractDto.build(salary_contract=salary_contract)

    async def create(self, salary_contract: SalaryContract) -> int:
        self.session.add(salary_contract)
        await self.session.commit()
        await self.session.refresh(salary_contract)
        return salary_contract.id

    async def partial_update(self, salary_contract_id: int, update_params: dict) -> SalaryContractDto:
        # 업데이트 쿼리 생성
        stmt = (
            update(SalaryContract)
            .filter(SalaryContract.id == salary_contract_id)
            .values(**update_params)
        )

        # 업데이트 실행 및 변경된 행의 개수 확인
        result = await self.session.execute(stmt)
        await self.session.commit()

        if result.rowcount == 0:
            # 변경된 행이 없으면 404 에러 발생
            raise HTTPException(status_code=404, detail="Salary contract not found")

        return await self.find_dto_by_id(salary_contract_id=salary_contract_id)
