from fastapi import HTTPException
from app.cruds.branches.policies.salary_polices_crud import create_parttimer_policies
from app.models.branches.auto_annual_leave_approval_model import AutoAnnualLeaveApproval
from app.models.branches.account_based_annual_leave_grant_model import AccountBasedAnnualLeaveGrant
from app.models.branches.entry_date_based_annual_leave_grant_model import EntryDateBasedAnnualLeaveGrant
from app.models.branches.condition_based_annual_leave_grant_model import ConditionBasedAnnualLeaveGrant
from app.models.histories.branch_histories_model import BranchHistories
from app.models.branches.branches_model import Branches, PersonnelRecordCategory
from app.models.branches.work_policies_model import BranchBreakTime, WorkPolicies, BranchWorkSchedule
from app.schemas.branches_schemas import AllowancePoliciesResponse, ScheduleHolidayUpdateDto, WorkPoliciesDto, AutoOvertimePoliciesDto, HolidayWorkPoliciesDto, OverTimePoliciesDto, AllowancePoliciesDto
from app.models.branches.auto_overtime_policies_model import AutoOvertimePolicies
from app.models.branches.holiday_work_policies_model import HolidayWorkPolicies
from app.models.branches.overtime_policies_model import OverTimePolicies
from app.models.branches.allowance_policies_model import AllowancePolicies
from app.common.dto.search_dto import BaseSearchDto
from app.common.dto.pagination_dto import PaginationDto
from app.schemas.branches_schemas import (
    AutoLeavePoliciesAndPartsDto, AccountPoliciesWithParts, EntryDatePoliciesWithParts, 
    ConditionPoliciesWithParts, AutoAnnualLeaveApprovalDto, AccountBasedGrantDto, 
    EntryDateBasedGrantDto, ConditionBasedGrantDto, PartIdWithName, BranchHistoryResponse, 
    BranchHistoriesResponse, BranchListResponse, BranchResponse, BranchRequest, 
    CombinedPoliciesDto, WorkPoliciesDto, AutoOvertimePoliciesDto, 
    HolidayWorkPoliciesDto, OverTimePoliciesDto, DefaultAllowancePoliciesDto, 
    HolidayAllowancePoliciesDto, PersonnelRecordCategoryRequest, 
    PersonnelRecordCategoryResponse, PersonnelRecordCategoriesResponse
)
from app.cruds.leave_policies import auto_annual_leave_approval_crud, account_based_annual_leave_grant_crud, entry_date_based_annual_leave_grant_crud, condition_based_annual_leave_grant_crud
from app.cruds.branches.policies import allowance_crud, holiday_work_crud, overtime_crud, work_crud, auto_overtime_crud
from app.cruds.parts import parts_crud
from app.cruds.branches import branches_crud, branch_histories_crud
from app.service import parts_service
from app.enums.parts import PartAutoAnnualLeaveGrant
from app.enums.branches import BranchHistoryType
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.exceptions.exceptions import NotFoundError, BadRequestError
import logging


# logger 설정
logger = logging.getLogger(__name__)

