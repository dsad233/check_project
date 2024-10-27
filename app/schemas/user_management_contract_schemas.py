from pydantic import BaseModel

from app.models.users.users_contract_model import Contract
from app.models.users.users_model import Users

# ==================== Request ====================

class AddContract(BaseModel):
    user_id: int
    manager_id: int
    contract_name: str
    contract_type_id: int
    expired_at: str

class RequestAddContracts(BaseModel):
    contracts: list[AddContract]

class RequestRemoveContract(BaseModel):
    user_id: int
    contract_id: int

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
