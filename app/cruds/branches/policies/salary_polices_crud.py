from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import Optional, Dict, Any, List
from app.models.branches.parttimer_policies_model import ParttimerPolicies
from app.models.branches.salary_polices_model import CombinedPoliciesUpdate, SalaryTemplatesPolicies
from app.models.branches.allowance_policies_model import AllowancePolicies
from app.models.parts.parts_model import Parts


async def get_all_policies(db: Session, branch_id: int) -> Dict[str, Any]:
    """
    임금 명세서 설정을 조회합니다.

    이 함수는 지점의 파트타이머 정책, 급여 템플릿 정책, 수당 정책을 포함한 임금 명세서 설정을 조회합니다.

    Returns:
        Dict[str, Any]: 다음 키를 포함하는 딕셔너리를 반환합니다:
            - parttimer_policies: 파트타이머 정책 정보 (branch단위)
            - salary_templates_policies: 급여 템플릿 정책 목록, 리스트 안에 딕셔너리 형태로 반환(part단위)
            - allowance_policies: 수당 정책 정보 (branch단위)

    Raises:
        SQLAlchemyError: 데이터베이스 조회 중 오류가 발생한 경우
    """
    parttimer_query = select(ParttimerPolicies).filter(
        ParttimerPolicies.branch_id == branch_id
    )
    parttimer_policies = (await db.execute(parttimer_query)).scalar_one_or_none()
    
    salary_templates_query = (
        select(SalaryTemplatesPolicies, Parts.name.label('part_name')) 
        .join(Parts, SalaryTemplatesPolicies.part_id == Parts.id) 
        .filter(
            SalaryTemplatesPolicies.branch_id == branch_id
        )
    )
    result = await db.execute(salary_templates_query)
    salary_templates_policies = []
    
    for row in result:
        policy = row[0]  # SalaryTemplatesPolicies 조회결과
        policy.part_name = row[1] # part_id와 일치하는 part name
        salary_templates_policies.append(policy)
        
    
    allowance_query = select(AllowancePolicies).filter(
        AllowancePolicies.branch_id == branch_id,
        AllowancePolicies.deleted_yn == "N"
    )
    allowance_policies = (await db.execute(allowance_query)).scalar_one_or_none()
    
    return {
        "parttimer_policies" : parttimer_policies,
        "salary_templates_policies" : salary_templates_policies,
        "allowance_policies" : allowance_policies,
    }


async def update_policies(db: Session, branch_id: int, update_data: CombinedPoliciesUpdate) -> Dict[str, Any]:
    """
    임금 명세서 설정을 업데이트합니다.

    파트타이머 정책, 급여 템플릿 정책, 수당 정책을 포함한 임금 명세서 설정을 업데이트하고 업데이트된 정보를 반환합니다.

    Args:
        db (Session): 데이터베이스 세션 객체
        branch_id (int): 업데이트할 지점의 ID
        update_data (CombinedPoliciesUpdate): 업데이트할 정책 데이터를 포함하는 객체
            - parttimer_policies: 파트타이머 정책 업데이트 데이터
            - salary_templates_policies: 급여 템플릿 정책 업데이트 데이터 리스트
            - allowance_policies: 수당 정책 업데이트 데이터

    Returns:
        Dict[str, Any]: 업데이트된 모든 정책 정보를 포함하는 딕셔너리:
            - parttimer_policies: 업데이트된 파트타이머 정책(branch단위)
            - salary_templates_policies: 업데이트된 급여 템플릿 정책 목록(part단위), 리스트 안에 딕셔너리 형태로 반환
            - allowance_policies: 업데이트된 수당 정책(branch단위)
    """
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


async def create_salary_templates_policies(db: Session, branch_id: int, part_ids: List[int]) -> None:
    """지점의 파트별 급여 템플릿 정책을 생성합니다.

    Args:
        db (Session): 데이터베이스 세션 객체
        branch_id (int): 지점 ID
        part_ids (List[int]): 파트 ID 리스트

    Returns:
        None
    """
    for part_id in part_ids:
        policy = SalaryTemplatesPolicies(
            branch_id=branch_id,
            part_id=part_id
        )
        db.add(policy)
    await db.flush()

async def create_parttimer_policies(db: Session, branch_id: int) -> None:
    """지점의 파트타이머 정책을 생성합니다.

    Args:
        db (Session): 데이터베이스 세션 객체
        branch_id (int): 지점 ID

    Returns:
        None
    """
    policy = ParttimerPolicies(
        branch_id=branch_id
    )
    db.add(policy)
    await db.flush()

async def create_allowance_policies(db: Session, branch_id: int) -> None:
    """지점의 수당 정책을 생성합니다.

    Args:
        db (Session): 데이터베이스 세션 객체
        branch_id (int): 지점 ID

    Returns:
        None
    """
    policy = AllowancePolicies(
        branch_id=branch_id
    )
    db.add(policy)
    await db.flush()