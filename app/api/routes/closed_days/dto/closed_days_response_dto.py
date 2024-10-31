from datetime import datetime
from typing import List

from pydantic import BaseModel


class HospitalClosedDaysResponseDTO(BaseModel):
    hospital_closed_days: List[str]

    @classmethod
    def to_DTO(cls, hospital_closed_days: List[str]):
        return cls(hospital_closed_days=hospital_closed_days)

class UserClosedDaySummaryDTO(BaseModel):
    closed_date: str
    category: str

    @classmethod
    def to_DTO(cls, closed_date: str, category: str):
        return cls(closed_date=closed_date, category=category)

class UserClosedDayDetailDTO(BaseModel):
    user_id: int
    user_name: str
    part_name: str
    user_closed_days: List[UserClosedDaySummaryDTO]

    @classmethod
    def to_DTO(cls, user_id: int, user_name: str, part_name: str, user_closed_days: List[UserClosedDaySummaryDTO]):
        return cls(user_id=user_id, user_name=user_name, part_name=part_name, user_closed_days=user_closed_days)

class UserClosedDayDetail(BaseModel):
    user_id: int
    user_name: str
    part_name: str
    category: str

class UserClosedDaysResponseDTO(BaseModel):
    user_closed_days: dict[str, List[UserClosedDayDetail]]

    @classmethod
    def to_DTO(cls, user_closed_days: dict[str, List[UserClosedDayDetail]]):
        return cls(user_closed_days=user_closed_days)

# Example usage
# user_closed_days = {
#     '2024-01-01': [
#         UserClosedDayDetail(user_id=1, user_name="박다인", part_name="코디", category="정규휴무"),
#         UserClosedDayDetail(user_id=2, user_name="성동제", part_name="양진아", category="연차")
#     ],
#     '2024-01-02': [
#         UserClosedDayDetail(user_id=3, user_name="장석찬", part_name="코디", category="연차 종일"),
#         UserClosedDayDetail(user_id=4, user_name="이다희", part_name="간호", category="연차 종일")
#     ],
#     '2024-01-03': [
#         UserClosedDayDetail(user_id=5, user_name="고혜솔", part_name="간호", category="조퇴")
#     ]
# }

# dto = UserClosedDaysResponseDTO.to_DTO(user_closed_days)

class EntireClosedDayResponseDTO(BaseModel):
    user_closed_days: UserClosedDaysResponseDTO
    hospital_closed_days: HospitalClosedDaysResponseDTO

    @classmethod
    def to_DTO(cls, user_closed_days: List[UserClosedDayDetailDTO], hospital_closed_days: List[str]):
        return cls(user_closed_days=user_closed_days, hospital_closed_days=hospital_closed_days)
