import logging
from typing import Any, List, Union, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import inspect
from pydantic import BaseModel
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
from app.core.database import get_db
from app.cruds.branches.policies import allowance_crud, auto_overtime_crud, holiday_work_crud, overtime_crud, work_crud
from app.middleware.tokenVerify import validate_token
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
# router = APIRouter()

class CombinedPoliciesResponse(BaseModel):
    work_policies: Optional[WorkPoliciesDto] = None
    auto_overtime_policies: Optional[AutoOvertimePoliciesDto] = None
    holiday_work_policies: Optional[HolidayWorkPoliciesDto] = None
    overtime_policies: Optional[OverTimePoliciesDto] = None
    default_allowance_policies: Optional[DefaultAllowancePoliciesDto] = None
    holiday_allowance_policies: Optional[HolidayAllowancePoliciesDto] = None

class CombinedPoliciesRequest(BaseModel):
    work_policies: WorkPoliciesDto
    auto_overtime_policies: AutoOvertimePoliciesDto
    holiday_work_policies: HolidayWorkPoliciesDto
    overtime_policies: OverTimePoliciesDto
    default_allowance_policies: DefaultAllowancePoliciesDto
    holiday_allowance_policies: HolidayAllowancePoliciesDto


@router.get("/", response_model=CombinedPoliciesResponse)
async def get_work_policies(*,
    session: AsyncSession = Depends(get_db),
    branch_id: int
) -> CombinedPoliciesResponse:
        work_policies = await work_crud.get_work_policies(session=session, branch_id=branch_id)
        auto_overtime_policies = await auto_overtime_crud.get_auto_overtime_policies(session=session, branch_id=branch_id)
        holiday_work_policies = await holiday_work_crud.get_holiday_work_policies(session=session, branch_id=branch_id)
        overtime_policies = await overtime_crud.get_overtime_policies(session=session, branch_id=branch_id)
        allowance_policies = await allowance_crud.get_allowance_policies(session=session, branch_id=branch_id)

        # SQLAlchemy 모델을 Pydantic 모델로 변환
        work_policies_dto = WorkPoliciesDto.model_validate(work_policies) if work_policies else None
        auto_overtime_policies_dto = AutoOvertimePoliciesDto.model_validate(auto_overtime_policies) if auto_overtime_policies else None
        holiday_work_policies_dto = HolidayWorkPoliciesDto.model_validate(holiday_work_policies) if holiday_work_policies else None
        overtime_policies_dto = OverTimePoliciesDto.model_validate(overtime_policies) if overtime_policies else None
        default_allowance_policies_dto = DefaultAllowancePoliciesDto.model_validate(allowance_policies) if allowance_policies else None
        holiday_allowance_policies_dto = HolidayAllowancePoliciesDto.model_validate(allowance_policies) if allowance_policies else None

        return CombinedPoliciesResponse(work_policies=work_policies_dto,
                                        auto_overtime_policies=auto_overtime_policies_dto,
                                        holiday_work_policies=holiday_work_policies_dto,
                                        overtime_policies=overtime_policies_dto,
                                        default_allowance_policies=default_allowance_policies_dto,
                                        holiday_allowance_policies=holiday_allowance_policies_dto)

@router.post("/", response_model=str)
async def update_work_policies(*,
    session: AsyncSession = Depends(get_db),
    branch_id: int,
    policies_in: CombinedPoliciesRequest
) -> str:
    
    await work_crud.update_work_policies(session=session, branch_id=branch_id, work_policies_update=policies_in.work_policies)
    await auto_overtime_crud.update_auto_overtime_policies(session=session, branch_id=branch_id, auto_overtime_policies_update=policies_in.auto_overtime_policies)
    await holiday_work_crud.update_holiday_work_policies(session=session, branch_id=branch_id, holiday_work_policies_update=policies_in.holiday_work_policies)
    await overtime_crud.update_overtime_policies(session=session, branch_id=branch_id, overtime_policies_update=policies_in.overtime_policies)
    await allowance_crud.update_allowance_policies(session=session, branch_id=branch_id, default_allowance_update=policies_in.default_allowance_policies, holiday_allowance_update=policies_in.holiday_allowance_policies)

    return f"{branch_id} 번 지점의 근무정책 업데이트 완료"