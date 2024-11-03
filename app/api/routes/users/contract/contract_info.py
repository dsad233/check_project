from fastapi import APIRouter, Depends, Path, Body, Query
from fastapi.params import Annotated

from app.common.dto.response_dto import ResponseDTO
from app.dependencies.user_management import get_user_management_contract_info_service
from app.middleware.tokenVerify import get_current_user
from app.models.users.users_model import Users
from app.schemas.user_management.contract_info import RequestCreateContractInfo, RequestUpdateContractInfo, \
    ResponseTotalContractInfo, ResponseCreatedContractInfo
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
        created_contract_info_id = await contract_info_service.add_contract_info(
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


user_management_contract_info = UserManagementContractInfo()