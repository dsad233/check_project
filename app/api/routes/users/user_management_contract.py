from fastapi import APIRouter, Depends, HTTPException

from app.common.dto.response_dto import ResponseDTO
from app.core.database import async_session
from app.cruds.user_management.user_management_contract_crud import find_by_id_with_contracts, add_contracts, \
    hard_delete_contract
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users
from app.schemas.user_management_contract_schemas import ResponseUserContracts, RequestAddContracts, \
    ResponseAddedContracts, RequestRemoveContract

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()

class UserManagementContract:
    router = router

    @router.get("", response_model=ResponseDTO[ResponseUserContracts])
    async def get_user_contracts(
        user_id: int,
        current_user: Users = Depends(get_current_user),
    ):
        user = await find_by_id_with_contracts(session=db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        data = ResponseUserContracts.build(user.contracts_user_id)

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 계약서를 가져왔습니다.",
            data=data,
        )

    @router.post("", response_model=ResponseDTO[ResponseAddedContracts])
    async def add_user_contract(
        request_add_contracts: RequestAddContracts,
        current_user: Users = Depends(get_current_user),
    ):
        contracts = [
            {
                "user_id": contract.user_id,
                "manager_id": contract.manager_id,
                "contract_name": contract.contract_name,
                "contract_type_id": contract.contract_type_id,
                "expired_at": contract.expired_at
            }
            for contract in request_add_contracts.contracts
        ]

        add_contract_ids = await add_contracts(session=db, contracts=contracts)
        data = ResponseAddedContracts.build(contract_ids=add_contract_ids)

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 계약서를 추가했습니다.",
            data=data,
        )

    @router.delete("", response_model=ResponseDTO)
    async def delete_user_contract(
            request_remove_contract: RequestRemoveContract,
            current_user: Users = Depends(get_current_user),
    ):
        try:
            await hard_delete_contract(
                session=db,
                user_id=request_remove_contract.user_id,
                contract_id=request_remove_contract.contract_id
            )

            return ResponseDTO(
                status="SUCCESS",
                message="성공적으로 문서를 삭제했습니다."
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))



user_management_contract = UserManagementContract()