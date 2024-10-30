import logging
from typing import Any, List, Union, Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, inspect
from pydantic import BaseModel
from app.exceptions.exceptions import (
    BadRequestError,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
)
from app.core.database import get_db
from app.cruds.branches.policies import (
    allowance_crud,
    auto_overtime_crud,
    holiday_work_crud,
    overtime_crud,
    work_crud,
)
from app.middleware.tokenVerify import validate_token, get_current_user
from app.models.users.users_model import Users
from app.models.branches.allowance_policies_model import (
    AllowancePolicies,
    AllowancePoliciesDto,
    DefaultAllowancePoliciesDto,
    HolidayAllowancePoliciesDto,
)
from app.models.branches.auto_overtime_policies_model import (
    AutoOvertimePolicies,
    AutoOvertimePoliciesDto,
)
from app.models.branches.holiday_work_policies_model import (
    HolidayWorkPolicies,
    HolidayWorkPoliciesDto,
)
from app.models.branches.overtime_policies_model import (
    OverTimePolicies,
    OverTimePoliciesDto,
)
from app.models.branches.work_policies_model import (
    BreakTime,
    WorkPolicies,
    WorkPoliciesDto,
    WorkSchedule,
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
async def get_work_policies(
    *,
    session: AsyncSession = Depends(get_db),
    branch_id: int,
    user: Annotated[Users, Depends(get_current_user)],
) -> CombinedPoliciesDto:
    try:
        if user.role.strip() == "MSO 최고권한":
            pass
        elif user.role.strip() in ["최고관리자", "통합관리자", "파트관리자"]:
            if user.branch_id != branch_id:
                raise ForbiddenError(detail="다른 지점의 정보에 접근할 수 없습니다.")
        else:
            raise ForbiddenError(detail="권한이 없습니다.")

        work_policies = await work_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )
        auto_overtime_policies = await auto_overtime_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )
        holiday_work_policies = await holiday_work_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )
        overtime_policies = await overtime_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )
        allowance_policies = await allowance_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )

        return CombinedPoliciesDto(
            work_policies=WorkPoliciesDto.model_validate(work_policies or {}),
            auto_overtime_policies=AutoOvertimePoliciesDto.model_validate(
                auto_overtime_policies or {}
            ),
            holiday_work_policies=HolidayWorkPoliciesDto.model_validate(
                holiday_work_policies or {}
            ),
            overtime_policies=OverTimePoliciesDto.model_validate(
                overtime_policies or {}
            ),
            default_allowance_policies=DefaultAllowancePoliciesDto.model_validate(
                allowance_policies or {}
            ),
            holiday_allowance_policies=HolidayAllowancePoliciesDto.model_validate(
                allowance_policies or {}
            ),
        )
    except Exception as e:
        print(f"Error in get_work_policies: {e}")
        raise HTTPException(detail="근무정책 조회에 실패하였습니다.")


