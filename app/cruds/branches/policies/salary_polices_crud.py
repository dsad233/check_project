from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import Optional, Dict, Any, List
from app.models.branches.parttimer_policies_model import ParttimerPolicies
from app.models.branches.salary_polices_model import CombinedPoliciesUpdate, SalaryTemplatesPolicies
from app.models.branches.allowance_policies_model import AllowancePolicies
from app.models.parts.parts_model import Parts


async def get_all_policies(db: Session, branch_id: int) -> Dict[str, Any]:
    parttimer_query = select(ParttimerPolicies).filter(
        ParttimerPolicies.branch_id == branch_id
    )
    parttimer_policies = (await db.execute(parttimer_query)).scalar_one_or_none()
    
    # 브랜치의 모든 salary_templates_policies 가져오기
    salary_templates_query = (
        select(SalaryTemplatesPolicies, Parts.name.label('part_name'))  # Parts.name도 함께 선택
        .join(Parts, SalaryTemplatesPolicies.part_id == Parts.id)  # Parts 테이블과 조인
        .filter(
            SalaryTemplatesPolicies.branch_id == branch_id
        )
    )
    result = await db.execute(salary_templates_query)
    salary_templates_policies = []
    for row in result:
        policy = row[0]
        policy.part_name = row[1]  # part_name 추가
        salary_templates_policies.append(policy)
    
    allowance_query = select(AllowancePolicies).filter(
        AllowancePolicies.branch_id == branch_id,
        AllowancePolicies.deleted_yn == "N"
    )
    allowance_policies = (await db.execute(allowance_query)).scalar_one_or_none()
    
    return {
        "parttimer_policies": parttimer_policies,
        "salary_templates_policies": salary_templates_policies,
        "allowance_policies": allowance_policies
    }


async def update_policies(db: Session, branch_id: int, update_data: CombinedPoliciesUpdate) -> Dict[str, Any]:
    try:
        # 파트타이머 정책 업데이트
        if update_data.parttimer_policies:
            parttimer_query = select(ParttimerPolicies).filter(
                ParttimerPolicies.branch_id == branch_id
            )
            parttimer_policy = (await db.execute(parttimer_query)).scalar_one_or_none()
            if parttimer_policy:
                update_dict = update_data.parttimer_policies.model_dump(exclude_unset=True)
                for key, value in update_dict.items():
                    if key != 'branch_id':
                        setattr(parttimer_policy, key, value)

        # 급여 템플릿 정책 업데이트
        if update_data.salary_templates_policies:
            for template_data in update_data.salary_templates_policies:
                template_query = select(SalaryTemplatesPolicies).filter(
                    SalaryTemplatesPolicies.branch_id == branch_id,
                    SalaryTemplatesPolicies.part_id == template_data.part_id
                )
                template = (await db.execute(template_query)).scalar_one_or_none()
                if template:
                    update_dict = template_data.model_dump(exclude_unset=True)
                    for key, value in update_dict.items():
                        if key not in ['branch_id', 'part_id', 'part_name']:
                            setattr(template, key, value)

        # 수당 정책 업데이트
        if update_data.allowance_policies:
            allowance_query = select(AllowancePolicies).filter(
                AllowancePolicies.branch_id == branch_id,
                AllowancePolicies.deleted_yn == "N"
            )
            allowance_policy = (await db.execute(allowance_query)).scalar_one_or_none()
            if allowance_policy:
                update_dict = update_data.allowance_policies.model_dump(exclude_unset=True)
                for key, value in update_dict.items():
                    if key != 'branch_id':
                        setattr(allowance_policy, key, value)

        await db.commit()
        
        # 업데이트된 정책들 조회하여 반환
        return await get_all_policies(db, branch_id)
    
    except Exception as e:
        await db.rollback()
        raise e
