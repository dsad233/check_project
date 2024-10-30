from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from app.schemas.parts_schemas import PartIdWithName
from app.common.dto.pagination_dto import PaginationDto
from datetime import datetime


class AccountBasedGrantDto(BaseModel):
    account_based_january_1st: Literal['초기화', "다음해로 이월"] = Field(description="매 년 1월 1일기준", default="초기화")
    account_based_less_than_year: Literal['당해년도 일괄 부여', "매 월 1개씩 부여"] = Field(description="근속년수 1년 미만", default="당해년도 일괄 부여")
    account_based_decimal_point: Literal['0.5 기준 올림', "절삭", "올림", "반올림"] = Field(description="소수점처리", default="0.5 기준 올림")

    class Config:
        from_attributes = True


class ConditionBasedGrantDto(BaseModel):
    id: Optional[int] = Field(description="조건부여 아이디", default=None)
    condition_based_month: int = Field(description="월", default=0)
    condition_based_cnt: int = Field(description="일", default=0)

    @field_validator("id")
    def validate_id(cls, v):
        if v == "" or v == 0:
            return None
        return v

    class Config:
        from_attributes = True


class EntryDateBasedGrantDto(BaseModel):
    entry_date_based_remaining_leave: Literal['초기화', "다음해로 이월"] = Field(description="매 년 입사일 기준", default="초기화")

    class Config:
        from_attributes = True


class AccountPoliciesWithParts(AccountBasedGrantDto):
    part_ids: list[PartIdWithName] = []


class EntryDatePoliciesWithParts(EntryDateBasedGrantDto):
    part_ids: list[PartIdWithName] = []


class ConditionPoliciesWithParts(BaseModel):
    condition_based_grant: list[ConditionBasedGrantDto]
    part_ids: list[PartIdWithName] = []


class AutoAnnualLeaveApprovalDto(BaseModel):
    top_auto_approval: bool = Field(description="통합관리자 자동승인", default=False)
    total_auto_approval: bool = Field(description="관리자 자동승인", default=False)
    part_auto_approval: bool = Field(description="사원 자동승인", default=False)

    class Config:
        from_attributes = True


class AutoLeavePoliciesAndPartsDto(BaseModel):
    auto_approval_policies: AutoAnnualLeaveApprovalDto
    account_based_policies: AccountPoliciesWithParts
    entry_date_based_policies: EntryDatePoliciesWithParts
    condition_based_policies: ConditionPoliciesWithParts
    manual_based_parts: list[PartIdWithName] = []


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


class BranchHistoryResponse(BaseModel):
    snapshot_id: str
    history: dict

    class Config:
        from_attributes = True

class BranchHistoriesResponse(BaseModel):
    data: list[BranchHistoryResponse]
    pagination: PaginationDto


class BranchRequest(BaseModel):
    code: str = Field(description="지점 코드")
    name: str = Field(description="지점 이름")
    representative_name: str = Field(description="대표 원장 이름")
    registration_number: str = Field(description="사업자번호")
    call_number: str = Field(description="전화번호")
    address: str = Field(description="지점 주소")
    corporate_seal: Optional[str] = Field(description="법인 도장", default=None)
    nameplate: Optional[str] = Field(description="명판", default=None)
    mail_address: str = Field(description="메일 주소")

    @field_validator("corporate_seal", "nameplate")
    def validate_file_extension(cls, v):
        if v == "":
            return None
        return v


class BranchResponse(BaseModel):
    id: int = Field(description="지점 아이디")
    code: str = Field(description="지점 코드")
    name: str = Field(description="지점 이름")
    representative_name: str = Field(description="대표 원장 이름")
    registration_number: str = Field(description="사업자번호")
    call_number: str = Field(description="전화번호")
    address: str = Field(description="지점 주소")
    corporate_seal: Optional[str] = Field(description="법인 도장")
    nameplate: Optional[str] = Field(description="명판")
    mail_address: str = Field(description="메일 주소")
    created_at: datetime = Field(description="생성 일자")
    updated_at: datetime = Field(description="수정 일자")
    deleted_yn: str = Field(description="삭제 여부")

    class Config:
        from_attributes = True


class BranchListResponse(BaseModel):
    data: list[BranchResponse] = Field(description="지점 목록")
    pagination: PaginationDto = Field(description="페이지네이션")


class ManualGrantRequest(BaseModel):
    count: int
    user_ids: list[int]
    memo: Optional[str] = None