async def get_auto_leave_policies_and_parts(*, session: AsyncSession, branch_id: int) -> AutoLeavePoliciesAndPartsDto:
    """자동 연차 부여 및 승인 정책 조회"""
    branch = await branches_crud.find_by_id_with_policies(session=session, branch_id=branch_id)
    if not branch :
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    auto_annual_leave_approval_policies = branch.auto_annual_leave_approval
    account_based_grant_policies = branch.account_based_annual_leave_grant
    entry_date_based_grant_policies = branch.entry_date_based_annual_leave_grant
    condition_based_grant_policies = branch.condition_based_annual_leave_grant

    # 파트 조회
    parts = await parts_crud.find_all_by_branch_id(session=session, branch_id=branch_id)
    account_parts = []
    entry_date_parts = []
    condition_parts = []
    manual_parts = []
    for part in parts:
        if part.auto_annual_leave_grant == PartAutoAnnualLeaveGrant.ACCOUNTING_BASED_GRANT:
            account_parts.append(part)
        elif part.auto_annual_leave_grant == PartAutoAnnualLeaveGrant.ENTRY_DATE_BASED_GRANT:
            entry_date_parts.append(part)
        elif part.auto_annual_leave_grant == PartAutoAnnualLeaveGrant.CONDITIONAL_GRANT:
            condition_parts.append(part)
        else:
            manual_parts.append(part)

    return AutoLeavePoliciesAndPartsDto(
        auto_approval_policies=AutoAnnualLeaveApprovalDto.model_validate(auto_annual_leave_approval_policies or {}),
        account_based_policies=AccountPoliciesWithParts(
            **AccountBasedGrantDto.model_validate(account_based_grant_policies or {}).model_dump(),
            part_ids=[PartIdWithName.model_validate(part) for part in (account_parts or [])]
        ),
        entry_date_based_policies=EntryDatePoliciesWithParts(
            **EntryDateBasedGrantDto.model_validate(entry_date_based_grant_policies or {}).model_dump(),
            part_ids=[PartIdWithName.model_validate(part) for part in (entry_date_parts or [])]
        ),
        condition_based_policies=ConditionPoliciesWithParts(
            condition_based_grant=[ConditionBasedGrantDto.model_validate(condition_based_grant) for condition_based_grant in condition_based_grant_policies] if condition_based_grant_policies else [ConditionBasedGrantDto()],
            part_ids=[PartIdWithName.model_validate(part) for part in (condition_parts or [])]
        ),
        manual_based_parts=[PartIdWithName.model_validate(part) for part in (manual_parts or [])]
    )
        
    

