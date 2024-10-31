import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends, Request
from app.core.permissions.auth_utils import available_higher_than
from app.enums.users import Role
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.branches_schemas import (
    CombinedPoliciesDto,
    CombinedPoliciesUpdateDto,
)
from app.service import branch_service
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/get", response_model=CombinedPoliciesDto, summary="근무정책 조회")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def get_work_policies(
    *,
    context: Request,
    session: AsyncSession = Depends(get_db),
    branch_id: int, 
) -> CombinedPoliciesDto:

    return await branch_service.get_branch_policies(session=session, branch_id=branch_id)


@router.patch("/update", response_model=str, summary="근무정책 수정")
@available_higher_than(Role.INTEGRATED_ADMIN)
async def update_work_policies(
    *,
    context: Request,
    session: AsyncSession = Depends(get_db),
    branch_id: int,
    policies_in: CombinedPoliciesUpdateDto,
) -> str:
    
    return await branch_service.update_branch_policies(session=session, branch_id=branch_id, request=policies_in)
    
    
    # try:
    #     # WorkPolicies 업데이트
    #     work_policies = await work_crud.find_by_branch_id(
    #         session=session, branch_id=branch_id
    #     )
    #     if work_policies is None:
    #         new_policy = WorkPolicies(
    #             branch_id=branch_id,
    #             weekly_work_days=policies_in.work_policies.weekly_work_days,
    #             deleted_yn="N",
    #         )
    #         session.add(new_policy)
    #         await session.flush()

    #         for schedule_dto in policies_in.work_policies.work_schedules:
    #             new_schedule = WorkSchedule(
    #                 work_policy_id=new_policy.id,
    #                 day_of_week=schedule_dto.day_of_week,
    #                 start_time=schedule_dto.start_time,
    #                 end_time=schedule_dto.end_time,
    #                 is_holiday=schedule_dto.is_holiday,
    #             )
    #             new_policy.work_schedules.append(new_schedule)

    #         for break_dto in policies_in.work_policies.break_times:
    #             new_break = BreakTime(
    #                 work_policy_id=new_policy.id,
    #                 is_doctor=break_dto.is_doctor,
    #                 break_type=break_dto.break_type,
    #                 start_time=break_dto.start_time,
    #                 end_time=break_dto.end_time,
    #             )
    #             new_policy.break_times.append(new_break)
    #     else:
    #         update_policy = WorkPolicies(
    #             branch_id=branch_id,
    #             weekly_work_days=policies_in.work_policies.weekly_work_days,
    #         )

    #         update_policy.work_schedules = [
    #             WorkSchedule(
    #                 day_of_week=s.day_of_week,
    #                 start_time=s.start_time,
    #                 end_time=s.end_time,
    #                 is_holiday=s.is_holiday,
    #             )
    #             for s in policies_in.work_policies.work_schedules
    #         ]

    #         update_policy.break_times = [
    #             BreakTime(
    #                 is_doctor=b.is_doctor,
    #                 break_type=b.break_type,
    #                 start_time=b.start_time,
    #                 end_time=b.end_time,
    #             )
    #             for b in policies_in.work_policies.break_times
    #         ]

    #         await work_crud.update(
    #             session=session, branch_id=branch_id, work_policies_update=update_policy
    #         )

    #     # AutoOvertimePolicies 업데이트
    #     auto_overtime_policies = await auto_overtime_crud.find_by_branch_id(
    #         session=session, branch_id=branch_id
    #     )
    #     if auto_overtime_policies is None:
    #         await auto_overtime_crud.create(
    #             session=session,
    #             branch_id=branch_id,
    #             auto_overtime_policies_create=AutoOvertimePolicies(
    #                 branch_id=branch_id,
    #                 **policies_in.auto_overtime_policies.model_dump(),
    #             ),
    #         )
    #     else:
    #         await auto_overtime_crud.update(
    #             session=session,
    #             branch_id=branch_id,
    #             auto_overtime_policies_update=AutoOvertimePolicies(
    #                 branch_id=branch_id,
    #                 **policies_in.auto_overtime_policies.model_dump(exclude_unset=True),
    #             ),
    #         )

    #     # HolidayWorkPolicies 업데이트
    #     holiday_work_policies = await holiday_work_crud.find_by_branch_id(
    #         session=session, branch_id=branch_id
    #     )
    #     if holiday_work_policies is None:
    #         await holiday_work_crud.create(
    #             session=session,
    #             branch_id=branch_id,
    #             holiday_work_policies_create=HolidayWorkPolicies(
    #                 branch_id=branch_id,
    #                 **policies_in.holiday_work_policies.model_dump(),
    #             ),
    #         )
    #     else:
    #         await holiday_work_crud.update(
    #             session=session,
    #             branch_id=branch_id,
    #             holiday_work_policies_update=HolidayWorkPolicies(
    #                 branch_id=branch_id,
    #                 **policies_in.holiday_work_policies.model_dump(exclude_unset=True),
    #             ),
    #         )

    #     # OverTimePolicies 업데이트
    #     overtime_policies = await overtime_crud.find_by_branch_id(
    #         session=session, branch_id=branch_id
    #     )
    #     if overtime_policies is None:
    #         await overtime_crud.create(
    #             session=session,
    #             branch_id=branch_id,
    #             overtime_policies_create=OverTimePolicies(
    #                 branch_id=branch_id, **policies_in.overtime_policies.model_dump()
    #             ),
    #         )
    #     else:
    #         await overtime_crud.update(
    #             session=session,
    #             branch_id=branch_id,
    #             overtime_policies_update=OverTimePolicies(
    #                 branch_id=branch_id,
    #                 **policies_in.overtime_policies.model_dump(exclude_unset=True),
    #             ),
    #         )

    #     # AllowancePolicies 업데이트
    #     allowance_policies = await allowance_crud.find_by_branch_id(
    #         session=session, branch_id=branch_id
    #     )
    #     if allowance_policies is None:
    #         await allowance_crud.create(
    #             session=session,
    #             branch_id=branch_id,
    #             allowance_policies_create=AllowancePolicies(
    #                 branch_id=branch_id,
    #                 **policies_in.default_allowance_policies.model_dump(),
    #                 **policies_in.holiday_allowance_policies.model_dump(),
    #             ),
    #         )
    #     else:
    #         await allowance_crud.update(
    #             session=session,
    #             branch_id=branch_id,
    #             allowance_policies_update=AllowancePolicies(
    #                 branch_id=branch_id,
    #                 **policies_in.default_allowance_policies.model_dump(
    #                     exclude_unset=True
    #                 ),
    #                 **policies_in.holiday_allowance_policies.model_dump(
    #                     exclude_unset=True
    #                 ),
    #             ),
    #         )

    #     await session.commit()
    #     return f"{branch_id} 번 지점의 근무정책 업데이트 완료"

    # except Exception as e:
    #     await session.rollback()
    #     logger.error(f"Database error occurred: {str(e)}")
    #     raise HTTPException(
    #         status_code=500, detail="근무정책 업데이트에 실패하였습니다."
    #     )
