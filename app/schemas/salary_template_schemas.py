from pydantic import BaseModel, Field
from typing import Optional
from app.common.dto.pagination_dto import PaginationDto


class SalaryTemplateRequest(BaseModel):
    id: Optional[int] = Field(default=None, description="템플릿ID")
    part_id: int = Field(description="직책ID")
    name: str = Field(description="템플릿명")
    is_january_entry: bool = Field(description="1월입사여부")
    weekly_work_days: int = Field(description="주간근무일수")
    month_salary: int = Field(description="월급")
    included_holiday_allowance: bool = Field(description="휴일수당포함여부")
    included_job_allowance: bool = Field(description="직책수당포함여부")
    hour_wage: int = Field(description="시급")
    basic_salary: int = Field(description="기본급여")
    contractual_working_hours: int = Field(description="소정근로시간")
    weekly_rest_hours: int = Field(description="주휴시간")
    annual_salary: int = Field(description="연봉")
    comprehensive_overtime_allowance: int = Field(description="포괄산정연장근무수당")
    comprehensive_overtime_hour: int = Field(description="포괄산정연장근무시간")
    annual_leave_allowance: int = Field(description="연차수당")
    annual_leave_allowance_hour: int = Field(description="연차수당시간")
    annual_leave_allowance_day: int = Field(description="연차수당일수")
    hire_year: int = Field(descriptio="입사년도 ( 몇년도 기준 임금정책인지 )")



class SalaryTemplateResponse(BaseModel):
    id: Optional[int] = Field(default=None, description="템플릿ID")
    part_id: int = Field(description="직책ID")
    part_name: Optional[str] = Field(description="직책명", default=None)
    name: str = Field(description="템플릿명")
    is_january_entry: bool = Field(description="1월입사여부")
    weekly_work_days: int = Field(description="주간근무일수")
    month_salary: int = Field(description="월급")
    included_holiday_allowance: bool = Field(description="휴일수당포함여부")
    included_job_allowance: bool = Field(description="직책수당포함여부")
    hour_wage: int = Field(description="시급")
    basic_salary: int = Field(description="기본급여")
    contractual_working_hours: int = Field(description="소정근로시간")
    weekly_rest_hours: int = Field(description="주휴시간")
    annual_salary: int = Field(description="연봉")
    comprehensive_overtime_allowance: int = Field(description="포괄산정연장근무수당")
    comprehensive_overtime_hour: int = Field(description="포괄산정연장근무시간")
    annual_leave_allowance: int = Field(description="연차수당")
    annual_leave_allowance_hour: int = Field(description="연차수당시간")
    annual_leave_allowance_day: int = Field(description="연차수당일수")
    hire_year: int = Field(descriptio="입사년도 ( 몇년도 기준 임금정책인지 )")

    holiday_allowance: Optional[int] = Field(description="휴일수당", default=None)
    job_allowance: Optional[int] = Field(description="직무(직책)수당", default=None)
    meal_allowance: Optional[int] = Field(description="식대", default=None)

    class Config:
        from_attributes = True


class SalaryTemplatesResponse(BaseModel):
    data: list[SalaryTemplateResponse]
    pagination: PaginationDto

    class Config:
        from_attributes = True