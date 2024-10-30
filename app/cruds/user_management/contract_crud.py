import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, insert, text
from sqlalchemy.orm import selectinload, joinedload

from app.models.users.users_contract_model import Contract, ContractSendMailHistory
from app.models.users.users_model import Users

logger = logging.getLogger(__name__)

async def find_user_by_id_with_contracts(*, session: AsyncSession, user_id: int) -> Optional[Users]:
    stmt = (
        select(Users)
        .options(
            # user_id 관계로 연결된 contracts 로드
            selectinload(Users.contracts_user_id).options(
                # 각 contract의 manager 정보도 로드
                joinedload(Contract.manager)
            ),
            # manager_id 관계로 연결된 contracts 로드
            selectinload(Users.contracts_manager_id)
        )
        .where(Users.id == user_id)
        .where(Users.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def find_contract_by_contract_id(*, session: AsyncSession, user_id: int, contract_id: int) -> Optional[Contract]:
    stmt = (
        select(Contract)
        .where(Contract.id == contract_id)
        .where(Contract.user_id == user_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def find_contract_send_mail_histories_by_user_id(
    *,
    session: AsyncSession,
    user_id: int
) -> list[ContractSendMailHistory]:
    stmt = (
        select(ContractSendMailHistory)
        .options(joinedload(ContractSendMailHistory.request_user))
        .options(joinedload(ContractSendMailHistory.contract))
        .where(ContractSendMailHistory.user_id == user_id)
        .order_by(ContractSendMailHistory.created_at.desc())  # 최신순 정렬
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())  # 모든 결과 반환


async def add_contracts(*, session: AsyncSession, contracts: list[dict]) -> list[int]:
    try:
        stmt = insert(Contract).values(contracts)
        await session.execute(stmt)

        last_id_result = await session.execute(text("SELECT LAST_INSERT_ID()"))
        first_id = last_id_result.scalar()

        created_ids = list(range(first_id, first_id + len(contracts)))

        await session.commit()
        return created_ids

    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to add contracts: {str(e)}")
        raise e

async def add_contract_send_mail_history(*, session: AsyncSession, contract_send_mail_history_dict: dict):
    try:
        stmt = insert(ContractSendMailHistory).values(contract_send_mail_history_dict)
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to add contract send mail history: {str(e)}")
        raise e

async def hard_delete_contract(*, session: AsyncSession, user_id: int, contract_id: int):
    try:
        stmt = (
            select(Contract)
            .where(Contract.user_id == user_id)
            .where(Contract.id == contract_id)
        )
        result = await session.execute(stmt)
        contract = result.scalar_one_or_none()
        if not contract:
            raise Exception("Contract not found")

        await session.delete(contract)
        await session.commit()
    except Exception as e:
        logger.error(f"Failed to hard delete contract: {e}")
        await session.rollback()
        raise e