from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.api.routes.parts_policy.schema.parts_policy_schema import (
    PartWorkPolicyCreate,
    PartWorkPolicyResponse,
)
from app.core.database import async_session
from app.middleware.tokenVerify import validate_token
from app.models.models import Users
from app.models.policies.branchpolicies import WorkPolicies, PartWorkPolicies

router = APIRouter(dependencies=[Depends(validate_token)])
db = async_session()


@router.get("")
async def getPartWorkPolicies(
    branch_id: int, current_user: Users = Depends(validate_token)
):
    try:
        if current_user.role.strip() not in ["MSO 최고권한", "최고관리자"] or (
            current_user.role.strip() == "최고관리자"
            and current_user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        query = select(PartWorkPolicies).where(
            (PartWorkPolicies.branch_id == branch_id)
            & (PartWorkPolicies.deleted_yn == "N")
        )
        result = await db.execute(query)
        part_work_policies = result.scalars().all()

        if not part_work_policies:
            raise HTTPException(
                status_code=400, detail="존재하지 않는 부서 근무 정책입니다."
            )

        part_work_policy_responses = []
        
        for policy in part_work_policies:
            part_work_policy_response = PartWorkPolicyResponse(
                id=policy.id,
                work_start_time=policy.work_start_time,
                work_end_time=policy.work_end_time,
                lunch_start_time=policy.lunch_start_time,
                lunch_end_time=policy.lunch_end_time,
                break_time_1=policy.break_time_1,
                break_time_2=policy.break_time_2,
            )
            part_work_policy_responses.append(part_work_policy_response)
            
        return part_work_policy_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{part_id}")
async def getPartWorkPolicy(
    branch_id: int, part_id: int, current_user: Users = Depends(validate_token)
):
    try:
        if current_user.role.strip() not in ["MSO 최고권한", "최고관리자"] or (
            current_user.role.strip() == "최고관리자"
            and current_user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        query = select(PartWorkPolicies).where(
            (PartWorkPolicies.part_id == part_id)
            & (PartWorkPolicies.branch_id == branch_id)
            & (PartWorkPolicies.deleted_yn == "N")
        )
        result = await db.execute(query)
        part_work_policy = result.scalars().one_or_none()

        if not part_work_policy:
            raise HTTPException(status_code=400, detail="존재하지 않는 부서 근무 정책입니다.")

        part_work_policy_response = PartWorkPolicyResponse(
            id=part_work_policy.id,
            work_start_time=part_work_policy.work_start_time,
            work_end_time=part_work_policy.work_end_time,
            lunch_start_time=part_work_policy.lunch_start_time,
            lunch_end_time=part_work_policy.lunch_end_time,
            break_time_1=part_work_policy.break_time_1,
            break_time_2=part_work_policy.break_time_2,
        )
        return part_work_policy_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{part_id}")
async def createPartWorkPolicy(
    branch_id: int,
    part_id: int,
    data: PartWorkPolicyCreate,
    current_user: Users = Depends(validate_token),
):
    try:
        if current_user.role.strip() not in ["MSO 최고권한", "최고관리자"] or (
            current_user.role.strip() == "최고관리자"
            and current_user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        part_work_policy_query = select(PartWorkPolicies).where(
            (PartWorkPolicies.part_id == part_id)
            & (PartWorkPolicies.branch_id == branch_id)
            & (PartWorkPolicies.deleted_yn == "N")
        )
        result = await db.execute(part_work_policy_query)
        part_work_policy = result.scalars().one_or_none()

        if part_work_policy:
            raise HTTPException(
                status_code=400, detail="이미 존재하는 부서 근무 정책입니다."
            )

        work_policy_query = select(WorkPolicies).where(
            WorkPolicies.id == data.work_policy_id
        )
        result = await db.execute(work_policy_query)
        work_policy = result.scalars().one_or_none()

        if not work_policy:
            raise HTTPException(
                status_code=400, detail="존재하지 않는 근무 정책입니다."
            )

        # work_policy를 참조하며, 유효성을 판단하기

        create_data = PartWorkPolicies(
            part_id=part_id,
            work_policy_id=data.work_policy_id,
            work_start_time=work_policy.work_start_time,
            work_end_time=work_policy.work_end_time,
            lunch_start_time=work_policy.lunch_start_time,
            lunch_end_time=work_policy.lunch_end_time,
            break_time_1=work_policy.break_time_1,
            break_time_2=work_policy.break_time_2,
        )
        db.add(create_data)
        await db.commit()

        return {"message": "부서 근무 정책 생성에 성공하였습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{part_id}")
async def updatePartWorkPolicy(
    branch_id: int,
    part_id: int,
    data: PartWorkPolicyCreate,
    current_user: Users = Depends(validate_token),
):
    try:
        if current_user.role.strip() not in ["MSO 최고권한", "최고관리자"] or (
            current_user.role.strip() == "최고관리자"
            and current_user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        part_work_policy_query = (
            select(PartWorkPolicies)
            .options(selectinload(PartWorkPolicies.work_policy))
            .where(
                (PartWorkPolicies.part_id == part_id)
                & (PartWorkPolicies.branch_id == branch_id)
                & (PartWorkPolicies.deleted_yn == "N")
            )
        )
        result = await db.execute(part_work_policy_query)
        part_work_policy = result.scalars().one_or_none()

        if not part_work_policy:
            raise HTTPException(
                status_code=400, detail="존재하지 않는 부서 근무 정책입니다."
            )

        # 유효성 검증다

        if data.work_start_time is not None:
            part_work_policy.work_start_time = data.work_start_time
        if data.work_end_time is not None:
            part_work_policy.work_end_time = data.work_end_time
        if data.lunch_start_time is not None:
            part_work_policy.lunch_start_time = data.lunch_start_time
        if data.lunch_end_time is not None:
            part_work_policy.lunch_end_time = data.lunch_end_time
        if data.break_time_1 is not None:
            part_work_policy.break_time_1 = data.break_time_1
        if data.break_time_2 is not None:
            part_work_policy.break_time_2 = data.break_time_2

        await db.commit()

        return {"message": "부서 근무 정책 수정에 성공하였습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{part_id}")
async def deletePartWorkPolicy(
    branch_id: int, part_id: int, current_user: Users = Depends(validate_token)
):
    try:
        if current_user.role.strip() not in ["MSO 최고권한", "최고관리자"] or (
            current_user.role.strip() == "최고관리자"
            and current_user.branch_id != branch_id
        ):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")

        query = delete(PartWorkPolicies).where(
            (PartWorkPolicies.part_id == part_id)
            & (PartWorkPolicies.branch_id == branch_id)
            & (PartWorkPolicies.deleted_yn == "N")
        )
        await db.execute(query)
        await db.commit()

        return {"message": "부서 근무 정책 삭제에 성공하였습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