@router.patch("/update", response_model=str)
async def update_work_policies(
    *,
    session: AsyncSession = Depends(get_db),
    user: Annotated[Users, Depends(get_current_user)],
    branch_id: int,
    policies_in: CombinedPoliciesDto,
) -> str:
    try:
        if user.role.strip() == "MSO 최고권한":
            pass
        elif user.role.strip() in ["최고관리자", "통합관리자", "파트관리자"]:
            if user.branch_id != branch_id:
                raise ForbiddenError(detail="다른 지점의 정보에 접근할 수 없습니다.")
        else:
            raise ForbiddenError(detail="권한이 없습니다.")

        # WorkPolicies 업데이트
        work_policies = await work_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )
        if work_policies is None:
            # 새로운 정책 생성
            new_policy = WorkPolicies(
                branch_id=branch_id,
                weekly_work_days=policies_in.work_policies.weekly_work_days,
                deleted_yn="N",
            )
            session.add(new_policy)
            await session.flush()

            # 스케줄과 휴게시간 추가
            for schedule_dto in policies_in.work_policies.work_schedules:
                new_schedule = WorkSchedule(
                    work_policy_id=new_policy.id,
                    day_of_week=schedule_dto.day_of_week,
                    start_time=schedule_dto.start_time,
                    end_time=schedule_dto.end_time,
                    is_holiday=schedule_dto.is_holiday,
                )
                session.add(new_schedule)

            for break_dto in policies_in.work_policies.break_times:
                new_break = BreakTime(
                    work_policy_id=new_policy.id,
                    is_doctor=break_dto.is_doctor,
                    break_type=break_dto.break_type,
                    start_time=break_dto.start_time,
                    end_time=break_dto.end_time,
                )
                session.add(new_break)
        else:
            # 기존 정책 업데이트
            work_policies.weekly_work_days = policies_in.work_policies.weekly_work_days

            # 기존 스케줄과 휴게시간 삭제 후 새로 추가
            await session.execute(
                delete(WorkSchedule).where(
                    WorkSchedule.work_policy_id == work_policies.id
                )
            )
            await session.execute(
                delete(BreakTime).where(BreakTime.work_policy_id == work_policies.id)
            )

            for schedule_dto in policies_in.work_policies.work_schedules:
                new_schedule = WorkSchedule(
                    work_policy_id=work_policies.id,
                    day_of_week=schedule_dto.day_of_week,
                    start_time=schedule_dto.start_time,
                    end_time=schedule_dto.end_time,
                    is_holiday=schedule_dto.is_holiday,
                )
                session.add(new_schedule)

            for break_dto in policies_in.work_policies.break_times:
                new_break = BreakTime(
                    work_policy_id=work_policies.id,
                    is_doctor=break_dto.is_doctor,
                    break_type=break_dto.break_type,
                    start_time=break_dto.start_time,
                    end_time=break_dto.end_time,
                )
                session.add(new_break)

        # AutoOvertimePolicies 업데이트
        auto_overtime_policies = await auto_overtime_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )
        if auto_overtime_policies is None:
            await auto_overtime_crud.create(
                session=session,
                branch_id=branch_id,
                auto_overtime_policies_create=AutoOvertimePolicies(
                    branch_id=branch_id,
                    **policies_in.auto_overtime_policies.model_dump(),
                ),
            )
        else:
            await auto_overtime_crud.update(
                session=session,
                branch_id=branch_id,
                auto_overtime_policies_update=AutoOvertimePolicies(
                    branch_id=branch_id,
                    **policies_in.auto_overtime_policies.model_dump(exclude_unset=True),
                ),
            )

        # HolidayWorkPolicies 업데이트
        holiday_work_policies = await holiday_work_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )
        if holiday_work_policies is None:
            await holiday_work_crud.create(
                session=session,
                branch_id=branch_id,
                holiday_work_policies_create=HolidayWorkPolicies(
                    branch_id=branch_id,
                    **policies_in.holiday_work_policies.model_dump(),
                ),
            )
        else:
            await holiday_work_crud.update(
                session=session,
                branch_id=branch_id,
                holiday_work_policies_update=HolidayWorkPolicies(
                    branch_id=branch_id,
                    **policies_in.holiday_work_policies.model_dump(exclude_unset=True),
                ),
            )

        # OverTimePolicies 업데이트
        overtime_policies = await overtime_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )
        if overtime_policies is None:
            await overtime_crud.create(
                session=session,
                branch_id=branch_id,
                overtime_policies_create=OverTimePolicies(
                    branch_id=branch_id, **policies_in.overtime_policies.model_dump()
                ),
            )
        else:
            await overtime_crud.update(
                session=session,
                branch_id=branch_id,
                overtime_policies_update=OverTimePolicies(
                    branch_id=branch_id,
                    **policies_in.overtime_policies.model_dump(exclude_unset=True),
                ),
            )

        # AllowancePolicies 업데이트
        allowance_policies = await allowance_crud.find_by_branch_id(
            session=session, branch_id=branch_id
        )
        if allowance_policies is None:
            await allowance_crud.create(
                session=session,
                branch_id=branch_id,
                allowance_policies_create=AllowancePolicies(
                    branch_id=branch_id,
                    **policies_in.default_allowance_policies.model_dump(),
                    **policies_in.holiday_allowance_policies.model_dump(),
                ),
            )
        else:
            await allowance_crud.update(
                session=session,
                branch_id=branch_id,
                allowance_policies_update=AllowancePolicies(
                    branch_id=branch_id,
                    **policies_in.default_allowance_policies.model_dump(
                        exclude_unset=True
                    ),
                    **policies_in.holiday_allowance_policies.model_dump(
                        exclude_unset=True
                    ),
                ),
            )

        await session.commit()
        return f"{branch_id} 번 지점의 근무정책 업데이트 완료"

    except Exception as e:
        await session.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(
            status_code=500, detail="근무정책 업데이트에 실패하였습니다."
        )
