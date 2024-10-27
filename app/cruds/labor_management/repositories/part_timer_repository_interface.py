from typing import List
from app.cruds.labor_management.dto.part_timer_work_history_response_dto import PartTimerWorkHistoryResponseDTO
from app.cruds.labor_management.dto.part_timers_response_dto import PartTimerSummaryResponseDTO

class IPartTimerRepository:
    async def get_all_part_timers(self, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        raise NotImplementedError

    async def get_part_timer_work_history(self, user_id: int, year: int, month: int) -> List[PartTimerWorkHistoryResponseDTO]:
        raise NotImplementedError
    
    async def get_all_part_timers_by_branch_id(self, branch_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        raise NotImplementedError
    
    async def get_all_part_timers_by_part_id(self, part_id: int, year: int, month: int) -> List[PartTimerSummaryResponseDTO]:
        raise NotImplementedError
