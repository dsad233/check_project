from datetime import datetime, time
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class AttendanceStatus(str, Enum):
    CLOSED = "휴점"
    FIXED_CLOSED = "정기 휴점"
    OFF = "휴무"
    FIXED_OFF = "정기 휴무"
    WORK = "출근"
    NONE = "없음"
    TIME_OFF_START = "휴직 시작"
    TIME_OFF_END = "휴직 끝"
    RESIGNATION = "퇴사"
    NOT_HIRE = "미입사"

class Weekday(int, Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

class CommuteRecord(BaseModel):
    clock_in: Optional[time] = Field(None, description="출근 시간")
    clock_out: Optional[time] = Field(None, description="퇴근 시간")
    status: Optional[str] = Field(default=AttendanceStatus.NONE, description="출근 상태")

    model_config = {
        "use_enum_values": True
    }


class UserCommuteDetail(BaseModel):
    user_id: int
    user_name: str
    gender: str
    branch_id: int
    branch_name: str
    weekly_work_days: int
    part_id: int
    part_name: str
    commute_records: Dict[str, CommuteRecord]

class CommutesManagerResponseDTO(BaseModel):
    message: str = "Success"
    data: List[UserCommuteDetail]
    pagination: dict
    last_day: int

    @classmethod
    def to_DTO(cls, data: List[dict], pagination: dict, last_day: int):
        return cls(
            data=data,
            pagination=pagination,
            last_day=last_day
        )