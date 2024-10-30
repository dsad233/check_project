# 출퇴근 시간 정정 요청 모델 정의
from datetime import time
from pydantic import BaseModel

from app.models.users.part_timer.users_part_timer_work_contract_model import WorkTypeEnum

class PartTimerCommuteHistoryCorrectionRequestDTO(BaseModel):
    work_type: WorkTypeEnum
    work_start_set_time: time
    work_end_set_time: time
    rest_minutes: int