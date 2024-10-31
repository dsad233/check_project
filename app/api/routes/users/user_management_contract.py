from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dto.response_dto import ResponseDTO
from app.core.database import get_db
from app.cruds.user_management.contract_crud import find_user_by_id_with_contracts, add_contracts, \
    hard_delete_contract, find_contract_by_contract_id, add_contract_send_mail_history, \
    find_contract_send_mail_histories_by_user_id
from app.enums.user_management import Status as SendMailStatus
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users
from app.schemas.user_management_contract_schemas import ResponseUserContracts, RequestAddContracts, \
    ResponseAddedContracts, RequestRemoveContract, RequestSendMailContract, ResponseSendMailContract
from app.service.user_management.contract_service import UserManagementContractService
from app.service.user_management.work_contract_service import UserManagementWorkContractService

router = APIRouter(dependencies=[Depends(validate_token)])
user_management_contract_service = UserManagementContractService()
user_management_work_contract_service = UserManagementWorkContractService()

class UserManagementContract:
    router = router

    @router.get("", response_model=ResponseDTO[ResponseUserContracts])
    async def get_user_contracts(
            user_id: int,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        user = await find_user_by_id_with_contracts(session=db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        data = ResponseUserContracts.build(user.contracts_user_id)

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 계약서를 가져왔습니다.",
            data=data,
        )

    @router.get("/history")
    async def get_user_contract_histories(
            user_id: int,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        user = await find_user_by_id_with_contracts(session=db, user_id=user_id)
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
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        contracts = [
            {
                "user_id": contract.user_id,
                "manager_id": contract.manager_id,
                "contract_name": contract.contract_name,
                "contract_type_id": contract.contract_type_id,
                "start_at": contract.start_at,
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
            db: AsyncSession = Depends(get_db),
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

    @router.post("/request-contract")
    async def request_contract(
            user_id: int,
            work_contract_history_id: int,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        await user_management_contract_service.create_contract(
            user_id=user_id,
            manager_id=current_user.id,
            work_contract_history_id=work_contract_history_id,
            session=db
        )

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 계약서를 요청했습니다."
        )

    @router.get("/send_mail/{user_id}", response_model=ResponseDTO[ResponseSendMailContract])
    async def get_send_mail_history(
            user_id: int,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        contract_send_mail_histories = await find_contract_send_mail_histories_by_user_id(
            session=db,
            user_id=user_id
        )

        data = ResponseSendMailContract.build(contract_send_mail_histories)

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 계약서 메일 전달 이력을 가져왔습니다.",
            data=data
        )


    @router.post("/send_mail", response_model=ResponseDTO)
    async def send_mail_contract(
            request_send_mail_contract: RequestSendMailContract,
            db: AsyncSession = Depends(get_db),
            current_user: Users = Depends(get_current_user),
    ):
        # 계약서 정보 가져오기
        contract = await find_contract_by_contract_id(
            session=db,
            user_id=request_send_mail_contract.user_id,
            contract_id=request_send_mail_contract.request_contract_id
        )

        # 메일 보내기 로직
        print(f"메일을 보내는 로직: {contract}")

        # 메일 전달 history
        contract_send_mail_history_dict = {
            "contract_id": contract.id,
            "user_id": request_send_mail_contract.user_id,
            "request_user_id": request_send_mail_contract.request_user_id,
            "contract_start_at": contract.start_at,
            "contract_expired_at": contract.expired_at,
            "status": SendMailStatus.SUCCESS
        }

        await add_contract_send_mail_history(
            session=db,
            contract_send_mail_history_dict=contract_send_mail_history_dict
        )

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 계약서 메일을 발송했습니다."
        )


user_management_contract = UserManagementContract()