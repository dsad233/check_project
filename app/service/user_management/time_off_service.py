from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users.time_off_model import TimeOff
from app.schemas.user_management.time_off_schemas import TimeOffCreateRequestDto, TimeOffUpdateRequestDto
from app.cruds.users import time_off_crud
from fastapi import HTTPException
from app.exceptions.exceptions import NotFoundError
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
        id: int,
        time_off_update_request: TimeOffUpdateRequestDto
) -> TimeOff:
    try:

        # request를 딕셔너리화해서 id 컬럼 추가
        update_data = time_off_update_request.model_dump()
        update_data['id'] = id

        # TimeOff 인스턴스로 만들어 crud 호출
        time_off_update_result = await time_off_crud.time_off_update(
            session = session,
            time_off_update_request = TimeOff(**update_data)
        )

        if time_off_update_result is None:
            raise NotFoundError(
                detail = "업데이트할 휴직 데이터를 찾을 수 없습니다."
            )
        return time_off_update_result
    
    except Exception as error:
        if isinstance(error, NotFoundError):
            raise error

        logger.error(f"휴직 데이터 업데이트 중 오류 발생: {str(error)}")
        raise HTTPException(
            status_code=500,
            detail="휴직 데이터 업데이트 중 오류가 발생했습니다."
        )
    

async def time_off_delete(
        *,
        session: AsyncSession,
        id: int
) -> bool:
    try:
        time_off_delete_result = await time_off_crud.time_off_delete(
            session = session,
            id = id
        )

        if not time_off_delete_result:
            raise NotFoundError(
                detail = "삭제할 휴직 데이터를 찾을 수 없습니다."
            )
        return True

    except Exception as error:
        if isinstance(error, NotFoundError):
            raise error
        
        logger.error(f"휴직 데이터 삭제 중 오류 발생: {str(error)}")
        raise HTTPException(
            status_code = 500,
            detail = "휴직 데이터 삭제 중 오류가 발생했습니다."
        )