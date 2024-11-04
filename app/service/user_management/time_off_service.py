from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users.time_off_model import TimeOff
from app.schemas.user_management.time_off_schemas import TimeOffCreateRequestDto
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

        # 이미 휴직 등록이 되어있는지 확인
        # 이미 되어 있다면 예외 처리 로직 필요


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