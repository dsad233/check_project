from datetime import date
from pydantic import BaseModel, Field

class UnusedAnnualLeaveAllowanceDTO(BaseModel):
    count: int = Field(description="미사용 연차 개수")
    daily_salary: int = Field(description="일급")
    total_amount: int = Field(description="총 금액")

class UsedAnnualLeaveDeductionDTO(BaseModel):
    count: int = Field(description="사용 연차 개수")
    total_amount: int = Field(description="총 공제 금액")

class EntireSalaryInfoResponseDTO(BaseModel):
    id: int = Field(description="급여 정보 ID")
    user_id: int = Field(description="사용자 ID")
    name: str = Field(description="이름")
    part_id: int = Field(description="파트 ID")
    part_name: str = Field(description="파트명")
    hire_date: date = Field(description="입사일")
    resignation_date: date | None = Field(description="퇴사일")
    monthly_salary: int = Field(description="월급")
    base_salary: int = Field(description="기본급")
    meal_allowance: int = Field(description="식대")
    fixed_overtime_allowance: int = Field(description="포괄 산정 연장 근로 수당")
    annual_leave_allowance: int = Field(description="연차 수당")
    holiday_allowance: int = Field(description="휴일 수당")
    night_work_allowance: int = Field(description="야간수당")
    duty_allowance: int = Field(description="직무 수당")
    insentive_allowance: int = Field(description="인센티브")
    holiday_work_allowance: int = Field(description="휴일근로수당")
    previous_month_unpaid: int = Field(description="전월미지급")
    overtime_allowance: int = Field(description="O.T 수당")
    weekend_work_allowance: int = Field(description="주말 근로수당")
    unused_annual_leave_allowance: UnusedAnnualLeaveAllowanceDTO = Field(description="미사용 연차수당")        
    used_annual_leave_deduction: UsedAnnualLeaveDeductionDTO = Field(description="연차 사용 공제")
    attendance_deduction: int = Field(description="근태 공제")
    vehicle_maintenance_allowance: int = Field(description="차량 유지비")
    total_salary: int = Field(description="급여 합계")

    hourly_wage: int = Field(description="통상 시급") # 최저시급과 비교하기 위한 필드






