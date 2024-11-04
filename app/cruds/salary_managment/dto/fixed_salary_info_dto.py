from datetime import date
from typing import Any

from pydantic import BaseModel
from sqlalchemy import Row

class FixedSalaryInfoDTO(BaseModel):
    """직원 고정 급여 정보 DTO"""
    user_id: int
    part_name: str
    hire_date: date
    resignation_date: date | None
    monthly_salary: int
    annual_leave_allowance: int
    annual_leave_count: int
    annual_leave_hour_per_day: int
    remaining_annual_leave: float
    duty_allowance: int
    meal_allowance: int
    vehicle_maintenance_allowance: int
    weekly_rest_hours: int

    @classmethod
    def to_DTO(cls, row: Row[Any]):
        return cls(**dict(zip(cls.__annotations__.keys(), row)))
