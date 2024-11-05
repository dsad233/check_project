from fastapi import APIRouter, Depends, Request
from app.core.database import get_db
from app.core.permissions.auth_utils import available_higher_than
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums.users import Role

from app.schemas.user_management.time_off_schemas import TimeOffCreateRequestDto, TimeOffUpdateRequestDto, TimeOffResponseDto
from app.models.users.time_off_model import TimeOff
from app.service.user_management import time_off_service
from app.common.dto.response_dto import ResponseDTO

router = APIRouter()

@router.post("", response_model=ResponseDTO[TimeOffResponseDto], status_code=201, summary='휴직 등록')
@available_higher_than(Role.MSO)
async def create_time_off(
    *,
    request: Request,
    session: AsyncSession = Depends(get_db),
    time_off_create_request: TimeOffCreateRequestDto
) -> ResponseDTO[TimeOffResponseDto]:
    
    time_off_create = await time_off_service.time_off_create(
        session = session,
        time_off_create_request = time_off_create_request
    )
    time_off_create_response = TimeOffResponseDto.model_validate(time_off_create)

    return ResponseDTO(
        status = "SUCCESS",
        message = "휴직 등록이 완료되었습니다.",
        data = time_off_create_response
    )

@router.patch("", response_model=ResponseDTO[TimeOffResponseDto], status_code=200, summary='휴직 데이터 업데이트')
@available_higher_than(Role.MSO)
async def update_time_off(
    *,
    request: Request,
    session: AsyncSession = Depends(get_db),
    time_off_update_request: TimeOffUpdateRequestDto
) -> ResponseDTO[TimeOffResponseDto]:
    
    time_off_update = await time_off_service.time_off_update(
        session = session,
        time_off_update_request = time_off_update_request
    )
    time_off_update_response = TimeOffResponseDto.model_validate(time_off_update)

    return ResponseDTO(
        status = "SUCCESS",
        message = "휴직 업데이트가 완료되었습니다.",
        data = time_off_update_response
    )