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
    auto_annual_leave_approval_policies: AutoAnnualLeaveApproval = await auto_annual_leave_approval_crud.find_by_branch_id(session=session, branch_id=branch_id)
    account_based_grant_policies: AccountBasedAnnualLeaveGrant = await account_based_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)
    entry_date_based_grant_policies: EntryDateBasedAnnualLeaveGrant = await entry_date_based_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)
    condition_based_grant_policies: list[ConditionBasedAnnualLeaveGrant] = await condition_based_annual_leave_grant_crud.find_all_by_branch_id(session=session, branch_id=branch_id)

    # 파트 조회
    account_parts = await parts_crud.find_all_by_auto_annual_leave_grant(session=session, request=PartAutoAnnualLeaveGrant.ACCOUNTING_BASED_GRANT)
    entry_date_parts = await parts_crud.find_all_by_auto_annual_leave_grant(session=session, request=PartAutoAnnualLeaveGrant.ENTRY_DATE_BASED_GRANT)
    condition_parts = await parts_crud.find_all_by_auto_annual_leave_grant(session=session, request=PartAutoAnnualLeaveGrant.CONDITIONAL_GRANT)
    manual_parts = await parts_crud.find_all_by_auto_annual_leave_grant(session=session, request=PartAutoAnnualLeaveGrant.MANUAL_GRANT)

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
    auto_annual_leave_approval_policies: AutoAnnualLeaveApproval = await auto_annual_leave_approval_crud.find_by_branch_id(session=session, branch_id=branch_id)
    account_based_grant_policies: AccountBasedAnnualLeaveGrant = await account_based_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)
    entry_date_based_grant_policies: EntryDateBasedAnnualLeaveGrant = await entry_date_based_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)
    condition_based_grant_policies: list[ConditionBasedAnnualLeaveGrant] = await condition_based_annual_leave_grant_crud.find_all_by_branch_id(session=session, branch_id=branch_id)

    # 자동 승인 정책 업데이트
    if auto_annual_leave_approval_policies is None:
        await auto_annual_leave_approval_crud.create(session=session, branch_id=branch_id, auto_annual_leave_approval_create=AutoAnnualLeaveApproval(branch_id=branch_id, **request.auto_approval_policies.model_dump()))
    else:
        await auto_annual_leave_approval_crud.update(session=session, branch_id=branch_id, auto_annual_leave_approval_update=AutoAnnualLeaveApproval(branch_id=branch_id, **request.auto_approval_policies.model_dump(exclude_unset=True)))

    # 회계 부여 정책 업데이트
    if account_based_grant_policies is None:
        await account_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id, account_based_annual_leave_grant_create=AccountBasedAnnualLeaveGrant(branch_id=branch_id, **request.account_based_policies.model_dump(exclude={'part_ids'})))
    else:
        await account_based_annual_leave_grant_crud.update(session=session, branch_id=branch_id, account_based_annual_leave_grant_update=AccountBasedAnnualLeaveGrant(branch_id=branch_id, **request.account_based_policies.model_dump(exclude={'part_ids'})))

    # 입사일 부여 정책 업데이트
    if entry_date_based_grant_policies is None:
        await entry_date_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id, entry_date_based_annual_leave_grant_create=EntryDateBasedAnnualLeaveGrant(branch_id=branch_id, **request.entry_date_based_policies.model_dump(exclude={'part_ids'})))
    else:
        await entry_date_based_annual_leave_grant_crud.update(session=session, branch_id=branch_id, entry_date_based_annual_leave_grant_update=EntryDateBasedAnnualLeaveGrant(branch_id=branch_id, **request.entry_date_based_policies.model_dump(exclude={'part_ids'})))

    # 조건 부여 정책 업데이트
    saved_ids = set([condition_based_grant.id for condition_based_grant in condition_based_grant_policies])
    request_ids = set([condition_based_grant.id for condition_based_grant in request.condition_based_policies.condition_based_grant])
    # 삭제할 부서 id 추출
    ids_to_delete = saved_ids - request_ids
    # 삭제
    await condition_based_annual_leave_grant_crud.delete_all_id(session=session, branch_id=branch_id, ids=ids_to_delete)
    # 추가
    for condition_based_grant in request.condition_based_policies.condition_based_grant:
        if condition_based_grant.id is None:
            await condition_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id, condition_based_annual_leave_grant_create=ConditionBasedAnnualLeaveGrant(branch_id=branch_id, **condition_based_grant.model_dump()))
        else:
            if condition_based_grant.id in saved_ids:
                await condition_based_annual_leave_grant_crud.update(session=session, branch_id=branch_id, condition_based_annual_leave_grant_update=ConditionBasedAnnualLeaveGrant(branch_id=branch_id, **condition_based_grant.model_dump()))
    
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
    count = await branches_crud.count_all(session=session)
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
    branch = await branches_crud.find_by_id(session=session, branch_id=branch_id)
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
    work_policies = await work_crud.find_by_branch_id(session=session, branch_id=branch_id)
    auto_overtime_policies = await auto_overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
    holiday_work_policies = await holiday_work_crud.find_by_branch_id(session=session, branch_id=branch_id)
    overtime_policies = await overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
    allowance_policies = await allowance_crud.find_by_branch_id(session=session, branch_id=branch_id)

    return CombinedPoliciesDto(
        work_policies=WorkPoliciesDto.model_validate(work_policies or {}),
        auto_overtime_policies=AutoOvertimePoliciesDto.model_validate(auto_overtime_policies or {}),
        holiday_work_policies=HolidayWorkPoliciesDto.model_validate(holiday_work_policies or {}),
        overtime_policies=OverTimePoliciesDto.model_validate(overtime_policies or {}),
        default_allowance_policies=DefaultAllowancePoliciesDto.model_validate(allowance_policies or {}),
        holiday_allowance_policies=HolidayAllowancePoliciesDto.model_validate(allowance_policies or {})
    )


