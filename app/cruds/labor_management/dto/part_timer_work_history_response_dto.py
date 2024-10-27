from pydantic import BaseModel
from datetime import datetime

class PartTimerWorkHistoryResponseDTO(BaseModel):
    commute_id: int
    part_name: str
    task: str
    work_start_time: datetime
    work_end_time: datetime
    work_start_set_time: datetime
    work_end_set_time: datetime
    working_hours: float
    rest_minites: int
    total_wage: float
    created_at: datetime