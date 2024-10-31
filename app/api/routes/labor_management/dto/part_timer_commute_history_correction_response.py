from datetime import time
from pydantic import BaseModel

from app.api.routes.labor_management.dto.part_timer_commute_history_correction_request import PartTimerCommuteHistoryCorrectionRequestDTO
from app.models.users.part_timer.users_part_timer_work_contract_model import WorkTypeEnum

class PartTimerCommuteHistoryCorrectionResponseDTO(BaseModel):
    commute_id: int
    work_type: WorkTypeEnum
    work_start_set_time: time 
    work_end_set_time: time 
    work_hours: float
    rest_minutes: int
    total_wage: int | None # 프론트에서 전체 목록 조회로 임금 계산은 보류

    class Builder:
        def __init__(self, commute_id: int, requestDTO: PartTimerCommuteHistoryCorrectionRequestDTO):
            self._commute_id = commute_id
            self._work_type = requestDTO.work_type
            self._work_start_set_time = requestDTO.work_start_set_time
            self._work_end_set_time = requestDTO.work_end_set_time
            self._work_hours = None
            self._rest_minutes = requestDTO.rest_minutes
            self._total_wage = None

        def set_work_type(self, work_type: WorkTypeEnum) -> 'PartTimerCommuteHistoryCorrectionResponseDTO.Builder':
            self._work_type = work_type
            return self

        def set_work_time(self, work_start_set_time: time, work_end_set_time: time) -> 'PartTimerCommuteHistoryCorrectionResponseDTO.Builder':
            self._work_start_set_time = work_start_set_time
            self._work_end_set_time = work_end_set_time
            self._work_hours = work_end_set_time.hour + work_end_set_time.minute / 60 - work_start_set_time.hour - work_start_set_time.minute / 60
            return self

        def set_rest_minutes(self, rest_minutes: int) -> 'PartTimerCommuteHistoryCorrectionResponseDTO.Builder':
            self._rest_minutes = rest_minutes
            return self

        def set_total_wage(self, total_wage: int) -> 'PartTimerCommuteHistoryCorrectionResponseDTO.Builder':
            self._total_wage = total_wage
            return self

        def build(self) -> 'PartTimerCommuteHistoryCorrectionResponseDTO':
            return PartTimerCommuteHistoryCorrectionResponseDTO(
                commute_id=self._commute_id,
                work_type=self._work_type,
                work_start_set_time=self._work_start_set_time,
                work_end_set_time=self._work_end_set_time,
                work_hours=self._work_hours,
                rest_minutes=self._rest_minutes,
                total_wage=self._total_wage
            )

    @classmethod
    def builder(cls) -> 'Builder':
        return cls.Builder()