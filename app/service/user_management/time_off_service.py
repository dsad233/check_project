from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users.time_off_model import TimeOff
from app.schemas.user_management.time_off_schemas import TimeOffCreateRequestDto, TimeOffUpdateRequestDto
from app.cruds.users import time_off_crud
from fastapi import HTTPException
import logging


logger = logging.getLogger(__name__)

async def time_off_create(
        *,
        session: AsyncSession,
        time_off_create_request: TimeOffCreateRequestDto
) -> TimeOff:
    try:
        time_off_create_result = await time_off_crud.time_off_create(
            session = session,
            time_off_create_request = TimeOff(**time_off_create_request.model_dump())
        )
        return time_off_create_result
    
    except Exception as error:
        logger.error(f"휴직 등록 중 오류 발생: {str(error)}")

        raise HTTPException(
            status_code=500,
            detail="휴직 등록 중 오류가 발생했습니다."
        )

async def time_off_update(
        *,
        session: AsyncSession,
        time_off_update_request: TimeOffUpdateRequestDto
) -> TimeOff:
    try:
        time_off_update_result = await time_off_crud.time_off_update(
            session = session,
            time_off_update_request = TimeOff(**time_off_update_request.model_dump())
        )

        if time_off_update_result is None:
            raise HTTPException(
                status_code = 404,
                detail = "업데이트할 휴직 데이터를 찾을 수 없습니다."
            )

        return time_off_update_result
    
    except Exception as error:
        if isinstance(error, HTTPException):
            raise error

        logger.error(f"휴직 업데이트 중 오류 발생: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail="휴직 업데이트 중 오류가 발생했습니다."
        )
    