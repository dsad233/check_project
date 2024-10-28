from typing import List
from pydantic import BaseModel
from datetime import datetime

class PartTimerWorkHistoryDTO(BaseModel):
    commute_id: int
    part_name: str
    task: str
    work_start_time: datetime
    work_end_time: datetime
    work_start_set_time: datetime
    work_end_set_time: datetime
    working_hours: float
    rest_minutes: int
    total_wage: float
    created_at: datetime

class PartTimerWorkHistorySummaryDTO(BaseModel):
    total_work_days: int
    total_work_hours: float
    total_hospital_work_hours: float
    total_holiday_work_hours: float
    total_wage: float

class PartTimerWorkHistoryResponseDTO(BaseModel):
    part_timer_work_histories: List[PartTimerWorkHistoryDTO] | None
    summary: PartTimerWorkHistorySummaryDTO | None

    @classmethod
    def get_part_timer_work_history_response(cls, part_timer_work_histories: List[PartTimerWorkHistoryDTO], summary: PartTimerWorkHistorySummaryDTO) -> "PartTimerWorkHistoryResponseDTO":
        return cls(part_timer_work_histories=part_timer_work_histories, summary=summary)

