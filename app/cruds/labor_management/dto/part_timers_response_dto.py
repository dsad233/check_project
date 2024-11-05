from datetime import time
from pydantic import BaseModel

class PartTimerSummaryResponseDTO(BaseModel):
    user_id: int
    gender: str
    branch_name: str
    user_name: str
    part_name: str
    work_days: int
    hospital_work_hours: float
    holiday_work_hours: float
    total_work_hours: float
    total_wage: float
    phone_number: str
    branch_id: int
    part_id: int
    calculate_start_time: time | None
    calculate_end_time: time | None