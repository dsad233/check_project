import logging
from typing import Any, List, Union, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect
from pydantic import BaseModel
from app.exceptions.exceptions import BadRequestError, NotFoundError, UnauthorizedError, ForbiddenError
from app.core.database import get_db
from app.cruds.branches.policies import allowance_crud, auto_overtime_crud, holiday_work_crud, overtime_crud, work_crud
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users
from app.models.branches.allowance_policies_model import (
    AllowancePolicies,AllowancePoliciesDto,DefaultAllowancePoliciesDto,HolidayAllowancePoliciesDto
)
from app.models.branches.auto_overtime_policies_model import (
    AutoOvertimePolicies,AutoOvertimePoliciesDto
)
from app.models.branches.holiday_work_policies_model import (
    HolidayWorkPolicies,HolidayWorkPoliciesDto
)
from app.models.branches.overtime_policies_model import (
    OverTimePolicies, OverTimePoliciesDto
)
from app.models.branches.work_policies_model import (
    WorkPolicies,WorkPoliciesDto
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(validate_token)])

class CombinedPoliciesDto(BaseModel):
    work_policies: WorkPoliciesDto
    auto_overtime_policies: AutoOvertimePoliciesDto
    holiday_work_policies: HolidayWorkPoliciesDto
    overtime_policies: OverTimePoliciesDto
    default_allowance_policies: DefaultAllowancePoliciesDto
    holiday_allowance_policies: HolidayAllowancePoliciesDto


@router.get("/get", response_model=CombinedPoliciesDto)
async def get_work_policies(*,
    session: AsyncSession = Depends(get_db),
    branch_id: int,
    user: Annotated[Users, Depends(get_current_user)]
) -> CombinedPoliciesDto:
    try:
        if user.role.strip() == "MSO 최고권한":
            pass
        elif user.role.strip() in ["최고관리자", "통합관리자", "파트관리자"]:
            if user.branch_id != branch_id:
                raise ForbiddenError(detail="다른 지점의 정보에 접근할 수 없습니다.")
        else:
            raise ForbiddenError(detail="권한이 없습니다.")
        
        work_policies = await work_crud.find_by_branch_id(session=session, branch_id=branch_id)
        auto_overtime_policies = await auto_overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
        holiday_work_policies = await holiday_work_crud.find_by_branch_id(session=session, branch_id=branch_id)
        overtime_policies = await overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
        allowance_policies = await allowance_crud.find_by_branch_id(session=session, branch_id=branch_id)

        return CombinedPoliciesDto(work_policies=WorkPoliciesDto.model_validate(work_policies or {}),
                                    auto_overtime_policies=AutoOvertimePoliciesDto.model_validate(auto_overtime_policies or {}),
                                    holiday_work_policies=HolidayWorkPoliciesDto.model_validate(holiday_work_policies or {}),
                                    overtime_policies=OverTimePoliciesDto.model_validate(overtime_policies or {}),
                                    default_allowance_policies=DefaultAllowancePoliciesDto.model_validate(allowance_policies or {}),
                                    holiday_allowance_policies=HolidayAllowancePoliciesDto.model_validate(allowance_policies or {}))
    except Exception as e:
        print(f"Error in get_work_policies: {e}")
        raise InternalServerError(detail="근무정책 조회에 실패하였습니다.")

@router.patch("/update", response_model=str)
async def update_work_policies(*,
    session: AsyncSession = Depends(get_db),
    user: Annotated[Users, Depends(get_current_user)],
    branch_id: int,
    policies_in: CombinedPoliciesDto
) -> str:
    
    if user.role.strip() == "MSO 최고권한":
        pass
    elif user.role.strip() in ["최고관리자", "통합관리자", "파트관리자"]:
        if user.branch_id != branch_id:
            raise ForbiddenError(detail="다른 지점의 정보에 접근할 수 없습니다.")
    else:
        raise ForbiddenError(detail="권한이 없습니다.")

    # WorkPolicies 업데이트
    work_policies = await work_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if work_policies is None:
        await work_crud.create(session=session, branch_id=branch_id, work_policies_update=WorkPolicies(branch_id=branch_id, **policies_in.work_policies.model_dump()))
    else:
        await work_crud.update(session=session, branch_id=branch_id, work_policies_update=WorkPolicies(branch_id=branch_id, **policies_in.work_policies.model_dump(exclude_unset=True)))

    # AutoOvertimePolicies 업데이트
    auto_overtime_policies = await auto_overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if auto_overtime_policies is None:
        await auto_overtime_crud.create(session=session, branch_id=branch_id, auto_overtime_policies_update=AutoOvertimePolicies(branch_id=branch_id, **policies_in.auto_overtime_policies.model_dump()))
    else:
        await auto_overtime_crud.update(session=session, branch_id=branch_id, auto_overtime_policies_update=AutoOvertimePolicies(branch_id=branch_id, **policies_in.auto_overtime_policies.model_dump(exclude_unset=True)))

    # HolidayWorkPolicies 업데이트
    holiday_work_policies = await holiday_work_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if holiday_work_policies is None:
        await holiday_work_crud.create(session=session, branch_id=branch_id, holiday_work_policies_update=HolidayWorkPolicies(branch_id=branch_id, **policies_in.holiday_work_policies.model_dump()))
    else:
        await holiday_work_crud.update(session=session, branch_id=branch_id, holiday_work_policies_update=HolidayWorkPolicies(branch_id=branch_id, **policies_in.holiday_work_policies.model_dump(exclude_unset=True)))

    # OverTimePolicies 업데이트
    overtime_policies = await overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if overtime_policies is None:
        await overtime_crud.create(session=session, branch_id=branch_id, overtime_policies_update=OverTimePolicies(branch_id=branch_id, **policies_in.overtime_policies.model_dump()))
    else:
        await overtime_crud.update(session=session, branch_id=branch_id, overtime_policies_update=OverTimePolicies(branch_id=branch_id, **policies_in.overtime_policies.model_dump(exclude_unset=True)))

    # AllowancePolicies 업데이트
    allowance_policies = await allowance_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if allowance_policies is None:
        await allowance_crud.create(session=session, branch_id=branch_id, allowance_policies_update=AllowancePolicies(branch_id=branch_id,
                                                                                                                    **policies_in.default_allowance_policies.model_dump(),
                                                                                                                    **policies_in.holiday_allowance_policies.model_dump()))
    else:
        await allowance_crud.update(session=session, branch_id=branch_id, allowance_policies_update=AllowancePolicies(branch_id=branch_id,
                                                                                                                    **policies_in.default_allowance_policies.model_dump(exclude_unset=True),
                                                                                                                    **policies_in.holiday_allowance_policies.model_dump(exclude_unset=True)))
    return f"{branch_id} 번 지점의 근무정책 업데이트 완료"