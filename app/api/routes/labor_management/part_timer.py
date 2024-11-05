from datetime import datetime
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.labor_management.dto.part_timer_commute_history_correction_request import PartTimerCommuteHistoryCorrectionRequestDTO
from app.api.routes.labor_management.dto.part_timer_commute_history_correction_response import PartTimerCommuteHistoryCorrectionResponseDTO
from app.api.routes.labor_management.dto.part_timers_summaries_with_page import PartTimersSummariesDTO, PartTimersSummariesWithPageInfoDTO
from app.cruds.labor_management.dto.part_timer_work_history_response_dto import PartTimerWorkHistoryResponseDTO

from app.core.permissions.auth_utils import available_higher_than

from app.cruds.labor_management.repositories.part_timer_repository import PartTimerRepository
from app.cruds.labor_management.repositories.part_timer_repository_interface import IPartTimerRepository
from app.enums.users import Role
from app.exceptions.exceptions import BadRequestError, NotFoundError
from app.core.database import get_db

router = APIRouter()

# 리포지토리 의존성 함수 정의
def get_part_timer_repository(db: AsyncSession = Depends(get_db)) -> IPartTimerRepository:
    return PartTimerRepository(db)
    # return MockPartTimerRepository.get_instance()

@router.get("/part-timers", summary="파트타이머 월간 근로 관리 조회", description="지점 및 파트별 대한 파트타이머 근로 관리 조회 API")
@available_higher_than(Role.ADMIN)
async def get_part_timers(
    request: Request, # available_higher_than에서 권한 확인을 위해 필요
    repo: IPartTimerRepository = Depends(get_part_timer_repository),
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month),
    branch_id: int = Query(None),
    part_id: int = Query(None),
    page_num: int = Query(1),
    page_size: int = Query(10)
    ) -> PartTimersSummariesWithPageInfoDTO:

    if branch_id and part_id:
        summaries = await repo.get_all_part_timers_by_branch_id_and_part_id(branch_id, part_id, year, month, page_num, page_size)
        total = await repo.get_total_count_part_timers_by_branch_id_and_part_id(branch_id, part_id, year, month) or 0
        return PartTimersSummariesWithPageInfoDTO.toDTO(summaries, total, page_num, page_size)
    elif branch_id:
        summaries = await repo.get_all_part_timers_by_branch_id(branch_id, year, month, page_num, page_size)
        total = await repo.get_total_count_part_timers_by_branch_id(branch_id, year, month) or 0
        return PartTimersSummariesWithPageInfoDTO.toDTO(summaries, total, page_num, page_size)
    else:
        if request.state.user.role != Role.MSO:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
        summaries = await repo.get_all_part_timers(year, month, page_num, page_size)
        total = await repo.get_total_count_part_timers(year, month) or 0
        return PartTimersSummariesWithPageInfoDTO.toDTO(summaries, total, page_num, page_size)

@router.get("/part-timer", summary="이름과 전화번호로 특정 or 다수 파트타이머 검색", description="특정 지점과 파트에 대한 이름과 전화번호로 특정 직원을 검색할 수 있는 API")
@available_higher_than(Role.ADMIN)
async def get_part_timer_by_user_info(
    request: Request,
    repo: IPartTimerRepository = Depends(get_part_timer_repository),
    branch_id: int = Query(...),
    part_id: int = Query(...),
    user_name: str = Query(None),
    phone_number: str = Query(None, pattern="^[0-9\\-]+$"),
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month)) -> PartTimersSummariesDTO:

    if not user_name and not phone_number:
        raise BadRequestError("사용자 이름 또는 전화번호를 입력해주세요.")
    return PartTimersSummariesDTO.toDTO(await repo.get_part_timer_by_user_info(year, month, user_name, phone_number, branch_id, part_id))

@router.get("/part-timer/work-history", summary="파트타이머 근로 내역 조회", description="특정 파트타이머가 언제 출퇴근을 했는 지를 상세하게 볼 수 있는 API")
@available_higher_than(Role.ADMIN)
async def get_part_timer_work_history(
    request: Request,
    repo: IPartTimerRepository = Depends(get_part_timer_repository),
    user_id: int = Query(...),   
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month)) -> PartTimerWorkHistoryResponseDTO:

    part_timer_work_histories = await repo.get_part_timer_work_histories(user_id, year, month)
    # DB 값과 동일하게 값을 위해 part_timer_work_histories를 계산하지 않고 DB에서 조회
    summary = await repo.get_part_timer_work_history_summary_by_user_id(user_id, year, month) 

    return PartTimerWorkHistoryResponseDTO.get_part_timer_work_history_response(part_timer_work_histories, summary)

@router.patch("/part-timer/work-history/{commute_id}", summary="파트타이머 근무 내역 정정", description="파트타이머의 근무 내역을 정정할 수 있는 API, 변경된 내용만 응답으로 반환")
@available_higher_than(Role.ADMIN)
async def patch_part_timer_work_time(
    request: Request,
    repo: IPartTimerRepository = Depends(get_part_timer_repository),
    commute_id: int = Path(...),
    correction_data: PartTimerCommuteHistoryCorrectionRequestDTO = Body(...)) -> PartTimerCommuteHistoryCorrectionResponseDTO:

    if not await repo.exist_part_timer_work_history(commute_id):
        raise NotFoundError("출퇴근 기록이 없습니다.")
    return await repo.update_part_timer_work_history(commute_id, correction_data)
