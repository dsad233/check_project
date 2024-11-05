from fastapi import APIRouter, Depends, Request, Path
from typing import List, Optional
from app.core.database import get_db
from app.core.permissions.auth_utils import available_higher_than
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums.users import Role

from app.schemas.user_management.time_off_schemas import TimeOffCreateRequestDto, TimeOffUpdateRequestDto, TimeOffResponseDto, TimeOffReadAllResponseDto
from app.service.user_management import time_off_service
from app.common.dto.response_dto import ResponseDTO

router = APIRouter()

# 회원상세 - 휴직등록 부분 GET(READ)은 user_management.py의 get_user_detail에 포함되어 있음

@router.get("", response_model=ResponseDTO[List[TimeOffReadAllResponseDto]], status_code=200, summary='휴직 데이터 조회')
@available_higher_than(Role.MSO)
async def read_all_time_off(
    *,
    request: Request,
    branch_name: Optional[str] = None,
    part_name: Optional[str] = None,
    name: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
) -> ResponseDTO[List[TimeOffReadAllResponseDto]]:
    
    time_off_read_all = await time_off_service.time_off_read_all(
        session = session,
        branch_name = branch_name,
        part_name = part_name,
        name = name
    )

    if not time_off_read_all:
        message = '휴직 데이터가 존재하지 않습니다.'
    else: message = '휴직 데이터 조회가 완료되었습니다.'

    return ResponseDTO(
        status = 'SUCCESS',
        message = message,
        data = time_off_read_all
    )

@router.post("", response_model=ResponseDTO[TimeOffResponseDto], status_code=201, summary='휴직 등록')
@available_higher_than(Role.MSO)
async def create_time_off(
    *,
    time_off_create_request: TimeOffCreateRequestDto,
    request: Request,
    session: AsyncSession = Depends(get_db)
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

@router.patch("/{id}", response_model=ResponseDTO[TimeOffResponseDto], status_code=200, summary='휴직 데이터 업데이트')
@available_higher_than(Role.MSO)
async def update_time_off(
    *,
    id: int = Path(
        ...,
        description="업데이트할 휴직 데이터의 id",
        gt=0,
        examples=3
    ),
    time_off_update_request: TimeOffUpdateRequestDto,
    request: Request,
    session: AsyncSession = Depends(get_db)
) -> ResponseDTO[TimeOffResponseDto]:
    
    
    time_off_update = await time_off_service.time_off_update(
        session = session,
        id = id,
        time_off_update_request = time_off_update_request
    )
    time_off_update_response = TimeOffResponseDto.model_validate(time_off_update)

    return ResponseDTO(
        status = "SUCCESS",
        message = "휴직 데이터 업데이트가 완료되었습니다.",
        data = time_off_update_response
    )

@router.delete("/{id}", response_model=ResponseDTO, status_code=200, summary='휴직 데이터 삭제')
@available_higher_than(Role.MSO)
async def delete_time_off(
    *,
    id: int = Path(
        ...,
        description="삭제할 휴직 데이터 ID",
        gt=0,
        examples=3
    ),
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> ResponseDTO:
    
    await time_off_service.time_off_delete(
        session = session,
        id = id
    )

    return ResponseDTO(
        status = "SUCCESS",
        message = "휴직 데이터 삭제가 완료되었습니다."
    )