async def update_auto_leave_policies_and_parts(
        *, 
        session: AsyncSession, 
        branch_id: int, 
        request: AutoLeavePoliciesAndPartsDto, 
        current_user_id: int
) -> bool:
    """자동 연차 부여 및 승인 정책 수정, 히스토리 생성"""
    branch = await branches_crud.find_by_id_with_policies(session=session, branch_id=branch_id)
    if not branch:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    auto_annual_leave_approval_policies = branch.auto_annual_leave_approval
    account_based_grant_policies = branch.account_based_annual_leave_grant
    entry_date_based_grant_policies = branch.entry_date_based_annual_leave_grant
    condition_based_grant_policies = branch.condition_based_annual_leave_grant

    # 자동 승인 정책 업데이트
    if not auto_annual_leave_approval_policies:
        await auto_annual_leave_approval_crud.create(
            session=session, 
            branch_id=branch_id, 
            request=AutoAnnualLeaveApproval(branch_id=branch_id, **request.auto_approval_policies.model_dump())
        )
    else:
        await auto_annual_leave_approval_crud.update(
            session=session, 
            branch_id=branch_id, 
            request=AutoAnnualLeaveApproval(branch_id=branch_id, **request.auto_approval_policies.model_dump(exclude_unset=True)),
            old=auto_annual_leave_approval_policies
        )

    # 회계 부여 정책 업데이트
    if not account_based_grant_policies:
        await account_based_annual_leave_grant_crud.create(
            session=session, 
            branch_id=branch_id, 
            request=AccountBasedAnnualLeaveGrant(branch_id=branch_id, **request.account_based_policies.model_dump(exclude={'part_ids'}))
        )
    else:
        await account_based_annual_leave_grant_crud.update(
            session=session, 
            branch_id=branch_id, 
            request=AccountBasedAnnualLeaveGrant(branch_id=branch_id, **request.account_based_policies.model_dump(exclude={'part_ids'})),
            old=account_based_grant_policies
        )

    # 입사일 부여 정책 업데이트
    if not entry_date_based_grant_policies:
        await entry_date_based_annual_leave_grant_crud.create(
            session=session, 
            branch_id=branch_id, 
            request=EntryDateBasedAnnualLeaveGrant(branch_id=branch_id, **request.entry_date_based_policies.model_dump(exclude={'part_ids'}))
        )
    else:
        await entry_date_based_annual_leave_grant_crud.update(
            session=session, 
            branch_id=branch_id, 
            request=EntryDateBasedAnnualLeaveGrant(branch_id=branch_id, **request.entry_date_based_policies.model_dump(exclude={'part_ids'})),
            old=entry_date_based_grant_policies
        )

    # 조건 부여 정책 업데이트
    existing_ids = {policy.id for policy in condition_based_grant_policies}
    request_ids = {
        policy.id for policy in request.condition_based_policies.condition_based_grant 
        if policy.id is not None
    }
    
    # 삭제할 ID 추출
    ids_to_delete = existing_ids - request_ids
    
    # 삭제 처리
    if ids_to_delete:
        await condition_based_annual_leave_grant_crud.delete_all_id(
            session=session,
            branch_id=branch_id,
            ids=ids_to_delete
        )

    # 기존 정책 딕셔너리 생성
    existing_dict = {policy.id: policy for policy in condition_based_grant_policies}
    
    # 업데이트 및 생성
    for new_policy in request.condition_based_policies.condition_based_grant:
        if new_policy.id is None:
            # 새로운 정책 생성
            await condition_based_annual_leave_grant_crud.create(
                session=session,
                branch_id=branch_id,
                request=ConditionBasedAnnualLeaveGrant(
                    branch_id=branch_id,
                    **new_policy.model_dump()
                )
            )
        else:
            # 기존 정책 업데이트
            old_policy = existing_dict.get(new_policy.id)
            if old_policy:
                await condition_based_annual_leave_grant_crud.update(
                    session=session,
                    branch_id=branch_id,
                    request=ConditionBasedAnnualLeaveGrant(
                        branch_id=branch_id,
                        **new_policy.model_dump(exclude_unset=True)
                    ),
                    old=old_policy
                )
    
    # 파트 auto_annual_leave_grant 업데이트
    all_parts = (
        request.account_based_policies.part_ids +
        request.entry_date_based_policies.part_ids +
        request.condition_based_policies.part_ids +
        request.manual_based_parts
    )

    for part in all_parts:
        if part in request.account_based_policies.part_ids:
            grant_type = PartAutoAnnualLeaveGrant.ACCOUNTING_BASED_GRANT
        elif part in request.entry_date_based_policies.part_ids:
            grant_type = PartAutoAnnualLeaveGrant.ENTRY_DATE_BASED_GRANT
        elif part in request.condition_based_policies.part_ids:
            grant_type = PartAutoAnnualLeaveGrant.CONDITIONAL_GRANT
        else:
            grant_type = PartAutoAnnualLeaveGrant.MANUAL_GRANT

        await parts_service.update_auto_annual_leave_grant(
            session=session,
            part_id=part.id,
            request=grant_type
        )

    history = await get_auto_leave_policies_and_parts(session=session, branch_id=branch_id)
    snapshot_id = datetime.now().strftime('%Y%m%d%H%M%S')
    await branch_histories_crud.create_branch_history(
        session=session, 
        branch_id=branch_id, 
        request=BranchHistories(
            branch_id=branch_id, 
            created_by=current_user_id, 
            snapshot_id=snapshot_id, 
            history=history.model_dump(), 
            history_type=BranchHistoryType.AUTO_ANNUAL_LEAVE_GRANT
        )
    )
        
    return True


async def get_branch_histories(*, session: AsyncSession, branch_id: int, request: BaseSearchDto, history_type: BranchHistoryType) -> BranchHistoriesResponse:
    """지점 히스토리 조회"""
    branch_histories = await branch_histories_crud.get_branch_histories(session=session, branch_id=branch_id, request=request, history_type=history_type)
    total_count = await branch_histories_crud.get_total_cnt(session=session, branch_id=branch_id, history_type=history_type)
    return BranchHistoriesResponse(data=branch_histories, pagination=PaginationDto(total_record=total_count))


