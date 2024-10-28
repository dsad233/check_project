from typing import Optional

from pydantic import BaseModel

from app.models.users.users_model import Users
from app.models.users.users_work_contract_model import WorkContract, FixedRestDay


# ==================== Request ====================

class RequestWorkContractFixedRestDay(BaseModel):
    rest_day: str
    every_over_week: bool


class RequestCreateWorkContract(BaseModel):
    user_id: int
    contract_start_date: str
    contract_end_date: Optional[str] = None
    is_fixed_rest_day: bool
    fixed_rest_days: Optional[list[RequestWorkContractFixedRestDay]]
    weekly_work_start_time: str
    weekly_work_end_time: str
    weekly_is_rest: bool
    saturday_work_start_time: str
    saturday_work_end_time: str
    saturday_is_rest: bool
    sunday_work_start_time: str
    sunday_work_end_time: str
    sunday_is_rest: bool
    break_start_time: str
    break_end_time: str


class RequestPatchWorkContract(BaseModel):
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    is_fixed_rest_day: Optional[bool] = None
    fixed_rest_days: Optional[list[RequestWorkContractFixedRestDay]] = None
    weekly_work_start_time: Optional[str] = None
    weekly_work_end_time: Optional[str] = None
    weekly_is_rest: Optional[bool] = None
    saturday_work_start_time: Optional[str] = None
    saturday_work_end_time: Optional[str] = None
    saturday_is_rest: Optional[bool] = None
    sunday_work_start_time: Optional[str] = None
    sunday_work_end_time: Optional[str] = None
    sunday_is_rest: Optional[bool] = None
    break_start_time: Optional[str] = None
    break_end_time: Optional[str] = None

    def to_update_dict(self) -> dict:
        return {
            key: value
            for key, value in self.model_dump().items()
            if value is not None
        }

# ==================== Response ====================

class ResponseCreatedWorkContractDto(BaseModel):
    work_contract_id: int

    @classmethod
    def build(cls, work_contract_id: int):
        return cls(
            work_contract_id=work_contract_id
        )

class UserDto(BaseModel):
    user_id: int
    employment_status: str

    @classmethod
    def build(cls, user):
        return cls(
            user_id=user.id,
            employment_status=user.employment_status,
        )


class UserWorkContractFixedRestDayDto(BaseModel):
    rest_day: str
    every_over_week: bool

    @classmethod
    def build(cls, fixed_rest_day: FixedRestDay):
        return cls(
            rest_day=fixed_rest_day.rest_day,
            every_over_week=fixed_rest_day.every_over_week
        )

class WorkContractDto(BaseModel):
    work_contract_id: int
    fixed_rest_days: list[UserWorkContractFixedRestDayDto]

    weekly_work_start_time: str
    weekly_work_end_time: str
    weekly_is_rest: bool
    saturday_work_start_time: str
    saturday_work_end_time: str
    saturday_is_rest: bool
    sunday_work_start_time: str
    sunday_work_end_time: str
    sunday_is_rest: bool

    break_start_time: str
    break_end_time: str

    @classmethod
    def build(cls, work_contract: WorkContract):
        try:
            return cls(
                work_contract_id=work_contract.id,
                fixed_rest_days=[
                    UserWorkContractFixedRestDayDto.build(
                        fixed_rest_day=rest_day
                    ) for rest_day in work_contract.fixed_rest_days],
                weekly_work_start_time=work_contract.weekly_work_start_time.strftime("%H:%M"),
                weekly_work_end_time=work_contract.weekly_work_end_time.strftime("%H:%M"),
                weekly_is_rest=work_contract.weekly_is_rest,
                saturday_work_start_time=work_contract.saturday_work_start_time.strftime("%H:%M"),
                saturday_work_end_time=work_contract.saturday_work_end_time.strftime("%H:%M"),
                saturday_is_rest=work_contract.saturday_is_rest,
                sunday_work_start_time=work_contract.sunday_work_start_time.strftime("%H:%M"),
                sunday_work_end_time=work_contract.sunday_work_end_time.strftime("%H:%M"),
                sunday_is_rest=work_contract.sunday_is_rest,
                break_start_time=work_contract.break_start_time.strftime("%H:%M"),
                break_end_time=work_contract.break_end_time.strftime("%H:%M")
            )
        except Exception as e:
            print(e)



class ResponseUserWorkContractDto(BaseModel):
    user: UserDto
    work_contract: WorkContractDto

    @classmethod
    def build(cls, user: Users, work_contract: WorkContract):
        return cls(
            user=UserDto.build(user),
            work_contract=WorkContractDto.build(work_contract)
        )