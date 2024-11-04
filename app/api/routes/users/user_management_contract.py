import asyncio

from fastapi import APIRouter, Depends

from app.common.dto.response_dto import ResponseDTO
from app.dependencies.user_management import get_user_management_contract_service
from app.enums.user_management import ContractType
from app.middleware.tokenVerify import get_current_user
from app.models.users.users_contract_model import Contract
from app.models.users.users_model import Users
from app.schemas.user_management_contract_schemas import RequestPermanentContract
from app.service.user_management.contract_service import UserManagementContractService

router = APIRouter()

class UserManagementContract:
    router = router


    @router.get("/{user_id}/history")
    async def get_contract_histories(
            user_id: int,
            contract_service: UserManagementContractService = Depends(get_user_management_contract_service),
            current_user: Users = Depends(get_current_user),
    ):
        contract_histories = await contract_service.get_contract_histories_by_user_id(user_id=user_id)

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 계약서 이력을 가져왔습니다.",
            data=contract_histories
        )

    @router.post("/permanent", response_model=ResponseDTO)
    async def add_permanent_contract(
            request_permanent_contract: RequestPermanentContract,
            contract_service: UserManagementContractService = Depends(get_user_management_contract_service),
            current_user: Users = Depends(get_current_user),
    ):
        await contract_service.register_permanent_contract(
            contract_info_id=request_permanent_contract.contract_info_id,
            work_contract=request_permanent_contract.work_contract.to_domain(),
            salary_contract=request_permanent_contract.salary_contract.to_domain(),
            note=request_permanent_contract.note,
            change_reason=request_permanent_contract.change_reason
        )

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 정규직 계약서를 생성했습니다."
        )

    @router.post("/temporary", response_model=ResponseDTO)
    async def add_temporary_contract(
            request_temporary_contract: RequestTemporaryContract,
            contract_service: UserManagementContractService = Depends(get_user_management_contract_service),
            current_user: Users = Depends(get_current_user),
    ):
        await contract_service.register_temporary_contract(
            contract_info_id=request_temporary_contract.contract_info_id,
            part_time_contract=request_temporary_contract.part_time_contract.to_domain(),
            note=request_temporary_contract.note,
            change_reason=request_temporary_contract.change_reason
        )

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 계약직 계약서를 생성했습니다."
        )

    # @router.patch("")


    @router.post("/request-contract")
    async def request_contract(
            user_id: int,
            work_contract_history_id: int,
            contract_service: UserManagementContractService = Depends(get_user_management_contract_service),
            current_user: Users = Depends(get_current_user),
    ):
        await contract_service.create_contract2(
            user_id=user_id,
            manager_id=current_user.id,
            work_contract_history_id=work_contract_history_id,
        )

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 계약서를 요청했습니다."
        )




    # @router.get("/send_mail/{user_id}", response_model=ResponseDTO[ResponseSendMailContract])
    # async def get_send_mail_history(
    #         user_id: int,
    #         db: AsyncSession = Depends(get_db),
    #         current_user: Users = Depends(get_current_user),
    # ):
    #     contract_send_mail_histories = await find_contract_send_mail_histories_by_user_id(
    #         session=db,
    #         user_id=user_id
    #     )
    #
    #     data = ResponseSendMailContract.build(contract_send_mail_histories)
    #
    #     return ResponseDTO(
    #         status="SUCCESS",
    #         message="성공적으로 계약서 메일 전달 이력을 가져왔습니다.",
    #         data=data
    #     )
    #
    #
    # @router.post("/send_mail", response_model=ResponseDTO)
    # async def send_mail_contract(
    #         request_send_mail_contract: RequestSendMailContract,
    #         db: AsyncSession = Depends(get_db),
    #         current_user: Users = Depends(get_current_user),
    # ):
    #     # 계약서 정보 가져오기
    #     contract = await find_contract_by_contract_id(
    #         session=db,
    #         user_id=request_send_mail_contract.user_id,
    #         contract_id=request_send_mail_contract.request_contract_id
    #     )
    #
    #     # 메일 보내기 로직
    #     print(f"메일을 보내는 로직: {contract}")
    #
    #     # 메일 전달 history
    #     contract_send_mail_history_dict = {
    #         "contract_id": contract.id,
    #         "user_id": request_send_mail_contract.user_id,
    #         "request_user_id": request_send_mail_contract.request_user_id,
    #         "contract_start_at": contract.start_at,
    #         "contract_expired_at": contract.expired_at,
    #         "status": SendMailStatus.SUCCESS
    #     }
    #
    #     await add_contract_send_mail_history(
    #         session=db,
    #         contract_send_mail_history_dict=contract_send_mail_history_dict
    #     )
    #
    #     return ResponseDTO(
    #         status="SUCCESS",
    #         message="성공적으로 계약서 메일을 발송했습니다."
    #     )


user_management_contract = UserManagementContract()