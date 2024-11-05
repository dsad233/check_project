from typing import List

from pydantic import BaseModel


from typing import List
from pydantic import BaseModel, Field

class EarlyClockInResponseDTO(BaseModel):
    user_id: int
    user_name: str
    part_name: str
    category: str = "조기 출근"

# 조기 출근 날짜와 직원 정보 조회
class EarlyClockInListResponseDTO(BaseModel):
    early_clock_in_days: dict[str, EarlyClockInResponseDTO]

    @classmethod
    def to_DTO(cls, early_clock_in_days: dict[str, EarlyClockInResponseDTO]):
        return cls(early_clock_in_days=early_clock_in_days)

# 조기 출근 날짜만 조회
class SimpleEarlyClockInListResponseDTO(BaseModel):
    early_clock_in_days: List[str]

    @classmethod
    def to_DTO(cls, early_clock_in_days: List[str]):
        return cls(early_clock_in_days=early_clock_in_days)
    
class HospitalClosedDaysResponseDTO(BaseModel):
    hospital_closed_days: List[str] = Field(description="병원 휴무일 목록")

    @classmethod
    def to_DTO(cls, hospital_closed_days: List[str]):
        return cls(hospital_closed_days=hospital_closed_days)

class UserClosedDaySummaryDTO(BaseModel):
    closed_date: str = Field(description="휴무일 날짜")
    category: str = Field(description="휴무 종류 (정규휴무, 연차 등)")

    @classmethod
    def to_DTO(cls, closed_date: str, category: str):
        return cls(closed_date=closed_date, category=category)
    
    def __eq__(self, other):
        if not isinstance(other, UserClosedDaySummaryDTO):
            return False
        return self.closed_date == other.closed_date and self.category == other.category

    def __hash__(self):
        return hash((self.closed_date, self.category))

class UserClosedDayDetailDTO(BaseModel):
    user_id: int = Field(description="직원 ID")
    user_name: str = Field(description="직원 이름")
    part_name: str = Field(description="소속 파트명")
    user_closed_days: set[UserClosedDaySummaryDTO] = Field(description="직원의 휴무일 정보 목록")

    @classmethod
    def to_DTO(cls, user_id: int, user_name: str, part_name: str, user_closed_days: set[UserClosedDaySummaryDTO]):
        return cls(user_id=user_id, user_name=user_name, part_name=part_name, user_closed_days=user_closed_days)

class UserClosedDayDetail(BaseModel):
    user_id: int = Field(description="직원 ID")
    user_name: str = Field(description="직원 이름")
    part_name: str = Field(description="소속 파트명")
    category: str = Field(description="휴무 종류 (정규휴무, 연차 등)")

    def __eq__(self, other):
        if not isinstance(other, UserClosedDayDetail):
            return False
        return self.user_id == other.user_id

    def __hash__(self):
        return hash(self.user_id)

class EntireClosedDayResponseDTO(BaseModel):
    user_closed_days: dict[str, set[UserClosedDayDetail]] = Field(description="날짜별 직원 휴무 정보")
    hospital_closed_days: List[str] = Field(description="병원 휴무일 목록")
    early_clock_in_days: dict[str, EarlyClockInResponseDTO] = Field(description="조기 출근 날짜와 직원 정보")

    @classmethod
    def to_DTO(cls, user_closed_days: dict[str, List[UserClosedDayDetail]], hospital_closed_days: List[str], early_clock_in_days: dict[str, EarlyClockInResponseDTO]):
        return cls(user_closed_days=user_closed_days, hospital_closed_days=hospital_closed_days, early_clock_in_days=early_clock_in_days)
    