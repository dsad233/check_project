from typing import List
from pydantic import BaseModel

from app.api.routes.labor_management.dto.page_info_dto import PageInfoDto
from app.cruds.labor_management.dto.part_timers_response_dto import PartTimerSummaryResponseDTO


class PartTimersSummariesWithPageInfoDTO(BaseModel):
    part_timer_summaries: List[PartTimerSummaryResponseDTO]
    page_info: PageInfoDto

    @classmethod
    def toDTO(cls, summaries: List[PartTimerSummaryResponseDTO], total: int, page_num: int, page_size: int) -> 'PartTimersSummariesWithPageInfoDTO':
        return cls(part_timer_summaries=summaries, page_info=PageInfoDto.toDTO(total, page_num, page_size))