async def get_branches(*, session: AsyncSession, request: BaseSearchDto) -> BranchListResponse:
    """지점 조회"""
    count = await branches_crud.count_non_deleted_all(session=session)
    if request.page == 0:
        branches = await branches_crud.find_all(session=session)
        pagination = PaginationDto(total_record=count, record_size=count)
    else:
        branches = await branches_crud.find_all_by_limit(session=session, request=request)
        pagination = PaginationDto(total_record=count)
    if branches is None:
        branches = []
    return BranchListResponse(data=branches, pagination=pagination)


async def create_branch(
        *, 
        session: AsyncSession, 
        request: BranchRequest
) -> bool:
    """지점 + 정책 생성"""
    duplicate_branch = await branches_crud.find_by_name(session=session, name=request.name)
    if duplicate_branch is not None:
        raise BadRequestError(detail=f"{request.name}은(는) 이미 존재합니다.")
    
    branch = await branches_crud.create(session=session, request=Branches(**request.model_dump()))
    branch_id = branch.id
    # 정책 생성
    if branch_id is not None:
        await account_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id)
        await allowance_crud.create(session=session, branch_id=branch_id)
        await auto_annual_leave_approval_crud.create(session=session, branch_id=branch_id)
        await auto_overtime_crud.create(session=session, branch_id=branch_id)
        await condition_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id)
        await entry_date_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id)
        await holiday_work_crud.create(session=session, branch_id=branch_id)
        await overtime_crud.create(session=session, branch_id=branch_id)
        await create_parttimer_policies(session=session, branch_id=branch_id)
        await work_crud.create(session=session, branch_id=branch_id)
        return True
    
    return False


async def revive_branch(*, session: AsyncSession, branch_id: int) -> bool:
    """삭제된 지점 복구"""
    branch = await branches_crud.find_deleted_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    return await branches_crud.revive(session=session, branch_id=branch_id)


async def get_deleted_branches(*, session: AsyncSession, request: BaseSearchDto) -> BranchListResponse:
    """삭제된 지점 조회"""
    count = await branches_crud.count_deleted_all(session=session)
    pagination = PaginationDto(total_record=count)
    branches = await branches_crud.find_deleted_all(
        session=session, request=request
    )
    if branches is None:
        branches = []
    return BranchListResponse(data=branches, pagination=pagination)


async def delete_branch(*, session: AsyncSession, branch_id: int) -> bool:
    """지점 삭제"""
    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    return await branches_crud.delete(session=session, branch_id=branch_id)


async def update_branch(*, session: AsyncSession, branch_id: int, request: BranchRequest) -> bool:
    """지점 수정"""
    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    
    if branch.name != request.name:
        duplicate_branch = await branches_crud.find_by_name(session=session, name=request.name)
        if duplicate_branch is not None:
            raise BadRequestError(detail=f"{request.name}은(는) 이미 존재합니다.")
    
    return await branches_crud.update(session=session, branch_id=branch_id, request=Branches(**request.model_dump()), old=branch)


async def get_branch_by_id(*, session: AsyncSession, branch_id: int) -> Branches:
    """지점 조회"""
    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    return branch