async def update_branch_policies(*, session: AsyncSession, branch_id: int, request: CombinedPoliciesDto) -> str:
    """지점 정책 수정"""
    try:
        # WorkPolicies 업데이트
        work_policies = await work_crud.find_by_branch_id(session=session, branch_id=branch_id)
        if work_policies is None:
            await work_crud.create(session=session, branch_id=branch_id)
            work_policies = await work_crud.find_by_branch_id(session=session, branch_id=branch_id)
            if work_policies is None:
                raise HTTPException(status_code=500, detail="근무정책 생성에 실패하였습니다.")
        else:
            await work_crud.update(
                session=session,
                branch_id=branch_id,
                work_policies_update=request.work_policies  # WorkPoliciesUpdateDto 타입으로 전달
            )

        # AutoOvertimePolicies 업데이트
        auto_overtime_policies = await auto_overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
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
        holiday_work_policies = await holiday_work_crud.find_by_branch_id(session=session, branch_id=branch_id)
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
        overtime_policies = await overtime_crud.find_by_branch_id(session=session, branch_id=branch_id)
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
        allowance_policies = await allowance_crud.find_by_branch_id(session=session, branch_id=branch_id)
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
        return f"{branch_id} 번 지점의 근무정책 업데이트 완료"

    except Exception as e:
        await session.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="근무정책 업데이트에 실패하였습니다."
        )

# 근무 캘린더에서 고정 휴점일을 변경할 때 사용
async def update_schedule_holiday(*, session: AsyncSession, branch_id: int, request: ScheduleHolidayUpdateDto) -> str:
    """지점 정책 수정"""
    try:
        # WorkPolicies 업데이트
        work_policies = await work_crud.find_by_branch_id(session=session, branch_id=branch_id)
        if work_policies is None:
            await work_crud.create(session=session, branch_id=branch_id)
            work_policies = await work_crud.find_by_branch_id(session=session, branch_id=branch_id)
            if work_policies is None:
                raise HTTPException(status_code=500, detail="근무정책 생성에 실패하였습니다.")
        else:
            await work_crud.update_schedule_holiday(
                session=session,
                branch_id=branch_id,
                work_policies_update=request.work_policies  # WorkPoliciesUpdateDto 타입으로 전달
            )

        await session.commit()
        return f"{branch_id} 번 지점의 근무정책 업데이트 완료"

    except Exception as e:
        await session.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="근무정책 업데이트에 실패하였습니다."
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
