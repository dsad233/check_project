from typing import Optional

from pydantic import BaseModel

from app.models.users.users_contract_model import Contract, ContractSendMailHistory
from app.models.users.users_model import Users
from app.schemas.user_management.part_timers_contract_schemas import RequestCreatePartTimeContract
from app.schemas.user_management.salary_contract import RequestCreateSalaryContract
from app.schemas.user_work_contract_schemas import RequestCreateWorkContract


# ==================== Request ====================

class AddContract(BaseModel):
    user_id: int
    manager_id: int
    contract_name: str
    contract_type_id: int
    start_at: str
    expired_at: str

class RequestAddContracts(BaseModel):
    contracts: list[AddContract]

class RequestRemoveContract(BaseModel):
    user_id: int
    contract_id: int

class RequestSendMailContract(BaseModel):
    user_id: int
    request_user_id: int
    request_contract_id: int


class BaseRequestContract(BaseModel):
    contract_info_id: int
    note: Optional[str] = None
    change_reason: Optional[str] = None

class RequestPermanentContract(BaseRequestContract):
    work_contract: RequestCreateWorkContract
    salary_contract: RequestCreateSalaryContract

class RequestTemporaryContract(BaseRequestContract):
    part_time_contract: RequestCreatePartTimeContract

# ==================== Response ====================

class ManagerDto(BaseModel):
    manager_id: int
    manager_name: str

    @classmethod
    def build(cls, manager: Users):
        return cls(manager_id=manager.id, manager_name=manager.name)

class ContractDto(BaseModel):
    contract_id: int
    manager: ManagerDto | None
    contract_name: str
    expired_at: str
    send_count: int = 0

    @classmethod
    def build(cls, contract: Contract):
        return cls(
            contract_id=contract.id,
            contract_name=contract.contract_name,
            manager=ManagerDto.build(manager=contract.manager),
            expired_at=str(contract.expired_at)
        )


class AddedContractDto(BaseModel):
    contract_id: int

    @classmethod
    def build(cls, contract_id: int):
        return cls(contract_id=contract_id)


class ResponseUserContracts(BaseModel):
    contracts: list[ContractDto]

    @classmethod
    def build(cls, contracts: list[Contract]):
        return cls(
            contracts=[
                ContractDto.build(contract=contract)
                for contract in contracts
            ]
       )


class ResponseAddedContracts(BaseModel):
    contracts: list[AddedContractDto]

    @classmethod
    def build(cls, contract_ids: list[int]):
        return cls(
            contracts=[
                AddedContractDto.build(contract_id=contract_id)
                for contract_id in contract_ids
            ]
        )


class SendMailRequestUserDto(BaseModel):
    id: int
    name: str

    @classmethod
    def build(cls, user: Users):
        return cls(id=user.id, name=user.name)

class SendMailContractDto(BaseModel):
    contract_id: int
    contract_name: str
    contract_start_at: str
    contract_expired_at: str

    @classmethod
    def build(cls, contract: Contract):
        return cls(
            contract_id=contract.id,
            contract_name=contract.contract_name,
            contract_start_at=str(contract.start_at),
            contract_expired_at=str(contract.expired_at)
        )

class SendMailHistoryDto(BaseModel):
    send_mail_history_id: int
    contract: SendMailContractDto
    request_user: SendMailRequestUserDto

    @classmethod
    def build(cls, contract_send_mail_history: ContractSendMailHistory):
        return cls(
            send_mail_history_id=contract_send_mail_history.id,
            contract=SendMailContractDto.build(contract=contract_send_mail_history.contract),
            request_user=SendMailRequestUserDto.build(user=contract_send_mail_history.request_user)
        )


class ResponseSendMailContract(BaseModel):
    send_mail_histories: list[SendMailHistoryDto]

    @classmethod
    def build(cls, contract_send_mail_histories: list[ContractSendMailHistory]):
        return cls(
            send_mail_histories=[
                SendMailHistoryDto.build(contract_send_mail_history=contract_send_mail_history)
                for contract_send_mail_history in contract_send_mail_histories
            ]
        )
