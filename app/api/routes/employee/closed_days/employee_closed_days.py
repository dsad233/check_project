from fastapi import APIRouter, Depends, Request
from datetime import datetime
from app.api.routes.closed_days.dto.closed_days_response_dto import EntireClosedDayResponseDTO
from app.service.closed_day_service import ClosedDayService

router = APIRouter()


@router.get("/closed-days", response_model=EntireClosedDayResponseDTO, summary="내 소속 지점의 휴무일 조회")
async def get_my_branch_closed_days(
        *,
        context: Request,
        service: ClosedDayService = Depends(ClosedDayService),
        year: int = datetime.now().year,
        month: int = datetime.now().month
) -> EntireClosedDayResponseDTO:
    """
    현재 로그인한 사용자의 소속 지점의 휴무일을 조회합니다.
    - 기본값으로 현재 년/월의 데이터를 조회
    """
    branch_id = context.state.user.branch_id
    user_closed_days = await service.get_all_user_closed_days_group_by_date(branch_id, year, month)
    hospital_closed_days = await service.get_all_hospital_closed_days(branch_id, year, month)
    early_clock_in_days = await service.get_all_user_early_clock_ins_group_by_date(branch_id, year, month)

    return EntireClosedDayResponseDTO.to_DTO(user_closed_days, hospital_closed_days, early_clock_in_days)