async def get_branch_policies(*, session: AsyncSession, branch_id: int) -> CombinedPoliciesDto:
    """지점 정책 조회"""
    branch = await branches_crud.find_by_id_with_policies(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    work_policies = branch.work_policies
    auto_overtime_policies = branch.auto_overtime_policies
    holiday_work_policies = branch.holiday_work_policies
    overtime_policies = branch.overtime_policies
    allowance_policies = branch.allowance_policies

    return CombinedPoliciesDto(
        work_policies=WorkPoliciesDto.model_validate(
            work_policies or WorkPoliciesDto(
                weekly_work_days=5,
                work_schedules=work_crud.generate_work_schedules(),
                break_times=work_crud.generate_break_times()
            )),
        auto_overtime_policies=AutoOvertimePoliciesDto.model_validate(auto_overtime_policies or {}),
        holiday_work_policies=HolidayWorkPoliciesDto.model_validate(holiday_work_policies or {}),
        overtime_policies=OverTimePoliciesDto.model_validate(overtime_policies or {}),
        default_allowance_policies=DefaultAllowancePoliciesDto.model_validate(allowance_policies or {}),
        holiday_allowance_policies=HolidayAllowancePoliciesDto.model_validate(allowance_policies or {})
    )


async def update_branch_policies(*, session: AsyncSession, branch_id: int, request: CombinedPoliciesDto) -> bool:
    """지점 정책 수정"""
    branch = await branches_crud.find_by_id_with_policies(session=session, branch_id=branch_id)
    if branch is None:
        raise NotFoundError(detail=f"{branch_id}번 지점이 없습니다.")
    # WorkPolicies 업데이트
    work_policies = branch.work_policies
    if work_policies is None:
        await work_crud.create(
            session=session, 
            branch_id=branch_id, 
            request=request.work_policies
        )
    else:
        await work_crud.update(
            session=session,
            branch_id=branch_id,
            request=request.work_policies,
            old=work_policies
        )

    # AutoOvertimePolicies 업데이트
    auto_overtime_policies = branch.auto_overtime_policies
    if auto_overtime_policies is None:
        await auto_overtime_crud.create(
            session=session, 
            branch_id=branch_id, 
            request=AutoOvertimePolicies(
                branch_id=branch_id, 
                **request.auto_overtime_policies.model_dump()
            )
        )
    else:
        await auto_overtime_crud.update(
            session=session, 
            branch_id=branch_id, 
            request=AutoOvertimePolicies(
                branch_id=branch_id, 
                **request.auto_overtime_policies.model_dump(exclude_unset=True)
            ),
            old=auto_overtime_policies
        )

    # HolidayWorkPolicies 업데이트
    holiday_work_policies = branch.holiday_work_policies
    if holiday_work_policies is None:
        await holiday_work_crud.create(
            session=session, 
            branch_id=branch_id, 
            request=HolidayWorkPolicies(
                branch_id=branch_id, 
                **request.holiday_work_policies.model_dump()
            )
        )
    else:
        await holiday_work_crud.update(
            session=session, 
            branch_id=branch_id, 
            request=HolidayWorkPolicies(
                branch_id=branch_id, 
                **request.holiday_work_policies.model_dump(exclude_unset=True)
            ),
            old=holiday_work_policies
        )

    # OverTimePolicies 업데이트
    overtime_policies = branch.overtime_policies
    if overtime_policies is None:
        await overtime_crud.create(
            session=session, 
            branch_id=branch_id, 
            request=OverTimePolicies(
                branch_id=branch_id, 
                **request.overtime_policies.model_dump()
            )
        )
    else:
        await overtime_crud.update(
            session=session, 
            branch_id=branch_id, 
            request=OverTimePolicies(
                branch_id=branch_id, 
                **request.overtime_policies.model_dump(exclude_unset=True)
            ),
            old=overtime_policies
        )

    # AllowancePolicies 업데이트
    allowance_policies = branch.allowance_policies
    if allowance_policies is None:
        await allowance_crud.create(
            session=session, 
            branch_id=branch_id, 
            request=AllowancePolicies(
                branch_id=branch_id, 
                **request.default_allowance_policies.model_dump(),
                **request.holiday_allowance_policies.model_dump()
            )
        )
    else:
        await allowance_crud.update(
            session=session, 
            branch_id=branch_id, 
            request=AllowancePolicies(
                branch_id=branch_id, 
                **request.default_allowance_policies.model_dump(exclude_unset=True),
                **request.holiday_allowance_policies.model_dump(exclude_unset=True)
            ),
            old=allowance_policies  # old 매개변수 추가
        )

    await session.commit()
    return True


# 근무 캘린더에서 고정 휴점일을 변경할 때 사용
async def update_schedule_holiday(*, session: AsyncSession, branch_id: int, request: ScheduleHolidayUpdateDto) -> str:
    """지점의 고정 휴무일 수정"""
    try:
        # 지점의 근무 정책 조회
        work_policies = await work_crud.find_by_branch_id(session=session, branch_id=branch_id)
        if work_policies is None:
            raise NotFoundError(detail=f"{branch_id}번 지점의 근무정책이 없습니다.")
        
        # 스케줄 업데이트
        await work_crud.update_schedule_holiday(
            session=session,
            branch_id=branch_id,
            work_policies_update=request.work_policies
        )

        await session.commit()
        return f"{branch_id}번 지점의 고정 휴무일 업데이트 완료"

    except NotFoundError as e:
        raise e

    except Exception as e:
        await session.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="고정 휴무일 업데이트에 실패하였습니다."
        )
    
    
