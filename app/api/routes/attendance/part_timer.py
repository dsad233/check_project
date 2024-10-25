from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.routes.attendance.dto.part_timers_response_dto import PartTimerListResponseDTO
from app.cruds.attendance.part_timer_manager.part_timer_crud import get_part_timer_summaries, get_part_timer_work_hours_and_total_wage

from app.middleware.tokenVerify import get_current_user, validate_token
from app.core.database import get_db
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])

@router.get("/part-timers", summary="파트타이머 월간 근로 관리 조회", description="MSO 최고 권한만 접근할 수 있는 전체 지점 및 파트에 대한 파트타이머 근로 관리 조회 API")
async def get_part_timers(
    user: Annotated[Users, Depends(get_current_user)], 
    session: AsyncSession = Depends(get_db),
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month)) -> List[PartTimerListResponseDTO]:
    if user.role.strip() != "MSO 최고권한":
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
    
    part_timer_summary = await get_part_timer_summaries(session, year, month)
    part_timer_work_hour_and_total_wage = await get_part_timer_work_hours_and_total_wage(session, year, month)

    return PartTimerListResponseDTO.get_part_timer_list_response(part_timer_summary, part_timer_work_hour_and_total_wage)

