from typing import Optional
from datetime import date

from pydantic import BaseModel, Field

from app.models.users.users_salary_contract_model import SalaryContract
from app.utils.datetime_utils import DatetimeUtil


class RequestCreateSalaryContract(BaseModel):
    contract_start_date: str
    contract_end_date: Optional[str]
    annual_salary: int
    monthly_salary: int
    base_salary: int
    base_hour_per_week: int
    base_hour_per_day: int
    weekly_rest_hours: int
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

    def to_domain(self) -> SalaryContract:
        return SalaryContract(
            contract_start_date=DatetimeUtil.str_to_date(self.contract_start_date),
            contract_end_date=DatetimeUtil.str_to_date(self.contract_end_date),
            annual_salary=self.annual_salary,
            monthly_salary=self.monthly_salary,
            base_salary=self.base_salary,
            base_hour_per_week=self.base_hour_per_week,
            base_hour_per_day=self.base_hour_per_day,
            weekly_rest_hours=self.weekly_rest_hours,
            fixed_overtime_allowance=self.fixed_overtime_allowance,
            fixed_overtime_hours=self.fixed_overtime_hours,
            annual_leave_allowance=self.annual_leave_allowance,
            annual_leave_hour_per_day=self.annual_leave_hour_per_day,
            annual_leave_count=self.annual_leave_count,
            holiday_allowance=self.holiday_allowance,
            holiday_allowance_hours=self.holiday_allowance_hours,
            duty_allowance=self.duty_allowance,
            night_allowance=self.night_allowance,
            meal_allowance=self.meal_allowance,
            vehicle_maintenance_allowance=self.vehicle_maintenance_allowance
        )

class RequestUpdateSalaryContract(BaseModel):
    salary_contract_id: int = Field(..., description="급여 계약 ID")
    contract_start_date: Optional[str] = Field(default=None, description="계약 시작일")
    contract_end_date: Optional[str] = Field(default=None, description="계약 종료일")
    annual_salary: Optional[int] = Field(default=None, description="연봉")
    monthly_salary: Optional[int] = Field(default=None, description="월급")
    base_salary: Optional[int] = Field(default=None, description="기본급")
    base_hour_per_week: Optional[int] = Field(default=None, description="기본근무시간 (일주일)")
    base_hour_per_day: Optional[int] = Field(default=None, description="기본근무시간 (하루)")
    weekly_rest_hours: Optional[int] = Field(default=None, description="주휴시간")
    fixed_overtime_allowance: Optional[int] = Field(default=None, description="고정연장근로수당")
    fixed_overtime_hours: Optional[int] = Field(default=None, description="고정연장근로시간")
    annual_leave_allowance: Optional[int] = Field(default=None, description="연차수당")
    annual_leave_hour_per_day: Optional[int] = Field(default=None, description="연차시간 (일)")
    annual_leave_count: Optional[int] = Field(default=None, description="연차수")
    holiday_allowance: Optional[int] = Field(default=None, description="휴일수당")
    holiday_allowance_hours: Optional[int] = Field(default=None, description="휴일수당시간")
    duty_allowance: Optional[int] = Field(default=None, description="근무수당")
    night_allowance: Optional[int] = Field(default=None, description="야간수당")
    meal_allowance: Optional[int] = Field(default=None, description="식대")
    vehicle_maintenance_allowance: Optional[int] = Field(default=None, description="차량유지비")


class SalaryContractDto(BaseModel):
    contract_start_date: str = Field(..., description="계약 시작일")
    contract_end_date: Optional[str] = Field(None, description="계약 종료일")
    annual_salary: int = Field(..., description="연봉")
    monthly_salary: int = Field(..., description="월급")
    base_salary: int = Field(..., description="기본급")
    base_hour_per_week: int = Field(..., description="기본근무시간 (일주일)")
    base_hour_per_day: int = Field(..., description="기본근무시간 (하루)")
    weekly_rest_hours: Optional[int] = Field(default=None, description="주휴시간")
    fixed_overtime_allowance: int = Field(..., description="고정연장근로수당")
    fixed_overtime_hours: int = Field(..., description="고정연장근로시간")
    annual_leave_allowance: int = Field(..., description="연차수당")
    annual_leave_hour_per_day: int = Field(..., description="연차시간 (일)")
    annual_leave_count: int = Field(..., description="연차수")
    holiday_allowance: Optional[int] = Field(None, description="휴일수당")
    holiday_allowance_hours: int = Field(..., description="휴일수당시간")
    duty_allowance: Optional[int] = Field(None, description="근무수당")
    night_allowance: Optional[int] = Field(None, description="야간수당")
    meal_allowance: Optional[int] = Field(None, description="식대")
    vehicle_maintenance_allowance: Optional[int] = Field(None, description="차량유지비")

    @classmethod
    def build(cls, salary_contract: SalaryContract):
        return cls(
            contract_start_date=DatetimeUtil.date_to_str(salary_contract.contract_start_date),
            contract_end_date=DatetimeUtil.date_to_str(salary_contract.contract_end_date) if salary_contract.contract_end_date else None,
            annual_salary=salary_contract.annual_salary,
            monthly_salary=salary_contract.monthly_salary,
            base_salary=salary_contract.base_salary,
            base_hour_per_week=salary_contract.base_hour_per_week,
            base_hour_per_day=salary_contract.base_hour_per_day,
            weekly_rest_hours=salary_contract.weekly_rest_hours,
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