# 자동 연차 부여 스케줄링
async def auto_annual_leave_grant_scheduling(*, session: AsyncSession):
    branches = await branches_crud.find_all_with_parts_users_auto_annual_leave_policies(session=session)
    for branch in branches:
        for part in branch.parts:
            # TODO: 유저마다 주 근무일수 다른거 분기 처리 해야함 지금은 5일로 고정
            if part.auto_annual_leave_grant == PartAutoAnnualLeaveGrant.MANUAL_GRANT:
                continue
            elif part.auto_annual_leave_grant == PartAutoAnnualLeaveGrant.ACCOUNTING_BASED_GRANT:
                await parts_service.account_based_auto_annual_leave_grant(session=session, part=part, branch=branch)
            elif part.auto_annual_leave_grant == PartAutoAnnualLeaveGrant.ENTRY_DATE_BASED_GRANT:
                await parts_service.entry_date_based_auto_annual_leave_grant(session=session, part=part, branch=branch)
            elif part.auto_annual_leave_grant == PartAutoAnnualLeaveGrant.CONDITIONAL_GRANT:
                await parts_service.condition_based_auto_annual_leave_grant(session=session, part=part, branch=branch)


async def create_personnel_record_category(
        *, session: AsyncSession, branch_id: int, request: PersonnelRecordCategoryRequest
) -> PersonnelRecordCategoryResponse:
    """지점 인사기록 카테고리 생성"""
    duplicate_category = await branches_crud.get_personnel_record_category_by_name(session=session, name=request.name, branch_id=branch_id)
    if duplicate_category is not None:
        raise BadRequestError(detail=f"{request.name}은(는) 이미 존재합니다.")
    return await branches_crud.create_personnel_record_category(session=session, request=PersonnelRecordCategory(branch_id=branch_id, **request.model_dump()))


async def get_personnel_record_categories(
        *, session: AsyncSession, branch_id: int, request: BaseSearchDto
) -> PersonnelRecordCategoriesResponse:
    """지점 인사기록 카테고리 조회"""
    personnel_record_categories = await branches_crud.get_personnel_record_categories(session=session, branch_id=branch_id, request=request)
    total_cnt = await branches_crud.get_personnel_record_categories_total_cnt(session=session, branch_id=branch_id)
    if total_cnt == 0:
        personnel_record_categories = []
    return PersonnelRecordCategoriesResponse(data=personnel_record_categories, pagination=PaginationDto(total_record=total_cnt))


async def update_personnel_record_category(
        *, session: AsyncSession, branch_id: int, personnel_record_category_id: int, request: PersonnelRecordCategoryRequest
) -> bool:
    """지점 인사기록 카테고리 수정"""
    personnel_record_category = await branches_crud.get_personnel_record_category(session=session, id=personnel_record_category_id)
    if personnel_record_category is None:
        raise NotFoundError(detail=f"{personnel_record_category_id}번 인사기록 카테고리가 없습니다.")
    await branches_crud.update_personnel_record_category(session=session, old=personnel_record_category, request=request.model_dump(exclude_unset=True))

    return True


async def delete_personnel_record_category(*, session: AsyncSession, branch_id: int, personnel_record_category_id: int) -> bool:
    """지점 인사기록 카테고리 삭제"""
    personnel_record_category = await branches_crud.get_personnel_record_category(session=session, id=personnel_record_category_id)
    if personnel_record_category is None:
        raise NotFoundError(detail=f"{personnel_record_category_id}번 인사기록 카테고리가 없습니다.")
    await branches_crud.delete_personnel_record_category(session=session, id=personnel_record_category_id)

    return True
