from fastapi import APIRouter, Depends, Path, Body, Query
from fastapi.params import Annotated

from app.common.dto.response_dto import ResponseDTO
from app.dependencies.user_management import get_user_management_contract_info_service
from app.middleware.tokenVerify import get_current_user
from app.models.users.users_model import Users
from app.schemas.user_management.contract_info import RequestCreateContractInfo, RequestUpdateContractInfo, \
    ResponseTotalContractInfo, ResponseCreatedContractInfo, RequestApproveContract
from app.schemas.user_management_contract_schemas import RequestUpdateContract
from app.service.user_management.contract_info_service import UserManagementContractInfoService

router = APIRouter()

class UserManagementContractInfo:
    router = router


    @router.get("/{user_id}", response_model=ResponseDTO[ResponseTotalContractInfo])
    async def get_user_contract_info(
            user_id: Annotated[int, Path(..., title="사용자 ID", gt=0)],
            contract_info_id: Annotated[int, Query(..., title="계약 정보 ID", gt=0)],
            contract_info_service: Annotated[UserManagementContractInfoService, Depends(get_user_management_contract_info_service)],
            current_user: Annotated[Users, Depends(get_current_user)],
    ):
        total_contract_info = await contract_info_service.get_total_contract_info(
            user_id=user_id,
            contract_info_id=contract_info_id
        )

        return ResponseDTO(
            message="계약 정보 조회 성공",
            status="SUCCESS",
            data=total_contract_info
        )

    @router.post("/{user_id}")
    async def add_user_contract_info(
            user_id: Annotated[int, Path(..., title="사용자 ID", gt=0)],
            request_create_contract_info: Annotated[RequestCreateContractInfo, Body(..., title="계약 정보 생성 요청")],
            contract_info_service: Annotated[UserManagementContractInfoService, Depends(get_user_management_contract_info_service)],
            current_user: Annotated[Users, Depends(get_current_user)],
    ):
        contract_info = request_create_contract_info.to_domain(user_id=user_id, manager_id=current_user.id)
        created_contract_info_id = await contract_info_service.register_new_contract_info(
            user_id=user_id,
            contract_info=contract_info
        )

        data = ResponseCreatedContractInfo.build(contract_info_id=created_contract_info_id)

        return ResponseDTO(
            message="계약 정보 생성 성공",
            status="SUCCESS",
            data=data
        )

    @router.patch("/{user_id}")
    async def update_user_contract_info(
            user_id: Annotated[int, Path(..., title="사용자 ID", gt=0)],
            contract_info_id: Annotated[int, Query(..., title="계약 정보 ID", gt=0)],
            request_create_contract_info: Annotated[RequestUpdateContractInfo, Body(..., title="계약 정보 수정 요청")],
            contract_info_service: Annotated[UserManagementContractInfoService, Depends(get_user_management_contract_info_service)],
            current_user: Annotated[Users, Depends(get_current_user)],
    ):
        raise NotImplementedError("아직 구현되지 않았습니다.")


    @router.patch("/{contract_info_id}/update", response_model=ResponseDTO)
    async def update_contract(
            contract_info_id: Annotated[int, Path(..., title="계약 정보 ID", gt=0)],
            request_update_contract: Annotated[RequestUpdateContract, Body(..., title="계약서 수정 요청")],
            contract_info_service: Annotated[UserManagementContractInfoService, Depends(get_user_management_contract_info_service)],
            current_user: Annotated[Users, Depends(get_current_user)],
    ):
        update_params = request_update_contract.model_dump(exclude_none=True)
        change_reason = update_params.pop("change_reason")
        note = update_params.pop("note")

        if not change_reason:
            raise ValueError("변경 사유는 필수입니다.")

        await contract_info_service.update_contract_info(
            contract_info_id=contract_info_id,
            update_params=update_params,
            change_reason=change_reason,
            note=note
        )

        return ResponseDTO(
            message="계약 정보 수정 성공",
            status="SUCCESS"
        )

    @router.post("/{contract_info_id}/send", response_model=ResponseDTO)
    async def send_contract(
            contract_info_id: Annotated[int, Path(..., title="계약 정보 ID", gt=0)],
            request_approve_contract: Annotated[RequestApproveContract, Body(..., title="계약 승인 요청")],
            contract_info_service: Annotated[UserManagementContractInfoService, Depends(get_user_management_contract_info_service)],
            current_user: Annotated[Users, Depends(get_current_user)],
    ):
        await contract_info_service.send_contracts(
            user_id=request_approve_contract.user_id,
            contract_info_id=contract_info_id
        )

        return ResponseDTO(
            message="계약 정보 전송 성공",
            status="SUCCESS"
        )


user_management_contract_info = UserManagementContractInfo()