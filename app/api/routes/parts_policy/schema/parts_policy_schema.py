from pydantic import BaseModel
from typing import Optional


class PartWorkPolicyCreate(BaseModel):
    work_policy_id: int
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    lunch_start_time: Optional[str] = None
    lunch_end_time: Optional[str] = None
    break_time_1: Optional[str] = None
    break_time_2: Optional[str] = None

class PartWorkPolicyResponse(BaseModel):
    id: int
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    lunch_start_time: Optional[str] = None
    lunch_end_time: Optional[str] = None
    break_time_1: Optional[str] = None
    break_time_2: Optional[str] = None

class PartSalaryPolicyResponse(BaseModel):
    id: int
    base_salary: Optional[int] = None
    annual_leave_days: Optional[int] = None
    sick_leave_days: Optional[int] = None
    overtime_rate: Optional[float] = None
    night_work_allowance: Optional[int] = None
    holiday_work_allowance: Optional[int] = None
    
class PartSalaryPolicyCreate(BaseModel):
    base_salary: Optional[int] = None
    annual_leave_days: Optional[int] = None
    sick_leave_days: Optional[int] = None
    overtime_rate: Optional[float] = None
    night_work_allowance: Optional[int] = None
    holiday_work_allowance: Optional[int] = None
