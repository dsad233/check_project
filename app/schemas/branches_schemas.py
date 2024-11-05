from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, Optional
from app.enums.users import Weekday
from app.schemas.parts_schemas import PartIdWithName
from app.common.dto.search_dto import NamePhoneSearchDto
from app.common.dto.pagination_dto import PaginationDto
from datetime import datetime, time, date


class AccountBasedGrantDto(BaseModel):
    account_based_january_1st: Literal["초기화", "다음해로 이월"] = Field(
        description="매 년 1월 1일기준", default="초기화"
    )
    account_based_less_than_year: Literal["당해년도 일괄 부여", "매 월 1개씩 부여"] = (
        Field(description="근속년수 1년 미만", default="당해년도 일괄 부여")
    )
    account_based_decimal_point: Literal["0.5 기준 올림", "절삭", "올림", "반올림"] = (
        Field(description="소수점처리", default="0.5 기준 올림")
    )

    model_config = ConfigDict(from_attributes=True)


class ConditionBasedGrantDto(BaseModel):
    id: Optional[int] = Field(description="조건부여 아이디", default=None)
    condition_based_month: int = Field(description="월", default=0)
    condition_based_cnt: int = Field(description="일", default=0)

    @field_validator("id")
    def validate_id(cls, v):
        if v == "" or v == 0:
            return None
        return v

    model_config = ConfigDict(from_attributes=True)


class EntryDateBasedGrantDto(BaseModel):
    entry_date_based_remaining_leave: Literal["초기화", "다음해로 이월"] = Field(
        description="매 년 입사일 기준", default="초기화"
    )

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class AutoLeavePoliciesAndPartsDto(BaseModel):
    auto_approval_policies: AutoAnnualLeaveApprovalDto
    account_based_policies: AccountPoliciesWithParts
    entry_date_based_policies: EntryDatePoliciesWithParts
    condition_based_policies: ConditionPoliciesWithParts
    manual_based_parts: list[PartIdWithName] = []


class BranchHistoryResponse(BaseModel):
    snapshot_id: str
    history: dict

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class BranchListResponse(BaseModel):
    data: list[BranchResponse] = Field(description="지점 목록")
    pagination: PaginationDto = Field(description="페이지네이션")


class ManualGrantRequest(BaseModel):
    count: int
    user_ids: list[int]
    memo: Optional[str] = None


class BranchWorkScheduleDto(BaseModel):
    day_of_week: Optional[Weekday] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_holiday: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class BranchBreakTimeDto(BaseModel):
    is_doctor: Optional[bool] = None
    break_type: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    model_config = ConfigDict(from_attributes=True)


class WorkPoliciesDto(BaseModel):
    weekly_work_days: Optional[int] = Field(description="주간 근무일", default=5)
    work_schedules: Optional[list[BranchWorkScheduleDto]] = Field(description="근무일정", default=[])
    break_times: Optional[list[BranchBreakTimeDto]] = Field(description="휴게시간", default=[])

    model_config = ConfigDict(from_attributes=True)
        
        
class BranchWorkScheduleUpdateDto(BaseModel):
    day_of_week: Optional[Weekday] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_holiday: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class BranchBreakTimeUpdateDto(BaseModel):
    is_doctor: Optional[bool] = None
    break_type: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    model_config = ConfigDict(from_attributes=True)


class WorkPoliciesUpdateDto(BaseModel):
    id: Optional[int] = None
    branch_id: Optional[int] = None
    weekly_work_days: Optional[int] = None
    work_schedules: Optional[list[BranchWorkScheduleUpdateDto]] = None
    break_times: Optional[list[BranchBreakTimeUpdateDto]] = None

    model_config = ConfigDict(from_attributes=True)


class AutoOvertimePoliciesDto(BaseModel):
    top_auto_applied: bool = Field(description="통합관리자 자동적용", default=False)
    total_auto_applied: bool = Field(description="관리자 자동적용", default=False)
    part_auto_applied: bool = Field(description="사원 자동적용", default=False)

    model_config = ConfigDict(from_attributes=True)


