# 출퇴근 시간 정정 요청 모델 정의
from datetime import datetime
from pydantic import BaseModel

# TODO: 데이터 정합성 검사 추가
class PartTimerCommuteHistoryCorrectionRequestDTO(BaseModel):
    part_id: int | None = None
    work_start_time: datetime | None = None
    work_end_time: datetime | None = None
    rest_minutes: int | None = None