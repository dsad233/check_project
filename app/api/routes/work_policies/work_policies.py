import logging
from typing import Any, List, Union, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect
from pydantic import BaseModel
from app.common.dto.pagination_dto import PaginationDto
from app.common.dto.search_dto import BaseSearchDto
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

class CombinedPoliciesResponse(BaseModel):
    work_policies: Optional[WorkPoliciesDto] = None
    auto_overtime_policies: Optional[AutoOvertimePoliciesDto] = None
    holiday_work_policies: Optional[HolidayWorkPoliciesDto] = None
    overtime_policies: Optional[OverTimePoliciesDto] = None
    default_allowance_policies: Optional[DefaultAllowancePoliciesDto] = None
    holiday_allowance_policies: Optional[HolidayAllowancePoliciesDto] = None

class CombinedPoliciesRequest(BaseModel):
    work_policies: Optional[WorkPoliciesDto] = None
    auto_overtime_policies: Optional[AutoOvertimePoliciesDto] = None
    holiday_work_policies: Optional[HolidayWorkPoliciesDto] = None
    overtime_policies: Optional[OverTimePoliciesDto] = None
    default_allowance_policies: Optional[DefaultAllowancePoliciesDto] = None
    holiday_allowance_policies: Optional[HolidayAllowancePoliciesDto] = None


@router.get("/get", response_model=CombinedPoliciesResponse)
async def get_work_policies(*,
    session: AsyncSession = Depends(get_db),
    branch_id: int
) -> CombinedPoliciesResponse:
    
    try:
        work_policies = await work_crud.get_work_policies(session=session, branch_id=branch_id)
        auto_overtime_policies = await auto_overtime_crud.get_auto_overtime_policies(session=session, branch_id=branch_id)
        holiday_work_policies = await holiday_work_crud.get_holiday_work_policies(session=session, branch_id=branch_id)
        overtime_policies = await overtime_crud.get_overtime_policies(session=session, branch_id=branch_id)
        allowance_policies = await allowance_crud.get_allowance_policies(session=session, branch_id=branch_id)

        # SQLAlchemy 모델을 Pydantic 모델로 변환
        work_policies_dto = WorkPoliciesDto.model_validate(work_policies or {})
        auto_overtime_policies_dto = AutoOvertimePoliciesDto.model_validate(auto_overtime_policies or {})
        holiday_work_policies_dto = HolidayWorkPoliciesDto.model_validate(holiday_work_policies or {})
        overtime_policies_dto = OverTimePoliciesDto.model_validate(overtime_policies or {})
        default_allowance_policies_dto = DefaultAllowancePoliciesDto.model_validate(allowance_policies or {})
        holiday_allowance_policies_dto = HolidayAllowancePoliciesDto.model_validate(allowance_policies or {})

        return CombinedPoliciesResponse(work_policies=work_policies_dto,
                                        auto_overtime_policies=auto_overtime_policies_dto,
                                        holiday_work_policies=holiday_work_policies_dto,
                                        overtime_policies=overtime_policies_dto,
                                        default_allowance_policies=default_allowance_policies_dto,
                                        holiday_allowance_policies=holiday_allowance_policies_dto)
    except Exception as e:
        logger.error(f"Error occurred while reading work policies: {e}")
        raise HTTPException(status_code=404, detail=f"Error occurred while reading work policies: {e}")

@router.patch("/update", response_model=str)
async def update_work_policies(*,
    session: AsyncSession = Depends(get_db),
    token: Annotated[Users, Depends(get_current_user)],
    branch_id: int,
    policies_in: CombinedPoliciesRequest
) -> str:
    try:
        allowed_roles = ["MSO 최고권한", "최고관리자", "통합관리자"]
        if token.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")
        
        if work_crud.get_work_policies(session=session, branch_id=branch_id) is None:
            await work_crud.create_work_policies_by_value(session=session, branch_id=branch_id, work_policies_update=policies_in.work_policies)
        else:
            await work_crud.update_work_policies(session=session, branch_id=branch_id, work_policies_update=policies_in.work_policies)
        if auto_overtime_crud.get_auto_overtime_policies(session=session, branch_id=branch_id) is None:
            await auto_overtime_crud.create_auto_overtime_policies_by_value(session=session, branch_id=branch_id, auto_overtime_policies_update=policies_in.auto_overtime_policies)
        else:
            await auto_overtime_crud.update_auto_overtime_policies(session=session, branch_id=branch_id, auto_overtime_policies_update=policies_in.auto_overtime_policies)
        if holiday_work_crud.get_holiday_work_policies(session=session, branch_id=branch_id) is None:
            await holiday_work_crud.create_holiday_work_policies_by_value(session=session, branch_id=branch_id, holiday_work_policies_update=policies_in.holiday_work_policies)
        else:
            await holiday_work_crud.update_holiday_work_policies(session=session, branch_id=branch_id, holiday_work_policies_update=policies_in.holiday_work_policies)
        if overtime_crud.get_overtime_policies(session=session, branch_id=branch_id) is None:
            await overtime_crud.create_overtime_policies_by_value(session=session, branch_id=branch_id, overtime_policies_update=policies_in.overtime_policies  )
        else:
            await overtime_crud.update_overtime_policies(session=session, branch_id=branch_id, overtime_policies_update=policies_in.overtime_policies)
        if allowance_crud.get_allowance_policies(session=session, branch_id=branch_id) is None:
            await allowance_crud.create_allowance_policies_by_value(session=session, branch_id=branch_id, default_allowance_update=policies_in.default_allowance_policies, holiday_allowance_update=policies_in.holiday_allowance_policies)
        else:
            await allowance_crud.update_allowance_policies(session=session, branch_id=branch_id, default_allowance_update=policies_in.default_allowance_policies, holiday_allowance_update=policies_in.holiday_allowance_policies)

        return f"{branch_id} 번 지점의 근무정책 업데이트 완료"
    except Exception as e:
        logger.error(f"Error occurred while updating work policies: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while updating work policies: {e}")
