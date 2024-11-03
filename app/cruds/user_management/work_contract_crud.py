from typing import Optional

from sqlalchemy import select, Tuple, update, delete
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.users.users_model import Users
from app.models.users.users_work_contract_history_model import ContractHistory
from app.models.users.users_work_contract_model import WorkContract, FixedRestDay
from app.schemas.user_work_contract_schemas import WorkContractDto


class UserManagementWorkContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_work_contract_by_user_id(self, user_id: int) -> Optional[WorkContract]:
        stmt = (
            select(WorkContract)
            .options(
                joinedload(WorkContract.user)  # user 정보도 함께 로드
            )
            .options(
                selectinload(WorkContract.fixed_rest_days),  # fixed_rest_days 정보도 함께 로드
                selectinload(WorkContract.break_times)  # break_times 정보도 함께 로드
        )
            .where(WorkContract.user_id == user_id)
            .join(
                WorkContract.user,
            )
            .where(
                Users.deleted_yn == "N",
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_work_contract_by_work_contract_id(self, work_contract_id: int) -> Optional[WorkContract]:
        stmt = (
            select(WorkContract)
            .options(
                selectinload(WorkContract.fixed_rest_days),  # fixed_rest_days 정보도 함께 로드
                selectinload(WorkContract.break_times)  # break_times 정보도 함께 로드
            )
            .where(WorkContract.id == work_contract_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_dto_by_work_contract_id(self, work_contract_id: int) -> WorkContractDto:
        work_contract = await self.find_work_contract_by_work_contract_id(work_contract_id)
        return WorkContractDto.build(work_contract=work_contract)

    async def find_work_contract_part_timer_by_user_id(self, user_id: int) -> Optional[WorkContract]:
        ...

    async def find_user_by_user_id(self, user_id: int) -> Optional[Users]:
        stmt = (
            select(Users)
            .where(Users.id == user_id)
            .where(Users.deleted_yn == "N")
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


    async def create_work_contract_with_rest_days(
            self,
            work_contract_dict: dict,
            fixed_rest_days: list[dict]
    ) -> int:
        try:
            # 1. WorkContract 먼저 생성
            work_contract_stmt = insert(WorkContract).values(**work_contract_dict)
            result = await self.session.execute(work_contract_stmt)

            # 생성된 WorkContract의 id 가져오기
            work_contract_id = result.lastrowid

            # 2. 받은 id로 FixedRestDay 생성
            if fixed_rest_days and work_contract_dict.get('is_fixed_rest_day'):
                rest_days_with_contract_id = [
                    {
                        "work_contract_id": work_contract_id,  # work_contract_id 추가
                        **rest_day
                    }
                    for rest_day in fixed_rest_days
                ]

                rest_days_stmt = insert(FixedRestDay).values(rest_days_with_contract_id)
                await self.session.execute(rest_days_stmt)

            # 3. 모든 작업이 성공하면 커밋
            await self.session.commit()

            return work_contract_id

        except Exception as e:
            # 실패시 롤백
            await self.session.rollback()
            raise e

    async def add_work_contract(self, work_contract: WorkContract) -> int:
        try:
            self.session.add(work_contract)
            await self.session.commit()
            await self.session.refresh(work_contract)
            return work_contract.id
        except Exception as e:
            await self.session.rollback()
            raise e


    async def update_work_contract_with_rest_days(
            self,
            work_contract_id: int,
            update_values: dict,
            fixed_rest_days: Optional[list] = None
    ) -> None:
        try:
            # 1. 근로계약 업데이트
            update_stmt = (
                update(WorkContract)
                .where(WorkContract.id == work_contract_id)
                .values(**update_values)
            )
            await self.session.execute(update_stmt)

            # 2. fixed_rest_days 처리
            if fixed_rest_days is not None:
                # 기존 휴무일 삭제
                delete_stmt = delete(FixedRestDay).where(
                    FixedRestDay.work_contract_id == work_contract_id
                )
                await self.session.execute(delete_stmt)

                # is_fixed_rest_day가 True이고 fixed_rest_days가 있으면 새로 생성
                if update_values.get('is_fixed_rest_day', True) and fixed_rest_days:
                    rest_days_data = [
                        {
                            "work_contract_id": work_contract_id,
                            **rest_day.model_dump()
                        }
                        for rest_day in fixed_rest_days
                    ]
                    insert_stmt = insert(FixedRestDay).values(rest_days_data)
                    await self.session.execute(insert_stmt)

            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            raise e
