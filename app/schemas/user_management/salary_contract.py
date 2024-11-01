from typing import Optional
from datetime import date

from pydantic import BaseModel

from app.models.users.users_salary_contract_model import SalaryContract
from app.utils.datetime_utils import DatetimeUtil


class RequestCreateSalaryContractDto(BaseModel):
    user_id: int

    contract_start_date: str
    contract_end_date: str
    annual_salary: int
    monthly_salary: int
    base_salary: int
    base_hour_per_week: int
    base_hour_per_day: int
    fixed_overtime_allowance: int
    fixed_overtime_hours: int
    annual_leave_allowance: Optional[int]
    annual_leave_hour_per_day: int
    annual_leave_count: int
    holiday_allowance: int
    holiday_allowance_hours: int
    duty_allowance: Optional[int]
    night_allowance: Optional[int]
    meal_allowance: Optional[int]
    vehicle_maintenance_allowance: Optional[int]

    @classmethod
    def to_domain(cls) -> SalaryContract:
        return SalaryContract(
            user_id=cls.user_id,
            contract_start_date=DatetimeUtil.str_to_date(cls.contract_start_date),
            contract_end_date=DatetimeUtil.str_to_date(cls.contract_end_date),
            annual_salary=cls.annual_salary,
            monthly_salary=cls.monthly_salary,
            base_salary=cls.base_salary,
            base_hour_per_week=cls.base_hour_per_week,
            base_hour_per_day=cls.base_hour_per_day,
            fixed_overtime_allowance=cls.fixed_overtime_allowance,
            fixed_overtime_hours=cls.fixed_overtime_hours,
            annual_leave_allowance=cls.annual_leave_allowance,
            annual_leave_hour_per_day=cls.annual_leave_hour_per_day,
            annual_leave_count=cls.annual_leave_count,
            holiday_allowance=cls.holiday_allowance,
            holiday_allowance_hours=cls.holiday_allowance_hours,
            duty_allowance=cls.duty_allowance,
            night_allowance=cls.night_allowance,
            meal_allowance=cls.meal_allowance,
            vehicle_maintenance_allowance=cls.vehicle_maintenance_allowance
        )

class RequestUpdateSalaryContractDto(BaseModel):
    user_id: int

    contract_start_date: Optional[str]
    contract_end_date: Optional[str]
    annual_salary: Optional[int]
    monthly_salary: Optional[int]
    base_salary: Optional[int]
    base_hour_per_week: Optional[int]
    base_hour_per_day: Optional[int]
    fixed_overtime_allowance: Optional[int]
    fixed_overtime_hours: Optional[int]
    annual_leave_allowance: Optional[int]
    annual_leave_hour_per_day: Optional[int]
    annual_leave_count: Optional[int]
    holiday_allowance: Optional[int]
    holiday_allowance_hours: Optional[int]
    duty_allowance: Optional[int]
    night_allowance: Optional[int]
    meal_allowance: Optional[int]
    vehicle_maintenance_allowance: Optional[int]


class SalaryContractDto(BaseModel):
    contract_start_date: str
    contract_end_date: str
    annual_salary: int
    monthly_salary: int
    base_salary: int
    base_hour_per_week: int
    base_hour_per_day: int
    fixed_overtime_allowance: int
    fixed_overtime_hours: int
    annual_leave_allowance: int
    annual_leave_hour_per_day: int
    annual_leave_count: int
    holiday_allowance: Optional[int]
    holiday_allowance_hours: int
    duty_allowance: Optional[int]
    night_allowance: Optional[int]
    meal_allowance: Optional[int]
    vehicle_maintenance_allowance: Optional[int]

    @classmethod
    def build(cls, salary_contract: SalaryContract):
        return cls(
            contract_start_date=DatetimeUtil.date_to_str(salary_contract.contract_start_date),
            contract_end_date=DatetimeUtil.date_to_str(salary_contract.contract_end_date),
            annual_salary=salary_contract.annual_salary,
            monthly_salary=salary_contract.monthly_salary,
            base_salary=salary_contract.base_salary,
            base_hour_per_week=salary_contract.base_hour_per_week,
            base_hour_per_day=salary_contract.base_hour_per_day,
            fixed_overtime_allowance=salary_contract.fixed_overtime_allowance,
            fixed_overtime_hours=salary_contract.fixed_overtime_hours,
            annual_leave_allowance=salary_contract.annual_leave_allowance,
            annual_leave_hour_per_day=salary_contract.annual_leave_hour_per_day,
            annual_leave_count=salary_contract.annual_leave_count,
            holiday_allowance=salary_contract.holiday_allowance,
            holiday_allowance_hours=salary_contract.holiday_allowance_hours,
            duty_allowance=salary_contract.duty_allowance,
            night_allowance=salary_contract.night_allowance,
            meal_allowance=salary_contract.meal_allowance,
            vehicle_maintenance_allowance=salary_contract.vehicle_maintenance_allowance
        )
