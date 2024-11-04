from typing import Optional

from pydantic import BaseModel

from app.models.users.users_contract_info_model import ContractInfo
from app.schemas.user_management.part_timers_contract_schemas import PartTimerWorkContractDto
from app.schemas.user_management.salary_contract import SalaryContractDto, RequestCreateSalaryContract
from app.schemas.user_work_contract_schemas import WorkContractDto, RequestCreateWorkContract
from app.utils.datetime_utils import DatetimeUtil


class ContractInfoDto(BaseModel):
    hire_date: str
    resignation_date: Optional[str]
    contract_renewal_date: Optional[str]
    part_id: int
    job_title: str
    position: str
    employ_status: str

    @classmethod
    def build(cls, contract_info: ContractInfo) -> "ContractInfoDto":
        return ContractInfoDto(
            hire_date=DatetimeUtil.date_to_str(contract_info.hire_date),
            resignation_date=DatetimeUtil.date_to_str(contract_info.resignation_date) if contract_info.resignation_date else None,
            contract_renewal_date=DatetimeUtil.date_to_str(contract_info.contract_renewal_date) if contract_info.contract_renewal_date else None,
            part_id=contract_info.part_id,
            job_title=contract_info.job_title,
            position=contract_info.position,
            employ_status=contract_info.employ_status
        )


class ResponseTotalContractInfo(BaseModel):
    contract_info: ContractInfoDto
    work_contract: Optional[WorkContractDto]
    salary_contract: Optional[SalaryContractDto]
    # part_time_contract: Optional[PartTimeContractDto]

    @classmethod
    def build(
            cls,
            contract_info: ContractInfoDto,
            work_contract: Optional[WorkContractDto],
            salary_contract: Optional[SalaryContractDto],
            part_time_contract: Optional[PartTimerWorkContractDto]
    ) -> "ResponseTotalContractInfo":
        return ResponseTotalContractInfo(
            contract_info=contract_info,
            work_contract=work_contract,
            salary_contract=salary_contract,
            part_time_contract=part_time_contract
        )

class ResponseCreatedContractInfo(BaseModel):
    contract_info_id: int

    @staticmethod
    def build(contract_info_id: int) -> "ResponseCreatedContractInfo":
        return ResponseCreatedContractInfo(contract_info_id=contract_info_id)


class RequestCreateContractInfo(BaseModel):
    hire_date: str
    resignation_date: Optional[str]
    contract_renewal_date: Optional[str]
    part_id: int
    job_title: str
    position: str
    employ_status: str

    @classmethod
    def to_domain(cls, user_id: int, manager_id: int) -> ContractInfo:
        return ContractInfo(
            user_id=user_id,
            manager_id=manager_id,
            hire_date=DatetimeUtil.str_to_date(cls.hire_date),
            resignation_date=DatetimeUtil.str_to_date(cls.resignation_date) if cls.resignation_date else None,
            contract_renewal_date=DatetimeUtil.str_to_date(cls.contract_renewal_date) if cls.contract_renewal_date else None,
            part_id=cls.part_id,
            job_title=cls.job_title,
            position=cls.position,
            employ_status=cls.employ_status
        )

class RequestUpdateContractInfo(BaseModel):
    hire_date: Optional[str]
    resignation_date: Optional[str]
    contract_renewal_date: Optional[str]
    part_id: Optional[int]
    job_title: Optional[str]
    position: Optional[str]
    employ_status: Optional[str]

class RequestApproveContract(BaseModel):
    user_id: int