class HolidayWorkPoliciesDto(BaseModel):
    do_holiday_work: bool = Field(description="휴무일 근무 여부", default=False)

    model_config = ConfigDict(from_attributes=True)


class OverTimePoliciesDto(BaseModel):
    doctor_ot_30: int = Field(description="O.T 30분 초과", default=0)
    doctor_ot_60: int = Field(description="O.T 60분 초과", default=0)
    doctor_ot_90: int = Field(description="O.T 90분 초과", default=0)
    doctor_ot_120: int = Field(description="O.T 120분 초과", default=0)

    common_ot_30: int = Field(description="O.T 30분 초과", default=0)
    common_ot_60: int = Field(description="O.T 60분 초과", default=0)
    common_ot_90: int = Field(description="O.T 90분 초과", default=0)
    common_ot_120: int = Field(description="O.T 120분 초과", default=0)

    model_config = ConfigDict(from_attributes=True)


class DefaultAllowancePoliciesDto(BaseModel):
    comprehensive_overtime: bool = Field(
        description="포괄산정 연장근무수당", default=False
    )
    annual_leave: bool = Field(description="연차수당", default=False)
    holiday_work: bool = Field(description="휴일수당", default=False)
    job_duty: bool = Field(description="직무수당", default=False)
    meal: bool = Field(description="식대", default=False)
    base_salary: bool = Field(description="기본급 사용여부", default=False)

    model_config = ConfigDict(from_attributes=True)


class HolidayAllowancePoliciesDto(BaseModel):
    doctor_holiday_work_pay: int = Field(description="의사 휴일수당", default=0)
    common_holiday_work_pay: int = Field(description="일반 휴일수당", default=0)

    model_config = ConfigDict(from_attributes=True)


class AllowancePoliciesDto(DefaultAllowancePoliciesDto, HolidayAllowancePoliciesDto):
    pass


class AllowancePoliciesResponse(BaseModel):
    branch_id: Optional[int] = None
    payment_day: Optional[int] = None
    job_duty: bool = Field(description="직무수당", default=False)
    meal: bool = Field(description="식대", default=False)
    base_salary: bool = Field(description="기본급 사용여부", default=False)

    is_additional_holiday_hundred: bool = Field(
        description="휴일 근로 수당 100원 단위", default=False
    )
    is_unused_annual_leave_hundred: bool = Field(
        description="미사용 연차 수당 100원 단위", default=False
    )
    is_annual_leave_deduction_hundred: bool = Field(
        description="연차사용공제 100원 단위", default=False
    )
    is_attendance_deduction_hundred: bool = Field(
        description="근태공제 100원 단위", default=False
    )

    display_meal_calc: bool = Field(description="식대 계산 표시", default=False)
    display_night_calc: bool = Field(description="야간 수당 계산 표시", default=False)

    model_config = ConfigDict(from_attributes=True)


class CombinedPoliciesDto(BaseModel):
    work_policies: WorkPoliciesDto
    auto_overtime_policies: AutoOvertimePoliciesDto
    holiday_work_policies: HolidayWorkPoliciesDto
    overtime_policies: OverTimePoliciesDto
    default_allowance_policies: DefaultAllowancePoliciesDto
    holiday_allowance_policies: HolidayAllowancePoliciesDto



class ScheduleHolidayUpdateDto(BaseModel):
    work_policies: WorkPoliciesUpdateDto


class PersonnelRecordCategoryRequest(BaseModel):
    id: Optional[int] = None
    name: str

    @field_validator("id")
    def validate_id(cls, v):
        if v == "" or v == 0:
            return None
        return v


class PersonnelRecordCategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class PersonnelRecordCategoriesResponse(BaseModel):
    data: list[PersonnelRecordCategoryResponse]
    pagination: PaginationDto
