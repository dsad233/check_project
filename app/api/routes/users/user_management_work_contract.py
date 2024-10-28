from fastapi import APIRouter, Depends

from app.common.dto.response_dto import ResponseDTO
from app.core.database import async_session
from app.cruds.user_management.users_work_contract_crud import find_work_contract_by_user_id, find_user_by_user_id, \
    find_work_contract_part_timer_by_user_id, create_work_contract
from app.exceptions.exceptions import BadRequestError
from app.middleware.tokenVerify import validate_token, get_current_user
from app.schemas.user_work_contract_schemas import RequestPatchWorkContract, RequestCreateWorkContract, \
    ResponseUserWorkContractDto
from app.enums.users import EmploymentStatus

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


class UserManagementWorkContract:
    router = router

    @router.get("/{user_id}", response_model=ResponseDTO[ResponseUserWorkContractDto])
    async def get_user_management_work_contract(
        user_id: int,
        current_user: dict = Depends(get_current_user)
    ):
        user = await find_user_by_user_id(session=db, user_id=user_id)
        user_employment_status = user.employment_status

        if user_employment_status == EmploymentStatus.PERMANENT:
            work_contract = await find_work_contract_by_user_id(session=db, user_id=user_id)
        elif user_employment_status == EmploymentStatus.TEMPORARY:
            work_contract = await find_work_contract_part_timer_by_user_id(session=db, user_id=user_id)
        else:
            raise BadRequestError("Invalid User Employment Status")

        data = ResponseUserWorkContractDto.build(user=user, work_contract=work_contract)

        return ResponseDTO(
            status="SUCCESS",
            message="User Management Work Contract",
            data=data,
        )



    @router.post("")
    async def create_user_management_work_contract(
        request_create_work_contract: RequestCreateWorkContract,
        current_user: dict = Depends(get_current_user)
    ):
        request_create_work_contract_dict = request_create_work_contract.model_dump()
        word_contract_id = await create_work_contract(
            session=db,
            work_contract_dict=request_create_work_contract_dict,
        )




    @router.patch("")
    async def patch_user_management_work_contract(
        request_patch_work_contract: RequestPatchWorkContract,
        current_user: dict = Depends(get_current_user)
    ):
        return {"message": "Patch User Management Work Contract"}



user_management_work_contract = UserManagementWorkContract()