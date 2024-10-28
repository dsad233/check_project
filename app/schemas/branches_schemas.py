from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from app.schemas.parts_schemas import PartIdWithName


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