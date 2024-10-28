from app.models.branches.auto_annual_leave_approval_model import AutoAnnualLeaveApproval
from app.models.branches.account_based_annual_leave_grant_model import AccountBasedAnnualLeaveGrant
from app.models.branches.entry_date_based_annual_leave_grant_model import EntryDateBasedAnnualLeaveGrant
from app.models.branches.condition_based_annual_leave_grant_model import ConditionBasedAnnualLeaveGrant
from app.schemas.branches_schemas import AutoLeavePoliciesAndPartsDto, AccountPoliciesWithParts, EntryDatePoliciesWithParts, ConditionPoliciesWithParts, AutoAnnualLeaveApprovalDto, AccountBasedGrantDto, EntryDateBasedGrantDto, ConditionBasedGrantDto, PartIdWithName
from app.cruds.leave_policies import auto_annual_leave_approval_crud, account_based_annual_leave_grant_crud, entry_date_based_annual_leave_grant_crud, condition_based_annual_leave_grant_crud
from app.cruds.parts import parts_crud
from app.enums.parts import PartAutoAnnualLeaveGrant
from sqlalchemy.ext.asyncio import AsyncSession


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
    

async def update_auto_leave_policies_and_parts(*, session: AsyncSession, branch_id: int, data: AutoLeavePoliciesAndPartsDto) -> bool:

    auto_annual_leave_approval_policies: AutoAnnualLeaveApproval = await auto_annual_leave_approval_crud.find_by_branch_id(session=session, branch_id=branch_id)
    account_based_grant_policies: AccountBasedAnnualLeaveGrant = await account_based_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)
    entry_date_based_grant_policies: EntryDateBasedAnnualLeaveGrant = await entry_date_based_annual_leave_grant_crud.find_by_branch_id(session=session, branch_id=branch_id)
    condition_based_grant_policies: list[ConditionBasedAnnualLeaveGrant] = await condition_based_annual_leave_grant_crud.find_all_by_branch_id(session=session, branch_id=branch_id)

    # 자동 승인 정책 업데이트
    if auto_annual_leave_approval_policies is None:
        await auto_annual_leave_approval_crud.create(session=session, branch_id=branch_id, auto_annual_leave_approval_create=AutoAnnualLeaveApproval(branch_id=branch_id, **data.auto_approval_policies.model_dump()))
    else:
        await auto_annual_leave_approval_crud.update(session=session, branch_id=branch_id, auto_annual_leave_approval_update=AutoAnnualLeaveApproval(branch_id=branch_id, **data.auto_approval_policies.model_dump(exclude_unset=True)))

     # 자동 부여 정책 업데이트

    if account_based_grant_policies is None:
        await account_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id, account_based_annual_leave_grant_create=AccountBasedAnnualLeaveGrant(branch_id=branch_id, **data.account_based_policies.model_dump(exclude={'part_ids'})))
    else:
        await account_based_annual_leave_grant_crud.update(session=session, branch_id=branch_id, account_based_annual_leave_grant_update=AccountBasedAnnualLeaveGrant(branch_id=branch_id, **data.account_based_policies.model_dump(exclude={'part_ids'})))

    if entry_date_based_grant_policies is None:
        await entry_date_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id, entry_date_based_annual_leave_grant_create=EntryDateBasedAnnualLeaveGrant(branch_id=branch_id, **data.entry_date_based_policies.model_dump(exclude={'part_ids'})))
    else:
        await entry_date_based_annual_leave_grant_crud.update(session=session, branch_id=branch_id, entry_date_based_annual_leave_grant_update=EntryDateBasedAnnualLeaveGrant(branch_id=branch_id, **data.entry_date_based_policies.model_dump(exclude={'part_ids'})))

    for condition_based_grant in data.condition_based_policies.condition_based_grant:
        if condition_based_grant.id is None:
            await condition_based_annual_leave_grant_crud.create(session=session, branch_id=branch_id, condition_based_annual_leave_grant_create=ConditionBasedAnnualLeaveGrant(branch_id=branch_id, **condition_based_grant.model_dump()))
        else:
            await condition_based_annual_leave_grant_crud.update(session=session, branch_id=branch_id, condition_based_annual_leave_grant_update=ConditionBasedAnnualLeaveGrant(branch_id=branch_id, **condition_based_grant.model_dump()))
    
    # 파트 auto_annual_leave_grant 업데이트
    all_parts = (
        data.account_based_policies.part_ids +
        data.entry_date_based_policies.part_ids +
        data.condition_based_policies.part_ids +
        data.manual_based_parts
    )

    for part in all_parts:
        if part in data.account_based_policies.part_ids:
            grant_type = PartAutoAnnualLeaveGrant.ACCOUNTING_BASED_GRANT
        elif part in data.entry_date_based_policies.part_ids:
            grant_type = PartAutoAnnualLeaveGrant.ENTRY_DATE_BASED_GRANT
        elif part in data.condition_based_policies.part_ids:
            grant_type = PartAutoAnnualLeaveGrant.CONDITIONAL_GRANT
        else:
            grant_type = PartAutoAnnualLeaveGrant.MANUAL_GRANT
            
        await parts_crud.update_auto_annual_leave_grant(
            session=session,
            branch_id=branch_id,
            part_id=part.id,
            auto_annual_leave_grant=grant_type
        )
        
    return True
