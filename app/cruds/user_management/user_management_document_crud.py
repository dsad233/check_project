import logging
from typing import Optional
from sqlalchemy import func, select, update, text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.users.users_document_model import Document
from app.models.users.users_model import Users

logger = logging.getLogger(__name__)


async def find_by_id_with_documents(*, session: AsyncSession, user_id: int) -> Optional[Users]:
    stmt = (
        select(Users)
        .options(selectinload(Users.documents))
        .where(Users.id == user_id)
        .where(Users.deleted_yn == "N")
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_documents(*, session: AsyncSession, documents: list[dict]) -> list[int]:
    try:
        stmt = insert(Document).values(documents)
        await session.execute(stmt)

        last_id_result = await session.execute(text("SELECT LAST_INSERT_ID()"))
        first_id = last_id_result.scalar()

        created_ids = list(range(first_id, first_id + len(documents)))

        await session.commit()
        return created_ids

    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to add documents: {str(e)}")
        raise e

async def delete_document(*, session: AsyncSession, user_id: int, document_id: int):
    try:
        stmt = (
            update(Document)
            .where(Document.user_id == user_id)
            .where(Document.id == document_id)
            .values(deleted_yn="Y")
        )
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        await session.rollback()
        raise e

async def hard_delete_document(*, session: AsyncSession, user_id: int, document_id: int):
    try:
        stmt = (
            select(Document)
            .where(Document.user_id == user_id)
            .where(Document.id == document_id)
        )
        result = await session.execute(stmt)
        document = result.scalar_one_or_none()
        if not document:
            raise Exception("Document not found")

        await session.delete(document)
        await session.commit()
    except Exception as e:
        logger.error(f"Failed to hard delete document: {e}")
        await session.rollback()
        raise e