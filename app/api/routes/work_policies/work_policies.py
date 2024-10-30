import logging
from typing import Any, List, Union, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
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
    branch_id: int
) -> CombinedPoliciesDto:
        
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
    
    
@router.patch("/update", response_model=bool)
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_work_policies(*,
    session: AsyncSession = Depends(get_db),
    branch_id: int,
    request: CombinedPoliciesDto,
    context: Request
) -> bool:

    # WorkPolicies 업데이트
    work_policies = await work_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if work_policies is None:
        await work_crud.create(session=session, branch_id=branch_id, work_policies_create=WorkPolicies(branch_id=branch_id, **request.work_policies.model_dump()))
    else:
        await work_crud.update(session=session, branch_id=branch_id, work_policies_update=WorkPolicies(branch_id=branch_id, **request.work_policies.model_dump(exclude_unset=True)))

    # AutoOvertimePolicies 업데이트
    auto_overtime_policies = await auto_overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if auto_overtime_policies is None:
        await auto_overtime_crud.create(session=session, branch_id=branch_id, auto_overtime_policies_create=AutoOvertimePolicies(branch_id=branch_id, **request.auto_overtime_policies.model_dump()))
    else:
        await auto_overtime_crud.update(session=session, branch_id=branch_id, auto_overtime_policies_update=AutoOvertimePolicies(branch_id=branch_id, **request.auto_overtime_policies.model_dump(exclude_unset=True)))

    # HolidayWorkPolicies 업데이트
    holiday_work_policies = await holiday_work_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if holiday_work_policies is None:
        await holiday_work_crud.create(session=session, branch_id=branch_id, holiday_work_policies_create=HolidayWorkPolicies(branch_id=branch_id, **request.holiday_work_policies.model_dump()))
    else:
        await holiday_work_crud.update(session=session, branch_id=branch_id, holiday_work_policies_update=HolidayWorkPolicies(branch_id=branch_id, **request.holiday_work_policies.model_dump(exclude_unset=True)))

    # OverTimePolicies 업데이트
    overtime_policies = await overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if overtime_policies is None:
        await overtime_crud.create(session=session, branch_id=branch_id, overtime_policies_create=OverTimePolicies(branch_id=branch_id, **request.overtime_policies.model_dump()))
    else:
        await overtime_crud.update(session=session, branch_id=branch_id, overtime_policies_update=OverTimePolicies(branch_id=branch_id, **request.overtime_policies.model_dump(exclude_unset=True)))

    # AllowancePolicies 업데이트
    allowance_policies = await allowance_crud.find_by_branch_id(session=session, branch_id=branch_id)
    if allowance_policies is None:
        await allowance_crud.create(session=session, branch_id=branch_id, allowance_policies_create=AllowancePolicies(branch_id=branch_id,
                                                                                                                    **request.default_allowance_policies.model_dump(),
                                                                                                                    **request.holiday_allowance_policies.model_dump()))
    else:
        await allowance_crud.update(session=session, branch_id=branch_id, allowance_policies_update=AllowancePolicies(branch_id=branch_id,
                                                                                                                    **request.default_allowance_policies.model_dump(exclude_unset=True),
                                                                                                                    **request.holiday_allowance_policies.model_dump(exclude_unset=True)))
    return True