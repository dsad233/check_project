from app.models.branches.auto_annual_leave_approval_model import AutoAnnualLeaveApproval
from app.models.branches.account_based_annual_leave_grant_model import AccountBasedAnnualLeaveGrant
from app.models.branches.entry_date_based_annual_leave_grant_model import EntryDateBasedAnnualLeaveGrant
from app.models.branches.condition_based_annual_leave_grant_model import ConditionBasedAnnualLeaveGrant
from app.models.histories.branch_histories_model import BranchHistories
from app.models.branches.branches_model import Branches
from app.common.dto.search_dto import BaseSearchDto
from app.common.dto.pagination_dto import PaginationDto
from app.schemas.branches_schemas import (AutoLeavePoliciesAndPartsDto, 
                                          AccountPoliciesWithParts, 
                                          EntryDatePoliciesWithParts, 
                                          ConditionPoliciesWithParts, 
                                          AutoAnnualLeaveApprovalDto, 
                                          AccountBasedGrantDto, 
                                          EntryDateBasedGrantDto, 
                                          ConditionBasedGrantDto, 
                                          PartIdWithName, 
                                          SalaryTemplateResponse,
                                          SalaryTemplatesResponse,
                                          BranchHistoryResponse,
                                          BranchHistoriesResponse,
                                          BranchListResponse,
                                          BranchResponse,
                                          BranchRequest)
from app.cruds.leave_policies import auto_annual_leave_approval_crud, account_based_annual_leave_grant_crud, entry_date_based_annual_leave_grant_crud, condition_based_annual_leave_grant_crud
from app.cruds.branches.policies import allowance_crud, holiday_work_crud, overtime_crud, work_crud, auto_overtime_crud
from app.cruds.salary_template import salary_template_crud
from app.cruds.parts import parts_crud
from app.cruds.branches import branches_crud, branch_histories_crud
from app.enums.parts import PartAutoAnnualLeaveGrant
from app.enums.branches import BranchHistoryType
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

async def get_auto_leave_policies_and_parts(*, session: AsyncSession, branch_id: int) -> AutoLeavePoliciesAndPartsDto:
    
    # 자동 연차 부여 및 승인 정책 조회
    auto_annual_leave_approval_policies: AutoAnnualLeaveApproval = await auto_annual_leave_approval_crud.find_by_branch_id(session=session, branch_id=branch_id)
    account_based_grant_policies: AccountBasedAnnualLeaveGrant = await account_based_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)
    entry_date_based_grant_policies: EntryDateBasedAnnualLeaveGrant = await entry_date_based_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)
    condition_based_grant_policies: list[ConditionBasedAnnualLeaveGrant] = await condition_based_annual_leave_grant_crud.find_all_by_branch_id(session=session, branch_id=branch_id)

    # 파트 조회
    account_parts = await parts_crud.find_all_by_branch_id_and_auto_annual_leave_grant(session=session, branch_id=branch_id, auto_annual_leave_grant=PartAutoAnnualLeaveGrant.ACCOUNTING_BASED_GRANT)
    entry_date_parts = await parts_crud.find_all_by_branch_id_and_auto_annual_leave_grant(session=session, branch_id=branch_id, auto_annual_leave_grant=PartAutoAnnualLeaveGrant.ENTRY_DATE_BASED_GRANT)
    condition_parts = await parts_crud.find_all_by_branch_id_and_auto_annual_leave_grant(session=session, branch_id=branch_id, auto_annual_leave_grant=PartAutoAnnualLeaveGrant.CONDITIONAL_GRANT)
    manual_parts = await parts_crud.find_all_by_branch_id_and_auto_annual_leave_grant(session=session, branch_id=branch_id, auto_annual_leave_grant=PartAutoAnnualLeaveGrant.MANUAL_GRANT)

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

        await parts_crud.update_auto_annual_leave_grant(
            session=session,
            branch_id=branch_id,
            part_id=part.id,
            auto_annual_leave_grant=grant_type
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


async def get_all_salary_template_and_allowance_policy(
        *, 
        session: AsyncSession, 
        branch_id: int, 
        request: BaseSearchDto
) -> SalaryTemplatesResponse:
    salary_templates = await salary_template_crud.find_salary_templates(session=session, branch_id=branch_id, request=request)
    if not salary_templates:
        return SalaryTemplatesResponse(data=[], pagination=PaginationDto(total_record=0))
    total_count = await salary_template_crud.count_all_by_branch_id(session=session, branch_id=branch_id)
    branch = await branches_crud.find_by_id_with_policies(session=session, branch_id=branch_id)

    data = [SalaryTemplateResponse(
        **SalaryTemplateResponse.model_validate(salary_template).model_dump(exclude_none=True),
        part_name=salary_template.part.name,
        job_allowance=branch.allowance_policies.job_allowance,
        meal_allowance=branch.allowance_policies.meal_allowance, 
        holiday_allowance=branch.allowance_policies.doctor_holiday_work_pay if salary_template.part.is_doctor else branch.allowance_policies.common_holiday_work_pay
        ) for salary_template in salary_templates]

    return SalaryTemplatesResponse(data=data, pagination=PaginationDto(total_record=total_count))


async def get_branch_histories(*, session: AsyncSession, branch_id: int, request: BaseSearchDto, history_type: BranchHistoryType) -> BranchHistoriesResponse:
    branch_histories = await branch_histories_crud.get_branch_histories(session=session, branch_id=branch_id, request=request, history_type=history_type)
    total_count = await branch_histories_crud.get_total_cnt(session=session, branch_id=branch_id, history_type=history_type)
    return BranchHistoriesResponse(data=branch_histories, pagination=PaginationDto(total_record=total_count))


async def get_branches(*, session: AsyncSession, request: BaseSearchDto) -> BranchListResponse:
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

    branch = await branches_crud.create(session=session, request=Branches(**request.model_dump()))
    branch_id = branch.id
    # 정책 생성
    if branch_id is not None:
        await holiday_work_crud.create(session=session, branch_id=branch_id)
        await overtime_crud.create(session=session, branch_id=branch_id)
        await work_crud.create(session=session, branch_id=branch_id)
        await auto_overtime_crud.create(session=session, branch_id=branch_id)
        await allowance_crud.create(session=session, branch_id=branch_id)
        await auto_annual_leave_approval_crud.create(session=session, branch_id=branch_id)
        await account_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id)
        await entry_date_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id)
        await condition_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id)

    return True
