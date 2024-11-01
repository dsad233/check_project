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


class EntireClosedDayResponseDTO(BaseModel):
    user_closed_days: dict[str, List[UserClosedDayDetail]]
    hospital_closed_days: List[str]

    @classmethod
    def to_DTO(cls, user_closed_days: dict[str, List[UserClosedDayDetail]], hospital_closed_days: List[str]):
        return cls(user_closed_days=user_closed_days, hospital_closed_days=hospital_closed_days)
