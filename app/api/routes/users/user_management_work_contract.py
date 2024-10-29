from fastapi import APIRouter, Depends

from app.common.dto.response_dto import ResponseDTO
from app.core.database import async_session
from app.cruds.user_management.users_work_contract_crud import find_work_contract_by_user_id, find_user_by_user_id, \
    find_work_contract_part_timer_by_user_id, create_work_contract_with_rest_days, \
    find_work_contract_by_work_contract_id, update_work_contract_with_rest_days
from app.exceptions.exceptions import BadRequestError
from app.middleware.tokenVerify import validate_token, get_current_user
from app.schemas.user_work_contract_schemas import RequestPatchWorkContract, RequestCreateWorkContract, \
    ResponseUserWorkContractDto, ResponseCreatedWorkContractDto, WorkContractDto
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
        try:
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
                message="사용자 근로 계약 정보가 조회되었습니다.",
                data=data,
            )
        except Exception as e:
            raise BadRequestError(str(e))


    @router.post("", response_model=ResponseDTO[ResponseCreatedWorkContractDto])
    async def create_user_management_work_contract(
        request_create_work_contract: RequestCreateWorkContract,
        current_user: dict = Depends(get_current_user)
    ):
        user_id = request_create_work_contract.user_id
        work_contract = await find_work_contract_by_user_id(session=db, user_id=user_id)

        if work_contract:
            work_contract_id = work_contract.id
            return ResponseDTO(
                status="FAILED",
                message="이미 근로계약이 존재합니다.",
                data=ResponseCreatedWorkContractDto.build(work_contract_id=work_contract_id)
            )

        request_create_work_contract_dict = request_create_work_contract.model_dump()
        request_fixed_rest_days = request_create_work_contract_dict.pop("fixed_rest_days")

        word_contract_id = await create_work_contract_with_rest_days(
            session=db,
            work_contract_dict=request_create_work_contract_dict,
            fixed_rest_days=request_fixed_rest_days,
        )

        data = ResponseCreatedWorkContractDto.build(work_contract_id=word_contract_id)

        return ResponseDTO(
            status="SUCCESS",
            message="성공적으로 근로계약이 생성되었습니다.",
            data=data,
        )


    @router.patch("", response_model=ResponseDTO[WorkContractDto])
    async def patch_user_management_work_contract(
        work_contract_id: int,
        request_patch_work_contract: RequestPatchWorkContract,
        current_user: dict = Depends(get_current_user)
    ):
        work_contract = await find_work_contract_by_work_contract_id(
            session=db,
            work_contract_id=work_contract_id
        )

        if not work_contract:
            return ResponseDTO.not_found(
                message="수정할 근로계약을 찾을 수 없습니다."
            )

        update_values = request_patch_work_contract.to_update_dict()

        if not update_values:
            return ResponseDTO(
                status="FAILED",
                message="수정할 데이터가 없습니다."
            )

        # 3. fixed_rest_days 분리
        fixed_rest_days = update_values.pop('fixed_rest_days', None)

        # 4. 트랜잭션 실행
        await update_work_contract_with_rest_days(
            session=db,
            work_contract_id=work_contract.id,
            update_values=update_values,
            fixed_rest_days=fixed_rest_days
        )

        updated_work_contract = await find_work_contract_by_work_contract_id(
            session=db,
            work_contract_id=work_contract_id
        )

        data = WorkContractDto.build(work_contract=updated_work_contract)

        return ResponseDTO(
            status="SUCCESS",
            message="근로계약이 성공적으로 수정되었습니다.",
            data=data
        )

user_management_work_contract = UserManagementWorkContract()