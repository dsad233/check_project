from datetime import datetime
from pydantic import BaseModel

class PartTimerCommuteHistoryCorrectionResponseDTO(BaseModel):
    commute_id: int | None = None # 출퇴근 기록 식별자
    part_id: int | None = None
    task: str | None = None
    work_start_time: datetime | None = None
    work_end_time: datetime | None = None
    working_hours: float | None = None
    rest_minutes: int | None = None