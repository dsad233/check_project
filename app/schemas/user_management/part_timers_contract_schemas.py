from datetime import date, time
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from app.models.users.part_timer.users_part_timer_work_contract_model import WorkTypeEnum, PartTimerWorkContract, \
    PartTimerWorkingTime, PartTimerHourlyWage, PartTimerAdditionalInfo


class WorkingTimeDto(BaseModel):
    day_of_week: int = Field(..., description="요일 (0: 일요일, 6: 토요일)", ge=0, le=6)
    work_start_time: time = Field(..., description="작업 시작 시간")
    work_end_time: time = Field(..., description="작업 종료 시간")

class HourlyWageDto(BaseModel):
    calculate_start_time: time = Field(..., description="시급 계산 시작 시간")
    calculate_end_time: time = Field(..., description="시급 계산 종료 시간")
    hourly_wage: int = Field(..., description="시급", gt=0)

class AdditionalInfoDto(BaseModel):
    work_type: WorkTypeEnum = Field(..., description="작업 유형")
    rest_minutes: int = Field(default=30, description="휴식 시간(분)", ge=0)
    work_set_start_time: time = Field(..., description="설정된 작업 시작 시간")
    work_set_end_time: time = Field(..., description="설정된 작업 종료 시간")

class RequestCreatePartTimeContract(BaseModel):
    contract_start_date: date = Field(..., description="계약 시작 날짜")
    contract_end_date: date = Field(..., description="계약 종료 날짜")
    daily_break_time: int = Field(default=30, description="일일 휴식 시간(분)", ge=30)
    working_times: List[WorkingTimeDto] = Field(..., description="작업 시간 목록")
    hourly_wages: List[HourlyWageDto] = Field(..., description="시급 정보 목록")

    @field_validator("contract_end_date")
    def validate_dates(cls, end_date, values):
        start_date = values.get("contract_start_date")
        if start_date and end_date < start_date:
            raise ValueError("계약 종료 날짜는 계약 시작 날짜보다 빠를 수 없습니다.")
        return end_date

    def to_domain(self) -> PartTimerWorkContract:
        # PartTimerWorkContract 엔티티 생성
        part_time_contract = PartTimerWorkContract(
            contract_start_date=self.contract_start_date,
            contract_end_date=self.contract_end_date,
            daily_break_time=self.daily_break_time,
        )

        # 작업 시간 (WorkingTime) 엔티티 리스트 생성
        part_time_contract.working_times = [
            PartTimerWorkingTime(
                day_of_week=working_time.day_of_week,
                work_start_time=working_time.work_start_time,
                work_end_time=working_time.work_end_time
            )
            for working_time in self.working_times
        ]

        # 시급 정보 (HourlyWage) 엔티티 리스트 생성
        part_time_contract.hourly_wages = [
            PartTimerHourlyWage(
                calculate_start_time=hourly_wage.calculate_start_time,
                calculate_end_time=hourly_wage.calculate_end_time,
                hourly_wage=hourly_wage.hourly_wage
            )
            for hourly_wage in self.hourly_wages
        ]

        return part_time_contract

class PartTimerWorkContractDto(BaseModel):
    contract_start_date: date = Field(..., description="계약 시작 날짜")
    contract_end_date: date = Field(..., description="계약 종료 날짜")
    daily_break_time: int = Field(..., description="일일 휴식 시간(분)")
    working_times: List[WorkingTimeDto] = Field(..., description="작업 시간 목록")
    hourly_wages: List[HourlyWageDto] = Field(..., description="시급 정보 목록")

    @classmethod
    def build(cls, part_time_contract: PartTimerWorkContract) -> "PartTimerWorkContractDto":
        return cls(
            contract_start_date=part_time_contract.contract_start_date,
            contract_end_date=part_time_contract.contract_end_date,
            daily_break_time=part_time_contract.daily_break_time,
            working_times=[
                WorkingTimeDto(
                    day_of_week=working_time.day_of_week,
                    work_start_time=working_time.work_start_time,
                    work_end_time=working_time.work_end_time
                )
                for working_time in part_time_contract.part_timer_working_times
            ],
            hourly_wages=[
                HourlyWageDto(
                    calculate_start_time=hourly_wage.calculate_start_time,
                    calculate_end_time=hourly_wage.calculate_end_time,
                    hourly_wage=hourly_wage.hourly_wage
                )
                for hourly_wage in part_time_contract.part_timer_hourly_wages
            ]
        )