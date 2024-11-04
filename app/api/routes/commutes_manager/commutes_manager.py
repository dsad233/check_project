from calendar import monthrange
from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from app.service.commutes_manager_service import CommutesManagerService
from app.api.routes.commutes_manager.dto.commutes_manager_response_dto import (
    CommutesManagerResponseDTO,
)

router = APIRouter()


@router.get("/commutes-manager", response_model=CommutesManagerResponseDTO)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_commutes_manager(
    request: Request,
    branch_id: Optional[int] = Query(None),
    part_id: Optional[int] = Query(None),
    user_name: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    commutes_manager_service: CommutesManagerService = Depends(CommutesManagerService),
):
    year = year or datetime.now().year
    month = month or datetime.now().month

    data, pagination = await commutes_manager_service.get_user_commutes(
        branch_id=branch_id,
        part_id=part_id,
        user_name=user_name,
        phone_number=phone_number,
        year=year,
        month=month,
        page=page,
        size=size,
    )

    last_day = monthrange(year, month)[1]

    return CommutesManagerResponseDTO.to_DTO(
        data=data, pagination=pagination, last_day=last_day
    )
