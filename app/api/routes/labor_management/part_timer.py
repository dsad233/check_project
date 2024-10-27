from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.labor_management.dto.part_timer_commute_history_correction_request_dto import PartTimerCommuteHistoryCorrectionRequestDTO
from app.cruds.labor_management.dto.part_timers_response_dto import PartTimerSummaryResponseDTO
from app.cruds.labor_management.dto.part_timer_work_history_response_dto import PartTimerWorkHistoryResponseDTO

from app.core.permissions.auth_utils import available_higher_than

from app.cruds.labor_management.repositories.mock_part_timer_repository import MockPartTimerRepository
from app.cruds.labor_management.repositories.part_timer_repository import PartTimerRepository
from app.cruds.labor_management.repositories.part_timer_repository_interface import IPartTimerRepository
from app.enums.users import Role
from app.middleware.tokenVerify import get_current_user, validate_token
from app.core.database import get_db
from app.models.users.users_model import Users

router = APIRouter(dependencies=[Depends(validate_token)])

# 리포지토리 의존성 함수 정의
def get_part_timer_repository(db: AsyncSession = Depends(get_db)) -> IPartTimerRepository:
    # TODO: 실제 DB 레포지토리 구현
    # return PartTimerRepository(db)
    return MockPartTimerRepository()

# TODO: 권한 체크 추가
@router.get("/part-timers", summary="파트타이머 월간 근로 관리 조회", description="MSO 최고 권한만 접근할 수 있는 전체 지점 및 파트에 대한 파트타이머 근로 관리 조회 API")
@available_higher_than(Role.ADMIN)
async def get_part_timers(
    request: Request, # available_higher_than에서 권한 확인을 위해 필요
    repo: IPartTimerRepository = Depends(get_part_timer_repository),
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month)) -> List[PartTimerSummaryResponseDTO]:

    return repo.get_all_part_timers(year, month)

@router.get("/part-timer/work-history", summary="파트타이머 근로 내역 조회", description="특정 파트타이머가 언제 출퇴근을 했는 지를 상세하게 볼 수 있는 API")
@available_higher_than(Role.ADMIN)
async def get_part_timer_work_history(
    request: Request,
    repo: IPartTimerRepository = Depends(get_part_timer_repository),
    user_id: int = Query(...),   
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month)) -> List[PartTimerWorkHistoryResponseDTO]:
    return repo.get_part_timer_work_history(user_id, year, month)

@router.patch("/part-timer/commute/{commute_id}", summary="파트타이머 출퇴근 시간 정정", description="파트타이머의 출퇴근 시간을 정정할 수 있는 API")
@available_higher_than(Role.ADMIN)
async def patch_part_timer_work_time(
    request: Request,
    repo: IPartTimerRepository = Depends(get_part_timer_repository),
    correction_data: PartTimerCommuteHistoryCorrectionRequestDTO = Body(...)):
    # TODO: 출퇴근 기록이 있는지 검증
    # ...
    # return repo.patch_part_timer_commute_history(correction_data)
    return "OK"
