from datetime import datetime
from typing import List

from app.api.routes.labor_management.dto.part_timer_commute_history_correction_request import PartTimerCommuteHistoryCorrectionRequestDTO
from app.api.routes.labor_management.dto.part_timer_commute_history_correction_response import PartTimerCommuteHistoryCorrectionResponseDTO
from app.cruds.labor_management.dto.part_timer_work_history_response_dto import PartTimerWorkHistoryDTO, PartTimerWorkHistorySummaryDTO
from app.cruds.labor_management.dto.part_timers_response_dto import PartTimerSummaryResponseDTO

class IPartTimerRepository:
    async def get_all_part_timers(self, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        raise NotImplementedError

    async def get_part_timer_work_histories(self, user_id: int, year: int, month: int) -> List[PartTimerWorkHistoryDTO]:
        raise NotImplementedError
    
    async def get_all_part_timers_by_branch_id(self, branch_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        raise NotImplementedError
    
    async def get_all_part_timers_by_branch_id_and_part_id(self, branch_id: int, part_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        raise NotImplementedError
    
    async def get_part_timer_work_history_summary_by_user_id(self, user_id: int, year: int, month: int) -> PartTimerWorkHistorySummaryDTO:
        raise NotImplementedError
    
    async def get_part_timer_by_user_info(self, year: int, month: int, user_name: str, phone_number: str, branch_id: int, part_id: int) -> PartTimerSummaryResponseDTO:
        raise NotImplementedError

    async def update_part_timer_work_history(self, commute_id: int, correction_data: PartTimerCommuteHistoryCorrectionRequestDTO) -> PartTimerCommuteHistoryCorrectionResponseDTO:
        raise NotImplementedError
    
    async def exist_part_timer_work_history(self, commute_id: int) -> bool:
        raise NotImplementedError
