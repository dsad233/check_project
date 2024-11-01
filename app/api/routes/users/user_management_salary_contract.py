from pyexpat.errors import messages

from fastapi import APIRouter, Depends
from fastapi.params import Query, Annotated, Path

from app.common.dto.response_dto import ResponseDTO
from app.dependencies.user_management import get_user_management_salary_contract_service
from app.middleware.tokenVerify import get_current_user
from app.models.users.users_model import Users
from app.models.users.users_salary_contract_model import SalaryContract
from app.schemas.user_management.salary_contract import SalaryContractDto, RequestCreateSalaryContractDto, \
    RequestUpdateSalaryContractDto
from app.service.user_management.salary_contract_service import UserManagementSalaryContractService

permanent_router = APIRouter(prefix="/permanent")
temporary_router = APIRouter(prefix="/temporary")



class UserManagementSalaryContract:
    permanent_router = permanent_router
    temporary_router = temporary_router

    @permanent_router.get(
        path="/{user_id}",
        response_model=SalaryContractDto,
        summary="정규직 사용자 임금계약 정보 조회"
    )
    async def get_salary_contract(
            user_id: Annotated[int, Path(..., title="사용자 ID", gt=0)],
            service: Annotated[UserManagementSalaryContractService, Depends(get_user_management_salary_contract_service)],
            current_user: Annotated[Users, Depends(get_current_user)]
    ):
        salary_contract: SalaryContractDto = await service.get_salary_contract_by_user_id(
            user_id=user_id
        )

        return ResponseDTO(
            messages="사용자의 급여 계약 정보를 조회하였습니다.",
            status="SUCCESS",
            data=salary_contract
        )

    @permanent_router.post(
        path="",
        summary="정규직 사용자 임금계약 정보 생성"
    )
    async def create_salary_contract(
            request_create_salary_contract: Annotated[RequestCreateSalaryContractDto, ...],
            service: Annotated[UserManagementSalaryContractService, Depends(get_user_management_salary_contract_service)],
            current_user: Annotated[Users, Depends(get_current_user)]
    ):
        salary_contract: SalaryContract = RequestCreateSalaryContractDto.to_domain()
        await service.create_salary_contract(salary_contract=salary_contract)

        return ResponseDTO(
            messages="사용자의 급여 계약 정보를 생성하였습니다.",
            status="SUCCESS",
        )

    @permanent_router.patch(
        path="/{user_id}",
        response_model=SalaryContractDto,
        summary="정규직 사용자 임금계약 정보 수정"
    )
    async def partial_update_salary_contract(
            user_id: Annotated[int, Path(..., title="사용자 ID", gt=0)],
            request_update_salary_contract: Annotated[RequestUpdateSalaryContractDto, ...],
            service: Annotated[UserManagementSalaryContractService, Depends(get_user_management_salary_contract_service)],
            current_user: Annotated[Users, Depends(get_current_user)]
    ):
        update_params: dict = request_update_salary_contract.model_dump(exclude_unset=True)

        updated_salary_contract_dto: SalaryContractDto = await service.partial_update_salary_contract(
            user_id=user_id,
            update_params=update_params
        )

        return ResponseDTO(
            messages="사용자의 급여 계약 정보를 수정하였습니다.",
            status="SUCCESS",
            data=updated_salary_contract_dto
        )


user_management_salary_contract = UserManagementSalaryContract()